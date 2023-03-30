from netpyne import sim

cfg, netParams = sim.loadFromIndexFile('index.npjson')
sim.createSimulateAnalyze(netParams = netParams, simConfig = cfg)
