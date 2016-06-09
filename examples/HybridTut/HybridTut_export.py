import HybridTut  # import parameters file
from netpyne import sim  # import netpyne sim module

sim.createAndExport(netParams = HybridTut.netParams, 
                       simConfig = HybridTut.simConfig,
                       reference = 'HybridTut')  # create and export network to NeuroML 2