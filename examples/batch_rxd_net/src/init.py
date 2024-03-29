"""
init.py

Starting script to run NetPyNE-based RxD model.

Usage:
    python src/init.py # Run simulation, optionally plot a raster

MPI usage:
    mpiexec -n 4 nrniv -python -mpi src/init.py
"""
from netpyne import sim
cfg, netParams = sim.readCmdLineArgs(simConfigDefault='src/cfg.py', netParamsDefault='src/netParams.py')	

# --------------------------------
# Instantiate network
# --------------------------------
sim.initialize(netParams, cfg)  # create network object and set cfg and net params
sim.net.createPops()                  # instantiate network populations
sim.net.createCells()                 # instantiate network cells based on defined populations
sim.net.connectCells()                # create connections between cells based on params
sim.net.addStims()                    # add external stimulation to cells (IClamps etc)
sim.net.addRxD(nthreads=4)                      # add reaction-diffusion (RxD)
sim.setupRecording()             # setup variables to record for each cell (spikes, V traces, etc)
sim.simulate()
sim.analyze()
