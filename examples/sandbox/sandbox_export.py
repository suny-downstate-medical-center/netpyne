import sandbox  # import parameters file
from netpyne import init  # import netpyne init module

init.createAndExport(netParams = sandbox.netParams, 
                       simConfig = sandbox.simConfig,
                       reference = 'sandbox')  # create and export network to NeuroML 2