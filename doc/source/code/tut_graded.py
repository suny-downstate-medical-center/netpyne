
from netpyne import specs, sim

netParams = specs.NetParams()  # object of class NetParams to store the network parameters
simConfig = specs.SimConfig()  # dictionary to store sets of simulation configurations


###############################################################################
# NETWORK PARAMETERS
###############################################################################

## Cell parameters/rules
PYRcell = {'secs': {}}
PYRcell['secs']['soma'] = {'geom': {}, 'mechs': {}}  # soma params dict
PYRcell['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}  # soma geometry
PYRcell['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
netParams.cellParams['PYR'] = PYRcell

# Population parameters
netParams.popParams['PYR1'] = {'cellType': 'PYR', 'numCells': 1}
netParams.popParams['PYR2'] = {'cellType': 'PYR', 'numCells': 1}
netParams.popParams['background1'] = {'cellModel': 'NetStim', 'numCells': 1, 'rate': 20, 'noise': 0.5, 'start': 1, 'seed': 2}  # background inputs
netParams.popParams['background2'] = {'cellModel': 'NetStim', 'numCells': 1, 'rate': 20, 'noise': 0.5, 'start': 1, 'seed': 2}  # background inputs

# Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': 0}
netParams.synMechParams['gradsyn'] = {
    'mod': 'GradedSyn',
    'esyn': -20.0,
    'vslope': 10.0,
    'vth': -40.0,
    'tau': 10.0,
    'pointerParams': {'target_var': 'vpeer', # establish pointer connection targeting 'vpeer' variable of GradedSyn mechanism
                      'bidirectional': False} # only connect in pre->post direction (otherwise - both ways, as it's usually done for gap junctions)
}


# Connections
netParams.connParams['bg1->PYR1'] = {
    'preConds': {'pop': 'background1'}, 'postConds': {'pop': 'PYR1'}, # background -> PYR
    'weight': 0.05,
    'synMech': 'AMPA',                 # target NMDA synapse
    'delay': 'uniform(1,5)'}           # uniformly distributed delays between 1-5ms

netParams.connParams['bg2->PYR2'] = {
    'preConds': {'pop': 'background2'}, 'postConds': {'pop': 'PYR2'}, # background -> PYR
    'weight': 0.05,
    'synMech': 'AMPA',                 # target NMDA synapse
    'delay': 'uniform(1,5)'}           # uniformly distributed delays between 1-5ms

netParams.connParams['PYR1->PYR2'] = {
    'preConds': {'pop': 'PYR1'}, 'postConds': {'pop': 'PYR2'}, # PYR1 -> PYR2 (gap junction)
    'weight': 0.1,        # it may be a separate factor, but here it is assumed to be the maximal conductance (see .mod)
    'synMech': 'gradsyn',
    'sec': 'soma',
    'loc': 0.5,
    'preSec': 'soma',
    'preLoc': 0.5}


###############################################################################
# SIMULATION PARAMETERS
###############################################################################

# Simulation parameters
simConfig.duration = 1000 # Duration of the simulation, in ms
simConfig.dt = 0.1 # Internal integration timestep to use
simConfig.createNEURONObj = True  # create HOC objects when instantiating network
simConfig.createPyStruct = True   # create Python structure (simulator-independent) when instantiating network
simConfig.verbose = True          # show detailed messages

# Recording
simConfig.recordTraces = {'Vsoma':{'sec':'soma','loc':0.5,'var':'v'}}

# # Analysis and plotting
simConfig.analysis['plotRaster'] = True
simConfig.analysis['plotTraces'] = {'include': [0,1], 'saveFig': True}  # Plot recorded traces for this list of cells


###############################################################################
# RUN SIM
###############################################################################

sim.createSimulateAnalyze()