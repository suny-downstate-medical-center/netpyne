import M1  # import parameters file
from netpyne import sim  # import netpyne init module

sim.createSimulateAnalyze(netParams = M1.netParams, simConfig = M1.simConfig, interval=1000)  # create and simulate network

# check model output
sim.checkOutput('M1')