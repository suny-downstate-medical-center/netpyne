from netpyne import specs

cfg = specs.SimConfig()

cfg.networkType = 'simple' # 'complex'

# --------------------------------------------------------
# Simple network
# --------------------------------------------------------

# Simulation options
cfg.dt = 0.025
cfg.duration = 0.5*1e3

cfg.verbose = False
cfg.saveJson = True
cfg.filename = 'simple_net'
cfg.saveDataInclude = ['simData']
cfg.recordStep = 0.1
cfg.printPopAvgRates = [000, cfg.duration]

cfg.allpops = ['M', 'S']
cfg.recordTraces = {'V_soma': {'sec':'soma', 'loc': 0.5, 'var':'v'}}
#cfg.analysis['plotTraces'] = {'include': [('M',0), ('S',0)], 'timeRange': [0,cfg.duration], 'figSize': (10,4), 'saveFig': True, 'showFig': False} 

#cfg.analysis['plotTraces'] = {'include': [(pop, 0) for pop in cfg.allpops], 'oneFigPer': 'trace', 'overlay': True, 'saveFig': True, 'showFig': False, 'figSize':(12,8)} #[(pop,0) for pop in alltypes]		## Seen in M1 cfg.py (line 68) 
# cfg.recordCells = [1]
# cfg.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}

# Variable parameters (used in netParams)
cfg.prob = 0.2
cfg.weight = 0.025
cfg.delay = 2
cfg.prob2 = 0.2
cfg.weight2 = 0.025
cfg.delay2 = 2
cfg.prob3 = 0.2
cfg.weight3 = 0.025
cfg.delay3 = 2
cfg.prob4 = 0.2
cfg.weight4 = 0.025
cfg.delay4 = 2
