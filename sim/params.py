"""
params.py 

netParams is a dict containing different sets of network parameters
eg. netParams['mpiHHTut'] or netParams['M1yfrac']

simConfig is a dict containing different sets of simulation configurations
eg. simConfig['default'] or simConfig['M1']

Contributors: salvadordura@gmail.com
"""

from pylab import array, inf


netParams = {}  # dictionary to store sets of network parameters
simConfig = {}  # dictionary to store sets of simulation configurations


###############################################################################
#
# NETWORK PARAMETERS
#
###############################################################################

###############################################################################
# MPI HH TUTORIAL PARAMS
###############################################################################

netParams['mpiHHTut'] = {}  # dictionary to store netParams
p = netParams['mpiHHTut']  # pointer to dict

## Position parameters
p['scale'] = 1 # Size of simulation in thousands of cells
p['corticalthick'] = 1000 # cortical thickness/depth

## Background input parameters
p['useBackground'] = True # Whether or not to use background stimuli
p['backgroundRate'] = 10 # Rate of stimuli (in Hz)
p['backgroundRateMin'] = 0.5 # Rate of stimuli (in Hz)
p['backgroundNumber'] = 1e10 # Number of spikes
p['backgroundNoise'] = 1 # Fractional noise
p['backgroundWeight'] = 0.1*array([1,0.1]) # Weight for background input for E cells and I cells
p['backgroundReceptor'] = 'NMDA' # Which receptor to stimulate
    
# Cell properties list
p['cellProperties'] = []

# PYR cell properties
cellProp = {'label': 'PYR', 'conditions': {'cellType': 'PYR'}, 'Izhi2007Type': 'RS', 'sections': {}}

soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'syns': {}}  # soma properties
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0, 'pt3d': []}
soma['geom']['pt3d'].append({'x': 0, 'y': 0, 'z': 0, 'd': 20})
soma['geom']['pt3d'].append({'x': 0, 'y': 0, 'z': 20, 'd': 20})
soma['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} 
soma['syns']['AMPA'] = {'type': 'ExpSyn', 'loc': 0.5, 'tau1': 0.05, 'tau2': 5.3, 'e': 0}

dend = {'geom': {}, 'topol': {}, 'mechs': {}, 'syns': {}}  # dend properties
dend['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 150.0, 'cm': 1, 'pt3d': []}
dend['geom']['pt3d'].append({'x': 0, 'y': 0, 'z': 0, 'd': 20})
dend['geom']['pt3d'].append({'x': 0, 'y': 0, 'z': 20, 'd': 20})
dend['topol'] = {'parentSec': 'soma', 'parentX': 0, 'childX': 0}
dend['mechs']['pas'] = {'g': 0.0000357, 'e': -70} 
dend['mechs']['nacurrent'] = {'ki': 1}
dend['syns']['NMDA'] = {'type': 'ExpSyn', 'loc': 1.0, 'tau1': 15, 'tau2': 150, 'r': 1, 'e': 0}

cellProp['sections'] = {'soma': soma, 'dend': dend}  # add sections to dict
p['cellProperties'].append(cellProp)  # add dict to list of cell properties

# Population parameters
p['popParams'] = []  # create list of populations - each item will contain dict with pop params
p['popParams'].append({'cellModel': 'HH', 'cellType': 'PYR', 'numCells': 100}) # add dict with params for this pop 

p['connType'] = 'random'
p['numReceptors'] = 1
p['maxcons']   = 20                   # number of connections onto each cell
p['weight']    = 0.004                # weight of each connection
p['delaymean'] = 13.0                 # mean of delays
p['delayvar']  = 1.4                  # variance of delays
p['delaymin']  = 0.2                  # miniumum delays
p['threshold'] = 10.0                 # threshold 




###############################################################################
# M1 6-LAYER YFRAC-BASED MODEL
###############################################################################

netParams['M1yfrac'] = {}  # dictionary to store netParams
p = netParams['M1yfrac']  # pointer to dict

## Position parameters
p['scale'] = 1 # Size of simulation in thousands of cells
p['cortthaldist'] = 1500 # Distance from relay nucleus to cortex -- ~1 cm = 10,000 um (check)
p['corticalthick'] = 1740 # cortical thickness/depth

## Background input parameters
p['useBackground'] = True # Whether or not to use background stimuli
p['backgroundRate'] = 5 # Rate of stimuli (in Hz)
p['backgroundRateMin'] = 0.1 # Rate of stimuli (in Hz)
p['backgroundNumber'] = 1e10 # Number of spikes
p['backgroundNoise'] = 1 # Fractional noise
p['backgroundWeight'] = 0.1*array([1,0.1]) # Weight for background input for E cells and I cells
p['backgroundReceptor'] = 'NMDA' # Which receptor to stimulate

# Cell properties list
p['cellProperties'] = []

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
p['cellProperties'].append(cellProp)  # add dict to list of cell properties

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
p['cellProperties'].append(cellProp)  # add dict to list of cell properties

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
p['cellProperties'].append(cellProp)  # add dict to list of cell properties

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
p['cellProperties'].append(cellProp)  # add dict to list of cell properties 

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
p['cellProperties'].append(cellProp)  # add dict to list of cell properties

# create list of populations, where each item contains a dict with the pop params
p['popParams'] = []  
     
p['popParams'].append({'label': 'IT_L23', 'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.1, 0.26], 'density': lambda y:2e3*y}) #  L2/3 IT
p['popParams'].append({'label': 'IT_L4',  'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.26, 0.31], 'density': lambda y:2e3*y}) #  L4 IT
p['popParams'].append({'label': 'IT_L5A', 'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.31, 0.52], 'density': lambda y:2e3*y}) #  L5A IT
p['popParams'].append({'label': 'IT_L5B', 'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.52, 0.77], 'density': lambda y:2e3*y}) #  L5B IT
p['popParams'].append({'label': 'PT_L5B', 'cellModel': 'Izhi2007b', 'cellType': 'PT',  'projTarget': '', 'yfracRange': [0.52, 0.77], 'density': lambda y:2e3*y}) #  L5B PT
p['popParams'].append({'label': 'IT_L6',  'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.77, 1.0], 'density': lambda y:1e3}) #  L6 IT
p['popParams'].append({'label': 'CT_L6',  'cellModel': 'Izhi2007b', 'cellType': 'CT',  'projTarget': '', 'yfracRange': [0.77, 1.0], 'density': lambda y:1e3}) #  L6 CT
p['popParams'].append({'label': 'PV_L23', 'cellModel': 'Izhi2007b', 'cellType': 'PV',  'projTarget': '', 'yfracRange': [0.1, 0.31], 'density': lambda y:1e3}) #  L2/3 PV (LTS)
p['popParams'].append({'label': 'SOM_L23','cellModel': 'Izhi2007b', 'cellType': 'SOM', 'projTarget': '', 'yfracRange': [0.1, 0.31], 'density': lambda y:2e3*y}) #  L2/3 SOM (FS)
p['popParams'].append({'label': 'PV_L5',  'cellModel': 'Izhi2007b', 'cellType': 'PV',  'projTarget': '', 'yfracRange': [0.31, 0.77], 'density': lambda y:0.5e3}) #  L5 PV (FS)
p['popParams'].append({'label': 'SOM_L5', 'cellModel': 'Izhi2007b', 'cellType': 'SOM', 'projTarget': '', 'yfracRange': [0.31, 0.77], 'density': lambda y:0.5e3}) #  L5 SOM (LTS)
p['popParams'].append({'label': 'PV_L6',  'cellModel': 'Izhi2007b', 'cellType': 'PV',  'projTarget': '', 'yfracRange': [0.77, 1.0], 'density': lambda y:0.5e3}) #  L6 PV (FS)
p['popParams'].append({'label': 'SOM_L6', 'cellModel': 'Izhi2007b', 'cellType': 'SOM', 'projTarget': '', 'yfracRange': [0.77, 1.0], 'density': lambda y:0.5e3}) #  L6 SOM (LTS)

cellsList = []
cellsList.append({'label':'gs15', 'x': 1, 'yfrac': 0.4 , 'z': 2})
cellsList.append({'label':'gs21', 'x': 2, 'yfrac': 0.5 , 'z': 3})
p['popParams'].append({'label': 'IT_cells', 'cellModel':'Izhi2007b', 'cellType':'IT', 'projTarget':'', 'cellsList': cellsList}) #  IT individual cells

cellsList = []
cellsList.append({'label':'bs50', 'cellModel': 'Izhi2007b',  'cellType':'PT', 'projTarget':'',       'x': 1, 'yfrac': 0.4 , 'z': 2})
cellsList.append({'label':'bs91', 'cellModel': 'HH',         'cellType':'PT', 'projTarget':'lumbar', 'x': 2, 'yfrac': 0.5 , 'z': 3})
p['popParams'].append({'label': 'PT_cells', 'cellsList': cellsList}) #  PT individual cells

## General connectivity parameters
p['connType'] = 'yfrac'
#p['numReceptors'] = 1 
p['useconnprobdata'] = True # Whether or not to use connectivity data
p['useconnweightdata'] = True # Whether or not to use weight data
p['mindelay'] = 2 # Minimum connection delay, in ms
p['velocity'] = 100 # Conduction velocity in um/ms (e.g. 50 = 0.05 m/s)
p['modelsize'] = 1000*p['scale'] # Size of netParamswork in um (~= 1000 neurons/column where column = 500um width)
p['sparseness'] = 0.1 # fraction of cells represented (num neurons = density * modelsize * sparseness)
p['scaleconnweight'] = 0.00025*array([[2, 1], [2, 0.1]]) # Connection weights for EE, EI, IE, II synapses, respectively
p['receptorweight'] = [1, 1, 1, 1, 1] # Scale factors for each receptor
p['scaleconnprob'] = 1/p['scale']*array([[1, 1], [1, 1]]) # scale*1* Connection probabilities for EE, EI, IE, II synapses, respectively -- scale for scale since size fixed
p['connfalloff'] = 100*array([2, 3]) # Connection length constants in um for E and I synapses, respectively
p['toroidal'] = False # Whether or not to have toroidal topology

## List of connectivity rules/params
p['connParams'] = []  

p['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'IT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty),
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # IT->IT rule

p['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'IT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # IT->IT rule

p['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'PT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # IT->PT rule

p['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'CT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # IT->CT rule

p['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'Pva'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # IT->Pva rule

p['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'Sst'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # IT->Sst rule

p['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'IT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # PT->IT rule

p['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'PT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prey,posty: 1), 'syn': 'AMPA'})  # PT->PT rule

p['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'CT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda prex,posty: 1), 'syn': 'AMPA'})  # PT->CT rule

p['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'Pva'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # PT->Pva rule

p['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'Sst'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # PT->Sst rule

p['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'IT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # CT->IT rule

p['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'PT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # CT->PT rule

p['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'CT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # CT->CT rule

p['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'Pva'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # CT->Pva rule

p['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'Sst'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # CT->Sst rule

p['connParams'].append({'preTags': {'cellType': 'Pva'}, 'postTags': {'cellType': 'IT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Pva->IT rule

p['connParams'].append({'preTags': {'cellType': 'Pva'}, 'postTags': {'cellType': 'PT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Pva->PT rule

p['connParams'].append({'preTags': {'cellType': 'Pva'}, 'postTags': {'cellType': 'CT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Pva->CT rule

p['connParams'].append({'preTags': {'cellType': 'Pva'}, 'postTags': {'cellType': 'Pva'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Pva->Pva rule

p['connParams'].append({'preTags': {'cellType': 'Pva'}, 'postTags': {'cellType': 'Sst'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Pva->Sst rule

p['connParams'].append({'preTags': {'cellType': 'Sst'}, 'postTags': {'cellType': 'IT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Sst->IT rule

p['connParams'].append({'preTags': {'cellType': 'Sst'}, 'postTags': {'cellType': 'PT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Sst->PT rule             

p['connParams'].append({'preTags': {'cellType': 'Sst'}, 'postTags': {'cellType': 'CT'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Sst->CT rule

p['connParams'].append({'preTags': {'cellType': 'Sst'}, 'postTags': {'cellType': 'Pva'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Sst->Pva rule

p['connParams'].append({'preTags': {'cellType': 'Sst'}, 'postTags': {'cellType': 'Sst'},
    'connProb': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'connWeight': (lambda x,y: 1), 'syn': 'AMPA'})  # Sst->Sst rule





###############################################################################
#
# SIMULATION PARAMETERS
#
###############################################################################


###############################################################################
# DEFAULT
###############################################################################

simConfig['default'] = {}  # dictionary to store simConfig
cfg = simConfig['default']  # pointer to dict

# Simulation parameters
cfg['duration'] = cfg['tstop'] = 1*1e3 # Duration of the simulation, in ms
#h.dt = cfg['dt'] = 0.5 # Internal integration timestep to use
cfg['recordStep'] = 10 # Step size in ms to save data (eg. V traces, LFP, etc)
cfg['saveFileStep'] = 1000 # step size in ms to save data to disk
cfg['randseed'] = 1 # Random seed to use

## Recording 
cfg['recdict'] = {'Vsoma':'soma(0.5)._ref_v'}
cfg['simdataVecs'] = ['spkt', 'spkid']


## Saving and plotting parameters
cfg['filename'] = '../data/m1ms'  # Set file output name
cfg['savemat'] = True # Whether or not to write spikes etc. to a .mat file
cfg['savetxt'] = False # save spikes and conn to txt file
cfg['savedpk'] = True # save to a .dpk pickled file
cfg['recordTraces'] = True  # whether to record cell traces or not
cfg['saveBackground'] = False # save background (NetStims) inputs
cfg['verbose'] = 0 # Whether to write nothing (0), diagnostic information on events (1), or everything (2) a file directly from izhi.mod
cfg['plotraster'] = True # Whether or not to plot a raster
cfg['plotpsd'] = False # plot power spectral density
cfg['maxspikestoplot'] = 3e8 # Maximum number of spikes to plot
cfg['plotconn'] = False # whether to plot conn matrix
cfg['plotweightchanges'] = False # whether to plot weight changes (shown in conn matrix)
cfg['plot3darch'] = False # plot 3d architecture

## Stimulus parameters
cfg['usestims'] = False # Whether or not to use stimuli at all
cfg['ltptimes']  = [5, 10] # Pre-microstim touch times
cfg['ziptimes'] = [10, 15] # Pre-microstim touch times



###############################################################################
# M1
###############################################################################

simConfig['M1'] = dict(simConfig['default']) # deep copy of existing config
cfg = simConfig['M1']

cfg['recdict'] = {'V':'sec(0.5)._ref_v', 'u':'m._ref_u', 'I':'m._ref_i'}



