import HHTut  # import parameters file
from netpyne import sim  # import netpyne sim module

sim.createAndSimulate(netParams = HHTut.netParams, simConfig = HHTut.simConfig)  # create and simulate network