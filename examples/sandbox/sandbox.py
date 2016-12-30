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

# Population parameters
#netParams.popParams['PYR1'] = {'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 10} # pop of HH cells
#netParams.popParams['artifVec'] = {'cellModel': 'VecStim', 'numCells': 10000, 'interval': 100, 'noise': 0.5, 'start': 50}  # pop of NetStims
netParams.popParams['artifNet'] = {'cellModel': 'VecStim', 'numCells': 1000, 'rate': 5, 'noise': 0.5, 'start': 50, 
    'pulses': [{'start': 200, 'end': 300, 'rate': 50, 'noise':0.2}, {'start': 500, 'end': 800, 'rate': 30, 'noise':0.5}]}  # pop of NetStims

# Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': 0}


# Stimulation parameters
# netParams.stimSourceParams['background'] = {'type': 'NetStim', 'interval': 100, 'number': 1e5, 'start': 500, 'noise': 0.5}  # stim using NetStims after 500ms
# netParams.stimTargetParams['bkg->PYR1'] = {'source': 'background', 'conds': {'popLabel': 'PYR1'}, 'sec':'soma', 'loc': 0.5, 'weight': 0.5, 'delay': 1}


# Cell parameters
## PYR cell properties
cellParams = Dict()
cellParams.secs.soma.geom = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
cellParams.secs.soma.mechs.hh = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}
cellParams.conds = {'cellType': 'PYR'}
netParams.cellParams['PYR'] = cellParams


# Connections
netParams.connParams['artif1->PYR1'] = {
    'preConds': {'popLabel': 'artif1'}, 'postConds': {'popLabel': 'PYR1'},
    'convergence': 8,
    'weight': 0.005,                    
    'synMech': 'AMPA',                
    'delay': 'uniform(1,5)'}          

# netParams.connParams['PYR1->artif2'] = {
#     'preConds': {'popLabel': 'PYR1'}, 'postConds': {'popLabel': 'artif2'},
#     'probability': 0.2,
#     'weight': 0.2,                     
#     'delay': 'uniform(1,5)'}     

# netParams.addConnParams('artif2->artif3',
#     {'preConds': {'popLabel': 'artif2'}, 'postConds': {'popLabel': 'artif3'}, 
#     'divergence': 20,
#     'weight': 0.05,              
#     'delay': 3})        


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


