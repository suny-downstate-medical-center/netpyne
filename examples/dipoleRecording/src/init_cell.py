from netpyne import sim

cfg, netParams = sim.loadFromIndexFile('index_cell.npjson')
sim.createSimulateAnalyze(netParams = netParams, simConfig = cfg)    
#sim.analysis.plotCSD()