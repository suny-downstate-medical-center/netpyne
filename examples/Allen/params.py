from netpyne import specs,sim

###############################################################################
# NETWORK PARAMETERS
###############################################################################

netParams = specs.NetParams()       # object of class NetParams to store the network parameters

netParams.sizeX = 25                # x-dimension (horizontal length) size in um
netParams.sizeY = 1200              # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = 25                # z-dimension (horizontal length) size in um
netParams.propVelocity = 200.0      # propagation velocity (um/ms)
netParams.probLengthConst = 100.0   # length constant for conn probability (um)


## Population parameters
netParams.popParams['L2_E']  = {'cellType': 'E2', 'density': 80e3, 'ynormRange': [0.2,0.4], 'cellModel': 'perisom'}
netParams.popParams['L2_IF'] = {'cellType': 'IF', 'density': 10e3, 'ynormRange': [0.2,0.4], 'cellModel': 'perisom'} 
netParams.popParams['L2_IL'] = {'cellType': 'IL', 'density': 10e3, 'ynormRange': [0.2,0.4], 'cellModel': 'perisom'}
netParams.popParams['L4_E']  = {'cellType': 'E4', 'density': 80e3, 'ynormRange': [0.4,0.6], 'cellModel': 'perisom'} 
netParams.popParams['L4_IF'] = {'cellType': 'IF', 'density': 10e3, 'ynormRange': [0.4,0.6], 'cellModel': 'perisom'} 
netParams.popParams['L4_IL'] = {'cellType': 'IL', 'density': 10e3, 'ynormRange': [0.4,0.6], 'cellModel': 'perisom'} 
netParams.popParams['L5_E']  = {'cellType': 'E5', 'density': 80e3, 'ynormRange': [0.6,0.8], 'cellModel': 'perisom'}
netParams.popParams['L5_IF'] = {'cellType': 'IF', 'density': 10e3, 'ynormRange': [0.6,0.8], 'cellModel': 'perisom'} 
netParams.popParams['L5_IL'] = {'cellType': 'IL', 'density': 10e3, 'ynormRange': [0.6,0.8], 'cellModel': 'perisom'}


## Cell property rules
# import biophysical perisomatic models
netParams.importCellParams(label='E2_perisom', conds={'cellType': 'E2', 'cellModel': 'perisom'}, fileName='getCells.py', cellName='E2')
netParams.importCellParams(label='E4_perisom', conds={'cellType': 'E4', 'cellModel': 'perisom'}, fileName='getCells.py', cellName='E4')
netParams.importCellParams(label='E5_perisom', conds={'cellType': 'E5', 'cellModel': 'perisom'}, fileName='getCells.py', cellName='E5')
netParams.importCellParams(label='IF_perisom', conds={'cellType': 'IF', 'cellModel': 'perisom'}, fileName='getCells.py', cellName='IF')
netParams.importCellParams(label='IL_perisom', conds={'cellType': 'IL', 'cellModel': 'perisom'}, fileName='getCells.py', cellName='IL')

# add simple model
cellRule = {'conds': {'cellType': 'E2', 'cellModel': 'simple'},  'secs': {}}                        # cell rule dict
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                # soma params dict
cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                           # soma geometry
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}  # soma hh mechanism
netParams.cellParams['E2_simple'] = cellRule                                                        # add cell params rule

# Set vinit for all sections of all cells
for cellRule in netParams.cellParams.values():
    for sec in cellRule['secs'].values():
        sec['vinit'] = -90.0


## Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # excitatory synaptic mechanism
netParams.synMechParams['GABA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 18.2, 'e': -80}  # inhibitory synaptic mechanism
 

## Cell connectivity rules
conns = 1
if conns:
    netParams.connParams['E2->all'] = {'preConds': {'cellType': 'E2'},          # presyn: E2
        'postConds': {'ynorm': [0.2, 0.8]},                                     # postsyn: 0.2-0.8
        'probability': '0.2*exp(-dist_3D/probLengthConst)',                     # distance-dependent probability
        'weight': 0.05,                                                         # synaptic weight 
        'delay': 'dist_3D/propVelocity',                                        # distance-dependent transmission delay (ms) 
        'synMech': 'AMPA',                                                      # target synaptic mechanism        
        'synsPerConn': 5}                                                       # synapses per connection  

    netParams.connParams['E4->E2'] = {'preConds': {'popLabel': 'L4_E'},         # presyn: L4_E
        'postConds': {'popLabel': 'L2_E'},                                      # postsyn: L2_E 
        'probability': 0.15,                                                    # fixed probability
        'weight': '0.5*post_ynorm',                                             # synaptic weight depends of normalized cortical depth of postsyn cell 
        'delay': 'gauss(5,1)',                                                  # gaussian distributed transmission delay (ms) 
        'synMech': 'AMPA',                                                      # target synaptic mechanism 
        'synsPerConn': 5}                                                       # uniformly distributed synapses per connection  

    netParams.connParams['I->all'] = {'preConds': {'cellType': ['IF', 'IL']}, # presyn: I
        'postConds': {'cellModel': 'perisom', 'y': [100, 1100]},                # postsyn: perisom, [100,1100]
        'probability': '0.2*exp(-dist_3D/probLengthConst)',                     # distance-dependent probability
        'weight': 0.002,                                                        # synaptic weight 
        'delay': 'dist_3D/propVelocity',                                        # transmission delay (ms) 
        'synMech': 'GABA',                                                      # synaptic mechanism 
        'synsPerConn': 5}                                                       # synapses per connection  


## Subcellular connectivity rules


## Stimulation parameters
netParams.stimSourceParams['Input1'] = {'type': 'NetStim', 'interval': 'uniform(10,50)', 'noise': 0.5}    # Input NetStim params 

netParams.stimTargetParams['Input1->all'] = {'source': 'Input1', 'conds': {'ynorm': [0,1]},       # Input source -> all cells
  'weight': 0.05,  'delay': 2, 'sec': 'all', 'synMech': 'AMPA', 'synsPerConn': 5}   # connection params


###############################################################################
# SIMULATION CONFIGURATION
###############################################################################

simConfig = specs.SimConfig()                # object of class SimConfig to store simulation configuration

simConfig.duration = 100                     # Duration of the simulation, in ms
simConfig.dt = 0.1                           # Internal integration timestep, in ms
simConfig.verbose = 1                        # Show detailed messages 
simConfig.createNEURONObj = False              # create HOC objects when instantiating network
simConfig.createPyStruct = True              # create Python structure (simulator-independent) when instantiating network

# Recording
simConfig.recordStep = 0.1                                  # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.recordTraces = {'V_soma': {'sec': 'soma_0', 'loc': 0.5, 'var': 'v'},
    'V_dend6': {'sec': 'dend_6', 'loc': 0.5, 'var': 'v'}}   # Dict with traces to record

# Saving
simConfig.filename = 'Allen'                  # Set file output name
simConfig.saveDataInclude = ['netParams', 'net', 'simConfig']
simConfig.saveJson = True                     # Save params, network and sim output to pickle file

# Analysis
simConfig.addAnalysis('plotRaster', True) #{'orderBy': 'y', 'orderInverse': True})      # Plot a raster
simConfig.addAnalysis('plotTraces', {'include': [('L2_E', 0), ('L5_IF', 0)]})      # Plot recorded traces for this list of cells
# simConfig.addAnalysis('plot2Dnet', True)           # plot 2D visualization of cell positions and connections
# simConfig.addAnalysis('plotConn', True)           # plot connectivity matrix

#sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig) 

# import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty
