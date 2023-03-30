"""
init.py

Starting script to run NetPyNE-based model.

Usage:  python src/init.py  # Run simulation, optionally plot a raster

MPI usage:  mpiexec -n 4 nrniv -python -mpi src/init.py
"""

from netpyne import sim

cfg, netParams = sim.readCmdLineArgs(simConfigDefault='src/cfg.py', netParamsDefault='src/netParams.py')

# sim.createSimulateAnalyze(netParams, cfg)
#​
sim.initialize(
    simConfig = cfg, 	
    netParams = netParams)  				# create network object and set cfg and net params
sim.net.createPops()               			# instantiate network populations
sim.net.createCells()              			# instantiate network cells based on defined populations
sim.net.connectCells()            			# create connections between cells based on params
sim.net.addStims() 							# add network stimulation
sim.setupRecording()              			# setup variables to record for each cell (spikes, V traces, etc)
sim.runSim()                      			# run parallel Neuron simulation  
sim.gatherData()                  			# gather spiking data and cell info from each node

# distributed saving (to avoid errors with large output data)
#sim.saveDataInNodes()
#sim.gatherDataFromFiles(saveMerged=True)

sim.saveData()                  			# gather spiking data and cell info from each node
sim.analysis.plotData()        