Overview
=======================================

What is NetPyNE?
----------------

NetPyNE (Network development Python package for NEURON) is a python package to facilitate the development and parallel simulation of biological cell networks using the NEURON simulator.

.. image:: figs/overview.png
	:width: 80%	
	:align: center

NEURON is a widely used neuronal simulator, with over 1600 published models. It enables multiscale simulation ranging from the molecular to the network level. However, learning to use NEURON, especially running parallel simulations, requires much technical training. NetPyNE (Network development Python package for NEURON) greatly facilitates the development and parallel simulation of biological neuronal networks in NEURON, potentially bringing its benefits to a wider audience, including experimentalists. It is also intended for experienced modelers, providing powerful features to incorporate complex anatomical and physiological data into models.

What can I do with NetPyNE?
---------------------------

NetPyNE seamlessly converts a set of high-level specifications into a NEURON model. Specifications are provided in a simple, standardized, declarative format, based solely on Python’s lists and dictionaries. The user can define network populations and their properties, including cell type, number or density. For each cell type, the user can define morphology, biophysics and implementation, or choose to import these from existing files (HOC templates or Python classes). Cell models for each population can be easily changed, and several models can be combined to generate efficient hybrid networks, eg. composed of Hodgkin-Huxley multicompartment cells and Izhikevich point neurons. 

NetPyNE provides an extremely flexible format to specify connectivity, with rules based on pre- and post-synaptic cell properties, such as cell type or location. Multiple connectivity functions are available, including all-to-all, probabilistic, convergent or divergent. Additionally, connectivity parameters (eg. weight, probability or delay) can be specified as a function of pre/post-synaptic spatial properties. This enables implementation of complex biological patterns, such as delays or connection probabilities that depend on distance between cells, or weights that depend on the post-synaptic neuron’s cortical depth. The subcellular distribution of synapses along the dendrites can be specified, and is automatically adapted to the morphology of each model neuron. Learning mechanisms, including spike-timing dependent plasticity and reinforcement learning, can be readily incorporated.

Using the high-level network specifications, NetPyNE instantiates the full model (all cells and connections) as a hierarchical Python structure including the NEURON objects necessary for simulation. Based on a set of simulation options (eg. duration, integration step), NetPyNE runs the model in parallel using MPI, eliminating the burdensome task of manually distributing the workload and gathering data across computing nodes. Optionally NetPyNE plots output data, such as spike raster plots, LFP power spectra, connectivity matrix, or intrinsic time-varying variables (eg. voltage) of any subset of cells. To facilitate data sharing, the package saves and loads the high-level specifications, instantiated network, and simulation results using common file formats (Pickle, Matlab, JSON or HDF5). NetPyNE can convert instantiated networks to and from NeuroML, a standard data format for exchanging models in computational neuroscience.

NetPyNE has been used to develop a variety of multiscale models: primary motor cortex with cortical depth-dependent connectivity; the claustrum; and sensorimotor cortex that learns to control a virtual arm. The package is open source, easily installed, and includes comprehensive online documentation, a step-by-step tutorial and example networks. We believe this tool will strengthen the neuroscience community and encourage collaborations between experimentalists and modelers.


.. image:: figs/netstruct.png
	:width: 80%
	:align: center


Main Features
--------------

* Clear separation (modularization) of parameter specifications, network instantiation and NEURON simulation code. 
* Easy-to-use, standardized, flexible, extensible and NEURON-independent format to specify parameters:
	* Populations
	* Cell property rules 
	* Connectivity rules
	* Simulation configuration
* Support for normalized cortical depth (yfrac) dependence of cell density and connectivity.
* Easy specification, importing and swapping of cell models (eg. point neuron vs multicompartment)
* Support for hybrid networks eg. combining point and multicompartment neurons. 
* Multiple connectivity functions (eg. full, random, probabilistic) with optional parameters (eg. delay range)
* Support for user-defined connectivity functions.
* Populations, cell properties and connectivity rules can include reference to annotations (eg. for provenance).
* NEURON-independent instantiation of network (all cells, connections, ...) using Python objects and containers.
* NEURON-specific instantiation of network ready for simulation.
* Enables sharing of Python-based network objects, which can then be instantiated and simulated in NEURON.
* Easy MPI parallel simulation of network, including cell distribution across nodes and gathering of data from all nodes.
* Analysis and visualization of network (eg. connectivity matrix) and simulation output (eg. voltage traces, raster plot)
* Data exporting/sharing to several formats (pickle, Matlab, JSON, HDF5, NeuroML) of the following:
	* Parameters/specifications
	* Instantiated networks
	* Simulation results
