from netpyne import specs

netParams = specs.NetParams()   # object of class NetParams to store the network parameters

###############################################################################
#
# MPI HH TUTORIAL PARAMS
#
###############################################################################

###############################################################################
# NETWORK PARAMETERS
###############################################################################

# Population parameters
netParams.popParams['PYR_HH_pop'] = {'cellType': 'PYR_HH', 'numCells': 50} # add dict with params for this pop
netParams.popParams['PYR_Izhi_pop'] = {'cellType': 'PYR_Izhi', 'numCells': 50} # add dict with params for this pop


# Cell parameters list
## PYR cell properties (HH)
cellRule = {'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'topol': {}, 'mechs': {}}  # soma properties
cellRule['secs']['soma']['geom'] = {'diam': 6.3, 'L': 5, 'Ra': 123.0, 'pt3d':[]}
cellRule['secs']['soma']['geom']['pt3d'].append((0, 0, 0, 20))
cellRule['secs']['soma']['geom']['pt3d'].append((0, 0, 20, 20))
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}

cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  # dend properties
cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1, 'pt3d': []}
cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}
cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70}

netParams.cellParams['PYR_HH'] = cellRule  # add dict to list of cell properties

## PYR cell properties (Izhi)
cellRule = {'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'pointps':{}}  # soma properties
cellRule['secs']['soma']['geom'] = {'diam': 10, 'L': 10, 'cm': 31.831}
cellRule['secs']['soma']['pointps']['Izhi'] = {'mod':'Izhi2007b',
    'C':1, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}
netParams.cellParams['PYR_Izhi'] = cellRule  # add dict to list of cell properties


# Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'ExpSyn', 'tau': 0.1, 'e': 0}


# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.5}
netParams.stimTargetParams['bg->PYR_Izhi'] = {'source': 'bkg', 'conds': {'cellType': 'PYR_Izhi'},
                                            'weight': 1, 'delay': 'uniform(1,5)', 'synMech': 'AMPA'}
netParams.stimTargetParams['bg->PYR_HH'] = {'source': 'bkg', 'conds': {'cellType': 'PYR_HH'},
                                            'weight': 1, 'synMech': 'AMPA', 'sec': 'dend', 'loc': 1.0, 'delay': 'uniform(1,5)'}


# Connectivity parameters
netParams.connParams['PYR->PYR'] = {
    'preConds': {'cellType': ['PYR_HH', 'PYR_Izhi']}, 
    'postConds': {'cellType': ['PYR_HH', 'PYR_Izhi']},
    'weight': 0.2,                    # weight of each connection
    'delay': '0.2+normal(13.0,1.4)',     # delay min=0.2, mean=13.0, var = 1.4
    'threshold': 10,                    # threshold
    'convergence': 'uniform(0,5)',       # convergence (num presyn targeting postsyn) is uniformly distributed between 1 and 10
    'synMech': 'AMPA'}