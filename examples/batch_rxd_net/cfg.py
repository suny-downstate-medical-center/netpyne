from netpyne import specs

#------------------------------------------------------------------------------
#
# SIMULATION CONFIGURATION
#
#------------------------------------------------------------------------------

# Run parameters
cfg = specs.SimConfig()       # object of class cfg to store simulation configuration
cfg.duration = 1.0*1e3        # Duration of the simulation, in ms
cfg.hParams['v_init'] = -65   # set v_init to -65 mV
cfg.dt = 0.1                  # Internal integration timestep to use
cfg.verbose = False            # Show detailed messages
cfg.recordStep = 1             # Step size in ms to save data (eg. V traces, LFP, etc)
cfg.filename = 'rxd_net'   # Set file output name
cfg.saveJson = True
cfg.saveDataInclude = ['simData', 'simConfig', 'netParams', 'net']

 # Network dimensions
cfg.sizeX = 100
cfg.sizeY = 500
cfg.sizeZ = 100

# Recording/plotting parameters
cfg.recordTraces = {'V_soma':{'sec': 'soma','loc': 0.5,'var': 'v'},
                          'ik_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'ik'},
                          'cai_soma': {'sec': 'soma', 'loc':0.5, 'var': 'cai'},
                          'cao_soma': {'sec': 'soma', 'loc':0.5, 'var': 'cao'}}

cfg.recordLFP = [[-15, y, 1.0*cfg.sizeZ] for y in range(int(cfg.sizeY/3), int(cfg.sizeY), int(cfg.sizeY/3))]

cfg.analysis['plotTraces']={'include': [0], 'saveFig' : False}
cfg.analysis['plotRaster'] = {'orderBy': 'y', 'orderInverse': True, 'saveFig': False, 'figSize': (9,3)}      # Plot a raster
cfg.analysis['plotLFP'] = {'includeAxon': False, 'figSize': (6,10), 'NFFT': 256, 'noverlap': 48, 'nperseg': 64, 'saveFig': False}
# cfg.analysis['plotRxDConcentration'] = {'speciesLabel': 'ca', 'regionLabel': 'ecs', 'saveFig' : False}

# parameters
## Change ip3_init from 0 to 0.1 to observe multiscale effect:
## high ip3 -> ER Ca released to Cyt -> kBK channels open -> less firing
cfg.ip3_init = 0.0
cfg.gip3r = 12040 * 100
