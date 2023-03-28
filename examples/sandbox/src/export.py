import sys

if '-nogui' in sys.argv:
    import netpyne
    netpyne.__gui__ = False

from netpyne import sim  # import netpyne sim module

cfg, netParams = sim.loadFromIndexFile('index.npjson')
sim.createExportNeuroML2(netParams = netParams,
                       simConfig = cfg,
                       reference = 'sandbox')  # create and export network to NeuroML 2
