"""
params.py 

netParams is a dict containing a set of network parameters using a standardized structure

simConfig is a dict containing a set of simulation configurations using a standardized structure

Contributors: salvadordura@gmail.com
"""

from netpyne import specs

netParams = specs.NetParams()   # object of class NetParams to store the network parameters
simConfig = specs.SimConfig()   # object of class SimConfig to store the simulation configuration


###############################################################################
#
# MPI HH TUTORIAL PARAMS
#
###############################################################################

###############################################################################
# NETWORK PARAMETERS
###############################################################################

# Population parameters
netParams.addPopParams('PYR', {'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 200}) # add dict with params for this pop 
netParams.addPopParams('background', {'cellModel': 'NetStim', 'rate': 10, 'noise': 0.5, 'start': 1})  # background inputs

# Cell parameters

## PYR cell properties
cellRule = {'conds': {'cellModel': 'HH', 'cellType': 'PYR'},  'secs': {}} 	# cell rule dict
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}  														# soma params dict
cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}  									# soma geometry
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  		# soma hh mechanism
cellRule['secs']['soma']['vinit'] = -71
netParams.addCellParams('PYR', cellRule)  												# add dict to list of cell params


# Synaptic mechanism parameters
netParams.addSynMechParams('AMPA', {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': 0})

 
# Connectivity parameters
netParams.addConnParams('PYR->PYR',
    {'preConds': {'popLabel': 'PYR'}, 'postConds': {'popLabel': 'PYR'},
    'weight': 0.002,                    # weight of each connection
    'delay': '0.2+gauss(13.0,1.4)',     # delay min=0.2, mean=13.0, var = 1.4
    'threshold': 10,                    # threshold
    'convergence': 'uniform(1,15)'})    # convergence (num presyn targeting postsyn) is uniformly distributed between 1 and 15


netParams.addConnParams('bg->PYR',
    {'preConds': {'popLabel': 'background'}, 'postConds': {'cellType': 'PYR'}, # background -> PYR
    'weight': 0.1,                    # fixed weight of 0.08
    'synMech': 'AMPA',                     # target NMDA synapse
    'delay': 'uniform(1,5)'})           # uniformly distributed delays between 1-5ms


###############################################################################
# SIMULATION PARAMETERS
###############################################################################

# Simulation parameters
simConfig.duration = 1*1e3 # Duration of the simulation, in ms
simConfig.dt = 0.025 # Internal integration timestep to use
simConfig.seeds = {'conn': 1, 'stim': 1, 'loc': 1} # Seeds for randomizers (connectivity, input stimulation and cell locations)
simConfig.createNEURONObj = 1  # create HOC objects when instantiating network
simConfig.createPyStruct = 1  # create Python structure (simulator-independent) when instantiating network
simConfig.verbose = False  # show detailed messages 

# Recording 
simConfig.recordCells = []  # which cells to record from
simConfig.recordTraces = {'Vsoma':{'sec':'soma','loc':0.5,'var':'v'}}
simConfig.recordStim = True  # record spikes of cell stims
simConfig.recordStep = 0.1 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
simConfig.filename = 'HHTut'  # Set file output name
simConfig.saveFileStep = 1000 # step size in ms to save data to disk
simConfig.savePickle = False # Whether or not to write spikes etc. to a .mat file


# Analysis and plotting 
simConfig.addAnalysis('plotRaster', True) # Plot raster
simConfig.addAnalysis('plotTraces', {'include': [2]}) # Plot raster
simConfig.addAnalysis('plot2Dnet', True) # Plot 2D net cells and connections



