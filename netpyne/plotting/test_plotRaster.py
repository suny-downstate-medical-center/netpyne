import os

def runSim():

    from netpyne import specs, sim

    ## Network parameters
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
    netParams.cellParams['ETC'] = PYRcell

    ## Population parameters
    netParams.popParams['Pop_0'] = {'cellType': 'PYR', 'numCells': 20}
    netParams.popParams['Pop_1'] = {'cellType': 'PYR', 'numCells': 20}
    netParams.popParams['Pop_2'] = {'cellType': 'ETC', 'numCells': 10}

    ## Synaptic mechanism parameters
    netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  # excitatory synaptic mechanism

    ## Stimulation parameters
    netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.5}
    netParams.stimTargetParams['bkg->PYR'] = {'source': 'bkg', 'conds': {'cellType': 'PYR'}, 'weight': 0.01, 'delay': 5, 'synMech': 'exc', 'sec':'soma'}

    netParams.stimSourceParams['IClamp0'] = {'type': 'IClamp', 'del': 200, 'dur': 200, 'amp': '10.0'}
    netParams.stimTargetParams['IClamp0->cell0'] = {'source': 'IClamp0', 'conds': {'gid': 0}, 'sec': 'soma', 'loc': 0.5}


    ## Cell connectivity rules
    netParams.connParams['Pop_0->Pop_1'] = {'preConds': {'pop': 'Pop_0'}, 'postConds': {'pop': 'Pop_1'}, 
        'probability': 0.5,         # probability of connection
        'weight': 0.01,             # synaptic weight 
        'delay': 5,                 # transmission delay (ms) 
        'sec': 'dend',              # section to connect to
        'loc': 1.0,                 # location of synapse
        'synMech': 'exc'}           # target synaptic mechanism

    netParams.connParams['Pop_1->Pop_2'] = {'preConds': {'pop': 'Pop_1'}, 'postConds': {'pop': 'Pop_2'}, 
        'probability': 0.75,         # probability of connection
        'weight': 0.015,             # synaptic weight 
        'delay': 5,                 # transmission delay (ms) 
        'sec': 'dend',              # section to connect to
        'loc': 1.0,                 # location of synapse
        'synMech': 'exc'}           # target synaptic mechanism


    # Simulation options
    simConfig = specs.SimConfig()       # object of class SimConfig to store simulation configuration

    simConfig.duration = 1*1e3          # Duration of the simulation, in ms
    simConfig.dt = 0.025                # Internal integration timestep to use
    simConfig.verbose = False           # Show detailed messages 
    #simConfig.recordTraces = {'V_soma': {'conds': {'gid': [0,10]},'sec':'soma','loc':0.5,'var':'v'}}  
    #simConfig.recordTraces['IClamp0i'] = {'conds': {'gid': [0]}, 'sec': 'soma', 'loc': 0.5,'var':'i'}
    #simConfig.recordTraces['SM0'] = {'conds': {'gid': [0]}, 'sec': 'dend', 'synMech': 'exc', 'var': 'i'}

    #simConfig.recordCells = ['all']
    simConfig.recordStep = 1            # Step size in ms to save data (eg. V traces, LFP, etc)
    simConfig.filename = 'testing'         # Set file output name
    simConfig.savePickle = False        # Save params, network and sim output to pickle file

    simConfig.analysis['plotRaster'] = {'saveFig': True} #, 'include': 'allNetStims'}                  # Plot a raster
    #simConfig.analysis['plotTraces'] = {'include': [1], 'saveFig': True}  # Plot recorded traces for this list of cells
    #simConfig.analysis['plot2Dnet'] = {'saveFig': True}                   # plot 2D cell positions and connections

    # Create network and run simulation
    sim.createSimulateAnalyze(netParams = netParams, simConfig = simConfig)    
   
    #rasterData = sim.analysis.prepareRaster()
    #rasterPlotter = sim.plotting.plotRaster(rasterData, marker='o')
    #rasterPlotter = sim.plotting.plotRaster(marker='o') # it also works without data input

    return sim

def test_simConfig_raster():
    sim = runSim()
    assert os.path.isfile('testing_raster.png')



def save_raster_plots(sim):
    rasterData = sim.analysis.prepareRaster()
    for file_format in ['jpg', 'pdf', 'ps', 'svg', 'tif']:
        sim.plotting.plotRaster(saveFig=True, fileType=file_format)
        
def test_raster_file_formats():
    sim = runSim()
    save_raster_plots(sim)
    for file_format in ['jpg', 'pdf', 'ps', 'svg', 'tif']:
        assert os.path.isfile('file_format' + '.' + file_format)




