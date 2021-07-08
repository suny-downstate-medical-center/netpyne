from netpyne import sim

cfg, netParams = sim.readCmdLineArgs(
    simConfigDefault="saving_dist_cfg.py", netParamsDefault="saving_netParams.py"
)
sim.initialize(simConfig=cfg, netParams=netParams)
sim.net.createPops()
sim.net.createCells()
sim.net.connectCells()
sim.net.addStims()
sim.setupRecording()
sim.runSim()
# sim.gatherData()
# sim.saveData()
##### new #####
sim.saveDataInNodes()
sim.gatherDataFromFiles()
##### end new #####
sim.analysis.plotData()
