"""
params.py 

netParams is a dict containing a set of network parameters using a standardized structure

simConfig is a dict containing a set of simulation configurations using a standardized structure

Contributors: salvadordura@gmail.com
"""

from pylab import array
from utils import importCell


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

# General network parameters
netParams['scale'] = 1 # Size of simulation in thousands of cells
netParams['modelsize'] = 1000*netParams['scale'] # Size of netParamswork in um (~= 1000 neurons/column where column = 500um width)
netParams['sparseness'] = 0.1 # fraction of cells represented (num neurons = density * modelsize * sparseness)
netParams['cortthaldist'] = 1500 # Distance from relay nucleus to cortex -- ~1 cm = 10,000 um (check)
netParams['corticalthick'] = 1740 # cortical thickness/depth

## General connectivity parameters
netParams['mindelay'] = 2 # Minimum connection delay, in ms
netParams['velocity'] = 100 # Conduction velocity in um/ms (e 100 um = 0.1 m/s)
netParams['scaleconnweight'] = 0.025 # Connection weight scale factor
netParams['receptorweight'] = 1 # [1, 1, 1, 1, 1] # Scale factors for each receptor
netParams['scaleconnprob'] = 1 # 1/netParams['scale']*array([[1, 1], [1, 1]]) # scale*1* Connection probabilities for EE, EI, IE, II synapses, respectively -- scale for scale since size fixed
netParams['connfalloff'] = 200 # 100*array([2, 3]) # 2 in um for E and I synapses, respectively
netParams['toroidal'] = False # Whether or not to have toroidal topology

# Izhi cell params (used in cell properties)
izhiParams = {}
izhiParams['RS'] = {'C':100, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}
izhiParams['IB'] = {'C':150, 'k':1.2, 'vr':-75, 'vt':-45, 'vpeak':50, 'a':0.01, 'b':5, 'c':-56, 'd':130, 'celltype':2}
izhiParams['LTS'] = {'C':100, 'k':1.0, 'vr':-56, 'vt':-42, 'vpeak':40, 'a':0.03, 'b':8, 'c':-53, 'd':20, 'celltype':4}
izhiParams['FS'] = {'C':20, 'k':1.0, 'vr':-55, 'vt':-40, 'vpeak':25, 'a':0.2, 'b':-2, 'c':-45, 'd':-55, 'celltype':5}

# Cell properties list
netParams['cellProps'] = []

