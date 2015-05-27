"""
main.py

A modularized large-scale network simulation. 
Built solely in Python with MPI support. 
Runs in real-time with over >10k cells when appropriately parallelized.

Usage:
    python main.py # Run simulation, optionally plot a raster

MPI usage:
    mpiexec -n 4 nrniv -python -mpi main.py

2015may22 salvadordura@gmail.com
"""

from time import time
from neuron import h# Import NEURON

import params as p
import shared as s


###############################################################################
### Sequence of commands to run full model
###############################################################################
def runSeq():
    if s.rank==0: verystart=time()  # store initial time
    s.sim.readArgs()  # set parameters based on commandline arguments
    s.network.createPops()  # instantiate network populations
    s.network.createCells()  # instantiate network cells based on defined populations
    s.network.connectCells()  
    s.network.addBackground()
    #s.network.addStimulation()
    s.sim.setupRecording()
    s.sim.runSim()
    s.sim.gatherData()
    s.sim.saveData()
    s.analysis.plotData()

    if s.rank==0:
        totaltime = time()-verystart # See how long it took in total
        print('\nDone; total time = %0.1f s.' % totaltime)


runSeq()
