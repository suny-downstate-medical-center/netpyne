from netpyne import specs, sim
import numpy as np

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

## Population parameters
numCells = 2
netParams.popParams['IT5B'] = {'numCells': numCells, 'cellType': 'IT', 'cellModel': 'HH', }

## Cell property rules
netParams.loadCellParamsRule(label='IT5B_reduced', fileName='IT5B_reduced_cellParams.pkl')
netParams.cellParams['IT5B_reduced']['conds'] = {'cellType': 'IT'}

## Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # excitatory synaptic mechanism


netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.0}
netParams.stimTargetParams['bg1'] = {'source': 'bkg', 
									'conds': {'pop': 'IT5B'}, 
									'weight': 0.1, 
									'delay': 5, 
									'sec': ['soma', 'Adend1', 'Adend2', 'Adend3', 'Bdend'],
									'synsPerConn': 3}


# Simulation options
simConfig = specs.SimConfig()		# object of class SimConfig to store simulation configuration

simConfig.duration = 1*1e3 			# Duration of the simulation, in ms
simConfig.dt = 0.025			# Internal integration timestep to use
simConfig.verbose = 1  # Show detailed messages
simConfig.seeds = {'conn': 4321, 'stim': 1234, 'loc': 4321}
simConfig.hParams = {'celsius': 34, 'v_init': -80}
simConfig.oneSynPerNetcon = False
simConfig.distributeSynsUniformly = False
simConfig.connRandomSecFromList = True

simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
simConfig.recordStep = 0.05 			# Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.saveJson = True 	
simConfig.filename = 'model3'  # Set file output name
 
simConfig.analysis['plotRaster'] = True 			# Plot a raster
simConfig.analysis['plotTraces'] = {'include': [0]} 			# Plot recorded traces for this list of cells

# Create network and run simulation
sim.create(netParams = netParams, simConfig = simConfig)


