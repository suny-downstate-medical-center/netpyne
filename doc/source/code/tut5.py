from netpyne import sim

# Network parameters
netParams = {}  # dictionary to store sets of network parameters

netParams['sizeX'] = 100 # x-dimension (horizontal length) size in um
netParams['sizeY'] = 1000 # y-dimension (vertical height or cortical depth) size in um
netParams['sizeZ'] = 100 # z-dimension (horizontal length) size in um
netParams['propVelocity'] = 100.0 # propagation velocity (um/ms)
netParams['probLengthConst'] = 150.0 # length constant for conn probability (um)


## Population parameters
netParams['popParams'] = []  # list of populations - each item will contain dict with pop params
netParams['popParams'].append({'popLabel': 'E2', 'cellType': 'E', 'numCells': 50, 'yRange': [100,300], 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'I2', 'cellType': 'I', 'numCells': 50, 'yRange': [100,300], 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'E4', 'cellType': 'E', 'numCells': 50, 'yRange': [300,600], 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'I4', 'cellType': 'I', 'numCells': 50, 'yRange': [300,600], 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'E5', 'cellType': 'E', 'numCells': 50, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'I5', 'cellType': 'I', 'numCells': 50, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'background', 'rate': 20, 'noise': 0.3, 'cellModel': 'NetStim'})

## Cell property rules
netParams['cellParams'] = [] # list of cell property rules - each item will contain dict with cell properties
cellRule = {'label': 'PYRrule', 'conditions': {'cellType': 'E'},  'sections': {}}     # cell rule dict
soma = {'geom': {}, 'mechs': {}}                                            # soma params dict
soma['geom'] = {'diam': 15, 'L': 14, 'Ra': 120.0}                                   # soma geometry
soma['mechs']['hh'] = {'gnabar': 0.13, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}          # soma hh mechanism
cellRule['sections'] = {'soma': soma}                                                   # add soma section to dict
netParams['cellParams'].append(cellRule)                                                # add dict to list of cell par

cellRule = {'label': 'BASrule', 'conditions': {'cellType': 'I'},  'sections': {}}     # cell rule dict
soma = {'geom': {}, 'mechs': {}}                                            # soma params dict
soma['geom'] = {'diam': 10.0, 'L': 9.0, 'Ra': 110.0}                                    # soma geometry
soma['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}          # soma hh mechanism
cellRule['sections'] = {'soma': soma}                                                   # add soma section to dict
netParams['cellParams'].append(cellRule)                                                # add dict to list of cell par


## Synaptic mechanism parameters
netParams['synMechParams'] = []
netParams['synMechParams'].append({'label': 'exc', 'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 5.3, 'e': 0})  # NMDA synaptic mechanism
netParams['synMechParams'].append({'label': 'inh', 'mod': 'Exp2Syn', 'tau1': 0.6, 'tau2': 8.5, 'e': -75})  # GABA synaptic mechanism
 

## Cell connectivity rules
netParams['connParams'] = [] 

netParams['connParams'].append({'preTags': {'popLabel': 'background'}, 'postTags': {'cellType': ['E', 'I']}, # background -> all
  'weight': 0.01,                     # synaptic weight 
  'delay': 'max(1, gauss(5,2))',      # transmission delay (ms) 
  'synMech': 'exc'})                  # synaptic mechanism 

netParams['connParams'].append({'preTags': {'cellType': 'E'}, 'postTags': {'y': [100,1000]},  #  E -> all (100-1000 um)
  'probability': 0.1,#'uniform(0.05,0.2)',    # probability of connection
  'weight': '0.005*post_ynorm',         # synaptic weight 
  'delay': 'dist_3D/propVelocity',      # transmission delay (ms) 
  'synMech': 'exc'})                    # synaptic mechanism 

netParams['connParams'].append({'preTags': {'cellType': 'I'}, 'postTags': {'popLabel': ['E2','E4','E5']},       #  I -> E
  'probability': '0.4*exp(-dist_3D/probLengthConst)',   # probability of connection
  'weight': 0.001,                                     # synaptic weight 
  'delay': 'dist_3D/propVelocity',                    # transmission delay (ms) 
  'synMech': 'inh'})                                  # synaptic mechanism 


# Simulation options
simConfig = {}
simConfig['duration'] = 1*1e3           # Duration of the simulation, in ms
simConfig['dt'] = 0.1                 # Internal integration timestep to use
simConfig['verbose'] = False            # Show detailed messages 
simConfig['recordTraces'] = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
simConfig['recordStep'] = 1             # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig['filename'] = 'model_output'  # Set file output name
simConfig['savePickle'] = False         # Save params, network and sim output to pickle file

simConfig['analysis'] = {}
simConfig['analysis']['plotRaster'] = {'orderBy': 'y', 'orderInverse': True}      # Plot a raster
simConfig['analysis']['plotTraces'] = {'include': [('E2',0), ('E4', 0), ('E5', 5)]}      # Plot recorded traces for this list of cells
simConfig['analysis']['plot2Dnet'] = True           # plot 2D visualization of cell positions and connections
simConfig['analysis']['plotConn'] = True           # plot connectivity matrix

# Create network and run simulation
sim.createAndSimulate(netParams = netParams, simConfig = simConfig)    
   
# import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty
