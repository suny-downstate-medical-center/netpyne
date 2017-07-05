
from netpyne import specs  # import netpyne specs module
from netpyne import sim    # import netpyne sim module

###############################################################################
# NETWORK PARAMETERS
###############################################################################
netParams = specs.NetParams()

netParams.popParams['pop_pre'] = {'cellModel': 'RS1', 'cellType': 'RS', 'numCells': 2}
netParams.popParams['pop_post'] = {'cellModel': 'RS1', 'cellType': 'RS', 'numCells': 1}

# cellParams
netParams.cellParams['RS'] = {'conds': {'cellModel': 'RS1', 'cellType': 'RS'}, 
                            'secs': {'soma': {'geom':{'diam': 18.8, 'L': 18.8, 'Ra': 123.0}, 
                                              'mechs': {'hh': {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}}}}}

# synMechParams
netParams.synMechParams['expsyn'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 5.0, 'e': 0}

netParams.stimSourceParams['Stim0_0_pop_pre_0_soma_0_5'] = {
        'type': 'NetStim', 'rate': 100, 'noise': 0.0}

# stimTargetParams
netParams.stimTargetParams['Stim0_0_pop_pre_0_soma_0_5'] = {
        'conds': {'pop': 'pop_pre'}, #'cellList': [0,1],
        'loc': 0.5,
        'sec': 'soma',
        'weight': 0.05,
        'synMech': 'expsyn',
        'source': 'Stim0_0_pop_pre_0_soma_0_5'}

# connParams
netParams.connParams['pre->post'] = {
    'preConds': {'pop': 'pop_pre'},
    'postConds': {'pop': 'pop_post'},
    'synMech': 'expsyn',
    'weight': 0.1,
    'delay': 5,
    'threshold': 0
}
 
###############################################################################
# SIMULATION PARAMETERS
###############################################################################

simConfig = specs.SimConfig()   # object of class SimConfig to store the simulation configuration

# Simulation parameters
simConfig.duration = simConfig.tstop = 100.0 # Duration of the simulation, in ms
simConfig.dt = 0.1 # Internal integration timestep to use

simConfig.seeds = {'conn': 0, 'stim': 0, 'loc': 0} 

simConfig.createNEURONObj = 1  # create HOC objects when instantiating network
simConfig.createPyStruct = 1  # create Python structure (simulator-independent) when instantiating network
simConfig.verbose = 0 # show detailed messages 

# Recording 
simConfig.recordCells = ['all']  

# Column: v_pop_pre_0_RS_v: Pop: pop_pre; cell: 0; segment id: $oc.segment_id; segment name: soma; Neuron loc: soma(0.5); value: v (v)
simConfig.recordTraces['Volts_file__pop_pre_pop_pre_0_soma_v'] = {'sec':'soma','loc':0.5,'var':'v','conds':{'pop':'pop_pre'}}#,'cellLabel':0}}
# Column: v_pop_pre_1_RS_v: Pop: pop_pre; cell: 1; segment id: $oc.segment_id; segment name: soma; Neuron loc: soma(0.5); value: v (v)
simConfig.recordTraces['Volts_file__pop_pre_pop_pre_1_soma_v'] = {'sec':'soma','loc':0.5,'var':'v','conds':{'pop':'pop_pre'}}#, 'cellLabel':1}}
# Column: v_pop_post_0_RS_v: Pop: pop_post; cell: 0; segment id: $oc.segment_id; segment name: soma; Neuron loc: soma(0.5); value: v (v)
simConfig.recordTraces['Volts_file__pop_post_pop_post_0_soma_v'] = {'sec':'soma','loc':0.5,'var':'v','conds':{'pop':'pop_post'}}#, 'cellLabel':0}}

simConfig.recordStim = True  # record spikes of cell stims
simConfig.recordStep = simConfig.dt # Step size in ms to save data (eg. V traces, LFP, etc)

# Analysis and plottingsimConfig.plotRaster = True # Whether or not to plot a raster
simConfig.analysis.plotTraces = {'include': ['all']}

# Saving
simConfig.saveJson=1
simConfig.saveFileStep = simConfig.dt # step size in ms to save data to disk

###############################################################################
# RUN SIM
###############################################################################

sim.create()
sim.cfg.filename = 'SpikingNet_netpyne_'+str(sim.nhosts)  # Set file output name
sim.simulate()
sim.analyze()

sim.pc.barrier()
sim.pc.done()
quit()
