from netpyne import init, utils

# Network parameters
netParams = {}  # dictionary to store sets of network parameters

## Population parameters
netParams['popParams'] = []  # list of populations - each item will contain dict with pop params
netParams['popParams'].append({'popLabel': 'HH_pop', 'cellType': 'PYR', 'numCells': 5, 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'HH3D_pop', 'cellType': 'PYR', 'numCells': 5, 'cellModel': 'HH3D'}) 
netParams['popParams'].append({'popLabel': 'Traub_pop', 'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Traub'})
netParams['popParams'].append({'popLabel': 'Mainen_pop', 'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Mainen'})
netParams['popParams'].append({'popLabel': 'Friesen_pop', 'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Friesen'})
netParams['popParams'].append({'popLabel': 'Izhi03b_pop', 'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Izhi2003a'}) 
netParams['popParams'].append({'popLabel': 'Izhi03b_pop', 'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Izhi2003b'}) 
netParams['popParams'].append({'popLabel': 'Izhi07a_pop', 'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Izhi2007a'}) 
netParams['popParams'].append({'popLabel': 'Izhi07b_pop', 'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Izhi2007b'}) 
netParams['popParams'].append({'popLabel': 'background', 'rate': 50, 'noise': 0.5, 'source': 'random', 'cellModel': 'NetStim'})

## Cell property rules
netParams['cellParams'] = [] # list of cell property rules - each item will contain dict with cell properties

### HH
cellRule = {'label': 'PYR_HH_rule', 'conditions': {'cellType': 'PYR', 'cellModel': 'HH'},  'sections': {}} 	# cell rule dict
cellRule['sections'] = utils.importCell(fileName='HHCellFile.py', cellName='HHCellClass')
netParams['cellParams'].append(cellRule)  												# add dict to list of cell parameters

### HH3D
cellRule = {'label': 'PYR_HH3D_rule', 'conditions': {'cellType': 'PYR', 'cellModel': 'HH3D'},  'sections': {}} 	# cell rule dict
cellRule['sections'] = utils.importCell(fileName='geom.hoc', cellName='E21')
cellRule['sections']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  		# soma hh mechanism
for secName in cellRule['sections']:
	cellRule['sections'][secName]['mechs']['pas'] = {'g': 0.0000357, 'e': -70}
	cellRule['sections'][secName]['geom']['cm'] = 10
