from netpyne import specs, sim

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

netParams.shape = 'cylinder' # cylindrical (column-like) volume

#------------------------------------------------------------------------------
# General connectivity parameters
#------------------------------------------------------------------------------
netParams.scaleConnWeight = 1.0 # Connection weight scale factor (default if no model specified)
netParams.scaleConnWeightModels = {'HH_simple': 1.0, 'HH_reduced': 1.0, 'HH_full': 1.0} #scale conn weight factor for each cell model
netParams.scaleConnWeightNetStims = 1.0 #0.5  # scale conn weight factor for NetStims
netParams.defaultThreshold = 0.0 # spike threshold, 10 mV is NetCon default, lower it for all cells
netParams.defaultDelay = 2.0 # default conn delay (ms)
netParams.propVelocity = 500.0 # propagation velocity (um/ms)
netParams.probLambda = 100.0  # length constant (lambda) for connection probability decay (um)
netParams.defineCellShapes = True  # convert stylized geoms to 3d points



## Population parameters
netParams.popParams['IT5B'] = {'cellType': 'IT', 'numCells': 1, 'cellModel': 'HH'}
netParams.popParams['TVL'] = { 'numCells': 100, 'rate': 15, 'noise': 1.0, 'start':0, 'cellModel': 'NetStim'}

## Cell property rules
netParams.loadCellParamsRule(label='IT5B_reduced', fileName='IT5B_reduced_cellParams.pkl')
netParams.cellParams['IT5B_reduced']['conds'] = {'cellType': 'IT'}


## Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # excitatory synaptic mechanism

## Cell connectivity rules
netParams.connParams['TVL->IT5B'] = { 	#  S -> M label
	'preConds': {'pop': 'TVL'}, 	# conditions of presyn cells
	'postConds': {'pop': 'IT5B'}, # conditions of postsyn cells
	'probability': 1.0, 			# probability of connection
	'weight': 0.5, 				# synaptic weight
	'delay': 5,						# transmission delay (ms)
	'synMech': ['AMPA'],
    'synsPerConn': 1,
    'sec': ['Adend1']}   			# synaptic mechanism


# Simulation options
simConfig = specs.SimConfig()		# object of class SimConfig to store simulation configuration

simConfig.duration = 1*1e3 			# Duration of the simulation, in ms
simConfig.dt = 0.05			# Internal integration timestep to use
simConfig.verbose = False  			# Show detailed messages
simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
simConfig.recordStep = 0.1 			# Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'model3'  # Set file output name
simConfig.saveJson = True 	
simConfig.seeds = {'conn': 4321, 'stim': 1234, 'loc': 4321}
 

simConfig.hParams = {'celsius': 34, 'v_init': -0}

simConfig.printPopAvgRates = [0, simConfig.duration]

simConfig.analysis['plotRaster'] = True 			# Plot a raster
simConfig.analysis['plotTraces'] = {'include': [0]} 			# Plot recorded traces for this list of cells
#simConfig.analysis['plot2Dnet'] = True           # plot 2D visualization of cell positions and connections

# Create network and run simulation
sim.createSimulateAnalyze(netParams = netParams, simConfig = simConfig)

# import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty

