import os
import sys
from sbol import *

TESTINGDIR = os.path.dirname(os.path.abspath(__file__))
PARENTDIR = os.path.dirname(TESTINGDIR)
sys.path.insert(0,PARENTDIR)

import SBOLconverter as py

#testing that Excel sheet is able to open

global doc1
doc1 = Document()
global doc2
doc2 = Document()

# testing two different Excel files
testfile1 = 'testing/SBOL_Sample_test_1.xlsm'
testfile2 = 'testing/SBOL_Sample_test_2.xlsm'

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

samplelist1 = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0]
sampledescriptions1 = ['Test 0.01', 'Test 0.02', 'Test 0.05', 'Test 0.1', 'Test 0.2', 'Test 0.5', 'Test 1', 'Test 2', 'Test 5', 'Test 10', 'Test 20', 'Test 50', 'Test 100', 'Test 200', 'Test 500', 'Test 1000', 'Test 2000', 'Test 5000', 'Beads', 'red', 'blue', 'Blank', 'GFP']
# samplelist2 =
# sampledescriptions2 =

expconditions1 = ['DOX', 'DOSE', 'Code', 'BaseDox', '10xDox']
# expconditions2 = 

"""
DEFINING THE TESTING FUNCTIONS
"""

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
    return (wb, ExpSheet)


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


def ModuleDefTest(modlist, newmodlist, ExpSheet, doc):
    ModDefDict = py.ModMaker(modlist, newmodlist, ExpSheet, doc)
    # checking that the ModuleDef dictionary contains all the modules in the module list
    assert list(set(ModDefDict.keys()) - set(newmodlist)) == []
    for newmod in ModDefDict:
        # checking that the type stored in the ModuleDef dictionary is a ModuleDefinition
        assert type(ModDefDict[newmod]) == py.sbol.libsbol.ModuleDefinition
    return ModDefDict


def SamplesTest(wb, modlist, newmodlist, moddict, samplelist, sampledescriptions, expconditions, expname, doc):
    # locating "Samples" sheet 
    SampleSheet = py.SamplesSheetFinder(wb)
    assert SampleSheet

    # extracting the list of Samples and their corresponding descriptions
    (SampleList, SampleDescriptions) = py.SampleListDesc(SampleSheet)
    assert SampleList == samplelist
    assert SampleDescriptions == sampledescriptions

    # creating a dictionary storing all experimental conditions
    ConditionDictionary = py.SampleExpConditions(SampleSheet, SampleList)
    assert len(ConditionDictionary) <= 5
    assert list(set(ConditionDictionary.keys()) - set(expconditions)) == []

    # creating a dictionary of Sample Modules, with a list of ExpName and Sample Number concatenated together
    (SampleModDefDict, newSampleList) = py.SampleModMaker(SampleSheet,SampleList,SampleDescriptions,ConditionDictionary,expname,doc)
    assert len(SampleModDefDict) == len(SampleList)
    assert list(set(SampleModDefDict.keys()) - set(newSampleList)) == []
    for sample in newSampleList:
        # checking that the type stored in the ModuleDef dictionary is a ModuleDefinition
        if expname in sample:
            assert True
        assert type(SampleModDefDict[sample]) == py.sbol.libsbol.ModuleDefinition

    # first checking that there are no Modules associated with each Sample ModuleDefinition
    testmodlist = []
    for sample in SampleModDefDict:
        mods = SampleModDefDict[sample].modules.getAll()
        for mod in mods:
            testmodlist.append(mod)
    assert testmodlist == []

    # adding a Module corresponding to the DNA mix used in each sample to each Sample ModuleDef
    ret = py.ModAdder(SampleList, newSampleList, SampleModDefDict, modlist, newmodlist, moddict, ConditionDictionary)
    assert ret == 0
    
    # making sure that some of the Samples now have Modules
    for sample in SampleModDefDict:
        mods = SampleModDefDict[sample].modules.getAll()
        for mod in mods:
            testmodlist.append(mod)
    assert testmodlist != []
    for test in testmodlist:
        assert type(test) == py.sbol.libsbol.Module


def CompTest(plasmidlist_norepeats, doc):
    CompDefDict = py.CompMaker(plasmidlist_norepeats,doc)
    # checking that the CompDef dictionary contains all the plasmids in the plasmid list
    assert list(set(CompDefDict.keys()) - set(plasmidlist_norepeats)) == []
    # checking that the type stored in the CompDef dictionary is a ComponentDefiniiton
    for comp in CompDefDict:
        assert type(CompDefDict[comp]) == py.sbol.libsbol.ComponentDefinition 
    # later add an assert that checks whether the Google API correctly extracted existing plasmid URI info
    return CompDefDict


def FuncTest(modlist, newmodlist, moddict, compdict, expsheet, unit, doc):
    # there should be no functionalComponents before the function is called
    for mod in moddict:
        funcComps = moddict[mod].functionalComponents.getAll()
        assert funcComps == []
    ret = py.FuncMaker(modlist, newmodlist, moddict, compdict, expsheet, unit)
    assert ret == 0
    # making sure the ModuleDefinitions now have FunctionalComponents
    for mod in moddict:
        funcComps = moddict[mod].functionalComponents.getAll()
        assert funcComps != []
        for func in funcComps:
            assert type(func) == py.sbol.libsbol.FunctionalComponent


"""
CALLING THE TESTING FUNCTIONS
"""
(wb1,expsheet1) = ExpInfoTest(testfile1, expname1, unit1)
(wb2,expsheet2) = ExpInfoTest(testfile2, expname2, unit2)

PlasModTest(modlist1, newmodlist1, plasmidlist1, plasmidlist1_norepeats, expname1, expsheet1)
#PlasModTest(modlist2, newmodlist2, plasmidlist2, plasmidlist2_norepeats, expname2, ExpSheet2)

moddict1 = ModuleDefTest(modlist1, newmodlist1, expsheet1, doc1)
#moddict2 = ModuleDefTest(modlist2, newmodlist2, ExpSheet2, doc2)

SamplesTest(wb1,modlist1,newmodlist1,moddict1,samplelist1,sampledescriptions1,expconditions1,expname1,doc1)
# SamplesTest(wb2,modlist2,newmodlist2,moddict2,samplelist2,sampledescriptions2,expconditions2,expname2,doc2)

compdict1 = CompTest(plasmidlist1_norepeats, doc1)
# compdict2 = CompTest(plasmidlist2_norepeats, doc2)

FuncTest(modlist1, newmodlist1, moddict1, compdict1, expsheet1, unit1, doc1)
# FuncTest(modlist2, newmodlist2, moddict2, compdict2, expsheet2, unit2, doc2)


