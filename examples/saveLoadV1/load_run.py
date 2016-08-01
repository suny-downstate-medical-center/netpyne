from netpyne import specs, sim

###############################################################################
# SIMULATION CONFIGURATION
###############################################################################

simConfig = specs.SimConfig()                # object of class SimConfig to store simulation configuration

simConfig.duration = 50                      # Duration of the simulation, in ms
simConfig.dt = 0.05                           # Internal integration timestep, in ms
simConfig.createNEURONObj = True             # create HOC objects when instantiating network
simConfig.createPyStruct = True              # create Python structure (simulator-independent) when instantiating network

# Recording
simConfig.recordStep = 0.1                                  # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.recordTraces = {'V_soma': {'sec': 'soma_0', 'loc': 0.5, 'var': 'v'},
                        'V_dend6': {'sec': 'dend_6', 'loc': 0.5, 'var': 'v'}}   # Dict with traces to record

# Analysis
simConfig.addAnalysis('plotRaster', {'orderBy': 'y', 'orderInverse': True})      		# Plot a raster
simConfig.addAnalysis('plotTraces', {'include': [('L2_E', 0), ('L5_IF', 0)]})           # Plot recorded traces for this list of cells
simConfig.addAnalysis('plot2Dnet', {'include': ['L2_E', 'L4_E']})                       # plot 2D visualization of cell positions and connections
simConfig.addAnalysis('plotConn', True)                                               	# plot connectivity matrix


###############################################################################
# LOAD, RUN AND ANALYZE NETWORK
###############################################################################

sim.loadSimulateAnalyze(filename='V1.json', simConfig=simConfig)    
