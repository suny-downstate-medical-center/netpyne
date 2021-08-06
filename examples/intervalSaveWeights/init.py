"""
init.py

Starting script to run NetPyNE-based M1 model.

Usage:
    python init.py # Run simulation, optionally plot a raster

MPI usage:
    mpiexec -n 4 nrniv -python -mpi init.py
"""

import matplotlib; matplotlib.use('Agg')  # to avoid graphics error in servers

from netpyne import sim
from cfg import cfg
from netParams import netParams
import os

### This is an example function run at an interval during the simulation
### This function save weights everytime it runs and will save simulation data
### at a different interval defined by cfg.intervalRun and cfg.saveInterval.
def saveWeights(simTime):

    # if a list for weights is not initialized make one
    if not hasattr(sim, 'allWeights'):
        sim.allWeights=[]

    # save the weights
    for cell in sim.net.cells:
        for conn in cell.conns:
            sim.allWeights.append(float(conn['hObj'].weight[0]))

    # if the sim time matches the saveInterval then save data
    # NOTE: intervalRun must divide evenly into saveInterval (saveInterval % intervalRun == 0)
    if (round(simTime, 4) % cfg.saveInterval == 0):
            sim.intervalSave(simTime)


print("Starting sim ...")

(pops, cells, conns, stims, rxd, simData) = sim.create(netParams, cfg, output=True)

# we run with an interval function defined above
# if you just want to save the data and not the wieghts you can use the sim.intervalSave function instead of saveWeights
sim.runSimWithIntervalFunc(cfg.intervalRun, saveWeights)

# we run fileGather() instead of gather
sim.fileGather()
sim.analyze()


sim.checkOutput('M1detailed')
