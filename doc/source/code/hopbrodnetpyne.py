# execfile('hopbrodnetpyne.py')
# notebook: ~/nrniv/notebooks/nbnetpyne.dol
from netpyne import sim
netParams, simConfig, simConfig['analysis'] = {}, {}, {}
for key in ['popParams', 'cellParams', 'synMechParams', 'connParams']: netParams[key] = []
netParams['stimParams'] = {'sourceList': [], 'stimList': []}

# Network and connections
netParams['popParams'].extend([{'popLabel': 'hop', 'cellType': 'PYR', 'cellModel': 'HH', 'numCells': 1}])
netParams['connParams'].extend([{'preTags': {'popLabel': 'hop'}, 'postTags': {'popLabel': 'hop'}, 'weight': 0.0, 'synMech': 'inh', 'delay': 5}])
netParams['stimParams']['sourceList'].append({'label': 'bg', 'type': 'IClamp', 'delay': 10, 'dur': int(1000), 'amp': 0.5})

# cells
netParams['cellParams'].append(
  {'label': 'hh_PYR', 
   'conds': {'cellType': 'PYR'}, # could have complex rule here for eg PYR cells in certain loc with particular implementation
   'secs': {'soma': {'geom' :  {'diam': 5, 'L': 5}, 'vinit' : -70.6, 
                         'mechs':  {'hh' : {'gnabar': 0.10, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}}}}}) 
netParams['synMechParams'].extend([{'label': 'exc', 'mod': 'Exp2Syn', 'tau2': 1.0, 'e': 0},
                                   {'label': 'inh', 'mod': 'Exp2Syn', 'tau2': 1.0, 'e': -80}])
netParams['stimParams']['stimList'].append(  {'source': 'bg', 'sec':'soma', 'loc': 0.5, 'conds': {'popLabel':'hop'}})

# Simulation parameters
simConfig['duration'] = 500     # Duration of the simulation, in ms
simConfig['recordTraces'] = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}
                          #'ik_soma':{'sec':'soma','loc':0.5,'var':'ik'}}
                          #'exc_soma':{'sec':'soma','synMech':'exc', 'loc':0.5,'var':'i'}}  # Dict with traces to record
simConfig['analysis']['plotTraces']={'include': [0]}

# Create network and run simulation
def create ():
  global pops,cells
  sim.initialize(netParams, simConfig)
  pops = sim.net.createPops()                      # instantiate network populations
  cells = sim.net.createCells()                     # instantiate network cells based on defined populations
  sim.net.addStims()
  sim.net.connectCells()                    # create connections between cells based on params
  sim.setupRecording()                      # setup variables to record for each cell (spikes, V traces, etc)

def run (): sim.simulate()
def plot (): sim.analysis.plotData()

# Interacting with network
def changeWeights(net, newWeight):
    netcons = [conn['hNetcon'] for cell in net.cells for conn in cell.conns]
    for netcon in netcons: 
      netcon.weight[0] = newWeight


create()
run()
# sim.analysis.plotRaster()
# sim.analysis.plotRaster(syncLines=True)
sim.analysis.plotData()
changeWeights(sim.net, 0.5)  # increase inh conns weight increase sync

