from netpyne import specs, sim

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

## Population parameters
netParams.addPopParams('S', {'cellType': 'PYR', 'numCells': 20, 'cellModel': 'HH'}) 
netParams.addPopParams('M', {'cellType': 'PYR', 'numCells': 20, 'cellModel': 'HH'}) 
netParams.addPopParams('background', {'rate': 10, 'noise': 0.5, 'cellModel': 'NetStim'})

## Cell property rules
cellRule = {'conds': {'cellType': 'PYR'},  'secs': {}} 	# cell rule dict
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}  														# soma params dict
cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}  									# soma geometry
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  		# soma hh mechanism
netParams.addCellParams('PYRrule', cellRule)  												# add dict to list of cell params

## Synaptic mechanism parameters
netParams.addSynMechParams('exc', {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 5.0, 'e': 0})  # excitatory synaptic mechanism
 
## Cell connectivity rules
netParams.addConnParams('S->M', #  S -> M label
	{'preConds': {'popLabel': 'S'}, # conditions of presyn cells
	'postConds': {'popLabel': 'M'}, # conditions of postsyn cells
	'probability': 0.5, 		# probability of connection
	'weight': 0.01, 			# synaptic weight 
	'delay': 5,					# transmission delay (ms) 
	'synMech': 'exc'})   		# synaptic mechanism 

netParams.addConnParams('bg->PYR', # background -> PYR label
	{'preConds': {'popLabel': 'background'}, 
	'postConds': {'cellType': 'PYR'}, 
	'weight': 0.01, 				# synaptic weight 
	'delay': 5, 				# transmission delay (ms) 
	'synMech': 'exc'})  		# synaptic mechanism 


# Simulation options
simConfig = specs.SimConfig()		# object of class SimConfig to store simulation configuration

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
