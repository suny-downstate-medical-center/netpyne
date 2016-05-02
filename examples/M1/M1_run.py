import M1  # import parameters file
from netpyne import init  # import netpyne init module

init.createAndSimulate(netParams = M1.netParams, simConfig = M1.simConfig)  # create and simulate network