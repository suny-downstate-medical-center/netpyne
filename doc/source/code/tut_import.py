from netpyne import specs, sim, utils

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

## Population parameters
netParams.addPopParams('HH_pop', {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'HH'}) 
netParams.addPopParams('HH3D_pop', {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'HH3D'}) 
netParams.addPopParams('Traub_pop', {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Traub'})
netParams.addPopParams('Mainen_pop', {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Mainen'})
netParams.addPopParams('Friesen_pop', {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Friesen'})
netParams.addPopParams('Izhi03a_pop', {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Izhi2003a'}) 
netParams.addPopParams('Izhi03b_pop', {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Izhi2003b'}) 
netParams.addPopParams('Izhi07a_pop', {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Izhi2007a'}) 
netParams.addPopParams('Izhi07b_pop', {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Izhi2007b'}) 
netParams.addPopParams('background', {'rate': 50, 'noise': 0.5, 'cellModel': 'NetStim'})


### HH
netParams.importCellParams(label='PYR_HH_rule', conds={'cellType': 'PYR', 'cellModel': 'HH'},
	fileName='HHCellFile.py', cellName='HHCellClass', importSynMechs=True)

### HH3D
cellRule = netParams.importCellParams(label='PYR_HH3D_rule', conds={'cellType': 'PYR', 'cellModel': 'HH3D'}, 
	fileName='geom.hoc', cellName='E21', importSynMechs=True)
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  	# soma hh mechanism
for secName in cellRule['secs']:
 	cellRule['secs'][secName]['mechs']['pas'] = {'g': 0.0000357, 'e': -70}
 	cellRule['secs'][secName]['geom']['cm'] = 1

### Traub
cellRule = netParams.importCellParams(label='PYR_Traub_rule', conds= {'cellType': 'PYR', 'cellModel': 'Traub'}, 
	fileName='pyr3_traub.hoc', cellName='pyr3')
somaSec = cellRule['secLists']['Soma'][0] 
cellRule['secs'][somaSec]['spikeGenLoc'] = 0.5

### Mainen
netParams.importCellParams(label='PYR_Mainen_rule', conds={'cellType': 'PYR', 'cellModel': 'Mainen'}, 
	fileName='mainen.py', cellName='PYR2')

### Friesen
cellRule = netParams.importCellParams(label='PYR_Friesen_rule', conds={'cellType': 'PYR', 'cellModel': 'Friesen'}, 
	fileName='friesen.py', cellName='MakeRSFCELL')
cellRule['secs']['axon']['spikeGenLoc'] = 0.5  # spike generator location.

### Izhi2003a (independent voltage)
cellRule = netParams.importCellParams(label='PYR_Izhi03a_rule', conds={'cellType': 'PYR', 'cellModel':'Izhi2003a'},
	fileName='izhi2003Wrapper.py', cellName='IzhiCell',  cellArgs={'type':'tonic spiking', 'host':'dummy'})
cellRule['secs']['soma']['pointps']['Izhi2003a_0']['vref'] = 'V' # specify that uses its own voltage V

### Izhi2003b (section voltage)
netParams.importCellParams(label='PYR_Izhi03b_rule', conds={'cellType': 'PYR', 'cellModel':'Izhi2003b'},
		fileName='izhi2003Wrapper.py', cellName='IzhiCell',  cellArgs={'type':'tonic spiking'})

### Izhi2007a (independent voltage)
cellRule = netParams.importCellParams(label='PYR_Izhi07a_rule', conds={'cellType': 'PYR', 'cellModel':'Izhi2007a'}, 
	fileName='izhi2007Wrapper.py', cellName='IzhiCell',  cellArgs={'type':'RS', 'host':'dummy'})
cellRule['secs']['soma']['pointps']['Izhi2007a_0']['vref'] = 'V' # specify that uses its own voltage V
cellRule['secs']['soma']['pointps']['Izhi2007a_0']['synList'] = ['AMPA', 'NMDA', 'GABAA', 'GABAB']  # specify its own synapses

### Izhi2007b (section voltage)
netParams.importCellParams(label='PYR_Izhi07b_rule', conds={'cellType': 'PYR', 'cellModel':'Izhi2007b'},
	fileName='izhi2007Wrapper.py', cellName='IzhiCell',  cellArgs={'type':'RS'})


## Synaptic mechanism parameters
netParams.addSynMechParams('AMPA', {'mod': 'Exp2Syn', 'tau1': 1.0, 'tau2': 5.0, 'e': 0})  # soma NMDA synapse
 

## Connectivity params
netParams.addConnParams('bg1',
	{'preConds': {'popLabel': 'background'}, 'postConds': {'cellType': 'PYR', 'cellModel': ['Traub', 'HH', 'HH3D', 'Mainen', 'Izhi2003b', 'Izhi2007b']}, # background -> PYR (weight=0.1)
	'connFunc': 'fullConn', 	# connectivity function (all-to-all)
	'weight': 0.1, 			# synaptic weight 
	'delay': 5,					# transmission delay (ms) 
	'sec': 'soma'})		

netParams.addConnParams('bg2',
	{'preConds': {'popLabel': 'background'}, 'postConds': {'cellType': 'PYR', 'cellModel': ['Friesen','Izhi2003a', 'Izhi2007a']}, # background -> PYR (weight = 10)
	'connFunc': 'fullConn', 	# connectivity function (all-to-all)
	'weight': 5, 				# synaptic weight 
	'delay': 5,					# transmission delay (ms) 
	'synMech':'AMPA',
	'sec': 'soma'})				

netParams.addConnParams('recurrent',
	{'preConds': {'cellType': 'PYR'}, 'postConds': {'cellType': 'PYR'},  #  PYR -> PYR random
	'connFunc': 'convConn', 	# connectivity function (random)
	'convergence': 'uniform(0,10)', 			# max number of incoming conns to cell
	'weight': 0.001, 			# synaptic weight 
	'delay': 5,					# transmission delay (ms) 
	'sec': 'soma'})				# section to connect to


# Simulation options
simConfig = specs.SimConfig()					# object of class SimConfig to store simulation configuration
simConfig.duration = 1*1e3 			# Duration of the simulation, in ms
simConfig.dt = 0.025 				# Internal integration timestep to use
simConfig.verbose = False			# Show detailed messages 
simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
simConfig.recordStep = 1 			# Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'model_output'  # Set file output name
simConfig.savePickle = False 		# Save params, network and sim output to pickle file

simConfig.addAnalysis('plotRaster', {'orderInverse': True})			# Plot a raster
simConfig.addAnalysis('plotTraces', {'include': [0]}) 			# Plot recorded traces for this list of cells


# Create network and run simulation
sim.createSimulateAnalyze(netParams = netParams, simConfig = simConfig)    
   
# import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty
