from netpyne import specs

cfg = specs.SimConfig()

cfg.duration = 750
cfg.dt = 0.1
cfg.hparams = {'v_init': -65.0}
cfg.verbose = False
cfg.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
cfg.recordStim = False
cfg.recordStep = 0.1            # Step size in ms to save data (eg. V traces, LFP, etc)
cfg.filename = '00'         # Set file output name
cfg.savePickle = False        # Save params, network and sim output to pickle file
cfg.saveDat = False
cfg.printRunTime = 0.1 
cfg.recordLFP = [[50, 50, 50]]

cfg.analysis['plotRaster']={
                            'colorbyPhase':{
#                                'signal': LFP_array,          # when signal is provided as a np.array
#                                'signal': 'LFP_signal.pkl',   # when signal is provided as a list in a .pkl
#                                'fs': 10000,                  # in both cases, sampling frequency would be neccessary
                                'signal': 'LFP',               # internal signal, from the computation of LFPs
                                'electrode':1, 
                                'filtFreq':[4,8], 
                                'filtOrder': 3,
                                'pop_background': True,
                                'include_signal': True
                                },
                            'include':['allCells'], 
                            'saveFig':True, 'timeRange': [100,600]}      # Plot a raster
cfg.analysis['plotTraces'] = {'include': [0, 1, 800, 801, 1000, 1001], 'saveFig': True}  # Plot recorded traces for this list of cells
cfg.analysis['plotLFPTimeSeries'] = {'showFig': True, 'saveFig': True} 
#cfg.analysis['plotShape'] = {'includePre': ['all'],'includePost': [0,800,1000],'cvar':'numSyns','dist':0.7, 'saveFig': True}
