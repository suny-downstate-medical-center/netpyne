"""
netparams.py

netParams is a dict containing a set of network parameters using a standardized structure

simConfig is a dict containing a set of simulation configurations using a standardized structure
"""

from netpyne import specs

netParams = specs.NetParams()   # object of class NetParams to store the network parameters
simConfig = specs.SimConfig()   # object of class SimConfig to store the simulation configuration

###############################################################################
#
# MPI HH TUTORIAL PARAMS
#
###############################################################################

###############################################################################
# NETWORK PARAMETERS
###############################################################################

netParams.scaleConnWeight = 0.001 # Connection weight scale factor

# Population parameters
netParams.popParams['Psh'] = {'cellModel': 'Izhi', 'cellType': 'RS', 'numCells': 40} # add dict with params for this pop
netParams.popParams['Pel'] = {'cellModel': 'Izhi', 'cellType': 'RS', 'numCells': 40} # add dict with params for this pop
netParams.popParams['ES'] = {'cellModel': 'Izhi', 'cellType': 'RS', 'numCells': 80} # add dict with params for this pop
netParams.popParams['ISL'] = {'cellModel': 'Izhi', 'cellType': 'LTS', 'numCells': 10} # add dict with params for this pop
netParams.popParams['IS'] = {'cellModel': 'Izhi', 'cellType': 'FS', 'numCells': 10} # add dict with params for this pop
netParams.popParams['EM'] = {'cellModel': 'Izhi', 'cellType': 'RS', 'numCells': 80} # add dict with params for this pop
netParams.popParams['IML'] = {'cellModel': 'Izhi', 'cellType': 'LTS', 'numCells': 10} # add dict with params for this pop
netParams.popParams['IM'] = {'cellModel': 'Izhi', 'cellType': 'FS', 'numCells': 10} # add dict with params for this pop


# Izhi cell params (used in cell properties)
izhiParams = {}
izhiParams['RS'] = {'mod':'Izhi2007b', 'C':1, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}
izhiParams['LTS'] = {'mod':'Izhi2007b', 'C':1, 'k':1.0, 'vr':-56, 'vt':-42, 'vpeak':40, 'a':0.03, 'b':8, 'c':-53, 'd':20, 'celltype':4}
izhiParams['FS'] = {'mod':'Izhi2007b', 'C':0.2, 'k':1.0, 'vr':-55, 'vt':-40, 'vpeak':25, 'a':0.2, 'b':-2, 'c':-45, 'd':-55, 'celltype':5}

# Cell properties list

