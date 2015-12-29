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

from params import mpiHHTut, mpiHybridTut, M1yfrac
import shared as s


def runModel(simConfig, netParams):
    ''' Sequence of commands to run full model '''
    s.sim.initialize(simConfig, netParams)  # create network object and set cfg and net params
    s.net.createPops()                  # instantiate network populations
    s.net.createCells()                 # instantiate network cells based on defined populations
    s.net.connectCells()                # create connections between cells based on params
    s.sim.setupRecording()              # setup variables to record for each cell (spikes, V traces, etc)
    s.sim.runSim()                      # run parallel Neuron simulation  
    s.sim.gatherData()                  # gather spiking data and cell info from each node
    s.sim.saveData()                    # save params, cell info and sim output to file (pickle,mat,txt,etc)
    s.analysis.plotData()               # plot spike raster


# Main call
runModel(                                      # execute sequence of commands to run full model
    simConfig = M1yfrac.simConfig,     # pass simulation config options and network params as arguments
    netParams = M1yfrac.netParams)      

