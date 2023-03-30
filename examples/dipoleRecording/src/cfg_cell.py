from netpyne import specs

# Simulation options
cfg = specs.SimConfig()        # object of class SimConfig to store simulation configuration
cfg.duration = 0.05*1e3           # Duration of the simulation, in ms
cfg.dt = 0.1                # Internal integration timestep to use
cfg.verbose = False            # Show detailed messages
cfg.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}
cfg.recordStep = 1             # Step size in ms to save data (eg. V traces, LFP, etc)
cfg.filename = 'cell_dipole'  # Set file output name

cfg.recordDipole = True
cfg.saveDipoleCells = ['all']
cfg.saveDipolePops = ['E']


cfg.analysis['plotTraces'] = {'include': [('E',0)], 'oneFigPer':'cell', 'overlay': True, 'figSize': (5,3),'saveFig': True}      # Plot recorded traces for this list of cells
#cfg.analysis['plotLFP'] = {'includeAxon': False, 'plots': ['timeSeries',  'locations'], 'figSize': (5,9), 'saveFig': True}
#cfg.analysis['getCSD'] = {'timeRange': [10,45],'spacing_um': 150, 'vaknin': True}
#cfg.analysis['plotCSD'] = {'timeRange': [10,45]}
#sim.analysis.getCSD(...args...)
#cfg.analysis['plotCSD'] = {}