from netpyne import init

# Network parameters
netParams = {}  # dictionary to store sets of network parameters

## Population parameters
netParams['popParams'] = []  # list of populations - each item will contain dict with pop params
netParams['popParams'].append({'popLabel': 'S', 'cellType': 'PYR', 'numCells': 20, 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'M', 'cellType': 'PYR', 'numCells': 20, 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'background', 'rate': 10, 'noise': 0.5, 'cellModel': 'NetStim'})

## Cell property rules
netParams['cellParams'] = [] # list of cell property rules - each item will contain dict with cell properties
cellRule = {'label': 'PYRrule', 'conditions': {'cellType': 'PYR'},  'sections': {}} 	# cell rule dict
soma = {'geom': {}, 'mechs': {}, 'synMechs': {}}  											# soma params dict
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}  									# soma geometry
soma['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  		# soma hh mechanisms
dend = {'geom': {}, 'topol': {}, 'mechs': {}, 'synMechs': {}}  								# dend params dict
dend['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
dend['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology 
dend['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 										# dend mechanisms
cellRule['sections'] = {'soma': soma, 'dend': dend}  									# add soma and dend sections to dict
netParams['cellParams'].append(cellRule)  												# add dict to list of cell parameters


## Synaptic mechanism parameters
netParams['synMechParams'] = []
netParams['synMechParams'].append({'label': 'exc', 'mod': 'Exp2Syn', 'tau1': 1.0, 'tau2': 5.0, 'e': 0})  # excitatory synaptic mechanism
 

## Cell connectivity rules
netParams['connParams'] = []  
netParams['connParams'].append({'preTags': {'popLabel': 'S'}, 'postTags': {'popLabel': 'M'},  #  S -> M
	'probability': 0.5, 		# probability of connection
	'weight': 0.01, 			# synaptic weight 
	'delay': 5,					# transmission delay (ms) 
	'sec': 'dend',				# section to connect to
	'loc': '1.0',				# location of synapse
	'synMech': 'exc'})   		# target synaptic mechanism
netParams['connParams'].append({'preTags': {'popLabel': 'background'}, 'postTags': {'cellType': 'PYR'}, # background -> PYR
	'weight': 0.01, 				# synaptic weight 
	'delay': 5, 				# transmission delay (ms) 
	'synMech': 'exc'})  	# target synapse 


# Simulation options
simConfig = {}
simConfig['duration'] = 1*1e3 			# Duration of the simulation, in ms
simConfig['dt'] = 0.025 				# Internal integration timestep to use
simConfig['verbose'] = False  			# Show detailed messages 
simConfig['recordTraces'] = {'V_soma':{'sec':'soma','pos':0.5,'var':'v'}}  # Dict with traces to record
simConfig['recordStep'] = 1 			# Step size in ms to save data (eg. V traces, LFP, etc)
simConfig['filename'] = 'model_output'  # Set file output name
simConfig['savePickle'] = False 		# Save params, network and sim output to pickle file
simConfig['plotRaster'] = True 			# Plot a raster
simConfig['plotCells'] = [1]	 		# Plot recorded traces for this list of cells


# Create network and run simulation
init.createAndSimulate(netParams = netParams, simConfig = simConfig)    
   
# import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty
