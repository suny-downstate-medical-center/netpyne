"""
params.py 

netParams is a dict containing a set of network parameters using a standardized structure

simConfig is a dict containing a set of simulation configurations using a standardized structure

Contributors: salvadordura@gmail.com
"""


netParams = {}  # dictionary to store sets of network parameters
simConfig = {}  # dictionary to store sets of simulation configurations

###############################################################################
#
# M1 6-LAYER YNORM-BASED MODEL
#
###############################################################################

###############################################################################
# NETWORK PARAMETERS
###############################################################################


# General network parameters
netParams['scale'] = 1 # Scale factor for number of cells
netParams['sizeX'] = 1000 # x-dimension (horizontal length) size in um
netParams['sizeY'] = 1500 # y-dimension (vertical height or cortical depth) size in um
netParams['sizeZ'] = 1000 # z-dimension (horizontal depth) size in um


## General connectivity parameters
netParams['scaleConnWeight'] = 0.025 # Connection weight scale factor
netParams['defaultDelay'] = 2.0 # default conn delay (ms)
netParams['propVelocity'] = 100.0 # propagation velocity (um/ms)
netParams['connfalloff'] = 200 # connection fall off constant (um)
netParams['scaleConnWeight'] = 1 # Connection weight scale factor


# Population parameters
netParams['popParams'] = []  # create list of populations - each item will contain dict with pop params
     
netParams['popParams'].append({'popLabel': 'IT_L23', 'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'ynormRange': [0.1, 0.26], 'density': '1e3*ynorm'}) #  L2/3 IT
netParams['popParams'].append({'popLabel': 'IT_L4',  'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'ynormRange': [0.26, 0.31], 'density': '1e3*ynorm'}) #  L4 IT
netParams['popParams'].append({'popLabel': 'IT_L5A', 'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'ynormRange': [0.31, 0.52], 'density': '1e3*ynorm'}) #  L5A IT
netParams['popParams'].append({'popLabel': 'IT_L5B', 'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'ynormRange': [0.52, 0.77], 'density': '0.5e3*ynorm'}) #  L5B IT
netParams['popParams'].append({'popLabel': 'PT_L5B', 'cellModel': 'Izhi2007b', 'cellType': 'PT',  'projTarget': '', 'ynormRange': [0.52, 0.77], 'density': '0.5e3*ynorm'}) #  L5B PT
netParams['popParams'].append({'popLabel': 'IT_L6',  'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'ynormRange': [0.77, 1.0], 'density': '0.5e3*ynorm'}) #  L6 IT
netParams['popParams'].append({'popLabel': 'CT_L6',  'cellModel': 'Izhi2007b', 'cellType': 'CT',  'projTarget': '', 'ynormRange': [0.77, 1.0], 'density': '0.5e3*ynorm'}) #  L6 CT
netParams['popParams'].append({'popLabel': 'PV_L23', 'cellModel': 'Izhi2007b', 'cellType': 'PV',  'projTarget': '', 'ynormRange': [0.1, 0.31], 'density': '0.5e3*ynorm'}) #  L2/3 PV (FS)
netParams['popParams'].append({'popLabel': 'SOM_L23','cellModel': 'Izhi2007b', 'cellType': 'SOM', 'projTarget': '', 'ynormRange': [0.1, 0.31], 'density': '0.2e3*ynorm'}) #  L2/3 SOM (LTS)
netParams['popParams'].append({'popLabel': 'PV_L5',  'cellModel': 'Izhi2007b', 'cellType': 'PV',  'projTarget': '', 'ynormRange': [0.31, 0.77], 'density': 200}) #  L5 PV (FS)
netParams['popParams'].append({'popLabel': 'SOM_L5', 'cellModel': 'Izhi2007b', 'cellType': 'SOM', 'projTarget': '', 'ynormRange': [0.31, 0.77], 'density': 200}) #  L5 SOM (LTS)
netParams['popParams'].append({'popLabel': 'PV_L6',  'cellModel': 'Izhi2007b', 'cellType': 'PV',  'projTarget': '', 'ynormRange': [0.77, 1.0], 'density': 200}) #  L6 PV (FS)
netParams['popParams'].append({'popLabel': 'SOM_L6', 'cellModel': 'Izhi2007b', 'cellType': 'SOM', 'projTarget': '', 'ynormRange': [0.77, 1.0], 'density': 200}) #  L6 SOM (LTS)
netParams['popParams'].append({'popLabel': 'background', 'cellModel': 'NetStim', 'rate': 100, 'noise': 0.5, 'source': 'random'})  # background inputs

cellsList = [] 
cellsList.append({'cellLabel':'gs15', 'x': 1, 'ynorm': 0.4 , 'z': 2})
cellsList.append({'cellLabel':'gs21', 'x': 2, 'ynorm': 0.5 , 'z': 3})
netParams['popParams'].append({'popLabel': 'IT_cells', 'cellModel':'Izhi2007b', 'cellType':'IT', 'projTarget':'', 'cellsList': cellsList}) #  IT individual cells

cellsList = []
cellsList.append({'cellLabel':'bs50', 'cellType':'PT', 'projTarget':'',       'x': 1, 'ynorm': 0.4 , 'z': 2})
cellsList.append({'cellLabel':'bs91', 'cellType':'PT', 'projTarget':'lumbar', 'x': 2, 'ynorm': 0.5 , 'z': 3})
netParams['popParams'].append({'popLabel': 'PT_cells', 'cellModel':'HH', 'cellsList': cellsList}) #  PT individual cells

# Cell parameters

## Izhi cell params (used in cell properties)
izhiParams = {}
izhiParams['RS'] = {'_type':'Izhi2007b', 'C':100, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}
izhiParams['IB'] = {'_type':'Izhi2007b', 'C':150, 'k':1.2, 'vr':-75, 'vt':-45, 'vpeak':50, 'a':0.01, 'b':5, 'c':-56, 'd':130, 'celltype':2}
izhiParams['LTS'] = {'_type':'Izhi2007b', 'C':100, 'k':1.0, 'vr':-56, 'vt':-42, 'vpeak':40, 'a':0.03, 'b':8, 'c':-53, 'd':20, 'celltype':4}
izhiParams['FS'] = {'_type':'Izhi2007b', 'C':20, 'k':1.0, 'vr':-55, 'vt':-40, 'vpeak':25, 'a':0.2, 'b':-2, 'c':-45, 'd':-55, 'celltype':5}

netParams['cellParams'] = []

## IT cell params
cellRule = {'label': 'IT', 'conditions': {'cellType': 'IT'}, 'sections': {}}
soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'pointps':{}, 'synMechs': {}}  #  soma
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
soma['mechs']['hh'] = {'gnabar': 1, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} # HH
soma['pointps']['Izhi'] = izhiParams['RS'] 
cellRule['sections'] = {'soma': soma}  # add sections to dict
netParams['cellParams'].append(cellRule)  # add dict to list of cell properties

## PT cell params
cellRule = {'label': 'PT', 'conditions': {'cellType': 'PT'}, 'sections': {}}
soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'pointps':{}}  #  soma
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
soma['mechs']['hh'] = {'gnabar': 1, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} # HH 
soma['pointps']['Izhi'] = izhiParams['IB'] 
cellRule['sections'] = {'soma': soma}  # add sections to dict
netParams['cellParams'].append(cellRule)  # add dict to list of cell properties

## CT cell params
cellRule = {'label': 'CT', 'conditions': {'cellType': 'CT'}, 'sections': {}}
soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'pointps':{}}  #  soma
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
soma['mechs']['hh'] = {'gnabar': 1, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} # HH 
soma['pointps']['Izhi'] = izhiParams['RS'] 
cellRule['sections'] = {'soma': soma}  # add sections to dict
netParams['cellParams'].append(cellRule)  # add dict to list of cell properties

## SOM cell params
cellRule = {'label': 'SOM', 'conditions': {'cellType': 'SOM'}, 'sections': {}}
soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'pointps':{}}  #  soma
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
soma['mechs']['hh'] = {'gnabar': 1, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} # HH 
soma['pointps']['Izhi'] = izhiParams['LTS'] 
cellRule['sections'] = {'soma': soma}  # add sections to dict
netParams['cellParams'].append(cellRule)  # add dict to list of cell properties 

## PV cell params
cellRule = {'label': 'PV', 'conditions': {'cellType': 'PV'}, 'sections': {}}
soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'pointps':{}}  #  soma
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
soma['mechs']['hh'] = {'gnabar': 1, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} # HH 
soma['pointps']['Izhi'] = izhiParams['FS'] 
cellRule['sections'] = {'soma': soma}  # add sections to dict
netParams['cellParams'].append(cellRule)  # add dict to list of cell properties


# Synaptic mechanism parameters
netParams['synMechParams'] = []
netParams['synMechParams'].append({'label':'AMPA', 'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0})  # AMPA
netParams['synMechParams'].append({'label':'NMDA', 'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 1.50, 'e': 0})  # NMDA
netParams['synMechParams'].append({'label':'GABAA', 'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80})  # GABAA
netParams['synMechParams'].append({'label':'GABAB', 'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80})  # GABAB


# List of connectivity rules/params
netParams['connParams'] = []  

netParams['connParams'].append({'preTags': {'popLabel': 'background'}, 'postTags': {'cellType': ['IT', 'PT', 'CT', 'PV', 'SOM']}, # background -> All
    'connFunc': 'fullConn',
    'weight': 10, 
    'synMech': 'NMDA',
    'delay': 5})  

netParams['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'IT'}, # IT->IT rule
    'divergence': '10*pre_y+0.01/pre_y',
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5,
    'synMech': 'AMPA',
    'annot': 'ITtoITconn'})  

netParams['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'PT'}, # IT->PT rule    
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'CT'}, # IT->CT rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'PV'}, # IT->PV rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'GABAA'})  

netParams['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'SOM'}, # IT->SOM rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'IT'}, # PT->IT rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'PT'}, # PT->PT rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'CT'}, # PT->CT rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'PV'}, # PT->PV rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'SOM'}, # PT->SOM rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'IT'}, # CT->IT rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'PT'}, # CT->PT rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'CT'}, # CT->CT rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'PV'}, # CT->PV rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'SOM'}, # CT->SOM rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PV'}, 'postTags': {'cellType': 'IT'}, # PV->IT rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'GABAA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PV'}, 'postTags': {'cellType': 'PT'}, # PV->PT rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'GABAA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PV'}, 'postTags': {'cellType': 'CT'}, # PV->CT rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'GABAA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PV'}, 'postTags': {'cellType': 'PV'}, # PV->PV rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PV'}, 'postTags': {'cellType': 'SOM'}, # PV->SOM rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'GABAA'})  

netParams['connParams'].append({'preTags': {'cellType': 'SOM'}, 'postTags': {'cellType': 'IT'}, # SOM->IT rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'GABAA'})  

netParams['connParams'].append({'preTags': {'cellType': 'SOM'}, 'postTags': {'cellType': 'PT'}, # SOM->PT rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'GABAA'})               

netParams['connParams'].append({'preTags': {'cellType': 'SOM'}, 'postTags': {'cellType': 'CT'}, # SOM->CT rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'GABAA'})  

netParams['connParams'].append({'preTags': {'cellType': 'SOM'}, 'postTags': {'cellType': 'PV'}, # SOM->PV rule 
    'probability': '0.1*pre_y+0.01/post_y', 
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'GABAA'})  

netParams['connParams'].append({'preTags': {'cellType': 'SOM'}, 'postTags': {'cellType': 'SOM'}, # SOM->SOM rule 
    'probability': '0.1*pre_y+0.01/post_y',
    'weight': '1*exp(-dist_2D/connfalloff)', 
    'delay': 5, 
    'synMech': 'GABAA'})  



# Dictionary of annotations
netParams['annots'] = {}
netParams['annots']['ITtoITconn'] = 'L2: weak by wiring matrix in (Weiler et al., 2008); L5 strong by wiring matrix in (Weiler et al., 2008)'


###############################################################################
# SIMULATION CONFIGURATION
###############################################################################

simConfig = {}  # dictionary to store simConfig

# Simulation parameters
simConfig['duration'] = 1*1e3 # Duration of the simulation, in ms
simConfig['dt'] = 0.5 # Internal integration timestep to use
simConfig['randseed'] = 1 # Random seed to use
simConfig['createNEURONObj'] = 1  # create HOC objects when instantiating network
simConfig['createPyStruct'] = 1  # create Python structure (simulator-independent) when instantiating network
simConfig['verbose'] = 0 # Whether to write nothing (0) or diagnostic information on events (1)


# Recording 
simConfig['recordCells'] = []  # list of cells to record from
simConfig['recordTraces'] = {'V':{'sec':'soma','pos':0.5,'var':'v'}, 'u':{'sec':'soma', 'pointProcess':'hPoint', 'var':'u'}, 'I':{'sec':'soma', 'pointProcess':'hPoint', 'var':'i'}}
simConfig['recordStim'] = True  # record spikes of cell stims
simConfig['recordStep'] = 10 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
simConfig['filename'] = 'M1ynorm'  # Set file output name
simConfig['saveFileStep'] = 1000 # step size in ms to save data to disk
simConfig['savePickle'] = False # Whether or not to write spikes etc. to a .mat file
simConfig['saveJson'] = False # Whether or not to write spikes etc. to a .mat file
simConfig['saveMat'] = False # Whether or not to write spikes etc. to a .mat file
simConfig['saveTxt'] = False # save spikes and conn to txt file
simConfig['saveDpk'] = False # save to a .dpk pickled file


# Analysis and plotting 
simConfig['plotRaster'] = True # Whether or not to plot a raster
simConfig['plotCells'] = [1] # plot recorded traces for this list of cells 
simConfig['plotLFPSpectrum'] = False # plot power spectral density
simConfig['maxspikestoplot'] = 3e8 # Maximum number of spikes to plot
simConfig['plotConn'] = False # whether to plot conn matrix
simConfig['plotWeightChanges'] = False # whether to plot weight changes (shown in conn matrix)
simConfig['plot3dArch'] = False # plot 3d architecture


