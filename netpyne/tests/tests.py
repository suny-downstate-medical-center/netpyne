"""
test_validate.py

Testing code for Validation class

Contributors: mitra.siddhartha@gmail.com
"""

import unittest
import numbers
import sys
import os
import traceback
import numpy

from netpyne import utils

VALID_SHAPES = ['cuboid', 'ellipsoid', ' cylinder']
POP_NUMCELLS_PARAMS = ['Density','NumCells','GridSpacing']
VALID_GEOMETRIES = ['cm', 'L', 'diam', 'Ra', 'pt3d']
VALID_GEOMETRIES_SUBSET = ['L', 'diam', 'Ra']
PT_3D = 'pt3d'
VALID_TOPOLOGY_PARAMS = ['parentSec', 'parentX','childX']

MESSAGE_TYPE_WARNING = "WARNING"
MESSAGE_TYPE_ERROR = "ERROR"
MESSAGE_TYPE_INFO = "INFO"

TEST_TYPE_EXISTS = "testExists" # parameter must exist
TEST_TYPE_EXISTS_IN_LIST = "Exists in list" # ex. one of paremters number, density, gridspacing must be specified
TEST_TYPE_IS_VALID_RANGE = "Is Valid Range" # like [0,1]
TEST_TYPE_IN_RANGE = "In Range" # ex. xnormRange must be between 0 and 1

TEST_TYPE_EQ = "Equal to" # ex. equal to

TEST_TYPE_GT = "Greater than" # ex. greater than
TEST_TYPE_GTE = "Greater than or equal to" # ex. greater than or equal to

TEST_TYPE_GT_ZERO = "Greater than zero" # ex. greater than
TEST_TYPE_GTE_ZERO = "Greater than or equal to zero" # ex. greater than or equal to

TEST_TYPE_LT = "Lesser than" # ex. lesser than
TEST_TYPE_LTE = "Lesser than or equal to" # ex. lesser than or equal to

TEST_TYPE_LT_ZERO = "Lesser than zero" # ex. lesser than
TEST_TYPE_LTE_ZERO = "Lesser than or equal to zero" # ex. lesser than or equal to

TEST_TYPE_IS_DICT = "Is dictionary" # must be a dictionary

TEST_TYPE_IS_NUMERIC = "Is Numeric" # must be numeric
TEST_TYPE_IS_FLOAT = "Is Float" # must be float
TEST_TYPE_IS_INT = "Is Integer" # must be integer
TEST_TYPE_IS_CHARACTER = "Is Character" # must be char [a-z][A-Z]
TEST_TYPE_VALUE_LIST = "Value List" # must be in valid values list
TEST_TYPE_EXISTS_IN_DICT = "Exists in Dict" # input param must exist in dict
TEST_TYPE_EXISTS_IN_NESTED_DICT = "Exists in nested dict" # input param must exist in nested dict
TEST_TYPE_SPECIAL = "Special" # special method, method name provided
TEST_TYPE_EXISTS_IN_ALL_DICTS = "Exists in all dicts"

TEST_TYPE_VALID_GEOMETRIES = "Valid geometries"
TEST_TYPE_VALID_TOPOLOGIES = "Valid topologies"
TEST_TYPE_VALID_MECHS = "Valid mechs"
TEST_TYPE_VALID_IONS = "Valid ions"
TEST_TYPE_VALID_POINTPS = "Valid pointps"

TEST_TYPE_VALID_CONN_LIST = "Valid conn list"

TEST_TYPE_VALID_SYN_MECHS = "Valid synaptic mechanisms"
TEST_TYPE_ARRAY_IN_RANGE = "Array elements in range"

TEST_TYPE_EXISTS_IN_POP_LABELS = "Exists in pop labels"
TEST_TYPE_VALID_SEC_LIST = "Valid sec list for conn"
TEST_TYPE_CONN_PARM_HIERARCHY = "Check for parameter hierarchy"
TEST_TYPE_CONN_SHAPE = "Check for shape in conn params"
TEST_TYPE_CONN_PLASTICITY = "Check for shape in conn plasticity"
TEST_TYPE_STIM_SOURCE_TEST = "Stim target test"
TEST_TYPE_STIM_TARGET_TEST = "Stim source test"
TEST_TYPE_IS_VALID_SPIKE_GENLOC = "Spike gen loc"

testFunctionsMap = {}

testFunctionsMap [TEST_TYPE_EXISTS] = "testExists"
testFunctionsMap [TEST_TYPE_EXISTS_IN_LIST] = "testExistsInList"
testFunctionsMap [TEST_TYPE_IS_VALID_RANGE] = "testIsValidRange"
testFunctionsMap [TEST_TYPE_IN_RANGE] = "testInRange"
testFunctionsMap [TEST_TYPE_EQ] = "testEquals"

testFunctionsMap [TEST_TYPE_GT] = "testGt"
testFunctionsMap [TEST_TYPE_GTE] = "testGte"
testFunctionsMap [TEST_TYPE_GTE_ZERO] = "testGteZero"

testFunctionsMap [TEST_TYPE_LT] = "testGt"
testFunctionsMap [TEST_TYPE_LTE] = "testGte"
testFunctionsMap [TEST_TYPE_LTE_ZERO] = "testGteZero"

testFunctionsMap [TEST_TYPE_VALUE_LIST] = "testExists"

testFunctionsMap [TEST_TYPE_EXISTS_IN_LIST] = "testExistsInList"
testFunctionsMap [TEST_TYPE_EXISTS_IN_DICT] = "testExistsInDict"
testFunctionsMap [TEST_TYPE_EXISTS_IN_ALL_DICTS] = "testExistsInAllDicts"

testFunctionsMap [TEST_TYPE_VALID_GEOMETRIES] = "testValidGeometries"
testFunctionsMap [TEST_TYPE_VALID_TOPOLOGIES] = "testValidTopologies"

testFunctionsMap [TEST_TYPE_VALID_MECHS] = "testValidMechs"
testFunctionsMap [TEST_TYPE_VALID_IONS] = "testValidIons"
testFunctionsMap [TEST_TYPE_VALID_POINTPS] = "testValidPointps"
testFunctionsMap [TEST_TYPE_VALID_SYN_MECHS] = "testValidSynMechs"
testFunctionsMap [TEST_TYPE_ARRAY_IN_RANGE] = "testArrayInRange"

testFunctionsMap [TEST_TYPE_EXISTS_IN_POP_LABELS] = "testExistsInPopLabels"
testFunctionsMap [TEST_TYPE_VALID_SEC_LIST] = "testValidSecLists"

testFunctionsMap [TEST_TYPE_VALID_CONN_LIST] = "testValidConnList"
testFunctionsMap [TEST_TYPE_CONN_PARM_HIERARCHY] = "testTypeHierarchy"
testFunctionsMap [TEST_TYPE_CONN_SHAPE] = "testValidConnShape"
testFunctionsMap [TEST_TYPE_CONN_PLASTICITY] = "testValidConnPlasticity"

testFunctionsMap [TEST_TYPE_STIM_SOURCE_TEST] = "testValidStimSource"
testFunctionsMap [TEST_TYPE_STIM_TARGET_TEST] = "testValidStimTarget"

testFunctionsMap [TEST_TYPE_IS_VALID_SPIKE_GENLOC] = "testSpikeGenLoc"

class TestTypeObj(object):

    def __init__(self):

        self.testType = '' # test name
        self.params = ''
        self.errorMessages = []

    def __unicode__(self):
        return str(self.testType)

    def testExists(self, val,params):
        try:
            # print ( " val = " + str(val ) + " -- " + str(params))
            assert (val in params), val + " must be specified."
        except AssertionError as e:
            e.args += (val,)
            raise

    def testExistsInList(self, val,params):
        try:
            assert any([x in params for x in val]), " At least one of " + str(val) + " must be specified in " + str(params) + "."
        except AssertionError as e:
            e.args += (val,)
            raise

    def testExistsInDict(self, val,paramDict, dictKey):
        try:
            existsInDict = False
            #print ( " ::: in exists in dict test " + str(paramDict) + " val " + str(val))
            for key, valueDict in paramDict.items():
                # print
                #print ( " ^^^^^ ---- valueDict[dictKey] " + str(valueDict) + " val " + str(val))
                if val == valueDict[dictKey]:
                    existsInDict = True
                    break
            assert existsInDict is True, " Value " + str(val) + "exists in dictionary " + str(params) + "."
        except AssertionError as e:
            e.args += (val,)
            raise

    def testExistsInAllDicts(self, paramValues,paramKey, dictKey):
        try:
            existsInDict = True
            for key, valueDict in paramValues[paramKey].items():
                if dictKey not in valueDict:
                    existsInDict = False
                    break
            assert existsInDict is True, " Value " + str(paramKey) + "exists in dictionary " + str(paramValues) + "."
        except AssertionError as e:
            e.args += (val,)
            raise

    def testExistsInPopLabels(self, val,paramValues, popLabels):
        try:
            existsInPopLabels = False
            popLabelsSpecified = False
            #print ( " val " + str(val) + " pop labels = " + str(popLabels))
            paramPopLabel = ''
            errorMessage = ''
            if 'popLabel' in paramValues[val]:
                popLabelsSpecified = True
                #print (" 1 =  " + str(paramValues[val]['popLabel']) + " 2 = " + str(popLabels.keys()))
                if paramValues[val]['popLabel'] not in popLabels.keys():
                    errorMessage = "Pop label specified in conn params is: " + str(paramValues[val]['popLabel']) + ". This does not exist in list of pop labels = " + str(popLabels.keys()) + "."
                    return errorMessage
                # for popLabel in popLabels.keys():
                #     if paramValues[val]['popLabel'] != popLabel:
                #         print ( " --- 1 : " + str(paramValues[val]['popLabel']) + " pop label " + str(popLabel))
                #         errorMessage = "Pop label specified in conn params is: " + str(paramValues[val]['popLabel']) + ". This does not exist in list of pop labels = " + str(popLabels.keys()) + "."
                #         existsInPopLabels = False
                #         break
            #assert existsInPopLabels is True, errorMessage
        except Exception as e:
            # e.args += (e,)
            raise
        return errorMessage

    def testIsValidRange(self, val,params): # TEST_TYPE_IS_VALID_RANGE
        try:
            if val in params:
                assert (isinstance(params[val], list)) # chk if list
                assert (len(params[val]) == 2) # chk if len is 2 ( is range)
                assert ( params[val][0] < params[val][1]) # check if lower < upper value in range
        except AssertionError as e:
            e.args += (val,)
            raise

    def testInRange(self, val,range, params): # TEST_TYPE_IN_RANGE
        try:
            if val in params:
            #     print ( "************* BEFORE !!!!!!!")
                assert (params[val][0] >= range[0] and params[val][1] <= range[1])
        except AssertionError as e:
            # print ( "************* IN ERROR !!!!!!!")
            e.args += (val,)
            raise

    def testEquals(self, val,compareVal):
        try:
            assert (val == compareVal)
        except AssertionError as e:
            e.args += (val,)
            raise

    def testGt(self, val,compareVal): # TEST_TYPE_GT
        try:
            assert (val > compareVal)
        except AssertionError as e:
            e.args += (val,)
            raise

    def testGte(self, val,compareVal): # TEST_TYPE_GTE
        try:
            assert (val >= compareVal)
        except AssertionError as e:
            e.args += (val,)
            raise

    def testGteZero(self, val): # TEST_TYPE_GTE
        try:
            assert (val >= 0)
        except AssertionError as e:
            e.args += (val,)
            raise

    def testGtZero(self, val): # TEST_TYPE_GT
        try:
            assert (val > 0)
        except AssertionError as e:
            e.args += (val,)
            raise

    def testLt(self, val,compareVal): # TEST_TYPE_LT
        try:
            assert (val < compareVal)
        except AssertionError as e:
            e.args += (val,)
            raise

    def testLte(self,val,compareVal): # TEST_TYPE_LTE
        try:
            assert (val <= compareVal)
        except AssertionError as e:
            e.args += (val,)
            raise

    def testLteZero(self, val): # TEST_TYPE_LTE
        try:
            assert (val <= 0)
        except AssertionError as e:
            e.args += (val,)
            raise

    def testLtZero(self,val): # TEST_TYPE_LTE
        try:
            assert (val < 0)
        except AssertionError as e:
            e.args += (val,)
            raise

    def testIsDict(self,val): # TEST_TYPE_IS_DICT
        try:
            assert (isinstance (val,dict))
        except AssertionError as e:
            e.args += (val,)
            raise

    def testIsNumeric(self,val): # TEST_TYPE_IS_NUMERIC
        try:
            assert (isinstance (val,numbers.Number))
        except AssertionError as e:
            e.args += (val,)
            raise

    def testIsFloat(self,val): # TEST_TYPE_IS_FLOAT
        try:
            assert (isinstance (val,numbers.Real))
        except AssertionError as e:
            e.args += (val,)
            raise

    def testIsInt(self,val): # TEST_TYPE_IS_INT
        try:
            assert (isinstance (val,int))
        except AssertionError as e:
            e.args += (val,)
            raise

    def testIsCharacter(self,val): # TEST_TYPE_IS_CHARACTER
        try:
            isascii = lambda s: len(s) == len(s.encode())
            assert (isascii (val))
        except AssertionError as e:
            e.args += (val,)
            raise

    def testIsValueList(self,val, valList): # TEST_TYPE_VALUE_LIST
        try:
            assert (val in valList), val + " must be in list " + (",").join()
        except AssertionError as e:
            e.args += (val,)
            raise

    def testValidGeometries(self,paramValues): # TEST_TYPE_VALUE_LIST
        geomValid = True
        errorMessage = ''
        try:
            if 'secs' in paramValues:
                for key, values in paramValues['secs'].items():
                    if 'geom' in values:
                        if len(values['geom']) == 0:
                            errorMessage = "CellParams -> secs ('" + str(key) + "'): Geom parameters must be specified."
                            geomValid = False
                        #print (" :: " + str(values['geom'] ))
                        #print ( " -- " + str(all([x in values['geom'].keys() for x in VALID_GEOMETRIES_SUBSET])))
                        if not isinstance(values['geom'], dict):
                            errorMessage = "CellParams -> secs ('" + str(key) + "'): Geom parameters must be specified as a dict."
                            geomValid = False
                        if any ([x in values['geom'].keys() for x in VALID_GEOMETRIES_SUBSET]) and not all([x in values['geom'].keys() for x in VALID_GEOMETRIES_SUBSET]):
                            #print (" ----++ 999")
                            errorMessage = "CellParams -> secs ('" + str(key) + "'): If one of '" + str(VALID_GEOMETRIES_SUBSET) + "' are specified, then at least all of the parameters in that list needs to be specified. Values specified are: '" + str(values['geom']) + "'."
                            geomValid = False
                        assert geomValid is True

                        for key1, values1 in values['geom'].items():
                            #print ( " key1 = " + str(key1) + " -- " + str(key1 not in VALID_GEOMETRIES))
                            if key1 not in VALID_GEOMETRIES:

                                errorMessage = "CellParams -> secs ('" + str(key) + "') -> 'geom': Invalid geom parameter '"+ str(key1) + "' specified. Valid values are '" + str(VALID_GEOMETRIES) + "'."
                                geomValid = False
                            assert geomValid is True

                            if PT_3D in values['geom']:
                                if not isinstance ( values['geom'][PT_3D] , list ):
                                    errorMessage = "CellParams -> secs ('" + str(key) + "') -> 'geom': pt3D must be an array with each array element being a 4 length 4 array of floats."
                                    geomValid = False
                                elif len(values['geom'][PT_3D]) == 0 :
                                    errorMessage = "CellParams -> secs ('" + str(key) + "') -> 'geom': At least one element must be provided for pt3D."
                                    geomValid = False
                                assert geomValid is True
                                for elem in values['geom'][PT_3D]:
                                    if not isinstance ( elem , list ):
                                        errorMessage = "CellParams -> secs ('" + str(key) + "') -> 'geom' -> 'pt3D':Type error. pt3D must be an array with each array element being a 4length 4 array of floats."
                                        geomValid = False
                                    elif len(elem) != 4:
                                        errorMessage = "CellParams -> secs ('" + str(key) + "') -> 'geom' -> 'pt3D':Length error. pt3D must be an array with each array element being a 4 length 4 array of floats."
                                        geomValid = False
                                    assert geomValid is True
                                    for elem2 in elem:
                                        if not isinstance ( elem2, numbers.Real ):
                                            errorMessage = "CellParams -> secs ('" + str(key) + "') -> 'geom' -> 'pt3D':Float error. pt3D must be an array with each array element being a 4 length 4 array of floats. Value specified is: '" + str(elem2) + "'."
                                            geomValid = False
                                        assert geomValid is True

        except AssertionError as e:
            e.args += (errorMessage,)
            raise

    def testValidTopologies(self,paramValues): # TEST_TYPE_VALUE_LIST
        try:

            topolValid = True
            topolNeeded = False
            errorMessage = ''

            if 'secs' in paramValues:
                if len(paramValues['secs']) > 0 :
                    topolNeeded = True
                    for key, value in paramValues['secs'].items():
                        if 'topol' not in value:
                            topolValid = False
                            errorMessage = "CellParams -> secs ('" + str(paramValues['secs'].keys()) + "'): Topology needs to be specified if more than one section."
                        else:
                            topolValid = True
                            #print ( " **** past 1 " + str(  len(value['topol'].keys())) )
                            #print ("0 = " + str(topolValid))
                            if not isinstance (value['topol'], dict ) :
                                #print ( " **** past 0 ")

                                topolValid = False
                                errorMessage = "CellParams -> secs ('" + str(key) + "') -> topol: Topology, if specified, must be a dict. Value specified is '" + str(value['topol']) + "'."

                            elif len(value['topol'].keys()) < 3:
                                topolValid = False
                                #print ( " **** past 2 ")
                                errorMessage = "CellParams -> secs ('" + str(key) + "') -> topol: At least 3 parameters (parentSec, parentX and childX) must be specified for topology. Values specified are: '" + str(value['topol'].keys()) + "'."
                            elif not any([x in value['topol'].keys() for x in VALID_TOPOLOGY_PARAMS ]):
                                #print ( " **** past 3 ")
                                topolValid = False
                                errorMessage = "CellParams -> secs ('" + str(key) + "') -> topol: Invalid value specified :''" + str(value['topol']) + "'. Valid values are: '" + str(VALID_TOPOLOGY_PARAMS) + "'."
                            elif value['topol']['parentSec'] not in paramValues['secs']:
                                #print ( " **** past 4 ")
                                # print (" ::: secs are " + str(paramValues['secs']) )
                                topolValid = False
                                errorMessage = "CellParams -> secs ('" + str(key) + "') -> topol -> parentSec: parentSec '" + str(value['topol']['parentSec']) +"' does not point to a valid section. Valid sections are ('" + str(paramValues['secs'].keys()) + "')."
                            elif not isinstance ( value['topol']['parentX'] , numbers.Real ) :
                                #print ( " **** past 5 ")
                                topolValid = False
                                errorMessage = "CellParams -> secs ('" + str(key) + "') -> topol -> parentX: parentX is not a float."
                            elif not isinstance ( value['topol']['childX'] , numbers.Real ) :
                                #print ( " **** past 6 ")
                                topolValid = False
                                errorMessage = "CellParams -> secs ('" + str(key) + "') -> topol -> childX: childX is not a float."
                            elif value['topol']['parentX'] < 0 or value['topol']['parentX'] >1 :
                                #print ( " **** past 7 ")
                                topolValid = False
                                errorMessage = "CellParams -> secs ('" + str(key) + "') -> topol -> parentX: parentX must be between 0 and 1. Value specified is '" + str(value['topol']['parentX'] ) + "'."
                            elif value['topol']['childX'] < 0 or value['topol']['childX'] >1 :
                                #print ( " **** past 8 ")
                                topolValid = False
                                errorMessage = "CellParams -> secs ('" + str(key) + "') -> topol -> parentX: childX must be between 0 and 1. Value specified is '" + str(value['topol']['childX'] ) + "'."

            if topolNeeded:
