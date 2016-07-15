"""
sandbox.py 

netParams is a class containing a set of network parameters using a standardized structure

simConfig is a class containing a set of simulation configurations using a standardized structure

Contributors: salvadordura@gmail.com
"""

###############################################################################
#
# SANDBOX PARAMS
#
###############################################################################

from netpyne import specs,sim
from netpyne.specs import Dict

netParams = specs.NetParams()  # object of class NetParams to store the network parameters
simConfig = specs.SimConfig()  # dictionary to store sets of simulation configurations


###############################################################################
# NETWORK PARAMETERS
###############################################################################

netParams.scaleConnWeightModels = {'HH': 1.0}

# Population parameters
netParams.addPopParams('PYR', {'cellModel': 'HH', 'cellType': 'PYR2sec', 'ynormRange': [0,0.5], 'numCells': 10}) # add dict with params for this pop 
netParams.addPopParams('PYR2', {'cellModel': 'HH', 'cellType': 'PYR2sec', 'ynormRange': [0.3,0.6], 'numCells': 20}) # add dict with params for this pop 
netParams.addPopParams('PYR3', {'cellModel': 'HH', 'cellType': 'PYR2sec', 'ynormRange': [0.2,1.0],'numCells': 20}) # add dict with params for this pop 

netParams.addPopParams('background', {'cellModel': 'NetStim', 'rate': 100, 'noise': 0.5, 'start': 1, 'seed': 2})  # background inputs
netParams.addPopParams('background2', {'cellModel': 'NetStim', 'rate': 20, 'noise': 0.5, 'start': 1, 'seed': 2})  # background inputs


