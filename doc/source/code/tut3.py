from netpyne import sim, specs

# Network parameters
netParams = specs.NetParams()  # dictionary to store sets of network parameters

## Population parameters
netParams.addPopParams('S', {'cellType': 'PYR', 'numCells': 20, 'cellModel': 'HH'}) 
netParams.addPopParams('M', {'cellType': 'PYR', 'numCells': 20, 'cellModel': 'HH'}) 
netParams.addPopParams('background', {'rate': 10, 'noise': 0.5, 'cellModel': 'NetStim'})

## Cell property rules
netParams.addCellParams('PYRrule',			# cell rule label
	{'conditions': {'cellType': 'PYR'},  	# properties will be applied to cells that match these conditions	
	'sections': 							# sections 
		{'soma':							
			{'geom': {'diam': 18.8, 'L': 18.8, 'Ra': 123.0},									# soma geometry 
			'mechs': {'hh': {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}}},			# soma mechanisms
		'dend': 
			{'geom': {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1},							# dend geometry
			'topol': {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0},						# dend topology
			'mechs': {'pas': {'g': 0.0000357, 'e': -70}}}}}) 										# dend mechanisms

# # Alternative method
# cellRule = {'conditions': {'cellType': 'PYR'},  'sections': {}} 	# cell rule dict
# soma = {'geom': {}, 'mechs': {}}  											# soma params dict
# soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}  									# soma geometry
# soma['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  		# soma hh mechanisms
# dend = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
# dend['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
# dend['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology 
# dend['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 										# dend mechanisms
# cellRule['sections'] = {'soma': soma, 'dend': dend}  									# add soma and dend sections to dict
# netParams['cellParams'].append('PYRrule', cellRule)  												# add dict to list of cell parameters

## Synaptic mechanism parameters
netParams.addSynMechParams('exc', {'mod': 'Exp2Syn', 'tau1': 1.0, 'tau2': 5.0, 'e': 0})  # excitatory synaptic mechanism
 

## Cell connectivity rules
netParams.addConnParams('S->M',
	{'preTags': {'popLabel': 'S'}, 
	'postTags': {'popLabel': 'M'},  #  S -> M
	'probability': 0.5, 		# probability of connection
	'weight': 0.01, 			# synaptic weight 
	'delay': 5,					# transmission delay (ms) 
	'sec': 'dend',				# section to connect to
	'loc': 1.0,				# location of synapse
	'synMech': 'exc'})   		# target synaptic mechanism

netParams.addConnParams('bg->PYR',
	{'preTags': {'popLabel': 'background'}, 
	'postTags': {'cellType': 'PYR'}, # background -> PYR
	'weight': 0.01, 				# synaptic weight 
	'delay': 5, 				# transmission delay (ms) 
	'synMech': 'exc'})  	# target synapse 


# Simulation options
simConfig = specs.SimConfig()

simConfig.duration = 1*1e3 			# Duration of the simulation, in ms
simConfig.dt = 0.025 				# Internal integration timestep to use
simConfig.verbose = False  			# Show detailed messages 
simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
simConfig.recordStep = 1 			# Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'model_output'  # Set file output name
simConfig.savePickle = False 		# Save params, network and sim output to pickle file

simConfig.addAnalysis('plotRaster', True) 			# Plot a raster
simConfig.addAnalysis('plotTraces', {'include': [1]}) 			# Plot recorded traces for this list of cells
simConfig.addAnalysis('plot2Dnet', True)           # plot 2D visualization of cell positions and connections


# Create network and run simulation
sim.createSimulateAnalyze(netParams = netParams, simConfig = simConfig)    
   
# import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty
