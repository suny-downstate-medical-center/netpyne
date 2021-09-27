from netpyne import specs, sim

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

netParams.sizeX = 200 # x-dimension (horizontal length) size in um
netParams.sizeY = 1000 # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = 20 # z-dimension (horizontal length) size in um
netParams.propVelocity = 100.0 # propagation velocity (um/ms)
netParams.probLengthConst = 150.0 # length constant for conn probability (um)

## Population parameters
netParams.popParams['E2'] = {'cellType': 'E', 'numCells': 20, 'yRange': [100,300], 'cellModel': 'HH'}
netParams.popParams['I2'] = {'cellType': 'I', 'numCells': 20, 'yRange': [100,300], 'cellModel': 'HH'}
netParams.popParams['E4'] = {'cellType': 'E', 'numCells': 20, 'yRange': [300,600], 'cellModel': 'HH'}
netParams.popParams['I4'] = {'cellType': 'I', 'numCells': 20, 'yRange': [300,600], 'cellModel': 'HH'}
netParams.popParams['E5'] = {'cellType': 'E', 'numCells': 20, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}
netParams.popParams['I5'] = {'cellType': 'I', 'numCells': 20, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}

## Cell property rules
netParams.loadCellParamsRule(label='CellRule', fileName='IT2_reduced_cellParams.json')
netParams.cellParams['CellRule']['conds'] = {'cellType': ['E','I']}

## Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 5.3, 'e': 0}  # NMDA synaptic mechanism
netParams.synMechParams['inh'] = {'mod': 'Exp2Syn', 'tau1': 0.6, 'tau2': 8.5, 'e': -75}  # GABA synaptic mechanism

# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 40, 'noise': 0.3}
netParams.stimTargetParams['bkg->all'] = {'source': 'bkg', 'conds': {'cellType': ['E','I']}, 'weight': 10.0, 'sec': 'soma', 'delay': 'max(1, normal(5,2))', 'synMech': 'exc'}

## Cell connectivity rules
netParams.connParams['E->all'] = {
  'preConds': {'cellType': 'E'}, 'postConds': {'y': [100,1000]},  #  E -> all (100-1000 um)
  'probability': 0.1 ,                  # probability of connection
  'weight': '5.0*post_ynorm',         # synaptic weight
  'delay': 'dist_3D/propVelocity',      # transmission delay (ms)
  'synMech': 'exc'}                     # synaptic mechanism

netParams.connParams['I->E'] = {
  'preConds': {'cellType': 'I'}, 'postConds': {'pop': ['E2','E4','E5']},       #  I -> E
  'probability': '0.4*exp(-dist_3D/probLengthConst)',   # probability of connection
  'weight': 1.0,                                      # synaptic weight
  'delay': 'dist_3D/propVelocity',                      # transmission delay (ms)
  'synMech': 'inh'}                                     # synaptic mechanism


# Simulation configuration
simConfig = specs.SimConfig()        # object of class SimConfig to store simulation configuration
simConfig.duration = 3.0*1e3           # Duration of the simulation, in ms
simConfig.dt = 0.1                # Internal integration timestep to use
simConfig.verbose = False            # Show detailed messages
simConfig.recordStep = 1             # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'net_lfp'   # Set file output name

simConfig.recordLFP = [[-15, y, 1.0*netParams.sizeZ] for y in range(int(netParams.sizeY/5.0), int(netParams.sizeY), int(netParams.sizeY/5.0))]

#simConfig.analysis['plotRaster'] = {'orderBy': 'y', 'orderInverse': True, 'saveFig':True, 'figSize': (9,3)}      # Plot a raster
simConfig.analysis['plotLFP'] = {'includeAxon': False, 'figSize': (6,10), 'timeRange': [100,3000], 'saveFig': True} 
#simConfig.analysis['getCSD'] = {'spacing_um': 200, 'timeRange': [100,3000], 'vaknin': True}
#simConfig.analysis['plotLFP'] = {'includeAxon': False, 'figSize': (6,10), 'timeRange':[100,900], 'minFreq': 10, 'maxFreq':60, 'norm':1, 'plots': ['spectrogram'], 'showFig': True} 
simConfig.analysis['plotCSD'] = True #{'timeRange':[100,200]}

# Create network and run simulation
sim.createSimulateAnalyze(netParams = netParams, simConfig = simConfig)    
#sim.analysis.plotCSD(timeRange=[100,3000])