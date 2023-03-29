from netpyne import specs

cfg = specs.SimConfig()   # object of class SimConfig to store the simulation configuration

# Simulation parameters
cfg.duration = 1*1e3 # Duration of the simulation, in ms
cfg.dt = 0.025 # Internal integration timestep to use
cfg.seeds = {'conn': 1, 'stim': 1, 'loc': 1} # Seeds for randomizers (connectivity, input stimulation and cell locations)
cfg.verbose = False  # show detailed messages
cfg.hParams = {'v_init': -71}

# Recording
cfg.recordCells = []  # which cells to record from
cfg.recordTraces = {'Vsoma': {'sec': 'soma','loc': 0.5,'var': 'v'}}
cfg.recordStim = True  # record spikes of cell stims
cfg.recordStep = 0.1 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
cfg.filename = 'HHTut'  # Set file output name
cfg.saveFileStep = 1000 # step size in ms to save data to disk
cfg.savePickle = False # Whether or not to write spikes etc. to a .mat file
cfg.saveJson = True

# Analysis and plotting
cfg.analysis['plotRaster'] = {'saveData': 'raster_data.json', 'saveFig': True, 'showFig': True} # Plot raster
cfg.analysis['plotTraces'] = {'include': [2], 'saveFig': True, 'showFig': True} # Plot cell traces
cfg.analysis['plot2Dnet'] = {'saveFig': True, 'showFig': True} # Plot 2D cells and connections

cfg.validateNetParams=True