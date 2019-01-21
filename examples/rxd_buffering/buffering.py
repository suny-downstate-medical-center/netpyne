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
netParams.rxdParams['regions'] = {'cyt': {'cells': 'all', 'secs': 'all', 'nrn_region': 'i'}}

### species 
species = {}
species['ca'] = {'regions': ['cyt'], 'charge': 2, 'initial': 1}
species['buf'] = {'regions': ['cyt'], 'initial': 1}
species['cabuf'] = {'regions': ['cyt'], 'initial': 0}
netParams.rxdParams['species'] = species

### reactions
kf = 1
kb = 0.1
netParams.rxdParams['reactions'] = {'buffering': {'reactant': '2 * ca + buf', 'product': 'cabuf', 'rate_f': kf, 'rate_b': kb}}


#------------------------------------------------------------------------------
# SIMULATION CONFIGURATION#
#------------------------------------------------------------------------------

# Run parameters
cfg = specs.SimConfig()       # object of class cfg to store simulation configuration
cfg.duration = 100            # Duration of the simulation, in ms
cfg.recordTraces = {'ca': {'sec': 'soma', 'loc': 0.5, 'var': 'cai'},
                    'buf': {'sec': 'soma', 'loc': 0.5, 'var': 'bufi'},
                    'cabuf': {'sec': 'soma', 'loc': 0.5, 'var': 'cabufi'}}


cfg.analysis['plotTraces'] = {'include': ['cell'], 'overlay': True}


#------------------------------------------------------------------------------
# RUN MODEL
#------------------------------------------------------------------------------
sim.createSimulateAnalyze(netParams,cfg)


