from netpyne import specs, sim

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters


## Cell types
PYR_HH = {'secs': {}}
PYR_HH['secs']['soma'] = {'geom': {}, 'mechs': {}}                                                    # soma params dict
PYR_HH['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                               # soma geometry
PYR_HH['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}      # soma hh mechanisms
PYR_HH['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}                                       # dend params dict
PYR_HH['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}                      # dend geometry
PYR_HH['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}                  # dend topology
PYR_HH['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70}                                   # dend mechanisms
netParams.cellParams['PYR_HH'] = PYR_HH                                                               # add dict to list of cell parameters

PYR_Izhi = {'secs': {}}
PYR_Izhi['secs']['soma'] = {'geom': {}, 'pointps': {}}                        # soma params dict
PYR_Izhi['secs']['soma']['geom'] = {'diam': 10.0, 'L': 10.0, 'cm': 31.831}    # soma geometry
PYR_Izhi['secs']['soma']['pointps']['Izhi'] = {                               # soma Izhikevich properties
    'mod':'Izhi2007b',
    'C':1,
    'k':0.7,
    'vr':-60,
    'vt':-40,
    'vpeak':35,
    'a':0.03,
    'b':-2,
    'c':-50,
    'd':100,
    'celltype':1}
netParams.cellParams['PYR_Izhi'] = PYR_Izhi                                   # add dict to list of cell parameters

## Population parameters
netParams.popParams['S'] = {'cellType': 'PYR_Izhi', 'numCells': 20}
netParams.popParams['M'] = {'cellType': 'PYR_HH', 'numCells': 20}


## Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  # excitatory synapse


# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 100, 'noise': 0.5}
netParams.stimTargetParams['bkg->PYR'] = {'source': 'bkg', 'conds': {'cellType': ['PYR_Izhi', 'PYR_HH']}, 'weight': 0.01, 'delay': 5, 'synMech': 'exc'}


## Cell connectivity rules
netParams.connParams['S->M'] = {
    'preConds': {'pop': 'S'}, 'postConds': {'pop': 'M'},  #  S -> M
    'probability': 0.1,         # probability of connection
    'weight': 0.005,            # synaptic weight
    'delay': 5,                 # transmission delay (ms)
    'sec': 'dend',              # section to connect to
    'loc': 1.0,                 # location in section to connect to
    'synMech': 'exc'}           # target synapse


# Simulation options
simConfig = specs.SimConfig()       # object of class SimConfig to store simulation configuration
simConfig.duration = 1*1e3          # Duration of the simulation, in ms
simConfig.dt = 0.025                # Internal integration timestep to use
simConfig.verbose = False           # Show detailed messages
simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
simConfig.recordStep = 1            # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'tut4'         # Set file output name
simConfig.savePickle = False        # Save params, network and sim output to pickle file

simConfig.analysis['plotRaster'] = {'saveFig': True}                  # Plot a raster
simConfig.analysis['plotTraces'] = {'include': [1], 'saveFig': True}  # Plot recorded traces for this list of cells
simConfig.analysis['plot2Dnet'] = {'saveFig': True}                   # plot 2D cell positions and connections


# Create network and run simulation
sim.createSimulateAnalyze(netParams = netParams, simConfig = simConfig)

# import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty

# Check the model output: sim.checkOutput is used for testing purposes.  Please comment out the following line if you are exploring the tutorial.
sim.checkOutput('tut4')
