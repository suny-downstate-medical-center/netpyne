from netpyne import specs

# Simulation options
cfg = specs.SimConfig()		# object of class SimConfig to store simulation configuration

cfg.duration = 1*1e3 			# Duration of the simulation, in ms
cfg.dt = 0.025			# Internal integration timestep to use
cfg.verbose = 1  # Show detailed messages
cfg.seeds = {'conn': 4321, 'stim': 1234, 'loc': 4321}
cfg.hParams = {'celsius': 34, 'v_init': -80}
cfg.oneSynPerNetcon = False
cfg.distributeSynsUniformly = False
cfg.connRandomSecFromList = True

cfg.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
cfg.recordStep = 0.05 			# Step size in ms to save data (eg. V traces, LFP, etc)
cfg.saveJson = True
cfg.filename = 'model3'  # Set file output name

cfg.analysis['plotRaster'] = True 			# Plot a raster
cfg.analysis['plotTraces'] = {'include': [0]} 			# Plot recorded traces for this list of cells