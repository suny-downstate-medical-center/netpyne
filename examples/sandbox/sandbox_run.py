import sandbox  # import parameters file
from netpyne import sim # import netpyne sim module

sim.createAndSimulate(netParams = sandbox.netParams, simConfig = sandbox.simConfig)  # create and simulate network