#                print ("11 = " + str(topolValid))
                assert topolValid is True, errorMessage

        except AssertionError as e:
            e.args += ()
            raise

    def testValidMechs(self,paramValues): # TEST_TYPE_VALID_MECHS

        errorMessages = []
        mechsValidFlagList = []
        mechsWarningFlagList = []

        try:
            mechs = utils.mechVarList()["mechs"]
            if 'secs' in paramValues:
                for key, value in paramValues['secs'].items():
                    if 'mechs' in value:
                        for key1, values1 in paramValues['secs'][key].items():
                            if key1 == "mechs":
                                #errorMessage = str(paramValues['secs'][key][key1])
                                for key2, values2 in paramValues['secs'][key][key1].items():
                                    keys_suffixed = []
                                    mechsValidFlag = True
                                    mechsWarningFlag = False
                                    errorMessage = ''
                                    if key2.find("_ion") != -1:
                                        ionName = key2.split('_ion')[0]
                                        mechs[key2] = [x.replace(ionName, "") for x in mechs[key2] ]
                                        keys_suffixed = [x for x in values2.keys()]
                                        #print ( " !!!!!!!!  " + str(mechs[key2]) + " :: " + str(values2.keys()))
                                        if not any([x in mechs[key2] for x in values2.keys() ]):
                                            #print ( " 1111111 setting invalid 1 " )
                                            mechsValidFlag = False
                                            errorMessage = "CellParams -> secs ('" + str(key) + "') -> mechs ('" + str(key2) + "') -> ions ('" + str(ionName) + "') : Invalid ions (" + str(values2.keys()) + ") specified. Valid value are: " + str(mechs[key2]) + ". Values specified are " + str(values2.keys()) + "."
                                        elif not all([x in values2.keys() for x in mechs[key2] ]):
                                            #print ( " 2222222 setting invalid 2 ")
                                            mechsWarningFlag = True
                                            errorMessage = "CellParams -> secs ('" + str(key) + "') -> mechs ('" + str(key2) + "') -> ions ('" + str(ionName) + "') : Ion specifications incomplete (" + str(values2.keys()) + "). Complete list is: " + str(mechs[key2]) + ". Values specified are " + str(values2.keys()) + "."
                                    else:
                                        keys_suffixed = [x + "_" + key2 for x in values2.keys()]
                                        mechs_unsuffixed = [x.replace("_" + key2, "") for x in mechs[key2]]
                                        #print (" mechs[key2] = " + str(mechs[key2]) + " keys_suffixed = " + str(keys_suffixed))
                                        if not all([x in mechs[key2] for x in keys_suffixed]):
                                            #print ( " !!!!!!!! setting invalid 1 "  + str(mechs[key2]) + " :: " + str(values2.keys()))
                                            mechsValidFlag = False
                                            errorMessage = "CellParams -> secs ('" + str(key) + "') -> mechs ('" + str(key2) + "'): Invalid mechs (" + str(values2.keys()) + ") specified . Valid value are: " + str(mechs_unsuffixed) + ". Values specified are " + str(values2.keys()) + "."
                                        elif not all([x in keys_suffixed for x in mechs[key2] ]):
                                            #print ( " !!!!!!!! setting invalid 2 " + str (keys_suffixed) + " -- " + str(mechs[key2]) + " === " + str([x in keys_suffixed for x in mechs[key2] ]))
                                            mechsWarningFlag = True
                                            errorMessage = "CellParams -> secs ('" + str(key) + "') -> mechs ('" + str(key2) + "'): Incomplete list provided. Complete list is: " + str(mechs_unsuffixed) + ". Values specified are " + str(values2.keys()) + "."
                                            #errorMessage = str(paramValues['secs'][key][key1])

                                    mechsValidFlagList.append(mechsValidFlag)
                                    mechsWarningFlagList.append(mechsWarningFlagList)
                                    errorMessages.append(errorMessage)

            #assert mechsValid is True, " Must be a valid mech as specified in utils.mechVarList."
            # return errorMessage

        except:
            #e.args += (errorMessage)
            #raise
            #traceback.print_exc(file=sys.stdout)
            pass

        return errorMessages, mechsValidFlagList, mechsWarningFlagList

    def testValidPointps(self,paramValues): # TEST_TYPE_VALID_POINTPS

        errorMessages = []

        try:
            pointpsValid = True
            mechs = utils.mechVarList()["mechs"]

            if 'secs' in paramValues:
                for key, value in paramValues['secs'].items():
                    if 'pointps' in value:
                        for key1, values1 in paramValues['secs'][key].items():
                            if key1 == "pointps":
                                for key2, values2 in paramValues['secs'][key][key1].items():
                                    #print (" ** keys2, values2 = " + str(key2) + " :: " + str(values2))
                                    if 'mod' not in values2.keys():
                                        errorMessages.append("CellParams -> secs ('" + str(key) + "') -> pointps ('" + str(key2) + "'): mod must be specified")
                                        pointpsValid = False
                                    elif 'loc' in values2.keys():
                                        loc = values2['loc']
                                        if not isinstance(loc, numbers.Real ):
                                            errorMessages.append("CellParams -> secs ('" + str(key) + "') -> pointps ('" + str(key2) + "'): Loc must be a float. Value provided is " + str(loc))
                                        elif loc < 0 or loc >1:
                                            errorMessages.append("CellParams -> secs ('" + str(key) + "') -> pointps ('" + str(key2) + "'): Loc must be a between 0 and 1. Value provided is " + str(loc))
                                    elif 'synList' in values2.keys():
                                        if not isinstance ('synList', list):
                                            errorMessages.append("CellParams -> secs ('" + str(key) + "') -> pointps ('" + str(key2) + "'): SynList must be a list. Value provided is " + str(values2['synList']))

        except AssertionError as e:
            e.args += ()
            raise

        return errorMessages

    def testArrayInRange(self, val,range, params): # TEST_TYPE_IN_RANGE
        try:
            if val in params:
            #     print ( "************* BEFORE !!!!!!!")
                if isinstance (params[val], list):
                    flattenedList = numpy.ravel(params[val])
                    #print (" flag list " + str(flattenedList))
                    for x in flattenedList:
                        assert (x >= range[0] and x <= range[1])
                elif isinstance (params[val], numbers.Real):
                    assert (params[val] >= range[0] and params[val] <= range[1])
        except AssertionError as e:
            # print ( "************* IN ERROR !!!!!!!")
            e.args += (e,)
            raise

    def checkSyncMechs(self,paramValue, values, dimValues, dimSynMechs, synsPerConn): # check syncMechs

        #print ( " paramValue = " + str(paramValue) + " values = " + str(values) + " dimValues = " + str(dimValues) + " dimSynMechs = " + str(dimSynMechs) + " synsPerConn = " + str(synsPerConn))

        errorMessage = ''
        synMechsValid = True

        try:

            if dimSynMechs == 1:
                # print ( " in check 1 synsPerConn 333 " + str(dimLocs) + " :: " + str(synsPerConn))
                if synsPerConn != 1:
                    # print ( " in check 1 synsPerConn 444 " + str(dimLocs) + " :: " + str(synsPerConn))
                    if dimValues not in [0,1]:
                        errorMessage = "ConnParams -> '" + str(paramValue) + "' can only be a number, function or 1d list if only one 1 synMech and synsPerConn > 1."
                        synMechsValid = False
                    elif dimValues == 1 and len(values) != synsPerConn:
                        errorMessage = "ConnParams -> '" + str(paramValue) + "': Dimension of " + str(paramValue) + " locs array must be same as synsPerConn."
                        synMechsValid = False

                else: # only 1 synsPerConn
                    if dimValues !=0:
                        errorMessage = "ConnParams -> '" + str(paramValue) + "' can only be a number if 1 synMech and synsPerConn = 1."
                        synMechsValid = False
            else: # more than 1 synMech
                if synsPerConn != 1:
                    # print ( " in check 1 synsPerConn 333 dimlocs = " + str(dimLocs) + " synsPerConn = " + str(synsPerConn) + " dimSynMechs = " + str(dimSynMechs))
                    if dimValues not in [0,1,2]:
                        errorMessage = "ConnParams -> '" + str(paramValue) + "' can only be a number or 1d or 2D list if more than 1 synMech and synsPerConn > 1."
                        synMechsValid = False
                    elif dimValues == 1 and len(values) != dimSynMechs:
                        # print ( " in check 1 synsPerConn 555 ")
                        errorMessage = "ConnParams -> '" + str(paramValue) + "' can only be a number or 1d or 2D list if more than 1 synMech and synsPerConn > 1."
                        synMechsValid = False
                    elif dimValues == 2:
                        if numpy.array(locs).shape[1] != synsPerConn:
                            # print ( " in check 1 synsPerConn 666 " )
                            errorMessage = "ConnParams -> '" + str(paramValue) + "' can only be a number or 1d or 2D list if more than 1 synMech and synsPerConn > 1."
                            synMechsValid = False
                        elif numpy.array(values).shape[0] != dimSynMechs:
                            errorMessage = "ConnParams -> '" + str(paramValue) + "': Invalid " + str(paramValue) + " for synMechs and synsPerConn. If specifying 2D array, please ensure that the array of arrays has the number of elements as # of synMechs, with each array having the number of elements as specified by synsPerConn."
                            synMechsValid = False
                else: # only 1 synsPerConn
                    print ( " in check 1 synsPerConn " + str(dimValues))
                    if dimValues not in [0,1]:
                        #print ( " ---------- in error check 1 synsPerConn " + str(dimValues))
                        errorMessage =  "ConnParams -> " + str(paramValue) + " can only be a number or 1 D list if more than 1 synMech and synsPerConn = 1."
                        synMechsValid = False
                    elif dimValues == 1 and len(values) != dimSynMechs:
                        # print ( " in check 1 synsPerConn " + str(len(locs)))
                        errorMessage =  "ConnParams -> " + sstr(paramValue) + " can only be a number or 1d or 2D list if more than 1 synMech and synsPerConn = 1."
                        synMechsValid = False
        except Exception as e:
            return errorMessage, synMechsValid

        return errorMessage, synMechsValid

    def checkConnList(self,paramValue, values, dimValues, dimSynMechs, synsPerConn): # check syncMechs

        #print ( " paramValue = " + str(paramValue) + " values = " + str(values) + " dimValues = " + str(dimValues) + " dimSynMechs = " + str(dimSynMechs) + " synsPerConn = " + str(synsPerConn))

        errorMessage = ''

        try:

            if not isinstance (values, list):
                errorMessage = "ConnParams -> connList must be a list."
            return errorMessage

            if not isinstance (values, list):
                 flattenedList = numpy.ravel(values)
                 if not all([isinstance(x,numbers.Real) for x in flattenedList]):
                    errorMessage = "ConnParams -> connList can only contain floats."
            return errorMessage

            if dimValues not in [2,3]:
                    errorMessage = "ConnParams -> connList can only be 2D or 3D list."
                    return errorMessage

            # if dimSynMechs == 1:
            #     # print ( " in check 1 synsPerConn 333 " + str(dimLocs) + " :: " + str(synsPerConn))
            #     if synsPerConn != 1:
            #         # print ( " in check 1 synsPerConn 444 " + str(dimLocs) + " :: " + str(synsPerConn))
            #         if dimValues not in [1,2]:
            #             errorMessage = str(paramValue) + " can only be a 1D or 2D list if only one 1 synMech and synsPerConn > 1."
            #         elif dimValues == 1 and len(values) != synsPerConn:
            #             errorMessage = "Dimension of " + str(paramValue) + " locs array must be same as synsPerConn."
            #
            #     else: # only 1 synsPerConn
            #         if dimValues !=0:
            #             errorMessage = str(paramValue) + " can only be a list if 1 synMech and synsPerConn = 1."
            # else: # more than 1 synMech
            #     if synsPerConn != 1:
            #         # print ( " in check 1 synsPerConn 333 dimlocs = " + str(dimLocs) + " synsPerConn = " + str(synsPerConn) + " dimSynMechs = " + str(dimSynMechs))
            #         if dimValues not in [1,2,3]:
            #             errorMessage = str(paramValue) + " can only be a number or 2d or 3D list if more than 1 synMech and synsPerConn > 1."
            #         elif dimValues == 2 and len(values) != dimSynMechs:
            #             # print ( " in check 1 synsPerConn 555 ")
            #             errorMessage = str(paramValue) + " can only be a number or 2d or 3D list if more than 1 synMech and synsPerConn > 1."
            #         elif dimValues == 3:
            #             if numpy.array(locs).shape[2] != synsPerConn:
            #                 # print ( " in check 1 synsPerConn 666 " )
            #                 errorMessage = str(paramValue) + " can only be a number or 2d or 3D list if more than 1 synMech and synsPerConn > 1."
            #             elif numpy.array(values).shape[2] != dimSynMechs:
            #                 errorMessage = "Invalid " + str(paramValue) + " for synMechs and synsPerConn. If specifying 2D array, please ensure that the array of arrays has the number of elements as # of synMechs, with each array having the number of elements as specified by synsPerConn."
            #     else: # only 1 synsPerConn
            #         # print ( " in check 1 synsPerConn ")
            #         if dimValues not in [1,2]:
            #             errorMessage = str(paramValue) + " can only be a number or 1 D list if more than 1 synMech and synsPerConn = 1."
            #         elif dimValues == 1 and len(values) != dimSynMechs:
            #             # print ( " in check 1 synsPerConn " + str(len(locs)))
            #             errorMessage = str(paramValue) + " can only be a number or 1d or 2D list if more than 1 synMech and synsPerConn = 1."

        except Exception as e:
            return errorMessage

        return errorMessage

    def checkValidSyncMechs(self, synMechs, netParams):

        errorMessage = ''

        synMechsValid = True

        #print ( " syn mech params = " + str(netParams.synMechParams))
        try:
            if isinstance(synMechs, list):
                for synMech in synMechs:
                    if not synMech in netParams.synMechParams:
                        errorMessage = "ConnParams -> synMechs -> " + synMech + ": Synaptic mechanism is not valid."
                        synMechsValid = False
            # else:
            #     errorMessage = "ConnParams -> synMechs -> " + str(synMechs) + ": Synaptic mechanism is not valid, must be a list."
            #     synMechsValid = False
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            raise
        return errorMessage, synMechsValid

    def testValidSynMechs(self,parameterName, paramValues, netParams): # TEST_TYPE_VALID_SYN_MECHS

        # If omitted, defaults to netParams.defaultWeight = 1.
        # If have list of synMechs, can have single weight for all, or list of weights (one per synMech, e.g. for 2 synMechs: [0.1, 0.01]).
        # If have synsPerConn > 1, can have single weight for all, or list of weights (one per synapse, e.g. if synsPerConn = 3: [0.2, 0.3, 0.4])
        # If have both a list of synMechs and synsPerConn > 1, can have a 2D list for each synapse of each synMech (e.g. for 2 synMechs and synsPerConn = 3: [[0.2, 0.3, 0.4], [0.02, 0.04, 0.03]])

        #print ( " parameterName "  + str(parameterName))

        errorMessage = ''

        try:
            synMechsValid = True

            synsPerConn = 1
            synMechs = ''

            dimSynMechs = 1
            values = []
            dimValues = 1

            if 'synMech' in paramValues:
                synMechs = paramValues['synMech']
                # print (" *** synmechs " + str(synMechs))
                if isinstance(synMechs, list):
                    dimSynMechs = len(synMechs)
                else:
                    dimSynMechs = 1

            if 'synsPerConn' in paramValues:
                synsPerConn = paramValues ['synsPerConn']

            if parameterName in paramValues:
                values = paramValues [parameterName]
                dimValues = numpy.array(values).ndim

                if parameterName == 'loc':
                    flattenedValues = numpy.ravel(values)
                    if not all ([isinstance(x,numbers.Real) for x in flattenedValues]):
                        errorMessage = "ConnParams -> " + str(parameterName) + " must be a number with values between 0 and 1."
                        synMechsValid = False
                    elif not all ([x >= 0 and x <=1 for x in flattenedValues]):
                        #print ( " *** " + str(flattenedValues))
                        errorMessage = "ConnParams -> " + str(parameterName) + " must be a number with values between 0 and 1."
                        synMechsValid = False

            errorMessage += "Supplied values are: " + str(parameterName) + " = " + str(values) + " synMech = " + str(synMechs) + " synPerConn = " + str(synsPerConn) + "."

            assert synMechsValid is True

            # print ( " in check 1 synsPerConn 222 dimSynMechs = " + str(dimSynMechs) + " synsPerConn = " + str(synsPerConn))
            errorMessage, synMechsValid = self.checkValidSyncMechs(synMechs, netParams)

            errorMessage += "Supplied values are: " + str(parameterName) + " = " + str(values) + " synMech = " + str(synMechs) + " synPerConn = " + str(synsPerConn) + "."

            assert synMechsValid is True

            # print ( " in check 1 synsPerConn 222 dimSynMechs = " + str(dimSynMechs) + " synsPerConn = " + str(synsPerConn))
            errorMessage, synMechsValid = self.checkSyncMechs(parameterName, values, dimValues, dimSynMechs, synsPerConn)

            errorMessage += "Supplied values are: " + str(parameterName) + " = " + str(values) + " synMech = " + str(synMechs) + " synPerConn = " + str(synsPerConn) + "."

            assert synMechsValid is True
            # return errorMessage

        except AssertionError as e:
            e.args += (errorMessage, )
            raise

    def testValidConnList(self, paramValues, netParams): # TEST_TYPE_VALID_CONN_LIST

        #print ( " parameterName "  + str(parameterName))

        errorMessage = ''

        try:

            synsPerConn = 1
            synMechs = ''

            dimSynMechs = 1
            values = []
            dimValues = 1

            if 'synMech' in paramValues:
                synMechs = paramValues['synMech']
                # print (" *** synmechs " + str(synMechs))
                if isinstance(synMechs, list):
                    dimSynMechs = len(synMechs)
                else:
                    dimSynMechs = 1

            if 'synsPerConn' in paramValues:
                synsPerConn = paramValues ['synsPerConn']

            if 'connList' in paramValues:
                values = paramValues ['connList']
                dimValues = numpy.array(values).ndim

            # print ( " in check 1 synsPerConn 222 dimSynMechs = " + str(dimSynMechs) + " synsPerConn = " + str(synsPerConn))
            errorMessage = self.checkConnList(parameterName, values, dimValues, dimSynMechs, synsPerConn)

        except Exception as e:
            e.args += (e, )
            raise
        return errorMessage

    def testValidSecLists(self,paramValues): # TEST_TYPE_VALID_SEC_LIST

        errorMessage = ''

        try:

            cellParams = paramValues
            validSections = []

            secList = ''

            if isinstance ( cellParams , dict):
                for key, value in cellParams.items():
                    if key == "secs" and isinstance(value, dict):
                        #print (" value### = " + str(value.keys()))
                        validSections.extend ( value.keys())

        #    print ( " @@@@ valid sections = " + str(validSections))

            if 'secList' in cellParams:
                secList = cellParams['secList']
                #print ( " seclist = " + str(secList))
                if not isinstance (secList, dict):
                    errorMessage = "CellParams -> seclist must be a dict."
                else:
                    for key, value in secList.items():
                        #print ( " ^^^^^^^^ value = " + str(value))
                        if not isinstance (value, list):
                            errorMessage = "CellParams -> secList ('" + str(key) + "'):Each element of seclist must be a list. Value specified is: " + str(value) + "."
                        elif any ([x not in validSections for x in value]):
                            errorMessage = "CellParams -> secList ('" + str(key) + "'): " + str(value) + " - Sections specified in secList keys must be specified in cells. Valid list is " + str(validSections) + "."

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            e.args += (errorMessage, )
            raise
        return errorMessage

    def testTypeHierarchy(self,paramValues): # TEST_TYPE_CONN_PARM_HIERARCHY

        # probability > convergence > divergenece > connList

        errorMessage = ''

        #print ( " ::: in hierarchy ")

        try:

            probability = ''
            convergence = ''
            divergence = ''
            connList = ''

            if 'probability' in paramValues:
                probability = paramValues['probability']
            if 'convergence' in paramValues:
                convergence = paramValues['convergence']
            if 'divergence' in paramValues:
                divergence = paramValues['divergence']
            if 'connList' in paramValues:
                connList = paramValues['connList']

            # print (" paramValues " + str(paramValues))
            # print (" probability " + str(probability))
            # print (" convergence " + str(convergence))
            # print (" divergence " + str(divergence))
            # print (" connList " + str(connList))

            if probability != '':
                if convergence != '' or divergence != '' or connList != '':
                    errorMessage = "ConnParams -> probability: If probability is specified, then convergence and divergence and connList parameters will be ignored."
            elif convergence != '':
                if divergence != '' or connList != '':
                    errorMessage = "ConnParams -> convergence: If convergence is specified, then divergence and connList parameters will be ignored."
            elif divergence != '':
                if connList != '':
                    errorMessage = "ConnParams -> divergence: If divergence is specified, then connList parameters will be ignored."

        except Exception as e:
            #traceback.print_exc(file=sys.stdout)
            e.args += (errorMessage, )
            raise
        return errorMessage

    def testValidConnShape(self,paramValues): # TEST_TYPE_CONN_SHAPE

        errorMessages = []
        #print ( " in shape --- ")
        try:

            shape = {}

            if 'shape' in paramValues:
                shape = paramValues['shape']

            if not isinstance ( shape, dict):
                errorMessage = "Shape must be a dict."
                errorMessages.append(errorMessage)
                return errorMessages

            #- times at which to switch on and off the weight -
            # this is a list of times (numbers)
            switchOnOff = ''
            if 'switchOnOff' in shape:
                switchOnOff = shape["switchOnOff"]

            #Other options error
            pulseType = ''
            if 'pulseType' in shape:
                pulseType = shape["pulseType"]

            #- period (in ms) of the pulse
            pulsePeriod = ''
            if 'pulsePeriod' in shape:
                pulsePeriod = shape["pulsePeriod"]

            #Floats
            #- width (in ms) of the pulse
            pulseWidth = ''
            if 'pulseWidth' in paramValues:
                pulseWidth = paramValues["pulseWidth"]

            #print ( paramValues)

            if switchOnOff != '':
                if not isinstance ( switchOnOff, list):
                    errorMessage = "connList -> shape: SwitchOnOff, if specified, must be a list."
                    errorMessages.append(errorMessage)
                elif not all ([isinstance(x, numbers.Real) for x in switchOnOff]):
                    errorMessage = "connList -> shape: SwitchOnOff values must be numeric."
                    errorMessages.append(errorMessage)

            if pulseType != '':
                if pulseType not in ['square', 'gaussian'] :
                    errorMessage = "connList -> shape: Pulse type, if specified, can only be square or gaussian. Value specified is " + str(pulseType) + "."
                    errorMessages.append(errorMessage)

            if pulsePeriod != '':
                if not isinstance (pulsePeriod, numbers.Real):
                    errorMessage = "connList -> shape: Pulse period, if specified, must be a float. Value specified is " + str(pulsePeriod) + "."
                    errorMessages.append(errorMessage)

            if pulseWidth != '':
                if not isinstance (pulseWidth, numbers.Real):
                    errorMessage = "connList -> shape: Pulse width, if specified, must be a float. Value specified is " + str(pulseWidth) + "."
                    errorMessages.append(errorMessage)

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            e.args += ( )
            raise
        return errorMessages

    def testValidConnPlasticity(self,paramValues): # TEST_TYPE_CONN_PLASTICITY

        errorMessages = []

        try:

            plasticity = {}

            #print ( paramValues)

            if 'plasticity' in paramValues:
                plasticity = paramValues['plasticity']

            if not isinstance ( plasticity, dict):
                errorMessage = "connParams -> 'plasticity': Plasticity must be a dict."
                errorMessages.append(errorMessage)
                return errorMessages

            if 'mech' not in plasticity:
                errorMessage = "connParams -> 'plasticity' :'mech' must be specified in plasticity in connParams with label."
                errorMessages.append(errorMessage)
            if 'params' not in plasticity:
                errorMessage = "connParams -> 'plasticity': 'params' must be specified in plasticity."
                errorMessages.append(errorMessage)
            elif not isinstance (plasticity['params'], dict):
                errorMessage = "connParams -> 'plasticity': 'params' for plasticity must be a dict."
                errorMessages.append(errorMessage)

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            e.args += ( )
            raise
        return errorMessages

    def testValidSpikeGenLoc(self,paramValues): # TEST_TYPE_VALID_SEC_LIST

        errorMessages = []

        try:

            cellParams = paramValues
            validSections = []

            secList = ''
            # print (cellParams)
            if isinstance ( cellParams , dict):
                # print (cellParams)
                for key, value in cellParams.items():
                    # for key, value in value0.items():
                        if key == "secs" and isinstance(value, dict):
                            #print (" value### = " + str(value.keys()))
                            for key1, value1 in value.items():
                                if isinstance ( value1, dict) and 'spikeGenLoc' in value1:
                                    spikeGenLoc = value1['spikeGenLoc']
                                    if not isinstance (spikeGenLoc, numbers.Real ):
                                        errorMessages.append( "cellParams -> secs -> spikeGenLoc must be a float.")
                                        return errorMessages
                                    elif spikeGenLoc < 0 or spikeGenLoc > 1:
                                        errorMessages.append( "cellParams -> secs -> spikeGenLoc must be between 0 and 1.")
                                        return errorMessages

        except Exception as e:
            #traceback.print_exc(file=sys.stdout)
            e.args += ( )
            raise
        return errorMessages

    def testValidStimSource(self,paramValues): # TEST_TYPE_STIM_SOURCE_TEST

        errorMessages = []

        try:

            simType =  ''
            mechVarList = utils.mechVarList()
            allKeys = []
            validTypes = []
            if simType in paramValues['type']:

                simType = paramValues['type']

                allKeys = paramValues.keys()
                allKeys.remove('type')

            if 'pointps' in mechVarList:
                validTypes = mechVarList['pointps'].keys() + ['rate']

            if simType not in validTypes:
                errorMessage = " StimSourceParams -> type: Invalid simtype " + str(simType) + ". Valied values are: " + str(validTypes) + "."
                errorMessages.append(errorMessage)
            else:
                allowedValues = mechVarList['pointps'][simType] + ['rate']
                if any([x not in allowedValues for x in allKeys]):
                    errorMessage = "StimSourceParams -> : Invalid parameter specified. Values specified are " + str(allKeys) + ", while allowed values are: " + str(allowedValues)
                    errorMessages.append(errorMessage)

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            e.args += ( )
            raise
        return errorMessages

    def testValidStimTarget(self,paramValues, netParams): # TEST_TYPE_STIM_TARGET_TEST

        errorMessages = []

        stimSourceParams = netParams.stimSourceParams
        source = []

        if isinstance(stimSourceParams, dict):
            sources = stimSourceParams.keys()

        try:
            if 'source' not in paramValues:
                errorMessage = "stimTargetParams -> source: Source must be specified in stimTargetParams."
                errorMessages.append(errorMessage)
                return errorMessages
            elif paramValues['source'] not in sources:
                    errorMessage = "StimTargetParams -> source:" + str(paramValues['source'] ) + ": Invalid source specified in stimTargetParams. The source must exist in stimSourceParams."
                    errorMessages.append(errorMessage)
                    return errorMessages

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            e.args += ( )
            raise
        return errorMessages

