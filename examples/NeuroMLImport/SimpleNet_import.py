
from netpyne import sim
from netpyne import specs 


nml2_file_name = 'SimpleNet.net.nml'

simConfig = specs.SimConfig()  # dictionary to store simConfig

# Simulation parameters
simConfig.duration = 10000 # Duration of the simulation, in ms
simConfig.dt = 0.025 # Internal integration timestep to use
simConfig.verbose = True

simConfig.recordCells = ['all']  # which cells to record from
simConfig.recordTraces = {'Vsoma':{'sec':'soma','loc':0.5,'var':'v'}}
simConfig.filename = 'SimpleNet'  # Set file output name
simConfig.saveDat = True # save traces


simConfig.plotRaster = True # Whether or not to plot a raster
simConfig.plotCells = ['all'] # plot recorded traces for this list of cells

sim.importNeuroML2SimulateAnalyze(nml2_file_name,simConfig)
