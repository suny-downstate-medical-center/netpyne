"""
params.py 

netParams is a dict containing a set of network parameters using a standardized structure

simConfig is a dict containing a set of simulation configurations using a standardized structure

Contributors: salvadordura@gmail.com
"""

netParams = {}  # dictionary to store sets of network parameters
simConfig = {}  # dictionary to store sets of simulation configurations


###############################################################################
#
# MPI HH TUTORIAL PARAMS
#
###############################################################################

###############################################################################
# NETWORK PARAMETERS
###############################################################################

# Population parameters
netParams['popParams'] = []  # create list of populations - each item will contain dict with pop params
netParams['popParams'].append({'popLabel': 'PYR', 'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 200}) # add dict with params for this pop 
netParams['popParams'].append({'popLabel': 'background', 'cellModel': 'NetStim', 'rate': 10, 'noise': 0.5, 'start': 1})  # background inputs

# Cell parameters
netParams['cellParams'] = []

## PYR cell properties
cellRule = {'label': 'PYR', 'conditions': {'cellType': 'PYR'},  'sections': {}}
soma = {'geom': {}, 'topol': {}, 'mechs': {}}  # soma properties
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
soma['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} 

cellRule['sections'] = {'soma': soma}  # add sections to dict
netParams['cellParams'].append(cellRule)  # add dict to list of cell properties

# Synaptic mechanism parameters
netParams['synMechParams'] = []
netParams['synMechParams'].append({'label': 'AMPA', 'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': 0})
 
# Connectivity parameters
netParams['connParams'] = []  

netParams['connParams'].append(
    {'preTags': {'popLabel': 'PYR'}, 'postTags': {'popLabel': 'PYR'},
    'weight': 0.005,                    # weight of each connection
    'delay': '0.2+gauss(13.0,1.4)',     # delay min=0.2, mean=13.0, var = 1.4
    'threshold': 10,                    # threshold
    'convergence': 'uniform(1,15)'})    # convergence (num presyn targeting postsyn) is uniformly distributed between 1 and 15


netParams['connParams'].append(
    {'preTags': {'popLabel': 'background'}, 'postTags': {'cellType': 'PYR'}, # background -> PYR
    'weight': 0.1,                    # fixed weight of 0.08
    'synMech': 'AMPA',                     # target NMDA synapse
    'delay': 'uniform(1,5)'})           # uniformly distributed delays between 1-5ms


###############################################################################
# SIMULATION PARAMETERS
###############################################################################

simConfig = {}  # dictionary to store simConfig

# Simulation parameters
simConfig['duration'] = 1*1e3 # Duration of the simulation, in ms
simConfig['dt'] = 0.025 # Internal integration timestep to use
simConfig['seeds'] = {'conn': 1, 'stim': 1, 'loc': 1} # Seeds for randomizers (connectivity, input stimulation and cell locations)
simConfig['createNEURONObj'] = 1  # create HOC objects when instantiating network
simConfig['createPyStruct'] = 1  # create Python structure (simulator-independent) when instantiating network
simConfig['verbose'] = False  # show detailed messages 

# Recording 
simConfig['recordCells'] = []  # which cells to record from
simConfig['recordTraces'] = {'Vsoma':{'sec':'soma','loc':0.5,'var':'v'}}
simConfig['recordStim'] = True  # record spikes of cell stims
simConfig['recordStep'] = 0.1 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
simConfig['filename'] = 'HHTut'  # Set file output name
simConfig['saveFileStep'] = 1000 # step size in ms to save data to disk
simConfig['savePickle'] = False # Whether or not to write spikes etc. to a .mat file


# Analysis and plotting 
simConfig['analysis'] = {}
simConfig['analysis']['plotRaster'] = True # Plot raster
simConfig['analysis']['plotTraces'] = {'include': [2]} # Plot raster
simConfig['analysis']['plot2Dnet'] = True # Plot 2D net cells and connections



