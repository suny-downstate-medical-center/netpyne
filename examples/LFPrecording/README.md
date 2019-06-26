# LFP recording
## Description
Two examples of using LFP recording in NetPyNE:

1) LFP recording for a single cell -- M1 corticospinal neuron --  with 700+ compartments (segments) and multiple somatic and dendritic ionic channels. The cell parameters are loaded from a .json file. The cell receives NetStim input to its soma via an excitatory synapse. Ten LFP electrodes are placed at both sides of the neuron at 5 different cortical depths. The soma voltage, LFP time-resolved signal and the 3D locations of the electrodes are plotted:

![lfp_cell](https://github.com/Neurosim-lab/netpyne/raw/lfp/examples/LFPrecording/lfp_cell.png)

2) LFP recording for a network very similar to that shown in Tutorial 5. However, in this case, the cells have been replaced with a more realistic model: a 6-compartment corticostriatal neuron with multiple ionic channels. The cell parameters are loaded from a .json file. Cell receive NetStim inputs and include excitatory and inhibitory connections. Four LFP electrodes are placed at different cortical depths. The raster plot and LFP time-resolved signal, PSD, spectrogram and 3D locations of the electrodes are plotted:

![lfp_net](https://github.com/Neurosim-lab/netpyne/raw/lfp/examples/LFPrecording/lfp_net.png)

To record LFP just set the list of 3D locations of the LFP electrodes in the `simConfig` attribute `recordLFP` e.g. ``simConfig.recordLFP = e.g. [[50, 100, 50], [50, 200, 50]]`` (note the y coordinate represents depth, so will be represented as a negative value whehn plotted). The LFP signal in each electrode is obtained by summing the extracellular potential contributed by each segment of each neuron. Extracellular potentials are calculated using the "line source approximation" and assuming an Ohmic medium with conductivity sigma = 0.3 mS/mm. For more information on modeling LFPs see http://www.scholarpedia.org/article/Local_field_potential or https://doi.org/10.3389/fncom.2016.00065 .

To plot the LFP use the ``sim.analysis.plotLFP()`` method. This allows to plot for each electrode: 1) the time-resolved LFP signal ('timeSeries'), 2) the power spectral density ('PSD'), 3) the spectrogram / time-frequency profile ('spectrogram'), 4) and the 3D locations of the electrodes overlayed over the model neurons ('locations'). See :ref:`analysis_functions` for the full list of ``plotLFP()`` arguments.

For further details see Tutorial 9: http://neurosimlab.org/netpyne/tutorial.html#recording-and-plotting-lfps-tutorial-9

## Setup and execution

Requires NEURON with Python and MPI support. 

1. Type `nrnivmodl mod` to create a directory called either i686 or x86_64, depending on your computer's architecture. 
2. To run the single cell example type: `python lfp_cell.py` or `mpiexec -np [num_proc] nrniv -mpi lfp_cell.py`
2. To run the network cell example type: `python lfp_net.py` or `mpiexec -np [num_proc] nrniv -mpi lfp_net.py`

## Overview of file structure:

* /cell_lfp.py: Code to run example of LFP recording in single cell. 

* /net_lfp.py: Code to run example of LFP recording in network.

* /PT5B_reduced_cellParams.json: Parameters of cell used for single cell example (netParams.cellParams). 

* /IT2_reduced_cellParams.json: Parameters of cell used for network example (netParams.cellParams). 

* /mod/: Mod files required for single cell and network models.


For further information please contact: salvadordura@gmail.com 

