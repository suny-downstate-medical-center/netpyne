from netpyne import sim  # import netpyne init module

cfg, netParams = sim.loadFromIndexFile('../../HybridTut/index.npjson')
sim.createSimulateAnalyze(netParams = netParams, simConfig = cfg)  # create and simulate network

netParams.stimSourceParams['bkg']['noise'] = 1

sim.createExportNeuroML2(netParams = netParams,
                       simConfig = cfg,
                       reference = 'HybridTut')  # create and export network to NeuroML 2


###### Validate the NeuroML ######

from neuroml.utils import validate_neuroml2
validate_neuroml2('HybridTut.net.nml')