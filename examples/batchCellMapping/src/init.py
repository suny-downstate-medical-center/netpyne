"""
init.py

Starting script to run NetPyNE-based model.

Usage: python src/init.py  # Run simulation, optionally plot a raster

MPI usage:  mpiexec -n 4 nrniv -python -mpi src/init.py
"""

# import os
# os.chdir('examples/batchCellMapping')

from netpyne import sim
# read cfg and netParams from command line arguments
cfg, netParams = sim.readCmdLineArgs(simConfigDefault='src/cfg.py', netParamsDefault='src/netParams.py')
sim.createSimulateAnalyze(simConfig = cfg, netParams = netParams)
