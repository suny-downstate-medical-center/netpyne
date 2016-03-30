from netpyne import init

# Network parameters
netParams = {}  # dictionary to store sets of network parameters

netParams['sizeX'] = 1000 # x-dimension (horizontal length) size in um
netParams['sizeY'] = 1000 # y-dimension (vertical height or cortical depth) size in um
netParams['sizeZ'] = 1 # y-dimension (vertical height or cortical depth) size in um
netParams['propVelocity'] = 100.0 # propagation velocity (um/ms)
netParams['probLengthConst'] = 200.0 # propagation velocity (um/ms)


## Population parameters
netParams['popParams'] = []  # list of populations - each item will contain dict with pop params
netParams['popParams'].append({'popLabel': 'ES', 'cellType': 'PYR', 'numCells': 100, 'xnormRange': [0,1.0], 'ynormRange': [0,0.5], 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'IS', 'cellType': 'BAS', 'numCells': 100, 'xnormRange': [0,1.0], 'ynormRange': [0,0.5], 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'EM', 'cellType': 'PYR', 'numCells': 100, 'xnormRange': [0,1.0], 'ynormRange': [0.5,1.0], 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'IM', 'cellType': 'BAS', 'numCells': 100, 'xnormRange': [0,1.0], 'ynormRange': [0.5,1.0], 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'background', 'rate': 10, 'noise': 0.5, 'cellModel': 'NetStim'})

## Cell property rules
netParams['cellParams'] = [] # list of cell property rules - each item will contain dict with cell properties
cellRule = {'label': 'PYRrule', 'conditions': {'cellType': 'PYR'},  'sections': {}} 	# cell rule dict
soma = {'geom': {}, 'mechs': {}}  											# soma params dict
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}  									# soma geometry
soma['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  		# soma hh mechanism
cellRule['sections'] = {'soma': soma}  													# add soma section to dict
netParams['cellParams'].append(cellRule)  												# add dict to list of cell par

cellRule = {'label': 'BASrule', 'conditions': {'cellType': 'BAS'},  'sections': {}} 	# cell rule dict
soma = {'geom': {}, 'mechs': {}}  											# soma params dict
soma['geom'] = {'diam': 10.0, 'L': 10.0, 'Ra': 80.0}  									# soma geometry
soma['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  		# soma hh mechanism
cellRule['sections'] = {'soma': soma}  													# add soma section to dict
netParams['cellParams'].append(cellRule)  												# add dict to list of cell par


## Synaptic mechanism parameters
netParams['synMechParams'] = []
netParams['synMechParams'].append({'label': 'exc', 'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 5.0, 'e': 0})  # NMDA synaptic mechanism
netParams['synMechParams'].append({'label': 'inh', 'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 4.0, 'e': -80})  # GABA synaptic mechanism
 

## Cell connectivity rules
netParams['connParams'] = [] 

netParams['connParams'].append({'preTags': {'cellType': 'PYR'}, 'postTags': {'cellType': ['PYR','BAS']},  #  E -> all
	'probability': '0.1*post_ynorm', 		# probability of connection
	'weight': 0.01, 						# synaptic weight 
	'delay': 'dist_3D/propVelocity',			# transmission delay (ms) 
	'synMech': 'exc'})   					# synaptic mechanism 

netParams['connParams'].append({'preTags': {'cellType': 'BAS'}, 'postTags': {'cellType': ['PYR','BAS']},  #  I -> all
	'probability': '1*exp(-dist_3D/probLengthConst)', 	# probability of connection
	'weight': 0.00, 									# synaptic weight 
	'delay': 'dist_3D/propVelocity',						# transmission delay (ms) 
	'synMech': 'inh'})   								# synaptic mechanism 

netParams['connParams'].append({'preTags': {'popLabel': 'background'}, 'postTags': {'cellType': ['PYR', 'BAS']}, # background -> all
	'weight': 0.01, 					# synaptic weight 
	'delay': 'max(1, uniform(5,2))', 	# transmission delay (ms) 
	'synMech': 'exc'})  				# synaptic mechanism 


# Simulation options
simConfig = {}
simConfig['duration'] = 1*1e3 			# Duration of the simulation, in ms
simConfig['dt'] = 0.025 				# Internal integration timestep to use
simConfig['verbose'] = True  			# Show detailed messages 
simConfig['recordTraces'] = {'V_soma':{'sec':'soma','pos':0.5,'var':'v'}}  # Dict with traces to record
simConfig['recordStep'] = 1 			# Step size in ms to save data (eg. V traces, LFP, etc)
simConfig['filename'] = 'model_output'  # Set file output name
simConfig['savePickle'] = False 		# Save params, network and sim output to pickle file
simConfig['plotRaster'] = True 			# Plot a raster
simConfig['orderRasterYnorm'] = 1 	# Order cells in raster by yfrac (default is by pop and cell id)
simConfig['plotCells'] = [1] 			# Plot recorded traces for this list of cells


# Create network and run simulation
init.createAndSimulate(netParams = netParams, simConfig = simConfig)    
   
# import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty
