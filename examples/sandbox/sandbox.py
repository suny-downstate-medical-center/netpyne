"""
params.py 

netParams is a dict containing a set of network parameters using a standardized structure

simConfig is a dict containing a set of simulation configurations using a standardized structure

Contributors: salvadordura@gmail.com
"""

from netpyne import specs, sim

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

netParams.probLengthConst = 200

# Population parameters
netParams.popParams['PYR'] = {'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 100, 'xnormRange': [0,0.2]} # add dict with params for this pop 
netParams.popParams['PYR2'] = {'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 100, 'xnormRange': [0.8,1.0]} # add dict with params for this pop 
#netParams.popParams['PYR3'] = {'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 5, 'xNormRange': [0.8,1.0]} # add dict with params for this pop 
netParams.popParams['INT'] = {'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 100, 'xnormRange': [0.4,0.6]} # add dict with params for this pop 


# Cell parameters
## PYR cell properties
cellRule = {'conds': {'cellModel': 'HH', 'cellType': 'PYR'},  'secs': {}}   # cell rule dict
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                        # soma params dict
cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                                   # soma geometry
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}          # soma hh mechanism
cellRule['secs']['soma']['vinit'] = -71
netParams.cellParams['PYR'] = cellRule                                                  # add dict to list of cell params


# cellRule = {'conds': {'cellModel': 'HH', 'cellType': 'PYR2'},  'secs': {}}   # cell rule dict
# cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                        # soma params dict
# cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                                   # soma geometry
# cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}          # soma hh mechanism
# cellRule['secs']['soma']['vinit'] = -71
# netParams.cellParams['PYR2'] = cellRule                                                  # add dict to list of cell params

# Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': 0}


# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.5, 'start': 1}
netParams.stimSourceParams['bkg2'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.5, 'start': 1}

netParams.stimTargetParams['bkg->PYR1'] = {'source': 'bkg', 'conds': {'pop': 'PYR'}, 'weight': 0.1, 'delay': 'uniform(1,5)'}


# Connectivity parameters
netParams.connParams['PYR->ALL'] = {
    'preConds': {'pop': ['PYR']}, 'postConds': {'pop': ['PYR2', 'INT']},
    'weight': 0.002,                    # weight of each connection
    'delay': '0.2+normal(13.0,1.4)',     # delay min=0.2, mean=13.0, var = 1.4
    'threshold': 10,                    # threshold
    'probability': 0.2}

netParams.connParams['INT->PYR2'] = {
    'preConds': {'pop': ['INT']}, 'postConds': {'pop': ['PYR2']},
    'weight': 0.002,                    # weight of each connection
    'delay': '0.2+normal(13.0,1.4)',     # delay min=0.2, mean=13.0, var = 1.4
    'threshold': 10,                    # threshold
    'probability': 0.2, # '0.4*exp(-dist_3D/probLengthConst)',
    'disynapticBias': 0.2}  


###############################################################################
# SIMULATION PARAMETERS
###############################################################################

# Simulation parameters
simConfig.duration = 0.1*1e3 # Duration of the simulation, in ms
simConfig.dt = 0.05 # Internal integration timestep to use
simConfig.seeds = {'conn': 1, 'stim': 1, 'loc': 1} # Seeds for randomizers (connectivity, input stimulation and cell locations)
simConfig.createNEURONObj = 1  # create HOC objects when instantiating network
simConfig.createPyStruct = 1  # create Python structure (simulator-independent) when instantiating network
simConfig.verbose = 0  # show detailed messages 

simConfig.checkErrors = 0

# Recording 
simConfig.recordCells = []  # which cells to record from
simConfig.recordTraces = {'Vsoma':{'sec':'soma','loc':0.5,'var':'v','conds': {'cellType': 'PYR2'}}}
simConfig.recordStim = True  # record spikes of cell stims
simConfig.recordStep = 0.1 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
simConfig.filename = 'HHTut'  # Set file output name
simConfig.saveFileStep = 1000 # step size in ms to save data to disk
simConfig.savePickle = False # Whether or not to write spikes etc. to a .mat file
simConfig.saveMat = 0

# Analysis and plotting 
simConfig.analysis['plotRaster'] = True
#simConfig.analysis['plotTraces'] = {'include': ['all'], 'oneFigPer':'trace'}
#simConfig.analysis['plot2Dnet'] = True
sim.createSimulateAnalyze()


print sim.analysis.calculateDisynaptic()

#data=sim.loadSimData('HHTut.mat')


