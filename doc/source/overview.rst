NetPyNE Overview
=======================================

What is NetPyNE?
----------------

NetPyNE (**Net**\ works using **Py**\ thon and **NE**\ URON) is a python package to facilitate the development, parallel simulation and analysis of biological neuronal networks using the NEURON simulator.
Although NEURON already enables multiscale simulation ranging from the molecular to the network level, NEURON for networks, often requiring parallel simulations, requires substantial programming. NetPyNE greatly facilitates the development and parallel simulation of biological neuronal networks in NEURON for students and experimentalists. NetPyNE is also intended for experienced modelers, providing powerful features to incorporate complex anatomical and physiological data into models.

For a more detailed overview of NetPyNE see:

- `BioRxiv paper <https://www.biorxiv.org/content/early/2018/11/03/461137>`_

- `SLIDES for Computational Neuroscience conference CNS17 <http://it.neurosim.downstate.edu/salvadord/netpyne.pdf>`_

- `POSTER for Computational Neuroscience conference CNS16 <http://it.neurosim.downstate.edu/salvadord/CNS16_poster.pdf>`_ 

|

.. image:: figs/schematic.png
	:width: 90%	
	:align: center

Major Features
--------------

* **Converts a set of high-level specifications into a NEURON network model.**

* **Specifications are provided in a simple, standardized, declarative Python-based format.**

* Can easily define:
	* *Populations*: cell type and model, number of neurons or density, spatial extent, ...
	* *Cell properties*: Morphology, biophysics, implementation, ...
    * *Reaction-diffusion (RxD)*: Species, regions, reactions, ... 
	* *Synaptic mechanisms*: Time constants, reversal potential, implementation, ...
	* *Stimulation*: Spike generators, current clamps, spatiotemporal properties, ...
	* *Connectivity rules*: conditions of pre- an post-synaptic cells, different functions, ...
	* *Simulation configuration*: duration, saving and analysis, graphical output, ... 

* Cell properties highlights:
	* Import existing HOC and Python defined cell models into NetPyNE format.
	* Readily change model implementation *e.g.,* from Hodgkin-Huxley multicompartment to Izhikevich point neuron
	* Combine multiple cell models into hybrid networks for efficient large-scale networks.

* Connectivity rules highlights:
	* Flexible connectivity rules based on pre- and post-synaptic cell properties (*e.g.,* cell type or location). 
	* Connectivity functions available: all-to-all, probabilistic, convergent, divergent, and explicit list.  
	* Can specify parameters (*e.g.,* weight, probability or delay) as a function of pre/post-synaptic spatial properties, *e.g.,* delays or probability that depend on distance between cells or cortical depth.
	* Can specify subcellular distribution of synapses along the dendrites, and will be automatically adapted to the morphology of each model neuron. 
	* Can easily add learning mechanisms to synapses, including STDP and reinforcement learning.

* **Generates NEURON network instance ready for MPI parallel simulation -- takes care of cell distribution and gathering of data.**

* Analysis and plotting of network and simulation output:
	* Raster plot
	* Spike histogram of all cells, populations or single cells
	* Intrinsic cell variables (voltages, currents, conductances) plots
	* Local field potential (LFP) calculation and plots (time-resolved and power spectra)
	* Connectivity matrix at cell or population level (weights, num connections, efficiency, probability, ...)
	* 2D representation of network cell locations and connections
 	* 3D shape plot with option to include color-coded variables (eg, num of synapses) 
 	* Normalized transfer entropy and spectral Granger Causality

* Facilitates data sharing: 
	* Can save/load high-level specs, network instance, simulation configuration and simulation results.
	* Multiple formats supported: pickle, Matlab, JSON, CSV, HDF5
	* Can export/import to/from NeuroML and SONATA, standardized formats for neural models.

* Batch simulations:
	* Easy specification of parameters and range of values to explore in batch simulations.
	* Pre-defined, configurable setups to automatically submit jobs in multicore machines (Bulletin board) or supercomputers (SLURM or PBS Torque)
	* Analysis and visualization of multidimensional batch simulation results.

