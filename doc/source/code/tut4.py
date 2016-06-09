from netpyne import sim

# Network parameters
netParams = {}  # dictionary to store sets of network parameters

## Population parameters
netParams['popParams'] = []  # list of populations - each item will contain dict with pop params
netParams['popParams'].append({'popLabel': 'S', 'cellType': 'PYR', 'numCells': 20, 'cellModel': 'Izhi2007b'}) 
netParams['popParams'].append({'popLabel': 'M', 'cellType': 'PYR', 'numCells': 20, 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'background', 'rate': 100, 'noise': 0.5, 'cellModel': 'NetStim'})

## Cell property rules
netParams['cellParams'] = [] # list of cell property rules - each item will contain dict with cell properties
cellRule = {'label': 'PYR_HH_rule', 'conditions': {'cellType': 'PYR', 'cellModel': 'HH'},  'sections': {}} 	# cell rule dict
soma = {'geom': {}, 'mechs': {}, 'synMechs': {}}  											# soma params dict
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}  									# soma geometry
soma['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  		# soma hh mechanisms
dend = {'geom': {}, 'topol': {}, 'mechs': {}, 'synMechs': {}}  								# dend params dict
dend['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
dend['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology 
dend['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 										# dend mechanisms
cellRule['sections'] = {'soma': soma, 'dend': dend}  									# add soma section to dict
netParams['cellParams'].append(cellRule)  												# add dict to list of cell parameters

cellRule = {'label': 'PYR_Izhi_rule', 'conditions': {'cellType': 'PYR', 'cellModel':'Izhi2007b'},  'sections': {}} 	# cell rule dict
soma = {'geom': {}, 'pointps': {}, 'synMechs': {}}  										# soma params dict
soma['geom'] = {'diam': 10.0, 'L': 10.0, 'cm': 31.831}  									# soma geometry
soma['pointps']['Izhi'] = {'mod':'Izhi2007b', 
	'C':1, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}	# soma poinpt process
cellRule['sections'] = {'soma': soma}  									# add soma section to dict
netParams['cellParams'].append(cellRule)  	

## Synaptic mechanism parameters
netParams['synMechParams'] = []
netParams['synMechParams'].append({'label': 'exc', 'mod': 'Exp2Syn', 'tau1': 1.0, 'tau2': 5.0, 'e': 0})  # excitatory synapse
 

## Cell connectivity rules
netParams['connParams'] = []  
netParams['connParams'].append({'preTags': {'popLabel': 'S'}, 'postTags': {'popLabel': 'M'},  #  S -> M
	'probability': 0.1, 		# probability of connection
	'weight': 0.005, 			# synaptic weight 
	'delay': 5,					# transmission delay (ms) 
	'sec': 'dend',				# section to connect to
	'loc': 1.0,
	'synMech': 'exc'})   	# target synapse 
netParams['connParams'].append({'preTags': {'popLabel': 'background'}, 'postTags': {'cellType': 'PYR'}, # background -> PYR
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
simConfig['plotRaster'] = True 			# Plot a raster
simConfig['plotCells'] = [1] 			# Plot recorded traces for this list of cells
simConfig['plot2Dnet'] = True           # plot 2D visualization of cell positions and connections


# Create network and run simulation
sim.createAndSimulate(netParams = netParams, simConfig = simConfig)    
   
# import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty
