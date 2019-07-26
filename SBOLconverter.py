# Uncomment all import statements if NOT running with Jupyter Notebook
# Follow README for installation instructions

"""""
EXCEL IMPORT
"""""

from sbol import *
import re
import sys
import xlrd
import getpass

# global doc
# doc = Document()
# setHomespace('http://bu.edu/dasha')
# Config.setOption('sbol_typed_uris',False)
# Config.setOption('sbol_compliant_uris',True)

# creating a variable representing the Excel file
def MakeBook(file_location):
    wb = xlrd.open_workbook(file_location)
    return wb


# extracting experiment name from "Experiment" sheet and making sure there is a sheet named "Experiment DNA sample"
def ExpSheetFinder(wb, ExperimentSheetName):
    try:
        ExperimentSheet = wb.sheet_by_name(ExperimentSheetName)
    except:
        print('Error: No sheet named {} detected.'.format(ExperimentSheetName))
        return(-1)
    return(ExperimentSheet)

def ExpNameFinder(wb):
    NameSheet = wb.sheet_by_name('Experiment')
    LookingFor = 'Experiment Name'
    for r in range(0,NameSheet.nrows):
        cell_obj = NameSheet.cell(r,0)
        if (cell_obj.value == LookingFor):
            break
        else:
            r+=1
    if (r == NameSheet.nrows):
        print('Error: Experiment name not found in file. It must be in the first column of the "Experiment" sheet under the "Experiment Name" header.')
        return(-1)
    else:
        r+=1
        ExperimentName = (NameSheet.cell(r,0)).value
    return(ExperimentName)


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

# finding Sample sheet and extracting Sample List and Sample Descriptions
def SamplesSheetFinder(wb):
    try:
        SampleSheet = wb.sheet_by_name('Samples')
    except:
        print('Error: No sheet named "Samples" detected.')
        return(-1)
    return SampleSheet

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

# creating ModuleDefinitions for each Sample listed in the Samples Tab, and creating annotations for each Sample by getting information about Experimental Conditions

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

# creating Module Defs
def SampleModMaker(SampleSheet, SampleList, SampleDescriptions, ConditionDictionary, ExperimentName,doc):
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
        # creating annotations with Dox symbol, time, and any other experimental conditions listed
        for cond in ConditionDictionary:
            tempURI = temp.identity + '#' + cond
            value = (ConditionDictionary[cond])[val]
            if value != '':
                if is_number(value):
                    stringval = '%s' % float('%6g' % value)
                    # at most 6 significant figures
                    temp.setAnnotation(tempURI,stringval)
                else:
                    stringval = value
                    temp.setAnnotation(tempURI,stringval)
    return (SampleModDefDict, newSampleList)

# NEXT STEP: have the computer extract information about the condition keys (aka each explanation) so that when adding annotation it can be added as 0 ng instead of - or 100 ng instead of +
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
                    if codename == ModList[mod]:
                        displayID = newModList[mod]
                        test = ModDef.modules.create(displayID)
                        otherMD = ModDefDict[displayID]
                        test.definition = otherMD.identity
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

# creating ComponentDefinition for each plasmid type and adding description, key is the displayID and value is the CD
def CompMaker(PlasmidList_norepeat,doc):
    CompDefDict = {}
    # populating Component Dictionary
    for val in range(0,len(PlasmidList_norepeat)):
        displayID = PlasmidList_norepeat[val]
        existingNames = DictionaryNamesFinder()
        for name in existingNames:
            if displayID != name:
                temp = ComponentDefinition(displayID,BIOPAX_DNA) # encodes all plasmids as type BIOPAX_DNA
                CompDefDict[displayID] = temp
            #else:
                # add statememnts that find the URI of the existing part, then add it to the component dictionary
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
def FuncMaker(ModList, newModList, ModDefDict, CompDefDict, ExperimentSheet, Unit):
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
                valueURI = temp.identity + '#hasNumericalValue'
                value = (ExperimentSheet.cell(r,col)).value
                if value != '':
                    stringval = '%s' % float('%6g' % value)
                    # at most 6 significant figures
                    temp.setAnnotation(valueURI,stringval)
                    # temp.hasNumericalValue = FloatProperty(temp,'http://bu.edu/dasha/#hasNumericalValue','0','1')
                    # temp.hasNumericalValue = 10.0
                    # ^new way to create annotations, work in progress
                    unitsURI = temp.identity + '#hasUnit'
                    temp.setAnnotation(unitsURI,Unit)
                elif value == '':
                    ModDefDict[mod].functionalComponents.remove(temp.identity)
            r+=1
    return 0


# creating a Collection containing all the objects in the Document (Experiment Collection) and either adding it to an existing Project Collection or creating a new Project Collection. Logging in and uploading everything to SynBioHub
def UploadFunc(username, password, experimentID, experimentName, experimentDescription, projectURI, doc):
    shop = PartShop('https://synbiohub.org')
    shop.login(username, password)
    subcollection = Collection(experimentID)
    subcollection.name = experimentName
    subcollection.description = experimentDescription
    uriList = [obj.identity for obj in doc]
    subcollection.members = subcollection.members + uriList
    doc.addCollection(subcollection)
    result = shop.submit(doc,projectURI,2) # 2 means merge
    if result == 'Submission id and version does not exist':
        return(1)
    elif result == 'Submission successful' or result == 'Successfully uploaded':
        return(2)
    else:
        print(result)
        subcollection = doc.collections.remove(subcollection.identity)
        return(0)


# uploader if the user is creating a new Project Collection
def NewProjUpload(username, password, doc):
    shop = PartShop('https://synbiohub.org')
    shop.login(username, password)
    result = shop.submit(doc)
    print(result)
    return(0)


#new function to call Google API and check if the LCP dictionary has the component
"""
ALSO!! NEED TO ADD DOX AS A FUNCTIONAL COMPONENT BECAUSE IT IS PART OF THE MIX
"""

def DictionaryNamesFinder():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_info.json', scope)
    client = gspread.authorize(creds)

    #opening the spreadsheet
    spreadsheet = client.open("LCP Project Dictionary")
    worksheetNames = ['Reagent', 'Strain', 'Genetic Construct']
    existingNames = []
    for sheetName in worksheetNames:
        currentSheet = spreadsheet.worksheet(sheetName)
        currentInfo = currentSheet.get_all_records(False,2,'',False)
        if len(currentInfo) != 0:
            for index in range(0,len(currentInfo)):
                currentDictionary = currentInfo[index]
                existingNames.append(currentDictionary['Common Name'])
                keysList = currentDictionary.keys()
                for key in keysList:
                    if 'UID' in key and currentDictionary[key] is not '':
                        existingNames.append(currentDictionary[key])
    return existingNames
                

    # figure out what you are searching the dictionary for -- definitely plasmids, but also reagents and strians
    # maybe you should have 3 functions:
    # -- one that searches for plasmids, taking the plasmid list as input
    # -- one that searches for reagents, taking the experimental conditions list as input
    # -- one that searches for strains, (what even is that?)
    # They all return an array of any matching items, with item displayID (as defined by the user) and the item URI (as defined by LCP)

    # maybe create a dictionary that is an array of dictionaries, each containing first 

    #def NameFinder(sheet,partList):
    #    for part in partList:
    #        sheet.find(part)


    # Extract and print all of the values
    #sheet1 = spreadsheet.
    #list_of_hashes = sheet.get_all_values()
    #print(list_of_hashes)


    #sheet called 'Genetic Construct' and 'Reagant'

