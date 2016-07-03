"""
params.py 

netParams is a dict containing a set of network parameters using a standardized structure

simConfig is a dict containing a set of simulation configurations using a standardized structure

Contributors: salvadordura@gmail.com
"""

from netpyne import utils

netParams = {}  # dictionary to store sets of network parameters
simConfig = {}  # dictionary to store sets of simulation configurations


###############################################################################
#
# SANDBOX PARAMS
#
###############################################################################

###############################################################################
# NETWORK PARAMETERS
###############################################################################

netParams['scaleConnWeightModels'] = {'HH': 1.0}

# Population parameters
netParams['popParams'] = []  # create list of populations - each item will contain dict with pop params
netParams['popParams'].append({'popLabel': 'PYR', 'cellModel': 'HH', 'cellType': 'PYR2sec', 'ynormRange':[0,0.5], 'numCells': 10}) # add dict with params for this pop 
netParams['popParams'].append({'popLabel': 'PYR2', 'cellModel': 'HH', 'cellType': 'PYR2sec', 'ynormRange':[0.3,0.6], 'numCells': 20}) # add dict with params for this pop 
netParams['popParams'].append({'popLabel': 'PYR3', 'cellModel': 'HH', 'cellType': 'PYR2sec', 'ynormRange':[0.2,1.0],'numCells': 20}) # add dict with params for this pop 

netParams['popParams'].append({'popLabel': 'background', 'cellModel': 'NetStim', 'rate': 100, 'noise': 0.5, 'start':1, 'seed':2})  # background inputs
netParams['popParams'].append({'popLabel': 'background2', 'cellModel': 'NetStim', 'rate': 20, 'noise': 0.5, 'start':1, 'seed':2})  # background inputs


