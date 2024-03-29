"""
params.py

netParams is a dict containing a set of network parameters using a standardized structure

simConfig is a dict containing a set of simulation configurations using a standardized structure
"""

from netpyne import specs

netParams = specs.NetParams()   # object of class NetParams to store the network parameters

###############################################################################
#
# M1 6-LAYER ynorm-BASED MODEL
#
###############################################################################

###############################################################################
# NETWORK PARAMETERS
###############################################################################


# General network parameters
netParams.scale = 1 # Scale factor for number of cells
netParams.sizeX = 50 # x-dimension (horizontal length) size in um
netParams.sizeY = 1350 # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = 50 # z-dimension (horizontal depth) size in um

## General connectivity parameters
netParams.scaleConnWeight = 0.01 # Connection weight scale factor
netParams.scaleConnWeightNetStims = 0.1 # Connection weight scale factor for NetStims
netParams.defaultDelay = 2.0 # default conn delay (ms)
netParams.propVelocity = 100.0 # propagation velocity (um/ms)
netParams.probLambda = 100.0  # length constant (lambda) for connection probability decay (um)

## create list of populations, where each item contains a dict with the pop params
netParams.popParams['IT_L23'] = {'cellType': 'IT', 'ynormRange': [0.12, 0.31], 'density': 80e3} #  L2/3 IT # - same below
netParams.popParams['IT_L4'] =  {'cellType': 'IT', 'ynormRange': [0.31, 0.41], 'density': 80e3} #  L4 IT
netParams.popParams['IT_L5A'] = {'cellType': 'IT', 'ynormRange': [0.41, 0.52], 'density': 80e3} #  L5A IT
netParams.popParams['IT_L5B'] = {'cellType': 'IT', 'ynormRange': [0.52, 0.77], 'density': 40e3} #  L5B IT
netParams.popParams['PT_L5B'] = {'cellType': 'PT', 'ynormRange': [0.52, 0.77], 'density': 40e3} #  L5B PT
netParams.popParams['IT_L6'] =  {'cellType': 'IT', 'ynormRange': [0.77, 1.0], 'density': 40e3} #  L6 IT
netParams.popParams['CT_L6'] =  {'cellType': 'CT', 'ynormRange': [0.77, 1.0], 'density': 40e3} #  L6 CT
netParams.popParams['PV_L23'] = {'cellType': 'PV', 'ynormRange': [0.1, 0.31], 'density': 10e3} #  L2/3 PV (FS)
netParams.popParams['SOM_L23'] ={'cellType': 'SOM', 'ynormRange': [0.1, 0.31], 'density': 10e3} #  L2/3 SOM (LTS)
netParams.popParams['PV_L5'] =  {'cellType': 'PV', 'ynormRange': [0.31, 0.77], 'density': 10e3} #  L5 PV (FS)
netParams.popParams['SOM_L5'] = {'cellType': 'SOM','ynormRange': [0.31, 0.77], 'density': 10e3} #  L5 SOM (LTS)
netParams.popParams['PV_L6'] =  {'cellType': 'PV', 'ynormRange': [0.77, 1.0], 'density': 10e3} #  L6 PV (FS)
netParams.popParams['SOM_L6'] = {'cellType': 'SOM','ynormRange': [0.77, 1.0], 'density': 10e3} #  L6 SOM (LTS)


## Izhi cell params (used in cell properties)
izhiParams = {}
izhiParams['RS'] = {'mod':'Izhi2007b', 'C':1, 'k':0.7, 'vr':-60, 'vt':-40, 'vpeak':35, 'a':0.03, 'b':-2, 'c':-50, 'd':100, 'celltype':1}
izhiParams['IB'] = {'mod':'Izhi2007b', 'C':1.5, 'k':1.2, 'vr':-75, 'vt':-45, 'vpeak':50, 'a':0.01, 'b':5, 'c':-56, 'd':130, 'celltype':2}
izhiParams['LTS'] = {'mod':'Izhi2007b', 'C':1.0, 'k':1.0, 'vr':-56, 'vt':-42, 'vpeak':40, 'a':0.03, 'b':8, 'c':-53, 'd':20, 'celltype':4}
izhiParams['FS'] = {'mod':'Izhi2007b', 'C':0.2, 'k':1.0, 'vr':-55, 'vt':-40, 'vpeak':25, 'a':0.2, 'b':-2, 'c':-45, 'd':-55, 'celltype':5}

