NetPyNE Overview
=======================================

What is NetPyNE?
----------------

NetPyNE (Network development Python package for NEURON) is a python package to facilitate the development, parallel simulation and analysis of biological neuronal networks using the NEURON simulator.

NEURON is a widely used neuronal simulator, with over 1600 published models. It enables multiscale simulation ranging from the molecular to the network level. However, learning to use NEURON, especially running parallel simulations, requires much technical training. NetPyNE (Network development Python package for NEURON) greatly facilitates the development and parallel simulation of biological neuronal networks in NEURON, potentially bringing its benefits to a wider audience, including experimentalists. It is also intended for experienced modelers, providing powerful features to incorporate complex anatomical and physiological data into models.

.. image:: figs/overview.png
	:width: 80%	
	:align: center

What can I do with NetPyNE?
---------------------------

NetPyNE seamlessly converts a set of high-level specifications into a NEURON model. Specifications are provided in a simple, standardized, declarative format, based solely on Python’s lists and dictionaries. The user can define network populations and their properties, including cell type, number or density. For each cell type, the user can define morphology, biophysics and implementation, or choose to import these from existing files (HOC templates or Python classes). Cell models for each population can be easily changed, and several models can be combined to generate efficient hybrid networks, eg. composed of Hodgkin-Huxley multicompartment cells and Izhikevich point neurons. 

NetPyNE provides an extremely flexible format to specify connectivity, with rules based on pre- and post-synaptic cell properties, such as cell type or location. Multiple connectivity functions are available, including all-to-all, probabilistic, convergent or divergent. Additionally, connectivity parameters (eg. weight, probability or delay) can be specified as a function of pre/post-synaptic spatial properties. This enables implementation of complex biological patterns, such as delays or connection probabilities that depend on distance between cells, or weights that depend on the post-synaptic neuron’s cortical depth. The subcellular distribution of synapses along the dendrites can be specified, and is automatically adapted to the morphology of each model neuron. Learning mechanisms, including spike-timing dependent plasticity and reinforcement learning, can be readily incorporated.

Using the high-level network specifications, NetPyNE instantiates the full model (all cells and connections) as a hierarchical Python structure including the NEURON objects necessary for simulation. Based on a set of simulation options (eg. duration, integration step), NetPyNE runs the model in parallel using MPI, eliminating the burdensome task of manually distributing the workload and gathering data across computing nodes. Optionally NetPyNE plots output data, such as spike raster plots, LFP power spectra, connectivity matrix, or intrinsic time-varying variables (eg. voltage) of any subset of cells. To facilitate data sharing, the package saves and loads the high-level specifications, instantiated network, and simulation results using common file formats (Pickle, Matlab, JSON or HDF5). NetPyNE can convert instantiated networks to and from NeuroML, a standard data format for exchanging models in computational neuroscience.

NetPyNE has been used to develop a variety of multiscale models: primary motor cortex with cortical depth-dependent connectivity; the claustrum; and sensorimotor cortex that learns to control a virtual arm. The package is open source, easily installed, and includes comprehensive online documentation, a step-by-step tutorial and example networks. We believe this tool will strengthen the neuroscience community and encourage collaborations between experimentalists and modelers.



Main Features
--------------

* Converts a set of high-level specifications into a NEURON network model. 

* Specifications are provided in a simple, standardized, declarative Python-based format (lists and dictionaries).

* Can easily define:

	* *Populations*: cell type and model, number of neurons or density, spatial extent, ...
	* *Cell properties*: Morphology, biophysics, implementation, ...
	* *Synaptic mechanisms*: Time constants, reversal potential, implementation, ...
	* *Stimulation*: Spike generators, current clamps, spatiotemporal properties, ...
	* *Connectivity rules*: conditions of pre- an post-synaptic cells, different functions, ...
	* *Simulation configuration*: 

* Cell properties highlights:

	* Can easily import existing HOC and Python defined cell models into NetPyNE format.
	* Can easily change the model implementation eg. from Hodgkin-Huxley multicompartment to Izhikevich point neuron
	* Can combine multiple cell models to achieve efficient large-scale networks.

* Connectivity rules highlights:

	* Flexible connectivity rules based on pre- and post-synaptic cell properties (eg. cell type or location). 
	* Connectivity functions available: all-to-all, probabilistic, convergent, divergent, and explicit list.  
	* Can specify parameters (eg. weight, probability or delay) as a function of pre/post-synaptic spatial properties, eg. delays or probability that depend on distance between cells or cortical depth.
	* Can specify subcellular distribution of synapses along the dendrites, and will be automatically adapted to the morphology of each model neuron. 
	* Can easily add learning mechanisms to synapses, including STDP and reinforcement learning.

* Generates NEURON network instance ready for MPI parallel simulation -- takes care of cell distribution and gathering of data.

* Can analyse and plot network and simulation output data:
	* Raster plot
	* Spike histogram of all cells, populations or single cells
	* Intrinsic cell variables (voltages, currents, conductances) plots
	* Local field potential (LFP) calculation and plots (time-resolved and power spectra)
	* Connectivity matrix at cell or population level (weights, num connections, efficiency, probability, ...)
	* 2D representation of network cell locations and connections

* Faciliates data sharing: 
	* Can save/load high-level specs, network instance, simulation configuration and simulation results.
	* Multiple formats supported: pickle, Matlab, JSON, CSV, HDF5
	* Can export/import to/from NeuroML, the standard format for neural models.

* Open source, easily to install, comprehensive online documentation, and step-by-step tutorial and example networks.

