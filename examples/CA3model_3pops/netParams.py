from netpyne import specs
from cfg import cfg

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters
netParams.defaultThreshold = 0.0
netParams.defineCellShapes = True       # sets 3d geometry aligned along the y-axis 


###############################################################################
## Cell types
###############################################################################
# Basket cell
BasketCell = {'secs':{}}
BasketCell['secs']['soma'] = {'geom': {}, 'mechs': {}}
BasketCell['secs']['soma']['geom'] = {'diam': 100, 'L': 31.831, 'nseg': 1, 'cm': 1}
BasketCell['secs']['soma']['mechs'] = {'pas': {'g': 0.1e-3, 'e': -65}, 'Nafbwb': {}, 'Kdrbwb': {}}
netParams.cellParams['BasketCell'] = BasketCell


# OLM cell
OlmCell = {'secs':{}}
OlmCell['secs']['soma'] = {'geom': {}, 'mechs': {}}
OlmCell['secs']['soma']['geom'] = {'diam': 100, 'L': 31.831, 'nseg': 1, 'cm': 1}
OlmCell['secs']['soma']['mechs'] = {
    'pas': {'g': 0.1e-3, 'e': -65},
    'Nafbwb': {}, 
    'Kdrbwb': {},
    'Iholmw': {},
    'Caolmw': {},
    'ICaolmw': {},
    'KCaolmw': {}}
netParams.cellParams['OlmCell'] = OlmCell

	
# Pyramidal cell
PyrCell = {'secs':{}}
PyrCell['secs']['soma'] = {'geom': {}, 'mechs': {}}
PyrCell['secs']['soma']['geom'] = {'diam': 20, 'L': 20, 'cm': 1, 'Ra': 150}
PyrCell['secs']['soma']['mechs'] = {
    'pas': {'g': 0.0000357, 'e': -70}, 
    'nacurrent': {},
    'kacurrent': {},
    'kdrcurrent': {},
    'hcurrent': {}}
PyrCell['secs']['Bdend'] = {'geom': {}, 'mechs': {}}
PyrCell['secs']['Bdend']['geom'] = {'diam': 2, 'L': 200, 'cm': 1, 'Ra': 150}
PyrCell['secs']['Bdend']['topol'] = {'parentSec': 'soma', 'parentX': 0, 'childX': 0}
PyrCell['secs']['Bdend']['mechs'] = {
    'pas': {'g': 0.0000357, 'e': -70}, 
    'nacurrent': {'ki': 1},
    'kacurrent': {},
    'kdrcurrent': {},
    'hcurrent': {}}
PyrCell['secs']['Adend1'] = {'geom': {}, 'mechs': {}}
PyrCell['secs']['Adend1']['geom'] = {'diam': 2, 'L': 150, 'cm': 1, 'Ra': 150}
PyrCell['secs']['Adend1']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0} # here there is a change: connected to end soma(1) instead of soma(0.5)
PyrCell['secs']['Adend1']['mechs'] = {
    'pas': {'g': 0.0000357, 'e': -70}, 
    'nacurrent': {'ki': 0.5},
    'kacurrent': {'g': 0.072},
    'kdrcurrent': {},
    'hcurrent': {'v50': -82, 'g': 0.0002}}     
PyrCell['secs']['Adend2'] = {'geom': {}, 'mechs': {}}
PyrCell['secs']['Adend2']['geom'] = {'diam': 2, 'L': 150, 'cm': 1, 'Ra': 150}
PyrCell['secs']['Adend2']['topol'] = {'parentSec': 'Adend1', 'parentX': 1, 'childX': 0}
PyrCell['secs']['Adend2']['mechs'] = {
    'pas': {'g': 0.0000357, 'e': -70}, 
    'nacurrent': {'ki': 0.5},
    'kacurrent': {'g': 0, 'gd': 0.120},
    'kdrcurrent': {},
    'hcurrent': {'v50': -90, 'g': 0.0004}}        
