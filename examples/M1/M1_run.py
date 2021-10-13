import M1  # import parameters file
from netpyne import sim  # import netpyne init module

sim.createSimulateAnalyze(netParams = M1.netParams, simConfig = M1.simConfig)  # create and simulate network

# Check the model output: sim.checkOutput is used for testing purposes.  Please comment out the following line if you are exploring the example.
sim.checkOutput('M1')
