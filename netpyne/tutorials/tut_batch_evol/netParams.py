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
if cfg.networkType == 'simple':

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
	}

# --------------------------------------------------------
# Complex network
# --------------------------------------------------------
elif cfg.networkType == 'complex':

	netParams.sizeX = 100 # x-dimension (horizontal length) size in um
	netParams.sizeY = 1000 # y-dimension (vertical height or cortical depth) size in um
	netParams.sizeZ = 100 # z-dimension (horizontal length) size in um
	netParams.propVelocity = 100.0 # propagation velocity (um/ms)
	netParams.probLengthConst = cfg.probLengthConst # length constant for conn probability (um)


	## Population parameters
	netParams.popParams['E2'] = {'cellType': 'E', 'numCells': 50, 'yRange': [100,300], 'cellModel': 'HH'}
	netParams.popParams['I2'] = {'cellType': 'I', 'numCells': 50, 'yRange': [100,300], 'cellModel': 'HH'}
	netParams.popParams['E4'] = {'cellType': 'E', 'numCells': 50, 'yRange': [300,600], 'cellModel': 'HH'}
	netParams.popParams['I4'] = {'cellType': 'I', 'numCells': 50, 'yRange': [300,600], 'cellModel': 'HH'}
	netParams.popParams['E5'] = {'cellType': 'E', 'numCells': 50, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}
	netParams.popParams['I5'] = {'cellType': 'I', 'numCells': 50, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}


	## Cell property rules
	cellRule = {'conds': {'cellType': 'E'},  'secs': {}}  # cell rule dict
	cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                              # soma params dict
	cellRule['secs']['soma']['geom'] = {'diam': 15, 'L': 14, 'Ra': 120.0}                   # soma geometry
	cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.13, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}      # soma hh mechanism
	netParams.cellParams['Erule'] = cellRule                          # add dict to list of cell params

	cellRule = {'conds': {'cellType': 'I'},  'secs': {}}  # cell rule dict
	cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                              # soma params dict
	cellRule['secs']['soma']['geom'] = {'diam': 10.0, 'L': 9.0, 'Ra': 110.0}                  # soma geometry
	cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.11, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}      # soma hh mechanism
	netParams.cellParams['Irule'] = cellRule                          # add dict to list of cell params


	## Synaptic mechanism parameters
	netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 5.3, 'e': 0}  # NMDA synaptic mechanism
	netParams.synMechParams['inh'] = {'mod': 'Exp2Syn', 'tau1': 0.6, 'tau2': 8.5, 'e': -75}  # GABA synaptic mechanism


	# Stimulation parameters
	netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 20, 'noise': 0.3}
	netParams.stimTargetParams['bkg->all'] = {'source': 'bkg', 'conds': {'cellType': ['E','I']}, 'weight': cfg.stimWeight, 'delay': 'max(1, normal(5,2))', 'synMech': 'exc'}


	## Cell connectivity rules
	netParams.connParams['E->all'] = {
	  'preConds': {'cellType': 'E'}, 'postConds': {'y': [100,1000]},  #  E -> all (100-1000 um)
	  'probability': cfg.probEall,                  # probability of connection
	  'weight': str(cfg.weightEall)+'*post_ynorm',         # synaptic weight
	  'delay': 'dist_3D/propVelocity',      # transmission delay (ms)
	  'synMech': 'exc'}                     # synaptic mechanism

	netParams.connParams['I->E'] = {
	  'preConds': {'cellType': 'I'}, 'postConds': {'pop': ['E2','E4','E5']},       #  I -> E
	  'probability': str(cfg.probIE)+'*exp(-dist_3D/probLengthConst)',   # probability of connection
	  'weight': cfg.weightIE,                                      # synaptic weight
	  'delay': 'dist_3D/propVelocity',                      # transmission delay (ms)
	  'synMech': 'inh'}                                     # synaptic mechanism
