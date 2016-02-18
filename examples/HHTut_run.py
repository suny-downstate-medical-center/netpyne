import HHTut  # import parameters file
from netpyne import init  # import netpyne init module

init.createAndSimulate(netParams = HHTut.netParams, simConfig = HHTut.simConfig)  # create and simulate network