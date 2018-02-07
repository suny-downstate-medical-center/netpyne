from netpyne import specs, sim

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

netParams.sizeX = 100 # x-dimension (horizontal length) size in um
netParams.sizeY = 1000 # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = 100 # z-dimension (horizontal length) size in um
netParams.propVelocity = 100.0 # propagation velocity (um/ms)
netParams.probLengthConst = 150.0 # length constant for conn probability (um)

# import json
# file = 'ssc-3_spikes.json'
# with open(file, 'r') as f: spks = json.load(f)
# print spks
## Population parameters
netParams.popParams['E2'] = {'cellType': 'E', 'numCells': 3, 'yRange': [100,300], 'cellModel': 'HH'}
netParams.popParams['S2'] = {'cellModel': 'NetStim', 'numCells': 10, 'rate': 10} #[[50, 100, 200, 300], [150, 240, 412, 320],[55, 105, 210, 330]] }
#netParams.popParams['S3'] = {'cellModel': 'VecStim', 'numCells': 3, 'cellsList': [{'spkTimes': [50, 100, 200, 300]},
																				# {'spkTimes': [150, 240, 412, 320]},
																				# {'spkTimes': [55, 105, 210, 330]}]}


## Cell property rules
cellRule = {'conds': {'cellType': 'E'},  'secs': {}}  # cell rule dict
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                              # soma params dict
cellRule['secs']['soma']['geom'] = {'diam': 15, 'L': 14, 'Ra': 120.0}                   # soma geometry
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.13, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}      # soma hh mechanism
cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}  								# dend params dict
cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}							# dend geometry
cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}						# dend topology 
cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 	
netParams.cellParams['Erule'] = cellRule                          # add dict to list of cell params


## Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 5.3, 'e': 0}  # NMDA synaptic mechanism


## Cell connectivity rules
netParams.connParams['E->all'] = {
  'preConds': {'pop': 'S2'}, 'postConds': {'pop': 'E2'},  # S2->E2
  'weight': 0.01,         # synaptic weight 
  'delay': 1,      # transmission delay (ms) 
  'sec': ['soma','dend'],
  'loc': [0.1, 0.3],
  'synMech': 'exc'}                     # synaptic mechanism 

                            # synaptic mechanism 


# Simulation options
cfg = specs.SimConfig()        # object of class cfg to store simulation configuration
cfg.duration = 1*1e3           # Duration of the simulation, in ms
cfg.dt = 0.025                # Internal integration timestep to use
cfg.verbose = False            # Show detailed messages 
cfg.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
cfg.recordStep = 1             # Step size in ms to save data (eg. V traces, LFP, etc)
cfg.filename = 'sim'  # Set file output name
cfg.savePickle = False         # Save params, network and sim output to pickle file
cfg.saveMat = False         # Save params, network and sim output to pickle file
cfg.saveJson = 1
cfg.checkErrors = 0

cfg.analysis['plotRaster'] = {'saveFig': True, 'showFig': True, 'labels': 'overlay', 'popRates': True, 'orderInverse': True, 
							 'figSize': (4,4), 'lw': 0.3, 'markerSize':3, 'marker': '.', 'dpi': 300} 
cfg.analysis['plotTraces'] = {'include': [0]}

# cfg.analysis['plotSpikeHist'] = {'yaxis':'rate', 'binSize':5, 'graphType':'bar',
# 								'saveFig': True, 'showFig': False, 'popColors': popColors, 'figSize': (10,4), 'dpi': 300} 
#cfg.analysis['plotSpikeStats'] = {'saveFig': True}
#cfg.analysis['plotRatePSD'] = {'saveFig': True}


# Create network and run simulation
# sim.saveDataInclude = ['netParams', 'simConfig']
# sim.initialize(netParams = netParams, simConfig = cfg)
# sim.saveData()

#netParams.save()
#simConfig.save()

sim.createSimulateAnalyze(netParams = netParams, simConfig = cfg)    

# import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty
