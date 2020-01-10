"""
init.py

Starting script to run NetPyNE-based M1 model.

Usage:
    python init.py # Run simulation, optionally plot a raster

MPI usage:
    mpiexec -n 4 nrniv -python -mpi init.py

Contributors: salvadordura@gmail.com
"""

import matplotlib; matplotlib.use('Agg')  # to avoid graphics error in servers

from netpyne import sim
from cfg import cfg
from netParams import netParams
import os

cfg.saveWeights = True
cfg.intervalRun = 50 # define how often the interval function is run
cfg.saveInterval = 100 # define how often the data is saved, this can be used with interval run if you want to update the weights more often than you save
cfg.intervalFolder = 'temporary' #specify the location to save the interval data 

### This is an example function run at an interval during the simulation
### This function save weights everytime it runs and will save simulation data 
### at a different interval defined by cfg.intervalRun and cfg.saveInterval.
def saveWeights(t):

    # if a list for weights is not initialized make one
    if not hasattr(sim, 'allWeights'):
        sim.allWeights=[]
    
    # save the weights
    for cell in sim.net.cells:
        for conn in cell.conns:
            sim.allWeights.append(float(conn['hObj'].weight[0]))
    
    # if the sim time matches the saveInterval then save data
    # NOTE: intervalRun must divide evenly into saveInterval (saveInterval % intervalRun == 0)
    if (round(t, 4) % cfg.saveInterval == 0):
            sim.intervalSave(t)
    

print("Starting sim ...")

(pops, cells, conns, stims, rxd, simData) = sim.create(netParams, cfg, output=True)

# we run with an interval function defined above
sim.runSimWithIntervalFunc(cfg.intervalRun, saveWeights)  

# we run fileGather() instead of gather       
sim.fileGather()   
sim.analyze()


sim.checkOutput('M1detailed')