"""
params.py 

netParams is a dict containing a set of network parameters using a standardized structure

simConfig is a dict containing a set of simulation configurations using a standardized structure

Contributors: salvadordura@gmail.com
"""

###############################################################################
# NETWORK PARAMETERS
###############################################################################

netParams = {}  # dictionary to store sets of network parameters

# Population parameters
netParams['popParams'] = []  # create list of populations - each item will contain dict with pop params
netParams['popParams'].append({'popLabel': 'hop', 'cellType': 'PYR', 'cellModel': 'HH', 'numCells': 50}) # add dict with params for this pop 
netParams['popParams'].append({'popLabel': 'background', 'cellModel': 'NetStim', 'rate': 50, 'noise': 0.5, 'source': 'random'})  # background inputs

# Cell parameters
netParams['cellParams'] = []

## PYR cell properties
cellRule = {'label': 'PYR', 'conditions': {'cellType': 'PYR'},  'sections': {}}
soma = {'geom': {}, 'topol': {}, 'mechs': {}}  # soma properties
soma['geom'] = {'diam': 18.8, 'L': 18.8}
soma['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} 
cellRule['sections'] = {'soma': soma}  # add sections to dict
netParams['cellParams'].append(cellRule)  # add dict to list of cell properties

# Synaptic mechanism parameters
netParams['synMechParams'] = []
netParams['synMechParams'].append({'label': 'exc', 'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': 0})
netParams['synMechParams'].append({'label': 'inh', 'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': -80})

 
# Connectivity parameters
netParams['connParams'] = []  

netParams['connParams'].append(
    {'preTags': {'popLabel': 'background'}, 'postTags': {'popLabel': 'hop'}, # background -> PYR
    'weight': 0.1,                    # fixed weight of 0.08
    'synMech': 'exc',                 # target exc synapse
    'delay': 1})                      # uniformly distributed delays between 1-5ms

netParams['connParams'].append(
    {'preTags': {'popLabel': 'hop'}, 'postTags': {'popLabel': 'hop'},
    'weight': 0.0,                      # weight of each connection
    'synMech': 'inh',                   # target inh synapse
    'delay': 5})       				    # delay 


###############################################################################
# SIMULATION PARAMETERS
###############################################################################
simConfig = {}  # dictionary to store simConfig

# Simulation options
simConfig = {}
simConfig['duration'] = 0.5*1e3 		# Duration of the simulation, in ms
simConfig['dt'] = 0.025 				# Internal integration timestep to use
simConfig['verbose'] = False  			# Show detailed messages 
simConfig['recordTraces'] = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
simConfig['recordStep'] = 1 			# Step size in ms to save data (eg. V traces, LFP, etc)
simConfig['filename'] = 'model_output'  # Set file output name
simConfig['savePickle'] = False 		# Save params, network and sim output to pickle file

simConfig['analysis'] = {}
simConfig['analysis']['plotRaster'] = {'syncLines': True}      # Plot a raster
simConfig['analysis']['plotTraces'] = {'include': [1]}      # Plot recorded traces for this list of cells
simConfig['analysis']['plot2Dnet'] = True           # plot 2D visualization of cell positions and connections



###############################################################################
# EXECUTION CODE (via netpyne)
###############################################################################
from netpyne import sim

# Create network and run simulation
sim.initialize(                       # create network object and set cfg and net params
    simConfig = simConfig,   # pass simulation config and network params as arguments
    netParams = netParams)   
sim.net.createPops()                      # instantiate network populations
sim.net.createCells()                     # instantiate network cells based on defined populations
sim.net.connectCells()                    # create connections between cells based on params
sim.setupRecording()                  # setup variables to record for each cell (spikes, V traces, etc)
sim.runSim()                          # run parallel Neuron simulation  
sim.gatherData()                      # gather spiking data and cell info from each node
sim.saveData()                        # save params, cell info and sim output to file (pickle,mat,txt,etc)
sim.analysis.plotData()                   # plot spike raster


# ###############################################################################
# # INTERACTING WITH INSTANTIATED NETWORK
# ###############################################################################

def changeWeights(net, newWeight):
    netcons = [conn['hNetcon'] for cell in net.cells for conn in cell.conns]
    for netcon in netcons: 
        netcon.weight[0] = newWeight


changeWeights(sim.net, 0.5)  # increase inh conns weight increase sync

sim.runSim()                          # run parallel Neuron simulation  
sim.gatherData()                      # gather spiking data and cell info from each node
sim.saveData()                        # save params, cell info and sim output to file (pickle,mat,txt,etc)
sim.analysis.plotData()                   # plot spike raster








