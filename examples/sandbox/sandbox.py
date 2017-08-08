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

# Population parameters
netParams.popParams['PYR'] = {'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 5} # add dict with params for this pop 
netParams.popParams['PYR2'] = {'cellModel': 'HH', 'cellType': 'PYR2', 'numCells': 5} # add dict with params for this pop 


# Cell parameters
## PYR cell properties
cellRule = {'conds': {'cellModel': 'HH', 'cellType': 'PYR'},  'secs': {}}   # cell rule dict
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                        # soma params dict
cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                                   # soma geometry
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}          # soma hh mechanism
cellRule['secs']['soma']['vinit'] = -71
netParams.cellParams['PYR'] = cellRule                                                  # add dict to list of cell params


cellRule = {'conds': {'cellModel': 'HH', 'cellType': 'PYR2'},  'secs': {}}   # cell rule dict
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                        # soma params dict
cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                                   # soma geometry
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}          # soma hh mechanism
cellRule['secs']['soma']['vinit'] = -71
netParams.cellParams['PYR2'] = cellRule                                                  # add dict to list of cell params

# Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': 0}
netParams.synMechParams['AMPA2'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': 0}


# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.5, 'start': 1}
netParams.stimSourceParams['bkg2'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.5, 'start': 1}

netParams.stimTargetParams['bkg->PYR1'] = {'source': 'bkg', 'conds': {'pop': 'PYR'}, 'weight': 0.1, 'synsPerConn':5, 'loc':0.5, 'synMech': 'AMPA', 'delay': 'uniform(1,5)'}


        # # connect stim source to target
        # for i in range(len(ns['synMech'])):
        #     if ns['synMech'][i] == 'AMPA': 
        #         #ns['weight'][i] = ns['weight'][0] * cfg.ratioAMPANMDA
        #         cur_weight = list(np.array(cur_weight) * cfg.ratioAMPANMDA)
        #     for curpop in ic['pop']:
        #         netParams.stimTargetParams[nslabel+'_'+curpop+'_'+ns['synMech'][i]] = \
        #             {'source': nslabel, 'conds': {'popLabel': ns['pop']}, 'sec': ns['sec'], 'synsPerConn': numActiveSpines, 'loc': cur_loc, 'synMech': ns['synMech'][i], 'weight': cur_weight, 'delay': cur_delay}



# Connectivity parameters
# netParams.connParams['PYR->PYR'] = {
#     'preConds': {'pop': 'PYR'}, 'postConds': {'pop': ['PYR','PYR2']},
#     'weight': 0.002,                    # weight of each connection
#     'delay': '0.2+normal(13.0,1.4)',     # delay min=0.2, mean=13.0, var = 1.4
#     'threshold': 10,                    # threshold
#     'synsPerCon': 5,
#     'synMech': ['AMPA', 'AMPA2'],
#     'sec': 'soma',
#     'convergence': 'uniform(1,15)'}    # convergence (num presyn targeting postsyn) is uniformly distributed between 1 and 15


###############################################################################
# SIMULATION PARAMETERS
###############################################################################

# Simulation parameters
simConfig.duration = 1*1e3 # Duration of the simulation, in ms
simConfig.dt = 0.05 # Internal integration timestep to use
simConfig.seeds = {'conn': 1, 'stim': 1, 'loc': 1} # Seeds for randomizers (connectivity, input stimulation and cell locations)
simConfig.createNEURONObj = 1  # create HOC objects when instantiating network
simConfig.createPyStruct = 1  # create Python structure (simulator-independent) when instantiating network
simConfig.verbose = False  # show detailed messages 

simConfig.checkErrors = 1

# Recording 
simConfig.recordCells = []  # which cells to record from
simConfig.recordTraces = {'Vsoma':{'sec':'soma','loc':0.5,'var':'v','conds': {'cellType': 'PYR2'}}}
simConfig.recordStim = True  # record spikes of cell stims
simConfig.recordStep = 0.1 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
simConfig.filename = 'HHTut'  # Set file output name
simConfig.saveFileStep = 1000 # step size in ms to save data to disk
simConfig.savePickle = False # Whether or not to write spikes etc. to a .mat file
simConfig.saveMat = True

# Analysis and plotting 
simConfig.analysis['plotRaster'] = True #  {'saveFig':1}
#simConfig.analysis['plotTraces'] = {'include': ['all'], 'oneFigPer':'trace'}

sim.createSimulateAnalyze()

#data=sim.loadSimData('HHTut.mat')


