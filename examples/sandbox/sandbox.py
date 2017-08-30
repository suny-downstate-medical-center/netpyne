"""
"""

from netpyne import specs
from netpyne import sim  # import netpyne sim module


netParams = specs.NetParams()   # object of class NetParams to store the network parameters
cfg = specs.SimConfig()   # object of class SimConfig to store the simulation configuration

###############################################################################
# NETWORK PARAMETERS
###############################################################################

# Population parameters
netParams.popParams['ExcPop'] = {'cellModel': 'HH', 'cellType': 'Exc','numCells': 50, 'yRange': [300, 500]} # add dict with params for this pop 
netParams.popParams['InhPop'] = {'cellModel': 'HH', 'cellType': 'Inh','numCells': 50, 'yRange': [600, 800]} # add dict with params for this pop 


## Cell property rules
cellRule = {'conds': {'cellType': 'Exc'},  'secs': {}}  # cell rule dict
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                              # soma params dict
cellRule['secs']['soma']['geom'] = {'diam': 15, 'L': 14, 'Ra': 120.0}                   # soma geometry
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}      # soma hh mechanism
netParams.cellParams['Erule'] = cellRule                          # add dict to list of cell params

cellRule = {'conds': {'cellType': 'Inh'},  'secs': {}}  # cell rule dict
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                              # soma params dict
cellRule['secs']['soma']['geom'] = {'diam': 10.0, 'L': 9.0, 'Ra': 110.0}                  # soma geometry
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}      # soma hh mechanism
netParams.cellParams['Irule'] = cellRule                          # add dict to list of cell params

# Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 5.3, 'e': 0}  # NMDA synaptic mechanism
netParams.synMechParams['GABA'] = {'mod': 'Exp2Syn', 'tau1': 0.6, 'tau2': 8.5, 'e': -75}  # GABA synaptic mechanism


# Stimulation parameters
#netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.5, 'start': 1000, 'stop': 2000}
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'interval': 10, 'noise': 0.5, 'start': 100,'number':15}
netParams.stimTargetParams['bkg->ExcPopType'] = {'source': 'bkg', 'conds': {'popLabel': 'ExcPop'}, 'weight': 0.01, 'delay': 'uniform(1,5)', 'synMech': 'AMPA'}


# # Connectivity parameters
netParams.connParams['ExcPop->ExcPop'] = {
    'preConds': {'popLabel': 'ExcPop'},                                         # presyn: PYR_E
    'postConds': {'popLabel': 'ExcPop'},                                        # postsyn: PYR_E 
    'probability': 0.1,
    'weight': 0.008,                                                        # weight of each connection
    'delay': 'max(1, normal(10,2))',                                         # gaussian distributed transmission delay (ms)
    'synMech': 'AMPA'}                                                      # target synaptic mechanism 

# netParams.connParams['ExcPop->InhPop'] = {
#     'preConds': {'popLabel': 'ExcPop'},                                         # presyn: PYR_E
#     'postConds': {'popLabel': 'InhPop'},                                        # postsyn: PYR_I 
#     'probability': 0.1,                                                     # fixed probability
#     'weight': 0.003,                                                        # weight of each connection
#     'delay': 'max(1, normal(10,2))',                                         # gaussian distributed transmission delay (ms)
#     'synMech': 'AMPA'}                                                      # target synaptic mechanism 

# netParams.connParams['InhPop->ExcPop'] = {
#     'preConds': {'popLabel': 'InhPop'},                                         # presyn: PYR_I
#     'postConds': {'popLabel': 'ExcPop'},                                        # postsyn: PYR_E 
#     'probability': 0.1,                                                     # fixed probability
#     'weight': 0.006,                                                        # weight of each connection
#     'delay': 'max(1, normal(10,2))',                                         # gaussian distributed transmission delay (ms) 
#     'synMech': 'GABA'}                                                      # target synaptic mechanism 

##############################################################################
# SIMULATION PARAMETERS
###############################################################################

# Simulation parameters
cfg.duration = 2*1e3 # Duration of the simulation, in ms
cfg.dt = 0.025 # Internal integration timestep to use
cfg.seeds = {'conn': 1, 'stim': 1, 'loc': 1} # Seeds for randomizers (connectivity, input stimulation and cell locations)
cfg.createNEURONObj = 1  # create HOC objects when instantiating network
cfg.createPyStruct = 1  # create Python structure (simulator-independent) when instantiating network
cfg.verbose = False  # show detailed messages 

# Recording 
cfg.recordCells = []  # which cells to record from
cfg.recordTraces = {'Vsoma':{'sec':'soma','loc':0.5,'var':'v'}}
cfg.recordStim = True  # record spikes of cell stims
cfg.recordStep = 0.1 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
cfg.filename = 'FirstExampleOscill'  # Set file output name
cfg.saveFileStep = 1000 # step size in ms to save data to disk
cfg.savePickle = True # Whether or not to write spikes etc. to a .mat file

# Analysis and plotting 
cfg.analysis['plotRaster'] = True  # Plot raster
cfg.analysis['plotTraces'] = {'include': [('ExcPop',10), ('InhPop',10)]}  # Plot raster
# cfg.analysis['plot2Dnet'] = True  # Plot 2D net cells and connections
# cfg.analysis['plotConn'] = True


sim.createSimulateAnalyze(netParams = netParams, simConfig = cfg)
import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty
