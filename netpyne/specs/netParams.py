"""
Module containing classes for high-level network parameters and methods

"""

from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from builtins import next
from builtins import open
from builtins import range

# required to make json saving work in Python 2/3
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from future import standard_library
standard_library.install_aliases()
from collections import OrderedDict
from .dicts import Dict, ODict
from .. import conversion
from netpyne.logger import logger

# ----------------------------------------------------------------------------
# PopParams class
# ----------------------------------------------------------------------------

class PopParams(ODict):
    """
    Class to hold population parameters

    """


    def setParam(self, label, param, value):
        if label in self:
            d = self[label]
        else:
            return False

        dimParams = ['numCells', 'density', 'gridSpacing']
        if param in dimParams:
            for removeParam in dimParams: d.pop(removeParam, None)  # remove other properties

        d[param] = value

        return True

    def rename(self, old, new, label=None):
        return self.__rename__(old, new, label)


# ----------------------------------------------------------------------------
# CellParams class
# ----------------------------------------------------------------------------

class CellParams(ODict):
    """
    Class to hold cell parameters

    """


    def setParam(self, label, param, value):
        if label in self:
            d = self[label]
        else:
            return False

        d[param] = value

        return True

    def rename(self, old, new, label=None):
        success = self.__rename__(old, new, label)

        try:
            # special case: renaming cellParams[x]['secs'] requires updating topology
            if isinstance(label, (list, tuple)) and 'secs' in self[label[0]]:
                d = self[label[0]]
                for sec in list(d['secs'].values()):  # replace appearences in topol
                    if sec['topol'].get('parentSec') == old:
                        sec['topol']['parentSec'] = new
            return success
        except:
            return False


# ----------------------------------------------------------------------------
# ConnParams class
# ----------------------------------------------------------------------------

class ConnParams(ODict):
    """
    Class to hold connectivity parameters

    """


    def setParam(self, label, param, value):
        if label in self:
            d = self[label]
        else:
            return False

        d[param] = value

        return True

    def rename(self, old, new, label=None):
        return self.__rename__(old, new, label)


# ----------------------------------------------------------------------------
# SynMechParams class
# ----------------------------------------------------------------------------

class SynMechParams(ODict):
    """
    Class to hold synaptic mechanism parameters

    """


    def setParam(self, label, param, value):
        if label in self:
            d = self[label]
        else:
            return False

        d[param] = value

        return True

    def rename(self, old, new, label=None):
        return self.__rename__(old, new, label)


# ----------------------------------------------------------------------------
# SubConnParams class
# ----------------------------------------------------------------------------

class SubConnParams(ODict):
    """
    Class to hold subcellular connectivity parameters

    """


    def setParam(self, label, param, value):
        if label in self:
            d = self[label]
        else:
            return False

        d[param] = value

        return True

    def rename(self, old, new, label=None):
        return self.__rename__(old, new, label)


# ----------------------------------------------------------------------------
# StimSourceParams class
# ----------------------------------------------------------------------------

class StimSourceParams(ODict):
    """
    Class to hold stimulation source parameters

    """


    def setParam(self, label, param, value):
        if label in self:
            d = self[label]
        else:
            return False

        d[param] = value

        return True

    def rename(self, old, new, label=None):
        return self.__rename__(old, new, label)


# ----------------------------------------------------------------------------
# StimTargetParams class
# ----------------------------------------------------------------------------

class StimTargetParams(ODict):
    """
    Class to hold stimulation target parameters

    """


    def setParam(self, label, param, value):
        if label in self:
            d = self[label]
        else:
            return False

        d[param] = value

        return True

    def rename(self, old, new, label=None):
        return self.__rename__(old, new, label)


# ----------------------------------------------------------------------------
# RxD class
# ----------------------------------------------------------------------------

class RxDParams(ODict):
    """
    Class to hold reaction-diffusion (RxD) parameters

    """


    def setParam(self, label, param, value):
        if label in self:
            d = self[label]
        else:
            return False

        d[param] = value

        return True

    def rename(self, old, new, label=None):
        return self.__rename__(old, new, label)

# ----------------------------------------------------------------------------
# NETWORK PARAMETERS CLASS
# ----------------------------------------------------------------------------

