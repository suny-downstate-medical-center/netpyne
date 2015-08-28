"""
params.py 

netParams is a dict containing different sets of network parameters
eg. netParams['mpiHHTut'] or netParams['M1yfrac']

simConfig is a dict containing different sets of simulation configurations
eg. simConfig['default'] or simConfig['M1']

Contributors: salvadordura@gmail.com
"""

from pylab import array


netParams = {}  # dictionary to store sets of network parameters
simConfig = {}  # dictionary to store sets of simulation configurations

###############################################################################
#
# M1 6-LAYER YFRAC-BASED MODEL
#
###############################################################################

###############################################################################
# NETWORK PARAMETERS
###############################################################################

netParams['M1yfrac'] = {}  # dictionary to store netParams
p = netParams['M1yfrac']  # pointer to dict

## Position parameters
netParams['scale'] = 1 # Size of simulation in thousands of cells
netParams['cortthaldist'] = 1500 # Distance from relay nucleus to cortex -- ~1 cm = 10,000 um (check)
netParams['corticalthick'] = 1740 # cortical thickness/depth

## Background input parameters
netParams['useBackground'] = True # Whether or not to use background stimuli
netParams['backgroundRate'] = 5 # Rate of stimuli (in Hz)
netParams['backgroundRateMin'] = 0.1 # Rate of stimuli (in Hz)
netParams['backgroundNumber'] = 1e10 # Number of spikes
netParams['backgroundNoise'] = 1 # Fractional noise
netParams['backgroundWeight'] = 0.1*array([1,0.1]) # Weight for background input for E cells and I cells
netParams['backgroundReceptor'] = 'NMDA' # Which receptor to stimulate

# Cell properties list
netParams['cellProperties'] = []

# IT cell params
cellProp = {'label': 'IT', 'conditions': {'cellType': 'IT'}, 'Izhi2007Type': 'RS', 'sections': {}}

soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'syns': {}}  #  soma
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
soma['mechs']['hh'] = {'gnbar': 1, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} # HH 
soma['syns']['AMPA'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 0.05, 'tau2':5.3, 'e': 0}  # AMPA
soma['syns']['NMDA'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 15, 'tau2': 150, 'r': 1, 'e': 0}  # NMDA
soma['syns']['GABAA'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
soma['syns']['GABAB'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB

cellProp['sections'] = {'soma': soma}  # add sections to dict
netParams['cellProperties'].append(cellProp)  # add dict to list of cell properties

# PT cell params
cellProp = {'label': 'PT', 'conditions': {'cellType': 'PT'}, 'Izhi2007Type': 'RS', 'sections': {}}

soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'syns': {}}  #  soma
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
soma['mechs']['hh'] = {'gnbar': 1, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} # HH 
soma['syns']['AMPA'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 0.05, 'tau2':5.3, 'e': 0}  # AMPA
soma['syns']['NMDA'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 15, 'tau2': 150, 'r': 1, 'e': 0}  # NMDA
soma['syns']['GABAA'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
soma['syns']['GABAB'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB

cellProp['sections'] = {'soma': soma}  # add sections to dict
netParams['cellProperties'].append(cellProp)  # add dict to list of cell properties

# CT cell params
cellProp = {'label': 'CT', 'conditions': {'cellType': 'CT'}, 'Izhi2007Type': 'RS', 'sections': {}}

soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'syns': {}}  #  soma
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
soma['mechs']['hh'] = {'gnbar': 1, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} # HH 
soma['syns']['AMPA'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 0.05, 'tau2':5.3, 'e': 0}  # AMPA
soma['syns']['NMDA'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 15, 'tau2': 150, 'r': 1, 'e': 0}  # NMDA
soma['syns']['GABAA'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
soma['syns']['GABAB'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB

cellProp['sections'] = {'soma': soma}  # add sections to dict
netParams['cellProperties'].append(cellProp)  # add dict to list of cell properties

# SOM cell params
cellProp = {'label': 'SOM', 'conditions': {'cellType': 'SOM'}, 'Izhi2007Type': 'FS', 'sections': {}}

soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'syns': {}}  #  soma
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
soma['mechs']['hh'] = {'gnbar': 1, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} # HH 
soma['syns']['AMPA'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 0.05, 'tau2':5.3, 'e': 0}  # AMPA
soma['syns']['NMDA'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 15, 'tau2': 150, 'r': 1, 'e': 0}  # NMDA
soma['syns']['GABAA'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
soma['syns']['GABAB'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB

cellProp['sections'] = {'soma': soma}  # add sections to dict
netParams['cellProperties'].append(cellProp)  # add dict to list of cell properties 

# PV cell params
cellProp = {'label': 'PV', 'conditions': {'cellType': 'PV'}, 'Izhi2007Type': 'LTS', 'sections': {}}
soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'syns': {}}  #  soma
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
soma['mechs']['hh'] = {'gnbar': 1, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} # HH 
soma['syns']['AMPA'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 0.05, 'tau2':5.3, 'e': 0}  # AMPA
soma['syns']['NMDA'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 15, 'tau2': 150, 'r': 1, 'e': 0}  # NMDA
soma['syns']['GABAA'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
soma['syns']['GABAB'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB

cellProp['sections'] = {'soma': soma}  # add sections to dict
netParams['cellProperties'].append(cellProp)  # add dict to list of cell properties

# create list of populations, where each item contains a dict with the pop params
netParams['popParams'] = []  
     
netParams['popParams'].append({'label': 'IT_L23', 'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.1, 0.26], 'density': lambda y:2e3*y}) #  L2/3 IT
netParams['popParams'].append({'label': 'IT_L4',  'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.26, 0.31], 'density': lambda y:2e3*y}) #  L4 IT
netParams['popParams'].append({'label': 'IT_L5A', 'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.31, 0.52], 'density': lambda y:2e3*y}) #  L5A IT
netParams['popParams'].append({'label': 'IT_L5B', 'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.52, 0.77], 'density': lambda y:2e3*y}) #  L5B IT
netParams['popParams'].append({'label': 'PT_L5B', 'cellModel': 'Izhi2007b', 'cellType': 'PT',  'projTarget': '', 'yfracRange': [0.52, 0.77], 'density': lambda y:2e3*y}) #  L5B PT
netParams['popParams'].append({'label': 'IT_L6',  'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.77, 1.0], 'density': lambda y:1e3}) #  L6 IT
netParams['popParams'].append({'label': 'CT_L6',  'cellModel': 'Izhi2007b', 'cellType': 'CT',  'projTarget': '', 'yfracRange': [0.77, 1.0], 'density': lambda y:1e3}) #  L6 CT
netParams['popParams'].append({'label': 'PV_L23', 'cellModel': 'Izhi2007b', 'cellType': 'PV',  'projTarget': '', 'yfracRange': [0.1, 0.31], 'density': lambda y:1e3}) #  L2/3 PV (LTS)
netParams['popParams'].append({'label': 'SOM_L23','cellModel': 'Izhi2007b', 'cellType': 'SOM', 'projTarget': '', 'yfracRange': [0.1, 0.31], 'density': lambda y:2e3*y}) #  L2/3 SOM (FS)
netParams['popParams'].append({'label': 'PV_L5',  'cellModel': 'Izhi2007b', 'cellType': 'PV',  'projTarget': '', 'yfracRange': [0.31, 0.77], 'density': lambda y:0.5e3}) #  L5 PV (FS)
netParams['popParams'].append({'label': 'SOM_L5', 'cellModel': 'Izhi2007b', 'cellType': 'SOM', 'projTarget': '', 'yfracRange': [0.31, 0.77], 'density': lambda y:0.5e3}) #  L5 SOM (LTS)
netParams['popParams'].append({'label': 'PV_L6',  'cellModel': 'Izhi2007b', 'cellType': 'PV',  'projTarget': '', 'yfracRange': [0.77, 1.0], 'density': lambda y:0.5e3}) #  L6 PV (FS)
netParams['popParams'].append({'label': 'SOM_L6', 'cellModel': 'Izhi2007b', 'cellType': 'SOM', 'projTarget': '', 'yfracRange': [0.77, 1.0], 'density': lambda y:0.5e3}) #  L6 SOM (LTS)

cellsList = []
cellsList.append({'label':'gs15', 'x': 1, 'yfrac': 0.4 , 'z': 2})
cellsList.append({'label':'gs21', 'x': 2, 'yfrac': 0.5 , 'z': 3})
netParams['popParams'].append({'label': 'IT_cells', 'cellModel':'Izhi2007b', 'cellType':'IT', 'projTarget':'', 'cellsList': cellsList}) #  IT individual cells

cellsList = []
cellsList.append({'label':'bs50', 'cellModel': 'Izhi2007b',  'cellType':'PT', 'projTarget':'',       'x': 1, 'yfrac': 0.4 , 'z': 2})
cellsList.append({'label':'bs91', 'cellModel': 'HH',         'cellType':'PT', 'projTarget':'lumbar', 'x': 2, 'yfrac': 0.5 , 'z': 3})
netParams['popParams'].append({'label': 'PT_cells', 'cellsList': cellsList}) #  PT individual cells

## General connectivity parameters
netParams['connType'] = 'yfrac'
#netParams['numReceptors'] = 1 
netParams['useconnprobdata'] = True # Whether or not to use connectivity data
netParams['useconnweightdata'] = True # Whether or not to use weight data
netParams['mindelay'] = 2 # Minimum connection delay, in ms
netParams['velocity'] = 100 # Conduction velocity in um/ms (e.g. 50 = 0.05 m/s)
netParams['modelsize'] = 1000*netParams['scale'] # Size of netParamswork in um (~= 1000 neurons/column where column = 500um width)
netParams['sparseness'] = 0.1 # fraction of cells represented (num neurons = density * modelsize * sparseness)
netParams['scaleconnweight'] = 0.00025*array([[2, 1], [2, 0.1]]) # Connection weights for EE, EI, IE, II synapses, respectively
netParams['receptorweight'] = [1, 1, 1, 1, 1] # Scale factors for each receptor
netParams['scaleconnprob'] = 1/netParams['scale']*array([[1, 1], [1, 1]]) # scale*1* Connection probabilities for EE, EI, IE, II synapses, respectively -- scale for scale since size fixed
netParams['connfalloff'] = 100*array([2, 3]) # Connection length constants in um for E and I synapses, respectively
netParams['toroidal'] = False # Whether or not to have toroidal topology

## List of connectivity rules/params
netParams['connParams'] = []  

netParams['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'IT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty),
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA', 'annot': 'ITtoITconn'})  # IT->IT rule

netParams['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'IT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # IT->IT rule

netParams['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'PT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # IT->PT rule

netParams['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'CT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # IT->CT rule

netParams['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'Pva'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # IT->Pva rule

netParams['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'Sst'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # IT->Sst rule

netParams['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'IT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # PT->IT rule

netParams['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'PT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # PT->PT rule

netParams['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'CT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prex,posty: 1), 'syn': 'AMPA'})  # PT->CT rule

netParams['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'Pva'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # PT->Pva rule

netParams['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'Sst'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # PT->Sst rule

netParams['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'IT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # CT->IT rule

netParams['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'PT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # CT->PT rule

netParams['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'CT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # CT->CT rule

netParams['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'Pva'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # CT->Pva rule

netParams['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'Sst'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # CT->Sst rule

netParams['connParams'].append({'preTags': {'cellType': 'Pva'}, 'postTags': {'cellType': 'IT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Pva->IT rule

netParams['connParams'].append({'preTags': {'cellType': 'Pva'}, 'postTags': {'cellType': 'PT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Pva->PT rule

netParams['connParams'].append({'preTags': {'cellType': 'Pva'}, 'postTags': {'cellType': 'CT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Pva->CT rule

netParams['connParams'].append({'preTags': {'cellType': 'Pva'}, 'postTags': {'cellType': 'Pva'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Pva->Pva rule

netParams['connParams'].append({'preTags': {'cellType': 'Pva'}, 'postTags': {'cellType': 'Sst'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Pva->Sst rule

netParams['connParams'].append({'preTags': {'cellType': 'Sst'}, 'postTags': {'cellType': 'IT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Sst->IT rule

netParams['connParams'].append({'preTags': {'cellType': 'Sst'}, 'postTags': {'cellType': 'PT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Sst->PT rule             

netParams['connParams'].append({'preTags': {'cellType': 'Sst'}, 'postTags': {'cellType': 'CT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Sst->CT rule

netParams['connParams'].append({'preTags': {'cellType': 'Sst'}, 'postTags': {'cellType': 'Pva'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Sst->Pva rule

netParams['connParams'].append({'preTags': {'cellType': 'Sst'}, 'postTags': {'cellType': 'Sst'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Sst->Sst rule



# Dictionary of annotations
netParams['annots'] = {}
netParams['annots']['ITtoITconn'] = 'L2: weak by wiring matrix in (Weiler et al., 2008); L5 strong by wiring matrix in (Weiler et al., 2008)'

###############################################################################
# SIMULATION PARAMETERS
###############################################################################

simConfig = {}  # dictionary to store simConfig

# Simulation parameters
simConfig['duration'] = simConfig['tstop'] = 1*1e3 # Duration of the simulation, in ms
#h.dt = simConfig['dt'] = 0.5 # Internal integration timestep to use
simConfig['recordStep'] = 10 # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig['saveFileStep'] = 1000 # step size in ms to save data to disk
simConfig['randseed'] = 1 # Random seed to use

## Recording 
simConfig['recdict'] = {'V':'sec(0.5)._ref_v', 'u':'m._ref_u', 'I':'m._ref_i'}
simConfig['simdataVecs'] = ['spkt', 'spkid']


## Saving and plotting parameters
simConfig['filename'] = '../data/m1ms'  # Set file output name
simConfig['savemat'] = True # Whether or not to write spikes etc. to a .mat file
simConfig['savetxt'] = False # save spikes and conn to txt file
simConfig['savedpk'] = True # save to a .dpk pickled file
simConfig['recordTraces'] = True  # whether to record cell traces or not
simConfig['saveBackground'] = False # save background (NetStims) inputs
simConfig['verbose'] = 0 # Whether to write nothing (0), diagnostic information on events (1), or everything (2) a file directly from izhi.mod
simConfig['plotraster'] = True # Whether or not to plot a raster
simConfig['plotpsd'] = False # plot power spectral density
simConfig['maxspikestoplot'] = 3e8 # Maximum number of spikes to plot
simConfig['plotconn'] = False # whether to plot conn matrix
simConfig['plotweightchanges'] = False # whether to plot weight changes (shown in conn matrix)
simConfig['plot3darch'] = False # plot 3d architecture

## Stimulus parameters
simConfig['usestims'] = False # Whether or not to use stimuli at all
simConfig['ltptimes']  = [5, 10] # Pre-microstim touch times
simConfig['ziptimes'] = [10, 15] # Pre-microstim touch times


