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
	cfg.duration = 1*1e3           # Duration of the simulation, in ms
	cfg.dt = 0.1                # Internal integration timestep to use
	cfg.verbose = False            # Show detailed messages 
	cfg.recordStep = 1             # Step size in ms to save data (eg. V traces, LFP, etc)
	cfg.filename = 'complex_net'   # Set file output name
	cfg.saveDataInclude = ['simData']
	cfg.saveJson = True
	cfg.printPopAvgRates = [100, cfg.duration]

	# Variable parameters (used in netParams)
	cfg.probEall = 0.1 
	cfg.weightEall = 0.005 
	cfg.probIE = 0.4 
	cfg.weightIE = 0.001
	cfg.probLengthConst = 150 
	cfg.stimWeight = 0.1 
