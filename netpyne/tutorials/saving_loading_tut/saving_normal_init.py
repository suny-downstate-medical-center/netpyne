from netpyne import sim

cfg, netParams = sim.readCmdLineArgs(
    simConfigDefault="saving_normal_cfg.py", netParamsDefault="saving_netParams.py"
)
sim.initialize(simConfig=cfg, netParams=netParams)
sim.net.createPops()
sim.net.createCells()
sim.net.connectCells()
sim.net.addStims()
sim.setupRecording()
sim.runSim()
sim.gatherData()
sim.saveData()
sim.analysis.plotData()
