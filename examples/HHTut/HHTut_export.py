import HHTut  # import parameters file
from netpyne import sim  # import netpyne sim module

sim.createAndExport(netParams = HHTut.netParams, 
                       simConfig = HHTut.simConfig,
                       reference = 'HHTut')  # create and export network to NeuroML 2