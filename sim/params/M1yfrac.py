"""
params.py 

netParam is a dict containing different sets of network parameters
eg. netParam['mpiHHTut'] or netParam['M1yfrac']

simConfig is a dict containing different sets of simulation configurations
eg. simConfig['default'] or simConfig['M1']

Contributors: salvadordura@gmail.com
"""

from pylab import array


netParam = {}  # dictionary to store sets of network parameters
simConfig = {}  # dictionary to store sets of simulation configurations

###############################################################################
#
# M1 6-LAYER YFRAC-BASED MODEL
#
###############################################################################

###############################################################################
# NETWORK PARAMETERS
###############################################################################

netParam['M1yfrac'] = {}  # dictionary to store netParam
p = netParam['M1yfrac']  # pointer to dict

## Position parameters
netParam['scale'] = 1 # Size of simulation in thousands of cells
netParam['cortthaldist'] = 1500 # Distance from relay nucleus to cortex -- ~1 cm = 10,000 um (check)
netParam['corticalthick'] = 1740 # cortical thickness/depth

## Background input parameters
netParam['useBackground'] = True # Whether or not to use background stimuli
netParam['backgroundRate'] = 5 # Rate of stimuli (in Hz)
netParam['backgroundRateMin'] = 0.1 # Rate of stimuli (in Hz)
netParam['backgroundNumber'] = 1e10 # Number of spikes
netParam['backgroundNoise'] = 1 # Fractional noise
netParam['backgroundWeight'] = 0.1*array([1,0.1]) # Weight for background input for E cells and I cells
netParam['backgroundReceptor'] = 'NMDA' # Which receptor to stimulate

# Cell properties list
netParam['cellProps'] = []

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
netParam['cellProps'].append(cellProp)  # add dict to list of cell properties

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
netParam['cellProps'].append(cellProp)  # add dict to list of cell properties

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
netParam['cellProps'].append(cellProp)  # add dict to list of cell properties

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
netParam['cellProps'].append(cellProp)  # add dict to list of cell properties 

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
netParam['cellProps'].append(cellProp)  # add dict to list of cell properties


# create list of populations, where each item contains a dict with the pop params
netParam['popParams'] = []  
     