# Synaptic mechanism parameters
netParams['synMechParams'] = []
netParams['synMechParams'].append({'label': 'AMPA', 'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': 0})
netParams['synMechParams'].append({'label': 'NMDA', 'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 5.0, 'e': 0})
 

# Cell parameters
netParams['cellParams'] = []

## PYR cell properties
cellRule = {'label': 'PYR', 'conditions': {'cellType': 'PYR'},  'sections': {}}
soma = {'geom': {}, 'topol': {}, 'mechs': {}}  # soma properties
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
soma['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} 
cellRule['sections'] = {'soma': soma}  # add sections to dict
netParams['cellParams'].append(cellRule)  # add dict to list of cell properties


## Cell property rules
cellRule = {'label': 'PYR2sec', 'conditions': {'cellType': 'PYR2sec'},  'sections': {}, 'secLists': {}}     # cell rule dict
soma = {'geom': {}, 'mechs': {}}                                            # soma params dict
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'cm':1}                                   # soma geometry
soma['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.0003, 'el': -54}          # soma hh mechanisms
# dend = {'geom': {}, 'topol': {}, 'mechs': {}, 'synMechs': {}}                               # dend params dict
# dend['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}                          # dend geometry
# dend['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}                      # dend topology 
# dend['mechs']['pas'] = {'g': 0.0000357, 'e': -70}                                       # dend mechanisms
cellRule['sections'] = {'soma': soma} #, 'dend': dend}                                     # add soma and dend sections to dict

# cellRule['secLists']['all'] = ['soma', 'dend']
netParams['cellParams'].append(cellRule)  # add dict to list of cell properties

### HH
# cellRule = {'label': 'PYR_HH_rule', 'conditions': {'cellType': 'PYR', 'cellModel': 'HH'}} 	# cell rule dict
# synMechParams = []
# utils.importCell(cellRule=cellRule, synMechParams=netParams['synMechParams'], fileName='HHCellFile.py', cellName='HHCellClass')
# netParams['cellParams'].append(cellRule)  												# add dict to list of cell parameters


# Stimulation parameters
netParams['stimParams'] = {'sourceList': [], 'stimList': []}
netParams['stimParams']['sourceList'].append({'label': 'Input_1', 'type': 'IClamp', 'delay': 10, 'dur': 800, 'amp': 'uniform(0.05,0.5)'})
netParams['stimParams']['sourceList'].append({'label': 'Input_2', 'type': 'VClamp', 'dur':[0,1,1], 'amp':[1,1,1],'gain':1, 'rstim':0, 'tau1':1, 'tau2':1, 'i':1})
netParams['stimParams']['sourceList'].append({'label': 'Input_3', 'type': 'AlphaSynapse', 'onset': 'uniform(1,500)', 'tau': 5, 'gmax': 'post_ynorm', 'e': 0})
netParams['stimParams']['sourceList'].append({'label': 'Input_4', 'type': 'NetStim', 'interval': 'uniform(20,100)', 'number': 1000, 'start': 5, 'noise': 0.1})

netParams['stimParams']['stimList'].append({
    'source': 'Input_1', 
    'sec':'soma', 
    'loc': 0.5, 
    'conditions': {'popLabel':'PYR', 'cellList': range(8)}})


netParams['stimParams']['stimList'].append({
    'source': 'Input_3', 
    'sec':'soma', 
    'loc': 0.5, 
    'conditions': {'popLabel':'PYR2', 'ynorm':[0.2,0.6]}})

netParams['stimParams']['stimList'].append({
	'source': 'Input_4', 
	'sec':'soma', 
	'loc': 0.5, 
    'weight': '0.1+gauss(0.2,0.05)',
    'delay': 1,
	'conditions': {'popLabel':'PYR3', 'cellList': [0,1,2,3,4,5,10,11,12,13,14,15]}})


# Connectivity parameters
netParams['connParams'] = []  

netParams['connParams'].append(
    {'preTags': {'popLabel': 'PYR'}, 'postTags': {'popLabel': 'PYR'},
    'weight': [[0.005, 0.02, 0.05, 0.04, 0.1], [0.11, 0.22, 0.33, 0.44, 0.55]],                  # weight of each connection
    'delay': '0.2+gauss(13.0,1.4)',     # delay min=0.2, mean=13.0, var = 1.4
    'synsPerConn': 5,
    'sec': 'all',
    'synMech': ['AMPA', 'NMDA'],
    'threshold': 10})                    # threshold

netParams['connParams'].append(
    {'preTags': {'popLabel': 'PYR'}, 'postTags': {'popLabel': 'PYR'},
    'weight': 0.005,                    # weight of each connection
    'delay': '0.2+gauss(13.0,1.4)',     # delay min=0.2, mean=13.0, var = 1.4
    'threshold': 10,                    # threshold
    'convergence': 'uniform(1,15)'})    # convergence (num presyn targeting postsyn) is uniformly distributed between 1 and 15

# netParams['connParams'].append(
#     {'preTags': {'popLabel': 'PYR'}, 'postTags': {'popLabel': 'PYR'},
#     'weight': 0.005,                    # weight of each connection
#     'delay': '0.2+gauss(13.0,1.4)',     # delay min=0.2, mean=13.0, var = 1.4
#     'threshold': 10,                    # threshold
#     'divergence': 'uniform(1,15)'})    # convergence (num presyn targeting postsyn) is uniformly distributed between 1 and 15

# netParams['connParams'].append(
#     {'preTags': {'popLabel': ['PYR']}, 'postTags': {'cellModel': 'HH', 'popLabel': 'PYR2'},
#     'weight': 'uniform(0.01, 0.1)',                    # weight of each connection
#     'delay': '0.2+gauss(13.0,1.4)',     # delay min=0.2, mean=13.0, var = 1.4
#     'threshold': 10,                    # threshold
#     'convergence': 10})
#     #'probability': 'uniform(0.2,0.6)'})    # convergence (num presyn targeting postsyn) is uniformly distributed between 1 and 15


# netParams['connParams'].append(
#     {'preTags': {'popLabel': 'PYR'}, 'postTags': {'popLabel': 'PYR'},
#     'connList': [[0,1],[3,1]],			# list of connections
#     'synMech': ['AMPA', 'NMDA'], 
#     'synsPerConn': 3,
#     'weight': [[[0.1, 0.5, 0.7], [0.3, 0.4, 0.5]],[[0.1, 0.5, 0.7], [0.3, 0.4, 0.5]]],           # weight of each connection
# 	'delay': 5,
#     'loc': 0.2,
#     'threshold': 10})                   # threshold


# netParams['connParams'].append(
#     {'preTags': {'popLabel': 'background2'}, 'postTags': {'cellType': 'PYR2sec'}, # background -> PYR
#     'weight': 1.0,                    # fixed weight of 0.08
#     'synMech': 'AMPA',                     # target NMDA synapse
#     'delay': 4,
#     'sec': 'soma'})           # uniformly distributed delays between 1-5ms

# netParams['connParams'].append(
#     {'preTags': {'popLabel': 'background2'}, 'postTags': {'cellType': 'PYR2sec'}, # background -> PYR
#     'synMech': ['AMPA', 'NMDA'], 
#     'synsPerConn': 3,
#     'weight': 0.2,                  
#     'delay': [5, 10],                
#     'loc': [[0.1, 0.5, 0.7], [0.3, 0.4, 0.5]]})           # uniformly distributed delays between 1-5ms

# netParams['connParams'].append(
#     {'preTags': {'popLabel': 'background2'}, 'postTags': {'cellType': 'PYR2sec'}, # background -> PYR
#     'weight': 0.02,                    # fixed weight of 0.08
#     'synMech': 'AMPA',                     # target NMDA synapse
#     'synsPerConn': 2,
#     'delay': 1})           # uniformly distributed delays between 1-5ms



# netParams['connParams'].append(
#     {'preTags': {'popLabel': 'background2'}, 'postTags': {'cellType': 'PYR2sec'}, # background -> PYR
#     'weight': 0.1,                    # fixed weight of 0.08
#     'synMech': 'AMPA',                     # target NMDA synapse
#     'delay': 'uniform(1,5)'})           # uniformly distributed delays between 1-5ms

netParams['subConnParams'].append(
    {'preTags': {'cellType': ['PYR']}, # 'cellType': ['IT', 'PT', 'CT']
    'postTags': {'popLabel': 'PYR3'},  # 'popLabel': 'L5_PT'
    'sec': 'all',
    'ynormRange': [0, 1.0],
    'density': [0.2, 0.1, 0.0, 0.0, 0.2, 0.5] }) # subcellulalr distribution



###############################################################################
# SIMULATION PARAMETERS
###############################################################################

simConfig = {}  # dictionary to store simConfig

# Simulation parameters
simConfig['duration'] = 1*1e3 # Duration of the simulation, in ms
simConfig['dt'] = 0.025 # Internal integration timestep to use
simConfig['seeds'] = {'conn': 2, 'stim': 2, 'loc': 2} # Seeds for randomizers (connectivity, input stimulation and cell locations)
simConfig['createNEURONObj'] = 1  # create HOC objects when instantiating network
simConfig['createPyStruct'] = 1  # create Python structure (simulator-independent) when instantiating network
simConfig['verbose'] = 0 #False  # show detailed messages 


# Recording 
simConfig['recordCells'] = [1,2]  # which cells to record from
simConfig['recordTraces'] = {'Vsoma':{'sec':'soma','loc':0.5,'var':'v'}}
#'AMPA_i': {'sec':'soma', 'loc':0.5, 'synMech':'AMPA', 'var':'i'}}
simConfig['recordStim'] = True  # record spikes of cell stims
simConfig['recordStep'] = 0.1 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
simConfig['filename'] = 'mpiHHTut'  # Set file output name
simConfig['saveFileStep'] = 1000 # step size in ms to save data to disk
simConfig['savePickle'] = 1 # Whether or not to write spikes etc. to a .mat file
simConfig['saveJson'] = 0 # Whether or not to write spikes etc. to a .mat file
simConfig['saveMat'] = 0 # Whether or not to write spikes etc. to a .mat file
simConfig['saveDpk'] = 0 # save to a .dpk pickled file
simConfig['saveHDF5'] = 0
simConfig['saveCSV'] = 0
simConfig['analysis'] = {}
simConfig['analysis']['plotRaster'] = True
simConfig['analysis']['plotTraces'] = {'include': [1,('PYR2',1)], 'oneFigPer':'trace'}

# # Analysis and plotting 
# simConfig['analysis']['plotRaster']={ 
#  'maxSpikes':3e8, 
#  'overlaySpikeHist': True,
#  'syncLines': True, 
#  'orderBy':'ynorm'|'y'|'popLabel'|'cellType',
#  'figId': 1,  # figs with same figId will be converted to subplots
#  'saveData': 'data2.pkl',
#  'saveName': 'fig1.png'}
# (include = ['all'], timeRange = None, maxSpikes = 1e8, orderBy = 'gid', orderInverse = False, spikeHist = None, syncLines = False, saveData = None, saveFig = None): 

# simConfig['analysis']['plotSpikeHist']={'include': ['PYR', 'allNetStims', 'background2', ('PYR',[5,6,7,8])], 
#     'timeRange': [400,600], 'binSize': 10, 'overlay':True, 'graphType': 'line', 'yaxis': 'count', 'saveData': None, 'saveFig': None, 'showFig': True}

#simConfig['analysis']['plot2Dnet'] = {'include': ['allCells']}
