import HHTut  # import parameters file 
from netpyne import sim  # import netpyne sim module

sim.createSimulateAnalyze(netParams = HHTut.netParams, simConfig = HHTut.simConfig)  # create and simulate network

# check model output
sim.checkOutput('HHTut')