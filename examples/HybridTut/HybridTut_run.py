import HybridTut  # import parameters file
from netpyne import sim  # import netpyne init module

sim.createSimulateAnalyze(netParams = HybridTut.netParams, simConfig = HybridTut.simConfig)  # create and simulate network

# Check the model output: sim.checkOutput is used for testing purposes.  Please comment out the following line if you are exploring the example.
sim.checkOutput('HybridTut')
