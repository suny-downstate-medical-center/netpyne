"""
cfg.py

Example of saving different network components to file

cfg is an object containing a set of simulation configurations using a standardized structure
"""

from netpyne import specs

cfg = specs.SimConfig()   # object of class SimConfig to store the simulation configuration

# -----------------------------------------------------------------------------
# SIMULATION PARAMETERS
# -----------------------------------------------------------------------------

# Simulation parameters
cfg.duration = 1*1e3 # Duration of the simulation, in ms
cfg.dt = 0.025 # Internal integration timestep to use
cfg.seeds = {'conn': 1, 'stim': 1, 'loc': 1} # Seeds for randomizers (connectivity, input stimulation and cell locations)
cfg.createNEURONObj = 1  # create HOC objects when instantiating network
cfg.createPyStruct = 1  # create Python structure (simulator-independent) when instantiating network
cfg.verbose = False  # show detailed messages
cfg.saveCellSecs = False  # avoid saving detailed info about each cell's morphology and mechanisms
cfg.simLabel = 'output'

# Recording
cfg.recordTraces = {'Vsoma':{'sec':'soma','loc':0.5,'var':'v'}}
cfg.recordStim = True  # record spikes of cell stims
cfg.recordStep = 0.1 # Step size in ms to save data (eg. V traces, LFP, etc)

# Analysis and plotting
cfg.analysis['plotRaster'] = {'saveFig': 'out_raster.png'}  # Plot raster
cfg.analysis['plotTraces'] = {'include': [0], 'saveFig': 'out_V_cell0.png'}  # Plot raster
cfg.analysis['plot2Dnet'] = {'saveFig': 'out_net2D.png', 'figSize': (8,8)}  # Plot 2D net cells and connections
