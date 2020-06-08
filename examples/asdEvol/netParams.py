from netpyne import specs, sim

try:
	from __main__ import cfg
except:
	from simConfig import cfg

# Network parameters
netParams = specs.NetParams()

# --------------------------------------------------------
# Simple network
# --------------------------------------------------------

# Population parameters
netParams.popParams['S'] = {'cellType': 'PYR', 'numCells': 20, 'cellModel': 'HH'}
netParams.popParams['M'] = {'cellType': 'PYR', 'numCells': 20, 'cellModel': 'HH'}

# Cell property rules
cellRule = {'conds': {'cellType': 'PYR'},  'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}
cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}
netParams.cellParams['PYRrule'] = cellRule

# Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 5, 'e': 0}

# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.5}
netParams.stimTargetParams['bkg->PYR'] = {'source': 'bkg', 'conds': {'cellType': 'PYR'}, 'weight': 0.01, 'delay': 5, 'synMech': 'exc'}

# Cell connectivity rules
netParams.connParams['S->M'] = {
    'preConds': {'pop': 'S'},
    'postConds': {'pop': 'M'},
    'probability': cfg.prob,
    'weight': cfg.weight,
    'delay': cfg.delay,
    'synMech': 'exc'
	
