"""
params.py 

netParams is a dict containing a set of network parameters using a standardized structure

simConfig is a dict containing a set of simulation configurations using a standardized structure

Contributors: salvadordura@gmail.com
"""

from netpyne import specs

###############################################################################
# NETWORK PARAMETERS
###############################################################################

netParams = specs.NetParams()  # object of class NetParams to store the network parameters

# Population parameters
netParams.addPopParams('hop', {'cellType': 'PYR', 'cellModel': 'HH', 'numCells': 50}) # add dict with params for this pop 
netParams.addPopParams('background', {'cellModel': 'NetStim', 'rate': 50, 'noise': 0.5})  # background inputs

# Cell parameters

## PYR cell properties
cellRule = {'conds': {'cellType': 'PYR'},  'secs': {}}
cellRule['secs']['soma'] = {'geom': {}, 'topol': {}, 'mechs': {}}  # soma properties
cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8}
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} 
netParams.addCellParams('PYR', cellRule)  # add dict to list of cell properties

# Synaptic mechanism parameters
netParams.addSynMechParams('exc', {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': 0})
netParams.addSynMechParams('inh', {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': -80})

 
# Connectivity parameters
netParams.addConnParams('bg->hop',
    {'preConds': {'popLabel': 'background'}, 'postConds': {'popLabel': 'hop'}, # background -> PYR
    'weight': 0.1,                    # fixed weight of 0.1
    'synMech': 'exc',                 # target exc synapse
    'delay': 1})                      # uniformly distributed delays between 1-5ms

netParams.addConnParams('hop->hop',
    {'preConds': {'popLabel': 'hop'}, 'postConds': {'popLabel': 'hop'},
    'weight': 0.0,                      # weight of each connection
    'synMech': 'inh',                   # target inh synapse
    'delay': 5})       				    # delay 


###############################################################################
# SIMULATION PARAMETERS
###############################################################################
simConfig = specs.SimConfig()  # object of class SimConfig to store simulation configuration

# Simulation options
simConfig.duration = 0.5*1e3 		# Duration of the simulation, in ms
simConfig.dt = 0.025 				# Internal integration timestep to use
simConfig.verbose = False  			# Show detailed messages 
simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
simConfig.recordStep = 1 			# Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'model_output'  # Set file output name
simConfig.savePickle = False 		# Save params, network and sim output to pickle file

simConfig.addAnalysis('plotRaster', {'syncLines': True})      # Plot a raster
simConfig.addAnalysis('plotTraces', {'include': [1]})      # Plot recorded traces for this list of cells
simConfig.addAnalysis('plot2Dnet', True)           # plot 2D visualization of cell positions and connections


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








