# Running batch simulations using NetPyNE

Includes two toy examples using the 6-compartment M1 Corticospinal cell.
1) f-I curve as a function of the amplitude of an IClamp and dendritic Na conductance.
2) EPSP amplitude as a function of the weight of aNetStim and the rise time of an NMDA synapse.

The code runs the required batch simulations in parallel using MPI and plots the corresponding figures.

## Requirements
- NEURON with MPI support
- NetPyNE 

## Quick steps to run batch sims and plot results 

1) Compile mod files: 
	cd mod
	mkmod

2) Run batch simulations: 
	./runbatch [num_cores]

3) Plot results:
	ipython -i analysis.py


## Code structure:

* netParams.py: Defines the network model. Includes "fixed" parameter values of cells, synapses, connections, stimulation, etc. Changes to this file should only be made for relatively stable improvements of the model. Parameter values that will be varied systematically to explore or tune the model should be included here by referencing the appropiate variable in the simulation configuration (cfg) module. Only a single netParams file is required for each batch of simulations.

* cfg.py: Simulation configuration module. Includes parameter values for each simulation run such as duration, dt, recording parameters etc. Also includes the model parameters that are being varied to explore or tune the network. When running a batch, NetPyNE will create one cfg file for each parameter configuration.

* init.py: Sequence of commands to run a single simulation. Can be executed via 'ipython init.py'. When running a batch, NetPyNE will call init.py multiple times, pass a different cfg file for each of the parameter configurations explored. 

* batch.py: Defines the parameters and parameter values explored in the batch, as well as the run configuration (e.g. using MPI in a multicore machine or PBS Torque for HPCs). Includes examples of how to create 2 different batch simulations: 
	1) batchNa(): explore the effect of changing the amplitude of an IClamp and the dendritic Na conductance.
	2) batchNMDA(): explore the effect of changing the weight of NetStim and the rise time of an NMDA synapse.

To run, add a call to either of these functions in __main__(), or import the batch module and run interactively. 

To add new batch explorations, follow the format of the above example, making sure that the parameters being explored are included in cfg.py and referenced appropiately in netParams.py

* runbatch: Shell script to run the batch simulation using mpi. Alternatively, can run "manually" using: 
mpiexec -np [num_cores] nrniv -python -mpi batch.py 

* analysis.py: Functions to read and plot figures from the batch simulation results. Can call readPlotNa() or readPlotNMDA() from __main__() or import analysis and call interactively.  

* utils.py: Support functions to read output data from batch simulations, and others. Eventually, some of these functions will be moved to NetPyNE. 

* /cells: Folder containing cell model. In this case only includes SPI6.py. NetPyNE will import the cell specifications from this file. 

* /data: Folder to store output of simulations.

* /mod: Folder containing mod files (need to clean up to keep just mod files required for this model)


For further information please contact: salvadordura@gmail.com 

