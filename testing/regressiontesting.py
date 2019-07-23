import SBOLconverter as py

#testing that Excel sheet is able to open
testfile = './testing/SBOL_Sample_test.xlsm'
wb = py.MakeBook(testfile)
assert wb

#testing that Experiment Name and the sheet with Experimental Data is able to be found
ExperimentalSheetName = 'Experiment DNA sample'
(ExpName, ExpSheet) = py.ExcelImport(wb,ExperimentalSheetName) 
assert ExpName == 'Test Experiment'
assert ExpSheet

#testing that Unit can be found
Unit = py.UnitCollectionFunc(ExpSheet)
assert Unit == 'ng'

#testing that the list of Modules and all Plasmids is extracted
(ModList,PlasmidList_orig) = py.PlasModList(ExpSheet)
assert ModList == ['A','B','C','D','E','F']
assert PlasmidList_orig == ['pBW465', 'pBW2139', 'pBW339', 'pBW586', 'pBW2909', 'pLC41', 'pLC20', 'BW363', 'pBW465', 'pBW2139', 'pBW339', 'pBW586', 'pBW2909', 'pLC41', 'pLC20', 'BW363']

#testing that all repeats in Plasmid list are removed
PlasmidList_norepeat = py.PlasNoRepeat(PlasmidList_orig)
assert PlasmidList_norepeat == ['pBW465', 'pBW2139', 'pBW339', 'pBW586', 'pBW2909', 'pLC41', 'pLC20', 'BW363']

#testing that the Module List is in a format supported by SynBioHub and that the Experiment Name is properly attached to each Module
ModList = ['A','B','C','D','E','F']
ExpName = 'Test Experiment'
NewModList = py.ModListCleaner(ModList,ExpName)
assert NewModList == ['Test_Experiment_codenameA', 'Test_Experiment_codenameB', 'Test_Experiment_codenameC', 'Test_Experiment_codenameD', 'Test_Experiment_codenameE', 'Test_Experiment_codenameF']

#testing that ModulesDefinitions are correctly created for each Module
ModList = ['A','B','C','D','E','F']
NewModList == ['Test_Experiment_codenameA', 'Test_Experiment_codenameB', 'Test_Experiment_codenameC', 'Test_Experiment_codenameD', 'Test_Experiment_codenameE', 'Test_Experiment_codenameF']
ModDefDict = py.ModMaker(ExpSheet,ModList,NewModList)
assert list(set(ModDefDict.keys()) - set(NewModList)) == 0
for newmod in NewModList:
    assert type(ModDefDict[newmod]) == ModuleDefinition

# SamplesOutput = py.SamplesImport(ModList,NewModList,ModDefDict,wb,ExpName)
# if SamplesOutput == 0:
#     print('Test 8/10: creating Module Definitions for each Sample in the Samples tab, adding Annotations for each Experimental Condition successful...')
#     testcounter +=1

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

# if testcounter == 10:
#     print('All tests passed.')

# #need to test all the upload functions
