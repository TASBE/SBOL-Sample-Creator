from __future__ import print_function
# Follow README for installation instructions

"""""
EXCEL IMPORT
"""""

from sbol import *
import re
import sys
import xlrd
import getpass

import pickle    
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# creating a variable representing the Excel file
def MakeBook(file_location):
    wb = xlrd.open_workbook(file_location)
    return wb

# making sure there is a sheet named "Experiment DNA sample"
def ExpSheetFinder(wb, ExperimentSheetName):
    try:
        ExperimentSheet = wb.sheet_by_name(ExperimentSheetName)
    except:
        print('Error: No sheet named {} detected.'.format(ExperimentSheetName))
        return(-1)
    return(ExperimentSheet)

# extracting experiment name from "Experiment" sheet
def ExpNameFinder(wb):
    NameSheet = wb.sheet_by_name('Experiment')
    LookingFor = 'Experiment Name'
    for r in range(0,NameSheet.nrows):
        cell_obj = NameSheet.cell(r,0)
        if (cell_obj.value == LookingFor):
            r+=1
            ExperimentName = (NameSheet.cell(r,0)).value
            return(ExperimentName)
        else:
            r+=1
    print('Error: Experiment name not found in file. It must be in the first column of the "Experiment" sheet under the "Experiment Name" header.')
    return(-1)

# extracting information about each key in the Experimental conditions column (units, symbol meaning, etc)
def ConditionKeyExtractor(wb):
    ConditionKeyDict = {}
    NameSheet = wb.sheet_by_name('Experiment')
    for condNum in range(0,5):
        LookingFor = 'Condition Key ' + str(condNum + 1)
        for r in range(0,NameSheet.nrows):
            cell_obj = NameSheet.cell(r,0)
            if cell_obj.value == LookingFor:
                r += 1
                cond = NameSheet.cell(r,1).value
                ConditionKeyDict[cond] = {}
                tempDict = ConditionKeyDict[cond]
                r += 2
                while NameSheet.cell(r,0).value != '':
                    tempDict[NameSheet.cell(r,0).value] = NameSheet.cell(r,1).value
                    r += 1
    return(ConditionKeyDict)

# extracting the unit from "Experiment DNA sample" sheet
def UnitCollectionFunc(ExperimentSheet):
    Unit = ''
    for r in range(0,ExperimentSheet.nrows):
        cell_obj = ExperimentSheet.cell(r,0)
        if (cell_obj.value == 'Unit:' or cell_obj.value == 'Unit' or cell_obj.value == 'unit:' or cell_obj.value == 'unit'):
            Unit = (ExperimentSheet.cell(r,1)).value
        else:
            r+=1

    if Unit == '':
        print('Error: Unit not found.')
        return(-1)
    return(Unit)


# extracting a list of all the ModuleDefinitions from the "Experiment DNA sample" sheet. Then, creating a list of plasmids that are contained within each Module
def PlasModList(ExperimentSheet):
    ModList = []
    LookingFor = 'Plasmid Number'
    for r in range(0,ExperimentSheet.nrows):
        cell_obj = ExperimentSheet.cell(r,0)
        if cell_obj.value == LookingFor:
            col = 1
            while (ExperimentSheet.cell(r,col)).value != '' and (ExperimentSheet.cell(r,col)).value != 'Plasmid Description':
                ModList.append(ExperimentSheet.cell(r,col).value)
                col+=1
        else:
            r+=1
    if ModList == []:
        print('Error: No modules found. They need to be in a row with "Plasmid Number" as the header.')
        return(-1,-1)
    PlasmidList_orig = []
    for r in range(0,ExperimentSheet.nrows):
        cell_obj = ExperimentSheet.cell(r,0)
        if (cell_obj.value == LookingFor):
            r+=1
            while (r < ExperimentSheet.nrows and (ExperimentSheet.cell(r,0)).value != ''):
                PlasmidList_orig.append((ExperimentSheet.cell(r,0)).value)
                r+=1
    if PlasmidList_orig == []:
        print('Error: No plasmids found. They need to be in the first column with "Plasmid Number" as the header.')
        return(-1,-1)
    return(ModList,PlasmidList_orig)


