import sandbox  # import parameters file
from netpyne import sim  # import netpyne sim module

sim.createAndExport(netParams = sandbox.netParams, 
                       simConfig = sandbox.simConfig,
                       reference = 'sandbox')  # create and export network to NeuroML 2