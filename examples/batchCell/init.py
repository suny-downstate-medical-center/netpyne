"""
init.py

Starting script to run NetPyNE-based model.

Usage:  python init.py  # Run simulation, optionally plot a raster

MPI usage:  mpiexec -n 4 nrniv -python -mpi init.py

Contributors: salvadordura@gmail.com
"""

from netpyne import sim

cfg, netParams = sim.readCmdLineArgs()					# read cfg and netParams from command line arguments
sim.initialize(simConfig = cfg, netParams = netParams)  # create network object and set cfg and net params
sim.net.createPops()               						# instantiate network populations
sim.net.createCells()              						# instantiate network cells based on defined populations
sim.net.connectCells()            						# create connections between cells based on params
sim.net.addStims() 										# add network stimulation
sim.setupRecording()              						# setup variables to record for each cell (spikes, V traces, etc)
sim.runSim()                      						# run parallel Neuron simulation  
sim.gatherData()                  						# gather spiking data and cell info from each node
sim.saveData()                    						# save params, cell info and sim output to file (pickle,mat,txt,etc)
sim.analysis.plotData()         						# plot spike raster
