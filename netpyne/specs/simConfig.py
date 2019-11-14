"""
specs/simConfig.py

SimConfig class includes simulation configuration parameters and methods

Contributors: salvadordura@gmail.com
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

# required to make json saving work in Python 2/3
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from builtins import open
from future import standard_library
standard_library.install_aliases()

from collections import OrderedDict
from .dicts import Dict, ODict


# ----------------------------------------------------------------------------
# SIMULATION CONFIGURATION CLASS
# ----------------------------------------------------------------------------

class SimConfig (object):

    def __init__(self, simConfigDict = None):
        # Simulation parameters
        self.duration = self.tstop = 1*1e3 # Duration of the simulation, in ms
        self.dt = 0.025 # Internal integration timestep to use
        self.hParams = Dict({'celsius': 6.3, 'v_init': -65.0, 'clamp_resist': 0.001})  # parameters of h module
        self.coreneuron = False  # use CoreNEURON to run the simulation (beta version)
        self.cache_efficient = False  # use CVode cache_efficient option to optimize load when running on many cores
        self.cvode_active = False  # Use CVode variable time step
        self.cvode_atol = 0.001  # absolute error tolerance
        self.seeds = Dict({'conn': 1, 'stim': 1, 'loc': 1}) # Seeds for randomizers (connectivity, input stimulation and cell locations)
        self.rand123GlobalIndex = None  # Sets the global index used by all instances of the Random123 instances of Random
        self.createNEURONObj = True  #  create runnable network in NEURON when instantiating netpyne network metadata
        self.createPyStruct = True  # create Python structure (simulator-independent) when instantiating network
        self.addSynMechs = True  # whether to add synaptich mechanisms or not
        self.includeParamsLabel = True  # include label of param rule that created that cell, conn or stim
        self.gatherOnlySimData = False  # omits gathering of net+cell data thus reducing gatherData time
        self.compactConnFormat = False  # replace dict format with compact list format for conns (need to provide list of keys to include)
        self.connRandomSecFromList = True  # select random section (and location) from list even when synsPerConn=1 
        self.distributeSynsUniformly = True  # locate synapses at uniformly across section list; if false, place one syn per section in section list   
        self.pt3dRelativeToCellLocation = True  # Make cell 3d points relative to the cell x,y,z location
        self.invertedYCoord = True  # Make y-axis coordinate negative so they represent depth when visualized (0 at the top)
        self.allowSelfConns = False  # allow connections from a cell to itself
        self.allowConnsWithWeight0 = True  # allow connections with weight 0
        self.saveCellSecs = True  # save all the sections info for each cell (False reduces time+space; available in netParams; prevents re-simulation)
        self.saveCellConns = True  # save all the conns info for each cell (False reduces time+space; prevents re-simulation)
        self.timing = True  # show timing of each process
        self.saveTiming = False  # save timing data to pickle file
        self.printRunTime = False  # print run time at interval (in sec) specified here (eg. 0.1)
        self.printPopAvgRates = False  # print population avg firing rates after run
        self.printSynsAfterRule = False  # print total of connections after each conn rule is applied 
        self.verbose = False  # show detailed messages

        # Recording
        self.recordCells = []  # what cells to record traces from (eg. 'all', 5, or 'PYR')
        self.recordTraces = {}  # Dict of traces to record
        self.recordCellsSpikes = -1  # cells to record spike times from (-1 to record from all)
        self.recordStim = False  # record spikes of cell stims
        self.recordLFP = []  # list of 3D locations to record LFP from
        self.recordDipoles = False # record dipoles
        self.saveLFPCells = False  # Store LFP generate individually by each cell 
        self.recordStep = 0.1 # Step size in ms to save data (eg. V traces, LFP, etc)
        self.recordTime = True  # record time step of recording

        # Saving
        self.simLabel = ''  # name of simulation (used as filename if none provided)
        self.saveFolder = ''  # path where to save output data
        self.filename = 'model_output'  # Name of file to save model output (if omitted then saveFolder+simLabel is used)
        self.saveDataInclude = ['netParams', 'netCells', 'netPops', 'simConfig', 'simData']
        self.timestampFilename = False  # Add timestamp to filename to avoid overwriting
        self.savePickle = False # save to pickle file
        self.saveJson = False # save to json file
        self.saveMat = False # save to mat file
        self.saveCSV = False # save to txt file
        self.saveDpk = False # save to .dpk pickled file
        self.saveHDF5 = False # save to HDF5 file
        self.saveDat = False # save traces to .dat file(s)
        self.backupCfgFile = [] # copy cfg file, list with [sourceFile,destFolder] (eg. ['cfg.py', 'backupcfg/'])

        # error checking
        self.checkErrors = False # whether to validate the input parameters (will be turned off if num processors > 1)
        self.checkErrorsVerbose = False # whether to print detailed errors during input parameter validation
        # self.exitOnError = False # whether to hard exit on error

        # Analysis and plotting
        self.analysis = ODict()

        # fill in params from dict passed as argument
        if simConfigDict:
            for k,v in simConfigDict.items():
                if isinstance(v, OrderedDict):
                    setattr(self, k, ODict(v))
                elif isinstance(v, dict):
                    setattr(self, k, Dict(v))
                else:
                    setattr(self, k, v)

    def save(self, filename):
        import os
        basename = os.path.basename(filename)
        folder = filename.split(basename)[0]
        ext = basename.split('.')[1]

        # make dir
        try:
            os.mkdir(folder)
        except OSError:
            if not os.path.exists(folder):
                print(' Could not create', folder)

        dataSave = {'simConfig': self.__dict__}

        # Save to json file
        if ext == 'json':
            from .. import sim
            print(('Saving simConfig to %s ... ' % (filename)))
            sim.saveJSON(filename, dataSave)

    def addAnalysis(self, func, params):
        self.analysis[func] =  params

    def todict(self):
        from ..sim import replaceDictODict
        return replaceDictODict(self.__dict__)
