"""
init.py

Starting script to run NetPyNE-based M1 model.

Usage:
    python init.py # Run simulation, optionally plot a raster

MPI usage:
    mpiexec -n 4 nrniv -python -mpi init.py

Contributors: salvadordura@gmail.com
"""

#import matplotlib; matplotlib.use('Agg')  # to avoid graphics error in servers

#from neuron import h,gui
from netpyne import sim
#from cfg_cell import cfg
#from netParams_cell import netParams

cfg, netParams = sim.readCmdLineArgs(simConfigDefault='cfg_cell.py', netParamsDefault='netParams_cell.py')
sim.initialize(
    simConfig = cfg, 	
    netParams = netParams)  				# create network object and set cfg and net params
sim.net.createPops()               			# instantiate network populations
sim.net.createCells()              			# instantiate network cells based on defined populations
sim.net.connectCells()            			# create connections between cells based on params
sim.net.addStims() 							# add network stimulation
sim.setupRecording()              			# setup variables to record for each cell (spikes, V traces, etc)
#sim.runSim()                      			# run parallel Neuron simulation  
#sim.gatherData()                  			# gather spiking data and cell info from each node
sim.analysis.plotData()         			# plot spike raster
#sim.saveData()                    			# save params, cell info and sim output to file (pickle,mat,txt,etc)


sim.analysis.plotShape(includePost = ['PT5B'], includePre = ['TVL'], includeAxon = 0, cvar = 'numSyns', dist = 0.58,
    figSize=(7,7), bkgColor=(0.9,0.9,0.9,1.0), fontSize=16, saveFig='paper_fig3.png', showFig=1)