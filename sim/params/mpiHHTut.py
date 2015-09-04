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

netParams['mpiHHTut'] = {}  # dictionary to store netParams
p = netParams['mpiHHTut']  # pointer to dict

## Position parameters
netParams['scale'] = 1 # Size of simulation in thousands of cells
netParams['corticalthick'] = 1000 # cortical thickness/depth
    
# Cell properties list
netParams['cellProps'] = []

# PYR cell properties
cellProp = {'label': 'PYR', 'conditions': {'cellType': 'PYR'}, 'Izhi2007Type': 'RS', 'sections': {}}

soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'syns': {}}  # soma properties
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0, 'pt3d': []}
soma['geom']['pt3d'].append({'x': 0, 'y': 0, 'z': 0, 'd': 20})
soma['geom']['pt3d'].append({'x': 0, 'y': 0, 'z': 20, 'd': 20})
soma['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} 
soma['syns']['AMPA'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 0.05, 'tau2': 5.3, 'e': 0}

dend = {'geom': {}, 'topol': {}, 'mechs': {}, 'syns': {}}  # dend properties
dend['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 150.0, 'cm': 1, 'pt3d': []}
dend['geom']['pt3d'].append({'x': 0, 'y': 0, 'z': 0, 'd': 20})
dend['geom']['pt3d'].append({'x': 0, 'y': 0, 'z': 20, 'd': 20})
dend['topol'] = {'parentSec': 'soma', 'parentX': 0, 'childX': 0}
dend['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 
dend['syns']['NMDA'] = {'type': 'Exp2Syn', 'loc': 1.0, 'tau1': 15, 'tau2': 150, 'e': 0}

cellProp['sections'] = {'soma': soma, 'dend': dend}  # add sections to dict
netParams['cellProps'].append(cellProp)  # add dict to list of cell properties

# Population parameters
netParams['popParams'] = []  # create list of populations - each item will contain dict with pop params
netParams['popParams'].append({'popLabel': 'PYR', 'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 10}) # add dict with params for this pop 
netParams['popParams'].append({'popLabel': 'background', 'cellModel': 'NetStim', 'rate': 100, 'noise': 0.5, 'source': 'random'})  # background inputs

netParams['popTagsCopiedToCells'] = ['popLabel', 'cellModel', 'cellType']

# Connectivity parameters

netParams['connParams'] = []  

netParams['connParams'].append(
    {'preTags': {'popLabel': 'PYR'}, 'postTags': {'popLabel': 'PYR'},
    'connType': 'random',   # pre and post cells selected randomly 
    'weight': 0.004,        # weight of each connection
    'delayMean': 13.0,      # mean of delays
    'delayVar': 1.4,        # variance of delays 
    'delayMin': 0.2,        # minimum delays
    'threshold': 10})       # threshold

netParams['connParams'].append(
    {'preTags': {'popLabel': 'background'}, 'postTags': {'cellType': 'PYR' }, # background -> PYR
    'connFunc': 'fullConn',
    'probability': 0.5, 
    'weight': 0.1, 
    'syn': 'NMDA',
    'delay': 5})  


###############################################################################
# SIMULATION PARAMETERS
###############################################################################

simConfig = {}  # dictionary to store simConfig


# Simulation parameters
simConfig['duration'] = simConfig['tstop'] = 1*1e3 # Duration of the simulation, in ms
simConfig['dt'] = 0.5 # Internal integration timestep to use
simConfig['recordStep'] = 10 # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig['saveFileStep'] = 1000 # step size in ms to save data to disk
simConfig['randseed'] = 1 # Random seed to use
simConfig['createNEURONObj'] = 1  # create HOC objects when instantiating network
simConfig['createPyStruct'] = 1  # create Python structure (simulator-independent) when instantiating network
# alternative: simConfig['createFuncs'] = ['createNEURONObj', 'createPyStruct']


## Recording 
simConfig['recdict'] = {'Vsoma':'soma(0.5)._ref_v'}
simConfig['simdataVecs'] = ['spkt', 'spkid']


## Saving and plotting parameters
simConfig['filename'] = '../data/m1ms'  # Set file output name
simConfig['savemat'] = True # Whether or not to write spikes etc. to a .mat file
simConfig['savetxt'] = False # save spikes and conn to txt file
simConfig['savedpk'] = True # save to a .dpk pickled file
simConfig['recordTraces'] = True  # whether to record cell traces or not
simConfig['saveBackground'] = False # save background (NetStims) inputs
simConfig['verbose'] = 0 # Whether to write nothing (0), diagnostic information on events (1), or everything (2) a file directly from izhi.mod
simConfig['plotraster'] = True # Whether or not to plot a raster
simConfig['plotpsd'] = False # plot power spectral density
simConfig['maxspikestoplot'] = 3e8 # Maximum number of spikes to plot
simConfig['plotconn'] = False # whether to plot conn matrix
simConfig['plotweightchanges'] = False # whether to plot weight changes (shown in conn matrix)
simConfig['plot3darch'] = False # plot 3d architecture


