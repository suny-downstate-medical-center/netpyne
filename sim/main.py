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



import sys
from numpy import mean, zeros
from time import time
import pickle
from neuron import h# Import NEURON
import network
import shared as s


###############################################################################
### Sequence of commands to run full model
###############################################################################
# standard sequence
def runSeq():
    verystart=time() # store initial time
    createCells()
    connectCells() 
    addBackground()
    addStimulation()
    setupRecording()
    runSim()
    gatherData()
    #saveData()
    #plotData()

    #s.pc.runworker() # MPI: Start simulations running on each host (add to simcontrol module)
    #s.pc.done() # MPI: Close MPI
    totaltime = time()-verystart # See how long it took in total
    print('\nDone; total time = %0.1f s.' % totaltime)


network.runSeq()
