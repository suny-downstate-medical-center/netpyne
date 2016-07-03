# # execfile('hopbrodnetpyne.py')
# from netpyne import sim
# netParams, simConfig = {}, {}
# for key in ['popParams', 'cellParams', 'synMechParams', 'connParams']: netParams[key] = []

# # NETWORK PARAMETERS
# netParams['popParams'].extend([{'popLabel': 'hop', 'cellType': 'PYR', 'cellModel': 'HH', 'numCells': 50},
#                                {'popLabel': 'background', 'cellModel': 'NetStim', 'rate': 50, 'noise': 0.5, 'source': 'random'}])  # background inputs
# ## set up the cell and synapses
# netParams['cellParams'].append(
#   {'label': 'PYR', 
#    'conditions': {'cellType': 'PYR'}, # could have complex rule here for eg PYR cells in certain loc with particular implementation
#    'sections': {'soma': {'geom' :  {'diam': 18.8, 'L': 18.8},
#                          'mechs':  {'hh' : {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}}}}}) 
# netParams['synMechParams'].extend([{'label': 'exc', 'mod': 'Exp2Syn', 'tau2': 1.0, 'e': 0},
#                                    {'label': 'inh', 'mod': 'Exp2Syn', 'tau2': 1.0, 'e': -80}])

# # Connectivity parameters
# netParams['connParams'].extend([{'preTags': {'popLabel': 'background'}, 'postTags': {'popLabel': 'hop'}, # background to drive cells
#                                  'weight': 0.1, 'synMech': 'exc', 'delay': 1},
#                                 {'preTags': {'popLabel': 'hop'}, 'postTags': {'popLabel': 'hop'},        # all to all
#                                  'weight': 0.0, 'synMech': 'inh', 'delay': 5}])

# # Simulation parameters
# simConfig['duration'] = 500 		# Duration of the simulation, in ms
# simConfig['recordTraces'] = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record

# # Create network and run simulation
# def create ():
#   sim.initialize(netParams, simConfig)
#   pops = sim.net.createPops()                      # instantiate network populations
#   cells = sim.net.createCells()                     # instantiate network cells based on defined populations
#   sim.net.connectCells()                    # create connections between cells based on params
#   sim.setupRecording()                      # setup variables to record for each cell (spikes, V traces, etc)

# def run (): sim.simulate()

# # Interacting with network
# def changeWeights(net, newWeight):
#     netcons = [conn['hNetcon'] for cell in net.cells for conn in cell.conns]
#     for netcon in netcons: 
#       netcon.weight[0] = newWeight

# '''
# create()
# run()
# sim.analysis.plotRaster()
# sim.analysis.plotRaster(syncLines=True)
# changeWeights(sim.net, 0.5)  # increase inh conns weight increase sync
# '''



# execfile('hopbrodnetpyne.py')
# notebook: ~/nrniv/notebooks/nbnetpyne.dol
from netpyne import sim
netParams, simConfig, simConfig['analysis'] = {}, {}, {}
for key in ['popParams', 'cellParams', 'synMechParams', 'connParams']: netParams[key] = []
netParams['stimParams'] = {'sourceList': [], 'stimList': []}

# Network and connections
netParams['popParams'].extend([{'popLabel': 'hop', 'cellType': 'PYR', 'cellModel': 'HH', 'numCells': 50}])
netParams['connParams'].extend([{'preTags': {'popLabel': 'hop'}, 'postTags': {'popLabel': 'hop'}, 'weight': 0.0, 'synMech': 'inh', 'delay': 5}])
netParams['stimParams']['sourceList'].append({'label': 'bg', 'type': 'IClamp', 'delay': 10, 'dur': int(1e9), 'amp': 'uniform(0.8,1.0)'})

# cells
netParams['cellParams'].append(
  {'label': 'hh_PYR', 
   'conditions': {'cellType': 'PYR'}, # could have complex rule here for eg PYR cells in certain loc with particular implementation
   'sections': {'soma': {'geom' :  {'diam': 18.8, 'L': 18.8},
                         'mechs':  {'hh' : {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}},
                         'vinit': -70}}}) 
netParams['synMechParams'].extend([{'label': 'exc', 'mod': 'Exp2Syn', 'tau2': 1.0, 'e': 0},
                                   {'label': 'inh', 'mod': 'Exp2Syn', 'tau2': 1.0, 'e': -80}])
netParams['stimParams']['stimList'].append(  {'source': 'bg', 'sec':'soma', 'loc': 0.5, 'conditions': {'popLabel':'PYR'}})

# Simulation parameters
simConfig['duration'] = 500     # Duration of the simulation, in ms
simConfig['recordTraces'] = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
#simConfig['recordCells'] = [5]
#simConfig['analysis']['plotTraces']={'include': [1]}

# Create network and run simulation
def create ():
  global pops,cells
  sim.initialize(netParams, simConfig)
  pops = sim.net.createPops()                      # instantiate network populations
  cells = sim.net.createCells()                     # instantiate network cells based on defined populations
  sim.net.connectCells()                    # create connections between cells based on params
  sim.setupRecording()                      # setup variables to record for each cell (spikes, V traces, etc)

def run (): sim.simulate()

# Interacting with network
def changeWeights(net, newWeight):
    netcons = [conn['hNetcon'] for cell in net.cells for conn in cell.conns]
    for netcon in netcons: 
      netcon.weight[0] = newWeight


create()
run()

#sim.cfg['analysis']['plotTraces']={'include': [5], ''}
# sim.setupRecording()
# run()
# sim.analysis.plotData()


sim.analysis.plotTraces(include=[5], rerun=True)
#sim.analysis.plotData()
#sim.analysis.plotRaster()
#sim.analysis.plotRaster(syncLines=True)
changeWeights(sim.net, 0.5)  # increase inh conns weight increase sync

