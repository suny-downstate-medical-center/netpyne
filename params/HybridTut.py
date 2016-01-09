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

# Cell properties list
netParams['cellParams'] = []

## PYR cell properties (HH)
cellRule = {'label': 'PYR_HH', 'conditions': {'cellType': 'PYR', 'cellModel': 'HH'},  'sections': {}}

soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'syns': {}}  # soma properties
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0, 'pt3d': []}
soma['geom']['pt3d'].append((0, 0, 0, 20))
soma['geom']['pt3d'].append((0, 0, 20, 20))
soma['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} 
soma['syns']['NMDA'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau': 0.1, 'e': 0}

dend = {'geom': {}, 'topol': {}, 'mechs': {}, 'syns': {}}  # dend properties
dend['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1, 'pt3d': []}
dend['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}
dend['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 
dend['syns']['NMDA'] = {'type': 'Exp2Syn', 'loc': 1.0, 'tau1': 0.1, 'tau2': 1, 'e': 0}

cellRule['sections'] = {'soma': soma, 'dend': dend}  # add sections to dict
netParams['cellParams'].append(cellRule)  # add dict to list of cell properties


## PYR cell properties (Izhi)
cellRule = {'label': 'PYR_Izhi', 'conditions': {'cellType': 'PYR', 'cellModel': 'Izhi2007b'},  'sections': {}}

soma = {'geom': {}, 'pointps':{}, 'syns': {}}  # soma properties
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0, 'pt3d': []}
soma['pointps']['Izhi2007b'] = {'C':100, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}

soma['syns']['NMDA'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau': 0.1, 'e': 0}

cellRule['sections'] = {'soma': soma}  # add sections to dict
netParams['cellParams'].append(cellRule)  # add dict to list of cell properties


# Population parameters
netParams['popParams'] = []  # create list of populations - each item will contain dict with pop params
netParams['popParams'].append({'popLabel': 'PYR', 'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 50}) # add dict with params for this pop 
netParams['popParams'].append({'popLabel': 'PYR', 'cellModel': 'Izhi2007b', 'cellType': 'PYR', 'numCells': 50}) # add dict with params for this pop 
netParams['popParams'].append({'popLabel': 'background', 'cellModel': 'NetStim', 'rate': 100, 'noise': 0.5, 'source': 'random'})  # background inputs

netParams['popTagsCopiedToCells'] = ['popLabel', 'cellModel', 'cellType']


# Connectivity parameters
netParams['connParams'] = []  

netParams['connParams'].append(
    {'preTags': {'popLabel': 'PYR'}, 'postTags': {'popLabel': 'PYR'},
    'connFunc': 'randConn', # connection function
    'weight': 0.004,        # weight of each connection
    'delayMean': 13.0,      # mean of delays
    'delayVar': 1.4,        # variance of delays 
    'delayMin': 0.2,        # minimum delays
    'threshold': 10,
    'maxConns': 20})       # threshold

netParams['connParams'].append(
    {'preTags': {'popLabel': 'background'}, 'postTags': {'cellType': 'PYR','cellModel': 'Izhi2007b'}, # background -> PYR (Izhi2007b)
    'connFunc': 'fullConn',
    'weight': 10, 
    'synReceptor': 'NMDA',
    'delay': 5})  

netParams['connParams'].append(
    {'preTags': {'popLabel': 'background'}, 'postTags': {'cellType': 'PYR', 'cellModel': 'HH'}, # background -> PYR (HH)
    'connFunc': 'fullConn',
    'weight': 20, 
    'synReceptor': 'NMDA',
    'sec': 'dend',
    'loc': 1.0,
    'delay': 5})  


###############################################################################
# SIMULATION PARAMETERS
###############################################################################

simConfig = {}  # dictionary to store simConfig

# Simulation parameters
simConfig['duration'] = simConfig['tstop'] = 1*1e3 # Duration of the simulation, in ms
simConfig['dt'] = 0.025 # Internal integration timestep to use
simConfig['randseed'] = 1 # Random seed to use
simConfig['createNEURONObj'] = 1  # create HOC objects when instantiating network
simConfig['createPyStruct'] = 1  # create Python structure (simulator-independent) when instantiating network
simConfig['verbose'] = 1  # show detailed messages 


# Recording 
simConfig['recordTraces'] = True  # whether to record cell traces or not
simConfig['recdict'] = {'Vsoma':{'sec':'soma','pos':0.5,'var':'v'}}
simConfig['recordStim'] = True  # record spikes of cell stims
simConfig['recordStep'] = 10 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
simConfig['filename'] = 'mpiHybridTut'  # Set file output name
simConfig['saveFileStep'] = 1000 # step size in ms to save data to disk
simConfig['savePickle'] = True # Whether or not to write spikes etc. to a .mat file
simConfig['saveJson'] = True # Whether or not to write spikes etc. to a .mat file
simConfig['saveMat'] = True # Whether or not to write spikes etc. to a .mat file
simConfig['saveTxt'] = False # save spikes and conn to txt file
simConfig['saveDpk'] = False # save to a .dpk pickled file


# Analysis and plotting 
simConfig['plotRaster'] = True # Whether or not to plot a raster
simConfig['plotTracesGids'] = [] # plot recorded traces for this list of cells
simConfig['plotPsd'] = False # plot power spectral density
simConfig['maxspikestoplot'] = 3e8 # Maximum number of spikes to plot
simConfig['plotConn'] = False # whether to plot conn matrix
simConfig['plotWeightChanges'] = False # whether to plot weight changes (shown in conn matrix)
simConfig['plot3dArch'] = False # plot 3d architecture

