"""
init.py

Starting script to run NetPyNE-based PT model.

Usage:
    python init.py # Run simulation, optionally plot a raster

MPI usage:
    mpiexec -n 4 nrniv -python -mpi init.py
"""

#import matplotlib; matplotlib.use('Agg')  # to avoid graphics error in servers

from netpyne import sim
from cfg import cfg
from netParams import netParams

sim.createSimulateAnalyze(netParams, cfg) #SimulateAnalyze(netParams, cfg)

# check model output
sim.checkOutput('PTcell')
