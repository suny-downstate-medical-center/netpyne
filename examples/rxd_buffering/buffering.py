from neuron import h
from netpyne import specs, sim



#------------------------------------------------------------------------------
# NETWORK PARAMETERS
#------------------------------------------------------------------------------
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
species['kbuf'] = {'regions': ['cyt'], 'initial': 0}
species['k'] = {'regions': ['cyt'], 'd': 1.0, 'initial': 0.1, 'charge': 1} 

netParams.rxdParams['species'] = species

### reactions
kf = 1e6
kb = 1e-2
#netParams.rxdParams['reactions'] = {'buffering': {'reactant': '2 * ca + buf', 'product': 'cabuf', 'rate_f': kf, 'rate_b': kb}}
reactions = {}
reactions['buffering'] = {'reactant': 'k+buf', 'product': 'kbuf', 'rate_f': '0.0008/(1+rxdmath.pow(2.71828,((7.5-k)/1.15)))','rate_b': 0.0008}
netParams.rxdParams['reactions'] = reactions

### rates
netParams.rxdParams['rates'] = {'degradation': {'species': 'buf', 'rate': '-1e-3 * buf'}}



#------------------------------------------------------------------------------
# SIMULATION CONFIGURATION#
#------------------------------------------------------------------------------

# Run parameters
cfg = specs.SimConfig()       # object of class cfg to store simulation configuration
cfg.duration = 500            # Duration of the simulation, in ms
cfg.recordTraces = {'k': {'sec': 'soma', 'loc': 0.5, 'var': 'cai'},
                    'buf': {'sec': 'soma', 'loc': 0.5, 'var': 'bufi'},
                    'cabuf': {'sec': 'soma', 'loc': 0.5, 'var': 'cabufi'}}


cfg.analysis['plotTraces'] = {'include': ['cell'], 'ylim':[0, 0.0001], 'overlay': True}


#------------------------------------------------------------------------------
# RUN MODEL
#------------------------------------------------------------------------------
sim.create(netParams,cfg)
sim.simulate()
sim.analyze()


