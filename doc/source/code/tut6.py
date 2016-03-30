"""
params.py 

netParams is a dict containing a set of network parameters using a standardized structure

simConfig is a dict containing a set of simulation configurations using a standardized structure

Contributors: salvadordura@gmail.com
"""

from netpyne import framework as f

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
netParams['popParams'].append({'popLabel': 'PYR', 'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 50}) # add dict with params for this pop 
netParams['popParams'].append({'popLabel': 'background', 'cellModel': 'NetStim', 'rate': 40, 'noise': 0.5, 'source': 'random'})  # background inputs

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
netParams['synMechParams'].append({'label': 'NMDA', 'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': 0})
 

# Connectivity parameters
netParams['connParams'] = []  

netParams['connParams'].append(
    {'preTags': {'popLabel': 'PYR'}, 'postTags': {'popLabel': 'PYR'},
    'weight': -0.02,                    # weight of each connection
    'delay': 5,     					# delay 
    'threshold': 10}) # ,                # threshold
    #'convergence': 'uniform(1,15)'})    # convergence (num presyn targeting postsyn) is uniformly distributed between 1 and 15

netParams['connParams'].append(
    {'preTags': {'popLabel': 'background'}, 'postTags': {'cellType': 'PYR'}, # background -> PYR
    'weight': 0.1,                    # fixed weight of 0.08
    'synMech': 'NMDA',                     # target NMDA synapse
    'delay': 'uniform(1,5)'})           # uniformly distributed delays between 1-5ms


###############################################################################
# SIMULATION PARAMETERS
###############################################################################

simConfig = {}  # dictionary to store simConfig

# Simulation parameters
simConfig['duration'] = 0.5*1e3 # Duration of the simulation, in ms
simConfig['dt'] = 0.025 # Internal integration timestep to use
simConfig['randseed'] = 1 # Random seed to use
simConfig['createNEURONObj'] = 1  # create HOC objects when instantiating network
simConfig['createPyStruct'] = 1  # create Python structure (simulator-independent) when instantiating network
simConfig['verbose'] = False  # show detailed messages 


# Recording 
simConfig['recordCells'] = []  # which cells to record from
simConfig['recordTraces'] = {'Vsoma':{'sec':'soma','pos':0.5,'var':'v'}}
simConfig['recordStim'] = True  # record spikes of cell stims
simConfig['recordStep'] = 0.1 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
simConfig['filename'] = 'mpiHHTut'  # Set file output name
simConfig['saveFileStep'] = 1000 # step size in ms to save data to disk
simConfig['savePickle'] = False # Whether or not to write spikes etc. to a .mat file
simConfig['saveJson'] = False # Whether or not to write spikes etc. to a .mat file
simConfig['saveMat'] = False # Whether or not to write spikes etc. to a .mat file
simConfig['saveTxt'] = False # save spikes and conn to txt file
simConfig['saveDpk'] = False # save to a .dpk pickled file


# Analysis and plotting 
simConfig['plotRaster'] = True # Whether or not to plot a raster
simConfig['plotCells'] = [0] # plot recorded traces for this list of cells
simConfig['plotSync'] = True  # add vertical lines for all spikes as an indication of synchrony
simConfig['plotLFPSpectrum'] = False # plot power spectral density
simConfig['maxspikestoplot'] = 3e8 # Maximum number of spikes to plot
simConfig['plotConn'] = False # whether to plot conn matrix
simConfig['plotWeightChanges'] = False # whether to plot weight changes (shown in conn matrix)
simConfig['plot3dArch'] = False # plot 3d architecture


# Create network and run simulation
# init.createAndSimulate(netParams = netParams, simConfig = simConfig)   
f.sim.initialize(                       # create network object and set cfg and net params
    simConfig = simConfig,   # pass simulation config and network params as arguments
    netParams = netParams)   
f.net.createPops()                      # instantiate network populations
f.net.createCells()                     # instantiate network cells based on defined populations
f.net.connectCells()                    # create connections between cells based on params
f.sim.setupRecording()                  # setup variables to record for each cell (spikes, V traces, etc)
f.sim.runSim()                          # run parallel Neuron simulation  
f.sim.gatherData()                      # gather spiking data and cell info from each node
f.sim.saveData()                        # save params, cell info and sim output to file (pickle,mat,txt,etc)
f.analysis.plotData()                   # plot spike raster


# f.net.changeAllWeights() or just changeAllWeights() not part of netpyne
# changeFracWeights() random fraction of weights