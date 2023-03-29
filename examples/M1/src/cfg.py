from netpyne import specs

cfg = specs.SimConfig()   # object of class SimConfig to store the simulation configuration

###############################################################################
#
# M1 6-LAYER ynorm-BASED MODEL
#
###############################################################################

###############################################################################
# SIMULATION CONFIGURATION
###############################################################################

# Simulation parameters
cfg.duration = 2*1e3 # Duration of the simulation, in ms
cfg.dt = 0.1 # Internal integration timestep to use
cfg.seeds = {'conn': 1, 'stim': 1, 'loc': 1} # Seeds for randomizers (connectivity, input stimulation and cell locations)
cfg.createNEURONObj = 1  # create HOC objects when instantiating network
cfg.createPyStruct = 1  # create Python structure (simulator-independent) when instantiating network
cfg.verbose = 0 # Whether to write diagnostic information on events
cfg.oneSynPerNetcon = False

# Recording
cfg.recordCells = []  # list of cells to record from
cfg.recordTraces = {'V':{'sec':'soma','loc':0.5,'var':'v'}} # 'V':{'sec':'soma','loc':0.5,'var':'v'}}
    #'V':{'sec':'soma','loc':0.5,'var':'v'},
    #'u':{'sec':'soma', 'pointp':'Izhi2007b_0', 'var':'u'},
    #'I':{'sec':'soma', 'pointp':'Izhi2007b_0', 'var':'i'},
    #'AMPA_i': {'sec':'soma', 'loc':'0.5', 'synMech':'AMPA', 'var':'i'},
    #'NMDA_i': {'sec':'soma', 'loc':'0.5', 'synMech':'NMDA', 'var':'iNMDA'}}  # Dict of traces to record
cfg.recordStim = False  # record spikes of cell stims
cfg.recordStep = 0.1 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
cfg.filename = 'data/M1_ynorm_izhi'  # Set file output name
cfg.saveFileStep = 1000 # step size in ms to save data to disk
cfg.savePickle = False # save to pickle file
cfg.saveJson = False # save to json file
cfg.saveMat = False # save to mat file
cfg.saveTxt = False # save to txt file
cfg.saveDpk = False # save to .dpk pickled file
cfg.saveHDF5 = False # save to HDF5 file


# Analysis and plotting
cfg.addAnalysis('plotRaster', True) # Whether or not to plot a raster
cfg.addAnalysis('plotTraces', {'include': [('IT_L23',0), ('PT_L5B',1), ('PV_L23',2), ('SOM_L5',3)]}) # plot recorded traces for this list of cells
cfg.addAnalysis('plot2Dnet', {'showConns': False})