"""
init.py

Starting script to run NetPyNE-based RxD model.

Usage:
    python init.py # Run simulation, optionally plot a raster

MPI usage:
    mpiexec -n 4 nrniv -python -mpi init.py
"""
from netpyne import sim
from netParams import netParams
from cfg import cfg

# --------------------------------
# Instantiate network
# --------------------------------
sim.initialize(netParams, cfg)  # create network object and set cfg and net params
sim.net.createPops()                  # instantiate network populations
sim.net.createCells()                 # instantiate network cells based on defined populations
sim.net.connectCells()                # create connections between cells based on params
sim.net.addStims()                    # add external stimulation to cells (IClamps etc)
sim.net.addRxD()                      # add reaction-diffusion (RxD)
sim.setupRecording()             # setup variables to record for each cell (spikes, V traces, etc)
sim.simulate()
sim.analyze()