class NetParams(object):
    """
    Class to hold all network parameters

    """



    def __init__(self, netParamsDict=None):
        self._labelid = 0
        # General network parameters
        self.scale = 1   # scale factor for number of cells
        self.sizeX = 100 # x-dimension (horizontal length) size in um
        self.sizeY = 100 # y-dimension (vertical height or cortical depth) size in um
        self.sizeZ = 100 # z-dimension (horizontal depth) size in um
        self.shape = 'cuboid' # network shape ('cuboid', 'cylinder' or 'ellipsoid')
        self.rotateCellsRandomly = False # random rotation of cells around y-axis [min,max] radians, e.g. [0, 3.0]
        self.defineCellShapes = False # convert stylized cell geometries to 3d points (calls h.define_shape)
        self.correctBorder = False  # distance (um) from which to correct connectivity border effect, [x,y,z] eg. [100,150,150]
        self.cellsVisualizationSpacingMultiplier = [1, 1, 1]  # x,y,z scaling factor for spacing between cells during visualization

        ## General connectivity parameters
        self.scaleConnWeight = 1 # Connection weight scale factor (NetStims not included)
        self.scaleConnWeightNetStims = 1 # Connection weight scale factor for NetStims
        self.scaleConnWeightModels = False # Connection weight scale factor for each cell model eg. {'Izhi2007': 0.1, 'Friesen': 0.02}
        self.defaultWeight = 1  # default connection weight
        self.defaultDelay = 1  # default connection delay (ms)
        self.defaultThreshold = 10  # default Netcon threshold (mV)
        self.propVelocity = 500.0  # propagation velocity (um/ms)

        # Cell params dict
        self.cellParams = CellParams()

        # Population params dict
        self.popParams = PopParams()  # create list of populations - each item will contain dict with pop params
        self.popTagsCopiedToCells = ['cellModel', 'cellType']

        # Synaptic mechanism params dict
        self.synMechParams = SynMechParams()

        # Connectivity params dict
        self.connParams = ConnParams()

        # Subcellular connectivity params dict
        self.subConnParams = SubConnParams()

        # Stimulation source and target params dicts
        self.stimSourceParams = StimSourceParams()
        self.stimTargetParams = StimTargetParams()

        # RxD params dicts
        self.rxdParams = RxDParams()

        # fill in params from dict passed as argument
        if netParamsDict:
            netParamsComponents = ['cellParams', 'popParams', 'synMechParams', 'connParams', 'subConnParams', 'stimSourceParams', 'stimTargetParams', 'rxdParams']
            for k,v in netParamsDict.items():
                if k in netParamsComponents:
                    for k2, v2 in netParamsDict[k].items():
                        if isinstance(v2, OrderedDict):
                            getattr(self, k)[k2] = ODict(v2)
                        elif isinstance(v2, dict):
                            getattr(self, k)[k2] = ODict(v2)
                        else:
                            getattr(self, k)[k2] = v2
                elif isinstance(v, OrderedDict):
                    setattr(self, k, ODict(v))
                elif isinstance(v, dict):
                    setattr(self, k, Dict(v))
                else:
                    setattr(self, k, v)

    def save(self, filename):
        import os
        from .. import sim
        basename = os.path.basename(filename)
        folder = filename.split(basename)[0]
        ext = basename.split('.')[1]

        # make dir
        try:
            os.mkdir(folder)
        except OSError:
            if not os.path.exists(folder):
                logger.warning(' Could not create ' + folder)

        dataSave = {'net': {'params': self.__dict__}}

        # Save to json file
        if ext == 'json':
            logger.info('Saving netParams to %s ... ' % (filename))
            sim.saveJSON(filename, dataSave)

    def addCellParams(self, label=None, params=None):
        if not label:
            label = int(self._labelid)
            self._labelid += 1
        self.cellParams[label] = Dict(params)

    def addPopParams(self, label=None, params=None):
        if not label:
            label = int(self._labelid)
            self._labelid += 1
        self.popParams[label] = Dict(params)

    def addSynMechParams(self, label=None, params=None):
        if not label:
            label = int(self._labelid)
            self._labelid += 1
        self.synMechParams[label] = Dict(params)

    def addConnParams(self, label=None, params=None):
        if not label:
            label = int(self._labelid)
            self._labelid += 1
        self.connParams[label] = Dict(params)

    def addSubConnParams(self, label=None, params=None):
        if not label:
            label = int(self._labelid)
            self._labelid += 1
        self.subConnParams[label] = Dict(params)

    def addStimSourceParams(self, label=None, params=None):
        if not label:
            label = int(self._labelid)
            self._labelid += 1
        self.stimSourceParams[label] = Dict(params)

    def addStimTargetParams(self, label=None, params=None):
        if not label:
            label = int(self._labelid)
            self._labelid += 1
        self.stimTargetParams[label] = Dict(params)

    # def rename(self, attr, old, new):
    #     try:
    #         obj = getattr(self, attr)
    #     except:
    #         logger.warning 'Error renaming: netParams does not contain %s' % (attr)
    #         return False

    #     if old not in obj:
    #         logger.warning 'Error renaming: netParams.%s rule does not contain %s' % (attribute, old)
    #         return False

    #     obj[new] = obj.pop(old)  # replace

    #     return True


    def importCellParams(self, label, fileName, cellName, conds={}, cellArgs=None, importSynMechs=False, somaAtOrigin=True, cellInstance=False):
        if cellArgs is None: cellArgs = {}
        if not label:
            label = int(self._labelid)
            self._labelid += 1
        secs, secLists, synMechs, globs = conversion.importCell(fileName, cellName, cellArgs, cellInstance)
        cellRule = {'conds': conds, 'secs': secs, 'secLists': secLists, 'globals': globs}

        # adjust cell 3d points so that soma is at location 0,0,0
        if somaAtOrigin:
            somaSec = next((sec for sec in cellRule['secs'] if 'soma' in sec), None)
            if not somaSec or not 'pt3d' in cellRule['secs'][somaSec]['geom']:
                pass
                #logger.warning('Cannot place soma at origin because soma does not exist or does not contain pt3d')
            else:
                soma3d = cellRule['secs'][somaSec]['geom']['pt3d']
                midpoint = int(len(soma3d)/2)
                somaX, somaY, somaZ = soma3d[midpoint][0:3]
                for sec in list(cellRule['secs'].values()):
                    if 'pt3d' in sec['geom']:
                        for i,pt3d in enumerate(sec['geom']['pt3d']):
                            sec['geom']['pt3d'][i] = (pt3d[0] - somaX, pt3d[1] - somaY, pt3d[2] - somaZ, pt3d[3])

        self.addCellParams(label, cellRule)

        if importSynMechs:
            for synMech in synMechs: self.addSynMechParams(cellName+'_'+synMech.pop('label'), synMech)

        return self.cellParams[label]

    def importCellParamsFromNet(self, labelList, condsList, fileName, cellNameList, importSynMechs=False):
        conversion.importCellsFromNet(self, fileName, labelList, condsList, cellNameList, importSynMechs)
        return self.cellParams


    def addCellParamsSecList(self, label, secListName, somaDist=None, somaDistY=None):
        import numpy as np

        if label in self.cellParams:
            cellRule = self.cellParams[label]
        else:
            logger.warning('Error adding secList: netParams.cellParams does not contain %s' % (label))
            return

        if somaDist is not None and (not isinstance(somaDist, list) or len(somaDist) != 2):
            logger.warning('Error adding secList: somaDist should be a list with 2 elements')
            return

        if somaDistY is not None and (not isinstance(somaDistY, list) or len(somaDistY) != 2):
            logger.warning('Error adding secList: somaDistY should be a list with 2 elements')
            return


        secList = []
        for secName, sec in cellRule.secs.items():
            if 'pt3d' in sec['geom']:
                pt3d = sec['geom']['pt3d']
                midpoint = int(len(pt3d)/2)
                x,y,z = pt3d[midpoint][0:3]
                if somaDist:
                    distSec = np.linalg.norm(np.array([x,y,z]))
                    if distSec >= somaDist[0] and distSec <= somaDist[1]:
                        secList.append(secName)
                elif somaDistY:
                    if y >= somaDistY[0] and y <= somaDistY[1]:
                        secList.append(secName)

            else:
                logger.warning('Error adding secList: Sections do not contain 3d points')
                return

        cellRule.secLists[secListName] = list(secList)

    def swapCellParamsPt3d(self, label, origIndex, targetIndex):
        if label in self.cellParams:
            cellRule = self.cellParams[label]
        else:
            logger.warning('Error swapping 3d pts: netParams.cellParams does not contain %s' % (label))
            return

        if origIndex not in list(range(4)) and targetIndex not in list(range(4)): # check valid indices (x,y,z,d)
            logger.warning('Error swapping 3d pts: indices should be 0, 1, 2 or 3 (x,y,z,d)')
            return

        for sec in list(cellRule.secs.values()):
            if 'pt3d' in sec['geom']:
                pt3d = sec['geom']['pt3d']
                for i,pt in enumerate(pt3d): pt3d[i] = list(pt)
                for pt in pt3d:
                    tmp = float(pt[origIndex])
                    pt[origIndex] = float(pt[targetIndex])
                    pt[targetIndex] = tmp


    def renameCellParamsSec(self, label, oldSec, newSec):
        self.cellParams.rename(oldSec, newSec, (label, 'secs'))


    def addCellParamsWeightNorm(self, label, fileName, threshold=1000):
        import pickle, sys
        if label in self.cellParams:
            cellRule = self.cellParams[label]
        else:
            logger.warning('Error adding weightNorm: netParams.cellParams does not contain %s' % (label))
            return

        with open(fileName, 'rb') as fileObj:
            if sys.version_info[0] == 2:
                weightNorm = pickle.load(fileObj)
            else:
                weightNorm = pickle.load(fileObj, encoding='latin1')

        try:
            somaSec = next((k for k in list(weightNorm.keys()) if k.startswith('soma')),None)
            somaWeightNorm = weightNorm[somaSec][0]
        except:
            logger.warning('Error setting weightNorm: no soma section available to set threshold')
            return
        for sec, wnorm in weightNorm.items():
            if sec in cellRule['secs']:
                wnorm = [min(wn,threshold*somaWeightNorm) for wn in wnorm]
                cellRule['secs'][sec]['weightNorm'] = wnorm  # add weight normalization factors for each section


    def addCellParamsTemplate(self, label, conds={}, template=None):
        if label in self.cellParams:
            logger.info('CellParams key %s already exists...' % (label))
        secs = {}

        if template == 'Simple_HH':
            secs['soma'] = {'geom': {}, 'mechs': {}}
            secs['soma']['geom'] = {'diam': 20, 'L': 20, 'Ra': 100.0, 'cm': 1}
            secs['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.0003, 'el': -54.3}

        elif template == 'BallStick_HH':
            secs['soma'] = {'geom': {}, 'mechs': {}}
            secs['soma']['geom'] = {'diam': 12, 'L': 12, 'Ra': 100.0, 'cm': 1}
            secs['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.0003, 'el': -54.3}

            secs['dend'] = {'geom': {}, 'mechs': {}}
            secs['dend']['geom'] = {'diam': 1.0, 'L': 200.0, 'Ra': 100.0, 'cm': 1}
            secs['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}
            secs['dend']['mechs']['pas'] = {'g': 0.001, 'e': -70}

        self.cellParams[label] = ({'conds': conds, 'secs': secs})

    def saveCellParamsRule(self, label, fileName):
        import pickle, json, os

        ext = os.path.basename(fileName).split('.')[1]

        if label in self.cellParams:
            cellRule = self.cellParams[label]
        else:
            logger.warning('Error saving: netParams.cellParams does not contain %s' % (label))
            return

        if ext == 'pkl':
            with open(fileName, 'wb') as fileObj:
                pickle.dump(cellRule, fileObj)
        elif ext == 'json':
            from .. import sim
            sim.saveJSON(fileName, cellRule)


    def loadCellParamsRule(self, label, fileName):
        import pickle, json, os, sys

        ext = os.path.basename(fileName).split('.')[1]
        if ext == 'pkl':
            with open(fileName, 'rb') as fileObj:
                if sys.version_info[0] == 2:
                    cellRule = pickle.load(fileObj)
                else:
                    cellRule = pickle.load(fileObj, encoding='latin1')
        elif ext == 'json':
            with open(fileName, 'rb') as fileObj:
                cellRule = json.load(fileObj)

        self.cellParams[label] = cellRule

    def loadCellParams(self, label, fileName):
        return self.loadCellParamsRule(label, fileName)

    def saveCellParams(self, label, fileName):
        return self.saveCellParamsRule(label, fileName)
    def todict(self):
        from ..sim import replaceDictODict
        return replaceDictODict(self.__dict__)
