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
netParams['popParams'].append({'popLabel': 'PYR_HH', 'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 50}) # add dict with params for this pop 
netParams['popParams'].append({'popLabel': 'PYR_Izhi', 'cellModel': 'Izhi2007b', 'cellType': 'PYR', 'numCells': 50}) # add dict with params for this pop 
netParams['popParams'].append({'popLabel': 'background', 'cellModel': 'NetStim', 'rate': 10, 'noise': 0.5})  # background inputs


# Cell parameters list
netParams['cellParams'] = []

## PYR cell properties (HH)
cellRule = {'label': 'PYR_HH', 'conds': {'cellType': 'PYR', 'cellModel': 'HH'},  'secs': {}}

soma = {'geom': {}, 'topol': {}, 'mechs': {}}  # soma properties
soma['geom'] = {'diam': 6.3, 'L': 5, 'Ra': 123.0, 'pt3d':[]}
soma['geom']['pt3d'].append((0, 0, 0, 20))
soma['geom']['pt3d'].append((0, 0, 20, 20))
soma['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} 

dend = {'geom': {}, 'topol': {}, 'mechs': {}}  # dend properties
dend['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1, 'pt3d': []}
dend['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}
dend['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 

cellRule['secs'] = {'soma': soma, 'dend': dend}  # add sections to dict
netParams['cellParams'].append(cellRule)  # add dict to list of cell properties

## PYR cell properties (Izhi)
cellRule = {'label': 'PYR_Izhi', 'conds': {'cellType': 'PYR', 'cellModel': 'Izhi2007b'},  'secs': {}}

soma = {'geom': {}, 'pointps':{}}  # soma properties
soma['geom'] = {'diam': 10, 'L': 10, 'cm': 31.831}
soma['pointps']['Izhi'] = {'mod':'Izhi2007b', 'C':1, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}
cellRule['secs'] = {'soma': soma}  # add sections to dict
netParams['cellParams'].append(cellRule)  # add dict to list of cell properties


# Synaptic mechanism parameters
netParams['synMechParams'] = []
netParams['synMechParams'].append({'label': 'AMPA', 'mod': 'ExpSyn', 'tau': 0.1, 'e': 0})
 

# Connectivity parameters
netParams['connParams'] = []  

netParams['connParams'].append(
    {'preConds': {'cellType': 'PYR'}, 'postConds': {'cellType': 'PYR'},
    'weight': 0.2,                    # weight of each connection
    'delay': '0.2+gauss(13.0,1.4)',     # delay min=0.2, mean=13.0, var = 1.4
    'threshold': 10,                    # threshold
    'convergence': 'uniform(0,5)',       # convergence (num presyn targeting postsyn) is uniformly distributed between 1 and 10
    'synMech': 'AMPA'})    


netParams['connParams'].append(
    {'preConds': {'popLabel': 'background'}, 'postConds': {'cellType': 'PYR','cellModel': 'Izhi2007b'}, # background -> PYR (Izhi2007b)
    'connFunc': 'fullConn',
    'weight': 1, 
    'delay': 'uniform(1,5)',
    'synMech': 'AMPA'})  


netParams['connParams'].append(
    {'preConds': {'popLabel': 'background'}, 'postConds': {'cellType': 'PYR', 'cellModel': 'HH'}, # background -> PYR (HH)
    'connFunc': 'fullConn',
    'weight': 1, 
    'synMech': 'AMPA',
    'sec': 'dend',
    'loc': 1.0,
    'delay': 'uniform(1,5)'})  



###############################################################################
# SIMULATION PARAMETERS
###############################################################################

simConfig = {}  # dictionary to store simConfig

# Simulation parameters
simConfig.duration = 1*1e3 # Duration of the simulation, in ms
simConfig.dt = 0.025 # Internal integration timestep to use
simConfig.seeds = {'conn': 1, 'stim': 1, 'loc': 1} # Seeds for randomizers (connectivity, input stimulation and cell locations)
simConfig.createNEURONObj = True  # create HOC objects when instantiating network
simConfig.createPyStruct = True  # create Python structure (simulator-independent) when instantiating network
simConfig.timing = True  # show timing  and save to file
simConfig.verbose = 1# False # show detailed messages 


# Recording 
simConfig.recordCells = []  # list of cells to record from 
simConfig.recordTraces = {'V':{'sec':'soma','loc':0.5,'var':'v'}, 
    'u':{'sec':'soma', 'pointp':'Izhi', 'var':'u'}, 
    'I':{'sec':'soma', 'pointp':'Izhi', 'var':'i'}, 
    'AMPA_g': {'sec':'soma', 'loc':0.5, 'synMech':'AMPA', 'var':'g'},
    'AMPA_i': {'sec':'soma', 'loc':0.5, 'synMech':'AMPA', 'var':'i'}}
simConfig.recordStim = True  # record spikes of cell stims
simConfig.recordStep = 0.025 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
simConfig.filename = 'mpiHybridTut'  # Set file output name
simConfig.saveFileStep = 1000 # step size in ms to save data to disk
simConfig.savePickle = False # Whether or not to write spikes etc. to a .mat file
simConfig.saveJson = False # Whether or not to write spikes etc. to a .mat file
simConfig.saveMat = False # Whether or not to write spikes etc. to a .mat file
simConfig.saveTxt = False # save spikes and conn to txt file
simConfig.saveDpk = False # save to a .dpk pickled file


# Analysis and plotting 
simConfig['analysis'] = {}
simConfig['analysis']['plotRaster'] = True # Whether or not to plot a raster
simConfig['analysis']['plotTraces'] = {'include': [1,51]} # plot recorded traces for this list of cells