PyrCell['secs']['Adend3'] = {'geom': {}, 'mechs': {}}
PyrCell['secs']['Adend3']['geom'] = {'diam': 2, 'L': 150, 'cm': 2, 'Ra': 150}
PyrCell['secs']['Adend3']['topol'] = {'parentSec': 'Adend2', 'parentX': 1, 'childX': 0}
PyrCell['secs']['Adend3']['mechs'] = {
    'pas': {'g': 0.0000714, 'e': -70}, 
    'nacurrent': {'ki': 0.5},
    'kacurrent': {'g': 0, 'gd': 0.200},
    'kdrcurrent': {},
    'hcurrent': {'v50': -90, 'g': 0.0007}}
netParams.cellParams['PyrCell'] = PyrCell


###############################################################################
## Synaptic mechs
###############################################################################

netParams.synMechParams['AMPAf'] = {'mod': 'MyExp2SynBB', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}
netParams.synMechParams['NMDA'] = {'mod': 'MyExp2SynNMDABB', 'tau1': 0.05, 'tau2': 5.3, 'tau1NMDA': 15, 'tau2NMDA': 150, 'r': 1, 'e': 0}
netParams.synMechParams['GABAf'] = {'mod': 'MyExp2SynBB', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}
netParams.synMechParams['GABAs'] = {'mod': 'MyExp2SynBB', 'tau1': 0.2, 'tau2': 20, 'e': -80}
netParams.synMechParams['GABAss'] = {'mod': 'MyExp2SynBB', 'tau1': 20, 'tau2': 40, 'e': -80}


###############################################################################
## Populations
###############################################################################
netParams.popParams['PYR'] = {'cellType': 'PyrCell', 'numCells': 800}
netParams.popParams['BC'] = {'cellType': 'BasketCell', 'numCells': 200}
netParams.popParams['OLM'] = {'cellType': 'OlmCell', 'numCells': 200}


###############################################################################
# Current-clamp to cells
###############################################################################
netParams.stimSourceParams['IClamp_PYR'] =  {'type': 'IClamp', 'del': 2*cfg.dt, 'dur': 1e9, 'amp': 50e-3}
netParams.stimSourceParams['IClamp_OLM'] =  {'type': 'IClamp', 'del': 2*cfg.dt, 'dur': 1e9, 'amp': -25e-3}

netParams.stimTargetParams['IClamp_PYR->PYR'] = {
        'source': 'IClamp_PYR',
        'sec': 'soma',
        'loc': 0.5,
        'conds': {'pop': 'PYR'}}

netParams.stimTargetParams['IClamp_OLM->OLM'] = {
        'source': 'IClamp_OLM',
        'sec': 'soma',
        'loc': 0.5,
        'conds': {'pop': 'OLM'}}


###############################################################################
# Setting connections
###############################################################################

# PYR -> X, NMDA
netParams.connParams['PYR->BC_NMDA'] = {'preConds': {'pop': 'PYR'}, 'postConds': {'pop': 'BC'},
    'convergence': 100,
    'weight': 1.38e-3,
    'delay': 2,
    'sec': 'soma',
    'loc': 0.5,
    'synMech': 'NMDA'}

netParams.connParams['PYR->OLM_NMDA'] = {'preConds': {'pop': 'PYR'}, 'postConds': {'pop': 'OLM'},
    'convergence': 10,
    'weight': 0.7e-3,
    'delay': 2,
    'sec': 'soma',
    'loc': 0.5,
    'synMech': 'NMDA'}

netParams.connParams['PYR->PYR_NMDA'] = {'preConds': {'pop': 'PYR'}, 'postConds': {'pop': 'PYR'},
    'convergence': 25,
    'weight': 0.004e-3,
    'delay': 2,
    'sec': 'Bdend',
    'loc': 1.0,
    'synMech': 'NMDA'}

# PYR -> X, AMPA
netParams.connParams['PYR->BC_AMPA'] = {'preConds': {'pop': 'PYR'}, 'postConds': {'pop': 'BC'},
    'convergence': 100,
    'weight': 0.36e-3,
    'delay': 2,
    'sec': 'soma',
    'loc': 0.5,
    'synMech': 'AMPAf'}

