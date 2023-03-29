from netpyne import sim  # import netpyne init module

example = 'M1'

cfg, netParams = sim.loadFromIndexFile('../../%s/index.npjson'%example)
sim.createSimulateAnalyze(netParams = netParams, simConfig = cfg)  # create and simulate network

print(netParams.stimSourceParams)
netParams.stimSourceParams['background_E']['noise'] = 1
netParams.stimSourceParams['background_I']['noise'] = 1

sim.createExportNeuroML2(netParams = netParams,
                       simConfig = cfg,
                       reference = example)  # create and export network to NeuroML 2


###### Validate the NeuroML ######

from neuroml.utils import validate_neuroml2
validate_neuroml2('%s.net.nml'%example)