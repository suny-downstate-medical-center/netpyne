## Version 0.4.8?

- Added option to specify weight scale factor separately for each cell model (issue #69)

- Fixed bug so can create Python and NEURON objects for connections independently 

## Version 0.4.7

- Added option for random seeds for connectivity, stimulation, and cell locations (issue #49)

- Added return pointers when create cells, pops, conns, stims, and recording (issue #48)

- Renamed point process param labels: '_type' -> 'mod', '_loc' -> 'loc' (issue #24)

- Added option to set h global variables (eg. celsius) (issue #31)

- Fixed importCell() so h global variables reset after importing (issue #31)

- Fixed importCell() so synapses stored in synMechParams (issue #25)

- Fixed bug when pop names contained same subset of characters (issue #40)


## Version 0.4.6

- Preliminary version of exporter to NeuroML2

- Added fromList connectivity function

- Added new dict 'stimParams' with support for IClamps

- Added 'start' param to NetStim populations

- Modified izhi2007 'u' starting value to be 0 instead of 0.2

- Modified izhi2007 'C' value and the section properties so that synaptic weights match HH

- Renamed NMDA synapses to AMPA

- Fixed bugs in tuts


## Version 0.4.5

- Fixed bug saving to JSON on single node

- Fixed plotting traces from using 'all' cells option

## Version 0.4.4

- Fixed bug when plottinc synMech traces

- Renamed 'pos' with 'loc' in recordTraces list

## Version 0.4.3

- Fixed bug in runSimWithIntervalFunc 

- Variable Netstims (NSLOCs) can now have noise > 0

## Version 0.4.2

- Placed show(block=False) in try except block since not supported by some graphic backends

- Create parallel context before re-creating net to avoid seg fault 

- Removed unnecessary modules in analysis.py

- Only call show() in analysis if some figure to show

## Version 0.4.1

- Fixed bug when distributing cells spatially based on xRange,yRange,zRange pop parameters

- Added axis labels to 2D visualization, and now works when running on multiple nodes too

- Reset Netstim random generators within runSim() so have reproducible results if working interactively 

## Version 0.4.0

- Fixed bug when distributing cells spatially based on normRange pop parameter

- Fixed bug in functional connectivity variables post_xnorm, post_ynorm, post_znorm

- Reversed ynorm based raster so higher y values are shown at the bottom (cortical-like)

- Added option to plot sync lines in raster and show sync measure

- Added 2D visualization of network cells and conns

- Fixed randomization of cell positions by adding lastGid

## Version 0.3.9

- Made synMech params independent of cell and referenced by labels (similar to NeuroML)

- Keep Neuron objects after sim so can explore, modify and/or rerun sim.

- Only gather data via py_alltoall if running on more than 1 node

## Version 0.3.8

- Fix recording of single cell of population when using MPI

- Fixed raster plotting based on NCD when using MPI

- Replaced save as .txt format with save as .csv

- Fixed bug when importing distributed mechanisms of cells

- importCell can use either *args or **kwargs

- Fixed bug in secLists implementation

- Removed mpl_toolkits.mplot3d import (unused and produced error in some Mac OS versions)

## Version 0.3.7

- Made conn functions more efficient using gid2lid and lid2gid

- Replaced 'syn' (synapse) with 'synMech' (synaptic mechanism) to avoid confusion with synaptic connections

## Version 0.3.6

- Fixed bug: STDP objects need to be stored so it works.

- Added support for SectionLists (modified format of importCell so also works)

- Fixed bugs: function-based connectivity 

## Version 0.3.5

- Fixed bugs: not checking connectivity rule conditions properly

- Fixed bug: number of connections depended on number of nodes

## Version 0.3.4

- Added option to add STDP plasticity and RL to connections

- Added option to run function at intervals during simulation, e.g. to interface with external program (such as virtual arm)

## Version 0.3.3

- Moved plot legend outside of plot area

- Changed order of raster population colors to make separation clearer

- Added option to select what cells to record/plot from separately; using new format with cells/pops in single list.

## Version 0.3.2

- Fixed bug: convergence connectivity produced error if used numeric value

## Version 0.3.1

- Added option to show and/or save to file the timing of initialization, cell creation, connection creation, setup recording, simulation run, data gathering, plotting, and saving. 

- Fixed bug: h.dt now set to value of simConfig['dt']

## Version 0.3

First version that was uploaded to pypi. Includes following features:

- Clear separation (modularization) of parameter specifications, network instantiation and NEURON simulation code.

- Easy-to-use, standardized, flexible, extensible and NEURON-independent format to specify parameters:
	- Populations
	- Cell property rules
	- Connectivity rules
	- Simulation configuration

- Support for cell location (eg. cortical depth) dependence of cell density and connectivity.

- Easy specification, importing and swapping of cell models (eg. point neuron vs multicompartment)

- Support for hybrid networks eg. combining point and multicompartment neurons.

- Multiple connectivity functions (eg. full, convergent, probabilistic) with optional parameters (eg. delay range)

- Support for user-defined connectivity functions.

- Populations, cell properties and connectivity rules can include reference to annotations (eg. for provenance).

- NEURON-independent instantiation of network (all cells, connections, ...) using Python objects and containers.

- NEURON-specific instantiation of network ready for simulation.

- Enables sharing of Python-based network objects, which can then be instantiated and simulated in NEURON.

- Easy MPI parallel simulation of network, including cell distribution across nodes an gathering of data from all nodes.

- Analysis and visualization of network (eg. connecitivity matrix) and simulation output (eg. voltage traces, raster plot)

- Data exporting/sharing to several formats (pickle, Matlab, JSON, HDF5) of the following:
	- Parameters/specifications
	- Instantiated networks
	- Simulation results