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
from neuron import h
from netpyne import utils

VALID_SHAPES = ['cuboid', 'ellipsoid', 'cylinder']
POP_NUMCELLS_PARAMS = ['Density','NumCells','GridSpacing']
VALID_GEOMETRIES = ['cm', 'L', 'diam', 'Ra', 'pt3d', 'nseg']
VALID_GEOMETRIES_SUBSET = ['L', 'diam', 'Ra']
PT_3D = 'pt3d'
VALID_TOPOLOGY_PARAMS = ['parentSec', 'parentX','childX']
PULSE_KEYS = ['start','end','rate','noise']
POP_STIM_KEYS = ['seeds','start','end','rate','noise','spkTimes','pulses']

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
TEST_TYPE_IS_LIST = "Is list" # must be a list
TEST_TYPE_IS_BOOL = "Is boolean" # must be a boolean

TEST_TYPE_IS_NUMERIC = "Is Numeric" # must be numeric
TEST_TYPE_IS_FLOAT = "Is Float" # must be float
TEST_TYPE_IS_INT = "Is Integer" # must be integer
TEST_TYPE_IS_CHARACTER = "Is Character" # must be char [a-z][A-Z]
TEST_TYPE_VALUE_LIST = "Value List" # must be in valid values list
TEST_TYPE_ALL_VALUE_LIST = " All value list" # every key in list must belong to list
TEST_TYPE_EXISTS_IN_DICT = "Exists in Dict" # input param must exist in dict
TEST_TYPE_EXISTS_IN_NESTED_DICT = "Exists in nested dict" # input param must exist in nested dict
TEST_TYPE_SPECIAL = "Special" # special method, method name provided
TEST_TYPE_EXISTS_IN_ALL_DICTS = "Exists in all dicts"
TEST_TYPE_DICT_KEY_VALID_VALUE = "Dict key is valid value"

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
TEST_TYPE_VALID_STIM = "Valid stim"
TEST_TYPE_VALID_ANALYSIS = " Valid analysis"
TEST_TYPE_VALID_HPARAMS = "hParams test"
class TestTypeObj(object):

    def __init__(self):

        self.testType = '' # test name
        self.params = ''
        self.errorMessages = []

    def __unicode__(self):
        return str(self.testType)

    def testExists(self, val,params):
        try:
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
            #print ( " VAL = " + str(val) + " paramDict " + str(paramDict) + " dictKey " + str(dictKey))
            if val == '':
                return
            existsInDict = False
            for key, valueDict in paramDict.items():
                if val == valueDict[dictKey]:
                    existsInDict = True
                    break
            assert existsInDict is True, " Value " + str(val) + "."
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
            assert existsInDict is True, " Value " + str(paramKey) + "."
        except AssertionError as e:
            e.args += (val,)
            raise

    def testExistsInPopLabels(self, val,paramValues, popLabels):
        try:
            existsInPopLabels = False
            popLabelsSpecified = False
            paramPopLabel = ''
            errorMessage = ''
            if isinstance (paramValues[val], dict ) and 'popLabel' in paramValues[val]:
                popLabelsSpecified = True
                #print( " LLL **** ")
                if isinstance (popLabels, dict) and paramValues[val]['popLabel'] not in popLabels.keys():
                    errorMessage = "ConnParams->'popLabel': Pop label specified in conn params is: " + str(paramValues[val]['popLabel']) + ". This does not exist in list of pop labels = " + str(popLabels.keys()) + "."
                    return errorMessage
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
                assert (params[val][0] >= range[0] and params[val][1] <= range[1])
        except AssertionError as e:
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
            # print (" **** val in dict = " + str(val))
            if val and val != '':
                assert (isinstance (val,dict)), "Value specified is " + val + "."
        except AssertionError as e:
            # print ( " ***** " + str(e))
            #e.args += (,)
            raise

    def testIsList(self,val): # TEST_TYPE_IS_LIST
        try:
            if val and val != '':
                assert (isinstance (val,list)), "Value specified is " + str(val) + "."
        except AssertionError as e:
            #e.args += (,)
            raise

    def testIsBoolean(self,val): # TEST_TYPE_IS_BOOLEAN
        try:
            assert (isinstance (val,bool) or val in [0,1]), "Value specified is " + str(val) + "."
        except AssertionError as e:
            #e.args += (,)
            raise

    def testIsNumeric(self,val): # TEST_TYPE_IS_NUMERIC
        try:
            assert (isinstance (val,numbers.Number))
        except AssertionError as e:
            #e.args += (val,)
            raise

    def testIsFloat(self,val): # TEST_TYPE_IS_FLOAT
        try:
            #print (" in float *** = " + str(val))
            assert (isinstance (val,numbers.Real))
        except AssertionError as e:
            #print ( " !!!!! in float error ")
            #e.args += (val,)
            raise

    def testIsInt(self,val): # TEST_TYPE_IS_INT
        try:
            assert (isinstance (val,int))
        except AssertionError as e:
            #e.args += (val,)
            raise

    def testIsCharacter(self,val): # TEST_TYPE_IS_CHARACTER
        try:
            isascii = lambda s: len(s) == len(s.encode())
            assert (isascii (val))
        except AssertionError as e:
            #e.args += (,)
            raise

    def testIsValueList(self,val, valList): # TEST_TYPE_VALUE_LIST
        try:
            # print ( " in val list test" + str(val) + " :: " + str(valList))
            assert (val in valList), str(val) + " must be in list " + str(valList)
        except AssertionError as e:
            print (e)
            #e.args += (,)
            raise

    def testIsAllValueList(self,val, valList): # TEST_TYPE_ALL_VALUE_LIST
        try:
            #print ( " 1")
            # print ( " in val list test" + str(val) + " :: " + str(valList))
            if isinstance(val, list) and isinstance(valList, list):
                assert (all([x in valList for x in val])), str(val[[x in valList for x in val].index(False)]) + " must be in list " + str(valList)
        except AssertionError as e:
            #print (" 1" + str(e))
            #e.args += (,)
            raise

    def testDictKeyValidValue(self,paramDict, valList): # TEST_TYPE_VALUE_LIST
        try:
            #print ( "2")
            #print ( " in val list test" + str(paramDict) + " :: " + str(valList))
            if isinstance(paramDict, dict) and isinstance(valList, list):
                if isinstance(valList, str):
                    valList = eval(valList)
                assert (all([x in valList for x in paramDict.keys()])), " contains invalid key '" + str(paramDict.keys()[[x in valList for x in paramDict.keys()].index(False)]) + "': Valid values are: " + str(valList) + "."
                #assert (all([x in valList for x in paramDict.keys()])), str(paramDict) + " must have keys in list " + str("") + ". Keys provided are " + str(paramDict.keys()) + "."

        except AssertionError as e:
            #print (" **** " + str(e))
            #e.args += (,)
            raise

    def testValidStim(self,paramValues): # TEST_TYPE_VALID_STIM
        try:

            stimValid = True
            stimParamsAllowed = False
            errorMessages = []

            #print ( " IN VALIDATION !!!! " + str(isinstance (paramValues, dict)))

            if isinstance (paramValues, dict):
                # for key, value in paramValues.items():
                #     print ( " IN VALIDATION 2222 !!!! " + str(value))
                #     if isinstance (value, dict):
                #         print ( 'cellModel' + str(value['cellModel']) )
                pointpsValues = []
                if 'pointps' in utils.mechVarList() and isinstance(utils.mechVarList()['pointps'], dict):
                    pointpsValues = utils.mechVarList()['pointps'].keys()
                if 'cellModel' in paramValues:
                    if paramValues['cellModel'] in pointpsValues:
                        stimParamsAllowed = True
            if not stimParamsAllowed:
                if any([x in POP_STIM_KEYS for x in  paramValues]):
                    stimValid = False
                    errorMessages.append("popParams: Any or all of the params '" + str(POP_STIM_KEYS)+ "' are allowed only if cellModel in '" + str(['IntFire1', 'IntFire2', 'NetStim', 'VecStim']) + "'.")
            else: # if stimParamsAllowed:
                #print ( " IN ELSE !!!!" + str(paramValues.keys()) + ":: " + str('pulses' in paramValues))
                if 'interval' in paramValues:
                    if not isinstance(paramValues['interval'], numbers.Real):
                        stimValid = False
                        errorMessages.append("popParams->'interval': Must be a float if specified. Value provided is:" + str(paramValues['interval']))
                if 'rate' in paramValues:
                    if not isinstance(paramValues['rate'], numbers.Real):
                        stimValid = False
                        errorMessages.append("popParams->'rate': Must be a float if specified. Value provided is:" + str(paramValues['rate']))
                if 'noise' in paramValues:
                    if not isinstance(paramValues['noise'], numbers.Real):
                        stimValid = False
                        errorMessages.append("popParams->'noise': Must be a float between 0 and 1 if specified. Value provided is:" + str(paramValues['noise']))
                    elif float(paramValues['noise']) < 0 or float(paramValues['noise']) > 1:
                        stimValid = False
                        errorMessages.append("popParams->'noise': Must be a float between 0 and 1 if specified. Value provided is:" + str(paramValues['noise']))
                if 'start' in paramValues:
                    if not isinstance(paramValues['start'], numbers.Real):
                        stimValid = False
                        errorMessages.append("popParams->'start': Must be a float if specified. Value provided is:" + str(paramValues['start']))
                if 'number' in paramValues:
                    if not isinstance(paramValues['number'], numbers.Real):
                        stimValid = False
                        errorMessages.append("popParams->'number': Must be a float if specified. Value provided is:" + str(paramValues['number']))
                if paramValues['cellModel'] != 'VecStim' and any([x in paramValues for x in ['spkTimes', 'pulses']]):
                        stimValid = False
                        errorMessages.append("popParams: 'spkTimes' or 'pulses' can be provided if 'cellModel' is 'VecStim' ")
                if 'spkTimes' in paramValues:
                    if not isinstance(paramValues['spkTimes'], list):
                        stimValid = False
                        errorMessages.append("popParams->'spkTimes': Must be a list if specified. Value provided is:" + str(paramValues['spkTimes']))
                if 'pulses' in paramValues:
                    #print (" *** IN PULSES ")
                    if not isinstance(paramValues['pulses'], list):
                        stimValid = False
                        errorMessages.append("popParams->'pulses': Must be a list of dicts if specified. They keys for each dict are '" + str(PULSE_KEYS) + "' Value provided is:" + str(paramValues['pulses']))
                    if not all( [isinstance(x, dict) for x in paramValues['pulses']]):
                        stimValid = False
                        errorMessages.append("popParams->'pulses': Must be a list of dicts if specified. Value provided is:" + str(paramValues['pulses']))
                    for pulseValue in paramValues['pulses']:
                        if not all([x in PULSE_KEYS for x in pulseValue.keys()]):
                            stimValid = False
                            errorMessages.append("popParams->'pulses': Must be a list of dicts if specified. Value provided is:'" + str(paramValues['pulses']) + "'. Keys of each dict must be in '" + str(PULSE_KEYS) + "'.")

        except Exception as e:
            e.args += ()
            raise

        return stimValid, errorMessages

    def testValidGeometries(self,paramValues): # TEST_TYPE_VALUE_LIST
        geomValid = True
        errorMessage = ''
        try:
            if 'secs' in paramValues:
                for key, values in paramValues['secs'].items():
                    if 'geom' in values:
                        if len(values['geom']) == 0:
                            errorMessage = "cellParams -> secs ('" + str(key) + "'): Geom parameters must be specified."
                            geomValid = False
                        if not isinstance(values['geom'], dict):
                            errorMessage = "cellParams -> secs ('" + str(key) + "'): Geom parameters must be specified as a dict."
                            geomValid = False
                        # if any ([x in values['geom'].keys() for x in VALID_GEOMETRIES_SUBSET]) and not all([x in values['geom'].keys() for x in VALID_GEOMETRIES_SUBSET]):
                        #     #print (" ----++ 999")
                        #     errorMessage = "cellParams -> secs ('" + str(key) + "'): If one of '" + str(VALID_GEOMETRIES_SUBSET) + "' are specified, then at least all of the parameters in that list needs to be specified. Values specified are: '" + str(values['geom']) + "'."
                        #     geomValid = False
                        if not geomValid:
                            break
                        #assert geomValid is True

                        for key1, values1 in values['geom'].items():

                            if key1 not in VALID_GEOMETRIES:
                                errorMessage = "cellParams -> secs ('" + str(key) + "') -> 'geom': Invalid geom parameter '"+ str(key1) + "' specified. Valid values are '" + str(VALID_GEOMETRIES) + "'."
                                geomValid = False
                            if not geomValid:
                                break
                            #assert geomValid is True

                            if PT_3D in values['geom']:
                                if not isinstance ( values['geom'][PT_3D] , list ):
                                    errorMessage = "cellParams -> secs ('" + str(key) + "') -> 'geom': pt3D must be an array with each array element being a 4-element list or array of floats."
                                    geomValid = False
                                elif len(values['geom'][PT_3D]) == 0:
                                    errorMessage = "cellParams -> secs ('" + str(key) + "') -> 'geom': At least one element must be provided for pt3D."
                                    geomValid = False

                                if not geomValid:
                                    break
                                #assert geomValid is True

                                for elem in values['geom'][PT_3D]:
                                    if not isinstance ( elem , list ):
                                        errorMessage = "cellParams -> secs ('" + str(key) + "') -> 'geom' -> 'pt3D':Type error. pt3D must be an array with each array element being a 4-element list or array of floats.Value specified is: '" + str(elem) + "'."
                                        geomValid = False
                                    elif len(elem) != 4:
                                        errorMessage = "cellParams -> secs ('" + str(key) + "') -> 'geom' -> 'pt3D':Length error. pt3D must be an array with each array element being a 4-element list or array of floats.Value specified is: '" + str(elem) + "'."
                                        geomValid = False
                                    if not geomValid:
                                        break
                                    for elem2 in elem:
                                        if not isinstance ( elem2, numbers.Real ):
                                            errorMessage = "cellParams -> secs ('" + str(key) + "') -> 'geom' -> 'pt3D':Float error. pt3D must be an array with each array element being a 4-element list or array of floats. Value specified is: '" + str(elem2) + "'."
                                            geomValid = False
                                        if not geomValid:
                                            break

            assert geomValid is True, errorMessage
        except AssertionError as e:
            e.args += ()
            raise
        # except Exception as e:
        #     traceback.print_exc(file=sys.stdout)
        #     raise

    def testValidTopologies(self,paramValues): # TEST_TYPE_VALUE_LIST
        try:

            topolValid = True
            topolNeeded = False
            errorMessage = ''

            if 'secs' in paramValues:
                if len(paramValues['secs']) > 0:
                    if len(paramValues['secs']) > 1: topolNeeded = True
                    for key, value in paramValues['secs'].items():
                        if 'topol' not in value:
                            if topolNeeded:
                                topolValid = False
                                errorMessage = "cellParams -> secs ('" + str(paramValues['secs'].keys()) + "'): Topology needs to be specified if more than one section."
                        else:
                            topolValid = True

                            if not isinstance (value['topol'], dict ):
                                topolValid = False
                                errorMessage = "cellParams -> secs ('" + str(key) + "') -> topol: Topology, if specified, must be a dict. Value specified is '" + str(value['topol']) + "'."

                            elif len(value['topol'].keys()) < 3:
                                topolValid = False
                                errorMessage = "cellParams -> secs ('" + str(key) + "') -> topol: At least 3 parameters (parentSec, parentX and childX) must be specified for topology. Values specified are: '" + str(value['topol'].keys()) + "'."
                            elif not any([x in value['topol'].keys() for x in VALID_TOPOLOGY_PARAMS ]):
                                topolValid = False
                                errorMessage = "cellParams -> secs ('" + str(key) + "') -> topol: Invalid value specified:''" + str(value['topol']) + "'. Valid values are: '" + str(VALID_TOPOLOGY_PARAMS) + "'."
                            elif value['topol']['parentSec'] not in paramValues['secs']:
                                topolValid = False
                                errorMessage = "cellParams -> secs ('" + str(key) + "') -> topol -> parentSec: parentSec '" + str(value['topol']['parentSec']) +"' does not point to a valid section. Valid sections are ('" + str(paramValues['secs'].keys()) + "')."
                            elif not isinstance ( value['topol']['parentX'] , numbers.Real ):
                                topolValid = False
                                errorMessage = "cellParams -> secs ('" + str(key) + "') -> topol -> parentX: Value should be a float."
                            elif not isinstance ( value['topol']['childX'] , numbers.Real ):
                                topolValid = False
                                errorMessage = "cellParams -> secs ('" + str(key) + "') -> topol -> childX: Value should be a float."
                            elif value['topol']['parentX'] < 0 or value['topol']['parentX'] >1:
                                topolValid = False
                                errorMessage = "cellParams -> secs ('" + str(key) + "') -> topol -> parentX: parentX must be between 0 and 1. Value specified is '" + str(value['topol']['parentX'] ) + "'."
                            elif value['topol']['childX'] < 0 or value['topol']['childX'] >1:
                                topolValid = False
                                errorMessage = "cellParams -> secs ('" + str(key) + "') -> topol -> parentX: childX must be between 0 and 1. Value specified is '" + str(value['topol']['childX'] ) + "'."

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
                                        if not any([x in mechs[key2] for x in values2.keys() ]):
                                            mechsValidFlag = False
                                            errorMessage = "cellParams -> secs ('" + str(key) + "') -> mechs ('" + str(key2) + "') -> ions ('" + str(ionName) + "'): Invalid ions (" + str(values2.keys()) + ") specified. Valid value are: " + str(mechs[key2]) + ". Values specified are " + str(values2.keys()) + "."
                                        elif not all([x in values2.keys() for x in mechs[key2] ]):
                                            mechsWarningFlag = True
                                            errorMessage = "cellParams -> secs ('" + str(key) + "') -> mechs ('" + str(key2) + "') -> ions ('" + str(ionName) + "'): Ion specifications incomplete (" + str(values2.keys()) + "). Complete list is: " + str(mechs[key2]) + ". Values specified are " + str(values2.keys()) + "."
                                    else:
                                        keys_suffixed = [x + "_" + key2 for x in values2.keys()]
                                        mechs_unsuffixed = [x.replace("_" + key2, "") for x in mechs[key2]]
                                        if not all([x in mechs[key2] for x in keys_suffixed]):
                                            mechsValidFlag = False
                                            errorMessage = "cellParams -> secs ('" + str(key) + "') -> mechs ('" + str(key2) + "'): Invalid mechs (" + str(values2.keys()) + ") specified . Valid value are: " + str(mechs_unsuffixed) + ". Values specified are " + str(values2.keys()) + "."
                                        elif not all([x in keys_suffixed for x in mechs[key2] ]):
                                            mechsWarningFlag = True
                                            errorMessage = "cellParams -> secs ('" + str(key) + "') -> mechs ('" + str(key2) + "'): Incomplete list provided. Complete list is: " + str(mechs_unsuffixed) + ". Values specified are " + str(values2.keys()) + "."

                                    mechsValidFlagList.append(mechsValidFlag)
                                    mechsWarningFlagList.append(mechsWarningFlagList)
                                    errorMessages.append(errorMessage)

        except:
            raise

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
                                    #print (" ** keys2, values2 = " + str(key2) + ":: " + str(values2))
                                    if 'mod' not in values2.keys():
                                        errorMessages.append("cellParams -> secs ('" + str(key) + "') -> pointps ('" + str(key2) + "'): mod must be specified")
                                        pointpsValid = False
                                    elif 'loc' in values2.keys():
                                        loc = values2['loc']
                                        if not isinstance(loc, numbers.Real ):
                                            errorMessages.append("cellParams -> secs ('" + str(key) + "') -> pointps ('" + str(key2) + "'): Loc must be a float. Value provided is " + str(loc))
                                        elif loc < 0 or loc >1:
                                            errorMessages.append("cellParams -> secs ('" + str(key) + "') -> pointps ('" + str(key2) + "'): Loc must be a between 0 and 1. Value provided is " + str(loc))
                                    elif 'synList' in values2.keys():
                                        if not isinstance ('synList', list):
                                            errorMessages.append("cellParams -> secs ('" + str(key) + "') -> pointps ('" + str(key2) + "'): SynList must be a list. Value provided is " + str(values2['synList']))

        except AssertionError as e:
            e.args += ()
            raise

        return errorMessages

    def testArrayInRange(self, val,range, params): # TEST_TYPE_IN_RANGE
        try:
            if val in params:
                if isinstance (params[val], list):
                    flattenedList = numpy.ravel(params[val])
                    for x in flattenedList:
                        assert (x >= range[0] and x <= range[1])
                elif isinstance (params[val], numbers.Real):
                    assert (params[val] >= range[0] and params[val] <= range[1])
        except AssertionError as e:
            e.args += (e,)
            raise

    def checkSyncMechs(self,paramValue, values, dimValues, dimSynMechs, synsPerConn): # check syncMechs

        errorMessage = ''
        synMechsValid = True

        try:

            if dimSynMechs == 1:
                if synsPerConn != 1:
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
                    if dimValues not in [0,1,2]:
                        errorMessage = "ConnParams -> '" + str(paramValue) + "' can only be a number or 1d or 2D list if more than 1 synMech and synsPerConn > 1."
                        synMechsValid = False
                    elif dimValues == 1 and len(values) != dimSynMechs:
                        errorMessage = "ConnParams -> '" + str(paramValue) + "' can only be a number or 1d or 2D list if more than 1 synMech and synsPerConn > 1."
                        synMechsValid = False
                    elif dimValues == 2:
                        if numpy.array(locs).shape[1] != synsPerConn:
                            errorMessage = "ConnParams -> '" + str(paramValue) + "' can only be a number or 1d or 2D list if more than 1 synMech and synsPerConn > 1."
                            synMechsValid = False
                        elif numpy.array(values).shape[0] != dimSynMechs:
                            errorMessage = "ConnParams -> '" + str(paramValue) + "': Invalid " + str(paramValue) + " for synMechs and synsPerConn. If specifying 2D array, please ensure that the array of arrays has the number of elements as # of synMechs, with each array having the number of elements as specified by synsPerConn."
                            synMechsValid = False
                else: # only 1 synsPerConn
                    if dimValues not in [0,1]:
                        errorMessage =  "ConnParams -> " + str(paramValue) + " can only be a number or 1 D list if more than 1 synMech and synsPerConn = 1."
                        synMechsValid = False
                    elif dimValues == 1 and len(values) != dimSynMechs:
                        errorMessage =  "ConnParams -> " + sstr(paramValue) + " can only be a number or 1d or 2D list if more than 1 synMech and synsPerConn = 1."
                        synMechsValid = False
        except Exception as e:
            return errorMessage, synMechsValid

        return errorMessage, synMechsValid

    def checkConnList(self,paramValue, values, dimValues, dimSynMechs, synsPerConn): # check syncMechs
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

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            raise
        return errorMessage, synMechsValid

    def testValidSynMechs(self,parameterName, paramValues, netParams): # TEST_TYPE_VALID_SYN_MECHS

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

            #print ( " @@@@ valid sections = " + str(validSections))
            if 'secList' in cellParams:
                secList = cellParams['secList']
                #print ( " seclist = " + str(secList))
                if not isinstance (secList, dict):
                    errorMessage = "cellParams -> seclist must be a dict."
                else:
                    for key, value in secList.items():
                        #print ( " ^^^^^^^^ value = " + str(value))
                        if not isinstance (value, list):
                            errorMessage = "cellParams -> secList ('" + str(key) + "'):Each element of seclist must be a list. Value specified is: " + str(value) + "."
                        elif any ([x not in validSections for x in value]):
                            errorMessage = "cellParams -> secList ('" + str(key) + "'): " + str(value) + " - Sections specified in secList keys must be specified in cells. Valid list is " + str(validSections) + "."

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            e.args += (errorMessage, )
            raise
        return errorMessage

    def testTypeHierarchy(self,paramValues): # TEST_TYPE_CONN_PARM_HIERARCHY

        # probability > convergence > divergenece > connList

        errorMessage = ''

        #print ( "::: in hierarchy ")

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
                if pulseType not in ['square', 'gaussian']:
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
            else:
                return errorMessages

            if not isinstance ( plasticity, dict):
                errorMessage = "connParams -> 'plasticity': Plasticity must be a dict."
                errorMessages.append(errorMessage)
                return errorMessages

            if 'mech' not in plasticity:
                errorMessage = "connParams -> 'plasticity':'mech' must be specified in plasticity in connParams with label."
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
                    errorMessage = "StimSourceParams: Invalid parameter specified. Values specified are " + str(allKeys) + ", while allowed values are: " + str(allowedValues)
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

    def testValidAnalysis(self, simConfig): # TEST_TYPE_VALID_ANALYSIS

        errorMessages = []
