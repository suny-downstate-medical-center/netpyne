import sandbox  # import parameters file
from netpyne import sim # import netpyne sim module

# netParams = sandbox.netParams
# simConfig = sandbox.simConfig
# sim.create()  # create and simulate network

sim.createAndSimulate(netParams = sandbox.netParams, simConfig = sandbox.simConfig)  # create and simulate network