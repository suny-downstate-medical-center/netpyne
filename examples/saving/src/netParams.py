"""
params.py

Example of saving different network components to file

netParams is an object containing a set of network parameters using a standardized structure
"""

from netpyne import specs

netParams = specs.NetParams()   # object of class NetParams to store the network parameters

# -----------------------------------------------------------------------------
# NETWORK PARAMETERS
# -----------------------------------------------------------------------------

# Population parameters
netParams.popParams['Epop'] = {'cellType': 'E', 'cellModel': 'HH', 'numCells': 80}  # add dict with params for this pop
netParams.popParams['RSpop'] = {'cellType': 'RS', 'cellModel': 'HH', 'numCells': 30}  # add dict with params for this pop
netParams.popParams['FSpop'] = {'cellType': 'FS', 'cellModel': 'HH', 'numCells': 30}  # add dict with params for this pop


# Cell parameters
## E cell properties
cellRule = {'conds': {'cellType': 'E'},  'secs': {}} 	# cell rule dict
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}  														# soma params dict
cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}  									# soma geometry
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  		# soma hh mechanism
netParams.cellParams['E'] = cellRule  												# add dict to list of cell params

## RS cell properties
cellRule = {'conds': {'cellType': 'RS'},  'secs': {}} 	# cell rule dict
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}  														# soma params dict
cellRule['secs']['soma']['geom'] = {'diam': 15.8, 'L': 15.8, 'Ra': 110.0}  									# soma geometry
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.13, 'gkbar': 0.036, 'gl': 0.003, 'el': -80}  		# soma hh mechanism
netParams.cellParams['RS'] = cellRule  												# add dict to list of cell params

## FS cell properties
cellRule = {'conds': {'cellType': 'FS'},  'secs': {}} 	# cell rule dict
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}  														# soma params dict
cellRule['secs']['soma']['geom'] = {'diam': 12.8, 'L': 12.8, 'Ra': 115.0}  									# soma geometry
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.11, 'gkbar': 0.036, 'gl': 0.003, 'el': -75}  		# soma hh mechanism
netParams.cellParams['FS'] = cellRule  												# add dict to list of cell params


# Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': 0}
netParams.synMechParams['GABA'] = {'mod': 'Exp2Syn', 'tau1': 0.2, 'tau2': 2.0, 'e': -70}


# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 20, 'noise': 0.5, 'start': 1}
netParams.stimTargetParams['bkg->PYR1'] = {'source': 'bkg', 'conds': {'pop': 'Epop'}, 'weight': 0.1, 'delay': 5}


# Connectivity parameters (rules)
netParams.connParams['E->RS'] = {
    'preConds': {'pop': 'Epop'},
    'postConds': {'pop': 'RSpop'},
    'probability': 0.1,
    'weight': 0.02,
    'delay': 5,
    'synMech': 'AMPA'}

netParams.connParams['E->FS'] = {
    'preConds': {'pop': 'Epop'},
    'postConds': {'cellType': 'FS'},
    'probability': 0.1,
    'weight': 0.02,
    'delay': 5,
    'synMech': 'AMPA'}

netParams.connParams['I->E'] = {
    'preConds': {'cellType': ['RS','FS']},
    'postConds': {'pop': 'Epop'},
    'probability': 0.2,
    'weight': 0.1,
    'delay': 5,
    'synMech': 'GABA'}
