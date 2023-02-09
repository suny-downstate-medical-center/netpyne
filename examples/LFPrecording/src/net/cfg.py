from netpyne import specs
from netParams import netParams # TODO: this workaround ignores the path to netParams specified in index.npjson (wouldn't work if changed)

# Simulation configuration
cfg = specs.SimConfig()        # object of class SimConfig to store simulation configuration
cfg.duration = 1.0*1e3           # Duration of the simulation, in ms
cfg.dt = 0.1                # Internal integration timestep to use
cfg.verbose = False            # Show detailed messages
cfg.recordStep = 1             # Step size in ms to save data (eg. V traces, LFP, etc)
cfg.filename = 'net_lfp'   # Set file output name
cfg.savePickle = True
cfg.recordLFP = [[-15, y, 1.0*netParams.sizeZ] for y in range(int(netParams.sizeY/5.0), int(netParams.sizeY), int(netParams.sizeY/5.0))]
cfg.saveLFPPops = ['I2', 'E4']
cfg.savePickle = True

#simConfig.analysis['plotRaster'] = {'orderBy': 'y', 'orderInverse': True, 'saveFig':True, 'figSize': (9,3)}      # Plot a raster
cfg.analysis['plotLFP'] = {'includeAxon': False, 'figSize': (6,10), 'timeRange': [100,1000], 'saveFig': True}  # optional: 'pop': 'E4'
#simConfig.analysis['getCSD'] = {'spacing_um': 200, 'timeRange': [100,3000], 'vaknin': True}
#simConfig.analysis['plotLFP'] = {'includeAxon': False, 'figSize': (6,10), 'timeRange':[100,900], 'minFreq': 10, 'maxFreq':60, 'norm':1, 'plots': ['spectrogram'], 'showFig': True} 
#simConfig.analysis['plotLFP'] = {'includeAxon': False, 'figSize': (6,10), 'timeRange':[100,900], 'plots': ['spectrogram'], 'showFig': True} 
#simConfig.analysis['plotCSD'] = True #{'timeRange':[100,200]}
