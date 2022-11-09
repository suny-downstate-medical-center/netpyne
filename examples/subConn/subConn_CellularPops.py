from netpyne import specs, sim
import matplotlib.pyplot as plt
import numpy as np

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters


## Cell types
PYRcell = {'secs': {}}

PYRcell['secs']['soma'] = {'geom': {}, 'mechs': {}}
PYRcell['secs']['soma']['geom'] = {'diam': 20, 'L': 20, 'Ra': 123.0}
PYRcell['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}

PYRcell['secs']['dend1'] = {'geom': {}, 'topol': {}, 'mechs': {}}
PYRcell['secs']['dend1']['geom'] = {'diam': 1.0, 'L': 250.0, 'Ra': 150.0, 'nseg': 5, 'cm': 1}
PYRcell['secs']['dend1']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}

# example of usage of cell vars
PYRcell['vars'] = {'g_base': 'normal(3.57e-5, 1e-8)',
                   'g_decay_const': 'uniform(100, 110)'}
# The expression for `g` below is evaluated for each segment, so if expression explicitly contains random function, new random value will be generated per segment (likewise, segment-dependant variables like `dist_path` will get their per-segment values).
# On the other hand, values of cell vars in it (here: `g_base` and `g_decay_const`) are calculated once per cell and preserved across all segments of this cell,
# which means that all random distributions in cell variables get repicked only once per cell).
PYRcell['secs']['dend1']['mechs']['pas'] = {'g': 'g_base + uniform(1.1e-5, 1.2e-5) * exp(-dist_path/g_decay_const)', 'e': -70}


PYRcell['secs']['dend2'] = {'geom': {}, 'topol': {}, 'mechs': {}}
PYRcell['secs']['dend2']['geom'] = {'diam': 0.8, 'L': 200.0, 'Ra': 150.0, 'nseg': 5, 'cm': 1}
PYRcell['secs']['dend2']['topol'] = {'parentSec': 'dend1', 'parentX': 1.0, 'childX': 0}
PYRcell['secs']['dend2']['mechs']['pas'] = {'g': 'g_base', 'e': -70}

PYRcell['secs']['dend3'] = {'geom': {}, 'topol': {}, 'mechs': {}}
PYRcell['secs']['dend3']['geom'] = {'diam': 0.5, 'L': 150.0, 'Ra': 150.0, 'nseg': 5, 'cm': 1}
PYRcell['secs']['dend3']['topol'] = {'parentSec': 'dend2', 'parentX': 1.0,  'childX': 0}
PYRcell['secs']['dend3']['mechs']['pas'] = {'g': 'g_base', 'e': -70}

netParams.cellParams['PYR'] = PYRcell

netParams.defineCellShapes = True       # sets 3d geometry aligned along the y-axis 

## Population parameters
Ns = 100
Nm = 20
netParams.popParams['S'] = {'cellType': 'PYR', 'numCells': Ns}
netParams.popParams['M'] = {'cellType': 'PYR', 'numCells': Nm}


## Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  # excitatory synaptic mechanism


# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 1, 'noise': 0.5}
netParams.stimTargetParams['bkg->PYR'] = {'source': 'bkg', 'conds': {'cellType': 'PYR'}, 'weight': 0.01, 'delay': 5, 'synMech': 'exc'}


## Cell connectivity rules
netParams.connParams['S->M'] = {'preConds': {'pop': 'S'}, 'postConds': {'pop': 'M'},  #  S -> M
    'probability': 0.5,         # probability of connection
    'weight': 0.0001,           # synaptic weight
    'delay': 5,                 # transmission delay (ms)
    'sec': 'dend1',              # section to connect to
    'loc': 0.5,                 # location of synapse
    'synMech': 'exc'}           # target synaptic mechanism


# Simulation options
simConfig = specs.SimConfig()       # object of class SimConfig to store simulation configuration

simConfig.duration = 1*1e3          # Duration of the simulation, in ms
simConfig.dt = 0.025                # Internal integration timestep to use
simConfig.verbose = False           # Show detailed messages
simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'},'V_dend1':{'sec':'dend1','loc':0.5,'var':'v'}}  # Dict with traces to record
simConfig.recordStep = 0.1            # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'subconn_without'         # Set file output name
simConfig.savePickle = False        # Save params, network and sim output to pickle file
simConfig.saveDat = True

watchneuron = Ns     # first neuron in population M (where S impinges on) 

simConfig.analysis['plotTraces'] = {'include': [watchneuron], 'saveFig': True}  # Plot recorded traces for this list of cells
simConfig.analysis['plotShape'] = {'includePre': ['S'],'includePost': [watchneuron],'cvar':'numSyns','dist':0.7, 'saveFig': True}

# Create network and run simulation
sim.createSimulateAnalyze(netParams = netParams, simConfig = simConfig)
t1 = sim.allSimData['t']
Vsoma1 = sim.allSimData['V_soma']['cell_%d' %watchneuron]
Vdend1 = sim.allSimData['V_dend1']['cell_%d' %watchneuron]

#################################################
## Adds a Subcellular synaptic redistribution
#################################################
gridY = [x for x in range(0, 470, 10)]
gridValues = [np.exp(-((x-270)/50)**2) for x in range(0, 470, 10)]

fig, ax= plt.subplots()
ax.plot(gridY,gridValues)
plt.xlabel('Distance')
plt.ylabel('Density')
fig.savefig('density.jpg')

netParams.subConnParams['S->M'] = {
    'preConds': {'pop': 'S'}, 'postConds': {'pop': 'M'},  #  S -> M
    'sec': ['dend1','dend2'],   # probability of connection
    'density': {'type':'1Dmap','gridY':gridY,'gridValues':gridValues,'fixedSomaY':0}
    } 

simConfig.filename = 'subconn_with'         # Set file output name

# Create network and run simulation
sim.createSimulateAnalyze(netParams = netParams, simConfig = simConfig)
t2 = sim.allSimData['t']
Vsoma2 = sim.allSimData['V_soma']['cell_%d' %watchneuron]
Vdend2 = sim.allSimData['V_dend1']['cell_%d' %watchneuron]

fig, ax= plt.subplots()
ax.plot(t1,Vdend1)
ax.plot(t2,Vdend2)
plt.xlabel('Time')
plt.ylabel('Vdend')
fig.savefig('comparison.jpg')