netParams.connParams['PYR->OLM_AMPA'] = {'preConds': {'pop': 'PYR'}, 'postConds': {'pop': 'OLM'},
    'convergence': 10,
    'weight': 0.36e-3,
    'delay': 2,
    'sec': 'soma',
    'loc': 0.5,
    'synMech': 'AMPAf'}

netParams.connParams['PYR->PYR_AMPA'] = {'preConds': {'pop': 'PYR'}, 'postConds': {'pop': 'PYR'},
    'convergence': 25,
    'weight': 0.02e-3,
    'delay': 2,
    'sec': 'Bdend',
    'loc': 1.0,
    'synMech': 'AMPAf'}

# BC -> X, GABA
netParams.connParams['BC->BC_GABA'] = {'preConds': {'pop': 'BC'}, 'postConds': {'pop': 'BC'},
    'convergence': 60,
    'weight':4.5e-3,
    'delay': 2,
    'sec': 'soma',
    'loc': 0.5,
    'synMech': 'GABAf'}

netParams.connParams['BC->PYR_GABA'] = {'preConds': {'pop': 'BC'}, 'postConds': {'pop': 'PYR'},
    'convergence': 50,
    'weight': 0.72e-3,
    'delay': 2,
    'sec': 'soma',
    'loc': 0.5,
    'synMech': 'GABAf'}


# OLM -> PYR, GABA
netParams.connParams['OLM->PYR_GABA'] = {'preConds': {'pop': 'OLM'}, 'postConds': {'pop': 'PYR'},
    'convergence': 20,
    'weight': 72e-3,
    'delay': 2,
    'sec': 'Adend2',
    'loc': 0.5,
    'synMech': 'GABAs'}


###############################################################################
# Setting NetStims
###############################################################################
# to PYR
netParams.stimSourceParams['NetStim_PYR_SOMA_AMPA'] = {'type': 'NetStim', 'interval': 1, 'number': 1000*cfg.duration, 'start': 0, 'noise': 1}
netParams.stimTargetParams['NetStim_PYR_SOMA_AMPA->PYR'] = {
        'source': 'NetStim_PYR_SOMA_AMPA',
        'conds': {'pop': 'PYR'},
        'sec': 'soma',
        'loc': 0.5,
        'weight': 4*0.05e-3,  # different from published value
        'delay': 2*cfg.dt,
        'synMech': 'AMPAf'}

netParams.stimSourceParams['NetStim_PYR_ADEND3_AMPA'] = {'type': 'NetStim', 'interval': 1, 'number': 1000*cfg.duration, 'start': 0, 'noise': 1}
netParams.stimTargetParams['NetStim_PYR_ADEND3_AMPA->PYR'] = {
        'source': 'NetStim_PYR_ADEND3_AMPA',
        'conds': {'pop': 'PYR'},
        'sec': 'Adend3',
        'loc': 0.5,
        'weight': 4*0.05e-3,  # different from published value
        'delay': 2*cfg.dt,
        'synMech': 'AMPAf'}

netParams.stimSourceParams['NetStim_PYR_SOMA_GABA'] = {'type': 'NetStim', 'interval': 1, 'number': 1000*cfg.duration, 'start': 0, 'noise': 1}
netParams.stimTargetParams['NetStim_PYR_SOMA_GABA->PYR'] = {
        'source': 'NetStim_PYR_SOMA_GABA',
        'conds': {'pop': 'PYR'},
        'sec': 'soma',
        'loc': 0.5,
        'weight': 0.012e-3,
        'delay': 2*cfg.dt,
        'synMech': 'GABAf'}

netParams.stimSourceParams['NetStim_PYR_ADEND3_GABA'] = {'type': 'NetStim', 'interval': 1, 'number': 1000*cfg.duration, 'start': 0, 'noise': 1}
netParams.stimTargetParams['NetStim_PYR_ADEND3_GABA->PYR'] = {
        'source': 'NetStim_PYR_ADEND3_GABA',
        'conds': {'pop': 'PYR'},
        'sec': 'Adend3',
        'loc': 0.5,
        'weight': 0.012e-3,
        'delay': 2*cfg.dt,
        'synMech': 'GABAf'}

