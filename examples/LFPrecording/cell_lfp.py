from netpyne import specs, sim

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

netParams.sizeX = 200 # x-dimension (horizontal length) size in um
netParams.sizeY = 1000 # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = 20 # z-dimension (horizontal length) size in um

## Population parameters
netParams.popParams['E'] = {'cellType': 'E', 'numCells': 1, 'yRange': [700,800], 'cellModel': 'HH'}

## Cell property rules
netParams.loadCellParamsRule(label='Erule', fileName='PT5B_full_cellParams.json')
netParams.cellParams['Erule']['conds'] = {'cellType': ['E']}

## Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 5.3, 'e': 0}  # NMDA synaptic mechanism

# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 50, 'noise': 0.0}
netParams.stimTargetParams['bkg->all'] = {'source': 'bkg', 'conds': {'cellType': ['E']}, 'weight': 10.0, 'sec': 'soma', 'delay': 15, 'synMech': 'exc'}


# Simulation options
simConfig = specs.SimConfig()        # object of class SimConfig to store simulation configuration
simConfig.duration = 0.05*1e3           # Duration of the simulation, in ms
simConfig.dt = 0.1                # Internal integration timestep to use
simConfig.verbose = False            # Show detailed messages
simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}
simConfig.recordStep = 1             # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'cell_lfp'  # Set file output name

simConfig.recordLFP = [[x, y, 35] for y in range(280, 1000, 150) for x in [30, 90]]

simConfig.analysis['plotTraces'] = {'include': [('E',0)], 'oneFigPer':'cell', 'overlay': True, 'figSize': (5,3),'saveFig': True}      # Plot recorded traces for this list of cells
simConfig.analysis['plotLFP'] = {'includeAxon': False, 'plots': ['timeSeries',  'locations'], 'figSize': (5,9), 'saveFig': True}

# Create network and run simulation
sim.createSimulateAnalyze(netParams = netParams, simConfig = simConfig)

# check model output
sim.checkOutput('cell_lfp')
