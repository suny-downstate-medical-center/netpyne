from netpyne import sim  # import netpyne init module

example = 'HHTut'

cfg, netParams = sim.loadFromIndexFile('../../%s/index.npjson'%example)
sim.createSimulateAnalyze(netParams = netParams, simConfig = cfg)  # create and simulate network

netParams.stimSourceParams['bkg']['noise'] = 1

sim.createExportNeuroML2(netParams = netParams,
                       simConfig = cfg,
                       reference = example)  # create and export network to NeuroML 2


###### Validate the NeuroML ######

from neuroml.utils import validate_neuroml2
validate_neuroml2('%s.net.nml'%example)