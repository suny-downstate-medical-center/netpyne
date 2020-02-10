from netpyne import specs, sim

import numpy
rng = numpy.random.RandomState()


# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters


## Population parameters
netParams.popParams['S'] = {'cellType': 'PYR', 'numCells': 20, 'cellModel': 'HH'}
netParams.popParams['M'] = {'cellType': 'PYR', 'numCells': 20, 'cellModel': 'HH'}

times = [0, 200, 400, 600, 800]
rates = [[10, 20, 30, 40, 0],
        [100, 0, 100, 0, 100],
        [40, 30, 20, 10, 0],
        [20, 0, 20, 0, 10]]

netParams.popParams['input'] = {'cellType': 'Ext', 'numCells': 4, 'cellModel': 'VecStim',
    'dynamicRates': {'rates': [rates[i] for i in range(len(rates))],
                    'times': times}} 


## Cell property rules
cellRule = {'conds': {'cellType': 'PYR'},  'secs': {}} 	# cell rule dict
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}  														# soma params dict
cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}  									# soma geometry
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  		# soma hh mechanism
netParams.cellParams['PYRrule'] = cellRule  												# add dict to list of cell params

## Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 5.0, 'e': 0}  # excitatory synaptic mechanism

# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.5}
netParams.stimTargetParams['bkg->PYR'] = {'source': 'bkg', 'conds': {'cellType': 'PYR'}, 'weight': 0.01, 'delay': 5, 'synMech': 'exc'}

## Cell connectivity rules
netParams.connParams['S->M'] = { 	#  S -> M label
	'preConds': {'pop': 'S'}, 	# conditions of presyn cells
	'postConds': {'pop': 'M'}, # conditions of postsyn cells
	'divergence': 12, 			# probability of connection
	'weight': 0.01, 				# synaptic weight
	'delay': 5,						# transmission delay (ms)
	'synMech': 'exc'}   			# synaptic mechanism


# Simulation options
simConfig = specs.SimConfig()		# object of class SimConfig to store simulation configuration

simConfig.duration = 1*1e3 			# Duration of the simulation, in ms
simConfig.dt = 0.025 				# Internal integration timestep to use
simConfig.verbose = False  			# Show detailed messages
simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
simConfig.recordStep = 0.1 			# Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'model_output'  # Set file output name
simConfig.savePickle = False 		# Save params, network and sim output to pickle file
simConfig.saveJson = True 	
simConfig.includeParamsLabel = False

simConfig.saveDataInclude = ['simData', 'simConfig', 'netParams']#, 'net']
simConfig.saveCellSecs = 0 #False
simConfig.saveCellConns = 0
# simConfig.recordLFP = [[150, y, 150] for y in [600, 800, 1000]] # only L5 (Zagha) [[150, y, 150] for y in range(200,1300,100)]

simConfig.analysis['plotRaster'] = True 			# Plot a raster
simConfig.analysis['plotTraces'] = {'include': [1]} 			# Plot recorded traces for this list of cells
#simConfig.analysis['plot2Dnet'] = True           # plot 2D visualization of cell positions and connections
#simConfig.analysis['plotLFP'] = True



# def modifyGnabar(t):
#     params = {'conds': {'cellType': 'PYR'}, 'secs': {'soma': {'mechs': {'hh': {'gnabar': 0.0}}}}}
#     sim.net.modifyCells(params)
#     print(sim.net.cells[0].secs['soma']['mechs']['hh'])


# Create network and run simulation
sim.create(netParams=netParams, simConfig=simConfig)
sim.runSim() #SimWithIntervalFunc(500, modifyGnabar)
sim.gatherData()                  			# gather spiking data and cell info from each node
sim.saveData()                    			# save params, cell info and sim output to file (pickle,mat,txt,etc)#
sim.analysis.plotData()         			# plot spike raster etc



# import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty

# check model output
#sim.checkOutput('tut2')