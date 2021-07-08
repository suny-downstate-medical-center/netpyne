from netpyne import specs

cfg = specs.SimConfig()

# Saving parameters
cfg.simLabel = "saving_dist"
cfg.saveFolder = cfg.simLabel + "_data"
# cfg.savePickle = True
cfg.saveDataInclude = ["simData", "simConfig", "netParams", "net"]

# Simulation parameters
cfg.duration = 10000
cfg.dt = 0.025
cfg.recordStep = 0.1

# Analysis parameters
cfg.recordTraces = {"V_soma": {"sec": "soma", "loc": 0.5, "var": "v"}}
cfg.analysis["plotRaster"] = {"saveFig": True}
cfg.analysis["plotTraces"] = {"include": [0], "saveFig": True}
cfg.analysis["plotConn"] = {"saveFig": True}

# Variable parameters (used in netParams)
cfg.synMechTau2 = 5
cfg.connWeight = 0.01
