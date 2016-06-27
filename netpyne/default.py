"""
params.py 
netParams is a dict containing a set of network parameters using a standardized structure
simConfig is a dict containing a set of simulation configurations using a standardized structure
Contributors: salvadordura@gmail.com
"""

netParams = {}  # dictionary to store sets of network parameters
simConfig = {}  # dictionary to store sets of simulation configurations


###############################################################################
#
# DEFAULT PARAMS
#
###############################################################################

###############################################################################
# NETWORK PARAMETERS
###############################################################################

# General network parameters
netParams['scale'] = 1 	 # scale factor for number of cells 
netParams['sizeX'] = 100 # x-dimension (horizontal length) size in um
netParams['sizeY'] = 100 # y-dimension (vertical height or cortical depth) size in um
netParams['sizeZ'] = 100 # z-dimension (horizontal depth) size in um


## General connectivity parameters
netParams['scaleConnWeight'] = 1 # Connection weight scale factor (NetStims not included)
netParams['scaleConnWeightNetStims'] = 1 # Connection weight scale factor for NetStims
netParams['scaleConnWeightModels'] = {} # Connection weight scale factor for each cell model eg. {'Izhi2007': 0.1, 'Friesen': 0.02}
netParams['defaultWeight'] = 1  # default connection weight
netParams['defaultDelay'] = 1  # default connection delay (ms)
netParams['defaultThreshold'] = 10  # default Netcon threshold (mV)
netParams['propVelocity'] = 500.0  # propagation velocity (um/ms)
 
# Cell properties list
netParams['cellParams'] = []

# Population parameters
netParams['popParams'] = []  # create list of populations - each item will contain dict with pop params
netParams['popTagsCopiedToCells'] = ['popLabel', 'cellModel', 'cellType']


# Connectivity parameters
netParams['connParams'] = []  

###############################################################################
# SIMULATION PARAMETERS
###############################################################################

simConfig = {}  # dictionary to store simConfig

# Simulation parameters
simConfig['duration'] = simConfig['tstop'] = 1*1e3 # Duration of the simulation, in ms
simConfig['dt'] = 0.025 # Internal integration timestep to use
simConfig['hParams'] = {'celsius': 6.3, 'clamp_resist': 0.001}  # parameters of h module 
simConfig['seeds'] = {'conn': 1, 'stim': 1, 'loc': 1} # Seeds for randomizers (connectivity, input stimulation and cell locations)
simConfig['createNEURONObj'] = True  # create HOC objects when instantiating network
simConfig['createPyStruct'] = True  # create Python structure (simulator-independent) when instantiating network
simConfig['timing'] = True  # show timing of each process
simConfig['saveTiming'] = False  # save timing data to pickle file
simConfig['verbose'] = False  # show detailed messages 


# Recording 
simConfig['recordCells'] = []  # what cells to record from (eg. 'all', 5, or 'PYR')
simConfig['recordTraces'] = {}  # Dict of traces to record 
simConfig['recordStim'] = False  # record spikes of cell stims
simConfig['recordStep'] = 0.1 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
simConfig['saveDataInclude'] = ['netParams', 'netCells', 'netPops', 'simConfig', 'simData']
simConfig['filename'] = 'model_output'  # Name of file to save model output
simConfig['timestampFilename'] = False  # Add timestamp to filename to avoid overwriting
simConfig['savePickle'] = False # save to pickle file
simConfig['saveJson'] = False # save to json file
simConfig['saveMat'] = False # save to mat file
simConfig['saveCSV'] = False # save to txt file
simConfig['saveDpk'] = False # save to .dpk pickled file
simConfig['saveHDF5'] = False # save to HDF5 file 
simConfig['saveDat'] = False # save traces to .dat file(s)


# Analysis and plotting 
simConfig['analysis'] = {}