## IT cell params
cellProp = {'label': 'IT', 'conditions': {'cellType': 'IT'}, 'sections': {}, 'pointNeuron': {}}
cellProp['pointNeuron']['Izhi2007b'] = izhiParams['RS']
soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'syns': {}}  #  soma
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
soma['mechs']['hh'] = {'gnabar': 1, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} # HH 
soma['syns']['AMPA'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 0.05, 'tau2':5.3, 'e': 0}  # AMPA
soma['syns']['NMDA'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 15, 'tau2': 150, 'e': 0}  # NMDA
soma['syns']['GABAA'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
soma['syns']['GABAB'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
cellProp['sections'] = {'soma': soma}  # add sections to dict
netParams['cellProps'].append(cellProp)  # add dict to list of cell properties

## PT cell params
cellProp = {'label': 'PT', 'conditions': {'cellType': 'PT'}, 'sections': {}, 'pointNeuron':{}}
cellProp['pointNeuron']['Izhi2007b'] = izhiParams['IB']
soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'syns': {}}  #  soma
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
soma['mechs']['hh'] = {'gnabar': 1, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} # HH 
soma['syns']['AMPA'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 0.05, 'tau2':5.3, 'e': 0}  # AMPA
soma['syns']['NMDA'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 15, 'tau2': 150, 'e': 0}  # NMDA
soma['syns']['GABAA'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
soma['syns']['GABAB'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
cellProp['sections'] = {'soma': soma}  # add sections to dict
netParams['cellProps'].append(cellProp)  # add dict to list of cell properties

## CT cell params
cellProp = {'label': 'CT', 'conditions': {'cellType': 'CT'}, 'sections': {}, 'pointNeuron':{}}
cellProp['pointNeuron']['Izhi2007b'] = izhiParams['RS']
soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'syns': {}, 'Izhi2007Type': 'RS'}  #  soma
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
soma['mechs']['hh'] = {'gnabar': 1, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} # HH 
soma['syns']['AMPA'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 0.05, 'tau2':5.3, 'e': 0}  # AMPA
soma['syns']['NMDA'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 15, 'tau2': 150, 'e': 0}  # NMDA
soma['syns']['GABAA'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
soma['syns']['GABAB'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
cellProp['sections'] = {'soma': soma}  # add sections to dict
netParams['cellProps'].append(cellProp)  # add dict to list of cell properties

## SOM cell params
cellProp = {'label': 'SOM', 'conditions': {'cellType': 'SOM'}, 'sections': {}, 'pointNeuron':{}}
cellProp['pointNeuron']['Izhi2007b'] = izhiParams['LTS']
soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'syns': {}, 'Izhi2007Type': 'LTS'}  #  soma
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
soma['mechs']['hh'] = {'gnabar': 1, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} # HH 
soma['syns']['AMPA'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 0.05, 'tau2':5.3, 'e': 0}  # AMPA
soma['syns']['NMDA'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 15, 'tau2': 150, 'e': 0}  # NMDA
soma['syns']['GABAA'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
soma['syns']['GABAB'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
cellProp['sections'] = {'soma': soma}  # add sections to dict
netParams['cellProps'].append(cellProp)  # add dict to list of cell properties 

## PV cell params
cellProp = {'label': 'PV', 'conditions': {'cellType': 'PV'}, 'sections': {}, 'pointNeuron':{}}
cellProp['pointNeuron']['Izhi2007b'] = izhiParams['FS']
soma = {'geom': {}, 'topol': {}, 'mechs': {}, 'syns': {}, 'Izhi2007Type': 'FS'}  #  soma
soma['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
soma['mechs']['hh'] = {'gnabar': 1, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} # HH 
soma['syns']['AMPA'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 0.05, 'tau2':5.3, 'e': 0}  # AMPA
soma['syns']['NMDA'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 15, 'tau2': 150, 'e': 0}  # NMDA
soma['syns']['GABAA'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
soma['syns']['GABAB'] = {'type': 'Exp2Syn', 'loc': 0.5, 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB
cellProp['sections'] = {'soma': soma}  # add sections to dict
netParams['cellProps'].append(cellProp)  # add dict to list of cell properties


## create list of populations, where each item contains a dict with the pop params
netParams['popParams'] = []  
     
netParams['popParams'].append({'popLabel': 'IT_L23', 'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.1, 0.26], 'density': lambda y:2e3*y}) #  L2/3 IT
netParams['popParams'].append({'popLabel': 'IT_L4',  'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.26, 0.31], 'density': lambda y:2e3*y}) #  L4 IT
netParams['popParams'].append({'popLabel': 'IT_L5A', 'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.31, 0.52], 'density': lambda y:2e3*y}) #  L5A IT
netParams['popParams'].append({'popLabel': 'IT_L5B', 'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.52, 0.77], 'density': lambda y:2e3*y}) #  L5B IT
netParams['popParams'].append({'popLabel': 'PT_L5B', 'cellModel': 'Izhi2007b', 'cellType': 'PT',  'projTarget': '', 'yfracRange': [0.52, 0.77], 'density': lambda y:2e3*y}) #  L5B PT
netParams['popParams'].append({'popLabel': 'IT_L6',  'cellModel': 'Izhi2007b', 'cellType': 'IT',  'projTarget': '', 'yfracRange': [0.77, 1.0], 'density': lambda y:1e3}) #  L6 IT
netParams['popParams'].append({'popLabel': 'CT_L6',  'cellModel': 'Izhi2007b', 'cellType': 'CT',  'projTarget': '', 'yfracRange': [0.77, 1.0], 'density': lambda y:1e3}) #  L6 CT
netParams['popParams'].append({'popLabel': 'PV_L23', 'cellModel': 'Izhi2007b', 'cellType': 'PV',  'projTarget': '', 'yfracRange': [0.1, 0.31], 'density': lambda y:1e3}) #  L2/3 PV (FS)
netParams['popParams'].append({'popLabel': 'SOM_L23','cellModel': 'Izhi2007b', 'cellType': 'SOM', 'projTarget': '', 'yfracRange': [0.1, 0.31], 'density': lambda y:2e3*y}) #  L2/3 SOM (LTS)
netParams['popParams'].append({'popLabel': 'PV_L5',  'cellModel': 'Izhi2007b', 'cellType': 'PV',  'projTarget': '', 'yfracRange': [0.31, 0.77], 'density': lambda y:0.5e3}) #  L5 PV (FS)
netParams['popParams'].append({'popLabel': 'SOM_L5', 'cellModel': 'Izhi2007b', 'cellType': 'SOM', 'projTarget': '', 'yfracRange': [0.31, 0.77], 'density': lambda y:0.5e3}) #  L5 SOM (LTS)
netParams['popParams'].append({'popLabel': 'PV_L6',  'cellModel': 'Izhi2007b', 'cellType': 'PV',  'projTarget': '', 'yfracRange': [0.77, 1.0], 'density': lambda y:0.5e3}) #  L6 PV (FS)
netParams['popParams'].append({'popLabel': 'SOM_L6', 'cellModel': 'Izhi2007b', 'cellType': 'SOM', 'projTarget': '', 'yfracRange': [0.77, 1.0], 'density': lambda y:0.5e3}) #  L6 SOM (LTS)
netParams['popParams'].append({'popLabel': 'background', 'cellModel': 'NetStim', 'rate': 200, 'noise': 0.5, 'source': 'random'})  # background inputs

cellsList = [] 
cellsList.append({'cellLabel':'gs15', 'x': 1, 'yfrac': 0.4 , 'z': 2})
cellsList.append({'cellLabel':'gs21', 'x': 2, 'yfrac': 0.5 , 'z': 3})
netParams['popParams'].append({'popLabel': 'IT_cells', 'cellModel':'Izhi2007b', 'cellType':'IT', 'projTarget':'', 'cellsList': cellsList}) #  IT individual cells

cellsList = []
cellsList.append({'cellLabel':'bs50', 'cellType':'PT', 'projTarget':'',       'x': 1, 'yfrac': 0.4 , 'z': 2})
cellsList.append({'cellLabel':'bs91', 'cellType':'PT', 'projTarget':'lumbar', 'x': 2, 'yfrac': 0.5 , 'z': 3})
netParams['popParams'].append({'popLabel': 'PT_cells', 'cellModel':'HH', 'cellsList': cellsList}) #  PT individual cells

netParams['popTagsCopiedToCells'] = ['popLabel', 'cellModel', 'cellType', 'projTarget']  # tags from population that are copied over to the cells


# List of connectivity rules/params
netParams['connParams'] = []  

netParams['connParams'].append({'preTags': {'popLabel': 'background'}, 'postTags': {'cellType': 'IT' }, # background -> IT
    'connFunc': 'fullConn',
    'probability': 0.5, 
    'weight': 0.1, 
    'synReceptor': 'NMDA',
    'delay': 5})  

netParams['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'IT'}, # IT->IT rule
    'connFunc': 'probConn',
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty),
    'weight': (lambda prey,posty: 1), 
    'delay': 5,
    'synReceptor': 'AMPA',
    'annot': 'ITtoITconn'})  

netParams['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'PT'}, # IT->PT rule
    'connFunc': 'probConn',    
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), \
    'weight': (lambda prey,posty: 1), 
    'delay': 5, 
    'synReceptor': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'CT'}, # IT->CT rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda prey,posty: 1), 
    'delay': 5, 
    'synReceptor': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'PV'}, # IT->PV rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda prey,posty: 1), 
    'delay': 5, 
    'synReceptor': 'GABAA'})  

netParams['connParams'].append({'preTags': {'cellType': 'IT'}, 'postTags': {'cellType': 'SOM'}, # IT->SOM rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda prey,posty: 1), 
    'delay': 5, 
    'synReceptor': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'IT'}, # PT->IT rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda prey,posty: 1), 
    'delay': 5, 
    'synReceptor': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'PT'}, # PT->PT rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda prey,posty: 1), 
    'delay': 5, 
    'synReceptor': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'CT'}, # PT->CT rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda prex,posty: 1), 
    'delay': 5, 
    'synReceptor': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'PV'}, # PT->PV rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda x,y: 1), 
    'delay': 5, 
    'synReceptor': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PT'}, 'postTags': {'cellType': 'SOM'}, # PT->SOM rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda x,y: 1), 
    'delay': 5, 
    'synReceptor': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'IT'}, # CT->IT rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda x,y: 1), 
    'delay': 5, 
    'synReceptor': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'PT'}, # CT->PT rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda x,y: 1), 
    'delay': 5, 
    'synReceptor': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'CT'}, # CT->CT rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda x,y: 1), 
    'delay': 5, 
    'synReceptor': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'PV'}, # CT->PV rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda x,y: 1), 
    'delay': 5, 
    'synReceptor': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'CT'}, 'postTags': {'cellType': 'SOM'}, # CT->SOM rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda x,y: 1), 
    'delay': 5, 
    'synReceptor': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PV'}, 'postTags': {'cellType': 'IT'}, # PV->IT rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda x,y: 1), 
    'delay': 5, 
    'synReceptor': 'GABAA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PV'}, 'postTags': {'cellType': 'PT'}, # PV->PT rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda x,y: 1), 
    'delay': 5, 
    'synReceptor': 'GABAA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PV'}, 'postTags': {'cellType': 'CT'}, # PV->CT rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda x,y: 1), 
    'delay': 5, 
    'synReceptor': 'GABAA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PV'}, 'postTags': {'cellType': 'PV'}, # PV->PV rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda x,y: 1), 
    'delay': 5, 
    'synReceptor': 'AMPA'})  

