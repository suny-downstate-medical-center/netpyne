from netpyne import specs, sim

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters


## Cell types
PYRcell = {'secs': {}}

PYRcell['secs']['soma'] = {'geom': {}, 'mechs': {}}
PYRcell['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
PYRcell['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}

PYRcell['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}
PYRcell['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}
PYRcell['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}
PYRcell['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70}

netParams.cellParams['PYR'] = PYRcell


## Population parameters
netParams.popParams['S'] = {'cellType': 'PYR', 'numCells': 20}
netParams.popParams['M'] = {'cellType': 'PYR', 'numCells': 20}


## Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  # excitatory synaptic mechanism


# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.5}
netParams.stimTargetParams['bkg->PYR'] = {'source': 'bkg', 'conds': {'cellType': 'PYR'}, 'weight': 0.01, 'delay': 5, 'synMech': 'exc'}


## Cell connectivity rules
netParams.connParams['S->M'] = {'preConds': {'pop': 'S'}, 'postConds': {'pop': 'M'},  #  S -> M
    'probability': 0.5,         # probability of connection
    'weight': 0.01,             # synaptic weight
    'delay': 5,                 # transmission delay (ms)
    'sec': 'dend',              # section to connect to
    'loc': 1.0,                 # location of synapse
    'synMech': 'exc'}           # target synaptic mechanism


# Simulation options
simConfig = specs.SimConfig()       # object of class SimConfig to store simulation configuration

simConfig.duration = 1*1e3          # Duration of the simulation, in ms
simConfig.dt = 0.025                # Internal integration timestep to use
simConfig.verbose = False           # Show detailed messages
simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
simConfig.recordStep = 1            # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'tut3'         # Set file output name
simConfig.savePickle = False        # Save params, network and sim output to pickle file

simConfig.analysis['plotRaster'] = {'saveFig': True}                  # Plot a raster
simConfig.analysis['plotTraces'] = {'include': [1], 'saveFig': True}  # Plot recorded traces for this list of cells
simConfig.analysis['plot2Dnet'] = {'saveFig': True}                   # plot 2D cell positions and connections


# Create network and run simulation
sim.createSimulateAnalyze(netParams = netParams, simConfig = simConfig)

# import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty

# Check the model output: sim.checkOutput is used for testing purposes.  Please comment out the following line if you are exploring the tutorial.
sim.checkOutput('tut3')
