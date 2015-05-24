"""
MODEL

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
import sim
import network
import analysis
import params as p
import shared as s


###############################################################################
### Sequence of commands to run full model
###############################################################################
def runSeq():
    if s.rank==0: verystart=time() # store initial time
    sim.readArgs()
    network.createCells()
    # network.connectCells() 
    # network.addBackground()
    # network.addStimulation()
    # sim.setupRecording()
    # sim.runSim()
    # sim.gatherData()
    # sim.saveData()
    # analysis.plotData()

    #s.pc.runworker() # MPI: Start simulations running on each host (add to simcontrol module)
    #s.pc.done() # MPI: Close MPI
    if s.rank==0:
        totaltime = time()-verystart # See how long it took in total
        print('\nDone; total time = %0.1f s.' % totaltime)


runSeq()
