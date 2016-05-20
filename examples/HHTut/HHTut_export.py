import HHTut  # import parameters file
from netpyne import init  # import netpyne init module

init.createAndExport(netParams = HHTut.netParams, 
                       simConfig = HHTut.simConfig,
                       reference = 'HHTut')  # create and export network to NeuroML 2