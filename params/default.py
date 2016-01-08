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
netParams['scale'] = 1 # Size of simulation in thousands of cells

## General connectivity parameters
netParams['mindelay'] = 2 # Minimum connection delay, in ms
netParams['velocity'] = 100 # Conduction velocity in um/ms (e 100 um = 0.1 m/s)
netParams['scaleconnweight'] = 1 # Connection weight scale factor
netParams['scaleconnprob'] = 1 # scale for scale since size fixed

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
simConfig['randseed'] = 1 # Random seed to use
simConfig['createNEURONObj'] = 1  # create HOC objects when instantiating network
simConfig['createPyStruct'] = 1  # create Python structure (simulator-independent) when instantiating network
simConfig['verbose'] = 0  # show detailed messages 


# Recording 
simConfig['recordTraces'] = True  # whether to record cell traces or not
simConfig['recdict'] = {}
simConfig['simDataVecs'] = ['spkt','spkid','stims']+simConfig['recdict'].keys()
simConfig['recordStim'] = False  # record spikes of cell stims
simConfig['recordStep'] = 1 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
simConfig['filename'] = 'model_output'  # Set file output name
simConfig['timestampFilename'] = True
simConfig['saveFileStep'] = 1000 # step size in ms to save data to disk
simConfig['savePickle'] = False # Whether or not to write spikes etc. to a .mat file
simConfig['saveJson'] = False # Whether or not to write spikes etc. to a .mat file
simConfig['saveMat'] = False # Whether or not to write spikes etc. to a .mat file
simConfig['saveTxt'] = False # save spikes and conn to txt file
simConfig['saveDpk'] = False # save to a .dpk pickled file


# Analysis and plotting 
simConfig['plotRaster'] = True # Whether or not to plot a raster
simConfig['orderRasterYfrac'] = False # Order cells in raster by yfrac (default is by pop and cell id)
simConfig['plotTracesGids'] = [] # plot recorded traces for this list of cells
simConfig['plotPsd'] = False # plot power spectral density
simConfig['maxspikestoplot'] = 3e8 # Maximum number of spikes to plot
simConfig['plotConn'] = False # whether to plot conn matrix
simConfig['plotWeightChanges'] = False # whether to plot weight changes (shown in conn matrix)
simConfig['plot3dArch'] = False # plot 3d architecture