# Synaptic mechanism parameters
netParams.addSynMechParams('AMPA', {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': 0})
netParams.addSynMechParams('NMDA', {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 5.0, 'e': 0})
 

# Cell parameters
## PYR cell properties
cellParams = Dict()
cellParams.secs.soma.geom = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
cellParams.secs.soma.mechs.hh = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}
cellParams.conds = {'cellType': 'PYR'}
netParams.addCellParams('PYR', cellParams)


## PYR2sec cell properties
soma = {'geom': {}, 'mechs': {}}                                                    # soma params dict
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'cm':1}                                   # soma geometry
soma['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.0003, 'el': -54}          # soma hh mechanisms
dend = {'geom': {}, 'topol': {}, 'mechs': {}, 'synMechs': {}}                               # dend params dict
dend['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}                          # dend geometry
dend['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}                      # dend topology 
dend['mechs']['pas'] = {'g': 0.0000357, 'e': -70}                                       # dend mechanisms
cellParams = {'conds': {'cellType': 'PYR2sec'},  
            'secs': {'soma': soma, 'dend': dend}, 
            'secLists': {'all': ['soma', 'dend']}}     # cell rule dict
netParams.addCellParams('PYR2sec', cellParams)  # add dict to list of cell properties

### HH
# cellRule = {'label': 'PYR_HH_rule', 'conds': {'cellType': 'PYR', 'cellModel': 'HH'}} 	# cell rule dict
# synMechParams = []
# utils.importCell(cellRule=cellRule, synMechParams=netParams['synMechParams'], fileName='HHCellFile.py', cellName='HHCellClass')
# netParams['cellParams'].append(cellRule)  												# add dict to list of cell parameters


#Stimulation parameters
netParams.addStimSourceParams('Input_1', {'type': 'IClamp', 'delay': 10, 'dur': 800, 'amp': 'uniform(0.05,0.5)'})
netParams.addStimSourceParams('Input_2', {'type': 'VClamp', 'dur':[0,1,1], 'amp': [1,1,1], 'gain': 1, 'rstim': 0, 'tau1': 1, 'tau2': 1, 'i': 1})
netParams.addStimSourceParams('Input_3', {'type': 'AlphaSynapse', 'onset': 'uniform(1,500)', 'tau': 5, 'gmax': 'post_ynorm', 'e': 0})
netParams.addStimSourceParams('Input_4', {'type': 'NetStim', 'interval': 'uniform(20,100)', 'number': 1000, 'start': 5, 'noise': 0.1})

netParams.addStimTargetParams('Input_1_PYR', 
    {'source': 'Input_1', 
    'sec':'soma', 
    'loc': 0.5, 
    'conds': {'popLabel':'PYR', 'cellList': range(8)}})


netParams.addStimTargetParams('Input_3_PYR2', 
    {'source': 'Input_3', 
    'sec':'soma', 
    'loc': 0.5, 
    'conds': {'popLabel':'PYR2', 'ynorm':[0.2,0.6]}})

netParams.addStimTargetParams('Input_4_PYR3', 
	{'source': 'Input_4', 
	'sec':'soma', 
	'loc': 0.5, 
    'weight': '0.1+gauss(0.2,0.05)',
    'delay': 1,
	'conds': {'popLabel':'PYR3', 'cellList': [0,1,2,3,4,5,10,11,12,13,14,15]}})


# # Connectivity parameters
# netParams.addConnParams('PYRconn1',
#     {'preConds': {'popLabel': 'PYR'}, 'postConds': {'popLabel': 'PYR'},
#     'weight': [[0.005, 0.02, 0.05, 0.04, 0.1], [0.11, 0.22, 0.33, 0.44, 0.55]],                  # weight of each connection
#     'delay': '0.2+gauss(13.0,1.4)',     # delay min=0.2, mean=13.0, var = 1.4
#     'synsPerConn': 5,
#     'sec': 'all',
#     'synMech': ['AMPA', 'NMDA'],
#     'threshold': 10})                    # threshold

netParams.addConnParams('PYRconn2',
    {'preConds': {'popLabel': 'PYR'}, 'postConds': {'popLabel': 'PYR'},
    'weight': 0.005,                    # weight of each connection
    'delay': '0.2+gauss(13.0,1.4)',     # delay min=0.2, mean=13.0, var = 1.4
    'threshold': 10,                    # threshold
    'convergence': 'uniform(1,15)',
    'synMech': 'AMPA',
    'sec': 'all',
    'synsPerConn': 2})    # convergence (num presyn targeting postsyn) is uniformly distributed between 1 and 15

# netParams.addConnParams('PYR->PYR',
#     {'preConds': {'popLabel': 'PYR'}, 'postConds': {'popLabel': ['PYR','PYR2', 'PYR3']},
#     'weight': 0.001,                    # weight of each connection
#     'delay': '0.2+gauss(13.0,1.4)',     # delay min=0.2, mean=13.0, var = 1.4
#     'threshold': 10,                    # threshold
#     'divergence': 'uniform(1,15)'})    # convergence (num presyn targeting postsyn) is uniformly distributed between 1 and 15

# netParams.addConnParams(2,
#     {'preConds': {'popLabel': ['PYR']}, 'postConds': {'cellModel': 'HH', 'popLabel': 'PYR2'},
#     'weight': 'uniform(0.01, 0.1)',                    # weight of each connection
#     'delay': '0.2+gauss(13.0,1.4)',     # delay min=0.2, mean=13.0, var = 1.4
#     'threshold': 10,                    # threshold
#     'convergence': 10})
#     #'probability': 'uniform(0.2,0.6)'})    # convergence (num presyn targeting postsyn) is uniformly distributed between 1 and 15


# netParams.addConnParams(3,
#     {'preConds': {'popLabel': 'PYR'}, 'postConds': {'popLabel': 'PYR'},
#     'connList': [[0,1],[3,1]],			# list of connections
#     'synMech': ['AMPA', 'NMDA'], 
#     'synsPerConn': 3,
#     'weight': [[[0.1, 0.5, 0.7], [0.3, 0.4, 0.5]],[[0.1, 0.5, 0.7], [0.3, 0.4, 0.5]]],           # weight of each connection
# 	'delay': 5,
#     'loc': 0.2,
#     'threshold': 10})                   # threshold


# netParams.addConnParams('bg->PYR',
#     {'preConds': {'popLabel': 'background2'}, 'postConds': {'cellType': 'PYR2sec'}, # background -> PYR
#     'weight': 1.0,                    # fixed weight of 0.08
#     'synMech': 'AMPA',                     # target NMDA synapse
#     'delay': 4,
#     'sec': 'soma'})           # uniformly distributed delays between 1-5ms

# netParams.addConnParams('PYRconn3',
#     {'preConds': {'popLabel': 'background2'}, 'postConds': {'cellType': 'PYR2sec'}, # background -> PYR
#     'synMech': ['AMPA', 'NMDA'], 
#     'synsPerConn': 3,
#     'weight': 0.2,                  
#     'delay': [5, 10],                
#     'loc': [[0.1, 0.5, 0.7], [0.3, 0.4, 0.5]]})           # uniformly distributed delays between 1-5ms

# netParams.addConnParams('PYRconn4',
#     {'preConds': {'popLabel': 'background2'}, 'postConds': {'cellType': 'PYR2sec'}, # background -> PYR
#     'weight': 0.02,                    # fixed weight of 0.08
#     'synMech': 'AMPA',                     # target NMDA synapse
#     'synsPerConn': 2,
#     'delay': 1})           # uniformly distributed delays between 1-5ms



# netParams.connParams['PYRconn5']= {'preConds': {'popLabel': 'background2'}, 'postConds': {'cellType': 'PYR2sec'}, # background -> PYR
#     'weight': 0.1,                    # fixed weight of 0.08
#     'synMech': 'AMPA',                     # target NMDA synapse
#     'delay': 'uniform(1,5)'}           # uniformly distributed delays between 1-5ms


# netParams.addConnParams('PYRsub1',
#     {'preConds': {'cellType': ['PYR2sec']}, # 'cellType': ['IT', 'PT', 'CT']
#     'postConds': {'popLabel': 'PYR'},  # 'popLabel': 'L5_PT'
#     'sec': 'all',
#     'ynormRange': [0, 1.0],
#     'density': [0.2, 0.1, 0.0, 0.0, 0.2, 0.5] }) # subcellulalr distribution



###############################################################################
# SIMULATION PARAMETERS
###############################################################################

# Simulation parameters
simConfig.duration = 1*1e3 # Duration of the simulation, in ms
simConfig.dt = 0.025 # Internal integration timestep to use
simConfig.seeds = {'conn': 2, 'stim': 2, 'loc': 2} # Seeds for randomizers (connectivity, input stimulation and cell locations)
simConfig.createNEURONObj = 1  # create HOC objects when instantiating network
simConfig.createPyStruct = 1  # create Python structure (simulator-independent) when instantiating network
simConfig.verbose = 1 #False  # show detailed messages 

# Recording 
simConfig.recordCells = [1,2]  # which cells to record from
simConfig.recordTraces = {'Vsoma':{'sec':'soma','loc':0.5,'var':'v'}}
#'AMPA_i': {'sec':'soma', 'loc':0.5, 'synMech':'AMPA', 'var':'i'}}
simConfig.recordStim = True  # record spikes of cell stims
simConfig.recordStep = 0.1 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
simConfig.filename = 'mpiHHTut'  # Set file output name
simConfig.saveFileStep = 1000 # step size in ms to save data to disk
simConfig.savePickle = 1 # Whether or not to write spikes etc. to a .mat file
simConfig.saveJson = 1 # Whether or not to write spikes etc. to a .mat file
simConfig.saveMat = 1 # Whether or not to write spikes etc. to a .mat file
simConfig.saveDpk = 0 # save to a .dpk pickled file
simConfig.saveHDF5 = 0
simConfig.saveCSV = 0

# # Analysis and plotting 
simConfig.addAnalysis('plotRaster', True)
#simConfig.addAnalysis('plotTraces', {'include': [1, ('PYR2',1)], 'oneFigPer':'trace'})
# simConfig.addAnalysis('plotSpikeHist', {'include': ['PYR', 'allNetStims', 'background2', ('PYR',[5,6,7,8])], 
#     'timeRange': [400,600], 'binSize': 10, 'overlay':True, 'graphType': 'line', 'yaxis': 'count', 'saveData': True, 'saveFig': True, 'showFig': True})
# simConfig.addAnalysis('plot2Dnet', {'include': ['allCells']})
# simConfig.addAnalysis('plotConn', True)


###############################################################################
# RUN SIM
###############################################################################

#sim.createSimulateAnalyze(netParams = netParams, simConfig = simConfig)  # create and simulate network
sim.createSimulate(netParams = netParams, simConfig = simConfig)  # create and simulate network
sim.saveData()
#sim.analysis.plotData()
# sim.initialize(netParams = netParams, simConfig = simConfig)
# sim.net.createPops()
# sim.net.createCells()

# ###############################################################################
# # MODIFY and RUN SIM
# ###############################################################################

# sim.net.modifyCells({'conds': {'label': 'PYR2sec'}, 
#                     'secs': {'soma': {'geom': {'L': 100}}}})

# sim.net.modifyConns({'conds': {'label': 'PYR->PYR', 'weight': [0,0.001], 'loc': 0.5},
#                     'postConds': {'popLabel': 'PYR2', 'ynorm': [0.4,0.6]},
#                     'weight': 0.01})

# sim.net.modifyStims({'conds': {'source': 'Input_1', 'label': 'Input_1_PYR', 'dur': [600, 900]}, 
#                     'cellConds': {'popLabel': 'PYR', 'ynorm': [0.0,0.5]},
#                     'delay': 300})



# sim.simulate() # create and simulate network
# sim.analyze()


