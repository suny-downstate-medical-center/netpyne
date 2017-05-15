"""
test_validate.py

Testing code for Validation class

Contributors: mitra.sidddhartha@gmail.com
"""
import unittest
import numbers
import sys
import os
import traceback
import specs

VALID_GEOMETRIES = ['pt3d', 'L', 'dia', 'Ra']
VALID_SHAPES = ['cuboid', 'ellipsoid', ' cylinder']
POP_NUMCELLS_PARAMS = ['Density','NumCells','GridSpacing']

MESSAGE_TYPE_WARN = "WARNING"
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
TEST_TYPE_SPECIAL = "Special" # special method, method name provided

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

    def testExistsInDict(self, val,dict):
        try:
            assert val in dict, " Value " + str(val) + "exists in dictionary " + str(params) + "."
        except AssertionError as e:
            e.args += (val,)
            raise

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

    def testIsNumeric(self,val): # TEST_TYPE_IS_DICT
        try:
            assert (isinstance (val,numbers.Number))
        except AssertionError as e:
            e.args += (val,)
            raise

    def testIsFloat(self,val): # TEST_TYPE_IS_FLOAT
        try:
            assert (isinstance (val,float))
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

# Tests that are defined for each set of parameters
class TestObj(object):

    def __init__(self):

        self.testName = '' # test name

        self.testParameterType = '' # test parameter, type string, list
        self.testParameterValue = '' # test parameter value, like 'shape'
        self.testParameterValueList = '' # test parameter value list, like ['density', 'numCells','gridSpacing']
        self.testParameterDictString = '' # for nested dicts like ['shape']['geom']

        self.testTypes = [] # list of be multiple tests
        self.testValueList = [] # could be restricted list like ['cuboid','ellipsoid','cylinder']
        self.testValueRange = [] # could be restricted range like [0,1]

        self.compareValueString = "" # variable name - like netParams.sizeX, or value
        self.compareValueDataType = "" # data type of compare value ( string or list or dict
        self.compareValueType = "" # eval (if compareValueString is string or int or float
        self.compareDict = {} # dict for running tests against input value
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
        # self.loadCellTests() # load cell tests
        # # self.loadConnTests() # load conn tests
        if self.verboseFlag:
            print (" *** Finish loading tests *** ")

    def runTests(self):

        # if self.verboseFlag:
        #     print (" *** Running tests *** ")
        self.runPopTests() # run pop tests
        self.runNetTests() # run net tests
        # self.runCellTests() # run cell tests
        # self.runConnTests() # run conn tests

        # if self.verboseFlag:
        #     print (" *** Finished running tests *** ")

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
        testObj.messageText = ["One of the following must be specified in parameters:"]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["volumeParamsTest"] = testObj

        # xnormrange test
        testObj = TestObj()
        testObj.testName = "xNormRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "xnormRange"
        testObj.testTypes = [TEST_TYPE_IS_VALID_RANGE, TEST_TYPE_IN_RANGE]
        testObj.testValueRange = "[0,1]"
        testObj.messageText = ["xNormRange invalid range.","xNormRange not in range."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["xNormRangeTest"] = testObj

        # ynormrange test
        testObj = TestObj()
        testObj.testName = "yNormRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "ynormRange"
        testObj.testTypes = [TEST_TYPE_IS_VALID_RANGE, TEST_TYPE_IN_RANGE]
        testObj.testValueRange = "[0,1]"
        testObj.messageText = ["yNormRange invalid.","yNormRange not in range."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["yNormRangeTest"] = testObj

        # znormrange test
        testObj = TestObj()
        testObj.testName = "zNormRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "znormRange"
        testObj.testTypes = [TEST_TYPE_IS_VALID_RANGE, TEST_TYPE_IN_RANGE]
        testObj.testValueRange = "[0,1]"
        testObj.messageText = ["zNormRange invalid.","zNormRange not in range."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["zNormRangeTest"] = testObj

        # xrange test
        testObj = TestObj()
        testObj.testName = "xRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "xRange"
        testObj.testTypes = [TEST_TYPE_IS_VALID_RANGE, TEST_TYPE_IN_RANGE]
        testObj.testValueRange = "[0,self.netParams.sizeX]"
        testObj.messageText = ["xRange invalid.","XRange not in range."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, TEST_TYPE_IN_RANGE]

        self.testParamsMap["pop"]["xRangeTest"] = testObj

        # yrange test
        testObj = TestObj()
        testObj.testName = "yRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "yRange"
        testObj.testTypes = [TEST_TYPE_IS_VALID_RANGE, TEST_TYPE_IN_RANGE]
        testObj.testValueRange = "[0,self.netParams.sizeY]"
        testObj.messageText = ["yRange invalid.", "YRange not in range."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR, MESSAGE_TYPE_ERROR]

        self.testParamsMap["pop"]["yRangeTest"] = testObj

        # zrange test
        testObj = TestObj()
        testObj.testName = "zRangeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "zRange"
        testObj.testTypes = [TEST_TYPE_IS_VALID_RANGE, TEST_TYPE_IN_RANGE]
        testObj.testValueRange = "[0,self.netParams.sizeX]"
        testObj.messageText = ["zRange invalid.", "ZRange not in range."]
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

        # condsTest test
        testObj = TestObj()
        testObj.testName = "condsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "conds"
        testObj.testTypes = [TEST_TYPE_IS_DICT]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["cell"]["condsTest"] = testObj

        # cellTypes test
        testObj = TestObj()
        testObj.testName = "cellTypeTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "cellType"
        testObj.testTypes = [TEST_TYPE_EXISTS_IN_DICT]
        testObj.compareDict = {}
        testObj.messageText = ["Cell type does not match the cell type specified in pop parameters."],
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["cell"]["cellTypeTest"] = testObj

        # cellModel test
        testObj = TestObj()
        testObj.testName = "cellModelTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "cellModel"
        testObj.testTypes = [TEST_TYPE_EXISTS_IN_DICT]
        testObj.messageText = ["Cell model does not match the cell model specified in pop parameters."],
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["cell"]["cellModelTest"] = testObj

        # cellModel test
        testObj = TestObj()
        testObj.testName = "cellModelTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "cellModel"
        testObj.testTypes = [TEST_TYPE_EXISTS_IN_DICT]
        testObj.messageText = ["Cell model does not match the cell model specified in pop parameters."],
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["cell"]["cellModelTest"] = testObj

        # geom test
        testObj = TestObj()
        testObj.testName = "geomExistTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "geom"
        testObj.testTypes = [TEST_TYPE_EXISTS]

        testObj.compareValueString = "cellParams.cellModel"
        testObj.compareValueDataType = "dict"
        testObj.compareValueType = "eval"

        testObj.messageText = ["Geom is not specified."]
        testObj.errorMessageLevel = [MESSAGE_TYPE_WARN]
        self.testParamsMap["cell"]["geomExistTest"] = testObj

        # geom test
        testObj = TestObj()
        testObj.testName = "geomValidTest",
        testObj.testParameterType = "string",
        testObj.testParameterValue = "geom",
        testObj.testTypes = [TEST_TYPE_VALUE_LIST],
        testObj.testValueList = VALID_GEOMETRIES,
        testObj.messageText = ["Geom is not valid."],
        testObj.errorMessageLevel = ["MESSAGE_TYPE_WARN"]

        self.testParamsMap["cell"]["geomValidTest"] = testObj

        # topol test
        testObj = TestObj()
        testObj.testName = "toplogyTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "topol"
        testObj.testTypes = [TEST_TYPE_SPECIAL]
        testObj.testTypeSpecialString = "checkCellTopology"
        testObj.messageText = ["Topology is not valid."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        self.testParamsMap["cell"]["toplogyTest"] = testObj

        # mechs test

        # -- mechs: not required, check mech and properties exist using utils.mechVarList()
        # -- ions: not required, check mech and properties exist using utils.mechVarList()
        # -- pointps: not required;
        # -- required key 'mod' wiht pointp label; check exists using utils.mechVarlist()
        # -- 'loc' also required; has to be between 0 and 1
        # -- 'vref' and 'synList' optional
        # - spikeGenLoc: not rquired; between 0 and 1

        testObj = TestObj()
        testObj.testName = "mechsTest",
        testObj.testParameterType = "string",
        testObj.testParameterValue = "mechs",
        testObj.testTypes = [TEST_TYPE_SPECIAL],
        testObj.testTypeSpecialString = "mechVarListTest"
        testObj.messageText = ["Incorrect parameter for mechanisms."],
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        self.testParamsMap["cell"]["mechsTest"] = testObj
        #ions
        testObj = TestObj()
        testObj.testName = "ionsTest",
        testObj.testParameterType = "string",
        testObj.testParameterValue = "mechs",
        testObj.testTypes = [TEST_TYPE_SPECIAL],
        testObj.testTypeSpecialString = "mechVarListTest"
        testObj.messageText = ["Incorrect parameter for mechanisms."],
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        self.testParamsMap["cell"]["ionsTest"] = testObj

        #pointps
        testObj = TestObj()
        testName = "pointpsTest",
        testObj.testParameterType = "string",
        testObj.testParameterValue = "ions",
        testObj.testTypes = [TEST_TYPE_SPECIAL],
        testObj.testTypeSpecialString = "mechVarListTest"
        testObj.messageText = ["Incorrect parameter for mechanisms."],
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        self.testParamsMap["cell"]["pointpsTest"] = testObj

    def loadConnTests(self):

        # if self.verboseFlag:
        #     print (" *** Loading conn tests *** ")

        self.testParamsMap["conn"] = {}

        # condsTest test
        testObj = TestObj()
        testObj.testName = "preCondsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "conds"
        testObj.testTypes = [TEST_TYPE_EXISTS]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["conn"]["preCondsTest"] = testObj

        # condsTest test
        testObj = TestObj()
        testObj.testName = "postCondsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "conds"
        testObj.testTypes = [TEST_TYPE_EXISTS]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["conn"]["postCondsTest"] = testObj

    def loadConnTests(self):

        # if self.verboseFlag:
        #     print (" *** Loading conn tests *** ")

        self.testParamsMap["conn"] = {}

        # condsTest test
        testObj = TestObj()
        testObj.testName = "preCondsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "conds"
        testObj.testTypes = [TEST_TYPE_EXISTS]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["conn"]["preCondsTest"] = testObj

        # condsTest test
        testObj = TestObj()
        testObj.testName = "postCondsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "conds"
        testObj.testTypes = [TEST_TYPE_EXISTS]
        testObj.errorMessageLevel = [MESSAGE_TYPE_ERROR]

        self.testParamsMap["conn"]["postCondsTest"] = testObj

        # if self.verboseFlag:
        #     print (" *** Finished loading conn tests *** ")

        # secs test
        testObj = TestObj()
        testObj.testName = "connsSecsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "secs"
        testObj.testTypes = [TEST_TYPE_EXISTS, TEST_TYPE_IS_DICT ]
        testObj.messageText = ["Secs, is specified, needs to be a dict.", "Secs is not specified. Will use 'soma' by default otherwise first available section."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_WARN", "MESSAGE_TYPE_ERROR"]

        self.testParamsMap["conn"]["connsSecsTest"] = testObj

        # locs test
        testObj = TestObj()
        testObj.testName = "locsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "locs"
        testObj.testTypes = [TEST_TYPE_SPECIAL ]
        testObj.testTypeSpecialString = "connsLocTest"
        testObj.messageText = ["Locs is invalid."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        self.testParamsMap["conn"]["locsTest"] = testObj

        # weight test
        testObj = TestObj()
        testObj.testName = "weightsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "weight"
        testObj.testTypeSpecialString = "connsWeightTest"
        testObj.testTypes = [TEST_TYPE_SPECIAL ]
        testObj.messageText = ["Weight is invalid."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        testParamsMap["conn"]["weightsTest"] = testObj

        # delay test
        testObj = TestObj()
        testObj.testName = "delayTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "delay"
        testObj.testTypeSpecialString = "connsDelayTest"
        testObj.testTypes = [TEST_TYPE_SPECIAL ]
        testObj.messageText = ["Delay is invalid."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        testParamsMap["conn"]["delayTest"] = testObj

        # synMech
        testObj = TestObj()
        testObj.testName = "synMechTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "synMech"
        testObj.testTypeSpecialString = "synMechsTest"
        testObj.testTypes = [TEST_TYPE_SPECIAL ]
        testObj.messageText = ["Syn Mech is invalid."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        testParamsMap["conn"]["synMechTest"] = testObj

        # synsPerConn
        #- synsPerConn: optional, defaults to 1; has to be >=1

        testObj = TestObj()
        testObj.testName = "synsPerConnTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "synsPerConn"
        testObj.testTypeSpecialString = "synMechsTest"
        testObj.testTypes = [TEST_TYPE_INTEGER, TEST_TYPE_GTE ]
        testObj.compareValueString = "1"
        testObj.compareValueType = "int"
        testObj.messageText = ["Syns Per Conn must be >= 1."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        testParamsMap["conn"]["synsPerConnTest"] = testObj

        # probability: optional; [0,1]
        testObj = TestObj()
        testObj.testName = "probabilityTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "probability"
        testObj.testTypes = [TEST_TYPE_IS_FLOAT, TEST_TYPE_GTE_ZERO, TEST_TYPE_LTE ]
        testObj.compareValueString = "1"
        testObj.compareValueType = "int"
        testObj.messageText = ["Probability needs to be between 0 and 1."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        testParamsMap["conn"]["probabilityTest"] = testObj

        # convergence  optional; positive integer

        testObj = TestObj()
        testObj.testName = "convergenceTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "convergence"
        testObj.testTypes = [TEST_TYPE_IS_INT, TEST_TYPE_GTE_ZERO ]
        testObj.messageText = ["Convergence, is specified, needs to be a positive integer."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        testParamsMap["conn"]["convergenceTest"] = testObj

        # divergence  optional; positive integer

        testObj = TestObj()
        testObj.testName = "divergenceTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "divergence"
        testObj.testTypes = [TEST_TYPE_IS_INT, TEST_TYPE_GTE_ZERO ]
        testObj.messageText = ["Divergence, is specified, needs to be a positive integer."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        testParamsMap["conn"]["divergenceTest"] = testObj
>>>>>>> format

        # secs test
        testObj = TestObj()
        testObj.testName = "connsSecsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "secs"
        testObj.testTypes = [TEST_TYPE_EXISTS, TEST_TYPE_IS_DICT ]
        testObj.messageText = ["Secs, is specified, needs to be a dict.", "Secs is not specified. Will use 'soma' by default otherwise first available section."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_WARN", "MESSAGE_TYPE_ERROR"]

        self.testParamsMap["conn"]["connsSecsTest"] = testObj

        # locs test
        testObj = TestObj()
        testObj.testName = "locsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "locs"
        testObj.testTypes = [TEST_TYPE_SPECIAL ]
        testObj.testTypeSpecialString = "connsLocTest"
        testObj.messageText = ["Locs is invalid."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        self.testParamsMap["conn"]["locsTest"] = testObj

        # weight test
        testObj = TestObj()
        testObj.testName = "weightsTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "weight"
        testObj.testTypeSpecialString = "connsWeightTest"
        testObj.testTypes = [TEST_TYPE_SPECIAL ]
        testObj.messageText = ["Weight is invalid."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        testParamsMap["conn"]["weightsTest"] = testObj

        # delay test
        testObj = TestObj()
        testObj.testName = "delayTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "delay"
        testObj.testTypeSpecialString = "connsDelayTest"
        testObj.testTypes = [TEST_TYPE_SPECIAL ]
        testObj.messageText = ["Delay is invalid."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        testParamsMap["conn"]["delayTest"] = testObj

        # synMech
        testObj = TestObj()
        testObj.testName = "synMechTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "synMech"
        testObj.testTypeSpecialString = "synMechsTest"
        testObj.testTypes = [TEST_TYPE_SPECIAL ]
        testObj.messageText = ["Syn Mech is invalid."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        testParamsMap["conn"]["synMechTest"] = testObj

        # synsPerConn
        #- synsPerConn: optional, defaults to 1; has to be >=1

        testObj = TestObj()
        testObj.testName = "synsPerConnTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "synsPerConn"
        testObj.testTypeSpecialString = "synMechsTest"
        testObj.testTypes = [TEST_TYPE_INTEGER, TEST_TYPE_GTE ]
        testObj.compareValueString = "1"
        testObj.compareValueType = "int"
        testObj.messageText = ["Syns Per Conn must be >= 1."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        testParamsMap["conn"]["synsPerConnTest"] = testObj

        # probability: optional; [0,1]
        testObj = TestObj()
        testObj.testName = "probabilityTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "probability"
        testObj.testTypes = [TEST_TYPE_IS_FLOAT, TEST_TYPE_GTE_ZERO, TEST_TYPE_LTE ]
        testObj.compareValueString = "1"
        testObj.compareValueType = "int"
        testObj.messageText = ["Probability needs to be between 0 and 1."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        testParamsMap["conn"]["probabilityTest"] = testObj

        # convergence  optional; positive integer

        testObj = TestObj()
        testObj.testName = "convergenceTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "convergence"
        testObj.testTypes = [TEST_TYPE_IS_INT, TEST_TYPE_GTE_ZERO ]
        testObj.messageText = ["Convergence, is specified, needs to be a positive integer."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        testParamsMap["conn"]["convergenceTest"] = testObj

        # divergence  optional; positive integer

        testObj = TestObj()
        testObj.testName = "divergenceTest"
        testObj.testParameterType = "string"
        testObj.testParameterValue = "divergence"
        testObj.testTypes = [TEST_TYPE_IS_INT, TEST_TYPE_GTE_ZERO ]
        testObj.messageText = ["Divergence, is specified, needs to be a positive integer."]
        testObj.errorMessageLevel = ["MESSAGE_TYPE_ERROR"]

        testParamsMap["conn"]["divergenceTest"] = testObj

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
        for testName, cellTestObj in self.testParamsMap["cell"].items():
            self.execRunTests(cellTestObj, cellParams)

        # if self.verboseFlag:
        #     print (" *** Finished running cell tests *** ")

    def runConnTests(self):

        # if self.verboseFlag:
        #     print (" *** Running conn tests *** ")

        connParams = self.netParams.connParams
        for testName, connTestObj in self.testParamsMap["conn"].items():
            self.execRunTests(connTestObj, connParams)

        # if self.verboseFlag:
        #     print (" *** Finished running conn tests *** ")

    def execRunTests(self, testObj, params):

        # if self.verboseFlag:
        #     print ( " ::: flag is " + str(self.verboseFlag))
        #
        #     print (" *** executing individual tests *** ")

        for testIndex, testType in enumerate(testObj.testTypes):

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

            elif testType == TEST_TYPE_IN_RANGE:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            self.testTypeObj.testInRange(testObj.testParameterValue, eval(testObj.testValueRange), paramValues)
                            if self.verboseFlag  and testObj.testParameterValue in paramValues:
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

            elif testType == TEST_TYPE_IS_VALID_RANGE:

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            self.testTypeObj.testIsValidRange(testObj.testParameterValue, paramValues)
                            if self.verboseFlag and testObj.testParameterValue in paramValues:
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
                            self.testTypeObj.testIsInt(testObj.testParameterValue)
                            if self.verboseFlag  and testObj.testParameterValue in paramValues:
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
                                print str(testObj.errorMessageLevel[testIndex]) + " : " + str(testObj.messageText[testIndex])

            elif testType == TEST_TYPE_GTE_ZERO :

                if isinstance(params, dict):

                    for paramLabel, paramValues in params.items():

                        try:
                            self.testTypeObj.testGteZero(testObj.testParameterValue, paramValues)
                            if self.verboseFlag and testObj.testParameterValue in paramValues:
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
