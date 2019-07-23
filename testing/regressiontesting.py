import SBOLconverter as py

testfile = './testing/SBOL_Sample_test.xlsm'
wb = py.MakeBook(testfile)
assert wb

(ExpName, ExpSheet) = py.ExcelImport(wb) 
assert ExpName == 'Test Experiment'
assert ExpSheet

Unit = py.UnitCollectionFunc(ExpSheet)
assert Unit == 'ng'

(ModList,PlasmidList_orig) = py.PlasModList(ExpSheet)
assert ModList == ['A','B','C','D','E','F']
assert PlasmidList_orig == ['pBW465', 'pBW2139', 'pBW339', 'pBW586', 'pBW2909', 'pLC41', 'pLC20', 'BW363', 'pBW465', 'pBW2139', 'pBW339', 'pBW586', 'pBW2909', 'pLC41', 'pLC20', 'BW363']
# if (ModList,PlasmidList_orig):
#     print('Test 4/10: creating list of Modules and plasmids successful...')
#     testcounter +=1

# PlasmidList_norepeat = py.PlasNoRepeat(PlasmidList_orig)
# if PlasmidList_norepeat:
#     print('Test 5/10: creating non-repeating list of plasmids successful...')
#     testcounter +=1

# NewModList = py.ModListCleaner(ModList,ExpName)
# if NewModList:
#     print('Test 6/10: creating SBOL-compliant list of Modules successful...')
#     testcounter +=1

# ModDefDict = py.ModMaker(ExpSheet,ModList,NewModList)
# if ModDefDict:
#     print('Test 7/10: creating ModuleDefinitions and dictionary of Modules successful...')
#     testcounter +=1

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
