from netpyne import specs, sim

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

netParams.shape = 'cylinder'
netParams.sizeX = 100 # x-dimension (horizontal length) size in um
netParams.sizeY = 1000 # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = 100 # z-dimension (horizontal length) size in um
netParams.propVelocity = 100.0 # propagation velocity (um/ms)
netParams.probLengthConst = 150.0 # length constant for conn probability (um)


## Population parameters
netParams.popParams['E2'] = {'cellType': 'E', 'numCells': 50, 'yRange': [100,300], 'cellModel': 'HH'}
netParams.popParams['I2'] = {'cellType': 'I', 'numCells': 50, 'yRange': [100,300], 'cellModel': 'HH'}
netParams.popParams['E4'] = {'cellType': 'E', 'numCells': 50, 'yRange': [300,600], 'cellModel': 'HH'}
netParams.popParams['I4'] = {'cellType': 'I', 'numCells': 50, 'yRange': [300,600], 'cellModel': 'HH'}
netParams.popParams['E5'] = {'cellType': 'E', 'numCells': 50, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}
netParams.popParams['I5'] = {'cellType': 'I', 'numCells': 50, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}


## Cell property rules
cellRule = {'conds': {'cellType': 'E'},  'secs': {}}  # cell rule dict
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                              # soma params dict
cellRule['secs']['soma']['geom'] = {'diam': 15, 'L': 14, 'Ra': 120.0}                   # soma geometry
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.13, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}      # soma hh mechanism
netParams.cellParams['Erule'] = cellRule                          # add dict to list of cell params

cellRule = {'conds': {'cellType': 'I'},  'secs': {}}  # cell rule dict
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                              # soma params dict
cellRule['secs']['soma']['geom'] = {'diam': 10.0, 'L': 9.0, 'Ra': 110.0}                  # soma geometry
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.11, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}      # soma hh mechanism
netParams.cellParams['Irule'] = cellRule                          # add dict to list of cell params


## Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 5.3, 'e': 0}  # NMDA synaptic mechanism
netParams.synMechParams['inh'] = {'mod': 'Exp2Syn', 'tau1': 0.6, 'tau2': 8.5, 'e': -75}  # GABA synaptic mechanism


## Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 20, 'noise': 0.3}
netParams.stimTargetParams['bkg->all'] = {'source': 'bkg',
										'conds': {'cellType': ['E','I']},
										'weight': 0.01,
										'delay': 'max(1, normal(5,2))',
										'synMech': 'exc'}

## Connectivity parameters
netParams.connParams['E->all'] = {
                'preConds': {'cellType': 'E'},
                'postConds': {'y': [100,1000]},  #  E -> all (100-1000 um)
                'probability': 0.1,                  # probability of connection
                'weight': '0.002*post_ynorm',         # synaptic weight
                'delay': 'dist_3D/propVelocity',      # transmission delay (ms)
                'synMech': 'exc'}                    # synaptic mechanism

netParams.connParams['I->E'] = {
                'preConds': {'cellType': 'I'},
                'postConds': {'pop': ['E2','E4','E5']},       #  I -> E
                'probability': '0.4*exp(-dist_3D/probLengthConst)',   # probability of connection
                'weight': 0.001,                                     # synaptic weight
                'delay': 'dist_3D/propVelocity',                    # transmission delay (ms)
                'synMech': 'inh'}                                  # synaptic mechanism


# Simulation options
cfg = specs.SimConfig()        # object of class simConfig to store simulation configuration

cfg.duration = 1*1e3           # Duration of the simulation, in ms
cfg.dt = 0.05                 # Internal integration timestep to use
cfg.verbose = False            # Show detailed messages
cfg.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
cfg.recordStep = 1             # Step size in ms to save data (e.g. V traces, LFP, etc)
cfg.filename = 'model_output'  # Set file output name
cfg.saveJson = True  # Save params, network and sim output to pickle file
cfg.recordStim = True  # required for netClamp to work

cfg.analysis['plotRaster'] = {'orderBy': 'y', 'orderInverse': True}      # Plot a raster
cfg.analysis['plotTraces'] = {'include': [5]}      # Plot recorded traces for this list of cells

# Create network and run simulation
if __name__ == "__main__":
    sim.createSimulateAnalyze(netParams = netParams, simConfig = cfg)
