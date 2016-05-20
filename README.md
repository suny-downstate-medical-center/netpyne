# NetPyNE (python package)
## Description
A Python package to facilitate the development and simulation of biological networks in NEURON ([NetPyNE Documentation](http://neurosimlab.org/netpyne/))

NEURON/Python-based modularized framework for network simulations with MPI. Using this modularized structure, users can define different models (including cell types, populations, connectivities, etc.) just by modifying a single parameters file, and easily simulate then in NEURON. Additionally, the framework allows to store a single data file with the following:

1. model specifications (conn rules etc)
2. network instantiation (list of all cells, connections, etc)
3. simulation parameters/configuration (duration, dt, etc)
4. simulation output (spikes, voltage traces etc)

The data file is available in Pickle, JSON and Matlab formats.

Three example model parameters are provided: 

1. **HHTut.py** - simple tutorial model with a single Hodgkin-Huxley population and random connectivity
2. **HybridTut.py** - simple tutorial model with a Hodgkin-Huxley and an Izhikevich populations, with random connectivity
3. **M1.py** - mouse M1 model with 14 populations and cortical depth-dependent connectivity.

Additional details of the modelling framework can be found here:

* [NetPyNE Documentation](http://neurosimlab.org/netpyne/)
* [SFN'15 poster](http://neurosimlab.org/salvadord/sfn15-sal-final.pdf)
* [slides](https://drive.google.com/file/d/0B8v-knmZRjhtVl9BOFY2bzlWSWs/view?usp=sharing)       
 
      
## Setup and execution

Requires NEURON with Python and MPI support. 

1. Install package via `pip install netpyne`.

2. Create a model file (eg. model.py) where you import the netpyne package and set the parameters (you can use some of the parameter files incldued in the `examples` folder, eg. `HHTut.py`):

	```
	import HHTut
	from netpyne import init
	init.createAndSimulate(
		simConfig = HHTut.simConfig,     
		netParams = HHTut.netParams)
	```

3. Type `nrnivmodl mod`. This should create a directory called either i686 or x86_64, depending on your computer's architecture. 

4. To run type `python model.py` (or `mpiexec -np [num_proc] nrniv -python -mpi model.py` for parallel simulation).

## Overview of files:

* **examples/**: Folder with examples.

* **doc/**: Folder with documentation source files.

* **netpyne/**: Folder with netpyne package files.

* **netpyne/init.py**: Main executable; calls functions from other modules. Sets what parameter file to use.

* **netpyne/framework.py**: Contains all the model shared variables and modules. It is imported as "s" from all other file, so that any variable or module can be referenced from any file using s.varName

* **netpyne/sim.py**: Simulation control functions (eg. runSim).

* **netpyne/network.py**: Network related functions (eg. createCells)

* **netpyne/cell.py**: contains cell and population classes to create cells based on the parameters.

* **netpyne/analysis.py**: functions to visualize and analyse data

* **netpyne/default.py**: default network and simulation parameters

* **netpyne/utils.py**: utility python methods (eg. to import cell parameters)



For further information please contact: salvadordura@gmail.com 

