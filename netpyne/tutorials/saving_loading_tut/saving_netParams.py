from netpyne import specs, sim

from __main__ import cfg

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

## Cell parameters
PYRcell = {'secs': {}}
PYRcell['secs']['soma'] = {'geom': {}, 'mechs': {}}
PYRcell['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}
PYRcell['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}
netParams.cellParams['PYR'] = PYRcell

## Population parameters
netParams.popParams['S'] = {'cellType': 'PYR', 'numCells': 20}
netParams.popParams['M'] = {'cellType': 'PYR', 'numCells': 20}

## Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': cfg.synMechTau2, 'e': 0}

# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.5}
netParams.stimTargetParams['bkg->PYR'] = {
    'source': 'bkg',
    'conds': {'cellType': 'PYR'},
    'weight': 0.01,
    'delay': 5,
    'synMech': 'exc',
}

## Cell connectivity rules
netParams.connParams['S->M'] = {
    'preConds': {'pop': 'S'},
    'postConds': {'pop': 'M'},
    'probability': 0.5,
    'weight': cfg.connWeight,
    'delay': 5,
    'synMech': 'exc',
}
