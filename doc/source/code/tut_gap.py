"""
tut_gap.py

Tutorial on using gap junctions
"""

from netpyne import specs, sim
from netpyne.specs import Dict

netParams = specs.NetParams()  # object of class NetParams to store the network parameters
simConfig = specs.SimConfig()  # dictionary to store sets of simulation configurations


###############################################################################
# NETWORK PARAMETERS
###############################################################################

# Population parameters
netParams.popParams['PYR1'] = {'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 1} # add dict with params for this pop
netParams.popParams['PYR2'] = {'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 1} # add dict with params for this pop
netParams.popParams['background'] = {'cellModel': 'NetStim', 'numCells': 2, 'rate': 20, 'noise': 0.5, 'start': 1, 'seed': 2}  # background inputs

# Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': 0}
netParams.synMechParams['esyn'] = {'mod': 'ElectSyn',
    'g': 0.000049999999999999996,
    'pointerParams': {
        'target_var':  'vpeer',
        'source_var': 'v', # already there by default:
        'bidirectional': True # already there by default:
    }
}

# Cell parameters
## PYR cell properties
cellParams = Dict()
cellParams.secs.soma.geom = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
cellParams.secs.soma.mechs.hh = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}
cellParams.conds = {'cellType': 'PYR'}
netParams.cellParams['PYR'] = cellParams

# Connections
netParams.connParams['bg->PYR1'] = {
    'preConds': {'pop': 'background'}, 'postConds': {'pop': 'PYR1'}, # background -> PYR
    'weight': 0.1,                    # fixed weight of 0.08
    'synMech': 'AMPA',                     # target NMDA synapse
    'delay': 'uniform(1,5)'}           # uniformly distributed delays between 1-5ms

netParams.connParams['PYR1->PYR2'] = {
    'preConds': {'pop': 'PYR1'}, 'postConds': {'pop': 'PYR2'}, # PYR1 -> PYR2 (gap junction)
    'weight': 200.0,
    'delay': 0.1,
    'synMech': 'esyn',
    # 'gapJunction': True, # deprecated way of defining default gap junction. Instead use 'pointerParams' when defining netParams.synMechParams
    'sec': 'soma',
    'loc': 0.5,
    'preSec': 'soma',
    'preLoc': 0.5}


###############################################################################
# SIMULATION PARAMETERS
###############################################################################

# Simulation parameters
simConfig.duration = 1*1e3 # Duration of the simulation, in ms
simConfig.dt = 0.1 # Internal integration timestep to use
simConfig.createNEURONObj = 1  # create HOC objects when instantiating network
simConfig.createPyStruct = 1  # create Python structure (simulator-independent) when instantiating network
simConfig.verbose = 0 #False  # show detailed messages

# Recording
simConfig.recordTraces = {'Vsoma':{'sec':'soma','loc':0.5,'var':'v'}}

# # Analysis and plotting
simConfig.analysis['plotRaster'] = True


###############################################################################
# RUN SIM
###############################################################################

sim.createSimulateAnalyze()
