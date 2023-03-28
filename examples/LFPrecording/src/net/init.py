from netpyne import sim

cfg, netParams = sim.loadFromIndexFile('index_net.npjson')

# Create network and run simulation

#sim.createSimulateAnalyze(netParams = netParams, simConfig = cfg)    
#sim.analysis.plotCSD(timeRange=[100,3000])
sim.initialize(
    simConfig = cfg, 	
    netParams = netParams)  				# create network object and set cfg and net params
sim.net.createPops()               			# instantiate network populations
sim.net.createCells()              			# instantiate network cells based on defined populations
sim.net.connectCells()            			# create connections between cells based on params
sim.net.addStims() 							# add network stimulation
sim.setupRecording()              			# setup variables to record for each cell (spikes, V traces, etc)
sim.runSim()                      			# run parallel Neuron simulation  
#sim.gatherData()                  			# gather spiking data and cell info from each node

# distributed saving (to avoid errors with large output data)
sim.saveDataInNodes()
sim.gatherDataFromFiles(saveMerged=True)

sim.analysis.plotData()         			# plot spike raster etc