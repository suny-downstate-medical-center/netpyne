from netpyne import specs

cfg = specs.SimConfig()

# Simulation options
cfg.dt = 0.025
cfg.duration = 1*1e3

cfg.verbose = False
cfg.saveJson = True
cfg.filename = 'output_file'
cfg.saveDataInclude = ['simData']
cfg.recordStep = 0.1
# cfg.recordCells = [1]
# cfg.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}

# Variable parameters (used in netParams)
cfg.prob = 0.2
cfg.weight = 0.025
cfg.delay = 2
