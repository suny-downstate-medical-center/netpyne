from netpyne import sim

cfg, netParams = sim.loadFromIndexFile('index_net.npjson')
sim.createSimulateAnalyze(netParams = netParams, simConfig = cfg)    
#sim.analysis.plotCSD(timeRange=[100,3000])