cellRule['sections']['soma']['syns']['NMDA'] = {'_type': 'Exp2Syn', '_loc': 0.5, 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  	# soma NMDA synapse
netParams['cellParams'].append(cellRule)  

### Traub
cellRule = {'label': 'PYR_Traub_rule', 'conditions': {'cellType': 'PYR', 'cellModel': 'Traub'},  'sections': {}, 'sectionLists': {}} 	# cell rule dict
utils.importCell(cellRule = cellRule, fileName='pyr3_traub.hoc', cellName='pyr3')
somaSec = cellRule['sectionLists']['Soma'][0] 
cellRule['sections'][somaSec]['syns']['NMDA'] = {'_type': 'Exp2Syn', '_loc': 0.5, 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  	# soma NMDA synapse
netParams['cellParams'].append(cellRule)  

### Mainen
cellRule = {'label': 'PYR_Mainen_rule', 'conditions': {'cellType': 'PYR', 'cellModel': 'Mainen'},  'sections': {}} 	# cell rule dict
cellRule['sections'] = utils.importCell(fileName='mainen.py', cellName='PYR2')
cellRule['sections']['soma']['syns']['NMDA'] = {'_type': 'Exp2Syn', '_loc': 0.5, 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  	# soma NMDA synapse
netParams['cellParams'].append(cellRule)  

### Friesen
cellRule = {'label': 'PYR_Friesen_rule', 'conditions': {'cellType': 'PYR', 'cellModel': 'Friesen'},  'sections': {}} 	# cell rule dict
cellRule['sections'] = utils.importCell(fileName='friesen.py', cellName='MakeRSFCELL')
cellRule['sections']['soma']['syns']['NMDA'] = {'_type': 'Exp2Syn', '_loc': 0.5, 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  	# soma NMDA synapse
cellRule['sections']['axon']['spikeGenLoc'] = 0.5  # spike generator location.
netParams['cellParams'].append(cellRule)  

### Izhi2003a (independent voltage)
cellRule = {'label': 'PYR_Izhi03a_rule', 'conditions': {'cellType': 'PYR', 'cellModel':'Izhi2003a'},  'sections': {}} 	# cell rule dict
cellRule['sections'] = utils.importCell(
	fileName='izhi2003Wrapper.py', cellName='IzhiCell',  cellArgs={'type':'tonic spiking', 'host':'dummy'})
cellRule['sections']['soma']['pointps']['Izhi2003a_0']['_vref'] = 'V' # specify that uses its own voltage V
netParams['cellParams'].append(cellRule)  	

### Izhi2003b (section voltage)
cellRule = {'label': 'PYR_Izhi03b_rule', 'conditions': {'cellType': 'PYR', 'cellModel':'Izhi2003b'},  'sections': {}} 	# cell rule dict
cellRule['sections'] = utils.importCell(
	fileName='izhi2003Wrapper.py', cellName='IzhiCell',  cellArgs={'type':'tonic spiking'})
cellRule['sections']['soma']['syns']['NMDA'] = {'_type': 'Exp2Syn', '_loc': 0.5, 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  	# soma NMDA synapse
netParams['cellParams'].append(cellRule)  	

### Izhi2007a (independent voltage)
cellRule = {'label': 'PYR_Izhi07a_rule', 'conditions': {'cellType': 'PYR', 'cellModel':'Izhi2007a'},  'sections': {}} 	# cell rule dict
cellRule['sections'] = utils.importCell(
	fileName='izhi2007Wrapper.py', cellName='IzhiCell',  cellArgs={'type':'RS', 'host':'dummy'})
cellRule['sections']['soma']['pointps']['Izhi2007a_0']['_vref'] = 'V' # specify that uses its own voltage V
cellRule['sections']['soma']['pointps']['Izhi2007a_0']['_synList'] = ['AMPA', 'NMDA', 'GABAA', 'GABAB']  # specify its own synapses
netParams['cellParams'].append(cellRule)  	

### Izhi2007b (section voltage)
cellRule = {'label': 'PYR_Izhi07b_rule', 'conditions': {'cellType': 'PYR', 'cellModel':'Izhi2007b'},  'sections': {}} 	# cell rule dict
cellRule['sections'] = utils.importCell(
	fileName='izhi2007Wrapper.py', cellName='IzhiCell',  cellArgs={'type':'RS'})
cellRule['sections']['soma']['syns']['NMDA'] = {'_type': 'Exp2Syn', '_loc': 0.5, 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  	# soma NMDA synapse
netParams['cellParams'].append(cellRule)  	


## Cell connectivity rules
netParams['connParams'] = []  

netParams['connParams'].append({
	'preTags': {'popLabel': 'background'}, 'postTags': {'cellType': 'PYR', 'cellModel': ['Traub', 'Mainen', 'Izhi2003b', 'Izhi2007b']}, # background -> PYR (weight=0.001)
	'connFunc': 'fullConn', 	# connectivity function (all-to-all)
	'weight': 0.001, 			# synaptic weight 
	'delay': 5,					# transmission delay (ms) 
	'sec': 'soma'})		

netParams['connParams'].append({
	'preTags': {'popLabel': 'background'}, 'postTags': {'cellType': 'PYR', 'cellModel': ['HH', 'HH3D']}, # background -> PYR (weight=0.1)
	'connFunc': 'fullConn', 	# connectivity function (all-to-all)
	'weight': 0.1, 			# synaptic weight 
	'delay': 5,					# transmission delay (ms) 
	'sec': 'soma'})		

netParams['connParams'].append({
	'preTags': {'popLabel': 'background'}, 'postTags': {'cellType': 'PYR', 'cellModel': ['Friesen', 'Izhi2003a', 'Izhi2007a']}, # background -> PYR (weight = 10)
	'connFunc': 'fullConn', 	# connectivity function (all-to-all)
	'weight': 5, 				# synaptic weight 
	'delay': 5,					# transmission delay (ms) 
	'synReceptor':'NMDA',
	'sec': 'soma'})				

netParams['connParams'].append({
	'preTags': {'cellType': 'PYR'}, 'postTags': {'cellType': 'PYR'},  #  PYR -> PYR random
	'connFunc': 'convConn', 	# connectivity function (random)
	'convergence': 'uniform(0,10)', 			# max number of incoming conns to cell
	'weight': 0.001, 			# synaptic weight 
	'delay': 5,					# transmission delay (ms) 
	'sec': 'soma'})				# section to connect to


# Simulation options
simConfig = {}
simConfig['duration'] = 1*1e3 			# Duration of the simulation, in ms
simConfig['dt'] = 0.025 				# Internal integration timestep to use
simConfig['verbose'] = False			# Show detailed messages 
simConfig['recordTraces'] = {'V_soma':{'sec':'soma','pos':0.5,'var':'v'}}  # Dict with traces to record
simConfig['recordStep'] = 1 			# Step size in ms to save data (eg. V traces, LFP, etc)
simConfig['filename'] = 'model_output'  # Set file output name
simConfig['savePickle'] = False 		# Save params, network and sim output to pickle file
simConfig['plotRaster'] = True 			# Plot a raster
simConfig['plotCells'] = [1] 			# Plot recorded traces for this list of cells


# Create network and run simulation
init.createAndSimulate(netParams = netParams, simConfig = simConfig)    
   
# import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty
