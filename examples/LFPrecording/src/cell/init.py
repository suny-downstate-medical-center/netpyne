from netpyne import sim
from netpyne.specs import netParams

cfg, netParams = sim.readCmdLineArgs()
if not cfg:
    from cfg import cfg
if not netParams:
    from netParams import netParams

# Create network and run simulation
sim.createSimulateAnalyze(netParams = netParams, simConfig = cfg)
#sim.analysis.plotCSD()