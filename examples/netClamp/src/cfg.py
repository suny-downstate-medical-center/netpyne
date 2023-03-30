import imp
from netpyne import specs

# Simulation options
cfg = specs.SimConfig()        # object of class simConfig to store simulation configuration

cfg.duration = 1*1e3           # Duration of the simulation, in ms
cfg.dt = 0.05                 # Internal integration timestep to use
cfg.verbose = False            # Show detailed messages
cfg.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
cfg.recordStep = 1             # Step size in ms to save data (e.g. V traces, LFP, etc)
cfg.filename = 'model_output'  # Set file output name
cfg.saveJson = True  # Save params, network and sim output to pickle file
cfg.recordStim = True  # required for netClamp to work

cfg.analysis['plotRaster'] = {'orderBy': 'y', 'orderInverse': True}      # Plot a raster
cfg.analysis['plotTraces'] = {'include': [5]}      # Plot recorded traces for this list of cells