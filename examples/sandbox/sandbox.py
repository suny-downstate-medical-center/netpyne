from netpyne import specs, sim

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

## Population parameters
netParams.popParams['E2'] = {'cellType': 'E', 'numCells': 5, 'yRange': [100,300], 'cellModel': 'HH'}

## Cell property rules
cellRule = {'conds': {'cellType': 'E'},  'secs': {}}  # cell rule dict
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}, 'ions':{}}                              # soma params dict
cellRule['secs']['soma']['geom'] = {'diam': 15, 'L': 14, 'Ra': 120.0, 'nseg': 1}                   # soma geometry
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.13, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}      # soma hh mechanism
cellRule['secs']['soma']['ions']['na'] = {'e': 60}  # soma hh mechanism
cellRule['secs']['soma']['weightNorm'] = [0.0005]

netParams.cellParams['Erule'] = cellRule                          # add dict to list of cell params


## Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 5.3, 'e': 0}  # NMDA synaptic mechanism
netParams.synMechParams['inh'] = {'mod': 'Exp2Syn', 'tau1': 0.6, 'tau2': 8.5, 'e': -75}  # GABA synaptic mechanism


# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 20, 'noise': 0.3}
netParams.stimTargetParams['bkg->all'] = {'source': 'bkg', 'conds': {'cellType': ['E','I']}, 'weight': 0.01, 'delay': 'max(1, normal(5,2))', 'synMech': 'exc'}



# Simulation options
simConfig = specs.SimConfig()        # object of class SimConfig to store simulation configuration
simConfig.duration = 1*1e3           # Duration of the simulation, in ms
simConfig.dt = 0.025                # Internal integration timestep to use
simConfig.verbose = 1          # Show detailed messages 
simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
simConfig.recordStep = 1             # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'tmp'  # Set file output name
simConfig.saveJson = True

# Create network and run simulation
sim.create(netParams=netParams, simConfig=simConfig)  #, interval = 100)    
sim.gatherData()
sim.analysis.plotConn()