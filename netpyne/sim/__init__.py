"""
Package for handling simulations

Contains all the model shared variables and modules.  It is imported as "sim" from all other files, so any variable or module can be referenced from any module using `sim.varName`.

"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# check for -nogui option
from future import standard_library
standard_library.install_aliases()
import sys
if '-nogui' in sys.argv:
    import netpyne
    netpyne.__gui__ = False


# import NEURON module
from neuron import h
try:
    h.nrnmpi_init()
pass:
    pass

#------------------------------------------------------------------------------
# Import simulation-related functions from this subpackage (/sim)
#------------------------------------------------------------------------------

# import setup functions
from .setup import initialize, setNet, setNetParams, setSimCfg, createParallelContext, \
	readCmdLineArgs, setupRecording, setupRecordLFP, setGlobals

# import run functions
from .run import preRun, runSim, runSimWithIntervalFunc, loadBalance, calculateLFP

# import gather functions
from .gather import gatherData, _gatherAllCellTags, _gatherAllCellConnPreGids, _gatherCells, fileGather

# import saving functions
from .save import saveJSON, saveData, distributedSaveHDF5, compactConnFormat, intervalSave, saveSimDataInNode, saveInNode

# import loading functions
from .load import loadSimCfg, loadNetParams, loadNet, loadSimData, loadAll, loadHDF5, ijsonLoad

# import utils functions (general)
from .utils import cellByGid, getCellsList, timing, version, gitChangeset, hashStr, hashList,\
	_init_stim_randomizer, unique, checkMemory 

# import utils functions to manipulate objects
from .utils import copyReplaceItemObj, copyRemoveItemObj, replaceFuncObj, replaceDictODict, \
	rename, clearObj, clearAll


# import wrapper functions
from .wrappers import create, simulate, intervalSimulate, analyze, createSimulate, \
	createSimulateAnalyze, intervalCreateSimulateAnalyze, load, loadSimulate, loadSimulateAnalyze, \
	createExportNeuroML2, importNeuroML2SimulateAnalyze
     

#------------------------------------------------------------------------------
# Import classes and functions from other subpackages (so available via sim)
#------------------------------------------------------------------------------

# import cell classes
from ..cell import CompartCell, PointCell, NML2Cell, NML2SpikeSource

# import Network and Pop classes
from ..network import Network, Pop

# import analysis-related module
from .. import analysis

# import testing related functions
from .. import tests
from ..tests.checks import checkOutput
from ..tests.tests import SimTestObj

# import export/import-related functions
from .. import conversion 
from ..conversion.neuromlFormat import * 