netParams.stimSourceParams['NetStim_PYR_ADEND3_NMDA'] = {'type': 'NetStim', 'interval': 100, 'number': int((1000/100.0)*cfg.duration), 'start': 0, 'noise': 1}
netParams.stimTargetParams['NetStim_PYR_ADEND3_NMDA->PYR'] = {
        'source': 'NetStim_PYR_ADEND3_NMDA',
        'conds': {'pop': 'PYR'},
        'sec': 'Adend3',
        'loc': 0.5,
        'weight': 6.5e-3,
        'delay': 2*cfg.dt,
        'synMech': 'NMDA'}

# to BC
netParams.stimSourceParams['NetStim_BC_SOMA_AMPA'] = {'type': 'NetStim', 'interval': 1, 'number': 1000*cfg.duration, 'start': 0, 'noise': 1}
netParams.stimTargetParams['NetStim_BC_SOMA_AMPA->BC'] = {
        'source': 'NetStim_BC_SOMA_AMPA',
        'conds': {'pop': 'BC'},
        'sec': 'soma',
        'loc': 0.5,
        'weight': 0.02e-3,
        'delay': 2*cfg.dt,
        'synMech': 'AMPAf'}

netParams.stimSourceParams['NetStim_BC_SOMA_GABA'] = {'type': 'NetStim', 'interval': 1, 'number': 1000*cfg.duration, 'start': 0, 'noise': 1}
netParams.stimTargetParams['NetStim_BC_SOMA_GABA->BC'] = {
        'source': 'NetStim_BC_SOMA_GABA',
        'conds': {'pop': 'BC'},
        'sec': 'soma',
        'loc': 0.5,
        'weight': 0.2e-3,
        'delay': 2*cfg.dt,
        'synMech': 'GABAf'}

# to OLM
netParams.stimSourceParams['NetStim_OLM_SOMA_AMPA'] = {'type': 'NetStim', 'interval': 1, 'number': 1000*cfg.duration, 'start': 0, 'noise': 1}
netParams.stimTargetParams['NetStim_OLM_SOMA_AMPA->OLM'] = {
        'source': 'NetStim_OLM_SOMA_AMPA',
        'conds': {'pop': 'OLM'},
        'sec': 'soma',
        'loc': 0.5,
        'weight': 0.0625e-3,
        'delay': 2*cfg.dt,
        'synMech': 'AMPAf'}

netParams.stimSourceParams['NetStim_OLM_SOMA_GABA'] = {'type': 'NetStim', 'interval': 1, 'number': 1000*cfg.duration, 'start': 0, 'noise': 1}
netParams.stimTargetParams['NetStim_OLM_SOMA_GABA->OLM'] = {
        'source': 'NetStim_OLM_SOMA_GABA',
        'conds': {'pop': 'OLM'},
        'sec': 'soma',
        'loc': 0.5,
        'weight': 0.2e-3,
        'delay': 2*cfg.dt,
        'synMech': 'GABAf'}

# Medial Septal inputs to BC and OLM cells
netParams.stimSourceParams['Septal'] = {'type': 'NetStim', 'interval': 150, 'number': int((1000/150)*cfg.duration), 'start': 0, 'noise': 0}
netParams.stimTargetParams['Septal->BC'] = {
        'source': 'Septal',
        'conds': {'pop': 'BC'},
        'sec': 'soma',
        'loc': 0.5,
        'weight': 1.6e-3,
        'delay': 2*cfg.dt,
        'synMech': 'GABAss'}

netParams.stimTargetParams['Septal->OLM'] = {
        'source': 'Septal',
        'conds': {'pop': 'OLM'},
        'sec': 'soma',
        'loc': 0.5,
        'weight': 1.6e-3,
        'delay': 2*cfg.dt,
        'synMech': 'GABAss'}