## RS Izhi cell params
cellRule = {'conds': {'cellType': 'RS', 'cellModel': 'Izhi'}, 'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'pointps':{}}  #  soma
cellRule['secs']['soma']['geom'] = {'diam': 10, 'L': 10, 'cm': 31.831}
cellRule['secs']['soma']['pointps']['Izhi'] = izhiParams['RS']
netParams.cellParams['RS_Izhi'] = cellRule  # add dict to list of cell properties

## LTS Izhi cell params
cellRule = {'conds': {'cellType': 'LTS', 'cellModel': 'Izhi'}, 'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'pointps':{}}  #  soma
cellRule['secs']['soma']['geom'] = {'diam': 10, 'L': 10, 'cm': 31.831}
cellRule['secs']['soma']['pointps']['Izhi'] = izhiParams['LTS']
netParams.cellParams['LTS_Izhi'] = cellRule  # add dict to list of cell properties

## FS Izhi cell params
cellRule = {'conds': {'cellType': 'FS', 'cellModel': 'Izhi'}, 'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'pointps':{}}  #  soma
cellRule['secs']['soma']['geom'] = {'diam': 10, 'L': 10, 'cm': 31.831}
cellRule['secs']['soma']['pointps']['Izhi'] = izhiParams['FS']
netParams.cellParams['FS_Izhi'] = cellRule  # add dict to list of cell properties


# Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0} # AMPA
netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 1.50, 'e': 0} # NMDA
netParams.synMechParams['GABA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80} # GABAA



# Stimulation parameters
netParams.stimSourceParams['backgroundE'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.5}  # background inputs
netParams.stimSourceParams['backgroundI'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.5}  # background inputs
netParams.stimSourceParams['stimPsh'] = {'type': 'NetStim', 'rate': 'variable', 'noise': 0} # stim inputs for P_sh
netParams.stimSourceParams['stimPel'] = {'type': 'NetStim', 'rate': 'variable', 'noise': 0} # stim inputs for P_el
netParams.stimSourceParams['stimEM'] = {'type': 'NetStim', 'rate': 'variable', 'noise': 0} # stim inputs for EM (explor movs)



# Connectivity parameters
# STDPparams = {'hebbwt': 0.00001, 'antiwt':-0.000013, 'wmax': 50, 'RLon': 1 , 'RLhebbwt': 0.001, 'RLantiwt': -0.001, \
#     'tauhebb': 10, 'RLwindhebb': 50, 'useRLexp': 1, 'softthresh': 0, 'verbose':0}

STDPparams = {'hebbwt': 0.00001, 'antiwt':-0.00001, 'wmax': 50, 'RLon': 1 , 'RLhebbwt': 0.001, 'RLantiwt': -0.000, \
    'tauhebb': 10, 'RLwindhebb': 50, 'useRLexp': 0, 'softthresh': 0, 'verbose':0}

# Background and stims

netParams.stimTargetParams['bg->E'] = {'source': 'backgroundE',
    'conds': {'pop': ['ES', 'EM']}, # background -> Exc
    'weight': 0.05,
    'delay': 'uniform(1,5)',
    'synMech': 'NMDA'}

netParams.stimTargetParams['bg->I'] = {'source': 'backgroundI',
    'conds': {'pop': ['ISL', 'IML', 'IS', 'IM']}, # background -> Inh
    'weight': 0.05,
    'delay': 'uniform(1,5)',
    'synMech': 'NMDA'}

netParams.stimTargetParams['Pstim_sh->Psh'] = {'source': 'stimPsh',
    'conds': {'pop': 'Psh'},  # Pstim_sh -> P_sh
    'weight': 0.1,
    'delay': 1,
    'synMech': 'NMDA'}

netParams.stimTargetParams['Pstim_el->Pel'] = {'source': 'stimPel',
    'conds': {'pop': 'Pel'},  # Pstim_el -> P_el
    'weight': 0.1,
    'delay': 1,
    'synMech': 'NMDA'}

netParams.stimTargetParams['EMstim->EM'] = {'source': 'stimEM',
    'conds': {'pop': 'EM'}, # EMstim-> EM
    'weight': 0.4,
    'delay': 'uniform(1,5)',
    'synMech': 'NMDA'}


# Sensory

netParams.addConnParams(None,
    {'preConds': {'pop': ['Psh', 'Pel']}, 'postConds': {'pop': 'ES'},  # P_sh,P_el -> ES
    'weight': 4,
    'probability': 0.1125,
    'delay': 5,
    'synMech': 'AMPA',
    'plast': {'mech': 'STDP', 'params': STDPparams}})

netParams.addConnParams(None,
    {'preConds': {'pop': 'ES'}, 'postConds': {'pop': 'ES'},  # ES -> ES
    'weight': 1.98,
    'probability': 0.05625,
    'delay': 5,
    'synMech': 'AMPA'})


netParams.addConnParams(None,
    {'preConds': {'pop': 'ES'}, 'postConds': {'pop': 'IS'},  # ES -> IS
    'weight': 0.48375,
    'probability': 1.150,
    'delay': 5,
    'synMech': 'AMPA'})

netParams.addConnParams(None,
    {'preConds': {'pop': 'ES'}, 'postConds': {'pop': 'ISL'},  # ES -> ISL
    'weight': 0.57375,
    'probability': 0.575,
    'delay': 5,
    'synMech': 'AMPA'})

netParams.addConnParams(None,
    {'preConds': {'pop': 'ES'}, 'postConds': {'pop': 'EM'},  # ES -> EM (plastic)
    'weight': 2.640,
    'probability': 0.33750,
    'delay': 5,
    'synMech': 'AMPA',
    'plast': {'mech': 'STDP', 'params': STDPparams}})


netParams.addConnParams(None,
    {'preConds': {'pop': 'IS'}, 'postConds': {'pop': 'ES'},  # IS -> ES
    'weight': 4.5,
    'probability': 0.495,
    'delay': 5,
    'synMech': 'GABA'})


netParams.addConnParams(None,
    {'preConds': {'pop': 'IS'}, 'postConds': {'pop': 'IS'},  # IS -> IS
    'weight': 4.5,
    'probability': 0.69750,
    'delay': 5,
    'synMech': 'GABA'})

netParams.addConnParams(None,
    {'preConds': {'pop': 'IS'}, 'postConds': {'pop': 'ISL'},  # IS -> ISL
    'weight': 4.5,
    'probability': 0.38250,
    'delay': 5,
    'synMech': 'GABA'})

netParams.addConnParams(None,
    {'preConds': {'pop': 'ISL'}, 'postConds': {'pop': 'IS'},  # ISL -> ES
    'weight': 2.25,
    'probability': 0.39375,
    'delay': 5,
    'synMech': 'GABA'})

netParams.addConnParams(None,
    {'preConds': {'pop': 'ISL'}, 'postConds': {'pop': 'IS'},  # ISL -> IS
    'weight': 2.25,
    'probability': 0.59625,
    'delay': 5,
    'synMech': 'GABA'})

netParams.addConnParams(None,
    {'preConds': {'pop': 'ISL'}, 'postConds': {'pop': 'ISL'},  # ISL -> ISL
    'weight': 4.5,
    'probability': 0.10125,
    'delay': 5,
    'synMech': 'GABA'})


netParams.addConnParams(None,
    {'preConds': {'pop': 'EM'}, 'postConds': {'pop': 'ES'},  # EM -> ES
    'weight': 0.72,
    'probability': 0.01125,
    'delay': 5,
    'synMech': 'AMPA'})#,
#    'plast': {'mech': 'STDP', 'params': STDPparams}})


# Motor

netParams.addConnParams(None,
    {'preConds': {'pop': 'EM'}, 'postConds': {'pop': 'EM'},  # EM -> EM
    'weight': 1.782,
    'probability': 0.05625,
    'delay': 5,
    'synMech': 'AMPA'})

netParams.addConnParams(None,
    {'preConds': {'pop': 'EM'}, 'postConds': {'pop': 'IM'},  # EM -> IM
    'weight': 1.15,
    'probability': 0.48375,
    'delay': 5,
    'synMech': 'AMPA'})

netParams.addConnParams(None,
    {'preConds': {'pop': 'EM'}, 'postConds': {'pop': 'IML'},  # EM -> IML
    'weight': 0.575,
    'probability': 0.57375,
    'delay': 5,
    'synMech': 'AMPA'})

netParams.addConnParams(None,
    {'preConds': {'pop': 'IM'}, 'postConds': {'pop': 'EM'},  # IM -> EM
    'weight': 9,
    'probability': 0.495,
    'delay': 5,
    'synMech': 'GABA'})

netParams.addConnParams(None,
    {'preConds': {'pop': 'IM'}, 'postConds': {'pop': 'IM'},  # IM -> IM
    'weight': 4.5,
    'probability': 0.69750,
    'delay': 5,
    'synMech': 'GABA'})

netParams.addConnParams(None,
    {'preConds': {'pop': 'IM'}, 'postConds': {'pop': 'IML'},  # IM -> IML
    'weight': 4.5,
    'probability': 0.38250,
    'delay': 5,
    'synMech': 'GABA'})

netParams.addConnParams(None,
    {'preConds': {'pop': 'IML'}, 'postConds': {'pop': 'EM'},  # IML -> EM
    'weight': 2.49,
    'probability': 0.39375,
    'delay': 5,
    'synMech': 'GABA'})

netParams.addConnParams(None,
    {'preConds': {'pop': 'IML'}, 'postConds': {'pop': 'IM'},  # IML -> IM
    'weight': 2.25,
    'probability': 0.59625,
    'delay': 5,
    'synMech': 'GABA'})

netParams.addConnParams(None,
    {'preConds': {'pop': 'IML'}, 'postConds': {'pop': 'IML'},  # IML -> IML
    'weight': 4.5,
    'probability': 0.10125,
    'delay': 5,
    'synMech': 'GABA'})


###############################################################################
# SIMULATION PARAMETERS
###############################################################################

# Simulation parameters
simConfig.duration = 1*1e3 # Duration of the simulation, in ms
simConfig.dt = 0.1 # Internal integration timestep to use
simConfig.seeds = {'conn': 1, 'stim': 1, 'loc': 1} # Seeds for randomizers (connectivity, input stimulation and cell locations)
simConfig.createNEURONObj = True  # create HOC objects when instantiating network
simConfig.createPyStruct = True  # create Python structure (simulator-independent) when instantiating network
simConfig.timing = True  # show timing  and save to file
simConfig.verbose = True # show detailed messages

# Recording
simConfig.recordCells = ['all']  # list of cells to record from
simConfig.recordTraces = {}
# {'V':{'sec':'soma','loc':0.5,'var':'v'},
#     'u':{'sec':'soma', 'pointp':'Izhi', 'var':'u'},
#     'I':{'sec':'soma', 'pointp':'Izhi', 'var':'i'},
#     'NMDA_g': {'sec':'soma', 'loc':0.5, 'synMech':'NMDA', 'var':'g'},
#     'NMDA_i': {'sec':'soma', 'loc':0.5, 'synMech':'NMDA', 'var':'i'},
#     'GABA_g': {'sec':'soma', 'loc':0.5, 'synMech':'GABA', 'var':'g'},
#     'GABA_i': {'sec':'soma', 'loc':0.5, 'synMech':'GABA', 'var':'i'}}
simConfig.recordStim = True  # record spikes of cell stims
simConfig.recordStep = 1.0 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
simConfig.filename = 'simdata'  # Set file output name
simConfig.saveFileStep = 1000 # step size in ms to save data to disk
simConfig.savePickle = False # Whether or not to write spikes etc. to a .mat file
simConfig.saveJson = False # Whether or not to write spikes etc. to a .mat file
simConfig.saveMat = True # Whether or not to write spikes etc. to a .mat file
simConfig.saveTxt = False # save spikes and conn to txt file
simConfig.saveDpk = False # save to a .dpk pickled file


# Analysis and plotting
simConfig.analysis['plotRaster'] = True # Whether or not to plot a raster
