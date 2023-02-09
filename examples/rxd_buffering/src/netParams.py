import imp
from netpyne import specs

netParams = specs.NetParams()  # object of class NetParams to store the network parameters

## Population parameters
netParams.popParams['cell'] = {'numCells': 1, 'cellModel': 'HH'}

## Cell property rules
netParams.cellParams['PYR'] = {'conds': {'cellModel': 'HH'},  'secs': {'soma': {}}}   # cell rule dict


## RxD params
### regions
netParams.rxdParams['regions'] = {'cyt': {'cells': ['all'], 'secs': 'soma', 'nrn_region': 'i'}}

### species
species = {}
species['ca'] = {'regions': ['cyt'], 'charge': 2, 'initial': 1e-4}
species['buf'] = {'regions': ['cyt'], 'initial': 1e-4}
species['cabuf'] = {'regions': ['cyt'], 'initial': 0}
netParams.rxdParams['species'] = species

### reactions
kf = 1e6
kb = 1e-2
netParams.rxdParams['reactions'] = {'buffering': {'reactant': '2 * ca + buf', 'product': 'cabuf', 'rate_f': kf, 'rate_b': kb}}

### rates
netParams.rxdParams['rates'] = {'degradation': {'species': 'buf', 'rate': '-1e-3 * buf'}}