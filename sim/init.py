"""
init.py

A modularized framework to develop and run large-scale network simulations. 
Built solely in Python with MPI support. 

Usage:
    python init.py # Run simulation, optionally plot a raster

MPI usage:
    mpiexec -n 4 nrniv -python -mpi main.py

Contributors: salvadordura@gmail.com
"""

from time import time
from neuron import h # Import NEURON

#import params as p
from params import mpiHHTut, M1yfrac
import shared as s

###############################################################################
# Sequence of commands to run full model
###############################################################################
def runModel():
    s.sim.initialize(                   # create network object and set cfg and net params
        simConfig = M1yfrac.simConfig, 
        netParams = M1yfrac.netParams)  
    s.net.createPops()                  # instantiate network populations
    s.net.createCells()                 # instantiate network cells based on defined populations
    s.net.connectCells()                # create connections between cells based on params
    s.sim.setupRecording()              # setup variables to record for each cell (spikes, V traces, etc)
    s.sim.runSim()                      # run parallel Neuron simulation  
    s.sim.gatherData()                  # gather spiking data and cell info from each node
    s.sim.saveData()                    # save params, cell info and sim output to file (pickle,mat,txt,etc)
    s.analysis.plotData()               # plot spike raster


runModel()                              # execute sequence of commands to run full model