## IT cell params
cellRule = {'conds': {'cellType': 'IT'}, 'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'pointps':{}}  #  soma
cellRule['secs']['soma']['geom'] = {'diam': 10, 'L': 10, 'cm': 31.831}
cellRule['secs']['soma']['pointps']['Izhi'] = izhiParams['RS']
netParams.cellParams['IT'] = cellRule  # add dict to list of cell properties

## PT cell params
cellRule = {'conds': {'cellType': 'PT'}, 'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'pointps':{}}  #  soma
cellRule['secs']['soma']['geom'] = {'diam': 10, 'L': 10, 'cm': 31.831}
cellRule['secs']['soma']['pointps']['Izhi'] = izhiParams['IB']
netParams.cellParams['PT'] = cellRule  # add dict to list of cell properties

## CT cell params
cellRule = {'conds': {'cellType': 'CT'}, 'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'pointps':{}}  #  soma
cellRule['secs']['soma']['geom'] = {'diam': 10, 'L': 10, 'cm': 31.831}
cellRule['secs']['soma']['pointps']['Izhi'] = izhiParams['RS']
netParams.cellParams['CT'] = cellRule  # add dict to list of cell properties

## SOM cell params
cellRule = { 'conds': {'cellType': 'SOM'}, 'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'pointps':{}}  #  soma
cellRule['secs']['soma']['geom'] = {'diam': 10, 'L': 10, 'cm': 31.831}
cellRule['secs']['soma']['pointps']['Izhi'] = izhiParams['LTS']
netParams.cellParams['SOM'] = cellRule  # add dict to list of cell properties

## PV cell params
cellRule = {'conds': {'cellType': 'PV'}, 'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'pointps':{}}  #  soma
cellRule['secs']['soma']['geom'] = {'diam': 10, 'L': 10, 'cm': 31.831}
cellRule['secs']['soma']['pointps']['Izhi'] = izhiParams['FS']
netParams.cellParams['PV'] = cellRule  # add dict to list of cell properties

# Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # AMPA
netParams.synMechParams['NMDA'] = {'mod': 'Exp2Syn', 'tau1': 0.15, 'tau2': 15, 'e': 0}  # NMDA
netParams.synMechParams['GABAA'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAA
netParams.synMechParams['GABAB'] = {'mod': 'Exp2Syn', 'tau1': 0.07, 'tau2': 9.1, 'e': -80}  # GABAB


# Stimulation parameters
netParams.stimSourceParams['background_E']  = {'type': 'NetStim', 'rate': 20, 'noise': 0.5} # background inputs to Exc
netParams.stimSourceParams['background_I']  = {'type': 'NetStim', 'rate': 20, 'noise': 0.5} # background inputs to Inh

netParams.stimTargetParams['bgE->IT,CT'] = {'source': 'background_E', 'conds': {'cellType': ['IT','CT']},
                                            'synMech': 'NMDA', 'weight': 0.1, 'delay': 'normal(5,3)'}
netParams.stimTargetParams['bgE->PT'] = {'source': 'background_E', 'conds': {'cellType': ['PT']},
                                            'synMech': 'NMDA', 'weight': 0.1, 'delay': 'normal(5,3)'}
netParams.stimTargetParams['bgI->PV'] = {'source': 'background_E', 'conds': {'cellType': ['PV']},
                                            'synMech': 'NMDA', 'weight': 0.05, 'delay': 'normal(5,3)'}
netParams.stimTargetParams['bgI->SOM'] = {'source': 'background_E', 'conds': {'cellType': ['SOM']},
                                            'synMech': 'NMDA', 'weight': 0.03, 'delay': 'normal(5,3)'}

# List of connectivity rules/params
netParams.ItoIweight = 0.5

# Generated using importConnFromExcel() function in params/utils.py
netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.1,0.2]},
'postConds': {'cellType': 'IT', 'ynorm': [0.1,0.2]},
'synMech': 'AMPA',
'probability': 0.09263,
'weight': 0.64,
'delay': 'defaultDelay+dist_3D/propVelocity'})


netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.1,0.2]},
'postConds': {'cellType': 'IT', 'ynorm': [0.2,0.3]},
'synMech': 'AMPA',
'probability': 0.05354,
'weight': 0.44,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.1,0.2]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3,0.4]},
'synMech': 'AMPA',
'probability': 0.15907,
'weight': 0.31,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.2,0.3]},
'postConds': {'cellType': 'IT', 'ynorm': [0.1,0.2]},
'synMech': 'AMPA',
'probability': 0.02652,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.2,0.3]},
'postConds': {'cellType': 'IT', 'ynorm': [0.2,0.3]},
'synMech': 'AMPA',
'probability': 0.18713,
'weight': 0.78,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.2,0.3]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3,0.4]},
'synMech': 'AMPA',
'probability': 0.05749,
'weight': 0.36,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.3,0.4]},
'postConds': {'cellType': 'IT', 'ynorm': [0.1,0.2]},
'synMech': 'AMPA',
'probability': 0.02757,
'weight': 0.98,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.3,0.4]},
'postConds': {'cellType': 'IT', 'ynorm': [0.2,0.3]},
'synMech': 'AMPA',
'probability': 0.06036,
'weight': 0.58,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.3,0.4]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3,0.4]},
'synMech': 'AMPA',
'probability': 0.24283,
'weight': 0.95,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.3,0.4]},
'postConds': {'cellType': ['IT','CT'], 'ynorm': [0.8,0.9]},
'synMech': 'AMPA',
'probability': 0.00112,
'weight': 2.27,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.4,0.5]},
'postConds': {'cellType': 'IT', 'ynorm': [0.1,0.2]},
'synMech': 'AMPA',
'probability': 0.05249,
'weight': 0.52,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.4,0.5]},
'postConds': {'cellType': 'IT', 'ynorm': [0.2,0.3]},
'synMech': 'AMPA',
'probability': 0.02253,
'weight': 0.67,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.4,0.5]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3,0.4]},
'synMech': 'AMPA',
'probability': 0.02279,
'weight': 0.48,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.4,0.5]},
'postConds': {'cellType': ['IT','CT'], 'ynorm': [0.8,0.9]},
'synMech': 'AMPA',
'probability': 0.02354,
'weight': 0.28,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.4,0.5]},
'postConds': {'cellType': ['IT','CT'], 'ynorm': [0.9,1.0]},
'synMech': 'AMPA',
'probability': 0.0045,
'weight': 0.28,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.5,0.6]},
'postConds': {'cellType': 'IT', 'ynorm': [0.1,0.2]},
'synMech': 'AMPA',
'probability': 0.03723,
'weight': 0.21,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.5,0.6]},
'postConds': {'cellType': 'IT', 'ynorm': [0.2,0.3]},
'synMech': 'AMPA',
'probability': 0.03549,
'weight': 0.26,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.5,0.6]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3,0.4]},
'synMech': 'AMPA',
'probability': 0.04656,
'weight': 0.17,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.5,0.6]},
'postConds': {'cellType': ['IT','CT'], 'ynorm': [0.8,0.9]},
'synMech': 'AMPA',
'probability': 0.01985,
'weight': 0.49,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.5,0.6]},
'postConds': {'cellType': ['IT','CT'], 'ynorm': [0.9,1.0]},
'synMech': 'AMPA',
'probability': 0.0041,
'weight': 0.49,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.6,0.7]},
'postConds': {'cellType': 'IT', 'ynorm': [0.1,0.2]},
'synMech': 'AMPA',
'probability': 0.0023,
'weight': 0.21,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.6,0.7]},
'postConds': {'cellType': 'IT', 'ynorm': [0.2,0.3]},
'synMech': 'AMPA',
'probability': 0.0164,
'weight': 0.26,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.6,0.7]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3,0.4]},
'synMech': 'AMPA',
'probability': 0.01887,
'weight': 0.17,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.6,0.7]},
'postConds': {'cellType': ['IT','CT'], 'ynorm': [0.8,0.9]},
'synMech': 'AMPA',
'probability': 0.02843,
'weight': 0.49,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.6,0.7]},
'postConds': {'cellType': ['IT','CT'], 'ynorm': [0.9,1.0]},
'synMech': 'AMPA',
'probability': 0.00608,
'weight': 0.49,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.7,0.8]},
'postConds': {'cellType': 'IT', 'ynorm': [0.2,0.3]},
'synMech': 'AMPA',
'probability': 0.00248,
'weight': 0.26,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.7,0.8]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3,0.4]},
'synMech': 'AMPA',
'probability': 0.02445,
'weight': 0.17,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.7,0.8]},
'postConds': {'cellType': ['IT','CT'], 'ynorm': [0.8,0.9]},
'synMech': 'AMPA',
'probability': 0.02534,
'weight': 0.49,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.7,0.8]},
'postConds': {'cellType': ['IT','CT'], 'ynorm': [0.9,1.0]},
'synMech': 'AMPA',
'probability': 0.01239,
'weight': 0.49,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.8,0.9]},
'postConds': {'cellType': ['IT','CT'], 'ynorm': [0.8,0.9]},
'synMech': 'AMPA',
'probability': 0.0282,
'weight': 0.53,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.8,0.9]},
'postConds': {'cellType': ['IT','CT'], 'ynorm': [0.9,1.0]},
'synMech': 'AMPA',
'probability': 0.01523,
'weight': 0.53,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.9,1.0]},
'postConds': {'cellType': ['IT','CT'], 'ynorm': [0.8,0.9]},
'synMech': 'AMPA',
'probability': 0.02209,
'weight': 0.53,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','CT'], 'ynorm': [0.9,1.0]},
'postConds': {'cellType': ['IT','CT'], 'ynorm': [0.9,1.0]},
'synMech': 'AMPA',
'probability': 0.0282,
'weight': 0.53,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0,0.0625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3125,0.375]},
'synMech': 'AMPA',
'probability': 0.01552,
'weight': 0.31,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0,0.0625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.375,0.4375]},
'synMech': 'AMPA',
'probability': 0.00752,
'weight': 0.43,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0,0.0625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.00313,
'weight': 0.55,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0,0.0625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.00161,
'weight': 0.55,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0,0.0625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.00162,
'weight': 0.22,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0,0.0625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.00566,
'weight': 0.22,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0,0.0625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.00283,
'weight': 0.22,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.0625,0.125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3125,0.375]},
'synMech': 'AMPA',
'probability': 0.01825,
'weight': 0.31,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.0625,0.125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.375,0.4375]},
'synMech': 'AMPA',
'probability': 0.02673,
'weight': 0.43,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.0625,0.125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.01177,
'weight': 0.55,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.0625,0.125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.00447,
'weight': 0.55,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.0625,0.125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.01216,
'weight': 0.22,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.0625,0.125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.01007,
'weight': 0.22,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.0625,0.125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.00672,
'weight': 0.22,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.125,0.1875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3125,0.375]},
'synMech': 'AMPA',
'probability': 0.0199,
'weight': 0.31,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.125,0.1875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.375,0.4375]},
'synMech': 'AMPA',
'probability': 0.25242,
'weight': 0.43,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.125,0.1875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.10856,
'weight': 0.55,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.125,0.1875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.01429,
'weight': 0.55,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.125,0.1875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.0429,
'weight': 0.22,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.125,0.1875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.0403,
'weight': 0.22,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.125,0.1875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.01982,
'weight': 0.22,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.1875,0.25]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3125,0.375]},
'synMech': 'AMPA',
'probability': 0.02528,
'weight': 0.36,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.1875,0.25]},
'postConds': {'cellType': 'IT', 'ynorm': [0.375,0.4375]},
'synMech': 'AMPA',
'probability': 0.07305,
'weight': 0.645,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.1875,0.25]},
'postConds': {'cellType': 'IT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.03289,
'weight': 0.93,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.1875,0.25]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.01182,
'weight': 1.01,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.1875,0.25]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.01017,
'weight': 1.01,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.1875,0.25]},
'postConds': {'cellType': 'IT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.00814,
'weight': 1.01,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.1875,0.25]},
'postConds': {'cellType': 'IT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.00615,
'weight': 1.01,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.25,0.3125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3125,0.375]},
'synMech': 'AMPA',
'probability': 0.03508,
'weight': 0.36,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.25,0.3125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.375,0.4375]},
'synMech': 'AMPA',
'probability': 0.02558,
'weight': 0.645,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.25,0.3125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.0212,
'weight': 0.93,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.25,0.3125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.01126,
'weight': 1.01,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.25,0.3125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.01244,
'weight': 1.01,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.25,0.3125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.01172,
'weight': 1.01,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.25,0.3125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.00771,
'weight': 1.01,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.3125,0.375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3125,0.375]},
'synMech': 'AMPA',
'probability': 0.24283,
'weight': 0.95,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.3125,0.375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.375,0.4375]},
'synMech': 'AMPA',
'probability': 0.02792,
'weight': 0.745,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.3125,0.375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.02731,
'weight': 0.54,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.3125,0.375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.01384,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.3125,0.375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.01409,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.3125,0.375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.02068,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.3125,0.375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.01678,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.375,0.4375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3125,0.375]},
'synMech': 'AMPA',
'probability': 0.01015,
'weight': 0.715,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.375,0.4375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.375,0.4375]},
'synMech': 'AMPA',
'probability': 0.27108,
'weight': 0.6575,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.375,0.4375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.02483,
'weight': 0.6,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.375,0.4375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.01865,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.375,0.4375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.01966,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.375,0.4375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.02269,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.4375,0.5]},
'postConds': {'cellType': 'IT', 'ynorm': [0.375,0.4375]},
'synMech': 'AMPA',
'probability': 0.0367,
'weight': 0.57,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.4375,0.5]},
'postConds': {'cellType': 'IT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.19058,
'weight': 0.66,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.4375,0.5]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.01417,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.4375,0.5]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.01148,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.4375,0.5]},
'postConds': {'cellType': 'IT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.00896,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.4375,0.5]},
'postConds': {'cellType': 'IT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.01049,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5,0.5625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3125,0.375]},
'synMech': 'AMPA',
'probability': 0.00516,
'weight': 0.17,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5,0.5625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.375,0.4375]},
'synMech': 'AMPA',
'probability': 0.06083,
'weight': 0.205,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5,0.5625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.05276,
'weight': 0.24,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5,0.5625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.07207,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5,0.5625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.01464,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5,0.5625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.02666,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5,0.5625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.0189,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5625,0.625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3125,0.375]},
'synMech': 'AMPA',
'probability': 0.02669,
'weight': 0.17,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5625,0.625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.375,0.4375]},
'synMech': 'AMPA',
'probability': 0.05569,
'weight': 0.205,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5625,0.625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.04304,
'weight': 0.24,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5625,0.625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.01716,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5625,0.625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.07207,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5625,0.625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.02512,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5625,0.625]},
'postConds': {'cellType': 'IT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.03215,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.625,0.6875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3125,0.375]},
'synMech': 'AMPA',
'probability': 0.012,
'weight': 0.17,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.625,0.6875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.375,0.4375]},
'synMech': 'AMPA',
'probability': 0.05577,
'weight': 0.205,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.625,0.6875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.04895,
'weight': 0.24,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.625,0.6875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.02604,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.625,0.6875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.02285,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.625,0.6875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.07207,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.625,0.6875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.03437,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.6875,0.75]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3125,0.375]},
'synMech': 'AMPA',
'probability': 0.01128,
'weight': 0.17,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.6875,0.75]},
'postConds': {'cellType': 'IT', 'ynorm': [0.375,0.4375]},
'synMech': 'AMPA',
'probability': 0.03357,
'weight': 0.205,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.6875,0.75]},
'postConds': {'cellType': 'IT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.05406,
'weight': 0.24,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.6875,0.75]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.03109,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.6875,0.75]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.02212,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.6875,0.75]},
'postConds': {'cellType': 'IT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.03198,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.6875,0.75]},
'postConds': {'cellType': 'IT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.07207,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.75,0.8125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.3125,0.375]},
'synMech': 'AMPA',
'probability': 0.02865,
'weight': 0.085,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.75,0.8125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.375,0.4375]},
'synMech': 'AMPA',
'probability': 0.03087,
'weight': 0.1225,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.75,0.8125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.02845,
'weight': 0.16,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.75,0.8125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.02626,
'weight': 0.505,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.75,0.8125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.03999,
'weight': 0.505,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.75,0.8125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.03449,
'weight': 0.505,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.75,0.8125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.03762,
'weight': 0.505,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.75,0.8125]},
'postConds': {'cellType': 'IT', 'ynorm': [0.75,0.8125]},
'synMech': 'AMPA',
'probability': 0.06514,
'weight': 0.5075,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.8125,0.875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.375,0.4375]},
'synMech': 'AMPA',
'probability': 0.10538,
'weight': 0.04,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.8125,0.875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.05033,
'weight': 0.08,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.8125,0.875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.0371,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.8125,0.875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.04348,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.8125,0.875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.07874,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.8125,0.875]},
'postConds': {'cellType': 'IT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.02447,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.875,0.9375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.375,0.4375]},
'synMech': 'AMPA',
'probability': 0.03777,
'weight': 0.04,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.875,0.9375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.03426,
'weight': 0.08,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.875,0.9375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.00944,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.875,0.9375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.01732,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.875,0.9375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.03038,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.875,0.9375]},
'postConds': {'cellType': 'IT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.03983,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.9375,1.0]},
'postConds': {'cellType': 'IT', 'ynorm': [0.375,0.4375]},
'synMech': 'AMPA',
'probability': 0.01306,
'weight': 0.04,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.9375,1.0]},
'postConds': {'cellType': 'IT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.0208,
'weight': 0.08,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.9375,1.0]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.00606,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.9375,1.0]},
'postConds': {'cellType': 'IT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.01059,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.9375,1.0]},
'postConds': {'cellType': 'IT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.01826,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.9375,1.0]},
'postConds': {'cellType': 'IT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.02623,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0,0.0625]},
'postConds': {'cellType': 'PT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 7e-05,
'weight': 0.55,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0,0.0625]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.00152,
'weight': 0.55,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0,0.0625]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.00175,
'weight': 0.22,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0,0.0625]},
'postConds': {'cellType': 'PT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.00834,
'weight': 0.22,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0,0.0625]},
'postConds': {'cellType': 'PT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.00121,
'weight': 0.22,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0,0.0625]},
'postConds': {'cellType': 'PT', 'ynorm': [0.75,0.8125]},
'synMech': 'AMPA',
'probability': 0.0151,
'weight': 0.11,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.0625,0.125]},
'postConds': {'cellType': 'PT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.00834,
'weight': 0.55,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.0625,0.125]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.03265,
'weight': 0.55,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.0625,0.125]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.0344,
'weight': 0.22,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.0625,0.125]},
'postConds': {'cellType': 'PT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.05135,
'weight': 0.22,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.0625,0.125]},
'postConds': {'cellType': 'PT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.02531,
'weight': 0.22,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.125,0.1875]},
'postConds': {'cellType': 'PT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.15193,
'weight': 0.55,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.125,0.1875]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.19617,
'weight': 0.55,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.125,0.1875]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.32257,
'weight': 0.22,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.125,0.1875]},
'postConds': {'cellType': 'PT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.11603,
'weight': 0.22,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.125,0.1875]},
'postConds': {'cellType': 'PT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.04989,
'weight': 0.22,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.125,0.1875]},
'postConds': {'cellType': 'PT', 'ynorm': [0.75,0.8125]},
'synMech': 'AMPA',
'probability': 0.03963,
'weight': 0.11,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.1875,0.25]},
'postConds': {'cellType': 'PT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.11919,
'weight': 0.93,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.1875,0.25]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.12195,
'weight': 1.01,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.1875,0.25]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.06862,
'weight': 1.01,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.1875,0.25]},
'postConds': {'cellType': 'PT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.01836,
'weight': 1.01,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.1875,0.25]},
'postConds': {'cellType': 'PT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.01323,
'weight': 1.01,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.25,0.3125]},
'postConds': {'cellType': 'PT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.06539,
'weight': 0.93,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.25,0.3125]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.06917,
'weight': 1.01,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.25,0.3125]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.03868,
'weight': 1.01,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.25,0.3125]},
'postConds': {'cellType': 'PT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.00778,
'weight': 1.01,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.25,0.3125]},
'postConds': {'cellType': 'PT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.00557,
'weight': 1.01,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.25,0.3125]},
'postConds': {'cellType': 'PT', 'ynorm': [0.75,0.8125]},
'synMech': 'AMPA',
'probability': 0.00954,
'weight': 0.505,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.3125,0.375]},
'postConds': {'cellType': 'PT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.03477,
'weight': 0.54,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.3125,0.375]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.03161,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.3125,0.375]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.01466,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.3125,0.375]},
'postConds': {'cellType': 'PT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.00559,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.3125,0.375]},
'postConds': {'cellType': 'PT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.00364,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.3125,0.375]},
'postConds': {'cellType': 'PT', 'ynorm': [0.75,0.8125]},
'synMech': 'AMPA',
'probability': 0.0032,
'weight': 1.575,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.375,0.4375]},
'postConds': {'cellType': 'PT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.012,
'weight': 0.6,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.375,0.4375]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.02515,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.375,0.4375]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.01581,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.375,0.4375]},
'postConds': {'cellType': 'PT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.0112,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.375,0.4375]},
'postConds': {'cellType': 'PT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.00632,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.375,0.4375]},
'postConds': {'cellType': 'PT', 'ynorm': [0.75,0.8125]},
'synMech': 'AMPA',
'probability': 0.00845,
'weight': 1.0775,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.4375,0.5]},
'postConds': {'cellType': 'PT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.19058,
'weight': 0.66,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.4375,0.5]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.01695,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.4375,0.5]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.02083,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.4375,0.5]},
'postConds': {'cellType': 'PT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.01875,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.4375,0.5]},
'postConds': {'cellType': 'PT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.01068,
'weight': 0.88,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.4375,0.5]},
'postConds': {'cellType': 'PT', 'ynorm': [0.75,0.8125]},
'synMech': 'AMPA',
'probability': 0.02621,
'weight': 0.58,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5,0.5625]},
'postConds': {'cellType': 'PT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.06517,
'weight': 0.24,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5,0.5625]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.07207,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5,0.5625]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.02806,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5,0.5625]},
'postConds': {'cellType': 'PT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.02714,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5,0.5625]},
'postConds': {'cellType': 'PT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.02555,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5,0.5625]},
'postConds': {'cellType': 'PT', 'ynorm': [0.75,0.8125]},
'synMech': 'AMPA',
'probability': 0.04785,
'weight': 0.6,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5625,0.625]},
'postConds': {'cellType': 'PT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.06122,
'weight': 0.24,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5625,0.625]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.02694,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5625,0.625]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.07207,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5625,0.625]},
'postConds': {'cellType': 'PT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.04268,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5625,0.625]},
'postConds': {'cellType': 'PT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.03144,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.5625,0.625]},
'postConds': {'cellType': 'PT', 'ynorm': [0.75,0.8125]},
'synMech': 'AMPA',
'probability': 0.06465,
'weight': 0.6,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.625,0.6875]},
'postConds': {'cellType': 'PT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.05847,
'weight': 0.24,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.625,0.6875]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.03243,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.625,0.6875]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.02506,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.625,0.6875]},
'postConds': {'cellType': 'PT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.07207,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.625,0.6875]},
'postConds': {'cellType': 'PT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.04815,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.625,0.6875]},
'postConds': {'cellType': 'PT', 'ynorm': [0.75,0.8125]},
'synMech': 'AMPA',
'probability': 0.05065,
'weight': 0.6,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.6875,0.75]},
'postConds': {'cellType': 'PT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.11183,
'weight': 0.24,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.6875,0.75]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.04361,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.6875,0.75]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.03592,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.6875,0.75]},
'postConds': {'cellType': 'PT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.03573,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.6875,0.75]},
'postConds': {'cellType': 'PT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.07207,
'weight': 0.71,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.6875,0.75]},
'postConds': {'cellType': 'PT', 'ynorm': [0.75,0.8125]},
'synMech': 'AMPA',
'probability': 0.03327,
'weight': 0.6,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.75,0.8125]},
'postConds': {'cellType': 'PT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.0287,
'weight': 0.16,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.75,0.8125]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.03114,
'weight': 0.505,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.75,0.8125]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.04704,
'weight': 0.505,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.75,0.8125]},
'postConds': {'cellType': 'PT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.064,
'weight': 0.505,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.75,0.8125]},
'postConds': {'cellType': 'PT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.04217,
'weight': 0.505,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.75,0.8125]},
'postConds': {'cellType': 'PT', 'ynorm': [0.75,0.8125]},
'synMech': 'AMPA',
'probability': 0.10083,
'weight': 0.5075,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.8125,0.875]},
'postConds': {'cellType': 'PT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.0842,
'weight': 0.08,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.8125,0.875]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.02139,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.8125,0.875]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.04168,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.8125,0.875]},
'postConds': {'cellType': 'PT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.0791,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.8125,0.875]},
'postConds': {'cellType': 'PT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.05949,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.8125,0.875]},
'postConds': {'cellType': 'PT', 'ynorm': [0.75,0.8125]},
'synMech': 'AMPA',
'probability': 0.06274,
'weight': 0.415,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.875,0.9375]},
'postConds': {'cellType': 'PT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.01194,
'weight': 0.08,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.875,0.9375]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.01487,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.875,0.9375]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.01159,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.875,0.9375]},
'postConds': {'cellType': 'PT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.01603,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.875,0.9375]},
'postConds': {'cellType': 'PT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.02624,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.875,0.9375]},
'postConds': {'cellType': 'PT', 'ynorm': [0.75,0.8125]},
'synMech': 'AMPA',
'probability': 0.02597,
'weight': 0.415,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.9375,1.0]},
'postConds': {'cellType': 'PT', 'ynorm': [0.4375,0.5]},
'synMech': 'AMPA',
'probability': 0.03389,
'weight': 0.08,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.9375,1.0]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5,0.5625]},
'synMech': 'AMPA',
'probability': 0.00614,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.9375,1.0]},
'postConds': {'cellType': 'PT', 'ynorm': [0.5625,0.625]},
'synMech': 'AMPA',
'probability': 0.0087,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.9375,1.0]},
'postConds': {'cellType': 'PT', 'ynorm': [0.625,0.6875]},
'synMech': 'AMPA',
'probability': 0.01269,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.9375,1.0]},
'postConds': {'cellType': 'PT', 'ynorm': [0.6875,0.75]},
'synMech': 'AMPA',
'probability': 0.0154,
'weight': 0.3,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'cellType': ['IT','PT','CT'], 'ynorm': [0.9375,1.0]},
'postConds': {'cellType': 'PT', 'ynorm': [0.75,0.8125]},
'synMech': 'AMPA',
'probability': 0.01161,
'weight': 0.415,
'delay': 'defaultDelay+dist_3D/propVelocity'})


