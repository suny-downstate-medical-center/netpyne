from netpyne import sim
from netpyne.specs import netParams

cfg, netParams = sim.loadFromIndexFile('index.npjson')

# Create network and run simulation
sim.createSimulateAnalyze(netParams = netParams, simConfig = cfg)
#sim.analysis.plotCSD()