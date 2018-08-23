from netpyne import specs

cfg = specs.SimConfig()

cfg.networkType = 'complex' # 'complex'

# --------------------------------------------------------
# Simple network
# --------------------------------------------------------
if cfg.networkType == 'simple':
	# Simulation options
	cfg.dt = 0.025
	cfg.duration = 2*1e3

	cfg.verbose = False
	cfg.saveJson = True
	cfg.filename = 'simple_net'
	cfg.saveDataInclude = ['simData']
	cfg.recordStep = 0.1
	cfg.printPopAvgRates = [500, cfg.duration]

	# cfg.recordCells = [1]
	# cfg.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}

	# Variable parameters (used in netParams)
	cfg.prob = 0.2
	cfg.weight = 0.025
	cfg.delay = 2

# --------------------------------------------------------
# Complex network
# --------------------------------------------------------
elif cfg.networkType == 'complex':
	simConfig.duration = 2.0*1e3           # Duration of the simulation, in ms
	simConfig.dt = 0.1                # Internal integration timestep to use
	simConfig.verbose = False            # Show detailed messages 
	simConfig.recordStep = 1             # Step size in ms to save data (eg. V traces, LFP, etc)
	simConfig.filename = 'complex_net'   # Set file output name

	cfg.printPopAvgRates = [500, cfg.duration]

	# Variable parameters (used in netParams)
	cfg.probEall = [0.05, 0.2] # 0.1
	cfg.weightEall = [2.5, 7.5] #5.0
	cfg.probIE = [0.2, 0.6] #0.4
	cfg.weightIE = 1.0
	cfg.probLengthConst = 150
