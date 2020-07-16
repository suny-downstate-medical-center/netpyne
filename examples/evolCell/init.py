"""
init.py

Starting script to run NetPyNE-based model.

Usage:  python init.py  # Run simulation, optionally plot a raster

MPI usage:  mpiexec -n 4 nrniv -python -mpi init.py

Contributors: salvadordura@gmail.com
"""

from netpyne import sim

cfg, netParams = sim.readCmdLineArgs()					# read cfg and netParams from command line arguments
sim.createSimulateAnalyze(simConfig = cfg, netParams = netParams) 
