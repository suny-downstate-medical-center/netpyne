from netpyne import specs, sim 

netParams = specs.NetParams()   # object of class NetParams to store the network parameters
simConfig = specs.SimConfig()   # object of class SimConfig to store the simulation configuration

###############################################################################
# NETWORK PARAMETERS
###############################################################################

# General network parameters
netParams.scale = 1 # Scale factor for number of cells
netParams.sizeX = 200 # x-dimension (horizontal length) size in um
netParams.sizeY = 1000 # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = 30 # z-dimension (horizontal depth) size in um

###############################################################################
# Building Network
###############################################################################

# Creating a single Motor neuron chains:
netParams.popParams['MN'] = {'cellModel': 'Izhi', 'cellType': 'MN', 'xnormRange': [0.6, 1.0], 'ynormRange': [0.1, 0.2], 'numCells': 1}

MN_Params = {}
MN_Params['MN'] = {'mod':'Izhi2003b', 'a':0.02, 'b':0.2, 'c':-53, 'd':6}

## MN cell params (left side):

cellRule = {'conds': {'cellType': ['MN']}, 'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'pointps':{}}  #  soma
#cellRule['secs']['soma']['geom'] = {'diam': 10, 'L': 10, 'cm': 31.831}
cellRule['secs']['soma']['pointps']['Izhi'] = MN_Params['MN'] 
netParams.cellParams['MN_Rule'] = cellRule  # add dict to list of cell properties

###############################################################################
# STIMULATION CONFIGURATION
###############################################################################

netParams.stimSourceParams['bkg'] = {'type': 'IClamp', 'del': 500, 'dur': 200, 'amp': 0.0750}
netParams.stimTargetParams['bkg->PMs'] = {'source': 'bkg', 'sec':'soma', 'loc': 0.8, 'conds': {'cellType':['MN']}}

###############################################################################
# SIMULATION CONFIGURATION
###############################################################################

# Simulation parameters
simConfig.duration = 2*1e3 # Duration of the simulation, in ms
simConfig.dt = 0.001 # Internal integration timestep to use
simConfig.seeds = {'conn': 1, 'stim': 1, 'loc': 1} # Seeds for randomizers (connectivity, input stimulation and cell locations)
simConfig.createNEURONObj = 1  # create HOC objects when instantiating network
simConfig.createPyStruct = 1  # create Python structure (simulator-independent) when instantiating network
simConfig.verbose = 0 # Whether to write diagnostic information on events 
simConfig.oneSynPerNetcon = False

# Recording 
simConfig.recordCells = []  # list of cells to record from 
simConfig.recordTraces = {'V':{'sec':'soma','loc':0.5,'var':'v'}} 
simConfig.recordStim = False  # record spikes of cell stims
simConfig.recordStep = 0.1 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
simConfig.filename = 'Test1'  # Set file output name
simConfig.saveFileStep = 1000 # step size in ms to save data to disk
simConfig.savePickle = False # save to pickle file