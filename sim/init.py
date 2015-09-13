"""
main.py

A modularized large-scale network simulation. 
Built solely in Python with MPI support. 
Runs in real-time with over >10k cells when appropriately parallelized.

Usage:
    python main.py # Run simulation, optionally plot a raster

MPI usage:
    mpiexec -n 4 nrniv -python -mpi main.py

Contributors: salvadordura@gmail.com
"""

from time import time
from neuron import h# Import NEURON

#import params as p
from params import mpiHHTut, M1yfrac
import shared as s

###############################################################################
# Sequence of commands to run full model
###############################################################################
def runSeq():
    # net = s.Network(params.net) # optionally can create or load network and pass as argument

    s.sim.initialize(simConfig = M1yfrac.simConfig, netParams = M1yfrac.netParams)
    
    s.net.createPops()  # instantiate network populations
    s.net.createCells()  # instantiate network cells based on defined populations
    s.net.connectCells()  
    s.sim.setupRecording()
    s.sim.runSim()
    s.sim.gatherData()
    # s.sim.saveData()
    # s.analysis.plotData()

runSeq()