# Tests that are defined for each set of parameters
class TestObj(object):

    def __init__(self):

        self.testName = '' # test name

        self.testParameterType = '' # test parameter, type string, list
        self.testParameterValue = '' # test parameter value, like 'shape'
        self.testParameterValue1 = '' # test parameter value, like 'shape'. Used for nested dicts like cellParams['conds']['cellType']
        self.testParameterValueList = '' # test parameter value list, like ['density', 'numCells','gridSpacing']
        self.testParameterDictString = '' # for nested dicts like ['shape']['geom']

        self.testTypes = [] # list of be multiple tests
        self.testValueList = [] # could be restricted list like ['cuboid','ellipsoid','cylinder']
        self.testValueRange = [] # could be restricted range like [0,1]

        self.compareValueString = "" # variable name - like netParams.sizeX, or value
        self.compareValueDataType = "" # data type of compare value ( string or list or dict
        self.compareValueType = "" # eval (if compareValueString is string or int or float
        self.conditionString = "" # condition for test

        self.messageText = [] # error message text - array for each test
        self.errorMessageLevel = [] # info, warn, error - array for each test

    def __unicode__(self):
        return str(self.testName)

# Tests that are defined for each set of parameters
class ErrorMessageObj(object):

    def __init__(self):

        self.messageText = '' # text
        self.errorMessageLevel = '' # info, warn, error
        self.errorMessageValue = '' # value

    def __unicode__(self):
        return str(self.messageText)

