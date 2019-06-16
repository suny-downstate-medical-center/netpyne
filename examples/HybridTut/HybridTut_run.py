import HybridTut  # import parameters file
from netpyne import sim  # import netpyne init module

sim.createSimulateAnalyze(netParams = HybridTut.netParams, simConfig = HybridTut.simConfig)  # create and simulate network

# check model output
sim.checkOutput('HybridTut')