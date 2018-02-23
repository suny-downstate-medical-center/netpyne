from netpyne import specs, sim

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

## Population parameters
#netParams.popParams['HH3D_pop'] = {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'HH3D'} 
netParams.popParams['Traub_pop'] = {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Traub'}


### HH3D
# cellRule = netParams.importCellParams(label='PYR_HH3D_rule', conds={'cellType': 'PYR', 'cellModel': 'HH3D'}, 
# 	fileName='geom.hoc', cellName='E21', importSynMechs=True)
# cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  	# soma hh mechanism
# for secName in cellRule['secs']:
#  	cellRule['secs'][secName]['mechs']['pas'] = {'g': 0.0000357, 'e': -70}
#  	cellRule['secs'][secName]['geom']['cm'] = 1

### Traub
cellRule = netParams.importCellParams(label='PYR_Traub_rule', conds= {'cellType': 'PYR', 'cellModel': 'Traub'}, 
	fileName='pyr3_traub.hoc', cellName='pyr3')
somaSec = cellRule['secLists']['Soma'][0] 
#netParams.renameCellParamsSec('PYR_Traub_rule', somaSec, 'soma')
cellRule['secs'][somaSec]['spikeGenLoc'] = 0.5

## Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  # soma NMDA synapse
 

# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 50, 'noise': 0.5}
netParams.stimTargetParams['bg1'] = {'source': 'bkg', 'conds': {'cellType': 'PYR', 'cellModel': ['Traub', 'HH', 'HH3D', 'Mainen', 'Izh2003b', 'Izh2007b']}, 
									'weight': 0.1, 'delay': 5, 'sec': 'soma'}
netParams.stimTargetParams['bg2'] = {'source': 'bkg', 'conds': {'cellType': 'PYR', 'cellModel': ['Friesen','Izh2003a', 'Izh2007a']}, 
									'weight': 5, 'delay': 5, 'sec': 'soma'}


## Connectivity params		
netParams.connParams['recurrent'] = {
	'preConds': {'cellType': 'PYR'}, 'postConds': {'cellType': 'PYR'},  #  PYR -> PYR random
	'connFunc': 'convConn', 	# connectivity function (random)
	'convergence': 'uniform(0,10)', 			# max number of incoming conns to cell
	'weight': 0.001, 			# synaptic weight 
	'delay': 5,					# transmission delay (ms) 
	'sec': 'soma'}				# section to connect to


# Simulation options
simConfig = specs.SimConfig()					# object of class SimConfig to store simulation configuration
simConfig.duration = 0.1*1e3 			# Duration of the simulation, in ms
simConfig.dt = 0.025 				# Internal integration timestep to use
simConfig.verbose = 0			# Show detailed messages 
simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
simConfig.recordStep = 1 			# Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'model_output'  # Set file output name
simConfig.savePickle = False 		# Save params, network and sim output to pickle file

simConfig.analysis['plotRaster'] = {'orderInverse': True, 'saveFig': 'tut_import_raster.png'}			# Plot a raster
simConfig.analysis['plotTraces'] = {'include': [0]} 			# Plot recorded traces for this list of cells


#simConfig.recordLFP = [[netParams.sizeX/2,y,netParams.sizeZ/2] for y in range(netParams.sizeY/5, netParams.sizeY, netParams.sizeY/5)]

#simConfig.analysis['plotRaster'] = True 			# Plot a raster
#simConfig.analysis['plotLFP'] = True #{'plots': ['locations'], 'electrodes': ['avg', 'all'], 'NFFT': 512, 'noverlap': 16, 'nperseg': 32}#, 'plots': ['PSD', 'timeFreq'], 'smooth':4}#['True
#simConfig.analysis['plotRatePSD'] = {'NFFT': 64, 'noverlap': 32}
#simConfig.analysis['plotShape'] = {'iv':0}

# Create network and run simulation
sim.createSimulateAnalyze(netParams = netParams, simConfig = simConfig)    
   #
# import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty
