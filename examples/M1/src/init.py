from netpyne import sim  # import netpyne init module

cfg, netParams = sim.loadFromIndexFile('index.npjson')
sim.createSimulateAnalyze(netParams = netParams, simConfig = cfg)  # create and simulate network
