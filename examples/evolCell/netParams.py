
"""
netParams.py 

High-level specifications for M1 network model using NetPyNE

Contributors: salvadordura@gmail.com
"""

from netpyne import specs

try:
    from __main__ import cfg  # import SimConfig object with params from parent module
except:
    from cfg import cfg  # if no simConfig in parent module, import directly from tut8_cfg module

#------------------------------------------------------------------------------
#
# NETWORK PARAMETERS
#
#------------------------------------------------------------------------------

netParams = specs.NetParams()   # object of class NetParams to store the network parameters

#------------------------------------------------------------------------------
# Cell parameters
#------------------------------------------------------------------------------

# cell params
netParams.loadCellParamsRule('ITS4_reduced', 'ITS4_reduced_cellParams.json')
netParams.cellParams['ITS4_reduced']['conds'] = {'cellType': 'ITS4'}

for sec, secDict in netParams.cellParams['ITS4_reduced']['secs'].items():
    print(sec)
    if sec in cfg.tune:
        # vinit
        print(cfg.tune)
        if 'vinit' in cfg.tune[sec]:
            print(secDict['vinit'], cfg.tune[sec]['vinit'])
            secDict['vinit'] = cfg.tune[sec]['vinit']
        
        # mechs
        for mech in secDict['mechs']:
            if mech in cfg.tune[sec]:
                for param in secDict['mechs']:
                    if param in cfg.tune[sec][mech]:
                        secDict['mechs'][mech][param] = cfg.tune[sec][mech][param]  
        
        # geom
        for geomParam in secDict['geom']:
            if geomParam in cfg.tune[sec]:
                secDict['geom'][geomParam] = cfg.tune[sec][geomParam]

#netParams.cellParams['ITS4_reduced']['secs'] = secDict

#------------------------------------------------------------------------------
# Population parameters
#------------------------------------------------------------------------------
netParams.popParams['ITS4'] = {'cellType': 'ITS4', 'numCells': 1}


#------------------------------------------------------------------------------
# Current inputs (IClamp)
#------------------------------------------------------------------------------
if cfg.addIClamp:	
     for iclabel in [k for k in dir(cfg) if k.startswith('IClamp')]:
        ic = getattr(cfg, iclabel, None)  # get dict with params

        # add stim source
        netParams.stimSourceParams[iclabel] = {'type': 'IClamp', 'delay': ic['start'], 'dur': ic['dur'], 'amp': ic['amp']}
        
        # connect stim source to target
        netParams.stimTargetParams[iclabel+'_'+ic['pop']] = \
            {'source': iclabel, 'conds': {'pop': ic['pop']}, 'sec': ic['sec'], 'loc': ic['loc']}