#        print ( " *** in analysis test" )
        try:

            if simConfig and simConfig.analysis:

                analysis = simConfig.analysis

                if not isinstance ( simConfig.analysis, dict):
                    errorMessages.append("SimConfig->'analysis': Must be a dict. Value provided is " + str(simConfig.analysis) + ".")
                    return errorMessages
                #print (" before ")
                validList = ['plotRaster','plotSpikeHist', 'plotSpikePSD', 'plotTraces', 'plotConn', 'plotConn', 'plot2Dnet', 'nTE', 'granger']
                # print ( [x in validList for x in analysis.keys()] )
                if not all ([x in validList for x in analysis.keys()]):
                    errorMessages.append("SimConfig->'analysis': Valid analysis functions are 'plotRaster','plotSpikeHist', 'plotSpikePSD', 'plotTraces', 'plotShape', 'plotConn', 'plot2DNet', 'nTE', 'granger'. Keys specified are " + str(analysis.keys()) + ".")
                #print (" after ")

                if 'plotRaster' in analysis:
                    #print ( " in plot raster ")

                    plotRaster = analysis['plotRaster']

                    if not isinstance ( plotRaster, dict) and not isinstance ( plotRaster, bool):
                        errorMessages.append("SimConfig->'analysis'->'plotRaster': Must be a dict.  Value provided is " + str(plotRaster) + ".")

                    else:

                        #print ( " in plot raster 2 " + str(plotRaster.keys()))
                        validList = ['include', 'timeRange', 'maxSpikes', 'orderBy', 'orderInverse', 'labels', 'popRates', 'spikeHist', 'spikeHistBin', 'syncLines', 'figSize', 'saveData', 'saveFig', 'showFig']

                        if not all(x in validList for x in plotRaster.keys()):
                            errorMessages.append("SimConfig->'analysis'->'plotRaster': plotRaster must be a dict with keys in list " + str(validList) + ". Keys supplied are " + str(plotRaster.keys()) + ".")

                        if 'include' in plotRaster and not isinstance( plotRaster['include'], dict):
                            errorMessages.append("SimConfig->'analysis'->'plotRaster'->'include': Must be a list. Value provided is " + str(plotRaster['include']) + ".")

                        # if 'timeRange' in plotRaster and not isinstance( plotRaster['timeRange'], dict):
                        #     errorMessages.append("SimConfig->'analysis'->'plotRaster'->'timeRange': Must be a list. Value provided is " + str(plotRaster['timeRange']) + ".")

                        if 'maxSpikes' in plotRaster and not isinstance( plotRaster['maxSpikes'], int):
                            errorMessages.append("SimConfig->'analysis'->'plotRaster'->'maxSpikes': Must be an integer. Value provided is " + str(plotRaster['maxSpikes']) + ".")

                        if 'orderBy' in plotRaster:

                            if not isinstance( plotRaster['orderBy'], list):
                                errorMessages.append("SimConfig->'analysis'->'plotRaster'->'orderBy': Must be a list. Value provided is " + str(plotRaster['orderBy']) + ".")
                            else:
                                if any ( [x not in ['gid', 'ynorm', 'y'] for x in plotRaster['orderBy'] ] ):
                                    errorMessages.append("SimConfig->'analysis'->'plotRaster'->'orderBy': Valid values are " + str(['gid', 'ynorm', 'y'])+ ". Value provided is " + str(plotRaster['orderBy']) + ".")

                        if 'orderInverse' in plotRaster:

                            if not isinstance( plotRaster['orderInverse'], bool):
                                errorMessages.append("SimConfig->'analysis'->'plotRaster'->'orderInverse': Must be boolean. Value provided is " + str(plotRaster['orderInverse']) + ".")

                        if 'labels' in plotRaster:

                            if not isinstance( plotRaster['labels'], list):
                                errorMessages.append("SimConfig->'analysis'->'plotRaster'->'labels': Must be a list. Value provided is " + str(plotRaster['labels']) + ".")
                            else:
                                if any ( [x not in ['legend', 'overlay', 'y'] for x in plotRaster['labels'] ] ):
                                    errorMessages.append("SimConfig->'analysis'->'plotRaster'->'labels': Valid values are " + str(['legend', 'overlay'])+ ". Value provided is " + str(plotRaster['labels']) + ".")

                        if 'popRates' in plotRaster:

                            if not isinstance( plotRaster['popRates'], list):
                                errorMessages.append("SimConfig->'analysis'->'plotRaster'->'popRates': Must be a list. Value provided is " + str(plotRaster['popRates']) + ".")
                            else:
                                if any ( [x not in ['legend', 'overlay', 'y'] for x in plotRaster['popRates'] ] ):
                                    errorMessages.append("SimConfig->'analysis'->'plotRaster'->'popRates': Valid values are " + str(['legend', 'overlay'])+ ". Value provided is " + str(plotRaster['labels']) + ".")

                        if 'popRates' in plotRaster:

                            if not isinstance( plotRaster['popRates'], list):
                                errorMessages.append("SimConfig->'analysis'->'plotRaster'->'popRates': Must be a list. Value provided is " + str(plotRaster['popRates']) + ".")
                            else:
                                if any ( [x not in ['legend', 'overlay', 'y'] for x in plotRaster['popRates'] ] ):
                                    errorMessages.append("SimConfig->'analysis'->'plotRaster'->'popRates': Valid values are " + str(['legend', 'overlay'])+ ". Value provided is " + str(plotRaster['labels']) + ".")

                        if 'spikeHist' in plotRaster:

                            if not isinstance( plotRaster['spikeHist'], list):
                                errorMessages.append("SimConfig->'analysis'->'plotRaster'->'spikeHist': Must be a list. Value provided is " + str(plotRaster['spikeHist']) + ".")
                            else:
                                if any ( [x not in ['legend', 'overlay', 'y'] for x in plotRaster['spikeHist'] ] ):
                                    errorMessages.append("SimConfig->'analysis'->'plotRaster'->'spikeHist': Valid values are " + str(['legend', 'overlay'])+ ". Value provided is " + str(plotRaster['labels']) + ".")

                if 'plotSpikeHist' in analysis:

                    plotSpikeHist = analysis['plotSpikeHist']

                    if not isinstance ( plotSpikeHist, dict) and not isinstance ( plotSpikeHist, bool):
                        errorMessages.append("SimConfig->'analysis'->'plotSpikeHist': Must be a dict.  Value provided is " + str(plotSpikeHist) + ".")

                    if 'include' in plotSpikeHist and not isinstance( plotSpikeHist['include'], list):
                        errorMessages.append("SimConfig->'analysis'->'plotSpikeHist'->'include': Must be a list. Value provided is " + str(plotSpikeHist['include']) + ".")

                    # if 'timeRange' in plotRaster and not isinstance( plotRaster['timeRange'], dict):
                    #     errorMessages.append("SimConfig->'analysis'->'plotRaster'->'timeRange': Must be a list. Value provided is " + str(plotRaster['timeRange']) + ".")

                    if 'orderInverse' in plotRaster:

                        if not isinstance( plotRaster['orderInverse'], bool) and not isinstance ( plotSpikeHist, dict):
                            errorMessages.append("SimConfig->'analysis'->'plotRaster'->'orderInverse': Must be boolean. Value provided is " + str(plotRaster['orderInverse']) + ".")

                    if 'overlay' in plotRaster:

                        if not isinstance( plotRaster['overlay'], bool):
                            errorMessages.append("SimConfig->'analysis'->'plotRaster'->'overlay': Must be boolean. Value provided is " + str(plotRaster['overlay']) + ".")

                    if 'graphType' in plotRaster and plotRaster['graphType'] not in ['line','bar']:
                        errorMessages.append("SimConfig->'analysis'->'plotRaster'->'graphType': GraphType must be in " + str(['line','bar']) + ". Value provided is " + str(plotRaster['graphType']) + ".")

                    if 'yaxis' in plotRaster and plotRaster['yaxis'] not in ['rate','count']:
                        errorMessages.append("SimConfig->'analysis'->'plotRaster'->'yaxis': yaxis must be in " + str(['rate','count']) + ". Value provided is " + str(plotRaster['yaxis']) + ".")

                    if 'figSize' in plotRaster and not isinstance (plotRaster['figSize'], tuple):
                        errorMessages.append("SimConfig->'analysis'->'plotRaster'->'figSize': figSize must be tuple if specified. Value provided is " + str(plotRaster['figSize']) + ".")

                    if 'binSize' in plotRaster and not isinstance( plotRaster['binSize'], int):
                        errorMessages.append("SimConfig->'analysis'->'plotRaster'->'binSize': Must be an integer. Value provided is " + str(plotRaster['binSize']) + ".")

                    if 'showFig' in plotRaster:

                        if not isinstance( plotRaster['showFig'], bool):
                            errorMessages.append("SimConfig->'analysis'->'plotRaster'->'showFig': Must be boolean. Value provided is " + str(plotRaster['showFig']) + ".")

                if 'plotSpikePSD' in analysis:

                    plotSpikePSD = analysis['plotSpikePSD']
                    if not isinstance ( plotSpikePSD, dict) and  not isinstance ( plotSpikePSD, bool):
                        errorMessages.append("SimConfig->'analysis'->'plotSpikePSD': Must be a dict.  Value provided is " + str(plotSpikePSD) + ".")

                    else:

                        validList = ['include', 'timeRange', 'binSize', 'Fs', 'spikeHist', 'overlay', 'yaxis', 'figSize', 'saveData', 'saveFig' , 'showFig']

                        if not all(x in validList for x in plotSpikePSD.keys()):
                            errorMessages.append("SimConfig->'analysis'->'plotSpikePSD': plotSpikePSD must be a dict with keys in list " + str(validList) + ". Keys supplied are " + str(plotSpikePSD.keys()) + ".")

                        if 'include' in plotSpikePSD and not isinstance( plotSpikePSD['include'], list):
                            errorMessages.append("SimConfig->'analysis'->'plotSpikePSD'->'include': Must be a list. Value provided is " + str(plotSpikePSD['include']) + ".")

                        # if 'timeRange' in plotRaster and not isinstance( plotRaster['timeRange'], dict):
                        #     errorMessages.append("SimConfig->'analysis'->'plotRaster'->'timeRange': Must be a list. Value provided is " + str(plotRaster['timeRange']) + ".")

                        if 'overlay' in plotSpikePSD:

                            if not isinstance( plotSpikePSD['overlay'], bool):
                                errorMessages.append("SimConfig->'analysis'->'plotSpikePSD'->'overlay': Must be boolean. Value provided is " + str(plotSpikePSD['overlay']) + ".")

                        if 'Fs' in plotSpikePSD and not isinstance ( plotSpikePSD['Fs'] , numbers.Real ):
                            errorMessages.append("SimConfig->'analysis'->'plotSpikePSD'->'Fs': Fs must be float. Value provided is " + str(plotSpikePSD['Fs']) + ".")

                        if 'figSize' in plotSpikePSD and not isinstance (plotSpikePSD['figSize'], tuple):
                            errorMessages.append("SimConfig->'analysis'->'plotSpikePSD'->'figSize': figSize must be tuple if specified. Value provided is " + str(plotSpikePSD['figSize']) + ".")

                        if 'binSize' in plotSpikePSD and not isinstance( plotSpikePSD['binSize'], int):
                            errorMessages.append("SimConfig->'analysis'->'plotSpikePSD'->'binSize': Must be an integer. Value provided is " + str(plotSpikePSD['binSize']) + ".")

                        if 'showFig' in plotSpikePSD:

                            if not isinstance( plotSpikePSD['showFig'], bool):
                                errorMessages.append("SimConfig->'analysis'->'plotSpikePSD'->'showFig': Must be boolean. Value provided is " + str(plotSpikePSD['showFig']) + ".")

                if 'plotTraces' in analysis:

                    plotTraces = analysis['plotTraces']
                    if not isinstance ( plotTraces, dict) and  not isinstance ( plotTraces, bool):
                        errorMessages.append("SimConfig->'analysis'->'plotTraces': Must be a dict.  Value provided is " + str(plotTraces) + ".")

                    else:

                        validList = ['include', 'timeRange','overlay', 'oneFigPer', 'rerun', 'figSize', 'saveData' , 'showFig']

                        if not all(x in validList for x in plotTraces.keys()):
                            errorMessages.append("SimConfig->'analysis'->'plotTraces': plotTraces must be a dict with keys in list " + str(validList) + ". Keys supplied are " + str(plotTraces.keys()) + ".")

                        if 'include' in plotTraces and not isinstance( plotTraces['include'], list):
                            errorMessages.append("SimConfig->'analysis'->'plotTraces'->'include': Must be a list. Value provided is " + str(plotTraces['include']) + ".")

                        # if 'timeRange' in plotRaster and not isinstance( plotRaster['timeRange'], dict):
                        #     errorMessages.append("SimConfig->'analysis'->'plotRaster'->'timeRange': Must be a list. Value provided is " + str(plotRaster['timeRange']) + ".")

                        if 'overlay' in plotTraces and not isinstance( plotTraces['overlay'], bool):
                                errorMessages.append("SimConfig->'analysis'->'plotTraces'->'overlay': Must be boolean. Value provided is " + str(plotTraces['overlay']) + ".")

                        if 'binSize' in plotTraces and not isinstance( plotTraces['binSize'], int):
                            errorMessages.append("SimConfig->'analysis'->'plotTraces'->'binSize': Must be an integer. Value provided is " + str(plotTraces['binSize']) + ".")

                        if 'oneFigPer' in plotTraces and plotTraces['oneFigPer'] not in ['cell','trace']:
                            errorMessages.append("SimConfig->'analysis'->'plotTraces'->'oneFigPer': oneFigPer must be in " + str(['rate','count']) + ". Value provided is " + str(plotTraces['oneFigPer']) + ".")

                        if 'rerun' in plotTraces and not isinstance( plotTraces['rerun'], bool):
                                errorMessages.append("SimConfig->'analysis'->'plotTraces'->'rerun': Must be boolean. Value provided is " + str(plotTraces['rerun']) + ".")

                        if 'figSize' in plotTraces and not isinstance (plotTraces['figSize'], tuple):
                            errorMessages.append("SimConfig->'analysis'->'plotTraces'->'figSize': figSize must be tuple if specified. Value provided is " + str(plotTraces['figSize']) + ".")

                        if 'saveFig' in plotTraces and not isinstance (plotTraces['saveFig'], tuple):
                            errorMessages.append("SimConfig->'analysis'->'plotTraces'->'saveFig': saveFig must be tuple if specified. Value provided is " + str(plotTraces['saveFig']) + ".")

                if 'plotShape' in analysis:

                    plotShapes = analysis['plotShapes']
                    if not isinstance ( plotShapes, dict) and  not isinstance ( plotShapes, bool):
                        errorMessages.append("SimConfig->'analysis'->'plotShapes': Must be a dict.  Value provided is " + str(plotShapes) + ".")
                    else:

                        validList = ['showSyns', 'include', 'style', 'siz', 'figSize', 'saveData', 'saveFig', 'showFig']

                        if not all(x in validList for x in plotShape.keys()):
                            errorMessages.append("SimConfig->'analysis'->'plotShape': plotShape must be a dict with keys in list " + str(validList) + ". Keys supplied are " + str(plotShape.keys()) + ".")

                        if 'showSyns' in plotShapes and not isinstance( plotShapes['showSyns'], bool):
                                errorMessages.append("SimConfig->'analysis'->'plotShapes'->'showSyns': Must be boolean. Value provided is " + str(plotShapes['showSyns']) + ".")

                        if 'showFig' in plotShapes and not isinstance( plotShapes['showFig'], bool):
                                errorMessages.append("SimConfig->'analysis'->'plotShapes'->'showFig': Must be boolean. Value provided is " + str(plotShapes['showFig']) + ".")

                if 'plotConn' in analysis:

                    plotConn = analysis['plotConn']

                    if not isinstance ( plotConn, dict) and  not isinstance ( plotConn, bool):
                        errorMessages.append("SimConfig->'analysis'->'plotConn': Must be a dict.  Value provided is " + str(plotConn) + ".")

                    else:

                        validList = ['include', 'feature', 'orderBy', 'figSize', 'groupBy', 'saveData', 'saveFig', 'showFig']

                        if not all(x in validList for x in plotConn.keys()):
                            errorMessages.append("SimConfig->'analysis'->'plotConn': plotConn must be a dict with keys in list " + str(validList) + ". Keys supplied are " + str(plotConn.keys()) + ".")

                        if 'include' in plotConn and not isinstance( plotConn['include'], list):
                            errorMessages.append("SimConfig->'analysis'->'plotConn'->'include': Must be a list. Value provided is " + str(plotConn['include']) + ".")

                        if 'feature' in plotConn:
                            if plotConn['spikeHist'] not in ['weight', 'delay', 'numConns']:
                                errorMessages.append("SimConfig->'analysis'->'plotConn'->'feature': Valid values are " + str(['weight', 'delay', 'numConns'])+ ". Value provided is " + str(plotConn['feature']) + ".")

                        if 'groupBy' in plotConn:
                            if plotConn['spikeHist'] not in ['pop', 'cell']:
                                errorMessages.append("SimConfig->'analysis'->'plotConn'->'groupBy': Valid values are " + str(['pop', 'cell'])+ ". Value provided is " + str(plotConn['groupBy']) + ".")

                        if 'orderBy' in plotConn:
                            if plotConn['spikeHist'] not in ['gid', 'ynorm', 'y']:
                                errorMessages.append("SimConfig->'analysis'->'plotConn'->'orderBy': Valid values are " + str(['gid', 'ynorm','y'])+ ". Value provided is " + str(plotConn['orderBy']) + ".")

                        if 'showFig' in plotConn and not isinstance( plotConn['showFig'], bool):
                                errorMessages.append("SimConfig->'analysis'->'plotConn'->'showFig': Must be boolean. Value provided is " + str(plotConn['showFig']) + ".")

                if 'plot2DNet' in analysis:

                    plot2DNet = analysis['plot2DNet']

                    if not isinstance ( plot2DNet, dict) and not isinstance ( plot2DNet, bool):
                        errorMessages.append("SimConfig->'analysis'->'plot2DNet': Must be a dict.  Value provided is " + str(plot2DNet) + ".")
                    else:

                        validList = ['include', 'feature', 'orderBy', 'figSize', 'groupBy', 'saveData', 'saveFig', 'showFig']

                        if not all(x in validList for x in plot2DNet.keys()):
                            errorMessages.append("SimConfig->'analysis'->'plot2DNet': plot2DNet must be a dict with keys in list " + str(validList) + ". Keys supplied are " + str(plot2DNet.keys()) + ".")

                        if 'include' in plot2DNet and not isinstance( plot2DNet['include'], list):
                            errorMessages.append("SimConfig->'analysis'->'plot2DNet'->'include': Must be a list. Value provided is " + str(plot2DNet['include']) + ".")

                        if 'orderBy' in plot2DNet:
                            if plot2DNet['spikeHist'] not in ['gid', 'ynorm', 'y']:
                                errorMessages.append("SimConfig->'analysis'->'plot2DNet'->'orderBy': Valid values are " + str(['gid', 'ynorm','y'])+ ". Value provided is " + str(plot2DNet['orderBy']) + ".")

                        if 'view' in plot2DNet:
                            if plot2DNet['spikeHist'] not in ['xy', 'xz']:
                                errorMessages.append("SimConfig->'analysis'->'plot2DNet'->'view': Valid values are " + str(['xy', 'xz'])+ ". Value provided is " + str(plot2DNet['view']) + ".")

                        if 'showConns' in plot2DNet and not isinstance( plot2DNet['showConns'], bool):
                                errorMessages.append("SimConfig->'analysis'->'plot2DNet'->'showConns': Must be boolean. Value provided is " + str(plot2DNet['showConns']) + ".")

                        if 'showFig' in plot2DNet and not isinstance( plot2DNet['showFig'], bool):
                                errorMessages.append("SimConfig->'analysis'->'plot2DNet'->'showFig': Must be boolean. Value provided is " + str(plot2DNet['showFig']) + ".")

                if 'nTE' in analysis:

                    nTE = analysis['nTE']

                    if not isinstance ( nTE, dict) and not isinstance ( nTE, bool):
                        errorMessages.append("SimConfig->'analysis'->'nTE': Must be a dict.  Value provided is " + str(nTE) + ".")
                    else:
                        validList = ['cells1', 'cells2', 'spks1', 'spks2', 'timeRange', 'binSize', 'numShuffle']

                        if not all(x in validList for x in nTE.keys()):
                            errorMessages.append("SimConfig->'analysis'->'nTE': nTE must be a dict with keys in list " + str(validList) + ". Keys supplied are " + str(nTE.keys()) + ".")

                        if 'cells1' in nTE and not isinstance( nTE['cells1'], list):
                            errorMessages.append("SimConfig->'analysis'->'nTE'->'cells1': Must be a list. Value provided is " + str(nTE['cells1']) + ".")

                        if 'cells2' in nTE and not isinstance( nTE['cells2'], list):
                            errorMessages.append("SimConfig->'analysis'->'nTE'->'cells2': Must be a list. Value provided is " + str(nTE['cells2']) + ".")

                        if 'spks1' in nTE and not isinstance( nTE['spks1'], list):
                            errorMessages.append("SimConfig->'analysis'->'nTE'->'spks1': Must be a list. Value provided is " + str(nTE['spks1']) + ".")

                        if 'spks2' in nTE and not isinstance( nTE['spks2'], list):
                            errorMessages.append("SimConfig->'analysis'->'nTE'->'spks2': Must be a list. Value provided is " + str(nTE['spks2']) + ".")

                        if 'binSize' in nTE and not isinstance( nTE['binSize'], int):
                            errorMessages.append("SimConfig->'analysis'->'nTE'->'binSize': Must be an int. Value provided is " + str(nTE['binSize']) + ".")

                        if 'numShuffle' in nTE and not isinstance( nTE['numShuffle'], int):
                            errorMessages.append("SimConfig->'analysis'->'nTE'->'numShuffle': Must be an int. Value provided is " + str(nTE['numShuffle']) + ".")

                if 'granger' in analysis:

                    granger = analysis['granger']

                    if not isinstance ( granger, dict) and not isinstance ( granger, bool):
                        errorMessages.append("SimConfig->'analysis'->'granger': Must be a dict.  Value provided is " + str(granger) + ".")
                    else:

                        validList = ['cells1', 'cells2', 'spks1', 'spks2','label1', 'label2', 'timeRange', 'binSize', 'plotFig', 'saveData', 'saveFig', 'showFig']

                        if not all(x in validList for x in granger.keys()):
                            errorMessages.append("SimConfig->'analysis'->'granger': granger must be a dict with keys in list " + str(validList) + ". Keys supplied are " + str(granger.keys()) + ".")

                        if 'cells1' in granger and not isinstance( granger['cells1'], list):
                            errorMessages.append("SimConfig->'analysis'->'granger'->'cells1': Must be a list. Value provided is " + str(granger['cells1']) + ".")

                        if 'cells2' in granger and not isinstance( granger['cells2'], list):
                            errorMessages.append("SimConfig->'analysis'->'granger'->'cells2': Must be a list. Value provided is " + str(granger['cells2']) + ".")

                        if 'spks1' in granger and not isinstance( granger['spks1'], list):
                            errorMessages.append("SimConfig->'analysis'->'granger'->'spks1': Must be a list. Value provided is " + str(granger['spks1']) + ".")

                        if 'spks2' in granger and not isinstance( granger['spks2'], list):
                            errorMessages.append("SimConfig->'analysis'->'granger'->'spks2': Must be a list. Value provided is " + str(granger['spks2']) + ".")

                        if 'binSize' in granger and not isinstance( granger['binSize'], int):
                            errorMessages.append("SimConfig->'analysis'->'granger'->'binSize': Must be an int. Value provided is " + str(granger['binSize']) + ".")

                        if 'plotFig' in plot2DNet and not isinstance( plot2DNet['plotFig'], bool):
                                errorMessages.append("SimConfig->'analysis'->'plot2DNet'->'plotFig': Must be boolean. Value provided is " + str(plot2DNet['plotFig']) + ".")

                        if 'showFig' in plot2DNet and not isinstance( plot2DNet['showFig'], bool):
                                errorMessages.append("SimConfig->'analysis'->'plot2DNet'->'showFig': Must be boolean. Value provided is " + str(plot2DNet['showFig']) + ".")

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

