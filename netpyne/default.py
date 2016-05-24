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
netParams['scaleConnWeight'] = 1 # Connection weight scale factor
netParams['defaultWeight'] = 1  # default connection weight
netParams['defaultDelay'] = 1  # default connection delay (ms)
netParams['propVelocity'] = 500.0 # propagation velocity (um/ms)
 
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
simConfig['createNEURONObj'] = True  # create HOC objects when instantiating network
simConfig['createPyStruct'] = True  # create Python structure (simulator-independent) when instantiating network
simConfig['timing'] = True  # show timing of each process
simConfig['saveTiming'] = False  # save timing data to pickle file
simConfig['verbose'] = False  # show detailed messages 


# Recording 
simConfig['recordCells'] = []  # what cells to record from (eg. 'all', 5, or 'PYR')
simConfig['recordTraces'] = {}  # Dict of traces to record 
simConfig['recordStim'] = False  # record spikes of cell stims
simConfig['recordStep'] = 1 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
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
simConfig['plotCells'] = [] # plot recorded traces for this list of cells
simConfig['plotRaster'] = True # Whether or not to plot a raster
simConfig['plotSync'] = False  # add vertical lines for all spikes as an indication of synchrony
simConfig['maxspikestoplot'] = 3e8 # Maximum number of spikes to plot
simConfig['orderRasterYnorm'] = False # Order cells in raster by yfrac (default is by pop and cell id)
simConfig['plotLFPSpectrum'] = False # plot power spectral density (not yet implemented)
simConfig['plot2Dnet'] = False # plot 2D visualization of cell positions and connections
simConfig['plotConn'] = False # whether to plot conn matrix (not yet implemented)
simConfig['plotWeightChanges'] = False # whether to plot weight changes (not yet implemented)
simConfig['plot3dArch'] = False # plot 3d architecture (not yet implemented)