from netpyne import sim

# Network parameters
netParams = {}  # dictionary to store sets of network parameters

## Population parameters
netParams['popParams'].append({'popLabel': 'S', 'cellType': 'PYR', 'numCells': 20, 'cellModel': 'Izhi2007b'}) 
netParams['popParams'].append({'popLabel': 'M', 'cellType': 'PYR', 'numCells': 20, 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'background', 'rate': 100, 'noise': 0.5, 'cellModel': 'NetStim'})

## Cell property rules
netParams.addCellParams('PYR_HH_rule',			# cell rule label
	{'conds': {'cellType': 'PYR', 'cellModel': 'HH'},  	# properties will be applied to cells that match these conditions	
	'secs': 																					# sections 
		{'soma': 
			{'geom': {'diam': 18.8, 'L': 18.8, 'Ra': 123.0},									# soma geometry 
			'mechs': {'hh': {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}}},		# soma mechanisms
		'dend': 
			{'geom': {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1},							# dend geometry
			'topol': {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0},						# dend topology
			'mechs': {'pas': {'g': 0.0000357, 'e': -70}}}}}) 									# dend mechanisms

netParams.addCellParams('PYR_Izhi_rule',
	{'conds': {'cellType': 'PYR', 'cellModel':'Izhi2007b'},
	'secs': 
		{'soma': 
			{'geom': {'diam': 10.0, 'L': 10.0, 'cm': 31.831},
			'pointps': {'Izhi':
				{'mod':'Izhi2007b', 'C':1, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}}}}})

## Synaptic mechanism parameters
netParams['synMechParams'].append({'label': 'exc', 'mod': 'Exp2Syn', 'tau1': 1.0, 'tau2': 5.0, 'e': 0})  # excitatory synapse
 

## Cell connectivity rules
netParams['connParams'] = []  
netParams['connParams'].append({'preConds': {'popLabel': 'S'}, 'postConds': {'popLabel': 'M'},  #  S -> M
	'probability': 0.1, 		# probability of connection
	'weight': 0.005, 			# synaptic weight 
	'delay': 5,					# transmission delay (ms) 
	'sec': 'dend',				# section to connect to
	'loc': 1.0,
	'synMech': 'exc'})   	# target synapse 
netParams['connParams'].append({'preConds': {'popLabel': 'background'}, 'postConds': {'cellType': 'PYR'}, # background -> PYR
	'weight': 0.01, 				# synaptic weight 
	'delay': 5, 				# transmission delay (ms) 
	'synMech': 'exc'})  	# target synapse 


# Simulation options
simConfig = {}
simConfig['duration'] = 1*1e3 			# Duration of the simulation, in ms
simConfig['dt'] = 0.025 				# Internal integration timestep to use
simConfig['verbose'] = False 			# Show detailed messages 
simConfig['recordTraces'] = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
simConfig['recordStep'] = 1 			# Step size in ms to save data (eg. V traces, LFP, etc)
simConfig['filename'] = 'model_output'  # Set file output name
simConfig['savePickle'] = False 		# Save params, network and sim output to pickle file

simConfig['analysis'] = {}
simConfig['analysis']['plotRaster'] = True 			# Plot a raster
simConfig['analysis']['plotTraces'] = {'include': [1]} 			# Plot recorded traces for this list of cells
simConfig['analysis']['plot2Dnet'] = True           # plot 2D visualization of cell positions and connections


# Create network and run simulation
sim.createAndSimulate(netParams = netParams, simConfig = simConfig)    
   
# import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty
