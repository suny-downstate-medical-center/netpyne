from netpyne import specs

# Network parameters
netParams = specs.NetParams()  # object of class NetParams to store the network parameters

## Population parameters
numCells = 2
netParams.popParams['IT5B'] = {'numCells': numCells, 'cellType': 'IT', 'cellModel': 'HH', }

## Cell property rules
netParams.loadCellParamsRule(label='IT5B_reduced', fileName='cells/IT5B_reduced_cellParams.pkl')
netParams.cellParams['IT5B_reduced']['conds'] = {'cellType': 'IT'}

## Synaptic mechanism parameters
netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # excitatory synaptic mechanism


netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.0}
netParams.stimTargetParams['bg1'] = {'source': 'bkg',
									'conds': {'pop': 'IT5B'},
									'weight': 0.1,
									'delay': 5,
									'sec': ['soma', 'Adend1', 'Adend2', 'Adend3', 'Bdend'],
									'synsPerConn': 3}