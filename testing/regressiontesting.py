import os
import sys
from sbol import *

TESTINGDIR = os.path.dirname(os.path.abspath(__file__))
PARENTDIR = os.path.dirname(TESTINGDIR)
sys.path.insert(0,PARENTDIR)

import SBOLconverter as py

#testing that Excel sheet is able to open
#testfile = './testing/SBOL_Sample_test.xlsm'

# ^^^ IMP ^^^

global doc1
doc1 = Document()
global doc2
doc2 = Document()

testfile1 = 'SBOL_Sample_test_1.xlsm'
testfile2 = 'SBOL_Sample_test_2.xlsm'

expname1 = 'Test Experiment 1'
expname2 = 'Test Experiment 2'

unit1 = 'ng'
unit2 = 'ng'

modlist1 = ['A','B','C','D','E','F']
newmodlist1 = ['Test_Experiment_1_codenameA', 'Test_Experiment_1_codenameB', 'Test_Experiment_1_codenameC', 'Test_Experiment_1_codenameD', 'Test_Experiment_1_codenameE', 'Test_Experiment_1_codenameF']
#modlist2
#newmodlist2

plasmidlist1 = ['pBW465', 'pBW2139', 'pBW339', 'pBW586', 'pBW2909', 'pLC41', 'pLC20', 'BW363', 'pBW465', 'pBW2139', 'pBW339', 'pBW586', 'pBW2909', 'pLC41', 'pLC20', 'BW363']
plasmidlist1_norepeats = ['pBW465', 'pBW2139', 'pBW339', 'pBW586', 'pBW2909', 'pLC41', 'pLC20', 'BW363']
#plasmidlist2
#plasmidlist2_norepeats

def ExpInfoTest(testfile, expname, unit):
    # locating Excel file
    wb = py.MakeBook(testfile)
    assert wb

    # testing that Experiment Name and the sheet with Experimental Data can be found
    ExperimentSheetName = 'Experiment DNA sample'
    ExpSheet = py.ExpSheetFinder(wb,ExperimentSheetName)
    assert ExpSheet
    ExpName = py.ExpNameFinder(wb)
    assert ExpName == expname

    # testing that Unit can be found
    Unit = py.UnitCollectionFunc(ExpSheet)
    assert Unit == unit

    # needed for the rest of the tests
    return ExpSheet


def PlasModTest(modlist, newmodlist, plasmidlist_repeats, plasmidlist_norepeats, expname, ExpSheet):
    # testing that the list of Modules and the list of all Plasmids is extracted
    (ModList,PlasmidList_orig) = py.PlasModList(ExpSheet)
    assert ModList == modlist
    assert PlasmidList_orig == plasmidlist_repeats

    # testing that all repeats in Plasmid list are removed
    PlasmidList_norepeat = py.PlasNoRepeat(PlasmidList_orig)
    assert PlasmidList_norepeat == plasmidlist_norepeats

    # testing that the Module List is in a format supported by SynBioHub and that the Experiment Name is properly attached to each Module
    newModList = py.ModListCleaner(modlist,expname)
    assert newModList == newmodlist


"""
SOME NOTES
"""
"""
    - systematically check for irregular character names
    - make sure to check the function where it makes sure that no two modules have the same name
    - don't assume that the variable already exists 
    - put each call to test the SBOLconverter functions into a seperate function in this document
    - think about having multiple Excel spreadsheet test documents, with different module configurations
    (stretch the limit of how Modules are being found in the document)
    - design the test Excel documents in a logical manner
"""

def ModuleDefinitionTest(modlist,newmodlist,ExpSheet,doc):
    ModDefDict = py.ModMaker(modlist, newmodlist, ExpSheet, doc)
    # checking that the ModuleDef dictionary contains all the modules in the module list
    assert list(set(ModDefDict.keys()) - set(newmodlist)) == []
    for newmod in newmodlist:
        # checking that the type stored in the ModuleDef dictionary is a ModuleDefinition
        assert type(ModDefDict[newmod]) == py.sbol.libsbol.ModuleDefinition


#testing that the Samples Tab Modules are correctly created
# def SamplesTest(wb,samplesheet,samplelist):
#     SampleSheet = py.SamplesSheetFinder(wb)
#     (SampleList, SampleDescriptions) = py.SampleListDesc(SampleSheet)
#     ConditionDictionary = py.SampleExpConditions(SampleSheet, SampleList)
#     (SampleModDefDict, newSampleList) = py.SampleModMaker(SampleSheet,SampleList,SampleDescriptions,ConditionDictionary,ExpName,doc)


#assert number of module defs in the document = number of samples


# CompDefDict = py.CompMaker(PlasmidList_norepeat)
# if CompDefDict:
#     print('Test 9/10: creating ComponentDefinition for each plasmid type and adding description successful...')
#     testcounter +=1

# FunctionalCompOutput = py.FuncMaker(NewModList,ModList,ExpSheet,CompDefDict,ModDefDict,Unit)
# if FunctionalCompOutput == 0:
#     print('Test 10/10: creating FunctionalComponents for each plasmid present in a Module, adding Annotations successful...')
#     testcounter +=1

# #ret = UploadFunc(username,password,projectID,projectName,projectDescription,experimentID,experimentName,experimentDescription,colURI)
# #if ret #can be 0,1,or 2:

# #need to test all the upload functions


ExpSheet1 = ExpInfoTest(testfile1, expname1, unit1)
ExpSheet2 = ExpInfoTest(testfile2, expname2, unit2)

PlasModTest(modlist1, newmodlist1, plasmidlist1, plasmidlist1_norepeats, expname1, ExpSheet1)
#PlasModTest(modlist2, newmodlist2, plasmidlist2, plasmidlist2_norepeats, expname2, ExpSheet2)

ModuleDefinitionTest(modlist1, newmodlist1, ExpSheet1, doc1)
#ModuleDefinitionTest(modlist2, newmodlist2, ExpSheet2, doc2)

