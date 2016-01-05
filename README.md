# NetPyNe (python package)
## Description
A Network development framework for Python-NEURON

NEURON/Python-based modularized framework for network simulations with MPI. Using this modularized structure, user can define different models (including cell types, populations, connectivities, etc.) just by modifying a single parameters file. Additionally, the framework allows to store a single data file the following:

1. model specifications (conn rules etc)
2. network instantiation (list of all cells, connections, etc)
3. simulation parameters/configuration (duration, dt, etc) and output spikes

The data file is available in Pickle, JSON and Matlab formats.

Three example model parameters are provided: 

1. **mpiHHTut.py** - simple tutorial model with a single Hodgkin-Huxley population and random connectivity
2. **mpiHybridTut.py** - simple tutorial model with a Hodgkin-Huxley and an Izhikevich populations, with random connectivity
3. **M1yfrac.py** - mouse M1 model with 14 populations and cortical depth-dependent connectivity.

Select which model to run by modifying the initialize call in init.py, eg.:

    `s.sim.initialize(                   
        simConfig = mpiHHTut.simConfig, 
        netParams = mpiHHTut.netParams)`
        
Additional details of the modelling framework can be found here:

* [Documentation](http://neurosimlab.org/salvadord/netpyne_doc/)
* [SFN'15 poster](http://neurosimlab.org/salvadord/sfn15-sal-final.pdf)
* [slides](https://drive.google.com/file/d/0B8v-knmZRjhtVl9BOFY2bzlWSWs/view?usp=sharing)       
 
      
## Setup and execution

Requires NEURON with Python and MPI support. 

1. Make sure the `netpyne` package is in the path

2. Create a model file where you import the netpyne package and set the parameters, eg. model.py:

	`from netpyne.params import mpiHHTut
	from netpyne import init

	init.createAndRun(                      
	    simConfig = mpiHHTut.simConfig,     
	    netParams = mpiHHTut.netParams)`

3. Type or `./compile or the equivalent `nrnivmodl mod`. This should create a directory called either i686 or x86_64, depending on your computer's architecture. 

4. To run type: `./runsim [num_proc]` or the equivalent `mpiexec -np [num_proc] nrniv -python -mpi model.py`

## Overview of file structure:

* **/init.py**: Main executable; calls functions from other modules. Sets what parameter file to use.

* **/params**: Contains a single parameters file to define each model. Includes simulation (simConfig) and network (netParams) parameters. 

* **/framework.py**: Contains all the model shared variables and modules. It is imported as "s" from all other file, so that any variable or module can be referenced from any file using s.varName

* **/sim.py**: Simulation control functions (eg. runSim).

* **/network.py**: Network related functions (eg. createCells)

* **/cell.py**: contains cell and population classes to create cells based on the parameters.

* **/analysis.py**: functions to visualize and analyse data

* **/cells/izhi2007.py**: Python class (wrapper) for Izhikevich 2007 neuron model

* **/mod/izhi2007b.mod**: NMODL definition of Izhikevich 2007 neuron model


For further information please contact: salvadordura@gmail.com 

