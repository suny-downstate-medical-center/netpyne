
"""
netParams.py 

High-level specifications for M1 network model using NetPyNE

Contributors: salvadordura@gmail.com
"""

from netpyne import specs

try:
    from __main__ import cfg  # import SimConfig object with params from parent module
except:
    from tut8_cfg import cfg  # if no simConfig in parent module, import directly from tut8_cfg module

###############################################################################
#
# NETWORK PARAMETERS
#
###############################################################################

netParams = specs.NetParams()   # object of class NetParams to store the network parameters

###############################################################################
# Cell parameters
###############################################################################

# PT cell params (6-comp)
cellRule = netParams.importCellParams(label='PT_6comp', conds={'cellType': 'PT', 'cellModel': 'HH_reduced'},
  fileName='cells/SPI6.py', cellName='SPI6')

cellRule['secLists']['alldend'] = ['Bdend', 'Adend1', 'Adend2', 'Adend3']  # define section lists
cellRule['secLists']['apicdend'] = ['Adend1', 'Adend2', 'Adend3']

for secName,sec in cellRule['secs'].items(): 
    sec['vinit'] = -75.0413649414  # set vinit for all secs
    if secName in cellRule['secLists']['alldend']:  
        sec['mechs']['nax']['gbar'] = cfg.dendNa  # set dend Na gmax for all dends


###############################################################################
# Population parameters
###############################################################################
netParams.popParams['PT5B'] =	{'cellModel': 'HH_reduced', 'cellType': 'PT', 'numCells': 1}


###############################################################################
# Synaptic mechanism parameters
###############################################################################
netParams.synMechParams['NMDA'] = {'mod': 'MyExp2SynNMDABB', 'tau1NMDA': cfg.tau1NMDA, 'tau2NMDA': 150, 'e': 0}


###############################################################################
# Current inputs (IClamp)
###############################################################################
if cfg.addIClamp:	
     for iclabel in [k for k in dir(cfg) if k.startswith('IClamp')]:
        ic = getattr(cfg, iclabel, None)  # get dict with params

        # add stim source
        netParams.stimSourceParams[iclabel] = {'type': 'IClamp', 'delay': ic['start'], 'dur': ic['dur'], 'amp': ic['amp']}
        
        # connect stim source to target
        netParams.stimTargetParams[iclabel+'_'+ic['pop']] = \
            {'source': iclabel, 'conds': {'pop': ic['pop']}, 'sec': ic['sec'], 'loc': ic['loc']}


###############################################################################
# NetStim inputs
###############################################################################
if cfg.addNetStim:
    for nslabel in [k for k in dir(cfg) if k.startswith('NetStim')]:
        ns = getattr(cfg, nslabel, None)

        # add stim source
        netParams.stimSourceParams[nslabel] = {'type': 'NetStim', 'start': ns['start'], 'interval': ns['interval'], 
                                               'noise': ns['noise'], 'number': ns['number']}

        # connect stim source to target
        netParams.stimTargetParams[nslabel+'_'+ns['pop']] = \
            {'source': nslabel, 'conds': {'pop': ns['pop']}, 'sec': ns['sec'], 'loc': ns['loc'],
             'synMech': ns['synMech'], 'weight': ns['weight'], 'delay': ns['delay']}
