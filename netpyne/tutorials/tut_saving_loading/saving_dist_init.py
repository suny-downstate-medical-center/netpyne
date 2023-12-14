import os
os.chdir('netpyne/tutorials/saving_loading_tut')

from netpyne import sim
# sim.gatherDataFromFiles(simLabel='saving_dist', saveFolder='saving_dist_data')

cfg, netParams = sim.readCmdLineArgs(simConfigDefault='saving_dist_cfg.py', netParamsDefault='saving_netParams.py')
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
