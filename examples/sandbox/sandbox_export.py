import sys

if '-nogui' in sys.argv:
    import netpyne
    netpyne.__gui__ = False
    
import sandbox  # import parameters file
from netpyne import sim  # import netpyne sim module

sim.createExportNeuroML2(netParams = sandbox.netParams, 
                       simConfig = sandbox.simConfig,
                       reference = 'sandbox')  # create and export network to NeuroML 2