# taking away duplicates from PlasmidList_orig so that unique ComponentDefinitions can be created
def PlasNoRepeat(PlasmidList_orig):
    import collections
    PlasmidList_norepeat = list(dict.fromkeys(PlasmidList_orig))
    return(PlasmidList_norepeat)


# function for finding a cell with a specific string
def DescriptionFinder(LookingFor, sheetname):
    for r in range(0,sheetname.nrows):
        for c in range(0,sheetname.ncols):
            cell_obj = sheetname.cell(r,c)
            if cell_obj.value == LookingFor:
                return (r,c)
    return(-1,-1)

"""""
MODULE DEFINITIONS -- DNA MIXES
"""""

# taking the module name/type of plasmid mix and putting a '_' where the spaces are, then composing the ModuleNames into a new list
def ModListCleaner(ModList, ExperimentName):
    clean = lambda varStr: re.sub('\W|^(?=\d)','_', varStr)
    #import urllib.parse
    #ExperimentName = urllib.parse.quote(ExperimentName)
    #'JHT6_codename_1_DNA_X' 
            # vs.
    #'JHT6_codename_10x3ADNA0x20X'
    #newModList = [(ExperimentName.replace('%','0x') + '_codename_' + urllib.parse.quote(ModName).replace('%','0x')) for ModName in ModList]
    newModList = [(clean(ExperimentName) + '_codename' + clean(ModName)) for ModName in ModList]
    return(newModList)


# creating the ModuleDefinitions from the module list, by making a dictionary with the key being the MD displayID and the value being the MD associated with that displayID
# ModDefDict[displayID] is of the type "MD"
# in the future, adding appropriate description to each MD
def ModMaker(ModList, newModList, ExperimentSheet, doc):
    ModDefDict = {}
    for val in range(0,len(newModList)):
        displayID = newModList[val]
        try:
            temp = ModuleDefinition(displayID)
            ModDefDict[displayID] = temp
            # temp.description = ModDescriptionList[val]
            # ^insert description by extracting it from the Excel files
            doc.addModuleDefinition(ModDefDict[displayID])
        except:
            formatlist = [ExperimentSheet.name,ModList[val]]
            print('Error: Detecting two columns in "{}" sheet with {} as the condition header.'.format(*formatlist))
            return(-1)
    return(ModDefDict)


"""""
MODULE DEFINITIONS -- SAMPLES
"""""

# finding Sample sheet and extracting Sample List
def SamplesSheetFinder(wb):
    try:
        SampleSheet = wb.sheet_by_name('Samples')
    except:
        print('Error: No sheet named "Samples" detected.')
        return(-1)
    return SampleSheet

# extracting Sample Descriptions from Sample sheet
def SampleListDesc(SampleSheet):
    SampleList = []
    SampleDescriptions = []
    for r in range(0,SampleSheet.nrows):
        cell_obj = SampleSheet.cell(r,0)
        if (cell_obj.value == 'SAMPLE\nNUMBER' or cell_obj.value == 'SAMPLE NUMBER'):
            r+=1
            while (SampleSheet.cell(r,0)).value != '':
                SampleList.append(SampleSheet.cell(r,0).value)
                SampleDescriptions.append(SampleSheet.cell(r,1).value)
                r+=1
        else:
            r+=1
    if SampleList == []:
        print('Error: First column in "Samples" sheet must have a column name SAMPLE NUMBER')
        return(-1,-1)
    return (SampleList, SampleDescriptions)

# getting information about Experimental Conditions for each Sample
def SampleExpConditions(SampleSheet, SampleList):
    # getting data about Experimental Conditions -- ASSUMING THERE ARE AT MOST 5 POSSIBLE COLUMNS
    ConditionDictionary = {}
    ConditionList1 = []
    ConditionList2 = []
    ConditionList3 = []
    ConditionList4 = []
    ConditionList5 = []

    LookingFor = 'Experimental Conditions (one per column, can vary). '
    try:
        (r,c) = DescriptionFinder(LookingFor,SampleSheet)
    except:
        try:
            (r,c) = DescriptionFinder('Experimental Conditions',SampleSheet)
        except:
            print('Error: "Samples" sheet must have a column titled "Experimental Conditions" or "Experimental Conditions (one per column, can vary). ".')
            return(-1)
    r+=1
    for cond in [ConditionList1,ConditionList2,ConditionList3,ConditionList4,ConditionList5]:
        for row in range(r,r+1+len(SampleList)):
            addval = (SampleSheet.cell(row,c)).value
            cond.append(addval)
            row+=1
        c+=1
        if(cond[0] != '' and cond[0] != '-'):
            ConditionDictionary[str(cond[0])] = cond[1:]
    return ConditionDictionary

