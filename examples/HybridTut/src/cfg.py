from netpyne import specs

cfg = specs.SimConfig()

cfg.duration = 1*1e3 # Duration of the simulation, in ms
cfg.dt = 0.025 # Internal integration timestep to use
cfg.seeds = {'conn': 1, 'stim': 1, 'loc': 1} # Seeds for randomizers (connectivity, input stimulation and cell locations)
cfg.createNEURONObj = True  # create HOC objects when instantiating network
cfg.createPyStruct = True  # create Python structure (simulator-independent) when instantiating network
cfg.timing = True  # show timing  and save to file
cfg.verbose = False # show detailed messages


# Recording
cfg.recordCells = []  # list of cells to record from
cfg.recordTraces = {'V':{'sec':'soma','loc':0.5,'var':'v'},
    'u':{'sec':'soma', 'pointp':'Izhi', 'var':'u'},
    'I':{'sec':'soma', 'pointp':'Izhi', 'var':'i'},
    'AMPA_g': {'sec':'soma', 'loc':0.5, 'synMech':'AMPA', 'var':'g'},
    'AMPA_i': {'sec':'soma', 'loc':0.5, 'synMech':'AMPA', 'var':'i'}}
cfg.recordStim = True  # record spikes of cell stims
cfg.recordStep = 0.025 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
cfg.filename = 'mpiHybridTut'  # Set file output name
cfg.saveFileStep = 1000 # step size in ms to save data to disk
cfg.savePickle = False # Whether or not to write spikes etc. to a .mat file
cfg.saveJson = False # Whether or not to write spikes etc. to a .mat file
cfg.saveMat = False # Whether or not to write spikes etc. to a .mat file
cfg.saveTxt = False # save spikes and conn to txt file
cfg.saveDpk = False # save to a .dpk pickled file


# Analysis and plotting
cfg.analysis['plotRaster'] = {'orderInverse': False} #True # Whether or not to plot a raster
cfg.analysis['plotTraces'] = {'include': [1,51]} # plot recorded traces for this list of cells