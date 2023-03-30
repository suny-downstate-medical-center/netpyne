from netpyne import sim

cfg, netParams = sim.loadFromIndexFile('index.npjson')

print("********************\n*\n*  Note: setting noise to 1, since noise can only be 0 or 1 in NeuroML export currently!\n*\n********************")
netParams.stimSourceParams['bkg']['noise'] = 1

cfg.verbose = True
sim.createExportNeuroML2(netParams = netParams,
                       simConfig = cfg,
                       reference = 'HHTut')  # create and export network to NeuroML 2


###### Validate the NeuroML ######

from neuroml.utils import validate_neuroml2
validate_neuroml2('HHTut.net.nml')


###### Export also to Python ######

from netpyne.conversion import createPythonScript
createPythonScript('HHTut_regen.py', netParams, cfg)


