from netpyne import specs, sim

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

## Population parameters
netParams.popParams['HH_pop'] = {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'HH'}
netParams.popParams['HH3D_pop_hoc'] = {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'HH3D_hoc'}
netParams.popParams['HH3D_pop_swc'] = {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'HH3D_swc'}
netParams.popParams['Traub_pop'] = {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Traub'}
netParams.popParams['Mainen_pop'] = {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Mainen'}
netParams.popParams['Friesen_pop'] = {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Friesen'}
netParams.popParams['Izhi03a_pop'] = {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Izh2003a'}
netParams.popParams['Izhi03b_pop'] = {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Izh2003b'}
netParams.popParams['Izhi07a_pop'] = {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Izh2007a'}
netParams.popParams['Izhi07b_pop'] = {'cellType': 'PYR', 'numCells': 5, 'cellModel': 'Izh2007b'}


### HH
netParams.importCellParams(
    label='PYR_HH_rule', 
    conds={'cellType': 'PYR', 'cellModel': 'HH'},
    fileName='HHCellFile.py', 
    cellName='HHCellClass', 
    importSynMechs=True,
    )


### HH3D HOC
cellRule = netParams.importCellParams(
    label='PYR_HH3D_hoc_rule', 
    conds={'cellType': 'PYR', 'cellModel': 'HH3D_hoc'},
    fileName='geom.hoc', 
    cellName='E21', 
    importSynMechs=False,
    )
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}
for secName in cellRule['secs']:
    cellRule['secs'][secName]['mechs']['pas'] = {'g': 0.0000357, 'e': -70}
    cellRule['secs'][secName]['geom']['cm'] = 1


### HH3D SWC
cellRule = netParams.importCellParams(
    label='PYR_HH3D_swc_rule', 
    conds={'cellType': 'PYR', 'cellModel': 'HH3D_swc'},
    fileName='BS0284.swc', 
    cellName='BS0284',
    )
netParams.renameCellParamsSec('PYR_HH3D_swc_rule', 'soma_0', 'soma')  # rename imported section 'soma_0' to 'soma'
for secName in cellRule['secs']:
    cellRule['secs'][secName]['mechs']['pas'] = {'g': 0.0000357, 'e': -70}
    cellRule['secs'][secName]['geom']['cm'] = 1
    if secName.startswith('soma'):
        cellRule['secs'][secName]['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}


### Traub
cellRule = netParams.importCellParams(
    label='PYR_Traub_rule', 
    conds={'cellType': 'PYR', 'cellModel': 'Traub'},
    fileName='pyr3_traub.hoc', 
    cellName='pyr3',
    )
somaSec = cellRule['secLists']['Soma'][0]
cellRule['secs'][somaSec]['spikeGenLoc'] = 0.5


### Mainen
netParams.importCellParams(
    label='PYR_Mainen_rule', 
    conds={'cellType': 'PYR', 'cellModel': 'Mainen'},
    fileName='mainen.py', 
    cellName='PYR2',
    )


### Friesen
cellRule = netParams.importCellParams(
    label='PYR_Friesen_rule', 
    conds={'cellType': 'PYR', 'cellModel': 'Friesen'},
    fileName='friesen.py', 
    cellName='MakeRSFCELL',
    )
cellRule['secs']['axon']['spikeGenLoc'] = 0.5


### Izhi2003a (independent voltage)
cellRule = netParams.importCellParams(
    label='PYR_Izhi03a_rule', 
    conds={'cellType': 'PYR', 'cellModel':'Izh2003a'},
    fileName='izhi2003Wrapper.py', 
    cellName='IzhiCell',
    cellArgs={'type':'tonic spiking', 'host':'dummy'},
    )
netParams.renameCellParamsSec('PYR_Izhi03a_rule', 'sec', 'soma')  # rename imported section 'sec' to 'soma'
cellRule['secs']['soma']['pointps']['Izhi2003a_0']['vref'] = 'V' # specify that uses its own voltage V


### Izhi2003b (section voltage)
netParams.importCellParams(
    label='PYR_Izhi03b_rule', 
    conds={'cellType': 'PYR', 'cellModel':'Izh2003b'},
    fileName='izhi2003Wrapper.py', 
    cellName='IzhiCell',  
    cellArgs={'type':'tonic spiking'},
    )


### Izhi2007a (independent voltage)
cellRule = netParams.importCellParams(
    label='PYR_Izhi07a_rule', 
    conds={'cellType': 'PYR', 'cellModel':'Izh2007a'},
    fileName='izhi2007Wrapper.py', 
    cellName='IzhiCell',  
    cellArgs={'type':'RS', 'host':'dummy'},
    )
netParams.renameCellParamsSec('PYR_Izhi07a_rule', 'sec', 'soma')  # rename imported section 'sec' to 'soma'
cellRule['secs']['soma']['pointps']['Izhi2007a_0']['vref'] = 'V' # specify that uses its own voltage V
cellRule['secs']['soma']['pointps']['Izhi2007a_0']['synList'] = ['AMPA', 'NMDA', 'GABAA', 'GABAB']  # specify its own synapses


### Izhi2007b (section voltage)
netParams.importCellParams(
    label='PYR_Izhi07b_rule', 
    conds={'cellType': 'PYR', 'cellModel':'Izh2007b'},
    fileName='izhi2007Wrapper.py', 
    cellName='IzhiCell',  
    cellArgs={'type':'RS'},
    )


## Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  # soma NMDA synapse


# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 50, 'noise': 0.5}
netParams.stimTargetParams['bg1'] = {'source': 'bkg', 'conds': {'cellType': 'PYR', 'cellModel': ['Traub', 'HH', 'HH3D_hoc', 'HH3D_swc', 'Mainen', 'Izh2003b', 'Izh2007b']}, 'weight': 0.1, 'delay': 5, 'sec': 'soma'}
netParams.stimTargetParams['bg2'] = {'source': 'bkg', 'conds': {'cellType': 'PYR', 'cellModel': ['Friesen','Izh2003a', 'Izh2007a']}, 'weight': 5, 'delay': 5, 'sec': 'soma'}


## Connectivity params
netParams.connParams['recurrent'] = {
    'preConds': {'cellType': 'PYR'}, 'postConds': {'cellType': 'PYR'},  #  PYR -> PYR random
    'connFunc': 'convConn',           # connectivity function (random)
    'convergence': 'uniform(0,10)',   # max number of incoming conns to cell
    'weight': 0.001,                  # synaptic weight
    'delay': 5,                       # transmission delay (ms)
    'sec': 'soma'}                    # section to connect to

netParams.connParams['HH->izhi07a'] = {
    'preConds': {'pop': 'HH_pop'}, 'postConds': {'pop': 'Izhi07a_pop'}, # background -> PYR (weight=0.1)
    'connFunc': 'fullConn',     # connectivity function (all-to-all)
    'weight': 5,                # synaptic weight
    'delay': 5,                 # transmission delay (ms)
    'sec': 'soma'}              # section to connect to

netParams.connParams['izhi07a->HH'] = {
    'preConds': {'pop': 'Izhi07a_pop'}, 'postConds': {'pop': 'HH_pop'}, # background -> PYR (weight=0.1)
    'connFunc': 'fullConn',     # connectivity function (all-to-all)
    'weight': 0.1,              # synaptic weight
    'delay': 5,                 # transmission delay (ms)
    'sec': 'soma'}              # section to connect to


# Simulation options
simConfig = specs.SimConfig()       # object of class SimConfig to store simulation configuration
simConfig.duration = 1*1e3          # Duration of the simulation, in ms
simConfig.dt = 0.025                # Internal integration timestep to use
simConfig.verbose = False           # Show detailed messages
simConfig.recordTraces = {'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}}
simConfig.recordStep = 1            # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'model_output' # Set file output name
simConfig.savePickle = False        # Save params, network and sim output to pickle file
simConfig.analysis['plotRaster'] = {'orderInverse': True, 'saveFig': 'tut_import_raster.png'}           
simConfig.analysis['plotTraces'] = {'include': ['HH3D_pop_hoc', 'HH3D_pop_swc']}            


# Create network and run simulation
sim.createSimulateAnalyze(netParams = netParams, simConfig = simConfig)

# import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty

# check model output
sim.checkOutput('tut_import')