netParams['connParams'].append({'preTags': {'cellType': 'PV'}, 'postTags': {'cellType': 'SOM'}, # PV->SOM rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda x,y: 1), 
    'delay': 5, 
    'synReceptor': 'GABAA'})  

netParams['connParams'].append({'preTags': {'cellType': 'SOM'}, 'postTags': {'cellType': 'IT'}, # SOM->IT rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda x,y: 1), 
    'delay': 5, 
    'synReceptor': 'GABAA'})  

netParams['connParams'].append({'preTags': {'cellType': 'SOM'}, 'postTags': {'cellType': 'PT'}, # SOM->PT rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda x,y: 1), 
    'delay': 5, 
    'synReceptor': 'GABAA'})               

netParams['connParams'].append({'preTags': {'cellType': 'SOM'}, 'postTags': {'cellType': 'CT'}, # SOM->CT rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda x,y: 1), 
    'delay': 5, 
    'synReceptor': 'GABAA'})  

netParams['connParams'].append({'preTags': {'cellType': 'SOM'}, 'postTags': {'cellType': 'PV'}, # SOM->PV rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda x,y: 1), 
    'delay': 5, 
    'synReceptor': 'GABAA'})  

netParams['connParams'].append({'preTags': {'cellType': 'SOM'}, 'postTags': {'cellType': 'SOM'}, # SOM->SOM rule
    'connFunc': 'probConn', 
    'probability': (lambda prey,posty: 0.1*prey+0.01/posty), 
    'weight': (lambda x,y: 1), 
    'delay': 5, 
    'synReceptor': 'GABAA'})  



