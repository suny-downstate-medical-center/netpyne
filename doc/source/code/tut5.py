from netpyne import init

# Network parameters
netParams = {}  # dictionary to store sets of network parameters

netParams['sizeX'] = 100 # x-dimension (horizontal length) size in um
netParams['sizeY'] = 1000 # y-dimension (vertical height or cortical depth) size in um
netParams['sizeZ'] = 100 # y-dimension (vertical height or cortical depth) size in um

## Population parameters
netParams['popParams'] = []  # list of populations - each item will contain dict with pop params
netParams['popParams'].append({'popLabel': 'E2', 'cellType': 'PYR', 'numCells': 20, 'ynormRange': [0,0.2], 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'I2', 'cellType': 'BAS', 'numCells': 20, 'ynormRange': [0,0.2], 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'E4', 'cellType': 'PYR', 'numCells': 20, 'ynormRange': [0.2,0.6], 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'I4', 'cellType': 'BAS', 'numCells': 20, 'ynormRange': [0.2,0.6], 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'E5', 'cellType': 'PYR', 'numCells': 20, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'I5', 'cellType': 'BAS', 'numCells': 20, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}) 
netParams['popParams'].append({'popLabel': 'background', 'rate': 15, 'noise': 0.3, 'cellModel': 'NetStim'})

## Cell property rules
netParams['cellParams'] = [] # list of cell property rules - each item will contain dict with cell properties
cellRule = {'label': 'PYRrule', 'conditions': {'cellType': 'PYR'},  'sections': {}}     # cell rule dict
soma = {'geom': {}, 'mechs': {}}                                            # soma params dict
soma['geom'] = {'diam': 15, 'L': 14, 'Ra': 120.0}                                   # soma geometry
soma['mechs']['hh'] = {'gnabar': 0.13, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}          # soma hh mechanism
cellRule['sections'] = {'soma': soma}                                                   # add soma section to dict
netParams['cellParams'].append(cellRule)                                                # add dict to list of cell par

cellRule = {'label': 'BASrule', 'conditions': {'cellType': 'BAS'},  'sections': {}}     # cell rule dict
soma = {'geom': {}, 'mechs': {}}                                            # soma params dict
soma['geom'] = {'diam': 10.0, 'L': 9.0, 'Ra': 110.0}                                    # soma geometry
soma['mechs']['hh'] = {'gnabar': 0.11, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}          # soma hh mechanism
cellRule['sections'] = {'soma': soma}                                                   # add soma section to dict
netParams['cellParams'].append(cellRule)                                                # add dict to list of cell par


## Synaptic mechanism parameters
netParams['synMechParams'] = []
netParams['synMechParams'].append({'label': 'exc', 'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 4.0, 'e': 0})  # NMDA synaptic mechanism
netParams['synMechParams'].append({'label': 'inh', 'mod': 'Exp2Syn', 'tau1': 0.6, 'tau2': 3.5, 'e': -75})  # GABA synaptic mechanism
 

## Cell connectivity rules
netParams['connParams'] = [] 

netParams['connParams'].append({
  'preTags': {'cellType': 'PYR'}, 
  'postTags': {'cellType': ['PYR','BAS']},  #  E -> all
  'probability': 0.1,                   # probability of connection
  'weight': 0.01,                       # synaptic weight 0.005
  'delay': 5,                           # transmission delay (ms) 
  'synMech': 'exc'})                    # synaptic mechanism 

netParams['connParams'].append({
  'preTags': {'popLabel': 'I3'}, 
  'postTags': {'popLabel': 'E3'},       #  I -> all
  'probability': 0.2,                   # probability of connection
  'weight': 0.01,                       # synaptic weight 
  'delay': 4,                           # transmission delay (ms) 
  'synMech': 'inh'})                    # synaptic mechanism 

netParams['connParams'].append({
  'preTags': {'popLabel': 'I4'}, 
  'postTags': {'popLabel': 'E4'},  #  I -> all
  'probability': 0.2,   # probability of connection
  'weight': 0.01,                                    # synaptic weight 
  'delay': 4,                    # transmission delay (ms) 
  'synMech': 'inh'})                                  # synaptic mechanism 

netParams['connParams'].append({
  'preTags': {'popLabel': 'I5'}, 
  'postTags': {'popLabel': 'E5'},  #  I -> all
  'probability': 0.2,   # probability of connection
  'weight': 0.01,                                    # synaptic weight 
  'delay': 4,                    # transmission delay (ms) 
  'synMech': 'inh'})

netParams['connParams'].append(
   {'preTags': {'popLabel': 'background'}, 
   'postTags': {'cellType': ['PYR', 'BAS']}, # background -> all
    'weight': 0.01,                     # synaptic weight 
    'delay': 10,    # transmission delay (ms) 
    'synMech': 'exc'})                  # synaptic mechanism 


# Simulation options
simConfig = {}
simConfig['duration'] = 1*1e3           # Duration of the simulation, in ms
simConfig['dt'] = 0.1                 # Internal integration timestep to use
simConfig['verbose'] = False            # Show detailed messages 
simConfig['recordTraces'] = {'V_soma':{'sec':'soma','pos':0.5,'var':'v'}}  # Dict with traces to record
simConfig['recordStep'] = 1             # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig['filename'] = 'model_output'  # Set file output name
simConfig['savePickle'] = False         # Save params, network and sim output to pickle file
simConfig['plotRaster'] = True          # Plot a raster
simConfig['orderRasterYnorm'] = 1       # Order cells in raster by yfrac (default is by pop and cell id)
simConfig['plotCells'] = ['E3','E4']    # Plot recorded traces for this list of cells
simConfig['plot2Dnet'] = True           # Plot recorded traces for this list of cells


# Create network and run simulation
init.createAndSimulate(netParams = netParams, simConfig = simConfig)    
   
# import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty
