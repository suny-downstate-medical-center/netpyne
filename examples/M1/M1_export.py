import M1  # import parameters file
from netpyne import sim  # import netpyne sim module

sim.createAndExport(netParams = M1.netParams, 
                       simConfig = M1.simConfig,
                       reference = 'M1')  # create and export network to NeuroML 2