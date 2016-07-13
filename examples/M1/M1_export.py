import M1  # import parameters file
from netpyne import sim  # import netpyne sim module

sim.createAndExportNeuroML2(netParams = M1.netParams, 
                       simConfig = M1.simConfig,
                       reference = 'M1',
                       connections=True,
                       stimulations=True)  # create and export network to NeuroML 2