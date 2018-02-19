"""
init.py

Starting script to run NetPyNE-based PT model.

Usage:
    python init.py # Run simulation, optionally plot a raster

MPI usage:
    mpiexec -n 4 nrniv -python -mpi init.py

Contributors: salvadordura@gmail.com
"""

#import matplotlib; matplotlib.use('Agg')  # to avoid graphics error in servers

from netpyne import sim
from cfg import cfg
from netParams import netParams

sim.createSimulate(netParams, cfg) #SimulateAnalyze(netParams, cfg)
#sim.runSim()