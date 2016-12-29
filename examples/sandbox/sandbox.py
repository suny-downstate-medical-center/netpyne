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

import netpyne
netpyne.__gui__ = True

from netpyne import specs, sim
from netpyne.specs import Dict

netParams = specs.NetParams()  # object of class NetParams to store the network parameters
simConfig = specs.SimConfig()  # dictionary to store sets of simulation configurations


###############################################################################
# NETWORK PARAMETERS
###############################################################################

netParams.scaleConnWeightModels = {'HH': 1.0}
netParams.shape = 'cuboid'#'ellipsoid'# 'cylinder' 
netParams.sizeX = 100
netParams.sizeY = 300
netParams.sizeZ = 50


# Population parameters
netParams.popParams['PYR1'] = {'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 100}#, 'xRange': [20,80], 'ynormRange': [0.3,0.7]}) # add dict with params for this pop 
#netParams.addPopParams('PYR2', {'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 1}) # add dict with params for this pop 
netParams.popParams['bkg1'] = {'cellModel': 'NetStim', 'numCells': 100, 'rate': 50, 'noise': 0.8, 'start': 1, 'seed': 2}  # background inputs
netParams.popParams['bkg2'] = {'cellModel': 'IntFire2', 'numCells': 1, 'ib': 0}  # background inputs


# Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': 0}
#netParams.addSynMechParams('esyn', {'mod': 'ElectSyn', 'g': 0.000049999999999999996})

netParams.stimSourceParams['background'] = {'type': 'NetStim', 'interval': 5, 'number': 10000, 'start': 100, 'noise': 0.5}
netParams.stimTargetParams['bkg->PYR1'] = {'source': 'background', 'conds': {'popLabel': 'PYR1'}, 'sec':'soma', 'loc': 0.5, 'weight': 0.5, 'delay': 1}


# Cell parameters
## PYR cell properties
cellParams = Dict()
cellParams.secs.soma.geom = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
cellParams.secs.soma.mechs.hh = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}
cellParams.conds = {'cellType': 'PYR'}
netParams.addCellParams('PYR', cellParams)

# Connections
# netParams.connParams['bkg1->PYR1'] = {
#     'preConds': {'popLabel': 'bkg1'}, 'postConds': {'popLabel': 'PYR1'}, # background -> PYR
#     'convergence': 10,
#     'weight': 0.1,                    # fixed weight of 0.08
#     'synMech': 'AMPA',                     # target NMDA synapse
#     'delay': 'uniform(1,5)'}           # uniformly distributed delays between 1-5ms


# netParams.connParams['PYR1->bkg2'] = {
#     'preConds': {'popLabel': 'PYR1'}, 'postConds': {'popLabel': 'bkg2'}, # background -> PYR
#     'probability': 0.2,
#     'weight': 0.1,                    # fixed weight of 0.08
#     'synMech': 'AMPA',                     # target NMDA synapse
#     'delay': 'uniform(1,5)'}           # uniformly distributed delays between 1-5ms


# netParams.addConnParams('PYR1->PYR2',
#     {'preConds': {'popLabel': 'PYR1'}, 'postConds': {'popLabel': 'PYR2'}, # PYR1 -> PYR2 (gap junction)
#     'weight': 200.0,              
#     'synMech': 'esyn',                   
#     'gapJunction': True,
#     'sec': 'soma',
#     'loc': 0.5,
#     'preSec': 'soma',
#     'preLoc': 0.5})        


###############################################################################
# SIMULATION PARAMETERS
###############################################################################

# Simulation parameters
simConfig.duration = 1*1e3 # Duration of the simulation, in ms
simConfig.dt = 0.1 # Internal integration timestep to use
simConfig.seeds = {'conn': 2, 'stim': 2, 'loc': 2} # Seeds for randomizers (connectivity, input stimulation and cell locations)
simConfig.createNEURONObj = 1  # create HOC objects when instantiating network
simConfig.createPyStruct = 1  # create Python structure (simulator-independent) when instantiating network
simConfig.verbose = 0 #False  # show detailed messages 

# Recording 
simConfig.recordCells = [] # [1,2]  # which cells to record from
simConfig.recordTraces = {'Vsoma':{'sec':'soma','loc':0.5,'var':'v'}}

simConfig.recordStim = False  # record spikes of cell stims
simConfig.recordStep = 0.1 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
simConfig.filename = 'mpiHHTut'  # Set file output name
simConfig.saveFileStep = 1000 # step size in ms to save data to disk
simConfig.savePickle = 0 # Whether or not to write spikes etc. to a .mat file

# # Analysis and plotting 
simConfig.addAnalysis('plotRaster', {})#, {'spikeHist': 'subplot'})
# simConfig.addAnalysis('plotTraces', {'include': [0,1]})
#simConfig.addAnalysis('plot2Dnet', {'view': 'xz'})



###############################################################################
# RUN SIM
###############################################################################


sim.initialize(netParams = netParams, simConfig = simConfig)
sim.net.createPops()
sim.net.createCells()
sim.net.connectCells()
sim.net.addStims()
sim.setupRecording()

sim.simulate()

sim.analyze()


