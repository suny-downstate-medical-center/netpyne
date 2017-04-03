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
# SIMULATION PARAMETERS
###############################################################################

# Simulation parameters
simConfig.duration = 0.5*1e3 # Duration of the simulation, in ms
simConfig.dt = 0.1 # Internal integration timestep to use
simConfig.createNEURONObj = 1  # create HOC objects when instantiating network
simConfig.createPyStruct = 1  # create Python structure (simulator-independent) when instantiating network
simConfig.verbose = 1 #False  # show detailed messages 

# Recording 
simConfig.recordCells = [('PYR1',5), 8]
simConfig.recordTraces = {'Vsoma':{'sec':'soma','loc':0.5,'var':'v'}}

# # Analysis and plotting 
#simConfig.analysis['plotRaster'] = {'figSize': (20,8)} #True
#simConfig.analysis['plot2Dnet'] = True



###############################################################################
# NETWORK PARAMETERS
###############################################################################

netParams.sizeX = 100
netParams.sizeY = 50
netParams.sizeZ = 20



# Population parameters
netParams.popParams['PYR1'] = {'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 1} # 'gridSpacing': 10, 'xRange': [30,60]} # pop of HH cells
netParams.popParams['PYR2'] = {'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 1} # 'gridSpacing': 5, 'yRange': [20,40]} # pop of HH cells
#netParams.popParams['artifVec'] = {'cellModel': 'VecStim', 'numCells': 1, 'interval': 100, 'noise': 0.5, 'start': 50, 
#    'pulses':[{'start': 1000, 'end': 1400, 'rate': 100, 'noise': 0.5}]}  # pop of NetStims
# netParams.popParams['artif1'] = {'cellModel': 'VecStim', 'numCells': 100, 'rate': [0,5], 'noise': 1.0, 'start': 50}#, 
#    'pulses': [{'start': 200, 'end': 300, 'rate': 50, 'noise':0.2}, {'start': 500, 'end': 800, 'rate': 30, 'noise':0.5}]}  # pop of NetStims

# Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': 0}


# Stimulation parameters
#netParams.stimSourceParams['background'] = {'type': 'NetStim', 'interval': 100, 'number': 1e5, 'start': 500, 'noise': 0.5}  # stim using NetStims after 500ms
#netParams.stimTargetParams['bkg->PYR1'] = {'source': 'background', 'conds': {'popLabel': 'PYR1'}, 'sec':'soma', 'loc': 0.5, 'weight': 0.5, 'delay': 1}


# Cell parameters
## PYR cell properties
cellParams = Dict()
cellParams.secs.soma.geom = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
cellParams.secs.soma.mechs.hh = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}
cellParams.conds = {'cellType': 'PYR'}
netParams.cellParams['PYR'] = cellParams


# Connections
# netParams.connParams['artif1->PYR1'] = {
#     'preConds': {'popLabel': 'artif1'}, 'postConds': {'popLabel': 'PYR1'},
#     'convergence': 4,
#     'weight': 0.005,                    
#     'synMech': 'AMPA',                
#     'delay': 'uniform(1,5)',
#     'synsPerConn': 1}          

netParams.connParams['PYR1->PYR2_1'] = {
    'preConds': {'popLabel': 'PYR1'}, 'postConds': {'popLabel': 'PYR2'},
    'probability': 0.1,
    'weight': 0.2,                     
    'delay': 'uniform(1,5)',
    'synsPerConn': 1}     

netParams.connParams['PYR1->PYR2_2'] = {
    'preConds': {'popLabel': 'PYR1'}, 'postConds': {'popLabel': 'PYR2'},
    'probability': 0.1,
    'weight': 0.4,                     
    'delay': 'uniform(1,5)',
    'synsPerConn': 1} 

# netParams.addConnParams('artif1->PYR2',
#     {'preConds': {'popLabel': 'artif1'}, 'postConds': {'popLabel': 'PYR2'}, 
#     'divergence': 3,
#     'weight': 0.05,              
#     'delay': 3,
#     'synsPerConn': 1})        



###############################################################################
# RUN SIM
###############################################################################

sim.createSimulateAnalyze()


#sim.create()
#sim.gatherData()

