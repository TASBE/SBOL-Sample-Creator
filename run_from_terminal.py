from __future__ import print_function

from sbol import *
import re
import sys
import xlrd
import getpass
import SBOLconverter as py

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from synbiohub_adapter.upload_sbol import SynBioHub


global doc
doc = Document()
setHomespace('http://bu.edu/dasha')
Config.setOption('sbol_typed_uris',False)
Config.setOption('sbol_compliant_uris',True)

file_location = input('Enter the name of your file, including the extension: ')

ExperimentSheetName = 'Experiment DNA sample'

# extracting experiment information
wb = py.MakeBook(file_location)
ExpSheet = py.ExpSheetFinder(wb,ExperimentSheetName)
ExpName = py.ExpNameFinder(wb)
ConditionKeyDict = py.ConditionKeyExtractor(wb)
Unit = py.UnitCollectionFunc(ExpSheet)

# extracting plasmid and DNA mix information
(ModList,PlasmidList_orig) = py.PlasModList(ExpSheet)
PlasmidList_norepeat = py.PlasNoRepeat(PlasmidList_orig)

# extracting list of all Reagents, Strains, and Genetic Constructs present in the LCP Dictionary
existingNamesDict = py.LCPDictionaryCaller()

# creating ModuleDefinitions for DNA mixes
newModList = py.ModListCleaner(ModList,ExpName)
ModDefDict = py.ModMaker(ModList,newModList,ExpSheet,doc)

# creating ModuleDefinitions for Samples
SampleSheet = py.SamplesSheetFinder(wb)
(SampleList, SampleDescriptions) = py.SampleListDesc(SampleSheet)
ConditionDictionary = py.SampleExpConditions(SampleSheet, SampleList)
(SampleModDefDict, newSampleList, notInDict) = py.SampleModMaker(SampleSheet,SampleList,SampleDescriptions,ConditionDictionary,ExpName,existingNamesDict,ConditionKeyDict,doc)

# Adding DNA mix reference to each Sample, creating ComponentDefinitions for each plasmid
py.ModAdder(SampleList,newSampleList,SampleModDefDict,ModList,newModList,ModDefDict,ConditionDictionary)
(CompDefDict,notInDict2) = py.CompMaker(PlasmidList_norepeat,existingNamesDict,doc)

# creating FunctionalComponents for each plasmid within each DNA mix
py.FuncMaker(ModList, newModList, ModDefDict, CompDefDict, ExpSheet, Unit, doc)

# getting user input for collection information
projectID = input('Enter the project collection displayID: ')
projectName = input('Enter the project collection name: ')
projectDescription = input('Enter the project collection description: ')
projectVersion = input('Enter the project collection version (1.0.0 or 1): ')

experimentID = input('Enter the experiment collection displayID: ')
experimentName = input('Enter the experiment collection name: ')
experimentDescription = input('Enter the experiment collection description: ')

# logging into SynBioHub and uploading collection information
username = input('Enter your SynBioHub username: ')
password = getpass.getpass(prompt='Enter your SynBioHub password: ')
sbh = py.LoginFunc(username,password)
sep = '@'
rest = username.split(sep, 1)[0]
projectURI = "https://synbiohub.org/user/" + rest + "/" + projectID + "/" + projectID + "_collection/" + projectVersion
retVal = py.UploadFunc(sbh, experimentID, experimentName, experimentDescription, projectID, projectName, projectDescription, projectVersion, projectURI, doc)
if retVal == 1:
       print('project and collection ids are already in use, do you want to replace it ?')

       print('No project with the displayID "{}" found.'.format(projectID))
       answer = input('Do you want to create a new project with this displayID? (y/n)')
       if answer == 'y':
              formatlist = [projectID,experimentID]
              print('Creating a new project with displayID "{}" containing an experiment with displayID "{}".'.format(*formatlist))
              doc.displayId = projectID
              doc.name = projectName
              doc.description = projectDescription
              doc.version = projectVersion
              py.NewProjUpload(username,password,doc)
              print(projectURI)
              sys.exit()
       elif answer == 'n':
              print('Upload stopped.')
              sys.exit()
elif retVal == 2:
       print(projectURI)
       sys.exit()
else:
       sys.exit()

"""
SOME NOTES
"""
"""
    - systematically check for irregular character names
    - make sure to check the function where it makes sure that no two modules have the same name
    - don't assume that the variable already exists 
    - think about having multiple Excel spreadsheet test documents, with different module configurations
       (stretch the limit of how Modules are being found in the document)
    - design the test Excel documents in a logical manner
    - figure out how to check if a user has the exact same experiment and project combo already on SynBioHub, then overwrite it if they say yes

       WHY IS IT TAKING SO GODDAMN LONG TO UPLOAD EVERYTHING???
"""