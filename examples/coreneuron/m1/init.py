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

print("Starting sim ...")
sim.createSimulateAnalyze(netParams, cfg)

#sim.checkOutput('M1detailed')
if sim.rank == 0:
    with open('out_neuron.dat', 'w') as f:
        for spkid, spkt in zip(sim.allSimData['spkid'], sim.allSimData['spkt']):
            f.write('%.8g\t%d\n' % (spkt, spkid))

quit()