# creating Module Definition for each Sample, and adding the appropriate Annotations based on the Experimental Conditions in ConditionDictionary
def SampleModMaker(SampleSheet, SampleList, SampleDescriptions, ConditionDictionary, ExperimentName, existingNamesDict, ConditionKeyDict, doc):
    SampleModDefDict = {}
    clean = lambda varStr: re.sub('\W|^(?=\d)','_', varStr)
    newSampleList = [(clean(ExperimentName) + '_sample_' + str(round(SampleName))) for SampleName in SampleList]
    for val in range(0,len(newSampleList)):
        displayID = newSampleList[val]
        try:
            temp = ModuleDefinition(displayID)
            SampleModDefDict[displayID] = temp
            temp.description = SampleDescriptions[val]
            doc.addModuleDefinition(SampleModDefDict[displayID])
        except:
            formatlist = [SampleSheet.name,SampleList[val]]
            print('Error: Detecting two samples in "{}" sheet numbered {}.'.format(*formatlist))
            return(-1,-1)
        # creating either FuncComp or Annotations with Dox symbol, time, and any other experimental conditions listed
        for cond in ConditionDictionary:
            value = (ConditionDictionary[cond])[val]
            uriLink = 'http://bu.edu/dasha/#'
            rdf = uriLink + str(cond)
            if value != '':
                if is_number(value):
                    stringval = '%s' % float('%6g' % value) # at most 6 significant figures
                else:
                    stringval = value
                # extracting value and its explanation from ConditionDictionary
                conditionValue = stringval
                if cond in ConditionKeyDict:
                    conditionExplanation = (ConditionKeyDict[cond])[value]
                else:
                    conditionExplanation = ''
                counter = 0
                try:
                    codeVal = conditionExplanation.split()[0]
                except:
                    codeVal = ''
                if cond.lower() != 'time' and cond.lower() != 'code' and conditionValue != '0' and codeVal != '0': # creates FuncComps for all conditions except for time and code
                    if is_number(cond[0]):
                        compDisp = '_' + cond
                    else:
                        compDisp = cond
                    tempcomp = ComponentDefinition(compDisp)
                    temp2 = SampleModDefDict[displayID].functionalComponents.create(compDisp)
                    try:
                        temp2.definition = existingNamesDict[cond] # checks if exp. condition exists as a reagent in the LCP Dictionary, if so links to it
                    except:
                        temp2.definition = tempcomp.identity # creates a new CompDef if not in LCP dictionary
                    counter += 1
                    rdf1 = uriLink + 'hasKey'
                    rdf2 = uriLink + 'hasExplanation'
                    keyVal = TextProperty(temp2,rdf1,'0','1',conditionValue)
                    if conditionExplanation != '':
                        explanationVal = TextProperty(temp2,rdf2,'0','1',conditionExplanation)
                if counter == 0 and conditionValue != '0' and codeVal != '0':
                    newprop = TextProperty(temp,rdf,'0','1',conditionValue + ' ' + conditionExplanation)
    return (SampleModDefDict, newSampleList)

# creating Modules for each of the plasmid mixes and adding them to the appropriate Sample MD
def ModAdder(SampleList, newSampleList, SampleModDefDict, ModList, newModList, ModDefDict, ConditionDictionary):  
    isthereCode = 0
    validCodeCounter = 0
    for val in range(0,len(SampleList)):
        ModDef = SampleModDefDict[newSampleList[val]]
        for cond in ConditionDictionary:
            if(cond == 'Code' or cond == 'code'): # assumes there is such a column that corresponds to the names on the Experiment DNA sample tab
                isthereCode = 1
                codename = (ConditionDictionary[cond])[val]
                for mod in range(0,len(ModList)):
                    if codename.upper() == ModList[mod].upper():
                        displayID = newModList[mod]
                        temp = ModDef.modules.create(displayID)
                        otherMD = ModDefDict[displayID]
                        temp.definition = otherMD.identity
                        validCodeCounter += 1
                    if mod == (len(ModList) - 1) and validCodeCounter == 0:
                        print('Error: "{}" is listed as a Module name in the Code list but does not appear in the Module list.'.format(codename))
                        return(-1)
    if isthereCode == 0:
        print('Error: There must be a column in the Experimental Conditions tab in the Samples sheet named "Code" that corresponds to the names of each Module in the Experimental DNA sample sheet.')
        return(-1)
    return 0


