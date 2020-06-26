from netpyne import specs

cfg = specs.SimConfig()

cfg.networkType = 'simple' # 'complex'

# --------------------------------------------------------
# Simple network
# --------------------------------------------------------

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
