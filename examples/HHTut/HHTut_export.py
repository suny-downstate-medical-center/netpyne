import HHTut  # import parameters file
from netpyne import sim  # import netpyne sim module

sim.createAndExportNeuroML2(netParams = HHTut.netParams, 
                       simConfig = HHTut.simConfig,
                       reference = 'HHTut')  # create and export network to NeuroML 2