# Dictionary of annotations
netParams['annots'] = {}
netParams['annots']['ITtoITconn'] = 'L2: weak by wiring matrix in (Weiler et al., 2008); L5 strong by wiring matrix in (Weiler et al., 2008)'


###############################################################################
# SIMULATION CONFIGURATION
###############################################################################

simConfig = {}  # dictionary to store simConfig

# Simulation parameters
simConfig['duration'] = simConfig['tstop'] = 1*1e3 # Duration of the simulation, in ms
simConfig['dt'] = 0.5 # Internal integration timestep to use
simConfig['randseed'] = 1 # Random seed to use
simConfig['createNEURONObj'] = 1  # create HOC objects when instantiating network
simConfig['createPyStruct'] = 1  # create Python structure (simulator-independent) when instantiating network
simConfig['verbose'] = 0 # Whether to write nothing (0), diagnostic information on events (1), or everything (2) a file directly from izhi.mod


# Recording 
simConfig['recordTraces'] = True  # whether to record cell traces or not
simConfig['recdict'] = {} #{'V':{'sec':'soma','pos':0.5,'var':'v'}, 'u':{'sec':'soma', 'pointProcess':'hIzhi', 'var':'u'}, 'I':{'sec':'soma', 'pointProcess':'hIzhi', 'var':'i'}}
simConfig['simDataVecs'] = ['spkt', 'spkid','stims']+simConfig['recdict'].keys()
simConfig['recordStim'] = True  # record spikes of cell stims
simConfig['recordStep'] = 10 # Step size in ms to save data (eg. V traces, LFP, etc)

# Saving
simConfig['filename'] = '../data/M1yfrac'  # Set file output name
simConfig['saveFileStep'] = 1000 # step size in ms to save data to disk
simConfig['savePickle'] = True # Whether or not to write spikes etc. to a .mat file
simConfig['saveJson'] = True # Whether or not to write spikes etc. to a .mat file
simConfig['saveMat'] = True # Whether or not to write spikes etc. to a .mat file
simConfig['saveTxt'] = False # save spikes and conn to txt file
simConfig['saveDpk'] = False # save to a .dpk pickled file


# Analysis and plotting 
simConfig['plotRaster'] = True # Whether or not to plot a raster
simConfig['plotTracesGids'] = [] # plot recorded traces for this list of cells
simConfig['plotPsd'] = False # plot power spectral density
simConfig['maxspikestoplot'] = 3e8 # Maximum number of spikes to plot
simConfig['plotConn'] = False # whether to plot conn matrix
simConfig['plotWeightChanges'] = False # whether to plot weight changes (shown in conn matrix)
simConfig['plot3dArch'] = False # plot 3d architecture