* Current usage:
    * Used to develop models of many different brain regions and phenomena. See `full list of models <www.netpyne.org/models>`_.
    * Integrated with the Human Neocortical Neurosolver (https://hnn.brown.edu/) to add flexibility to its cortical model 
    * Used by Open Source Brain (www.opensourcebrain.org) to run parallel simulation of NeuroML-based NEURON models
    * Available to run simulations on XSEDE supercomputers via the `Neuroscience Gateway <www.nsgportal.org>`_. 

Questions, suggestions and contributions
-----------------------------------------

NetPyNE is currently being developed and supported by the Neurosim lab (http://neurosimlab.org) .

NetPyNE is open source and available at https://github.com/Neurosim-lab/netpyne .

For questions or suggestions please use the `Google NetPyNE QA forum <https://groups.google.com/forum/#!forum/netpyne-forum>`_ , the `NEURON NetPyNE forum <https://www.neuron.yale.edu/phpBB/viewforum.php?f=45>`_  or add an `Issue to github <https://github.com/Neurosim-lab/netpyne/issues>`_. 

For contributions (which are more than welcome!) please fork the repository and make a Pull Request with your changes.

For further information please contact salvadordura@gmail.com.


Publications
-------------

About NetPyNE 
^^^^^^^^^^^^^^^^

- Dura-Bernal S, Suter B, Gleeson P, Cantarelli M, Quintana A, Rodriguez F, Kedziora DJ, Chadderdon GL, Kerr CC, Neymotin SA, McDougal R, Hines M, Shepherd GMG, Lytton WW. **NetPyNE: a tool for data-driven multiscale modeling of brain circuits.** `bioRxiv 461137 <https://www.biorxiv.org/content/early/2018/11/03/461137>`_ , *2018.*

- Dura-Bernal S, Suter BA, Quintana A, Cantarelli M, Gleeson P, Rodriguez F, Neymotin SA, Hines M, Shepherd GMG, Lytton WW. **NetPyNE: a GUI-based tool to build, simulate and analyze large-scale, data-driven network models in parallel NEURON.** *Society for Neuroscience (SfN), 2018*.

- Dura-Bernal S, Suter BA, Neymotin SA, Shepherd GMG, Lytton WW. **Modeling the subcellular distribution of synaptic connections in cortical microcircuits.** *Society for Neuroscience (SFN), 2016*.

- Dura-Bernal S, Suter BA, Neymotin SA, Kerr CC, Quintana A, Gleeson P, Shepherd GMG, Lytton WW. **NetPyNE: a Python package for NEURON to facilitate development and parallel simulation of biological neuronal networks.** *Computational Neuroscience (CNS), 2016.*

- Gleeson P, Marin B, Sadeh S, Quintana A, Cantarelli M, Dura-Bernal S, Lytton WW, Davison A, Silver RA. **A set of curated cortical models at multiple scales on Open Source Brain.** *Computational Neuroscience (CNS), 2016*.

- Dura-Bernal S, Suter BA, Neymotin SA, Quintana AJ, Gleeson P, Shepherd GMG, Lytton WW. **Normalized cortical depth (NCD) as a primary coordinate system for cell connectivity in cortex: experiment and model.** *Society for Neuroscience (SFN), 2015.*


Using NetPyNE
^^^^^^^^^^^^^^^^^^

- Romaro C, Araujo Najman F, Dura-Bernal S, Roque AC. **Implementation of the Potjans-Diesmann cortical microcircuit model in NetPyNE/NEURON with rescaling option.** *Computational Neuroscience (CNS), 2018.*

- Rodriguez F. **Dentate gyrus network model.** *Computational Neuroscience (CNS), 2018.*

- Dura-Bernal S, Neymotin SA, Suter BA, Shepherd GMG, Lytton WW (2018) **Long-range inputs and H-current regulate different modes of operation in a multiscale model of mouse M1 microcircuits.** `bioRxiv 201707 <https://www.biorxiv.org/content/10.1101/201707v3>`_ , *2018.*

- Lytton WW, Seidenstein AH, Dura-Bernal S, McDougal RA, Schurmann F, Hines ML. **Simulation neurotechnologies for advancing brain research: Parallelizing large networks in NEURON.** *Neural Computation, 2016.*

- Dura-Bernal S, Menzies RS, McLauchlan C, van Albada SJ, Kedziora DJ, Neymotin SA, Lytton WW, Kerr CC. **Effect of network size on computational capacity.** *Computational Neuroscience (CNS), 2016.*
