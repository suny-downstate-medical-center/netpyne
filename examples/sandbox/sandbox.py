from netpyne import specs, sim

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

netParams.sizeX = 200 # x-dimension (horizontal length) size in um
netParams.sizeY = 1000 # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = 20 # z-dimension (horizontal length) size in um
netParams.propVelocity = 100.0 # propagation velocity (um/ms)
netParams.probLengthConst = 150.0 # length constant for conn probability (um)

## Population parameters
netParams.popParams['I2'] = {'cellType': 'SOM', 'numCells': 10, 'cellModel': 'HH_simple'}
netParams.popParams['I3'] = {'cellType': 'PV', 'numCells': 10, 'cellModel': 'HH_simple'}

netParams.popParams['input'] = {'numCells': 100, 'cellModel': 'NetStim', 'rate': 20, 'noise': 0.75}
netParams.popParams['input2'] = {'numCells': 50, 'cellModel': 'NetStim', 'rate': 20, 'noise': 0.75}


## Cell property rules
netParams.loadCellParamsRule(label='CellRule', fileName='IT2_reduced_cellParams.json')
netParams.cellParams['CellRule']['conds'] = {'cellType': ['E','I']}

#------------------------------------------------------------------------------
# PV + SOMcell params (3-comp)

ruleLabels = ['PV_simple', 'SOM_simple']
for ruleLabel in ruleLabels:
  netParams.loadCellParamsRule(label=ruleLabel, fileName=ruleLabel+'_cellParams.pkl')


# ## Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 5.3, 'e': 0}  # NMDA synaptic mechanism
netParams.synMechParams['inh'] = {'mod': 'Exp2Syn', 'tau1': 0.6, 'tau2': 8.5, 'e': -75}  # GABA synaptic mechanism


netParams.connParams['input->I'] = {
  'preConds': {'pop': ['input','input2', 'I2', 'I3']}, 'postConds': {'cellType': ['PV','SOM']},  #  E -> all (100-1000 um)
  'probability': 0.5 ,                  # probability of connection
  'weight': 0.5,         # synaptic wight 
  'delay': 2,      # transmission delay (ms) 
  'synMech': 'exc',
  'sec': 'soma'}                     # synaptic mechanism 


# # All->I; apical dendrites (no sCRACM)
# netParams.subConnParams['All->I'] = {
#   'preConds': {'pop': ['input','input2', 'I2', 'I3']}, 
#   'postConds': {'cellType': ['SOM', 'PV']},  
#   'sec': ['soma','dend'],
#   'density': 'uniform'} 


# Simulation configuration
simConfig = specs.SimConfig()        # object of class SimConfig to store simulation configuration
simConfig.duration = 1.0*1e3           # Duration of the simulation, in ms
simConfig.dt = 0.1                # Internal integration timestep to use
simConfig.verbose = False            # Show detailed messages 
simConfig.recordStep = 0.1             # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'net_lfp'   # Set file output name
simConfig.printSynsAfterRule = True
simConfig.recordTraces ={'V': {'sec': 'soma', 'loc': 0.5, 'var':'v'}}


lfp=0
if lfp:
  #simConfig.analysis['plotLFP'] = {'includeAxon': False, 'figSize': (6,10), 'plots': ['timeSeries'], 'NFFT': 256*2, 'noverlap': 128*2, 'nperseg': 132*2, 'saveFig': True} 
  simConfig.recordLFP = [[10,10,10]]

simConfig.analysis['plotRaster'] = {'popRates':1, 'orderBy': ['pop','y'], 'labels':'overlay', 'orderInverse': 0, 'saveFig':True, 'figSize': (9,3)}      # Plot a raster
#simConfig.analysis['plotTraces'] ={'include':[0]}
#simConfig.analysis['plotLFP'] = {'includeAxon': False, 'figSize': (6,10), 'NFFT': 256*20, 'noverlap': 128*20, 'nperseg': 132*20, 'saveFig': True} 
#simConfig.analysis['plotSpikeStats'] = {'include': ['E2', 'E4', ['E2', 'E4']] , 'stats': ['rate'], 'graphType': 'histogram', 'figSize': (10,6)}

# Create network and run simulation
#sim.createSimulateAnalyze(netParams = netParams, simConfig = simConfig)    

sim.initialize(
    simConfig = simConfig,  
    netParams = netParams)          # create network object and set cfg and net params
sim.net.createPops()                    # instantiate network populations
sim.net.createCells()                   # instantiate network cells based on defined populations
sim.net.addStims()              # add network stimulation
sim.net.connectCells()                  # create connections between cells based on params
sim.setupRecording()                    # setup variables to record for each cell (spikes, V traces, etc)
sim.runSim()                            # run parallel Neuron simulation  
#sim.distributedSaveHDF5()
sim.gatherData()                        # gather spiking data and cell info from each node
sim.saveData()                          # save params, cell info and sim output to file (pickle,mat,txt,etc)#
sim.analysis.plotData()               # plot spike raster etc

#conns, connFormat = sim.loadHDF5(sim.cfg.filename+'.h5')
#print len(conns)
#print sim.timingData