netParam['popParams'].append({'popLabel': 'IT_L23', 'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.1, 0.26], 'density': lambda y:2e3*y}) #  L2/3 IT
netParam['popParams'].append({'popLabel': 'IT_L4',  'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.26, 0.31], 'density': lambda y:2e3*y}) #  L4 IT
netParam['popParams'].append({'popLabel': 'IT_L5A', 'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.31, 0.52], 'density': lambda y:2e3*y}) #  L5A IT
netParam['popParams'].append({'popLabel': 'IT_L5B', 'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.52, 0.77], 'density': lambda y:2e3*y}) #  L5B IT
netParam['popParams'].append({'popLabel': 'PT_L5B', 'cellModel': 'Izhi2007b', 'cellType': 'PT',  'projTarget': '', 'yfracRange': [0.52, 0.77], 'density': lambda y:2e3*y}) #  L5B PT
netParam['popParams'].append({'popLabel': 'IT_L6',  'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.77, 1.0], 'density': lambda y:1e3}) #  L6 IT
netParam['popParams'].append({'popLabel': 'CT_L6',  'cellModel': 'Izhi2007b', 'cellType': 'CT',  'projTarget': '', 'yfracRange': [0.77, 1.0], 'density': lambda y:1e3}) #  L6 CT
netParam['popParams'].append({'popLabel': 'PV_L23', 'cellModel': 'Izhi2007b', 'cellType': 'PV',  'projTarget': '', 'yfracRange': [0.1, 0.31], 'density': lambda y:1e3}) #  L2/3 PV (LTS)
netParam['popParams'].append({'popLabel': 'SOM_L23','cellModel': 'Izhi2007b', 'cellType': 'SOM', 'projTarget': '', 'yfracRange': [0.1, 0.31], 'density': lambda y:2e3*y}) #  L2/3 SOM (FS)
netParam['popParams'].append({'popLabel': 'PV_L5',  'cellModel': 'Izhi2007b', 'cellType': 'PV',  'projTarget': '', 'yfracRange': [0.31, 0.77], 'density': lambda y:0.5e3}) #  L5 PV (FS)
netParam['popParams'].append({'popLabel': 'SOM_L5', 'cellModel': 'Izhi2007b', 'cellType': 'SOM', 'projTarget': '', 'yfracRange': [0.31, 0.77], 'density': lambda y:0.5e3}) #  L5 SOM (LTS)
netParam['popParams'].append({'popLabel': 'PV_L6',  'cellModel': 'Izhi2007b', 'cellType': 'PV',  'projTarget': '', 'yfracRange': [0.77, 1.0], 'density': lambda y:0.5e3}) #  L6 PV (FS)
netParam['popParams'].append({'popLabel': 'SOM_L6', 'cellModel': 'Izhi2007b', 'cellType': 'SOM', 'projTarget': '', 'yfracRange': [0.77, 1.0], 'density': lambda y:0.5e3}) #  L6 SOM (LTS)

cellsList = []
cellsList.append({'popLabel':'gs15', 'x': 1, 'yfrac': 0.4 , 'z': 2})
cellsList.append({'popLabel':'gs21', 'x': 2, 'yfrac': 0.5 , 'z': 3})
netParam['popParams'].append({'popLabel': 'IT_cells', 'cellModel':'Izhi2007b', 'cellType':'IT', 'projTarget':'', 'cellsList': cellsList}) #  IT individual cells

cellsList = []
cellsList.append({'popLabel':'bs50', 'cellModel': 'Izhi2007b',  'cellType':'PT', 'projTarget':'',       'x': 1, 'yfrac': 0.4 , 'z': 2})
cellsList.append({'popLabel':'bs91', 'cellModel': 'HH',         'cellType':'PT', 'projTarget':'lumbar', 'x': 2, 'yfrac': 0.5 , 'z': 3})
netParam['popParams'].append({'popLabel': 'PT_cells', 'cellsList': cellsList}) #  PT individual cells

netParam['popTagsCopiedToCells'] = ['popLabel', 'cellModel', 'cellType', 'projTarget']


## General connectivity parameters
netParam['connType'] = 'yfrac'
#netParam['numReceptors'] = 1 
netParam['useconnprobdata'] = True # Whether or not to use connectivity data
netParam['useconnweightdata'] = True # Whether or not to use weight data
netParam['mindelay'] = 2 # Minimum connection delay, in ms
netParam['velocity'] = 100 # Conduction velocity in um/ms (e.g. 50 = 0.05 m/s)
netParam['modelsize'] = 1000*netParam['scale'] # Size of netParamwork in um (~= 1000 neurons/column where column = 500um width)
netParam['sparseness'] = 0.1 # fraction of cells represented (num neurons = density * modelsize * sparseness)
netParam['scaleconnweight'] = 0.00025*array([[2, 1], [2, 0.1]]) # Connection weights for EE, EI, IE, II synapses, respectively
netParam['receptorweight'] = [1, 1, 1, 1, 1] # Scale factors for each receptor
netParam['scaleconnprob'] = 1/netParam['scale']*array([[1, 1], [1, 1]]) # scale*1* Connection probabilities for EE, EI, IE, II synapses, respectively -- scale for scale since size fixed
netParam['connfalloff'] = 100*array([2, 3]) # Connection length constants in um for E and I synapses, respectively
netParam['toroidal'] = False # Whether or not to have toroidal topology

## List of connectivity rules/params
netParam['connParams'] = []  

netParam['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'IT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty),
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA', 'annot': 'ITtoITconn'})  # IT->IT rule

netParam['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'IT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # IT->IT rule

netParam['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'PT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # IT->PT rule

netParam['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'CT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # IT->CT rule

netParam['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'Pva'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # IT->Pva rule

netParam['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'Sst'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # IT->Sst rule

netParam['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'IT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # PT->IT rule

netParam['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'PT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # PT->PT rule

netParam['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'CT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prex,posty: 1), 'syn': 'AMPA'})  # PT->CT rule

netParam['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'Pva'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # PT->Pva rule

netParam['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'Sst'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # PT->Sst rule

netParam['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'IT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # CT->IT rule

netParam['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'PT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # CT->PT rule

netParam['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'CT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # CT->CT rule

netParam['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'Pva'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # CT->Pva rule

netParam['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'Sst'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # CT->Sst rule

netParam['connParams'].append({'preTags': {'cellType': 'Pva'}, 'postTags': {'cellType': 'IT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Pva->IT rule

netParam['connParams'].append({'preTags': {'cellType': 'Pva'}, 'postTags': {'cellType': 'PT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Pva->PT rule

netParam['connParams'].append({'preTags': {'cellType': 'Pva'}, 'postTags': {'cellType': 'CT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Pva->CT rule

netParam['connParams'].append({'preTags': {'cellType': 'Pva'}, 'postTags': {'cellType': 'Pva'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Pva->Pva rule

netParam['connParams'].append({'preTags': {'cellType': 'Pva'}, 'postTags': {'cellType': 'Sst'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Pva->Sst rule

netParam['connParams'].append({'preTags': {'cellType': 'Sst'}, 'postTags': {'cellType': 'IT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Sst->IT rule

netParam['connParams'].append({'preTags': {'cellType': 'Sst'}, 'postTags': {'cellType': 'PT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Sst->PT rule             

netParam['connParams'].append({'preTags': {'cellType': 'Sst'}, 'postTags': {'cellType': 'CT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Sst->CT rule

netParam['connParams'].append({'preTags': {'cellType': 'Sst'}, 'postTags': {'cellType': 'Pva'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Sst->Pva rule

netParam['connParams'].append({'preTags': {'cellType': 'Sst'}, 'postTags': {'cellType': 'Sst'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Sst->Sst rule



# Dictionary of annotations
netParam['annots'] = {}
netParam['annots']['ITtoITconn'] = 'L2: weak by wiring matrix in (Weiler et al., 2008); L5 strong by wiring matrix in (Weiler et al., 2008)'

###############################################################################
# SIMULATION PARAMETERS
###############################################################################

simConfig = {}  # dictionary to store simConfig

# Simulation parameters
simConfig['duration'] = simConfig['tstop'] = 1*1e3 # Duration of the simulation, in ms
simConfig['dt'] = 0.5 # Internal integration timestep to use
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