netParams.addConnParams(None, {'preConds': {'pop': 'IT_L23'},
'postConds': {'pop': 'SOM_L23'},
'synMech': 'AMPA',
'probability': 0.18713,
'weight': 0.78,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': 'IT_L23'},
'postConds': {'pop': 'SOM_L5'},
'synMech': 'AMPA',
'probability': 0.21712,
'weight': 1.01,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': ['IT_L4','IT_L5A','IT_L5B','PT_L5B']},
'postConds': {'pop': 'SOM_L23'},
'synMech': 'AMPA',
'probability': 0.02222,
'weight': 0.3625,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': ['IT_L4','IT_L5A','IT_L5B','PT_L5B']},
'postConds': {'pop': 'SOM_L5'},
'synMech': 'AMPA',
'probability': 0.03494,
'weight': 0.1225,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': ['IT_L4','IT_L5A','IT_L5B','PT_L5B']},
'postConds': {'pop': 'SOM_L6'},
'synMech': 'AMPA',
'probability': 0.01553,
'weight': 0.4375,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': ['IT_L6','CT_L6']},
'postConds': {'pop': 'SOM_L5'},
'synMech': 'AMPA',
'probability': 0.02485,
'weight': 0.24786,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': ['IT_L6','CT_L6']},
'postConds': {'pop': 'SOM_L6'},
'synMech': 'AMPA',
'probability': 0.02343,
'weight': 0.53,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': 'IT_L23'},
'postConds': {'pop': 'PV_L23'},
'synMech': 'AMPA',
'probability': 0.18713,
'weight': 0.78,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': 'IT_L23'},
'postConds': {'pop': 'PV_L5'},
'synMech': 'AMPA',
'probability': 0.01996,
'weight': 0.11,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': ['IT_L4','IT_L5A','IT_L5B','PT_L5B']},
'postConds': {'pop': 'PV_L23'},
'synMech': 'AMPA',
'probability': 0.02222,
'weight': 0.3625,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': ['IT_L4','IT_L5A','IT_L5B','PT_L5B']},
'postConds': {'pop': 'PV_L5'},
'synMech': 'AMPA',
'probability': 0.19058,
'weight': 1.0775,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': ['IT_L4','IT_L5A','IT_L5B','PT_L5B']},
'postConds': {'pop': 'PV_L6'},
'synMech': 'AMPA',
'probability': 0.01553,
'weight': 0.4375,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': ['IT_L6','CT_L6']},
'postConds': {'pop': 'PV_L5'},
'synMech': 'AMPA',
'probability': 0.02485,
'weight': 0.24786,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': ['IT_L6','CT_L6']},
'postConds': {'pop': 'PV_L6'},
'synMech': 'AMPA',
'probability': 0.02343,
'weight': 0.53,
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': 'SOM_L23'},
'postConds': {'ynorm': [0.12,0.31]},
'synMech': 'GABAB',
'probability': '1.0 * exp(-dist_3D/probLambda)',
'weight': 'ItoIweight',
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': 'SOM_L5'},
'postConds': {'ynorm': [0.31,0.77]},
'synMech': 'GABAB',
'probability': '1.0 * exp(-dist_3D/probLambda)',
'weight': 'ItoIweight',
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': 'SOM_L6'},
'postConds': {'ynorm': [0.77,1.0]},
'synMech': 'GABAB',
'probability': '1.0 * exp(-dist_3D/probLambda)',
'weight': 'ItoIweight',
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': 'PV_L23'},
'postConds': {'ynorm': [0.12,0.31]},
'synMech': 'GABAA',
'probability': '1.0 * exp(-dist_3D/probLambda)',
'weight': 'ItoIweight',
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': 'PV_L5'},
'postConds': {'ynorm': [0.31,0.77]},
'synMech': 'GABAA',
'probability': '1.0 * exp(-dist_3D/probLambda)',
'weight': 'ItoIweight',
'delay': 'defaultDelay+dist_3D/propVelocity'})

netParams.addConnParams(None, {'preConds': {'pop': 'PV_L6'},
'postConds': {'ynorm': [0.77,1.0]},
'synMech': 'GABAA',
'probability': '1.0 * exp(-dist_3D/probLambda)',
'weight': 'ItoIweight',
'delay': 'defaultDelay+dist_3D/propVelocity'})



# Dictionary of annotations
netParams.annots = {}
