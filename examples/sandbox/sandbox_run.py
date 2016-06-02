import sandbox  # import parameters file
from netpyne import init  # import netpyne init module

init.createAndSimulate(netParams = sandbox.netParams, simConfig = sandbox.simConfig)  # create and simulate network