# checking if a string is a number, used to see if the experimental condition should be converted into a string or not
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
            return False


"""""
COMPONENT DEFINITIONS
"""""

# creating ComponentDefinitions for each plasmid type and adding description, key is the displayID and value is the CD
def CompMaker(PlasmidList_norepeat, existingNamesDict, doc):
    CompDefDict = {}
    # populating Component Dictionary
    for val in range(0,len(PlasmidList_norepeat)):
        displayID = PlasmidList_norepeat[val]
        temp = ComponentDefinition(displayID,BIOPAX_DNA) # encodes all plasmids as type BIOPAX_DNA
        for name in existingNamesDict:
            if displayID == name:
                temp.identity = existingNamesDict[name] # links to an existing component from the dictionary
        CompDefDict[displayID] = temp
    # adding the role to each component and then adding all component definitions to the doc
    for comp in CompDefDict:
        CompDefDict[comp].roles = SO_PLASMID
        doc.addComponentDefinition(CompDefDict[comp])
    return(CompDefDict)


"""""
FUNCTIONAL COMPONENTS + ANNOTATIONS
"""""

# function that finds modules from ModList in "Experiment Sheet"
def FindMod(val, ModList, ExperimentSheet):
    for row in range(0,ExperimentSheet.nrows):
        for col in range(0,ExperimentSheet.ncols):
            cellvalue = (ExperimentSheet.cell(row,col)).value
            if cellvalue == ModList[val]: return (row,col)
    return(-1,-1)

# creating FunctionalComponents for each plasmid present in each Module, and then adding the appropriate annotations
def FuncMaker(ModList, newModList, ModDefDict, CompDefDict, ExperimentSheet, Unit, doc):
    # FunCompDict = {}
    for val in range(0,len(ModList)):
        mod = newModList[val]
        (r,col) = FindMod(val,ModList,ExperimentSheet)
        r+=1
        endvar = 'b'
        while (r < ExperimentSheet.nrows and (ExperimentSheet.cell(r,0)).value != ''):
            if (ExperimentSheet.cell(r,0)).value in CompDefDict:
                displayId = (ExperimentSheet.cell(r,0)).value
                try:
                    temp = ModDefDict[mod].functionalComponents.create(displayId)
                    # FunCompDict[displayId+mod] = temp
                    temp.definition = (CompDefDict[displayId]).identity
                except:
                    displayId = displayId + endvar
                    endvar = chr(ord(endvar) + 1)
                    temp = ModDefDict[mod].functionalComponents.create(displayId)
                    # FunCompDict[displayId+mod] = temp
                    temp.definition = (CompDefDict[(displayId[:-1])]).identity
                (row,c) = DescriptionFinder('Plasmid Description',ExperimentSheet)
                descriptioncol = c
                PlasmidDescription = (ExperimentSheet.cell(r,descriptioncol)).value
                temp.description = PlasmidDescription
                temp.access = SBOL_ACCESS_PUBLIC
                temp.direction = SBOL_DIRECTION_NONE
                
                # setting annotations:
                value = (ExperimentSheet.cell(r,col)).value
                if value != '':
                    value = float('%6g' % value) # at most 6 significant figures
                    temp.hasNumericalValue = FloatProperty(temp,'http://bu.edu/dasha/#hasNumericalValue','0','1')
                    temp.hasNumericalValue = value
                    temp.hasUnit = URIProperty(temp,'http://bu.edu/dasha/#hasUnit','0','1')
                    temp.hasUnit = 'http://www.ontology-of-units-of-measure.org/resource/om-2/nanogram'
                    temp.symbol = TextProperty(temp,'http://bu.edu/dasha/#symbol','0','1')
                    temp.symbol = Unit
                    temp.types = URIProperty(temp,'http://bu.edu/dasha/#types','0','1')
                    temp.types = 'http://www.ebi.ac.uk/sbo/main/SBO:0000649'
                    
                elif value == '':
                    # deleting FuncComps for any unused plasmids in this specific mix
                    ModDefDict[mod].functionalComponents.remove(temp.identity)
            r+=1
    # deleting CompDefs for any plasmids/components that are unused in all of the ModuleDefs
    funclist = ''
    toRemove = []
    for mod in ModDefDict:
        funcs = ModDefDict[mod].functionalComponents
        for func in funcs:
            funclist = funclist + func.identity
    for comp in CompDefDict:
        if comp not in funclist:
            doc.componentDefinitions.remove(CompDefDict[comp].identity)
            toRemove.append(comp)
    for rem in toRemove:
        del CompDefDict[rem]
    return 0

