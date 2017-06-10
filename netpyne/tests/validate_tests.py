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
            self.paramsMap["stimSource"] = {}
            self.paramsMap["stimTarget"] = {}

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

            #
            # # cell params test
            # self.paramsMap["cell"]["condsTest"] = []
            #
            # # valid cell conds rule
            # params = ParamsObj()
            # cellRule = {'conds': {'cellType': 'E2', 'cellModel': 'simple'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['validConds'] = cellRule # add dict with params for this pop
            # #print ( str(cellRule["conds"]) )
            # self.paramsMap["cell"]["condsTest"].append(params)
            #
            # # valid cell conds rule
            # params = ParamsObj()
            # cellRule = {'conds': 'test',  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['inValidConds1'] = cellRule # add dict with params for this pop
            # #print ( str(cellRule["conds"]) )
            # self.paramsMap["cell"]["condsTest"].append(params)
            #
            # # invalid cell conds rule
            # params = ParamsObj()
            # cellRule = { 'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['inValidConds2'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["condsTest"].append(params)
            #
            # # cell params test
            # self.paramsMap["cell"]["secsTest"] = []
            #
            # # invalid sec type rule
            # params = ParamsObj()
            # cellRule = { 'secs': 'test'}                        # cell rule dict
            # params.netParams.cellParams['inValidSecs1'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["secsTest"].append(params)
            #
            # # cell types test
            # self.paramsMap["cell"]["cellTypesTest"] = []
            #
            # # valid cell type rule
            # params = ParamsObj()
            # params.netParams.popParams['validCellModelParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'numCells': 50}     # add dict with params for this pop
            # cellRule = {'conds': {'cellType': 'PYR'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['validCellTypes'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["cellTypesTest"].append(params)
            #
            # # invalid cell type rule
            # params = ParamsObj()
            # params.netParams.popParams['validCellModelParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'numCells': 50}     # add dict with params for this pop
            # cellRule = { 'conds': {'cellType': 'PY1'}, 'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['inValidCellTypes'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["cellTypesTest"].append(params)
            #
            # # cell params test
            # self.paramsMap["cell"]["cellModelsTest"] = []
            #
            # # valid cell model rule
            # params = ParamsObj()
            # params.netParams.popParams['validCellModelParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'numCells': 50}     # add dict with params for this pop
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['validCellModel'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["cellModelsTest"].append(params)
            #
            # # invalid cell model rule
            # params = ParamsObj()
            # params.netParams.popParams['validCellModelParams'] = {'cellType': 'PYR', 'cellModel': 'HH', 'numCells': 50}     # add dict with params for this pop
            # cellRule = { 'conds': {'cellModel': 'H1' }, 'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['inValidCellModel'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["cellModelsTest"].append(params)
            #
            # geom test
            self.paramsMap["cell"]["geomTest"] = []
            #
            # # valid geom rule
            # params = ParamsObj()
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['validGeom'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["geomTest"].append(params)
            #
            # # invalid geom rule
            # params = ParamsObj()
            # cellRule = { 'conds': {'cellModel': 'H1' }, 'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = { 'mechs': {}}                                                # soma params dict
            # params.netParams.cellParams['inValidGeom'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["geomTest"].append(params)
            #
            # #valid geom rule
            # params = ParamsObj()
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['validGeom1'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["geomTest"].append(params)
            #
            # # valid geom rule
            # params = ParamsObj()
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0, 'pt3d' : [] }                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['validGeom2'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["geomTest"].append(params)
            #
            # # valid geom rule
            # params = ParamsObj()
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'pt3d' : [] }                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['validGeom3'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["geomTest"].append(params)
            #
            # # valid geom rule
            # params = ParamsObj()
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'pt3d' : [[1,2,3,4],[3,4,5,6]] }                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['validGeom4'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["geomTest"].append(params)
            #
            # # invalid geom rule
            # params = ParamsObj()
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'pt3d' : 2.3 }                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['invalidGeom1'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["geomTest"].append(params)
            #
            # # invalid geom rule
            # params = ParamsObj()
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam' : 2.3 }                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['invalidGeom2'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["geomTest"].append(params)

            # # invalid geom rule
            # params = ParamsObj()
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'xy' : 2.3 }                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['invalidGeom3'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["geomTest"].append(params)
            #
            # # invalid geom rule
            # params = ParamsObj()
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['invalidGeom4'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["geomTest"].append(params)
            #
            # # invalid geom rule
            # params = ParamsObj()
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'pt3d':[2,3,4]}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['invalidGeom5'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["geomTest"].append(params)
            #
            # # invalid geom rule
            # params = ParamsObj()
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'pt3d':[[2,3,4],[3,4,5]]}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['invalidGeom6'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["geomTest"].append(params)
            #
            # # invalid geom rule
            # params = ParamsObj()
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'pt3d':[[2,3,4,4],[3,4,"a",3]]}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            # params.netParams.cellParams['invalidGeom7'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["geomTest"].append(params)

            # # topology test
            # self.paramsMap["cell"]["topologyTest"] = []
            #
            # # valid topology rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 										# dend mechanisms
            #
            # params.netParams.cellParams['validTopology1'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["topologyTest"].append(params)
            #
            # # invalid topology rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 										# dend mechanisms
            #
            # params.netParams.cellParams['invalidTopology1'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["topologyTest"].append(params)
            #
            # # invalid topology rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 										# dend mechanisms
            #
            # params.netParams.cellParams['invalidTopology2'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["topologyTest"].append(params)
            #
            # # invalid topology rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 										# dend mechanisms
            #
            # params.netParams.cellParams['invalidTopology3'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["topologyTest"].append(params)
            #
            # # invalid topology rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma1', 'parentX': 1.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 										# dend mechanisms
            #
            # params.netParams.cellParams['invalidTopology4'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["topologyTest"].append(params)
            #
            # # invalid topology rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 2.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 										# dend mechanisms
            #
            # params.netParams.cellParams['invalidTopology5'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["topologyTest"].append(params)
            #
            # # invalid topology rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 2.0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 										# dend mechanisms
            #
            # params.netParams.cellParams['invalidTopology6'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["topologyTest"].append(params)
            #
            # # mechs test
            # self.paramsMap["cell"]["mechsTest"] = []
            #
            # # valid mechs rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 										# dend mechanisms
            #
            # params.netParams.cellParams['validMechs1'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["mechsTest"].append(params)
            #
            # # invalid mechs rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 										# dend mechanisms
            #
            # params.netParams.cellParams['invalidMechs1'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["mechsTest"].append(params)
            #
            # # invalid mechs rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357} 										# dend mechanisms
            #
            # params.netParams.cellParams['invalidMechs2'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["mechsTest"].append(params)
            #
            # # invalid mechs rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl1': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 										# dend mechanisms
            #
            # params.netParams.cellParams['invalidMechs3'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["mechsTest"].append(params)
            #
            # # invalid mechs rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e1': -70} 										# dend mechanisms
            #
            # params.netParams.cellParams['invalidMechs4'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["mechsTest"].append(params)
            #
            # # ions test
            # self.paramsMap["cell"]["ionsTest"] = []
            #
            # # valid ions rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['soma']['mechs']['k_ion'] = {'i':10,'e':20,'o':30} # potassium ions
            # cellRule['secs']['soma']['mechs']['na_ion'] = {'o':3,'i':4,'e':5} # sodium ions
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 										# dend mechanisms
            #
            # params.netParams.cellParams['validIons1'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["ionsTest"].append(params)
            #
            # # invalid ions rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['soma']['mechs']['k_ion'] = {'x':10} # potassium ions
            # cellRule['secs']['soma']['mechs']['na_ion'] = {'y':3} # sodium ions
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 										# dend mechanisms
            #
            # params.netParams.cellParams['invalidIons1'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["ionsTest"].append(params)
            #
            # # invalid mechs rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['soma']['mechs']['k_ion'] = {'i':10} # potassium ions
            # cellRule['secs']['soma']['mechs']['na_ion'] = {'o':3} # sodium ions
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'e': 0.0000357, 'g':0.3} 										# dend mechanisms
            #
            # params.netParams.cellParams['invalidIons2'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["ionsTest"].append(params)
            #
            # # invalid mechs rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl1': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['soma']['mechs']['mg_ion'] = {'mg1':10} # mg ions
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 										# dend mechanisms
            #
            # params.netParams.cellParams['invalidIons3'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["ionsTest"].append(params)
            #
            # # invalid mechs rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e1': -70} 										# dend mechanisms
            #
            # params.netParams.cellParams['invalidIons4'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["ionsTest"].append(params)
            #
            # # pointps test
            # self.paramsMap["cell"]["pointpsTest"] = []
            #
            # # valid pointps rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'pointps': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['pointps']['Izhi'] = {'mod':'Izhi2007b', 'C':1, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}
            #
            # params.netParams.cellParams['validPointPs1'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["pointpsTest"].append(params)
            #
            # # invalid pointps rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'pointps': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['pointps']['Izhi'] = { 'C':1, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}
            #
            # params.netParams.cellParams['invalidPointPs1'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["pointpsTest"].append(params)
            #
            # # invalid pointps rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'pointps': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['pointps']['Izhi'] = {'mod':'Izhi2007b', 'C':1, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1,'synList' :'q'}
            #
            # params.netParams.cellParams['invalidPointPs2'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["pointpsTest"].append(params)
            #
            # # invalid pointps rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'pointps': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['pointps']['Izhi'] = {'mod':'Izhi2007b', 'C':1, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1,'loc' :4}
            #
            # params.netParams.cellParams['invalidPointPs2'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["pointpsTest"].append(params)
            #
            # # secList test
            # self.paramsMap["cell"]["secListTest"] = []
            #
            # # valid pointps rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'pointps': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['pointps']['Izhi'] = {'mod':'Izhi2007b', 'C':1, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70}
            #
            # cellRule['secList'] = {'apicdend': ['soma','dend'], 'basaldend':['dend']}
            #
            # params.netParams.cellParams['validSecList'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["secListTest"].append(params)
            #
            # # valid pointps rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'pointps': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['pointps']['Izhi'] = {'mod':'Izhi2007b', 'C':1, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70}
            #
            # cellRule['secList'] = {'apicdend': ['somax','dend'], 'basaldend':['dend']}
            #
            # params.netParams.cellParams['invalidSecList1'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["secListTest"].append(params)
            #
            # # valid pointps rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'pointps': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['pointps']['Izhi'] = {'mod':'Izhi2007b', 'C':1, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70}
            #
            # cellRule['secList'] = {'apicdend': 'soma', 'basaldend':['dend']}
            #
            # params.netParams.cellParams['invalidSecList2'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["secListTest"].append(params)

            # secList test
            self.paramsMap["cell"]["spikeGenLocTest"] = []

            # # valid pointps rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'pointps': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['pointps']['Izhi'] = {'mod':'Izhi2007b', 'C':1, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70}
            #
            # cellRule['secs']['axon'] = {'geom': {}, 'topol': {}, 'mechs': {}}
            # cellRule['secs']['axon']['spikeGenLoc'] = 0.7
            #
            # params.netParams.cellParams['validSpikeGneLoc'] = cellRule # add dict with params for this pop
            # self.paramsMap["cell"]["spikeGenLocTest"].append(params)

            # valid pointps rule
            params = ParamsObj()

            cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            cellRule['secs']['soma'] = {'geom': {}, 'pointps': {}}                                                # soma params dict
            cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            cellRule['secs']['soma']['pointps']['Izhi'] = {'mod':'Izhi2007b', 'C':1, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}

            cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology
            cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70}

            cellRule['secs']['axon'] = {'geom': {}, 'topol': {}, 'mechs': {}}
            cellRule['secs']['axon']['spikeGenLoc'] = 1.7

            params.netParams.cellParams['invalidSpikeGneLoc'] = cellRule # add dict with params for this pop
            self.paramsMap["cell"]["spikeGenLocTest"].append(params)
            #
            #
            # # conn test
            # self.paramsMap["conn"]["preCondsTest"] = []
            #
            # # valid mechs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'inh',                   # target inh synapse
            #     'delay': 5}                         # delay
            #
            # params.netParams.connParams['validPreConds1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["preCondsTest"].append(params)
            #
            # # invalid conds rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': 2.3 , 'postConds': {'popLabel': 'hop'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'inh',                   # target inh synapse
            #     'delay': 5}                         # delay
            #
            # params.netParams.connParams['invalidPreConds1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["preCondsTest"].append(params)
            #
            # # conn test
            # self.paramsMap["conn"]["postCondsTest"] = []
            #
            # # invalid conds rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'inh',                   # target inh synapse
            #     'delay': 5}                         # delay
            #
            # params.netParams.connParams['validPostConds1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["postCondsTest"].append(params)
            #
            # # invalid conds rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': 2.3,
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'inh',                   # target inh synapse
            #     'delay': 5}                         # delay
            #
            # params.netParams.connParams['invalidPostConds1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["postCondsTest"].append(params)

            # loc (optional) - Location of target synaptic mechanism (e.g. 0.3)
            # If omitted, defaults to 0.5.
            # If have list of synMechs, can have single loc for all, or list of locs (one per synMech, e.g. for 2 synMechs: [0.4, 0.7]).
            # If have synsPerConn > 1, can have single loc for all, or list of locs (one per synapse, e.g. if synsPerConn = 3: [0.4, 0.5, 0.7])
            # If have both a list of synMechs and synsPerConn > 1, can have a 2D list for each synapse of each synMech (e.g. for 2 synMechs and synsPerConn = 3: [[0.2, 0.3, 0.5], [0.5, 0.6, 0.7]])

            # # conn test
            # self.paramsMap["conn"]["connsLocTest"] = []
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'loc' : 1,
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'inh',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5}                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['validConnsLoc0'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsLocTest"].append(params)
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'loc' : [0.5,0.7],
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': ['AMPA','NMDA'],                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5}                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['validConnsLoc1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsLocTest"].append(params)
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'loc' : [[0.2, 0.3, 0.5], [0.5, 0.6, 0.7]],
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': ['AMPA','NMDA'],                   # target inh synapse
            #     'synsPerConn': 3,
            #     'delay': 5}                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['validConnsLoc2'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsLocTest"].append(params)

            # # valid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'loc' : [[0.2, 0.3, 0.5], [0.5, 0.6, 0.7]],
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': ['AMPA','NMDA'],                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5}                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['invalidConnsLoc1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsLocTest"].append(params)
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'loc' : [[0.2, 0.3, 0.5], [0.5, 0.6, 0.7]],
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 3,
            #     'delay': 5}                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['invalidConnsLoc2'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsLocTest"].append(params)
            #
            # # invalid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'loc' : 1.5,
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'inh',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5}                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['invalidConnsLoc3'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsLocTest"].append(params)

            # # conn test
            # self.paramsMap["conn"]["connsWeightTest"] = []
            #
            # # valid weights rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight' : 1,
            #     'loc': 0.0,                      # weight of each connection
            #     'synMech': 'inh',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5}                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['validConnsWeight0'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsWeightTest"].append(params)
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight' : [0.5,0.7],
            #     'loc': 1.0,
            #     'synMech': ['AMPA','NMDA'],                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5}                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['validConnsWeight1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsWeightTest"].append(params)
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight' : [[0.2, 0.3, 0.5], [0.5, 0.6, 0.7]],
            #     'loc': 0.0,                      # weight of each connection
            #     'synMech': ['AMPA','NMDA'],                   # target inh synapse
            #     'synsPerConn': 3,
            #     'delay': 5}                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['validConnsWeight2'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsWeightTest"].append(params)
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight' : [[0.2, 0.3, 0.5], [0.5, 0.6, 0.7]],
            #     'loc': 0.0,                      # weight of each connection
            #     'synMech': ['AMPA','NMDA'],                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5}                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['invalidConnsWeight1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsWeightTest"].append(params)
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight' : [[0.2, 0.3, 0.5], [0.5, 0.6, 0.7]],
            #     'loc': 0.0,                      # weight of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 3,
            #     'delay': 5}                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['invalidConnsWeight2'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsWeightTest"].append(params)
            #
            # # invalid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight' : 1.5,
            #     'loc': 0.0,                      # weight of each connection
            #     'synMech': 'inh',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5}                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['invalidConnsWeight3'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsWeightTest"].append(params)
            # # conn test
            # self.paramsMap["conn"]["connsDelayTest"] = []
            #
            # # valid weights rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'delay' : 1,
            #     'loc': 0.0,                      # weight of each connection
            #     'synMech': 'inh',                   # target inh synapse
            #     'synsPerConn': 1,
            #     }                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['validconnsDelay0'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsDelayTest"].append(params)
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'delay' : [0.5,0.7],
            #     'loc': 1.0,
            #     'synMech': ['AMPA','NMDA'],                   # target inh synapse
            #     'synsPerConn': 1,
            #     }                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['validconnsDelay1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsDelayTest"].append(params)
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'delay' : [[0.2, 0.3, 0.5], [0.5, 0.6, 0.7]],
            #     'loc': 0.0,                      # delay of each connection
            #     'synMech': ['AMPA','NMDA'],                   # target inh synapse
            #     'synsPerConn': 3,
            #     }                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['validconnsDelay2'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsDelayTest"].append(params)
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'delay' : [[0.2, 0.3, 0.5], [0.5, 0.6, 0.7]],
            #     'loc': 0.0,                      # delay of each connection
            #     'synMech': ['AMPA','NMDA'],                   # target inh synapse
            #     'synsPerConn': 1,
            #     }                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['invalidconnsDelay1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsDelayTest"].append(params)
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'delay' : [[0.2, 0.3, 0.5], [0.5, 0.6, 0.7]],
            #     'loc': 0.0,                      # delay of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 3,
            #     }                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['invalidconnsDelay2'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsDelayTest"].append(params)
            #
            # # invalid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'delay' : 1.5,
            #     'loc': 0.0,                      # weight of each connection
            #     'synMech': 'inh',                   # target inh synapse
            #     'synsPerConn': 1,
            #     }                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['invalidconnsDelay3'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsDelayTest"].append(params)

            #
            # # conn test
            # self.paramsMap["conn"]["synMechsTest"] = []
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'loc' : [0.5,0.7],
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5}                         # delay
            #
            # params.netParams.connParams['validSynMechs1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["synMechsTest"].append(params)
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'loc' : [[0.2, 0.3, 0.5], [0.5, 0.6, 0.7]],
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': ['AMPA','NMDA'],                   # target inh synapse
            #     'synsPerConn': 3,
            #     'delay': 5}                         # delay
            #
            # params.netParams.connParams['validSynMechs1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["synMechsTest"].append(params)
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'loc' : [[0.2, 0.3, 0.5], [0.5, 0.6, 0.7]],
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'XYZ',                   # target inh synapse
            #     'synsPerConn': 3,
            #     'delay': 5}                         # delay
            #
            # params.netParams.connParams['invalidSynMechs1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["synMechsTest"].append(params)
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'loc' : [[0.2, 0.3, 0.5], [0.5, 0.6, 0.7]],
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': ['XYZ','ABC'],                   # target inh synapse
            #     'synsPerConn': 3,
            #     'delay': 5}                         # delay
            #
            # params.netParams.connParams['invalidSynMechs2'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["synMechsTest"].append(params)

            # # conn test
            # self.paramsMap["conn"]["popLabelsTest"] = []
            #
            # # valid pop labels rule
            # params = ParamsObj()
            #
            # params.netParams.popParams['popLabel1'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50}     # add dict with params for this pop
            # params.netParams.popParams['popLabel2'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50}     # add dict with params for this pop
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'popLabel1'}, 'postConds': {'popLabel': 'popLabel2'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'inh',                   # target inh synapse
            #     'delay': 5}                         # delay
            #
            # params.netParams.connParams['validPopLabels1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["popLabelsTest"].append(params)
            #
            # # valid pop labels rule
            # params = ParamsObj()
            #
            # params.netParams.popParams['popLabel1'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50}     # add dict with params for this pop
            # params.netParams.popParams['popLabel2'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50}     # add dict with params for this pop
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'popLabel2'}, 'postConds': {'popLabel': 'popLabel3'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'inh',                   # target inh synapse
            #     'delay': 5}                         # delay
            #
            # params.netParams.connParams['invalidPopLabels1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["popLabelsTest"].append(params)
            # # conn test
            # self.paramsMap["conn"]["popLabelsTest"] = []

            # # valid pop labels rule
            # params = ParamsObj()
            #
            # params.netParams.popParams['popLabel1'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50}     # add dict with params for this pop
            # params.netParams.popParams['popLabel2'] = {'cellType': 'PYR', 'cellModel': 'HH', 'density' : 0.8, 'numCells': 50}     # add dict with params for this pop
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'popLabel1'}, 'postConds': {'popLabel': 'popLabel2'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'inh',                   # target inh synapse
            #     'delay': 5}                         # delay
            #
            # params.netParams.connParams['validPopLabels1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["popLabelsTest"].append(params)

            # # conn test
            # self.paramsMap["conn"]["secListTest"] = []
            #
            # # valid pop labels rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl1': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 										# dend mechanisms
            #
            # cellRule['secList'] = {'apicdend': ['soma','dend'], 'basaldend':['dend']}
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'popLabel2'}, 'postConds': {'popLabel': 'popLabel3'},
            #     'sec': 'apicdend',
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'inh',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5}                         # delay
            #
            # params.netParams.cellParams["cellParams1"] = cellRule
            #
            # params.netParams.connParams['validSecList1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["secListTest"].append(params)
            #
            # # valid pop labels rule
            # params = ParamsObj()
            #
            # cellRule = {'conds': {'cellModel': 'HH'},  'secs': {}}                        # cell rule dict
            # cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
            # cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
            # cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl1': 0.003, 'el': -70}  # soma hh mechanism
            #
            # cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
            # cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
            # cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology
            # cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 										# dend mechanisms
            #
            # cellRule['secList'] = {'apicdend': ['soma','dend'], 'basaldend':['dend']}
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'popLabel2'}, 'postConds': {'popLabel': 'popLabel3'},
            #     'sec': 'apicdend1',
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'inh',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5}                         # delay
            #
            # params.netParams.cellParams["cellParams1"] = cellRule
            #
            # params.netParams.connParams['invalidSecList1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["secListTest"].append(params)
            #
            # # conn test
            # self.paramsMap["conn"]["connListTest"] = []
            #
            # # valid pop labels rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'connList' : [[0,1],[2,1]],
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': ['AMPA','NMDA'],                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5}                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['validConnsLoc1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connListTest"].append(params)
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'connList' : [[[0.1,0.2], [0.1,0.3], [0.1,0.5]], [[0.5,0.1], [0.1,0.6], [0.1,0.7]]],
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': ['AMPA','NMDA'],                   # target inh synapse
            #     'synsPerConn': 3,
            #     'delay': 5}                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['validConnsLoc2'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsLocTest"].append(params)
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'connList' : [0.1,0.2],
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5}                         # delay
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['validConnsLoc3'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsLocTest"].append(params)
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'connList' : [[[0.1,0.2], [0.1,0.3], [0.1,0.5]], [[0.5,0.1], [0.1,0.6], [0.1,0.7]]],
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': ['AMPA','NMDA'],                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5}
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['invalidConnsLoc1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsLocTest"].append(params)
            #
            # # valid locs rule
            # params = ParamsObj()
            #
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'connList' : [[0.1,0.2], [0.1,0.3]],
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5}
            #
            # # Synaptic mechanism parameters
            # params.netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
            # params.netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
            # params.netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
            # params.netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
            #
            # params.netParams.connParams['invalidConnsLoc2'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsLocTest"].append(params)
            #
            # self.paramsMap["conn"]["connsHierarchyTest"] = []
            #
            # params = ParamsObj()
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5,
            #     'probability':0.5,
            #     'shape': {'switchOnOff': [200, 800], 'pulseType': 'square', 'pulsePeriod': 100, 'pulseWidth': 50},
            #     }
            #
            # params.netParams.connParams['validHierarchy1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsHierarchyTest"].append(params)
            #
            # params = ParamsObj()
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5,
            #     'probability':0.5,
            #     'convergence': 0.5,
            #     }
            #
            # params.netParams.connParams['invalidHierarchy1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsHierarchyTest"].append(params)
            #
            # params = ParamsObj()
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5,
            #     'convergence': 0.5,
            #     'divergence':0.5,
            #     }
            #
            # params.netParams.connParams['invalidHierarchy2'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsHierarchyTest"].append(params)
            #
            # self.paramsMap["conn"]["connsShapeTest"] = []
            #
            # params = ParamsObj()
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5,
            #     'shape': {'switchOnOff': [200, 800], 'pulseType': 'square', 'pulsePeriod': 100, 'pulseWidth': 50},
            #     }
            #
            # params.netParams.connParams['validShape1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsShapeTest"].append(params)
            #
            # params = ParamsObj()
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5,
            #     'shape': {'switchOnOff': 200, 'pulseType': 'square', 'pulsePeriod': 100, 'pulseWidth': 50},
            #     }
            #
            # params.netParams.connParams['invalidShape1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsShapeTest"].append(params)
            #
            # params = ParamsObj()
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5,
            #     'shape': {'switchOnOff': ['200','300'], 'pulseType': 'square', 'pulsePeriod': 100, 'pulseWidth': 50},
            #     }
            #
            # params.netParams.connParams['invalidShape2'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsShapeTest"].append(params)
            #
            # self.paramsMap["conn"]["connsPlasticityTest"] = []
            #
            # params = ParamsObj()
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5,
            #     'plasticity': {'mech': 'STDP', 'params': {'hebbwt': 0.01, 'antiwt':-0.01, 'wmax': 50, 'RLon': 1 ,'tauhebb': 10}},
            #     }
            #
            # params.netParams.connParams['validPlasticity1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsPlasticityTest"].append(params)
            #
            # params = ParamsObj()
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5,
            #     'plasticity': { 'params': {'hebbwt': 0.01, 'antiwt':-0.01, 'wmax': 50, 'RLon': 1 ,'tauhebb': 10}},
            #     }
            #
            # params.netParams.connParams['invalidPlasticity1'] = connRule # add dict with params for this pop
            # self.paramsMap["conn"]["connsPlasticityTest"].append(params)

            # self.paramsMap["stimSource"]["stimSourceTest"] = []
            #
            # params = ParamsObj()
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5,
            #     'plasticity': { 'params': {'hebbwt': 0.01, 'antiwt':-0.01, 'wmax': 50, 'RLon': 1 ,'tauhebb': 10}},
            #     }
            #
            # params.netParams.stimSourceParams['Input_1'] =  {'type': 'IClamp', 'delay': 10, 'dur': 800, 'amp': 'uniform(0.05,0.5)'}
            # params.netParams.stimSourceParams['Input_2'] = {'type': 'VClamp', 'dur':[0,1,1], 'amp':[1,1,1],'gain':1, 'rstim':0, 'tau1':1, 'tau2':1, 'i':1}
            # params.netParams.stimSourceParams['Input_3'] = {'type': 'AlphaSynapse', 'onset': 'uniform(1,500)', 'tau': 5, 'gmax': 'post_ynorm', 'e': 0}
            # params.netParams.stimSourceParams['Input_4'] = {'type': 'NetStim', 'interval': 'uniform(20,100)', 'number': 1000, 'start': 5, 'noise': 0.1}
            #
            # # Stimulation mapping parameters
            # params.netParams.stimTargetParams['Input1->PYR'] = {
            #     'source': 'Input_1',
            #     'sec':'soma',
            #     'loc': 0.5,
            #     'conds': {'pop':'PYR', 'cellList': range(8)}}
            # params.netParams.stimTargetParams['Input3->Basket'] = {
            #     'source': 'Input_3',
            #     'sec':'soma',
            #     'loc': 0.5,
            #     'conds': {'cellType':'Basket'}}
            # params.netParams.stimTargetParams['Input4->PYR3'] = {
            #         'source': 'Input_4',
            #         'sec':'soma',
            #         'loc': 0.5,
            #     'weight': '0.1+gauss(0.2,0.05)',
            #     'delay': 1,
            #         'conds': {'pop':'PYR3', 'cellList': [0,1,2,5,10,14,15]}}
            #
            # params.netParams.connParams['validStimSource1'] = connRule # add dict with params for this pop
            # self.paramsMap["stimSource"]["stimSourceTest"].append(params)
            #
            # params = ParamsObj()
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5,
            #     'plasticity': { 'params': {'hebbwt': 0.01, 'antiwt':-0.01, 'wmax': 50, 'RLon': 1 ,'tauhebb': 10}},
            #     }
            #
            # params.netParams.stimSourceParams['Input_1'] =  {'type': 'XYClamp', 'delay': 10, 'dur': 800, 'amp': 'uniform(0.05,0.5)'}
            # params.netParams.stimSourceParams['Input_2'] = {'type': 'VClamp', 'dur':[0,1,1], 'amp':[1,1,1],'gain':1, 'rstim':0, 'tau1':1, 'tau2':1, 'i':1}
            # params.netParams.stimSourceParams['Input_3'] = {'type': 'AlphaSynapse', 'onset': 'uniform(1,500)', 'tau': 5, 'gmax': 'post_ynorm', 'e': 0}
            # params.netParams.stimSourceParams['Input_4'] = {'type': 'NetStim', 'interval': 'uniform(20,100)', 'number': 1000, 'start': 5, 'noise': 0.1}
            #
            # # Stimulation mapping parameters
            # params.netParams.stimTargetParams['Input1->PYR'] = {
            #     'source': 'Input_1',
            #     'sec':'soma',
            #     'loc': 0.5,
            #     'conds': {'pop':'PYR', 'cellList': range(8)}}
            # params.netParams.stimTargetParams['Input3->Basket'] = {
            #     'source': 'Input_3',
            #     'sec':'soma',
            #     'loc': 0.5,
            #     'conds': {'cellType':'Basket'}}
            # params.netParams.stimTargetParams['Input4->PYR3'] = {
            #         'source': 'Input_4',
            #         'sec':'soma',
            #         'loc': 0.5,
            #     'weight': '0.1+gauss(0.2,0.05)',
            #     'delay': 1,
            #         'conds': {'pop':'PYR3', 'cellList': [0,1,2,5,10,14,15]}}
            #
            # params.netParams.connParams['invalidStimSource1'] = connRule # add dict with params for this pop
            # self.paramsMap["stimSource"]["stimSourceTest"].append(params)
            #
            # self.paramsMap["stimTarget"]["stimTargetTest"] = []
            #
            # params = ParamsObj()
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5,
            #     'plasticity': { 'params': {'hebbwt': 0.01, 'antiwt':-0.01, 'wmax': 50, 'RLon': 1 ,'tauhebb': 10}},
            #     }
            #
            # params.netParams.stimSourceParams['Input_1'] =  {'type': 'IClamp', 'delay': 10, 'dur': 800, 'amp': 'uniform(0.05,0.5)'}
            # params.netParams.stimSourceParams['Input_2'] = {'type': 'VClamp', 'dur':[0,1,1], 'amp':[1,1,1],'gain':1, 'rstim':0, 'tau1':1, 'tau2':1, 'i':1}
            # params.netParams.stimSourceParams['Input_3'] = {'type': 'AlphaSynapse', 'onset': 'uniform(1,500)', 'tau': 5, 'gmax': 'post_ynorm', 'e': 0}
            # params.netParams.stimSourceParams['Input_4'] = {'type': 'NetStim', 'interval': 'uniform(20,100)', 'number': 1000, 'start': 5, 'noise': 0.1}
            #
            # # Stimulation mapping parameters
            # params.netParams.stimTargetParams['Input1->PYR'] = {
            #     'source': 'Input_1',
            #     'sec':'soma',
            #     'loc': 0.5,
            #     'conds': {'pop':'PYR', 'cellList': range(8)}}
            # params.netParams.stimTargetParams['Input3->Basket'] = {
            #     'source': 'Input_3',
            #     'sec':'soma',
            #     'loc': 0.5,
            #     'conds': {'cellType':'Basket'}}
            # params.netParams.stimTargetParams['Input4->PYR3'] = {
            #         'source': 'Input_4',
            #         'sec':'soma',
            #         'loc': 0.5,
            #     'weight': '0.1+gauss(0.2,0.05)',
            #     'delay': 1,
            #         'conds': {'pop':'PYR3', 'cellList': [0,1,2,5,10,14,15]}}
            #
            # params.netParams.connParams['validStimTarget1'] = connRule # add dict with params for this pop
            # self.paramsMap["stimTarget"]["stimTargetTest"].append(params)
            #
            # params = ParamsObj()
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5,
            #     'plasticity': { 'params': {'hebbwt': 0.01, 'antiwt':-0.01, 'wmax': 50, 'RLon': 1 ,'tauhebb': 10}},
            #     }
            #
            # params.netParams.stimSourceParams['Input_1'] =  {'type': 'IClamp', 'delay': 10, 'dur': 800, 'amp': 'uniform(0.05,0.5)'}
            # params.netParams.stimSourceParams['Input_2'] = {'type': 'VClamp', 'dur':[0,1,1], 'amp':[1,1,1],'gain':1, 'rstim':0, 'tau1':1, 'tau2':1, 'i':1}
            # params.netParams.stimSourceParams['Input_3'] = {'type': 'AlphaSynapse', 'onset': 'uniform(1,500)', 'tau': 5, 'gmax': 'post_ynorm', 'e': 0}
            # params.netParams.stimSourceParams['Input_4'] = {'type': 'NetStim', 'interval': 'uniform(20,100)', 'number': 1000, 'start': 5, 'noise': 0.1}
            #
            # # Stimulation mapping parameters
            # params.netParams.stimTargetParams['Input1->PYR'] = {
            #     'source': 'Input_1',
            #     'sec':'soma',
            #     'loc': 0.5,
            #     'conds': {'pop':'PYR', 'cellList': range(8)}}
            # params.netParams.stimTargetParams['Input3->Basket'] = {
            #     'source': 'Input_3',
            #     'sec':'soma',
            #     'loc': 0.5,
            #     'conds': {'cellType':'Basket'}}
            # params.netParams.stimTargetParams['Input4->PYR3'] = {
            #         'source': 'Input_4',
            #         'sec':'soma',
            #         'loc': 0.5,
            #     'weight': '0.1+gauss(0.2,0.05)',
            #     'delay': 1,
            #         'conds': {'pop':'PYR3', 'cellList': [0,1,2,5,10,14,15]}}
            #
            # params.netParams.connParams['validStimTarget1'] = connRule # add dict with params for this pop
            # self.paramsMap["stimTarget"]["stimTargetTest"].append(params)
            #
            # params = ParamsObj()
            # # Connectivity parameters
            # connRule = {
            #     'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
            #     'weight': 0.0,                      # weight of each connection
            #     'synMech': 'AMPA',                   # target inh synapse
            #     'synsPerConn': 1,
            #     'delay': 5,
            #     'plasticity': { 'params': {'hebbwt': 0.01, 'antiwt':-0.01, 'wmax': 50, 'RLon': 1 ,'tauhebb': 10}},
            #     }
            #
            # params.netParams.stimSourceParams['Input_1'] =  {'type': 'IClamp', 'delay': 10, 'dur': 800, 'amp': 'uniform(0.05,0.5)'}
            # params.netParams.stimSourceParams['Input_2'] = {'type': 'VClamp', 'dur':[0,1,1], 'amp':[1,1,1],'gain':1, 'rstim':0, 'tau1':1, 'tau2':1, 'i':1}
            # params.netParams.stimSourceParams['Input_3'] = {'type': 'AlphaSynapse', 'onset': 'uniform(1,500)', 'tau': 5, 'gmax': 'post_ynorm', 'e': 0}
            # params.netParams.stimSourceParams['Input_4'] = {'type': 'NetStim', 'interval': 'uniform(20,100)', 'number': 1000, 'start': 5, 'noise': 0.1}
            #
            # # Stimulation mapping parameters
            # params.netParams.stimTargetParams['Input1->PYR'] = {
            #     'source': 'Input_11',
            #     'sec':'soma',
            #     'loc': 0.5,
            #     'conds': {'pop':'PYR', 'cellList': range(8)}}
            # params.netParams.stimTargetParams['Input3->Basket'] = {
            #     'source': 'Input_3',
            #     'sec':'soma',
            #     'loc': 0.5,
            #     'conds': {'cellType':'Basket'}}
            # params.netParams.stimTargetParams['Input4->PYR3'] = {
            #         'source': 'Input_4',
            #         'sec':'soma',
            #         'loc': 0.5,
            #     'weight': '0.1+gauss(0.2,0.05)',
            #     'delay': 1,
            #         'conds': {'pop':'PYR3', 'cellList': [0,1,2,5,10,14,15]}}
            #
            # params.netParams.connParams['invalidStimTarget1'] = connRule # add dict with params for this pop
            # self.paramsMap["stimTarget"]["stimTargetTest"].append(params)

        def runTestsWithParams(self):

            #self.runPopTestsWithParams()
            self.runNetTestsWithParams()
            #self.runCellTestsWithParams()
            #self.runConnTestsWithParams()
            #self.runStimSourceTests()
            #self.runStimTargetTests()

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
            #print ( " run cell tests ")
            cellParamsMap = self.paramsMap["cell"]
            # run the different tests for cell
            for testName, paramObjList in cellParamsMap.items():
                for paramsObj in paramObjList:
                    self.netPyneTestObj.netParams = paramsObj.netParams
                    self.netPyneTestObj.runTests()

        def runConnTestsWithParams(self):
            #print ( " #### running conn tests " )
            connParamsMap = self.paramsMap["conn"]
            print (" connParamsMap = " + str(connParamsMap))
            # run the different tests for conn
            for testName, paramObjList in connParamsMap.items():
                for paramsObj in paramObjList:
                    #print ( " calling tests")
                    self.netPyneTestObj.netParams = paramsObj.netParams
                    self.netPyneTestObj.runTests()

        def runStimSourceTests(self):
            #print ( " running conn tests " )
            stimSourceParamsMap = self.paramsMap["stimSource"]
            # run the different tests for conn
            for testName, paramObjList in stimSourceParamsMap.items():
                for paramsObj in paramObjList:
                    #print ( " calling tests")
                    self.netPyneTestObj.netParams = paramsObj.netParams
                    self.netPyneTestObj.runTests()

        def runStimTargetTests(self):
            #print ( " running conn tests " )
            stimTargetParamsMap = self.paramsMap["stimTarget"]
            # run the different tests for conn
            for testName, paramObjList in stimTargetParamsMap.items():
                for paramsObj in paramObjList:
                    #print ( " calling tests")
                    self.netPyneTestObj.netParams = paramsObj.netParams
                    self.netPyneTestObj.runTests()

runNetPyneTests = RunNetPyneTests()
#runNetPyneTests.runTestsWithParams()
