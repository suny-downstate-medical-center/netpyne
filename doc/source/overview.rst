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

NetPyNE is open source and available at https://github.com/Neurosim-lab/netpyne .

For questions or suggestions please use the `Google NetPyNE QA forum <https://groups.google.com/forum/#!forum/netpyne-forum>`_ , the `NEURON NetPyNE forum <https://www.neuron.yale.edu/phpBB/viewforum.php?f=45>`_  or add an `Issue to github <https://github.com/Neurosim-lab/netpyne/issues>`_. 

For contributions (which are more than welcome!) please fork the repository and make a Pull Request with your changes. See our contributors guide for more details: [IMPORTANT ADD LINK HERE!!!!!!!!!!!!!!!!!!!]

For further information please contact salvadordura@gmail.com.


Code of conduct
---------------------

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms. See more details here: [IMPORTANT - ADD THIS FILE TO ROOT OF REPO: e.g.: https://github.com/atom/atom/blob/master/CODE_OF_CONDUCT.md A https://www.contributor-covenant.org/version/2/0/code_of_conduct.md]


Publications
-------------

[IMPORTANT - UPDATE PUBS!!!!!!!!!!]

About NetPyNE 
^^^^^^^^^^^^^^^^

- Dura-Bernal S, Suter B, Gleeson P, Cantarelli M, Quintana A, Rodriguez F, Kedziora DJ, Chadderdon GL, Kerr CC, Neymotin SA, McDougal R, Hines M, Shepherd GMG, Lytton WW. **NetPyNE: a tool for data-driven multiscale modeling of brain circuits.** `bioRxiv 461137 <https://www.biorxiv.org/content/early/2018/11/03/461137>`_ , *2018.*
16.	Dura-Bernal S, Suter B, Gleeson P, Cantarelli M, Quintana A, Rodriguez F, Kedziora DJ, Chadderdon GL, Kerr CC, Neymotin SA, McDougal R, Hines M, Shepherd GMG, Lytton WW. (2019) NetPyNE: a tool for data-driven multiscale modeling of brain circuits. eLife 2019;8:e44494 


- Dura-Bernal S, Suter BA, Quintana A, Cantarelli M, Gleeson P, Rodriguez F, Neymotin SA, Hines M, Shepherd GMG, Lytton WW. **NetPyNE: a GUI-based tool to build, simulate and analyze large-scale, data-driven network models in parallel NEURON.** *Society for Neuroscience (SfN), 2018*.

- Dura-Bernal S, Suter BA, Neymotin SA, Shepherd GMG, Lytton WW. **Modeling the subcellular distribution of synaptic connections in cortical microcircuits.** *Society for Neuroscience (SFN), 2016*.

- Dura-Bernal S, Suter BA, Neymotin SA, Kerr CC, Quintana A, Gleeson P, Shepherd GMG, Lytton WW. **NetPyNE: a Python package for NEURON to facilitate development and parallel simulation of biological neuronal networks.** *Computational Neuroscience (CNS), 2016.*

- Gleeson P, Marin B, Sadeh S, Quintana A, Cantarelli M, Dura-Bernal S, Lytton WW, Davison A, Silver RA. **A set of curated cortical models at multiple scales on Open Source Brain.** *Computational Neuroscience (CNS), 2016*.

- Dura-Bernal S, Suter BA, Neymotin SA, Quintana AJ, Gleeson P, Shepherd GMG, Lytton WW. **Normalized cortical depth (NCD) as a primary coordinate system for cell connectivity in cortex: experiment and model.** *Society for Neuroscience (SFN), 2015.*


Make use and/or cite NetPyNE
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

15.	Gleeson P, Cantarelli M, Quintana A, Earnsah M, Piasini E, Birgiolas J, Cannon RC, Cayco- Gajic A, Crook S, Davison AP, Dura-Bernal S, et al. (2019) Open Source Brain: a collaborative resource for visualizing, analyzing, simulating and developing standardized models of neurons and circuits. Neuron, 10.1016/j.neuron.2019.05.019.

20.	Kuhl E, Alber M, Tepole BA; Cannon WR; De S; Dura-Bernal S, Garikipati K, Karniadakis GE, Lytton WW, Perdikaris P, Petzold L. (2019) Multiscale modeling meets machine learning: What can we learn? arXiv:1911.11958 [Preprint]. Under review in Computer Methods in Applied Mechanics and Engineering.

19.	Dai K, Hernando J, Billeh JN, Gratiy SL, Planas J, Davison AP, Dura-Bernal S, Gleeson P, Devresse A, Gevaert M, King JG, Van Geit WAH, Povolotsky AV, Muller E, Courcol J-D, Arkhipov A (2019). The SONATA Data Format for Efficient Description of Large-Scale Network Models. bioRxiv, 625491 [Preprint]. Under review in PLoS Computational Biology.

18.	Gao P, Graham J, Angulo S, Dura-Bernal S, Zhou W, Hines ML, Lytton WW, and Antic S (2019) Experimental measurements and computational model of glutamate mediated dendritic and somatic plateau potentials. bioRxiv, 828582 [Preprint]. Under review in Nature Communications..

17.	Peng G, Alber M, Buganza A, Cannon W, De S, Dura-Bernal S, Garikipati K, Karmiadakis G, Lytton W, Perdikaris P, Petzold L, Kuhl E. (2019) Integrating Machine Learning and Multiscale Modeling: Perspectives, Challenges, and Opportunities in the Biological, Biomedical, and Behavioral Sciences. Nature Partner Journals (npj) Digital Medicine, 2, 115.

15.	Gleeson P, Cantarelli M, Quintana A, Earnsah M, Piasini E, Birgiolas J, Cannon RC, Cayco- Gajic A, Crook S, Davison AP, Dura-Bernal S, et al. (2019) Open Source Brain: a collaborative resource for visualizing, analyzing, simulating and developing standardized models of neurons and circuits. Neuron, 10.1016/j.neuron.2019.05.019.


- Romaro C, Araujo Najman F, Dura-Bernal S, Roque AC. **Implementation of the Potjans-Diesmann cortical microcircuit model in NetPyNE/NEURON with rescaling option.** *Computational Neuroscience (CNS), 2018.*

- Rodriguez F. **Dentate gyrus network model.** *Computational Neuroscience (CNS), 2018.*

- Dura-Bernal S, Neymotin SA, Suter BA, Shepherd GMG, Lytton WW (2018) **Long-range inputs and H-current regulate different modes of operation in a multiscale model of mouse M1 microcircuits.** `bioRxiv 201707 <https://www.biorxiv.org/content/10.1101/201707v3>`_ , *2018.*

- Lytton WW, Seidenstein AH, Dura-Bernal S, McDougal RA, Schurmann F, Hines ML. **Simulation neurotechnologies for advancing brain research: Parallelizing large networks in NEURON.** *Neural Computation, 2016.*

- Dura-Bernal S, Menzies RS, McLauchlan C, van Albada SJ, Kedziora DJ, Neymotin SA, Lytton WW, Kerr CC. **Effect of network size on computational capacity.** *Computational Neuroscience (CNS), 2016.*


Current funding
---------------------

- National Institutes of Health (NIH), National Insititute of Biomedical Imaging and Bioengineering (NIBIB) U24 EB028998: "Dissemination of a tool for data-driven multiscale modeling of brain circuits", Period: 2019-2024; Amount: $1,171,482; PI: Salvador Dura-Bernal


Governance structure
---------------------

Major decisions about NetPyNE are made by the steering committee, guided by the code of conduct.

- Salvadord Dura-Bernal (Assistant Professor, State University of New York Downstate; Research Scientist, Nathan Kline Institute for Psychiatric Research)
- William W Lytton (Distinguisehd Professor, State University of New York Downstate)
- Samuel A Neymotin (Research Scientist, Nathan Kline Institute for Psychiatric Research)
- Michael Hines (Senior Research Scientist, Yale University)
- Robert A McDougal (Assistant Professor, Yale University)
- Padraig Gleeson (Principal Research Fellow, University College London)
- Benjamin A Suter (Postdoctoral Fellow, Institute of Science and Technology Austria)
- Cliff C Kerr (Senior Research Scientist, Institute for Disease Modeling)


Project roadmap
---------------------

- Robustness, reliability and reproducibility of existing features

- Ongoing development of new features

- Dissemination and community engagement



From grant:
SA1: Quality control: reliability, robustness and reproducibility:
SA1.1 Ensuring reliability of new features, such that they perform their intended function under all valid conditions and inputs. These features include: molecular reaction-diffusion (RxD) components, generation of complex complex subcellular connectivity patterns, distributed saving, and parameter optimization via evolutionary algorithms. 
SA1.2 Ensuring tool robustness and error handling, such that it is able to cope with erroneous inputs and errors during execution. Improved tool robustness will include input validation, exception handling and informational messages, which will prevent user frustration and largely increase the tool's accessibility. 
SA1.3 Ensuring simulation reproducibility across the most common platforms, including different versions of operating systems, Python, NEURON, MPI library; and HPC platform setup (eg XSEDE/NSG, Google Cloud Platform).

SA2: Extension of the graphical user interface (GUI). The NetPyNE GUI will be essential to engage new users and disseminate the tool to experimentalists, clinicians and students. We will extend it as follows: 
SA2.1 Incorporating missing components, that are currently only accessible programmatically: RxD, subcellular connectivity, complex stimulation and parameter optimization (only grid search).
SA2.2 Enabling a web-based multi-user deployment that allows users to build models and run simulations through a web browser over the internet, making the tool publicly available to the global research community.   
SA2.3 Improving plots by replacing the current static images with modern interactive and dynamic plots that facilitate understanding complex and large datasets, for the most common plots (connectivity matrix, raster plot and voltage traces).
SA2.4 Improving performance to enable 3D visualization and manipulation of medium-scale networks of ~1k-10k detailed neurons (currently limited to a few hundred).  

SA3. User training. We will implement complementary dissemination strategies to attract users and ensure these can effectively and reliably use NetPyNE beyond the duration of the project:
SA3.1 Updated and comprehensive online documentation covering all the tool components, options and modes of usage, with examples, so both beginner and advanced users can independently explore and fully exploit the tool.  
SA3.2 Online interactive tutorials so new users can receive training at their own pace through multimedia-rich step-by-step instructions that can be executed interactively (eg via GUI or Jupyter Notebook).
SA3.3 Workshops/tutorials at neuroscience conferences to engage potential users by providing an overview of the tool functionalities and benefits. 
SA3.4 Annual 1-day in-person course to provide in-depth training to researchers who could then teach tool usage at their labs or institutions.  

