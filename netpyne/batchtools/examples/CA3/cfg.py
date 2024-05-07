from netpyne.batchtools import specs

### config ###

cfg = specs.SimConfig()

cfg.duration = 1000
cfg.dt = 0.1
cfg.hparams = {'v_init': -65.0}
cfg.verbose = False
cfg.recordTraces = {}  # don't save this
cfg.recordStim = False
cfg.recordStep = 0.1            # Step size in ms to save data (eg. V traces, LFP, etc)
cfg.filename = '00'         # Set file output name
cfg.savePickle = False        # Save params, network and sim output to pickle file
cfg.saveDat = False
cfg.saveJson = True
cfg.printRunTime = 0.1 
cfg.recordLFP = None # don't save this

cfg.analysis['plotRaster'] = {'saveFig': True} # raster ok
cfg.analysis['plotTraces'] = { } # don't save this
cfg.analysis['plotLFPTimeSeries'] = { }  # don't save this 

cfg.cache_efficient = True # better with MPI?
""" remove all of the unecessary data """
cfg.saveCellSecs = False
cfg.saveCellConns = False

cfg.nmda={#NMDA search space
    "PYR->BC" : 1.38e-3,
    "PYR->OLM": 0.7e-3,
    "PYR->PYR": 0.004e-3,
}
cfg.ampa={#AMPA search space
    "PYR->BC" : 0.36e-3,
    "PYR->OLM": 0.36e-3,
    "PYR->PYR": 0.02e-3,
}

cfg.gaba = {#GABA search space
    "BC->BC"  : 4.5e-3,
    "BC->PYR" : 0.72e-3,
    "OLM->PYR": 72e-3,
}
