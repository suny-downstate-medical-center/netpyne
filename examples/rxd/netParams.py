from netpyne import specs, sim
import sys; reload(sys)

#------------------------------------------------------------------------------
#
# NETWORK PARAMETERS
#
#------------------------------------------------------------------------------

netParams = specs.NetParams()  # object of class NetParams to store the network parameters

netParams.sizeX = cfg.sizeX # x-dimension (horizontal length) size in um
netParams.sizeY = cfg.sizeY # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = cfg.sizeZ # z-dimension (horizontal length) size in um
netParams.propVelocity = 100.0 # propagation velocity (um/ms)
netParams.probLengthConst = 150.0 # length constant for conn probability (um)

## Population parameters
netParams.popParams['E2'] = {'cellType': 'E', 'numCells': 10, 'yRange': [50,150], 'cellModel': 'HH'}
netParams.popParams['I2'] = {'cellType': 'I', 'numCells': 10, 'yRange': [50,150], 'cellModel': 'HH'}
netParams.popParams['E4'] = {'cellType': 'E', 'numCells': 10, 'yRange': [150,300], 'cellModel': 'HH'}
netParams.popParams['I4'] = {'cellType': 'I', 'numCells': 10, 'yRange': [150,300], 'cellModel': 'HH'}
netParams.popParams['E5'] = {'cellType': 'E', 'numCells': 10, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}
netParams.popParams['I5'] = {'cellType': 'I', 'numCells': 10, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}

## Cell property rules
netParams.loadCellParamsRule(label='CellRule', fileName='cells/CSTR_rxd_cellParams.json')

## Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 5.3, 'e': 0}  # NMDA synaptic mechanism
netParams.synMechParams['inh'] = {'mod': 'Exp2Syn', 'tau1': 0.6, 'tau2': 8.5, 'e': -75}  # GABA synaptic mechanism

# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 20, 'noise': 0.3}
netParams.stimTargetParams['bkg->all'] = {'source': 'bkg', 'conds': {'cellType': ['E','I']}, 'weight': 0.01, 'sec': 'soma', 'delay': 'max(1, normal(5,2))', 'synMech': 'exc'}

## Cell connectivity rules
netParams.connParams['E->all'] = {
  'preConds': {'cellType': 'E'}, 'postConds': {'y': [50,500]},  #  E -> all (100-1000 um)
  'probability': 0.1,                  # probability of connection
  'weight': '0.04*post_ynorm',         # synaptic weight 
  'delay': 'dist_3D/propVelocity',      # transmission delay (ms)
  'sec': ['Adend1', 'Adend2', 'Adend3'], 
  'synMech': 'exc'}                     # synaptic mechanism 

netParams.connParams['I->E'] = {
  'preConds': {'cellType': 'I'}, 'postConds': {'pop': ['E2','E4','E5']},       #  I -> E
  'probability': '0.3*exp(-dist_3D/probLengthConst)',   # probability of connection
  'weight': 0.01,                                      # synaptic weight 
  'delay': 'dist_3D/propVelocity',                      # transmission delay (ms) 
  'sec': ['soma','Bdend'], 
  'synMech': 'inh'}                                     # synaptic mechanism 


# Simulation configuration
simConfig = specs.SimConfig()       # object of class SimConfig to store simulation configuration
simConfig.duration = 1.0*1e3        # Duration of the simulation, in ms
simConfig.hParams['v_init'] = -65   # set v_init to -65 mV
simConfig.dt = 0.1                  # Internal integration timestep to use
simConfig.verbose = False            # Show detailed messages 
simConfig.recordStep = 1             # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'net_lfp'   # Set file output name
simConfig.enableRxD = True      # enable RxD
simConfig.recordTraces = {'V_soma':{'sec': 'soma','loc': 0.5,'var': 'v'},
                          'ik_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'ik'},
                          'cai_soma': {'sec': 'soma', 'loc':0.5, 'var': 'cai'},
                          'cao_soma': {'sec': 'soma', 'loc':0.5, 'var': 'cao'}}


simConfig.recordLFP = [[-15, y, 1.0*netParams.sizeZ] for y in range(netParams.sizeY/3, netParams.sizeY, netParams.sizeY/3)]

simConfig.analysis['plotTraces']={'include': [0]}
simConfig.analysis['plotRaster'] = {'orderBy': 'y', 'orderInverse': True, 'saveFig': True, 'figSize': (9,3)}      # Plot a raster
simConfig.analysis['plotLFP'] = {'includeAxon': False, 'figSize': (6,10), 'NFFT': 256, 'noverlap': 48, 'nperseg': 64, 'saveFig': True} 
simConfig.analysis['plotRxDConcentration'] = {'speciesLabel': 'ca', 'regionLabel': 'extracellular'}


#### BELOW THIS LINE SHOULD BE DONE VIA NETPYNE-UI AND JUPYTER NB #####

testing = 0
if testing:
    # --------------------------------
    # Instantiate network (VIA NETPYNE-UI)
    # --------------------------------
    sim.initialize(netParams, simConfig)  # create network object and set cfg and net params
    sim.net.createPops()                  # instantiate network populations
    sim.net.createCells()                 # instantiate network cells based on defined populations
    sim.net.connectCells()                # create connections between cells based on params
    sim.net.addStims()                    # add external stimulation to cells (IClamps etc)

    # --------------------------------
    # Add RxD objects (VIA JUPYTER NB)
    # --------------------------------

    import gui_tut3_rxd
    sim.net.rxd['species']['ca'] = gui_tut3_rxd.ca
    sim.net.rxd['regions']['extracellular'] = gui_tut3_rxd.extracellular

    # --------------------------------
    # Simulate and analyze network (VIA NETPYNE-UI)
    # --------------------------------
    sim.setupRecording()             # setup variables to record for each cell (spikes, V traces, etc)
    sim.simulate()
    sim.analyze()      
    sim.analyze()