class SimTestObj(object):

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
        self.loadSimConfigTests() # load simConfig tests
        if self.verboseFlag:
            print (" *** Finish loading tests *** ")

    def runTests(self):

        if self.verboseFlag:
            print (" *** Running tests *** ")
        self.runPopTests() # run pop tests
        self.runNetTests() # run net tests
        self.runCellTests() # run cell tests
        self.runConnTests() # run conn tests
        self.runStimSourceTests() # load stimSource tests
        self.runStimTargetTests() # load stimTarget tests
        self.runSimConfigTests() # load simConfig tests

        if self.verboseFlag:
            print (" *** Finished running tests *** ")

    def loadSimConfigTests(self):

        # if self.verboseFlag:
        #     print (" *** Loading pop tests *** ")

        # initialiase list of test objs
        self.testParamsMap["simConfig"] = {}

        ## duration test
        ## duration - Duration of the simulation, in ms (default: 1000)

        testObj = TestObj()
        testObj.testName = "durationTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.duration"
        testObj.testTypes = [TEST_TYPE_IS_FLOAT]
        testObj.messageText = ["SimConfig->'duration': Value should be a float."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["durationTest"] = testObj

        ## dt test
        ## dt - Internal integration timestep to use (default: 0.025)

        testObj = TestObj()
        testObj.testName = "dtTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.dt"
        testObj.testTypes = [TEST_TYPE_IS_FLOAT]
        testObj.messageText = ["simConfig->'dt': Value should be a float."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["dtTest"] = testObj

        # hParams test

        testObj = TestObj()
        testObj.testName = "hParamsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.hParams"
        testObj.testTypes = [TEST_TYPE_IS_DICT, TEST_TYPE_DICT_KEY_VALID_VALUE ]
        testObj.testValueList = "h.__dict__.keys()"
        testObj.messageText = ["simConfig->'hParams':hParams is not a dict.", "simConfig->'hParams':"   ]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["hParamsTest"] = testObj

        ## cache_efficient test
        ## cache_efficient - Use CVode cache_efficient option to optimize load when running on many cores (default: False)

        testObj = TestObj()
        testObj.testName = "cacheEfficientTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.cache_efficient"
        testObj.testTypes = [TEST_TYPE_IS_BOOL]
        testObj.messageText = ["simConfig->'cacheEfficient':cacheEfficient is not a boolean."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["cacheEfficientTest"] = testObj

        ## cvode_active test
        ## cvode_active - Use CVode variable time step (default: False)

        testObj = TestObj()
        testObj.testName = "cvodeActiveTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.cvode_active"
        testObj.testTypes = [TEST_TYPE_IS_BOOL]
        testObj.messageText = ["simConfig->'cvodeActive':cvodeActive is not a boolean."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["cvodeActiveTest"] = testObj
        #
        ## seeds test

        testObj = TestObj()
        testObj.testName = "seedsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.seeds"
        testObj.testTypes = [TEST_TYPE_IS_DICT,TEST_TYPE_DICT_KEY_VALID_VALUE ]
        testObj.testValueList = ['conn', 'stim', 'loc']
        testObj.messageText = ["simConfig->'seeds':seeds is not a dict.","SimConfig->'seeds':"]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["seedsTest"] = testObj

        ## createNEURONObj test

        testObj = TestObj()
        testObj.testName = "createNEURONObjTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.createNEURONObj"
        testObj.testTypes = [TEST_TYPE_IS_BOOL]
        testObj.messageText = ["simConfig->'createNEURONObj':createNEURONObj is not a boolean."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["createNEURONObjTest"] = testObj

        ## createPyStruct test

        testObj = TestObj()
        testObj.testName = "createPyStructTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.createPyStruct"
        testObj.testTypes = [TEST_TYPE_IS_BOOL]
        testObj.messageText = ["simConfig->'createPyStruct':createPyStruct is not a boolean."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["createPyStructTest"] = testObj

        ## gatherOnlySimData test

        testObj = TestObj()
        testObj.testName = "gatherOnlySimDataTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.gatherOnlySimData"
        testObj.testTypes = [TEST_TYPE_IS_BOOL]
        testObj.messageText = ["simConfig->'gatherOnlySimData':gatherOnlySimData is not a boolean."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["gatherOnlySimDataTest"] = testObj

        ## printRunTime test
        ## printRunTime - Print run time at interval (in sec) specified here (eg. 0.1) (default: False)

        testObj = TestObj()
        testObj.testName = "printRunTimeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.printRunTime"
        testObj.testTypes = [TEST_TYPE_IS_BOOL]
        testObj.messageText = ["simConfig->'printRunTime':printRunTime is not a boolean."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["printRunTimeTest"] = testObj

        ## printPopAvgRates test

        testObj = TestObj()
        testObj.testName = "printPopAvgRatesTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.printPopAvgRates"
        testObj.testTypes = [TEST_TYPE_IS_BOOL]
        testObj.messageText = ["simConfig->'printPopAvgRates':printPopAvgRates is not a boolean."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["printPopAvgRatesTest"] = testObj

        ## includeParamsLabel test

        testObj = TestObj()
        testObj.testName = "includeParamsLabelTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.includeParamsLabel"
        testObj.testTypes = [TEST_TYPE_IS_BOOL]
        testObj.messageText = ["simConfig->'includeParamsLabel':includeParamsLabel is not a boolean."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["includeParamsLabelTest"] = testObj

        ## timing test

        testObj = TestObj()
        testObj.testName = "timingTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.timing"
        testObj.testTypes = [TEST_TYPE_IS_BOOL]
        testObj.messageText = ["simConfig->'timing':timing is not a boolean."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["timingTest"] = testObj

        ## saveTiming test

        testObj = TestObj()
        testObj.testName = "saveTimingTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.saveTiming"
        testObj.testTypes = [TEST_TYPE_IS_BOOL]
        testObj.messageText = ["simConfig->'saveTiming':saveTiming is not a boolean."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["saveTimingTest"] = testObj

        ## verbose test

        testObj = TestObj()
        testObj.testName = "verboseTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.verbose"
        testObj.testTypes = [TEST_TYPE_IS_BOOL]
        testObj.messageText = ["simConfig->'verbose':verbose is not a boolean."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["verboseTest"] = testObj

        ## recordCells test

        testObj = TestObj()
        testObj.testName = "recordCellsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.recordCells"
        testObj.testTypes = [TEST_TYPE_IS_LIST]
        testObj.messageText = ["simConfig->'recordCells':recordCells is not a list."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["recordCellsTest"] = testObj

        ## recordTraces test

        testObj = TestObj()
        testObj.testName = "recordTracesTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "recordTraces"
        testObj.testTypes = [TEST_TYPE_IS_DICT,TEST_TYPE_VALUE_LIST ]
        testObj.testValueList = ['sec','loc','var']
        testObj.messageText = ["simConfig->'recordTraces':recordTraces is not a dict.","simConfig->'recordTracesTest':is not a valid value. Valid values are 'netParams', 'netCells', 'netPops', 'simConfig', 'simData'."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["recordTracesTest"] = testObj
        #
        testObj = TestObj()
        testObj.testName = "saveDataInclude"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.saveDataInclude"
        testObj.testTypes = [TEST_TYPE_IS_LIST, TEST_TYPE_ALL_VALUE_LIST]
        testObj.testValueList = ['netParams', 'netCells', 'netPops', 'simConfig', 'simData']
        testObj.messageText = ["simConfig->'saveDataInclude':saveDataInclude is not a dict.","SimConfig->'saveDataInclude':is not a valid value. Valid values are 'netParams', 'netCells', 'netPops', 'simConfig', 'simData'." ]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["recordTracesTest"] = testObj
        ## recordStim test

        testObj = TestObj()
        testObj.testName = "recordStimTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.recordStim"
        testObj.testTypes = [TEST_TYPE_IS_BOOL]
        testObj.messageText = ["SimConfig->'recordStim':recordStim is not a boolean."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["recordStimTest"] = testObj

        ## recordStep test

        testObj = TestObj()
        testObj.testName = "recordStepTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.recordStep"
        testObj.testTypes = [TEST_TYPE_IS_FLOAT]
        testObj.messageText = ["SimConfig->'recordStep': Value should be a float."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["recordStepTest"] = testObj

        ## saveDataInclude test

        testObj = TestObj()
        testObj.testName = "saveDataIncludeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.saveDataInclude"
        testObj.testTypes = [TEST_TYPE_IS_LIST]
        testObj.messageText = ["SimConfig->'saveDataInclude': Value should be a float."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["saveDataIncludeTest"] = testObj


        ## savePickle test

        testObj = TestObj()
        testObj.testName = "savePickleTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.savePickle"
        testObj.testTypes = [TEST_TYPE_IS_BOOL]
        testObj.messageText = ["SimConfig->'savePickle':savePickle is not a boolean."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["savePickleTest"] = testObj

        ## saveJson test

        testObj = TestObj()
        testObj.testName = "saveJsonTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.saveJson"
        testObj.testTypes = [TEST_TYPE_IS_BOOL]
        testObj.messageText = ["SimConfig->'saveJson':saveJson is not a boolean."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["saveJsonTest"] = testObj

        ## saveMat test

        testObj = TestObj()
        testObj.testName = "saveMatTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.saveMat"
        testObj.testTypes = [TEST_TYPE_IS_BOOL]
        testObj.messageText = ["SimConfig->'saveMat':saveMat is not a boolean."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["saveMatTest"] = testObj

        # ## saveTxt test
        # testObj = TestObj()
        # testObj.testName = "saveTxtTest"
        # testObj.testParameterType = "string"
        # testObj.testParameterValue = "self.simConfig.saveTxt"
        # testObj.testTypes = [TEST_TYPE_IS_BOOL]
        # testObj.messageText = ["SimConfig->'saveTxt':saveTxt is not a boolean."]
        # testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        #
        # self.testParamsMap["simConfig"]["saveTxtTest"] = testObj

        ## saveDpk test

        testObj = TestObj()
        testObj.testName = "saveDpkTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.saveDpk"
        testObj.testTypes = [TEST_TYPE_IS_BOOL]
        testObj.messageText = ["SimConfig->'saveDpk':saveDpk is not a boolean."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["saveDpkTest"] = testObj

        ## saveHDF5 test

        testObj = TestObj()
        testObj.testName = "saveHDF5Test"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.saveHDF5"
        testObj.testTypes = [TEST_TYPE_IS_BOOL]
        testObj.messageText = ["SimConfig->'saveHDF5':saveHDF5 is not a boolean."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["saveHDF5Test"] = testObj

        ## backupCfgFile test

        testObj = TestObj()
        testObj.testName = "backupCfgFileTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.simConfig.backupCfgFile"
        testObj.testTypes = [TEST_TYPE_IS_LIST]
        testObj.messageText = ["SimConfig->'backupCfgFile':backupCfgFile is not a list."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["simConfig"]["backupCfgFileTest"] = testObj

        ## analysisTest test

        testObj = TestObj()
        testObj.testName = "analysisTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "analysis"
        testObj.testTypes = [TEST_TYPE_VALID_ANALYSIS]

        self.testParamsMap["simConfig"]["analysisTest"] = testObj

    def loadStimSourceTests(self):

        # if self.verboseFlag:
        #     print (" *** Loading pop tests *** ")

        # initialiase list of test objs
        self.testParamsMap["stimSource"] = {}

        ##cellModel test
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

        ##cellModel test
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

        ##cellModel test
        testObj = TestObj()
        testObj.testName = "cellModelTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "cellModel"
        testObj.testTypes = [TEST_TYPE_EXISTS]
        testObj.messageText = ["popParams->'cellModel': No cellModel specified in population parameters."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["cellModelTest"] = testObj

        ##volume params test
        testObj = TestObj()
        testObj.testName = "volumeParamsTest"
        testObj.testParameterType = "list"
        testObj.testParameterValueList = ['density','numCells','gridSpacing']
        testObj.testTypes = [TEST_TYPE_EXISTS_IN_LIST]
        testObj.messageText = ["popParams: One of the following must be specified in parameters: " + str(testObj.testParameterValueList)]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["volumeParamsTest"] = testObj

        # xnormrange test
        testObj = TestObj()
        testObj.testName = "xNormRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "xnormRange"
        testObj.testTypes = [TEST_TYPE_IS_VALID_RANGE, TEST_TYPE_IN_RANGE]
        testObj.testValueRange = "[0,1]"
        testObj.messageText = ["popParams->'xnormRange': XNormRange invalid range.","popParams->'xnormRange': XNormRange not in range."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["xNormRangeTest"] = testObj

        # ynormrange test
        testObj = TestObj()
        testObj.testName = "yNormRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "ynormRange"
        testObj.testTypes = [TEST_TYPE_IS_VALID_RANGE, TEST_TYPE_IN_RANGE]
        testObj.testValueRange = "[0,1]"
        testObj.messageText = ["popParams->'ynormRange': YNormRange invalid.","popParams->'ynormRange': YNormRange not in range."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["yNormRangeTest"] = testObj

        # znormrange test
        testObj = TestObj()
        testObj.testName = "zNormRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "znormRange"
        testObj.testTypes = [TEST_TYPE_IS_VALID_RANGE, TEST_TYPE_IN_RANGE]
        testObj.testValueRange = "[0,1]"
        testObj.messageText = ["popParams->'znormRange': ZNormRange invalid.","popParams->'znormRange': ZNormRange not in range."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["zNormRangeTest"] = testObj

        # xrange test
        testObj = TestObj()
        testObj.testName = "xRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "xRange"
        testObj.testTypes = [TEST_TYPE_IS_VALID_RANGE, TEST_TYPE_IN_RANGE]
        testObj.testValueRange = "[0,self.netParams.sizeX]"
        testObj.messageText = ["popParams->'xRange': xRange invalid.","popParams->'xRange': xRange not in range."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, TEST_TYPE_IN_RANGE]

        self.testParamsMap["pop"]["xRangeTest"] = testObj

        # yrange test
        testObj = TestObj()
        testObj.testName = "yRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "yRange"
        testObj.testTypes = [TEST_TYPE_IS_VALID_RANGE, TEST_TYPE_IN_RANGE]
        testObj.testValueRange = "[0,self.netParams.sizeY]"
        testObj.messageText = ["popParams->'yRange': yRange invalid.","popParams->'yRange': yRange not in range."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["yRangeTest"] = testObj

        # zrange test
        testObj = TestObj()
        testObj.testName = "zRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "zRange"
        testObj.testTypes = [TEST_TYPE_IS_VALID_RANGE, TEST_TYPE_IN_RANGE]
        testObj.testValueRange = "[0,self.netParams.sizeX]"
        testObj.messageText = ["popParams->'zRange': zRange invalid.","popParams->'zRange': zRange not in range."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["zRangeTest"] = testObj

        # stim test
        testObj = TestObj()
        testObj.testName = "stimTest"
        testObj.testParameterType = "string"
        testObj.testTypes = [TEST_TYPE_VALID_STIM]

        self.testParamsMap["pop"]["stimTest"] = testObj

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
        testObj.testTypes = [TEST_TYPE_IS_FLOAT, TEST_TYPE_GT_ZERO]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]
        testObj.messageText = ["NetParams->'sizeX': Value should be a float.","NetParams->'sizeX': sizeX is not greater than 0."]

        self.testParamsMap["net"]["sizeXTest"] = testObj

        # sizeY test
        testObj = TestObj()
        testObj.testName = "sizeYTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.netParams.sizeY"
        testObj.testTypes = [TEST_TYPE_IS_FLOAT, TEST_TYPE_GT_ZERO]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]
        testObj.messageText = ["NetParams->'sizeY': Value should be a float.","NetParams->'sizeY': sizeY is not greater than 0."]

        self.testParamsMap["net"]["sizeYTest"] = testObj

        # sizeZ test
        testObj = TestObj()
        testObj.testName = "sizeZTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.netParams.sizeZ"
        testObj.testTypes = [TEST_TYPE_IS_FLOAT, TEST_TYPE_GT_ZERO]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]
        testObj.messageText = ["NetParams->'sizeZ': Value should be a float.","NetParams->'sizeZ': sizeZ is not greater than 0."]

        self.testParamsMap["net"]["sizeZTest"] = testObj

        # shape test
        testObj = TestObj()
        testObj.testName = "shapeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "self.netParams.shape"
        testObj.testTypes = [TEST_TYPE_VALUE_LIST]
        testObj.testValueList = VALID_SHAPES
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        testObj.messageText = ["NetParams->'shape': Shape is not valid."]

        self.testParamsMap["net"]["shapeTest"] = testObj

        # if self.verboseFlag:
        #     print (" *** Finished loading net tests *** ")

    def loadCellTests(self):

        # if self.verboseFlag:
        #     print (" *** Loading cell tests *** ")

        self.testParamsMap["cell"] = {}

        # condsTest test
        testObj = TestObj()
        testObj.testName = "condsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "conds"
        testObj.testTypes = [TEST_TYPE_EXISTS, TEST_TYPE_IS_DICT]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]
        testObj.messageText = ["cellParams->'conds': Conds does not exist.", "cellParams->'conds': Conds is not a dict."]
        self.testParamsMap["cell"]["condsTest"] = testObj

        # secs test
        testObj = TestObj()
        testObj.testName = "secsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "secs"
        testObj.testTypes = [TEST_TYPE_IS_DICT]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        testObj.messageText = ["cellParams->'secs': Secs is not a dict."]
        self.testParamsMap["cell"]["secsTest"] = testObj

        # cellTypes test
        testObj = TestObj()
        testObj.testName = "cellTypesTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "conds"
        testObj.testParameterValue1 = "cellType"
        testObj.testTypes = [TEST_TYPE_EXISTS_IN_DICT]
        testObj.compareDict = "self.netParams.popParams"
        testObj.messageText = ["cellParams->'cellType': cellType does not match the cellType specified in pop parameters."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_WARNING]

        self.testParamsMap["cell"]["cellTypeTest"] = testObj

        # cellModel test
        testObj = TestObj()
        testObj.testName = "cellModelTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "conds"
        testObj.testParameterValue1 = "cellModel"
        testObj.testTypes = [TEST_TYPE_EXISTS_IN_DICT]
        testObj.compareDict = "self.netParams.popParams"
        testObj.messageText = ["cellParams->'cellModel': cellModel does not match the cellModel specified in pop parameters."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_WARNING]

        self.testParamsMap["cell"]["cellModelTest"] = testObj

        #geom test
        testObj = TestObj()
        testObj.testName = "geomExistTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "secs"
        testObj.testParameterDictString = "geom"
        testObj.testTypes = [TEST_TYPE_EXISTS_IN_ALL_DICTS]
        testObj.messageText = ["cellParams->'secs'->'geom': Geom is not specified in section "]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        self.testParamsMap["cell"]["geomExistTest"] = testObj

        # geom test
        testObj = TestObj()
        testObj.testName = "geomValidTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "geom"
        testObj.testTypes = [TEST_TYPE_VALID_GEOMETRIES]
        #testObj.testValueList = VALID_GEOMETRIES,
        testObj.messageText = ["cellParams->'secs'->'geom': Geom is not valid."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["cell"]["geomValidTest"] = testObj

        # topol test
        testObj = TestObj()
        testObj.testName = "topologyTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "topol"
        testObj.testTypes = [TEST_TYPE_VALID_TOPOLOGIES]
        testObj.messageText = ["cellParams->'secs'->'topol':Topology is not valid."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["cell"]["toplogyValidTest"] = testObj

        # mechs test
        testObj = TestObj()
        testObj.testName = "mechsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "mechs"
        testObj.testTypes = [TEST_TYPE_VALID_MECHS]
        testObj.messageText = ["Mechs are not valid."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["cell"]["mechsValidTest"] = testObj

        # pointps test
        testObj = TestObj()
        testObj.testName = "pointpsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "pointps"
        testObj.testTypes = [TEST_TYPE_VALID_POINTPS]
        testObj.messageText = ["Pointps are not valid."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["cell"]["pointpsValidTest"] = testObj

        # secList test
        testObj = TestObj()
        testObj.testName = "secListTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "secList"
        testObj.testTypes = [TEST_TYPE_VALID_SEC_LIST]
        testObj.messageText = ["SecList is not valid."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["cell"]["secListTest"] = testObj

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

        # pop Labels test
        testObj = TestObj()
        testObj.testName = "popLabelsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "preConds"
        testObj.testTypes = [TEST_TYPE_EXISTS_IN_POP_LABELS]
        testObj.messageText = ["ConnParams->'popLabel': Pop label specified for preConds not listed in pop parameters."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_WARNING]
        self.testParamsMap["conn"]["preCondsPopLabelsTest"] = testObj

        # pop Labels test
        testObj = TestObj()
        testObj.testName = "popLabelsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "postConds"
        testObj.testTypes = [TEST_TYPE_EXISTS_IN_POP_LABELS]
        testObj.messageText = ["ConnParams->'popLabel': Pop label specified for postConds not listed in pop parameters."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_WARNING]
        self.testParamsMap["conn"]["postCondsPopLabelsTest"] = testObj

        # condsTest test
        testObj = TestObj()
        testObj.testName = "preCondsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "preConds"
        testObj.testTypes = [TEST_TYPE_EXISTS, TEST_TYPE_IS_DICT]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]
        testObj.messageText = ["ConnParams->'preConds': Preconds does not exist.", "ConnParams->'preConds': Preconds is not a dict."]
        self.testParamsMap["conn"]["preCondsTest"] = testObj

        # condsTest test
        testObj = TestObj()
        testObj.testName = "postCondsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "postConds"
        testObj.testTypes = [TEST_TYPE_EXISTS, TEST_TYPE_IS_DICT]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]
        testObj.messageText = ["ConnParams->'postConds': Postconds does not exist.", "ConnParams->'postConds': Postconds is not a dict."]
        self.testParamsMap["conn"]["postCondsTest"] = testObj

        # secs test
        testObj = TestObj()
        testObj.testName = "connsSecsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "secs"
        testObj.testTypes = [TEST_TYPE_EXISTS, TEST_TYPE_IS_DICT ]
        testObj.messageText = ["ConnParams->'secs': Secs, is specified, needs to be a dict.", "ConnParams->'secs': Secs is not specified. Will use 'soma' by default otherwise first available section."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_WARNING", "MESSAGE_TYPE_ERROR"]

        self.testParamsMap["conn"]["connsSecsTest"] = testObj

        #locs test
        testObj = TestObj()
        testObj.testName = "connLocsRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "loc"
        testObj.testTypes = [TEST_TYPE_ARRAY_IN_RANGE]
        testObj.testValueRange = "[0,1]"
        testObj.messageText = ["ConnParams->'loc': Loc is not in range."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["conn"]["locsRangeTest"] = testObj

        # weights synMechs test
        testObj = TestObj()
        testObj.testName = "connWeightSynMechTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "weight"
        testObj.testTypes = [TEST_TYPE_VALID_SYN_MECHS]
        testObj.messageText = ["Syn Mechs are invalid."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        self.testParamsMap["conn"]["weightsMechsTest"] = testObj

        # delay synMechs test
        testObj = TestObj()
        testObj.testName = "connDelaySynMechTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "delay"
        testObj.testTypes = [TEST_TYPE_VALID_SYN_MECHS]
        testObj.messageText = ["Syn Mechs are invalid."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["conn"]["delayMechsTest"] = testObj

        # secs test
        testObj = TestObj()
        testObj.testName = "connsSecsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "secs"
        testObj.testTypes = [ TEST_TYPE_IS_DICT, TEST_TYPE_VALID_SEC_LIST ]
        testObj.messageText = ["ConnParams->'secs': Secs is not specified. Will use 'soma' by default otherwise first available section.", "ConnParams->'secs': Invalid sec."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_WARNING,MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["conn"]["connsSecsTest"] = testObj

        # secs test
        testObj = TestObj()
        testObj.testName = "connsSecsListTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "secs"
        testObj.testTypes = [TEST_TYPE_VALID_SEC_LIST ]
        testObj.messageText = ["If synsPerConn > 1, a list of sections or sectionList can be specified. These secs need to be specified in the cell parameters."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["conn"]["connsSecsListTest"] = testObj

        # conn list test
        testObj = TestObj()
        testObj.testName = "connsListTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "secs"
        testObj.testTypes = [TEST_TYPE_VALID_CONN_LIST ]
        testObj.messageText = ["If synsPerConn > 1, a list of sections or sectionList can be specified. These secs need to be specified in the cell parameters."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["conn"]["connsListTest"] = testObj

        # conn list test
        testObj = TestObj()
        testObj.testName = "hierarchyTest"
        testObj.testParameterType = "string"
        #testObj.testParameterValue = "secs"
        testObj.testTypes = [TEST_TYPE_CONN_PARM_HIERARCHY ]
        #testObj.messageText = ["If synsPerConn > 1, a list of sections or sectionList can be specified. These secs need to be specified in the cell parameters."]
        #testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["conn"]["connHierarchyTest"] = testObj

        # conn list test
        testObj = TestObj()
        testObj.testName = "shapeTest"
        testObj.testParameterType = "string"
        #testObj.testParameterValue = "secs"
        testObj.testTypes = [TEST_TYPE_CONN_SHAPE ]
        #testObj.messageText = ["If synsPerConn > 1, a list of sections or sectionList can be specified. These secs need to be specified in the cell parameters."]
        #testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        #
        self.testParamsMap["conn"]["connShapeTest"] = testObj

        # conn plasticity test
        testObj = TestObj()
        testObj.testName = "shapeTest"
        testObj.testParameterType = "string"
        #testObj.testParameterValue = "secs"
        testObj.testTypes = [TEST_TYPE_CONN_PLASTICITY ]
        #testObj.messageText = ["If synsPerConn > 1, a list of sections or sectionList can be specified. These secs need to be specified in the cell parameters."]
        #testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]
        #
        self.testParamsMap["conn"]["connPlasticityTest"] = testObj

        if self.verboseFlag:
            print (" *** Finished loading conn tests *** ")

    def runPopTests(self):

        # if self.verboseFlag:
        #     print ( "::: flag is " + str(self.verboseFlag))

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
        for testName, stimSourceTestObj in self.testParamsMap["stimSource"].items():
            self.execRunTests(stimSourceTestObj, stimSourceParams)

    def runStimTargetTests(self):

        # if self.verboseFlag:
        #     print (" *** Running stim target tests *** ")

        stimTargetParams = self.netParams.stimTargetParams
        for testName, stimTargetTestObj in self.testParamsMap["stimTarget"].items():
            self.execRunTests(stimTargetTestObj, stimTargetParams)

    def runSimConfigTests(self):

        # if self.verboseFlag:
        #     print (" *** Running stim target tests *** ")

        simConfigParams = self.simConfig
        for testName, simConfigTestObj in self.testParamsMap["simConfig"].items():
            self.execRunTests(simConfigTestObj, simConfigParams)

    def execRunTests(self, testObj, params):

        # print ( " !!!!!!!! for test " + str(testObj.testTypes))

        for testIndex, testType in enumerate(testObj.testTypes):

            #print ( " !!!!!!!! for test " + str(testType))

            if testType == TEST_TYPE_EXISTS:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            self.testTypeObj.testExists (testObj.testParameterValue,  paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex] + ".Values provided are: " + str(paramValues) )
                else:

                        try:
                            self.testTypeObj.testExists (testObj.testParameterValue,  paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(testObj.testParameterValue))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(testObj.testParameterValue))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex] + ".Values provided are: " + str(paramValues))

            elif testType == TEST_TYPE_EXISTS_IN_LIST:

                if isinstance(params, dict):
                    for paramLabel, paramValues in params.items():

                        try:
                            self.testTypeObj.testExistsInList (testObj.testParameterValueList,  paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex] + ".Values provided are: " + str(paramValues))

                else:

                        try:
                            self.testTypeObj.testExistsInList (testObj.testParameterValueList,  paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(testObj.testParameterValue))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(testObj.testParameterValue))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex] + ".Values provided are: " + str(paramValues))

            elif testType == TEST_TYPE_EXISTS_IN_DICT:

                if isinstance(params, dict):
                    for paramLabel, paramValues in params.items():

                        try:

                            if testObj.testParameterValue in paramValues and testObj.testParameterValue1 in paramValues[testObj.testParameterValue] and paramValues[testObj.testParameterValue][testObj.testParameterValue1]:
                                self.testTypeObj.testExistsInDict (  paramValues[testObj.testParameterValue][testObj.testParameterValue1],  eval(testObj.compareDict), testObj.testParameterValue1)
                                if self.verboseFlag:
                                    print ( "Test: " + str(paramValues[testObj.testParameterValue][testObj.testParameterValue1]) + " for: " + str(testType)+ " value: " + str(eval(testObj.compareDict)) )
                                    print ( "PASSED" )

                        except Exception as e:
                            #traceback.print_exc(file=sys.stdout)
                            if self.verboseFlag:
                                print ( "Test " + testObj.testParameterValue + " for: " + str(testType)+ " value: " + str(eval(testObj.compareDict)))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex] + " Value provided is '" + paramValues[testObj.testParameterValue][testObj.testParameterValue1] + "'.")

            elif testType == TEST_TYPE_IN_RANGE:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            self.testTypeObj.testInRange(testObj.testParameterValue, eval(testObj.testValueRange), paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType) + " value: " + str(paramValues))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType) + " value: " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex] + ".Values provided are: " + str(paramValues))
                else:

                        try:
                            self.testTypeObj.testInRange(testObj.testParameterValue, eval(testObj.testValueRange), paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(testObj.testParameterValue))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(testObj.testParameterValue))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex] + ".Values provided are: " + str(paramValues))

            elif testType == TEST_TYPE_ARRAY_IN_RANGE:

                    if isinstance(params, dict):

                        for paramLabel, paramValues in params.items():

                            try:
                                testParamValue = self.testTypeObj.testArrayInRange(testObj.testParameterValue, eval(testObj.testValueRange), paramValues)
                                if self.verboseFlag:
                                    print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(testObj.testParameterValue))
                                    print ( "PASSED" )

                            except Exception as e:

                                #traceback.print_exc(file=sys.stdout)
                                if self.verboseFlag:
                                    print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(testObj.testParameterValue))
                                paramValue = ''
                                if testObj.testParameterValue in paramValues:
                                    paramValue = paramValues[testObj.testParameterValue]
                                print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex] + " Value = " + str(paramValue))

            elif testType == TEST_TYPE_IS_VALID_RANGE:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            self.testTypeObj.testIsValidRange(testObj.testParameterValue, paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex] + ".Values provided are: " + str(paramValues))

                else:

                        try:
                            self.testTypeObj.testIsValidRange(testObj.testParameterValue, paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                            print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex] + ".Values provided are: " + str(paramValues))

            elif testType == TEST_TYPE_IS_INT:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            #print (" in int = " + str(paramValues))
                            self.testTypeObj.testIsInt(testObj.testParameterValue)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                                print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex] + ".Values provided are: " + str(paramValues))

                else:

                        try:
                            paramName = eval(testObj.testParameterValue)
                            #print (" in int 2 = " + str(paramName))

                            self.testTypeObj.testIsInt(paramName)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramName))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramName))
                            try:
                                print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex]) + " Value specified is " + str(paramName) + "." + ".Values provided are: " + str(paramValues)
                            except:
                                pass

            elif testType == TEST_TYPE_IS_FLOAT:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            #print (" in float = " + str(paramValues))
                            self.testTypeObj.testIsFloat(testObj.testParameterValue)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                                print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex] + ".Values provided are: " + str(paramValues))

                else:

                        try:
                            paramName = ''
                            try:
                                paramName = eval(testObj.testParameterValue)
                            except:
                                pass
                            if paramName != '':
                            #print (" in float 2 = " + str(paramName))

                                self.testTypeObj.testIsFloat(paramName)
                                if self.verboseFlag:
                                    print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramName))
                                    print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(testObj.testParameterValue) + ".")
                            try:
                                print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex]) + " Value specified is " + str(paramName) + "." + ".Values provided are: " + str(paramValues)
                            except:
                                pass

            elif testType == TEST_TYPE_GTE_ZERO:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            self.testTypeObj.testGteZero(testObj.testParameterValue, paramValues)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                            try:
                                print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex])
                            except:
                                pass

                else:
                        try:
                            paramName = ''
                            try:
                                paramName = eval(testObj.testParameterValue)
                            except:
                                pass
                            if paramName != '':
                                self.testTypeObj.testGteZero(paramName)
                                if self.verboseFlag:
                                    print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramName))
                                    print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramName))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex]) + ". Value specified is " + str(paramName) + " ."

            elif testType == TEST_TYPE_IS_DICT:
                #print (" in dict test type ")

                if isinstance(params, dict):
                    #print (" in dict test type 2 ")
                    for paramLabel, paramValues in params.items():

                        try:
                            if testObj.testParameterValue in paramValues:
                                self.testTypeObj.testIsDict(paramValues[testObj.testParameterValue])
                                if self.verboseFlag:
                                    print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                                    print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex])
                else:
                        try:
                            paramName = ''
                            try:
                                paramName = eval(testObj.testParameterValue)
                            except:
                                pass
                            self.testTypeObj.testIsDict(paramName)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramName))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(testObj.testParameterValue))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex]) + str(e[0])

            elif testType == TEST_TYPE_IS_LIST:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            if testObj.testParameterValue in paramValues:
                                self.testTypeObj.testIsList(paramValues[testObj.testParameterValue])
                                if self.verboseFlag:
                                    print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                                    print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex])

                else:
                        try:
                            paramName = ''
                            try:
                                paramName = eval(testObj.testParameterValue)
                            except:
                                # print ( " 333 " )
                                pass
                            if paramName != '':
                                # print (" ee ")
                                self.testTypeObj.testIsList(paramName)
                                if self.verboseFlag:
                                    print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramName))
                                    print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(testObj.testParameterValue))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex]) + str(" -- " + e[0])

            elif testType == TEST_TYPE_IS_BOOL:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            if testObj.testParameterValue in paramValues:
                                self.testTypeObj.testIsBoolean(paramValues[testObj.testParameterValue])
                                if self.verboseFlag:
                                    print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                                    print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex])
                else:
                        try:
                            # print (" --- " + str(testObj.testParameterValue))
                            paramName = ''
                            try:
                                paramName = eval(testObj.testParameterValue)
                            except:
                                pass
                            if paramName != '':
                                self.testTypeObj.testIsBoolean(paramName)
                                if self.verboseFlag:
                                    print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramName))
                                    print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(testObj.testParameterValue))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex]) + str(e[0])

            # elif testType == TEST_TYPE_IS_BOOL:
            #
            #     if isinstance(params, dict):
            #
            #         for paramLabel, paramValues in params.items():
            #
            #             try:
            #                 if testObj.testParameterValue in paramValues:
            #                     self.testTypeObj.testIsBoolean(paramValues[testObj.testParameterValue])
            #                     if self.verboseFlag:
            #                         print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
            #                         print ( "PASSED" )
            #
            #             except Exception as e:
            #                 if self.verboseFlag:
            #                     print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
            #                 print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex])
            #     else:
            #             try:
            #                 paramName = eval(testObj.testParameterValue)
            #
            #                 self.testTypeObj.testIsBoolean(paramName)
            #                 if self.verboseFlag:
            #                     print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramName))
            #                     print ( "PASSED" )
            #
            #             except Exception as e:
            #                 if self.verboseFlag:
            #                     print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(testObj.testParameterValue))
            #                 print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex]) + str(e[0])

            elif testType == TEST_TYPE_VALUE_LIST:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            if testObj.testParameterValue in paramValues:
                                self.testTypeObj.testIsValueList(paramValues[testObj.testParameterValue], testObj.testValueList)
                                if self.verboseFlag:
                                    print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                                    print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex])
                else:
                        try:
                            paramName = eval(testObj.testParameterValue)
                            self.testTypeObj.testIsValueList(paramName, testObj.testValueList)
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramName))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(testObj.testParameterValue))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex]) + str(e)
            elif testType == TEST_TYPE_ALL_VALUE_LIST:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            if testObj.testParameterValue in paramValues:
                                self.testTypeObj.testIsAllValueList(paramValues[testObj.testParameterValue], testObj.testValueList)
                                if self.verboseFlag:
                                    print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                                    print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex])
                else:
                        try:
                            paramName = ''
                            try:
                                paramName = eval(testObj.testParameterValue)
                            except:
                                pass
                            if paramName != '':
                                self.testTypeObj.testIsAllValueList(paramName, testObj.testValueList)
                                if self.verboseFlag:
                                    print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramName))
                                    print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(testObj.testParameterValue))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex]) + str(e)

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
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                                print ( "PASSED" )

                        except Exception as e:
                            if self.verboseFlag:
                                print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramValues))
                            print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex])

            elif testType == TEST_TYPE_DICT_KEY_VALID_VALUE:

                try:
                    paramDict = ''
                    try:
                        paramDict = eval(testObj.testParameterValue)
                    except:
                        pass
                    if paramDict != '':
                        self.testTypeObj.testDictKeyValidValue(paramDict, testObj.testValueList)
                        if self.verboseFlag:
                            print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(paramDict))
                            print ( "PASSED" )

                except Exception as e:
                    if self.verboseFlag:
                        print ( "Test: " + str(testObj.testParameterValue) + " for: " + str(testType)+ " value: " + str(testObj.testParameterValueList))
                    print str(testObj.errorMessageLevel[testIndex]) + ": " + str(testObj.messageText[testIndex]) + str(e)

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
                            #print (str(MESSAGE_TYPE_ERROR) + ": Geometry is invalid. ")
                            print (str(MESSAGE_TYPE_ERROR) + ":" + str(e))

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

                                    print (str(MESSAGE_TYPE_ERROR) + ": " + errorMessage)

                        except Exception as e:
                            traceback.print_exc(file=sys.stdout)
                            if self.verboseFlag:
                                print ( "Test: for valid mechanisms in cell")

                            print (str(MESSAGE_TYPE_ERROR) + ": Mechanism specified is invalid.")

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
                            print (str(MESSAGE_TYPE_ERROR) + ": Pointps in cell params specified is invalid. Please check against utils.mechVarlist.")

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

            elif testType == TEST_TYPE_VALID_STIM:

                if isinstance(params, dict):
                    for paramLabel, paramValues in params.items():
                        try:

                            stimValid, errorMessages = self.testTypeObj.testValidStim(paramValues)

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

            elif testType == TEST_TYPE_VALID_ANALYSIS:

                    try:

                        errorMessages = self.testTypeObj.testValidAnalysis(params)

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