# creating a Collection containing all the objects in the Document (Experiment Collection) and either adding it to an existing Project Collection or creating a new Project Collection. Logging in and uploading everything to SynBioHub
def UploadFunc(username, password, experimentID, experimentName, experimentDescription, projectURI, doc):
    shop = PartShop('https://synbiohub.org')
    try:
        shop.login(username, password)
    except RuntimeError as e:
        print(e)
        return(0)
    subcollection = Collection(experimentID)
    subcollection.name = experimentName
    subcollection.description = experimentDescription
    uriList = [obj.identity for obj in doc]
    subcollection.members = subcollection.members + uriList
    doc.addCollection(subcollection)
    try:
        result = shop.submit(doc,projectURI,2) # 2 means merge
        # took 1 min 13 seconds on 08/02
        print(result)
        if result == 'Submission successful' or result == 'Successfully uploaded':
            return(2)
    except RuntimeError as e:
        e = str(e)
        if e == 'HTTP post request failed with: Submission id and version does not exist':
            return(1)
        else:
            print(e)
            subcollection = doc.collections.remove(subcollection.identity)
            return(0)


# uploader if the user is creating a new Project Collection
def NewProjUpload(username, password, doc):
    shop = PartShop('https://synbiohub.org')
    # took 1 min 19 seconds on 08/02
    shop.login(username, password)
    result = shop.submit(doc)
    print(result)
    return(0)


# calls Google API and adds all existing Reagents, Strains, and Genetic Constructs into a local dictionary that can be searched later
# taken from Google Sheets example API call: https://developers.google.com/sheets/api/quickstart/python
def LCPDictionaryCaller():
    existingNamesDict = {}
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    # The ID and range of a sample spreadsheet.
    SPREADSHEET_ID = '1bo34Knob4ihKBY6eWFhxpUTkyHXYzylv8yiMZvhFq5M'
    RANGE_NAME = '!A2:H'

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    for sheetName in ['Reagent','Strain','Genetic Construct']:
        RANGE_NAME = sheetName + '!A2:I'
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId = SPREADSHEET_ID,
                                    range = RANGE_NAME).execute()
        
        values = result.get('values', [])
        colHeaders = values[0]
        uidNums = []
        for i in range(0,len(colHeaders)):
            if colHeaders[i] == 'Common Name':
                nameNum = i
            if colHeaders[i] == 'SynBioHub URI':
                uriNum = i
            if 'UID' in colHeaders[i]:
                uidNums.append(i)
        # looping through each row and adding to existingNamesDict
        for r in range(1,len(values)):
            currList = values[r]
            if currList[nameNum] != '':
                existingNamesDict[currList[nameNum]] = currList[uriNum]
                for num in uidNums:
                    if currList[num] != '':
                        if ',' in currList[num]: # parses a list of UID's that are separated by a comma into separate entries
                            tempkeylist = currList[num].split(',')
                            for tempkey in tempkeylist:
                                if tempkey[0] == ' ': # getting rid of any spaces that might have remained after the parsing
                                    tempkey = tempkey[1:] 
                                existingNamesDict[tempkey] = currList[uriNum]
                        else:
                            existingNamesDict[currList[num]] = currList[uriNum]
    return existingNamesDict