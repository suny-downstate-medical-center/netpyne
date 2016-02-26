import HybridTut  # import parameters file
from netpyne import init  # import netpyne init module

init.createAndSimulate(netParams = HybridTut.netParams, simConfig = HybridTut.simConfig)  # create and simulate network