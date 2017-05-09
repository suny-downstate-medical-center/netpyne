"""
test_validate.py

Testing code for Validation class

Contributors: mitra.sidddhartha@gmail.com
"""
from tests import *
import specs

class ParamsObj():

        """Set of possible parameters"""

        def __init__ (self):

            self.simConfig = specs.SimConfig()  # object of class SimConfig to store simulation configuration
            self.netParams = specs.NetParams()  # object of class NetParams to store the network parameters

class RunNetPyneTests():

        """Set of possible parameters"""

        def __init__ (self):
            self.paramsMap = {}
            self.netPyneTestObj = NetPyneTestObj(verboseFlag = True)
            self.loadTestsWithParams()
            self.runTestsWithParams()

        def loadTestsWithParams(self):

            # print ( " loading tests ")
            self.paramsMap["pop"] = {}
            self.paramsMap["net"] = {}
            self.paramsMap["conn"] = {}
            self.paramsMap["cell"] = {}

            self.paramsMap["pop"]["cellModelTest"] = []

            cellModelParams = ParamsObj()
            cellModelParams.netParams.popParams['validCellModelParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'numCells': 50}     # add dict with params for this pop
            self.paramsMap["pop"]["cellModelTest"].append(cellModelParams)

            cellModelParams = ParamsObj()
            cellModelParams.netParams.popParams['invalidCellModelParams'] = {'cellType': 'PYR', 'numCells': 50}     # add dict with params for this pop
            self.paramsMap["pop"]["cellModelTest"].append(cellModelParams)

            self.paramsMap["pop"]["volumeParamsTest"] = []

            volumeParams = ParamsObj()
            volumeParams.netParams.popParams['validVolumeParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50}     # add dict with params for this pop
            self.paramsMap["pop"]["volumeParamsTest"].append(volumeParams)

            volumeParams = ParamsObj()
            volumeParams.netParams.popParams['invalidVolumeParams'] = {'cellType': 'PYR', 'cellModel': 'HH'}     # add dict with params for this pop
            self.paramsMap["pop"]["volumeParamsTest"].append(volumeParams)

            self.paramsMap["pop"]["xNormRangeParamsTest"] = []

            params = ParamsObj()
            params.netParams.popParams['validxNormRangeParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50, 'xnormRange' : [0.6,0.9]}     # add dict with params for this pop
            self.paramsMap["pop"]["xNormRangeParamsTest"].append(params)

            params = ParamsObj()
            params.netParams.popParams['invalidxNormRangeParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50, 'xnormRange' : 0.6}     # add dict with params for this pop
            self.paramsMap["pop"]["xNormRangeParamsTest"].append(params)

            params = ParamsObj()
            params.netParams.popParams['invalidxNormRangeParams1'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50, 'xnormRange' : [6,10]}     # add dict with params for this pop
            self.paramsMap["pop"]["xNormRangeParamsTest"].append(params)

            self.paramsMap["pop"]["yNormRangeParamsTest"] = []

            params = ParamsObj()
            params.netParams.popParams['validyNormRangeParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50, 'ynormRange' : [0.6,0.9]}     # add dict with params for this pop
            self.paramsMap["pop"]["yNormRangeParamsTest"].append(params)

            params = ParamsObj()
            params.netParams.popParams['invalidyNormRangeParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50, 'ynormRange' : 0.6}     # add dict with params for this pop
            self.paramsMap["pop"]["yNormRangeParamsTest"].append(params)

            params = ParamsObj()
            params.netParams.popParams['invalidyNormRangeParams1'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50, 'ynormRange' : [6,10]}     # add dict with params for this pop
            self.paramsMap["pop"]["yNormRangeParamsTest"].append(params)

            self.paramsMap["pop"]["zNormRangeParamsTest"] = []

            params = ParamsObj()
            params.netParams.popParams['validzNormRangeParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50, 'znormRange' : [0.6,0.9]}     # add dict with params for this pop
            self.paramsMap["pop"]["zNormRangeParamsTest"].append(params)

            params = ParamsObj()
            params.netParams.popParams['invalidzNormRangeParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50, 'znormRange' : 0.6}     # add dict with params for this pop
            self.paramsMap["pop"]["zNormRangeParamsTest"].append(params)

            params = ParamsObj()
            params.netParams.popParams['invalidzNormRangeParams1'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50, 'znormRange' : [6,10]}     # add dict with params for this pop
            self.paramsMap["pop"]["zNormRangeParamsTest"].append(params)

            self.paramsMap["pop"]["zNormRangeParamsTest"] = []

            params = ParamsObj()
            params.netParams.popParams['validzNormRangeParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50, 'znormRange' : [0.6,0.9]}     # add dict with params for this pop
            self.paramsMap["pop"]["zNormRangeParamsTest"].append(params)

            params = ParamsObj()
            params.netParams.popParams['invalidzNormRangeParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50, 'znormRange' : 0.6}     # add dict with params for this pop
            self.paramsMap["pop"]["zNormRangeParamsTest"].append(params)

            params = ParamsObj()
            params.netParams.popParams['invalidzNormRangeParams1'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50, 'znormRange' : [6,10]}     # add dict with params for this pop
            self.paramsMap["pop"]["zNormRangeParamsTest"].append(params)

            self.paramsMap["pop"]["xRangeParamsTest"] = []

            params = ParamsObj()
            params.netParams.sizeX = 70   # max size for network
            params.netParams.popParams['validxRangeParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50, 'xRange' : [30,60]}     # add dict with params for this pop
            self.paramsMap["pop"]["xRangeParamsTest"].append(params)

            params = ParamsObj()
            params.netParams.sizeX = 70   # max size for network
            params.netParams.popParams['invalidxRangeParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50, 'xRange' : [40,90]}     # add dict with params for this pop
            self.paramsMap["pop"]["xRangeParamsTest"].append(params)

            self.paramsMap["pop"]["yRangeParamsTest"] = []

            params = ParamsObj()
            params.netParams.sizeY = 70   # max size for network
            params.netParams.popParams['validyRangeParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50, 'yRange' : [30,60]}     # add dict with params for this pop
            self.paramsMap["pop"]["yRangeParamsTest"].append(params)

            params = ParamsObj()
            params.netParams.sizeY = 70   # max size for network
            params.netParams.popParams['invalidyRangeParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50, 'yRange' : [40,90]}     # add dict with params for this pop
            self.paramsMap["pop"]["yRangeParamsTest"].append(params)

            self.paramsMap["pop"]["zRangeParamsTest"] = []

            params = ParamsObj()
            params.netParams.sizeZ = 70   # max size for network
            params.netParams.popParams['validzRangeParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50, 'zRange' : [30,60]}     # add dict with params for this pop
            self.paramsMap["pop"]["zRangeParamsTest"].append(params)

            params = ParamsObj()
            params.netParams.sizeZ = 70   # max size for network
            params.netParams.popParams['invalidzRangeParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50, 'zRange' : [40,90]}     # add dict with params for this pop
            self.paramsMap["pop"]["zRangeParamsTest"].append(params)

            #net params test
            self.paramsMap["net"]["sizeXParamsTest"] = []

            params = ParamsObj()
            params.netParams.sizeX = 70   # max size for network
            self.paramsMap["net"]["sizeXParamsTest"].append(params)

            params = ParamsObj()
            params.netParams.sizeX = 3.53   # max size for network
            self.paramsMap["net"]["sizeXParamsTest"].append(params)

            params = ParamsObj()
            params.netParams.sizeX = -44   # max size for network
            self.paramsMap["net"]["sizeXParamsTest"].append(params)

            self.paramsMap["net"]["shapeTest"] = []

            params = ParamsObj()
            params.netParams.shape = "cuboid"   # max size for network
            self.paramsMap["net"]["shapeTest"].append(params)

            params = ParamsObj()
            params.netParams.shape = "ellipsoid"   # max size for network
            self.paramsMap["net"]["shapeTest"].append(params)

            params = ParamsObj()
            params.netParams.shape = "cylinder"   # max size for network
            self.paramsMap["net"]["shapeTest"].append(params)

            params = ParamsObj()
            params.netParams.shape = "sphere"   # max size for network
            self.paramsMap["net"]["shapeTest"].append(params)

            # cell params test
            self.paramsMap["cell"]["condsTest"] = []

            # valid cell rule
            params = ParamsObj()
            cellRule = {'conds': {'cellType': 'E2', 'cellModel': 'simple'},  'secs': {}}                        # cell rule dict
            cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            params.netParams.cellParams['validCellParams'] = cellRule # add dict with params for this pop
            self.paramsMap["cell"]["condsTest"].append(params)

            # invalid cell rule
            params = ParamsObj()
            cellRule = { 'secs': {}}                        # cell rule dict
            cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            params.netParams.cellParams['inValidCellParams'] = cellRule # add dict with params for this pop
            self.paramsMap["cell"]["condsTest"].append(params)

        def runTestsWithParams(self):

            self.runPopTestsWithParams()
            #self.runNetTestsWithParams()
            #self.runCellTestsWithParams()
            # runConnTestsWithParams()

        def runPopTestsWithParams(self):
            popParamsMap = self.paramsMap["pop"]
            # run the different tests for pop
            for testName, paramObjList in popParamsMap.items():
                # run the test with different params
                for paramsObj in paramObjList:
                    self.netPyneTestObj.netParams = paramsObj.netParams
                    self.netPyneTestObj.runTests()

        def runNetTestsWithParams(self):
            netParamsMap = self.paramsMap["net"]
            # run the different tests for net
            for testName, paramObjList in netParamsMap.items():
                # run the test with different params
                for paramsObj in paramObjList:
                    self.netPyneTestObj.netParams = paramsObj.netParams
                    self.netPyneTestObj.runTests()

        def runCellTestsWithParams(self):
            cellParamsMap = self.paramsMap["cell"]
            # run the different tests for cell
            for testName, paramObjList in cellParamsMap.items():
                # run the test with different params
                for paramsObj in paramObjList:
                    self.netPyneTestObj.netParams = paramsObj.netParams
                    self.netPyneTestObj.runTests()

runNetPyneTests = RunNetPyneTests()
#runNetPyneTests.runTestsWithParams()
