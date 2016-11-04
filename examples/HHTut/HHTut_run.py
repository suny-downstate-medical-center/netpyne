import sys

if '-nogui' in sys.argv:
    import netpyne
    netpyne.__gui__ = False
    
import HHTut  # import parameters file 
from netpyne import sim  # import netpyne sim module

sim.createSimulateAnalyze(netParams = HHTut.netParams, simConfig = HHTut.simConfig)  # create and simulate network
