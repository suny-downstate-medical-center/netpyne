import sandbox  # import parameters file
from netpyne import sim # import netpyne init module

sim.createAndSimulate(netParams = sandbox.netParams, simConfig = sandbox.simConfig)  # create and simulate network