class NetPyneTestObj(object):

    def __init__(self, verboseFlag = False):

        # The tests to be conducted on the netpyne params
        self.testParamsMap = {}
        self.simConfig = ''  # object of class SimConfig to store simulation configuration
        self.netParams = ''
        self.testTypeObj = TestTypeObj()
        self.verboseFlag = verboseFlag
        self.errorMessageObjList = []
        self.loadTests()

    def loadTests(self):

        if self.verboseFlag:
            print (" *** Loading tests *** ")
        self.loadPopTests() # load pop tests
        self.loadNetTests() # load net tests
        self.loadCellTests() # load cell tests
        self.loadConnTests() # load conn tests
        self.loadStimSourceTests() # load stimSource tests
        self.loadStimTargetTests() # load stimTarget tests
        if self.verboseFlag:
            print (" *** Finish loading tests *** ")

    def runTests(self):

        # if self.verboseFlag:
        #     print (" *** Running tests *** ")
        self.runPopTests() # run pop tests
        self.runNetTests() # run net tests
        self.runCellTests() # run cell tests
        self.runConnTests() # run conn tests
        self.runStimSourceTests() # load stimSource tests
        self.runStimTargetTests() # load stimTarget tests

        # if self.verboseFlag:
        #     print (" *** Finished running tests *** ")

    def loadStimSourceTests(self):

        # if self.verboseFlag:
        #     print (" *** Loading pop tests *** ")

        # initialiase list of test objs
        self.testParamsMap["stimSource"] = {}

        ##cell model test
        testObj = TestObj()
        testObj.testName = "stimSourceTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "type"
        testObj.testTypes = [TEST_TYPE_STIM_SOURCE_TEST]
        testObj.messageText = ["Invalid stim source specified."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["stimSource"]["stimSourceTest"] = testObj

    def loadStimTargetTests(self):

        # if self.verboseFlag:
        #     print (" *** Loading pop tests *** ")

        # initialiase list of test objs
        self.testParamsMap["stimTarget"] = {}

        ##cell model test
        testObj = TestObj()
        testObj.testName = "stimTargetTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "type"
        testObj.testTypes = [TEST_TYPE_STIM_TARGET_TEST]
        testObj.messageText = ["Invalid stim target specified."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["stimTarget"]["stimTargetTest"] = testObj

    def loadPopTests(self):

        # if self.verboseFlag:
        #     print (" *** Loading pop tests *** ")

        # initialiase list of test objs
        self.testParamsMap["pop"] = {}

        ##cell model test
        testObj = TestObj()
        testObj.testName = "cellModelTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "cellModel"
        testObj.testTypes = [TEST_TYPE_EXISTS]
        testObj.messageText = ["No Cell Model specified in population paramters."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["cellModelTest"] = testObj

        ##volume params test
        testObj = TestObj()
        testObj.testName = "volumeParamsTest"
        testObj.testParameterType = "list"
        testObj.testParameterValueList = ['density','numCells','gridSpacing']
        testObj.testTypes = [TEST_TYPE_EXISTS_IN_LIST]
        testObj.messageText = ["One of the following must be specified in parameters: " + str(testObj.testParameterValueList)]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["volumeParamsTest"] = testObj

        # xnormrange test
        testObj = TestObj()
        testObj.testName = "xNormRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "xnormRange"
        testObj.testTypes = [TEST_TYPE_IS_VALID_RANGE, TEST_TYPE_IN_RANGE]
        testObj.testValueRange = "[0,1]"
        testObj.messageText = ["XNormRange invalid range.","XNormRange not in range."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["xNormRangeTest"] = testObj

        # ynormrange test
        testObj = TestObj()
        testObj.testName = "yNormRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "ynormRange"
        testObj.testTypes = [TEST_TYPE_IS_VALID_RANGE, TEST_TYPE_IN_RANGE]
        testObj.testValueRange = "[0,1]"
        testObj.messageText = ["YNormRange invalid.","YNormRange not in range."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["yNormRangeTest"] = testObj

        # znormrange test
        testObj = TestObj()
        testObj.testName = "zNormRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "znormRange"
        testObj.testTypes = [TEST_TYPE_IS_VALID_RANGE, TEST_TYPE_IN_RANGE]
        testObj.testValueRange = "[0,1]"
        testObj.messageText = ["ZNormRange invalid.","ZNormRange not in range."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["zNormRangeTest"] = testObj

        # xrange test
        testObj = TestObj()
        testObj.testName = "xRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "xRange"
        testObj.testTypes = [TEST_TYPE_IS_VALID_RANGE, TEST_TYPE_IN_RANGE]
        testObj.testValueRange = "[0,self.netParams.sizeX]"
        testObj.messageText = ["xRange invalid.","xRange not in range."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, TEST_TYPE_IN_RANGE]

        self.testParamsMap["pop"]["xRangeTest"] = testObj

        # yrange test
        testObj = TestObj()
        testObj.testName = "yRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "yRange"
        testObj.testTypes = [TEST_TYPE_IS_VALID_RANGE, TEST_TYPE_IN_RANGE]
        testObj.testValueRange = "[0,self.netParams.sizeY]"
        testObj.messageText = ["yRange invalid.", "yRange not in range."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["yRangeTest"] = testObj

        # zrange test
        testObj = TestObj()
        testObj.testName = "zRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "zRange"
        testObj.testTypes = [TEST_TYPE_IS_VALID_RANGE, TEST_TYPE_IN_RANGE]
        testObj.testValueRange = "[0,self.netParams.sizeX]"
        testObj.messageText = ["zRange invalid.", "zRange not in range."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["zRangeTest"] = testObj

        # if self.verboseFlag:
        #     print (" *** Finished loading pop tests *** ")

    def loadNetTests(self):

        # if self.verboseFlag:
        #     print (" *** Loading net tests *** ")

        self.testParamsMap["net"] = {}

        # sizeX test
        testObj = TestObj()
        testObj.testName = "sizeXTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.netParams.sizeX"
        testObj.testTypes = [TEST_TYPE_IS_INT, TEST_TYPE_GT_ZERO]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["net"]["sizeXTest"] = testObj

        # sizeY test
        testObj = TestObj()
        testObj.testName = "sizeYTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.netParams.sizeY"
        testObj.testTypes = [TEST_TYPE_IS_INT, TEST_TYPE_GT_ZERO]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["net"]["sizeYTest"] = testObj

        # sizeZ test
        testObj = TestObj()
        testObj.testName = "sizeZTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.netParams.sizeZ"
        testObj.testTypes = [TEST_TYPE_IS_INT, TEST_TYPE_GT_ZERO]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["net"]["sizeZTest"] = testObj

        # shape test
        testObj = TestObj()
        testObj.testName = "shapeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.netParams.shape"
        testObj.testTypes = [TEST_TYPE_VALUE_LIST]
        testObj.testValueList = VALID_SHAPES
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["net"]["shapeTest"] = testObj

        # if self.verboseFlag:
        #     print (" *** Finished loading net tests *** ")

    def loadCellTests(self):

        # if self.verboseFlag:
        #     print (" *** Loading cell tests *** ")

        self.testParamsMap["cell"] = {}

        # # condsTest test
        # testObj = TestObj()
        # testObj.testName = "condsTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "conds"
        # testObj.testTypes = [TEST_TYPE_EXISTS, TEST_TYPE_IS_DICT]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]
        # testObj.messageText = ["Conds does not exist.", "Conds is not a dict."]
        # self.testParamsMap["cell"]["condsTest"] = testObj
        #
        # # secs test
        # testObj = TestObj()
        # testObj.testName = "secsTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "secs"
        # testObj.testTypes = [TEST_TYPE_IS_DICT]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        # testObj.messageText = ["Secs is not a dict."]
        # self.testParamsMap["cell"]["secsTest"] = testObj
        #
        # # cellTypes test
        # testObj = TestObj()
        # testObj.testName = "cellTypesTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "conds"
        # testObj.testParameterValue1 = "cellType"
        # testObj.testTypes = [TEST_TYPE_EXISTS_IN_DICT]
        # testObj.compareDict = "self.netParams.popParams"
        # testObj.messageText = ["Cell type does not match the cell type specified in pop parameters."]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_WARNING]
        #
        # self.testParamsMap["cell"]["cellTypeTest"] = testObj
        #
        # # cellModel test
        # testObj = TestObj()
        # testObj.testName = "cellModelTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "conds"
        # testObj.testParameterValue1 = "cellModel"
        # testObj.testTypes = [TEST_TYPE_EXISTS_IN_DICT]
        # testObj.compareDict = "self.netParams.popParams"
        # testObj.messageText = ["Cell model does not match the cell model specified in pop parameters."]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_WARNING]
        #
        # self.testParamsMap["cell"]["cellModelTest"] = testObj
        #
        # #geom test
        # testObj = TestObj()
        # testObj.testName = "geomExistTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "secs"
        # testObj.testParameterDictString = "geom"
        # testObj.testTypes = [TEST_TYPE_EXISTS_IN_ALL_DICTS]
        # testObj.messageText = ["Geom is not specified in section "]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        # self.testParamsMap["cell"]["geomExistTest"] = testObj
        #
        # # geom test
        # testObj = TestObj()
        # testObj.testName = "geomValidTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "geom"
        # testObj.testTypes = [TEST_TYPE_VALID_GEOMETRIES]
        # #testObj.testValueList = VALID_GEOMETRIES,
        # testObj.messageText = ["Geom is not valid."]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        #
        # self.testParamsMap["cell"]["geomValidTest"] = testObj

        # # topol test
        # testObj = TestObj()
        # testObj.testName = "topologyTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "topol"
        # testObj.testTypes = [TEST_TYPE_VALID_TOPOLOGIES]
        # testObj.messageText = ["Topology is not valid."]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        #
        # self.testParamsMap["cell"]["toplogyValidTest"] = testObj
        #
        # # mechs test
        # testObj = TestObj()
        # testObj.testName = "mechsTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "mechs"
        # testObj.testTypes = [TEST_TYPE_VALID_MECHS]
        # testObj.messageText = ["Mechs are not valid."]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        #
        # self.testParamsMap["cell"]["mechsValidTest"] = testObj

        # # pointps test
        # testObj = TestObj()
        # testObj.testName = "pointpsTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "pointps"
        # testObj.testTypes = [TEST_TYPE_VALID_POINTPS]
        # testObj.messageText = ["Pointps are not valid."]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        #
        # self.testParamsMap["cell"]["pointpsValidTest"] = testObj

        # # secList test
        # testObj = TestObj()
        # testObj.testName = "secListTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "secList"
        # testObj.testTypes = [TEST_TYPE_VALID_SEC_LIST]
        # testObj.messageText = ["SecList is not valid."]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        #
        # self.testParamsMap["cell"]["secListTest"] = testObj

        # secList test
        testObj = TestObj()
        testObj.testName = "spikeGenLocTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "spikeGenLoc"
        testObj.testTypes = [TEST_TYPE_IS_VALID_SPIKE_GENLOC]
        # testObj.testValueRange = "[0,1]"
        # testObj.messageText = ["range specified for spikeGenLoc is invalid."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["cell"]["spikeGenLocTest"] = testObj

        # if self.verboseFlag:
        #     print (" *** Finished loading cell tests *** ")

    def loadConnTests(self):

        # if self.verboseFlag:
        #     print (" *** Loading conn tests *** ")

        self.testParamsMap["conn"] = {}

        # # pop Labels test
        # testObj = TestObj()
        # testObj.testName = "popLabelsTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "preConds"
        # testObj.testTypes = [TEST_TYPE_EXISTS_IN_POP_LABELS]
        # testObj.messageText = ["Pop label specified for preConds not listed in pop parameters."]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_WARNING]
        # self.testParamsMap["conn"]["preCondsPopLabelsTest"] = testObj
        #
        # # pop Labels test
        # testObj = TestObj()
        # testObj.testName = "popLabelsTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "postConds"
        # testObj.testTypes = [TEST_TYPE_EXISTS_IN_POP_LABELS]
        # testObj.messageText = ["Pop label specified for postConds not listed in pop parameters."]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_WARNING]
        # self.testParamsMap["conn"]["postCondsPopLabelsTest"] = testObj

        # # condsTest test
        # testObj = TestObj()
        # testObj.testName = "popLabelsTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "popLabel"
        # testObj.testTypes = [TEST_TYPE_POP_LABEL_VALID]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_WARNING]
        # testObj.messageText = ["Pop label specified in conn parameters."]
        # self.testParamsMap["conn"]["popLabelsTest"] = testObj

        # # condsTest test
        # testObj = TestObj()
        # testObj.testName = "preCondsTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "preConds"
        # testObj.testTypes = [TEST_TYPE_EXISTS, TEST_TYPE_IS_DICT]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]
        # testObj.messageText = ["Preconds does not exist.", "Preconds is not a dict."]
        # self.testParamsMap["conn"]["preCondsTest"] = testObj
        #
        # # condsTest test
        # testObj = TestObj()
        # testObj.testName = "postCondsTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "postConds"
        # testObj.testTypes = [TEST_TYPE_EXISTS, TEST_TYPE_IS_DICT]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]
        # testObj.messageText = ["Postconds does not exist.", "Postconds is not a dict."]
        # self.testParamsMap["conn"]["postCondsTest"] = testObj
        #
        # # secs test
        # testObj = TestObj()
        # testObj.testName = "connsSecsTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "secs"
        # testObj.testTypes = [TEST_TYPE_EXISTS, TEST_TYPE_IS_DICT ]
        # testObj.messageText = ["Secs, is specified, needs to be a dict.", "Secs is not specified. Will use 'soma' by default otherwise first available section."]
        # testObj.errorMessageLevel = ["MESSAGE_TYPE_WARNING", "MESSAGE_TYPE_ERROR"]
        #
        # self.testParamsMap["conn"]["connsSecsTest"] = testObj
        #
        # #locs test
        # testObj = TestObj()
        # testObj.testName = "connLocsRangeTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "loc"
        # testObj.testTypes = [TEST_TYPE_ARRAY_IN_RANGE]
        # testObj.testValueRange = "[0,1]"
        # testObj.messageText = ["Loc is not in range."]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        #
        # self.testParamsMap["conn"]["locsRangeTest"] = testObj
        #
        # # locs synMechs test
        # testObj = TestObj()
        # testObj.testName = "connLocsSynMechTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "loc"
        # testObj.testTypes = [TEST_TYPE_VALID_SYN_MECHS]
        # testObj.messageText = ["Syn Mechs are invalid."]
        # testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]
        #
        # self.testParamsMap["conn"]["synMechsTest"] = testObj
        #
        # # weights synMechs test
        # testObj = TestObj()
        # testObj.testName = "connWeightSynMechTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "weight"
        # testObj.testTypes = [TEST_TYPE_VALID_SYN_MECHS]
        # testObj.messageText = ["Syn Mechs are invalid."]
        # testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]
        #
        # self.testParamsMap["conn"]["weightsMechsTest"] = testObj

        # # delay synMechs test
        # testObj = TestObj()
        # testObj.testName = "connDelaySynMechTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "delay"
        # testObj.testTypes = [TEST_TYPE_VALID_SYN_MECHS]
        # testObj.messageText = ["Syn Mechs are invalid."]
        # testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]
        #
        # self.testParamsMap["conn"]["delayMechsTest"] = testObj

        #
        # # synsPerConn
        # #- synsPerConn: optional, defaults to 1; has to be >=1
        #
        # testObj = TestObj()
        # testObj.testName = "synsPerConnTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "synsPerConn"
        # testObj.testTypeSpecialString = "synMechsTest"
        # testObj.testTypes = [TEST_TYPE_INTEGER, TEST_TYPE_GTE ]
        # testObj.compareValueString = "1"
        # testObj.compareValueType = "int"
        # testObj.messageText = ["Syns Per Conn must be >= 1."]
        # testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]
        #
        # testParamsMap["conn"]["synsPerConnTest"] = testObj
        #
        # # probability: optional; [0,1]
        # testObj = TestObj()
        # testObj.testName = "probabilityTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "probability"
        # testObj.testTypes = [TEST_TYPE_IS_FLOAT, TEST_TYPE_GTE_ZERO, TEST_TYPE_LTE ]
        # testObj.compareValueString = "1"
        # testObj.compareValueType = "int"
        # testObj.messageText = ["Probability needs to be between 0 and 1."]
        # testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]
        #
        # testParamsMap["conn"]["probabilityTest"] = testObj
        #
        # # convergence  optional; positive integer
        #
        # testObj = TestObj()
        # testObj.testName = "convergenceTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "convergence"
        # testObj.testTypes = [TEST_TYPE_IS_INT, TEST_TYPE_GTE_ZERO ]
        # testObj.messageText = ["Convergence, is specified, needs to be a positive integer."]
        # testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]
        #
        # testParamsMap["conn"]["convergenceTest"] = testObj
        #
        # # divergence  optional; positive integer
        #
        # testObj = TestObj()
        # testObj.testName = "divergenceTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "divergence"
        # testObj.testTypes = [TEST_TYPE_IS_INT, TEST_TYPE_GTE_ZERO ]
        # testObj.messageText = ["Divergence, is specified, needs to be a positive integer."]
        # testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]
        #
        # testParamsMap["conn"]["divergenceTest"] = testObj

        # # secs test
        # testObj = TestObj()
        # testObj.testName = "connsSecsTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "secs"
        # testObj.testTypes = [TEST_TYPE_EXISTS, TEST_TYPE_IS_DICT, TEST_TYPE_VALID_SEC_LIST ]
        # testObj.messageText = ["Secs, if specified, needs to be a dict.", "Secs is not specified. Will use 'soma' by default otherwise first available section."]
        # testObj.errorMessageLevel = ["MESSAGE_TYPE_WARNING", "MESSAGE_TYPE_ERROR"]
        #
        # self.testParamsMap["conn"]["connsSecsTest"] = testObj
        #
        # # secs test
        # testObj = TestObj()
        # testObj.testName = "connsSecsListTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "secs"
        # testObj.testTypes = [TEST_TYPE_VALID_SEC_LIST ]
        # testObj.messageText = ["If synsPerConn > 1, a list of sections or sectionList can be specified. These secs need to be specified in the cell parameters."]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        #
        # self.testParamsMap["conn"]["connsSecsListTest"] = testObj
        #
        # # conn list test
        # testObj = TestObj()
        # testObj.testName = "connsListTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "secs"
        # testObj.testTypes = [TEST_TYPE_VALID_CONN_LIST ]
        # testObj.messageText = ["If synsPerConn > 1, a list of sections or sectionList can be specified. These secs need to be specified in the cell parameters."]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        #
        # self.testParamsMap["conn"]["connsListTest"] = testObj

        # # conn list test
        # testObj = TestObj()
        # testObj.testName = "hierarchyTest"
        # testObj.testParameterType = "string"
        # #testObj.testParameterValue = "secs"
        # testObj.testTypes = [TEST_TYPE_CONN_PARM_HIERARCHY ]
        # #testObj.messageText = ["If synsPerConn > 1, a list of sections or sectionList can be specified. These secs need to be specified in the cell parameters."]
        # #testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        #
        # self.testParamsMap["conn"]["connHierarchyTest"] = testObj

        # # conn list test
        # testObj = TestObj()
        # testObj.testName = "shapeTest"
        # testObj.testParameterType = "string"
        # #testObj.testParameterValue = "secs"
        # testObj.testTypes = [TEST_TYPE_CONN_SHAPE ]
        # #testObj.messageText = ["If synsPerConn > 1, a list of sections or sectionList can be specified. These secs need to be specified in the cell parameters."]
        # #testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        # #
        # self.testParamsMap["conn"]["connShapeTest"] = testObj
        #
        # # conn list test
        # testObj = TestObj()
        # testObj.testName = "shapeTest"
        # testObj.testParameterType = "string"
        # #testObj.testParameterValue = "secs"
        # testObj.testTypes = [TEST_TYPE_CONN_PLASTICITY ]
        # #testObj.messageText = ["If synsPerConn > 1, a list of sections or sectionList can be specified. These secs need to be specified in the cell parameters."]
        # #testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        # #
        # self.testParamsMap["conn"]["connPlasticityTest"] = testObj

        # if self.verboseFlag:
        #     print (" *** Finished loading conn tests *** ")

    def runPopTests(self):

        # if self.verboseFlag:
        #     print ( " ::: flag is " + str(self.verboseFlag))

            # print (" *** Running pop tests *** ")

        popParams = self.netParams.popParams
        for testName, popTestObj in self.testParamsMap["pop"].items():
            self.execRunTests(popTestObj, popParams)

        # if self.verboseFlag:
        #     print (" *** Finished running pop tests *** ")

    def runNetTests(self):

        # if self.verboseFlag:
        #     print (" *** Running net tests *** ")

        netParams = self.netParams
        for testName, netTestObj in self.testParamsMap["net"].items():
            self.execRunTests(netTestObj, netParams)

        # if self.verboseFlag:
        #     print (" *** Finished running net tests *** ")

    def runCellTests(self):

        # if self.verboseFlag:
        #     print (" *** Running cell tests *** ")

        cellParams = self.netParams.cellParams
        #print ( " *** in run cell tests " + str(cellParams))
        for testName, cellTestObj in self.testParamsMap["cell"].items():
            #print ( " ^^^ running test " + cellParams)
            self.execRunTests(cellTestObj, cellParams)

        # if self.verboseFlag:
        #     print (" *** Finished running cell tests *** ")

    def runConnTests(self):

        # if self.verboseFlag:
        #     print (" *** Running conn tests *** ")

        connParams = self.netParams.connParams
        #print (" ** " + str(self.testParamsMap["conn"]))
        for testName, connTestObj in self.testParamsMap["conn"].items():
            self.execRunTests(connTestObj, connParams)

        # if self.verboseFlag:
        #     print (" *** Finished running conn tests *** ")

    def runStimSourceTests(self):

        # if self.verboseFlag:
        #     print (" *** Running stim source tests *** ")

        stimSourceParams = self.netParams.stimSourceParams
        print (str(self.testParamsMap.keys()))
        for testName, stimSourceTestObj in self.testParamsMap["stimSource"].items():
            self.execRunTests(stimSourceTestObj, stimSourceParams)

    def runStimTargetTests(self):

        # if self.verboseFlag:
        #     print (" *** Running stim target tests *** ")

        stimTargetParams = self.netParams.stimTargetParams
        for testName, stimTargetTestObj in self.testParamsMap["stimTarget"].items():
            self.execRunTests(stimTargetTestObj, stimTargetParams)

    def execRunTests(self, testObj, params):

        #print ( " !!!!!!!! for test " + str(testObj.testTypes))

        for testIndex, testType in enumerate(testObj.testTypes):

            #print ( " !!!!!!!! for test " + str(testType))

            if testType == TEST_TYPE_EXISTS:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            self.testTypeObj.testExists (testObj.testParameterValue,  paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramValues))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + " : " + str(testObj.messageText[testIndex])
                else:

                        try:
                            self.testTypeObj.testExists (testObj.testParameterValue,  paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(testObj.testParameterValue))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(testObj.testParameterValue))
                            print str(testObj.errorMessageLevel[testIndex]) + " : " + str(testObj.messageText[testIndex])

            elif testType == TEST_TYPE_EXISTS_IN_LIST:

                if isinstance(params, dict):
                    for paramLabel, paramValues in params.items():

                        try:
                            self.testTypeObj.testExistsInList (testObj.testParameterValueList,  paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramValues))
                            print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + " : " + str(testObj.messageText[testIndex])

                else:

                        try:
                            self.testTypeObj.testExistsInList (testObj.testParameterValueList,  paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(testObj.testParameterValue))
                            print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(testObj.testParameterValue))
                            print str(testObj.errorMessageLevel[testIndex]) + " : " + str(testObj.messageText[testIndex])

            elif testType == TEST_TYPE_EXISTS_IN_DICT:

                if isinstance(params, dict):
                    for paramLabel, paramValues in params.items():

                        try:

                            if paramValues[testObj.testParameterValue] and paramValues[testObj.testParameterValue][testObj.testParameterValue1]:
                                self.testTypeObj.testExistsInDict (  paramValues[testObj.testParameterValue][testObj.testParameterValue1],  eval(testObj.compareDict), testObj.testParameterValue1)
                                if self.verboseFlag:
                                    print ( "Test: " + str(paramValues[testObj.testParameterValue][testObj.testParameterValue1]) + " for : " + str(testType)+ " value : " + str(eval(testObj.compareDict)) )
                                    print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag :
                                print ( "Test " + testObj.testParameterValue + " for : " + str(testType)+ " value : " + str(eval(testObj.compareDict)))
                            print str(testObj.errorMessageLevel[testIndex]) + " : " + str(testObj.messageText[testIndex])

            elif testType == TEST_TYPE_IN_RANGE:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            self.testTypeObj.testInRange(testObj.testParameterValue, eval(testObj.testValueRange), paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType) + " value : " + str(paramValues))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType) + " value : " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + " : " + str(testObj.messageText[testIndex])
                else:

                        try:
                            self.testTypeObj.testInRange(testObj.testParameterValue, eval(testObj.testValueRange), paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(testObj.testParameterValue))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(testObj.testParameterValue))
                            print str(testObj.errorMessageLevel[testIndex]) + " : " + str(testObj.messageText[testIndex])

            elif testType == TEST_TYPE_ARRAY_IN_RANGE:

                    if isinstance(params, dict):

                        for paramLabel, paramValues in params.items():

                            try:
                                testParamValue = self.testTypeObj.testArrayInRange(testObj.testParameterValue, eval(testObj.testValueRange), paramValues)
                                if self.verboseFlag:
                                    print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(testObj.testParameterValue))
                                    print ( "PASSED" )

                            except Exception as e:

                                #traceback.print_exc(file=sys.stdout)
                                if self.verboseFlag:
                                    print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(testObj.testParameterValue))
                                paramValue = ''
                                if testObj.testParameterValue in paramValues:
                                    paramValue = paramValues[testObj.testParameterValue]
                                print str(testObj.errorMessageLevel[testIndex]) + " : " + str(testObj.messageText[testIndex] + " Value = " + str(paramValue))

            elif testType == TEST_TYPE_IS_VALID_RANGE:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            self.testTypeObj.testIsValidRange(testObj.testParameterValue, paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramValues))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + " : " + str(testObj.messageText[testIndex])

                else:

                        try:
                            self.testTypeObj.testIsValidRange(testObj.testParameterValue, paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramValues))
                            print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + " : " + str(testObj.messageText[testIndex])

            elif testType == TEST_TYPE_IS_INT:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            self.testTypeObj.testIsInt(testObj.testParameterValue, paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramValues))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramValues))
                                print str(testObj.errorMessageLevel[testIndex]) + " : " + str(testObj.messageText[testIndex])

                else:

                        try:
                            paramName = eval(testObj.testParameterValue)

                            self.testTypeObj.testIsInt(paramName)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramName))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramName))
                            print "ERROR: Value specified is not an integer."

            elif testType == TEST_TYPE_GTE_ZERO:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            self.testTypeObj.testGteZero(testObj.testParameterValue, paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramValues))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + " : " + str(testObj.messageText[testIndex])

                else:
                        try:
                            paramName = eval(testObj.testParameterValue)

                            self.testTypeObj.testGteZero(paramName)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramName))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramName))
                            print str(testObj.errorMessageLevel[testIndex]) + " : " + str(testObj.messageText[testIndex])

            elif testType == TEST_TYPE_IS_DICT:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            if testObj.testParameterValue in paramValues:
                                self.testTypeObj.testIsDict(paramValues[testObj.testParameterValue])
                                if self.verboseFlag:
                                    print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramValues))
                                    print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + " : " + str(testObj.messageText[testIndex])

            elif testType == TEST_TYPE_EXISTS_IN_ALL_DICTS:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            self.testTypeObj.testExistsInAllDicts(
                                            paramValues,
                                            testObj.testParameterValue,
                                            testObj.testParameterDictString
                                            )

                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramValues))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for : " + str(testType)+ " value : " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + " : " + str(testObj.messageText[testIndex])

            elif testType == TEST_TYPE_VALID_GEOMETRIES:

                if isinstance(params, dict):
                    for paramLabel, paramValues in params.items():
                        try:
                            self.testTypeObj.testValidGeometries(paramValues)
                            if self.verboseFlag:
                                print ( "Test: for valid geometry in cell")
                                print ( "PASSED" )

                        except Exception as e:
                            #traceback.print_exc(file=sys.stdout)
                            if self.verboseFlag:
                                print ( "Test: for valid geometry in cell")
                            #print (str(MESSAGE_TYPE_ERROR) + " : Geometry is invalid. ")
                            print (str(MESSAGE_TYPE_ERROR) + " :" + str(e))

            elif testType == TEST_TYPE_VALID_TOPOLOGIES:

                if isinstance(params, dict):
                    for paramLabel, paramValues in params.items():
                        try:
                            self.testTypeObj.testValidTopologies(paramValues)
                            if self.verboseFlag:
                                print ( "Test: for valid topology in cell")
                                print ( "PASSED" )

                        except Exception as e:
                            #traceback.print_exc(file=sys.stdout)
                            if self.verboseFlag:
                                print ( "Test: for valid topology in cell")
                            #print ( "paramvalues = " + str(paramValues))
                            print (str(MESSAGE_TYPE_ERROR) + ": " + str(e))

            elif testType == TEST_TYPE_VALID_CONN_LIST:

                if isinstance(params, dict):
                    for paramLabel, paramValues in params.items():
                        try:

                            errorMessage = self.testTypeObj.testValidConnList(paramValues)

                            if errorMessage == '':
                                if self.verboseFlag:
                                    print ( "Test: for valid connList in cell")
                                    print ( "PASSED" )
                            else:
                                if self.verboseFlag:
                                    print ( "Test: for valid connList in cell")
                                print ( MESSAGE_TYPE_ERROR + ": " + errorMessage)

                        except Exception as e:
                            #traceback.print_exc(file=sys.stdout)
                            if self.verboseFlag:
                                print ( "Test: for valid conn list in cell")
                            #print ( "paramvalues = " + str(paramValues))
                            print (str(MESSAGE_TYPE_ERROR) + " : Topology is invalid. Must be specified if more than one section specified. For each topology, parentSec and parentX and childX must be defined. ParentSec needs to be a valid section, and both parentX and childX needs to be in range [0,1].")

            elif testType == TEST_TYPE_VALID_MECHS:

                errorMessage = ''
                mechsValid = True
                mechsWarning = False

                mechVarListString = ''

                if 'mechs' in utils.mechVarList():
                    mechVarListString = str(utils.mechVarList()['mechs'])

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():
                        try:
                            errorMessages, mechsValidFlagList, mechsWarningFlagList = self.testTypeObj.testValidMechs(paramValues)
                            #print ( " *******###### errorMessage = " + errorMessage + " mechsValid = " + str(mechsValid) + " mechsWarning " + str(mechsWarning))
                            for errorIndex, errorMessage in enumerate(errorMessages):

                                if errorMessage == '':
                                    if self.verboseFlag:
                                        print ( "Test: for valid mechanisms in cell")
                                        print ( "PASSED" )
                                    continue

                                if mechsValidFlagList[errorIndex]:
                                    if self.verboseFlag:
                                        print ( "Test: for valid mechanisms in cell")
                                    print ( MESSAGE_TYPE_WARNING + ": " + errorMessage)

                                elif mechVarListString[errorIndex]:

                                    if self.verboseFlag:
                                        print ( "Test: for valid mechanisms in cell")

                                    print (str(MESSAGE_TYPE_ERROR) + " : " + errorMessage)

                        except Exception as e:
                            traceback.print_exc(file=sys.stdout)
                            if self.verboseFlag:
                                print ( "Test: for valid mechanisms in cell")

                            print (str(MESSAGE_TYPE_ERROR) + " : Mechanism specified is invalid.")

            elif testType == TEST_TYPE_VALID_POINTPS:

                if isinstance(params, dict):
                    for paramLabel, paramValues in params.items():
                        try:
                            errorMessages = self.testTypeObj.testValidPointps(paramValues)

                            if len(errorMessages) == 0:
                                if self.verboseFlag:
                                    print ( "Test: for pointps in cell params.")
                                    print ( "PASSED" )
                            else:
                                if self.verboseFlag:
                                    print ( "Test: for pointps in cell params.")
                                for errorMessage in errorMessages:
                                    print ( MESSAGE_TYPE_ERROR + ": " + errorMessage)

                        except Exception as e:
                            #traceback.print_exc(file=sys.stdout)
                            if self.verboseFlag:
                                print ( "Test: for valid pointps in cell params.")
                            #print ( "paramvalues = " + str(paramValues))
                            print (str(MESSAGE_TYPE_ERROR) + " : Pointps in cell params specified is invalid. Please check against utils.mechVarlist.")

            elif testType == TEST_TYPE_VALID_SYN_MECHS:

                if isinstance(params, dict):
                    for paramLabel, paramValues in params.items():
                        try:
                            self.testTypeObj.testValidSynMechs(testObj.testParameterValue, paramValues, self.netParams)
                            if self.verboseFlag:
                                print ( "Test: for valid parameters in conn params.")
                                print ( "PASSED" )

                        except Exception as e:
                            #traceback.print_exc(file=sys.stdout)
                            if self.verboseFlag:
                                print ( "Test: for valid parameters in conn params.")
                            #print ( "paramvalues = " + str(paramValues))
                            print (str(MESSAGE_TYPE_ERROR) + ": " + str(e))

            elif testType == TEST_TYPE_EXISTS_IN_POP_LABELS:

                if isinstance(params, dict):
                    for paramLabel, paramValues in params.items():
                        try:
                            errorMessage = self.testTypeObj.testExistsInPopLabels(testObj.testParameterValue, paramValues, self.netParams.popParams)

                            if errorMessage != '':

                                    if self.verboseFlag:
                                        print ( "Test: for valid pop label in conn params.")
                                    print ( MESSAGE_TYPE_WARNING + ": " + errorMessage)

                            elif self.verboseFlag:
                                print ( "Test: for valid pop label in conn params.")
                                print ( "PASSED" )


                        except Exception as e:
                            #traceback.print_exc(file=sys.stdout)
                            if self.verboseFlag:
                                print ( "Test: for valid pop label in conn params.")
                            #print ( "paramvalues = " + str(paramValues))
                            print (str(MESSAGE_TYPE_WARNING) + ": " + str(e) + ".")

            elif testType == TEST_TYPE_VALID_SEC_LIST:

                if isinstance(params, dict):
                    for paramLabel, paramValues in params.items():
                        try:

                            errorMessage = self.testTypeObj.testValidSecLists(paramValues)

                            if errorMessage != '':

                                    if self.verboseFlag:
                                        print ( "Test: for valid sec list in conn params.")
                                    print ( MESSAGE_TYPE_ERROR + ": " + errorMessage)

                            elif self.verboseFlag:
                                print ( "Test: for valid sec list in conn params.")
                                print ( "PASSED" )

                        except Exception as e:
                            traceback.print_exc(file=sys.stdout)
                            if self.verboseFlag:
                                print ( "Test: for valid sec list in conn params.")
                            #print ( "paramvalues = " + str(paramValues))
                            print (str(MESSAGE_TYPE_ERROR) + ": " + str(e) + ".")

            elif testType == TEST_TYPE_CONN_PARM_HIERARCHY:

                if isinstance(params, dict):
                    for paramLabel, paramValues in params.items():
                        try:

                            errorMessage = self.testTypeObj.testTypeHierarchy(paramValues)

                            if errorMessage != '':

                                    if self.verboseFlag:
                                        print ( "Test: for valid hierarchy in conn params.")
                                    print ( MESSAGE_TYPE_WARNING + ": " + errorMessage)

                            elif self.verboseFlag:
                                print ( "Test: for valid hierarchy in conn params.")
                                print ( "PASSED" )

                        except Exception as e:
                            traceback.print_exc(file=sys.stdout)
                            if self.verboseFlag:
                                print ( "Test: for valid hierarchy in conn params.")
                            #print ( "paramvalues = " + str(paramValues))
                            print (str(MESSAGE_TYPE_WARNING) + ": " + str(e) + ".")

            elif testType == TEST_TYPE_CONN_SHAPE:

                if isinstance(params, dict):
                    for paramLabel, paramValues in params.items():
                        try:

                            errorMessages = self.testTypeObj.testValidConnShape(paramValues)

                            if len(errorMessages) == 0:
                                if self.verboseFlag:
                                    print ( "Test: for valid shape in conn params.")
                                    print ( "PASSED" )
                            else:
                                if self.verboseFlag:
                                    print ( "Test: for valid shape in conn params.")
                                for errorMessage in errorMessages:
                                    print ( MESSAGE_TYPE_ERROR + ": " + errorMessage)

                        except Exception as e:
                            traceback.print_exc(file=sys.stdout)
                            if self.verboseFlag:
                                print ( "Test: for valid conn shape in conn params.")
                            #print ( "paramvalues = " + str(paramValues))
                            print (str(MESSAGE_TYPE_ERROR) + ": " + str(e) + ".")

            elif testType == TEST_TYPE_CONN_PLASTICITY:

                if isinstance(params, dict):
                    for paramLabel, paramValues in params.items():
                        try:

                            errorMessages = self.testTypeObj.testValidConnPlasticity(paramValues)

                            if len(errorMessages) == 0:
                                if self.verboseFlag:
                                    print ( "Test: for valid plasticity in conn params.")
                                    print ( "PASSED" )
                            else:
                                if self.verboseFlag:
                                    print ( "Test: for valid plasticity in conn params.")
                                for errorMessage in errorMessages:
                                    print ( MESSAGE_TYPE_ERROR + ": " + errorMessage)

                        except Exception as e:
                            traceback.print_exc(file=sys.stdout)
                            if self.verboseFlag:
                                print ( "Test: for valid plasticity in conn params.")
                            #print ( "paramvalues = " + str(paramValues))
                            print (str(MESSAGE_TYPE_ERROR) + ": " + str(e) + ".")

            elif testType == TEST_TYPE_STIM_SOURCE_TEST:

                if isinstance(params, dict):
                    for paramLabel, paramValues in params.items():
                        try:

                            errorMessages = self.testTypeObj.testValidStimSource(paramValues)

                            if len(errorMessages) == 0:
                                if self.verboseFlag:
                                    print ( "Test: for valid stim source.")
                                    print ( "PASSED" )
                            else:
                                if self.verboseFlag:
                                    print ( "Test: for valid stim source.")
                                for errorMessage in errorMessages:
                                    print ( MESSAGE_TYPE_ERROR + ": " + errorMessage)

                        except Exception as e:
                            traceback.print_exc(file=sys.stdout)
                            if self.verboseFlag:
                                print ( "Test: for valid stim source.")
                            #print ( "paramvalues = " + str(paramValues))
                            print (str(MESSAGE_TYPE_ERROR) + ": " + str(e) + ".")

            elif testType == TEST_TYPE_STIM_TARGET_TEST:

                if isinstance(params, dict):
                    for paramLabel, paramValues in params.items():
                        try:

                            errorMessages = self.testTypeObj.testValidStimTarget(paramValues, self.netParams)

                            if len(errorMessages) == 0:
                                if self.verboseFlag:
                                    print ( "Test: for valid stim target.")
                                    print ( "PASSED" )
                            else:
                                if self.verboseFlag:
                                    print ( "Test: for valid stim target.")
                                for errorMessage in errorMessages:
                                    print ( MESSAGE_TYPE_ERROR + ": " + errorMessage)

                        except Exception as e:
                            traceback.print_exc(file=sys.stdout)
                            if self.verboseFlag:
                                print ( "Test: for valid stim target.")
                            #print ( "paramvalues = " + str(paramValues))
                            print (str(MESSAGE_TYPE_ERROR) + ": " + str(e) + ".")

            elif testType == TEST_TYPE_IS_VALID_SPIKE_GENLOC:

                if isinstance(params, dict):
                    for paramLabel, paramValues in params.items():
                        try:

                            errorMessages = self.testTypeObj.testValidSpikeGenLoc(paramValues)

                            if len(errorMessages) == 0:
                                if self.verboseFlag:
                                    print ( "Test: for valid spike gen loc target.")
                                    print ( "PASSED" )
                            else:
                                if self.verboseFlag:
                                    print ( "Test: for valid spike gen loc target.")
                                for errorMessage in errorMessages:
                                    print ( MESSAGE_TYPE_ERROR + ": " + errorMessage)

                        except Exception as e:
                            traceback.print_exc(file=sys.stdout)
                            if self.verboseFlag:
                                print ( "Test: for valid spike gen loc target.")
                            #print ( "paramvalues = " + str(paramValues))
                            print (str(MESSAGE_TYPE_ERROR) + ": " + str(e) + ".")
