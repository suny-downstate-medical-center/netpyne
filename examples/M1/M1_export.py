import M1  # import parameters file
from netpyne import init  # import netpyne init module

init.createAndExport(netParams = M1.netParams, 
                       simConfig = M1.simConfig,
                       reference = 'M1')  # create and export network to NeuroML 2