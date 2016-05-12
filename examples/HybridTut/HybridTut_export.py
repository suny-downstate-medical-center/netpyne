import HybridTut  # import parameters file
from netpyne import init  # import netpyne init module

init.createAndExport(netParams = HybridTut.netParams, 
                       simConfig = HybridTut.simConfig,
                       reference = 'HybridTut')  # create and export network to NeuroML 2