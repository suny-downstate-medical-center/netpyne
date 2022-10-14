"""
tut_artif.py

Tutorial on artificial cells (no sections)
"""

from netpyne import specs, sim
from netpyne.specs import Dict

netParams = specs.NetParams()  # object of class NetParams to store the network parameters
simConfig = specs.SimConfig()  # dictionary to store sets of simulation configurations


###############################################################################
# NETWORK PARAMETERS
###############################################################################
# Cell parameters
## PYR cell properties
cellParams = Dict()
cellParams.secs.soma.geom = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
cellParams.secs.soma.mechs.hh = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}
netParams.cellParams['PYR'] = cellParams

## IntFire2 artificial cell
netParams.cellParams['artif_IntFire2'] = {
    'cellModel': 'IntFire2',
    'params': {
        'ib': 0,
    },
}

## IntFire4 artificial cell
netParams.cellParams['artif_IntFire4'] = {
    'cellModel': 'IntFire4',
    'params': {
        'taue': 1.0,
    },
}

## NetStim artificial spike generator
netParams.cellParams['artif_NetStim'] = {
    'cellModel': 'NetStim'}
    
## VecStim artificial spike generator
netParams.cellParams['artif_VecStim'] = {
    'cellModel': 'VecStim'}  # pop of Vecstims with 2 pulses


# Population parameters
netParams.popParams['PYR1'] = {
    'cellType': 'PYR', 
    'numCells': 100} # pop of HH cells

netParams.popParams['pop_IntFire2'] = {
    'cellType': 'artif_IntFire2', 
    'numCells': 100}  # pop of IntFire2

netParams.popParams['pop_IntFire4'] = {
    'cellType': 'artif_IntFire4', 
    'numCells': 100}  # pop of IntFire4

netParams.popParams['pop_NetStim'] = {
    'cellType': 'artif_NetStim', 
    'numCells': 100,
    'rate': 10, 
    'noise': 0.8, 
    'start': 1, 
    'seed': 2}  # pop of NEtSims

netParams.popParams['pop_VecStim'] = {
    'cellType': 'artif_VecStim', 
    'numCells': 100, 
    'rate': 5, 
    'noise': 0.5, 
    'start': 50,
    'pulses': [{'start': 200, 'end': 300, 'rate': 60, 'noise':0.2}, 
               {'start': 500, 'end': 800, 'rate': 30, 'noise': 0.5}]}  # pop of Vecstims with 2 pulses


# Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': 0}


# Connections
netParams.connParams['NetStim->PYR1'] = {
    'preConds': {'pop': 'pop_NetStim'}, 
    'postConds': {'pop': 'PYR1'},
    'convergence': 3,
    'weight': 0.002,
    'synMech': 'AMPA',
    'delay': 'uniform(1,5)'}


netParams.connParams['VecStim->PYR1'] = {
    'preConds': {'pop': 'pop_VecStim'}, 
    'postConds': {'pop': 'PYR1'},
    'probability': 0.4,
    'weight': 0.005,
    'synMech': 'AMPA',
    'delay': 'uniform(1,5)'}

netParams.connParams['PYR1->IntFire2'] = {
    'preConds': {'pop': 'PYR1'}, 
    'postConds': {'pop': 'pop_IntFire2'},
    'probability': 0.2,
    'weight': 0.1,
    'synMech': 'AMPA',
    'delay': 'uniform(1,5)'}


netParams.connParams['IntFire2->IntFire4'] = {
    'preConds': {'pop': 'pop_IntFire2'}, 
    'postConds': {'pop': 'pop_IntFire4'},
    'probability': 0.1,
    'weight': 0.2,
    'delay': 'uniform(1,5)'}


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
simConfig.analysis['plotRaster'] = {'orderInverse': True}


###############################################################################
# RUN SIM
###############################################################################

sim.createSimulateAnalyze()
