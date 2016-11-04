import HHTut  # import parameters file
from netpyne import sim  # import netpyne sim module

import netpyne
netpyne.gui = False

np = HHTut.netParams
print("********************\n*\n*  Note: setting noise to 1, since noise can only be 0 or 1 in NeuroML export currently!\n*\n********************")
np.popParams['background']['noise'] = 1

sim.createExportNeuroML2(netParams = np, 
                       simConfig = HHTut.simConfig,
                       reference = 'HHTut')  # create and export network to NeuroML 2