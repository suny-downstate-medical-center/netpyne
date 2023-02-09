from netpyne import sim  # import netpyne sim module

cfg, netParams = sim.loadFromIndexFile('index.npjson')
print("********************\n*\n*  Note: setting noise to 1, since noise can only be 0 or 1 in NeuroML export currently!\n*\n********************")
netParams.stimSourceParams['background_E']['noise'] = 1
netParams.stimSourceParams['background_I']['noise'] = 1

sim.createExportNeuroML2(netParams = netParams,
                         simConfig = cfg,
                         reference = 'M1',
                         connections=True,
                         stimulations=True)  # create and export network to NeuroML 2

###### Validate the NeuroML ######

from neuroml.utils import validate_neuroml2
validate_neuroml2('M1.net.nml')
