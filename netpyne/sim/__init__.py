"""
Package for handling simulations

Contains all the model shared variables and modules.  It is imported as "sim" from all other files, so any variable or module can be referenced from any module using `sim.varName`.

"""

# check for -nogui option
import sys
if '-nogui' in sys.argv:
    import netpyne

    netpyne.__gui__ = False
from neuron import h


# ------------------------------------------------------------------------------
# Import simulation-related functions from this subpackage (/sim)
# ------------------------------------------------------------------------------

# import setup functions
from .setup import (
    initialize,
    setNet,
    setNetParams,
    setSimCfg,
    createParallelContext,
    readCmdLineArgs,
    setupRecording,
    setupRecordLFP,
    setGlobals,
)

# import run functions
from .run import preRun, runSim, runSimWithIntervalFunc, loadBalance, calculateLFP, calculateDipole

# import gather functions
from .gather import gatherData, _gatherAllCellTags, _gatherAllCellConnPreGids, _gatherCells, gatherDataFromFiles

# import saving functions
from .save import saveJSON, saveData, distributedSaveHDF5, compactConnFormat, intervalSave, saveDataInNodes, saveModel

# import loading functions
from .load import (
    loadSimCfg,
    loadNetParams,
    loadNet,
    loadSimData,
    loadAll,
    loadHDF5,
    ijsonLoad,
    loadModel,
    loadFromIndexFile,
)

# import utils functions (general)
from .utils import (
    loadPythonModule,
    cellByGid,
    getCellsList,
    timing,
    version,
    gitChangeset,
    hashStr,
    hashList,
    _init_stim_randomizer,
    unique,
    checkMemory,
    close,
)

# import utils functions to manipulate objects
from .utils import copyReplaceItemObj, copyRemoveItemObj, replaceFuncObj, replaceDictODict, rename, clearObj, clearAll

# import wrapper functions
from .wrappers import (
    create,
    simulate,
    intervalSimulate,
    distributedSimulate,
    analyze,
    createSimulate,
    createSimulateAnalyze,
    createSimulateAnalyzeInterval,
    createSimulateAnalyzeDistributed,
    runFromIndexFile,
    load,
    loadSimulate,
    loadSimulateAnalyze,
    createExportNeuroML2,
    importNeuroML2SimulateAnalyze,
    runSimIntervalSaving,
)


# ------------------------------------------------------------------------------
# Import classes and functions from other subpackages (so available via sim)
# ------------------------------------------------------------------------------

# import cell classes
from ..cell import CompartCell, PointCell, NML2Cell, NML2SpikeSource

# import Network and Pop classes
from ..network import Network, Pop

# import analysis-related module
from .. import analysis

# import plotting-related module
from .. import plotting

# import testing related functions
from .. import tests
from ..tests.checks import checkOutput
from ..tests.tests import SimTestObj

# import export/import-related functions
from .. import conversion
from ..conversion.neuromlFormat import *

# comm imports
from netpyne.specs import _batch_specs
if _batch_specs is True:
    from netpyne.specs import comm
    send = comm.send
    end_comm = comm.close # send automatically closes comm now #TODO remove.
else:
    def send(*args, **kwargs):
        """
        This method is implemented in batchtools,
        which requires the batchtk package to be
        installed. If you are seeing this message
        when calling help, it indicates there is
        an issue with your current batchtools
        installation
        """
        pass

