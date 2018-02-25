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
# netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 1, 'noise': 0.0}
# #netParams.stimSourceParams['bkg'] = {'type': 'IClamp', 'amp': 1.0, 'del': 50, 'dur': 100.0}

# netParams.stimTargetParams['bkg->all'] = {'source': 'bkg', 'conds': {'cellType': ['E','I']}, 'weight': 0.1, 'delay': 50, 'synMech': 'exc'}
# #netParams.stimTargetParams['bkg->all'] = {'source': 'bkg', 'conds': {'cellType': ['E','I']}, 'sec': 'soma', 'loc': 0.5}

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
  'weight': 0.01,                                      # synaptic weight 
  'delay': 'dist_3D/propVelocity',                      # transmission delay (ms) 
  'synMech': 'inh'}                                     # synaptic mechanism 


# Simulation options
simConfig = specs.SimConfig()        # object of class SimConfig to store simulation configuration
simConfig.duration = 1.0*1e3           # Duration of the simulation, in ms
simConfig.dt = 0.1                # Internal integration timestep to use
simConfig.verbose = False            # Show detailed messages 
simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'},
                        'Imemb':{'sec':'soma','loc':0.5,'var':'i_membrane'},
                        'Imemb_':{'sec':'soma','loc':0.5,'var':'i_membrane_'},
                        'ina':{'sec':'soma','loc':0.5,'var':'ina'},
                        'ik':{'sec':'soma','loc':0.5,'var':'ik'},
                        'ileak':{'sec':'soma','loc':0.5,'mech':'hh', 'var':'il'},
                        'isyn':{'sec':'soma','loc':0.5,'synMech': 'exc', 'var':'i'}}  # Dict with traces to record
simConfig.recordStep = 1             # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'model_output'  # Set file output name
simConfig.savePickle = False         # Save params, network and sim output to pickle file
simConfig.saveMat = False         # Save params, network and sim output to pickle file


simConfig.analysis['plotRaster'] = {'orderBy': 'y', 'orderInverse': True}      # Plot a raster
simConfig.analysis['plotTraces'] = {'include': [('E2',0)]}      # Plot recorded traces for this list of cells

simConfig.recordLFP = [[-10, y, 1.0*netParams.sizeZ] for y in range(netParams.sizeY/5, netParams.sizeY, netParams.sizeY/5)]
simConfig.analysis['plotLFP'] = {'includeAxon': False} # {'plots': ['timeSeries', 'PSD', 'locations']} #, 'electrodes': ['avg', 'all'], 'NFFT': 512, 'noverlap': 16, 'nperseg': 32}#, 'plots': ['PSD', 'timeFreq'], 'smooth':4}#['True

# Create network and run simulation
sim.createSimulateAnalyze(netParams = netParams, simConfig = simConfig)    

# import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty
