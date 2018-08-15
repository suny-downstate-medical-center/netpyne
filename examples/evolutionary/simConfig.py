from netpyne import specs

simConfig = specs.SimConfig()

# Simulation options
simConfig.dt = 0.025
simConfig.duration = 1*1e3

simConfig.verbose = False
simConfig.saveJson = True
simConfig.filename = 'output_file'

simConfig.recordStep = 0.1
simConfig.recordCells = [20]
simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}

# Variable parameters (used in netParams)
simConfig.synMechTau2 = 5
simConfig.connWeight = 0.01
