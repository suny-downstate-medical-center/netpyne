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

cfg, netParams = sim.loadFromIndexFile('index.npjson')

print("Starting sim ...")

(pops, cells, conns, stims, rxd, simData) = sim.create(netParams, cfg, output=True)

# saveInterval defines how often the data is saved
sim.runSimWithIntervalFunc(cfg.saveInterval, sim.intervalSave)

sim.gatherData()
sim.analyze()
