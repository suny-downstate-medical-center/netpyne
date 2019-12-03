# Version 0.9.4

- Added option to avoid creating connections with weight=0

- Made recording of dipoles optional with attribute cfg.recordDipoles

- Rotated conn matrix x-axis labels so can fit large matrices 

- Added 'removeWeightNorm' argument to plotConn() function

- Fixed file write permissions for evol optim batches

- Fixed bug calculating normally distributed rhythmic inputs - was using variance instead of std

- Fixed bug in iplotDipole when smoothing window size = 0

- Fixed bug in plotSpikeStats pop order

- Fixed bug is plots with scalebars

- Fixed bug in grid lines of plotConn

- Fixed bug in subConnParams by sorting conns to ensure reproducibility on different number of cores

- Fixed bug so uses 'Agg' backend if no display env variable e.g. in clusters


# Version 0.9.3.1

- Replaced deprecated imp module with importlib

- Fix to cellsGrid cell locations with normRange


# Version 0.9.3

- Improved conversion from SONATA format, including 300 biophys cell example

- Added saveCellConns, pt3dRelativeToCellLocation and invertedYCoord cfg options

- Added lineWidth as argument of plotRatePSD() and plotLFP()

- Modified plotLFP and plotRatePSD to use Morlet wavelet for PSD calculation

- Added lineWidth argument to some raster and LFP plots

- Added shuffling test to granger causality functions

- Fixed bug plotting traces with one fig per trace

- Fixed bug in granger functions - required conversion to int 

- Fixed bug in plotShape when cells sections not available

- Return meaningful cell info via 'repr' and 'str' for pointCell, compartCell

- Fixed spelling typos in documentation


# Version 0.9.2

- Support for saving simulation at intervals  

- Improved Python cell template import so can read section names from a Python list or dict of sections

- Fixed replicability issue across different number of cores when using 'connList' connectivity rules

- Improved speed performance of 'connList' connectivity rules

- Added option cfg.distributeSynsUniformly to locate synapses at uniformly across section list; if false, place one syn per section in section list 

- Updated RxD calcium buffering example

- Added netClamp example to re-simulate activity of single cell from network data

- Added support for recording and plotting variable time step

- Replaced spectrogram FFT method with Morlet wavelet method

- Updated installation instructions

- Added 'fontSize' argument to several plots

- Fixed issue completing batches in Python 3

- Fixed bug saving evolutionary optimization batch output file

- Fixed bug in plotShape()

- Fixed bug in plotSpikeStats()

- Fixed bug loading files with colons

- Fixed issue sorting raster by population and y coord


# Version 0.9.1.3

- Removed deprecated hold function from plotConn


# Version 0.9.1.2

- Set 'pandas==0.23.4' to avoid error 


# Version 0.9.1.1

- Fixed minor bug - axis font size changed from 12 to 2 by accident (change required for NetPyNE-UI)


# Version 0.9.1

- Updates to NeuroML converter 

- Add scalebar to rxd concentration plot

- Fixed bug so comparisons to basestring work in Python 2 and 3

- Fixed bug in string-based functions representation in GUI


# Version 0.9.0

- Added support for reaction-diffusion (RxD) and usage examples

- Improved performanced (speed) of connectivity algorithms 

- Major code refactor to split functions across modules and subpackages

- Switched to Python 3 as the default development environment

- Optimized implementation of raster and spikeHist plotting using Pandas

- Added support for recording spikes from only a subset of cells using e.g. cfg.recordCellsSpikes = ['E2']

- Support for exporting to SONATA standardized network format (Beta) 

- Support for Human Neocortical Neurosolver (HNN) dipole mechanisms

- Added option for filename to saveData()

- Removed pop cellModelClass when saving

- Removed cell h object keys when saving

- Added support for evolutionary algorithm optimization (via Inspyred) and usage example

- cfg.popAvgRates now accepts a time range to calculate rates (e.g. to discard initial period)

- All NEURON objects now accessible via ['hObj'] key within Python network structure

- Fixed bug in batch to allow having only grouped params

- Fixed bug initalizing batch 'mpi_bulletin' and batch tutorial example

- Fixed bug: removed '\_labelid' from netParams when saving

- Fixed bug: made self.scaleConnWeightModels False when not used (avoids saving weird dict in json)

- Fixed bug in Pickle file encoding so works in Python3 

- Fixed bug in convergence and divergence conn when repicking a value if postGid=preGid is randomly selected

- Fixed bug in rand initialization for string-based func with div conn

- Fixed issue in probabilistic connectivity random number generation to ensure replicability in Python 2 and 3.

NOTE on backward replicability: Due to several performance improvements and bug fixes to ensure future replicability in both Python 2 and 3, it won't be possible to replicate results of previous versions. 


# Version 0.7.9

- Extended metadata structure to interact with NetPyNE-UI

- Added preliminary data structures to support NEURON RxD

- Added plot RxD concentration to analysis

- Added netParams.correctBorder to compensate distance-dependent connectivity border effect

- Added option to run jobs directly on multiple mpi cores via Batch class 

- Added option for custom text in PBS or SLURM scripts to submit batch jobs

- Added option to filter LFP signal before ploting PSD

- Convert 'gid' to actual cell gid when used in point process params (useful for random seeds)

- Relaxed pyneuroml requirement so just shows a warning message 

- Preliminary function to save conns distributedly using HDF5

- Added function to validate string-based expressions

- Fixed bug: removed cell.\_segCoords and pop.\_morphSegCoords before saving to file

- Fixed rasterPlot pop label automated spacing

- Fixed bug: removed pandas requirement from LFP electrode module

- Fixed bug: updated rcParams text.fontsize to font.size

- Fixed bug: missing update of list-based loc in connList connections

- Fixed bug: delete sections after import cell only if section exists


# Version 0.7.8

- Added netParams.rotateCellsRandomly option to rotate cells randomly around y-axis

- Added netParams.defineCellShapes option to convert stylized cell geometries to 3d points 

- Added 'histogram' option to plotSpikeStats

- Improved shapePlot so generates 3d pts for stylized morphs and plots all cells by default

- Added showElectrodes and bkgColor options to shapePlot

- Adapted so can set cfg.createPyStruct=0 before creating conns to save memory on large nets

- Added option cfg.connRandomSecFromList=True to set if sec and loc are randomly chosen from list when synsPerConn=1 

- Added cfg.printSynsAfterRule to print total connections after each conn rule is applied 

- Fixed bug to ensure VecStim random streams are independent of simulation duration

- Fixed bug calculating avg pop rate in plotRaster when using subsets of pops

- Fixed bug LFP recording only applied to compartmental cells

- Fixed bug when using conn 'threshold' in verbose -- removed all since has no effect 

- Fixed bug when deleting sections -- needed sec.push() before

- Fixed bug in shapePlot figSize option

- Fixed format of git changeset stored -- removed 'g' prefix

- Fixed bug in Windows trying to get git changeset

- Fixed bug gathering LFP data

- Fixed bug importing global v_init from multiple cell files

- Fixed bug so gitChangeset() returns to orig folder even when git not installed

- Fixed bugs in plotConn -- missing rounding func and grouping by y interval


# Version 0.7.7

- Added LFP recording at arbitrary 3D locations

- Added plotting of LFP time series, PSD, freq vs time and electrode locations

- Updates to NeuroML conversion code.

- ShapePlot now shows segment diameters as linewidths (Python version)

- Added function to add 3D points (in NEURON+Python) from stylized geometry

- Connection sec and loc randomly chosen from list when synsPerConn=1 

- Set default NetStim noise to 0.0

- Fix synMech overwrite when importing multiple hoc/py cell templates

- Fixed bug importing multiple synMechs from hoc/py cell template

- Fixed bug using 'variable' NetStim (NSLOC)

- Fixed save method in NetParams to use ['net']['params']  

- Fixed bug using gap junctions with mpi (multiple cores)

- Fixed bug when creating conns afger loading json -- needed basestring instead of str

- Fixed bug when loading json with include format ('pop', 1) -- converted to list so added exception

- Fixed bug saving to .mat during batch sims

- Fixed bug in order of unique cell gids in analysis funcs 'include' param

- Fixed bug gathering data using the cfg.gatherSimOnlyData option

- Fixed bug where empty sections where created when recording from non-existing sections


# Version 0.7.6

- Added option to order raster spike trains by multipe tags (eg. ['pop', 'y'])

- Enable providing a 2D list of spike times to VecStim populations

- Added exception handling to analysis functions

- Updated saveLoadV1 examples to use compactConnFormat=True and saveCellSecs=False 

- Added cfg.rand123GlobalIndex to set global index used by all instances of the Random123 instances of Random

- plotTraces now plots any recorded cells if 'include' is None

- Made CVode object part of sim and simplified cvode calls

- Added sim.rename() wrapper function

- Added __rename__() method to dict class

- Fixed bug loading from compactConnFormat

- Fixed bug in IClamp: 'delay' -> 'del'

- Fixed bug calculating min convergece and divergence

- Fixed bug in plotRatePSD colors


# Version 0.7.5

- Improved NeuroML conversion support

- Make cfg.checkErrors = True by default, but set to False if using multiple cores or batch

- Added methods to rename netParams dict keys in a nested format (needed for GUI)

- Added analysis.plotSpikeStats() func to plot stats of cell rates, ISI CVs and synchronies 

- Added analysis.calculateRate() func to calculate avg and peak rate of pop subset at time range

- Added analysis.plotRates() func to plot avg and peak rate of different pop subsets at time range

- Added option to include list of pops or cells in 'include' arguments e.g. include=[['E4','E2'], [1,3]]

- Added cfg.compactConnFormat option to replace conns dict format with compact list format 

- Added option to plotConn() and plot2Dnet() to load data from compact format json files 

- Adapted python2 code so conversion to python3 via 2to3 command works straight away

- Added 'instantiate' argument to sim.load function

- Added 'dpi' argument to analysis.plotSpikeHist()

- Replaced init()/h.stdinit() with finitialize() so h.v_init and h.dt get set properly

- Removed call to h.stdrun() but made v_init a global in cfg.hParams and initialized h.tstop to cfg.duration

- Fixed bug setting globals that don't exist

- Fixed issue setting global variables when loading from json

- Fixed issue to make convergence+divergence connections randomization more robust and efficient (issue #254)

- Fixed bug in colors of plotSpikeHist

- Fixed bug in replaceDictODict() that lead to wrong results when importing cells

- Fixed bug when using sim.gatherOnlySimData

- Fixed bugs in saveLoadV1 example

- Fixed bug when generating subConn with createNEURONObj=False

# Version 0.7.4

- Added polarity param to analysis.plotEPSPAmp() 

- Added sim.gitChangeset() function and store netpyne_changeset in every output file

- Added function ijsonLoad() to load faster and save tags conns to json

- Fixed bug in convergence and divergence connectivity -- now fixed number and no self conns

- Fixed bug by converting tuples to strings when saving Matlab; now converts to lists

- Fixed bug use int as argument to np.full in fixedInterval variable

- Fixed bug that removed previously existing element from path during importCellParams()


# Version 0.7.3

- Option to create section lists based on y displacement from soma (addCellParamsSecList)

- Converted popParams, cellParams etc to object of their own class and added method to set param

- Added 'disynapticBias' option to increase probability of B->C conns if A->B and A->C exist 

- Added function analysis.calculateDisynaptic() to count number of disynaptic conns (A->B, B->C and A->C)

- Added 1 second between batch job submission to avoid saturating scheduler

- Fixed bug: init randomizer so params with string-based random func are independent of cores

- Fixed bug for newer pyplot versions: replace 'linewidths' with 'lw'


# Version 0.7.2

- Improved NeuroML importing/exporting

- Added error checking for simConfig

- Added popColors option to plotSpikeHist and plotRatePSD

- Added support to load params, cfg, net and simData from .mat files

- Made root section (with no parents) the source of spikes by default (issue #246)

- Added option to set initial cfg in batch sims

- Added option to set grouped params in Batch constructor

- Added option to not record time (to reduce output file size)

- Fixed bug: synMechFraction had no effect; replaced with synMechWeightFactor

- Fixed bug in modifyStims for NetStim 'interval' and 'rate' 

- Fixed bug importing cell -- use h.pop_section() to avoid stack overflow

- Fixed bug when adding stim NetStim where sec is a list

- Fixed bug when adding stim NetStim with multiple synMechs and synsPerConn>1


# Version 0.7.1

- Updates and bug fixes of NeuroML importer/exporter

- Added missing error checks and made error messages clearer 

- Added warning when point process mechanism (eg. VecStim) required for pop is not found

- Added 'ylim' option to plotTraces

- Changed 'postGid' to 'gid' in conditions of recordTraces

- Fixed bug: threshold in conns has no effect, have to use presyn cell threshold (issue #235)

- Fixed bug: avoid saving 't' multiple times when using multiple nodes

- Fixed bug: removed 'propList' param in list - was replaced by 'label'

- Fixed bug distributing cells of population with cellList (issue #235)

- Fixed bug saving to .mat: removed h.Random object from each pop

- Fixed bug: check if checkErrors exists in cfg before checking value

- Fixed bug importing multiple hoc cells consecutively (removed from memory properly)

# Version 0.7.0

IMPORTANT NOTE: NO BACKWARD REPRODUCIBILITY -- due to improvements in the random number generators it won't be possible to reproduce results of previous versions that required random values, e.g. random spike streams, connections or cell locations.

- Replaced python random package methods with more robust h.Random() methods (no backward reproducibility)

- Added netParams error checking (BETA version: set cfg.checkErrors = True to test) 

- Enabled use of VecStim spkTimes pops with individual list of cells

- Replaced 'pop' with 'popLabel' (added fix for backward compatibility) (issue #213)

- Can now add arbitrary set of spike times to VecStim pop 

- Dict with popColors can be passed to plotRaster() and plot2Dnet()

- Added analysis.plotEPSPAmp()

- readCmdLineArgs() now accepts default paths for cfg and netParams

- Added option to customize command in batch hpc runs (e.g. 'mpirun' vs 'ibrun')

- Added dpi param to plotRaster()

- Added recording of h.t to simData

- Replaced ions 'init_ext_conc' and 'init_int_conc' with 'o' and 'i' (issue #151)

- Replaced 'globs' with 'globals'

- Fixed bug in import of ion concentrations

- Fixed bug in title of plotTraces()

- Fixed bug when setting wrong num of weights or locs for synsPerConn>1

- Fixed bug: subConn rules now update weight if different weightNorm 

- Fixed bug: missing call to noiseFromRandom() for NetStims

- Fixed bug setting pop density with absoulute location ranges

- Fixed missing NeuroML message so only appears in master node

- Fixed bug in plotConn

- Fixed bug - stimTargetParams now accepts a list of secs for 'sec' param

# Version 0.6.9

- Improved support for NeuroML export

- Added option to skip batch job based on custom existing job filename (eg. 'skipCustom': '.run') 

- Added option to specify netParams .py file for batch 

- Modified hpc_torque batch to accept nodes and ppn

- New option to import cell with sections not inside an object 

- plotShape now shows real diameters in interviews by default

- Added option to set threshold when loading weightNorm

- Added support for conditions on recordTraces

- Fixed bug plotting NetStims (created as stims) in raster, spikeHist and ratePSD  

- Fixed bug in plotConn bar graphs

- Fixed bug: missing hRandom for NetStim populations

- Fixed bug: use Random123() instead of netstim.noiseFromRandom for NetStim stims

- Fixed bug: VectStim spike generation now reproducible for different durations

- Fixed bug in batch grouped params

- Fixed bug: getCellsList() only checked for tuples but when load from json converted to list

- Fixed bug so cell treshold is set by default to sim.net.defaultThreshold

- Fixed bug plotting overlayed spikeHist over raster plot

- Fixed bug in plotShape when includeAxon=False



# Version 0.6.8

- Keep track of last host after distributing cells of each pop (improves load balance) (issues #41 #196)

- Added option to run batch on HPC SLURM system (eg. SDSC Comet)

- Added cvode_atol option to cfg

- Improved plotShape() to use matplotlib and use colormap to show num syns 

- Batch params can now have an arbitrary number of levels in structure (eg. dict of list of dicts etc)

- Batch params can now be grouped ('group':True) so values vary together not combinatorally

- Removed pc.done() at the end of Batch.run() method so can run multiple batches from same script

- Added skipCfg option to batch

- Added cfg.saveCellSecs option to reduce save time and file size (secs available via netParams)

- Added cfg.saveCellConns option to reduce save time and file size 

- Modified code so 'cellModel' tag is optional

- Added renameCellParamsSec() method to netParams class  

- When importing cell global 'v_init' is stored as param for each section 

- Fixed small bugs when loading saved model

- Fixed bug when calling internal method _findPrePostCellsCondition()

- Fixed bug in subcellConn groupedSynMechs

- Fixed bug in subcellConn trying to add stims+conns to NetStims/VecStims

- Fixed bug in subcellConn so syns are not placed at loc 0.0 or 1.0 (error if syn uses ion)


# Version 0.6.7

- Added gridSpacing option to create populations with cells placed in grid with fixed spacing

- Added netParams functions: addCellParamsWeightNorm(), saveCellParamsRule() and loadCellParamsRule()

- Added option to importCell based on instantiated cell (not just template or class)

- Modified importCellParams to store mod mechanism global variables in cellRule['globals']

- Added support to export gap junctions to NeuroML

- Fixed bug during import that set section name to 'soma' if only 1 section


# Version 0.6.6

- Batch parameters can now include list or dict items

- Added 'weightNorm' param to sections so can normalize weight based on dendritic location

- Import cell function now has somaAtOrigin option to place the cell soma at coords 0,0,0

- Go back to using NetStim.noiseFromRandom, since noiseFromRandom123() only available in very recent versions

- Fixed bug in saveData option of figure plots

- Fixed bug passing figSize param to figures

- Fixed bug where gid only updated if cellParam rules were applied to the cell

- Fixed bug in importCell by deleting imported modules from sys.modules

- Fixed bug that prevented NetStim random noise generator from being initialized


# Version 0.6.5

- Added support for artificial cells (without sections) (issue #44)

- A single NetStim (within a population) can now be connected to multiple cells (issue #113)

- VecStim populations use same params as NetStims and allows for pulses at arbitrary times with different rates

- NetStim and VecStim population allow for a uniformly distributed rates in the form [min,max]

- Added option to run batch sims via mpi and bulletin board (master/slave) (issue #108)

- netParams.shape paramter to select either 'cuboid', 'cylinder' or 'ellipsoid' network shape (issue #26)

- analysis.plot2Dnet() 'view' param to select frontal ('xy') or top-down ('xz') view 

- analysis.plotConn() option to plot stacked bar graph, select different pre and post pops, synMech and syns vs conns

- Made distinction between number of connections and synaptic contacts (eg. can have 5 synsPerConn)

- New function netParams.addCellParamsSecList to create list of sections based on distance from soma

- Removed 'plast' and 'shape' from conns when not used (issue #177)

- Added option to center soma at origin when importing cell 

- Now using noiseFromRandom123() for NetStims() (issue #89)

- Fixed bug in readCmdLineArgs() 

- Fixed bug in saveData option of figure plots



# Version 0.6.4

- Added analysis.nTE() function to calculate normalized transfer entropy (issue #42)

- Added analysis.granger() function to calculate and plot Spectral Granger Causality (issue #42)

- Added analysis.plotRatePSD() to plot firing rate power spectral density 

- Added analysis.plotShape() to plot 3D morphology of cell and synapse locations

- Added option to fix soma depth for subcellular distributions based on 1d and 2d maps

- Added support for gap junction (electrical synapse) connections

- Improved import of multicompartmental cells from NeuroML2

- Added option to turn off graphics by adding -nogui from command line

- Added option to skip batch sims if output file already exists

- Added option to overlay pop labels and show avg rates to plotRaster() (issue #111)

- All section now include argument cell=self to differentiate them 

- Fixed travis script so checks all tuts and examples after each commit (issue #37)

- Fixed bug positioning cells with 3d geom

- Fixed bug in sim.clearAll by closing all figures instead of current (issue #168)

- Fixed bug: cache_efficient was not being turned on

- Fixed bug setting simConfig loaded from file

- Fixed bug in plotRaster inverseOrder option

- Fixed str vs basestring in analysis.py and simFuncs.py

- Fixed bug due to not inserting ions in section

# Version 0.6.3

- Added cvode_active simConfig option to set variable time step (issue #116)

- Added saving of avg pop rates

- Added save method to SimConfig and NetParams class

- Fixed bug importing 3d cell geometries

- Fixed bug in readCmdLine func

- Fixed bug reading from json (str vs unicode)

- Fixed bug setting mech param values for nseg>1

# Version 0.6.2

- Added importing of cell ion parameters (eg. 'ena' or 'ek')

- Added backupCfgFile (eg. ['cfg.py', 'backupcfg/']) to simConfig to copy cfg file after run

- Added gatherOnlySimData to simConfig to gather only simulation data and not cells or pops

- Added simLabel and saveFolder to simConfig (can be used instead of filename)

- Added printRunTime to simConfig to print run time (in sec) during execution

- Added printPopAvgRates to simConfig to print population avg firing rates after run 

- Automatic saving of netpyne and netParams version to file

- Moved creation of fih functions to set cell vinit from setupRecording() to preRun()

- Can now load netParams and simConfig from file without setting in sim

- Added sim.readCmdLineArgs to read simConfig and netParams filepaths from command line 

- Can now access NEURON's h module via sim.h

- Fixed bug so can load netParams and simConfig without initializing sim

- Fixed bug that prevented mechanism properties with value 0.0 from being set

- Fixed bug in code to distribute cells (converted numCells from float to int)

- Fixe bug in plotTraces

# Version 0.6.1

- Added global boolean variable netpyne.__gui__ to enable/disable graphics (issue #150)

- Spike histogram fixes: axis labels only in 1st subplot, limit time range, tight_layout only if <5 subplots

- Fixed bug so multiple traces figures are saved to separate files (issue #166)

- Fixed bug when using point process-based cells that include synapses (eg. Izhi2007a)

- Fixed bug where spike hist subplot didn't match raster axis

- Fixed bug when loading data from file with multiple cores  

- Fixed bug so modify functions work with multiple cores 

# Version 0.6.0

- Added option to shape conn weights dynamically to create temporal patterns (issue #33)

- Store all params of synMechs exhaustively instead of by reference (issue #139)

- Added netParams.importCellParamsFromNet() to import parameters of multiple cells from existing network (issue #154)

- Added modifySynMechs function

- Added option to record from all synMechs of a type (eg. 'AMPA')

- Fixed bugs and improved efficiency of modify, modifyConns and modifyStims function

- Fixed bug plotting traces

# Version 0.5.9

- Improved NeuroML2 import functions (issue #12)

- Added support for homeostatic scaling synapse (requires self NetCon) (issue #141)

- Added method to convert NetParams and SimConfig objects to dicts (issue #141)

- Fixed NetParams and SimConfig constructors so arguments are converted to Dict/ODict (issue #141)

- Added sim.loadBalance() func to calculate and print load balance information (issue #77)

## Version 0.5.8

- Fixed bug (introduced during debugging) that prevented random seeds from working properly

## Version 0.5.7

- Improved NeuroML import/export functions

- Added option for cache_efficient (optimized load balance when many cores) (issue #77)

- Added sim.clearAll() function to clear all objects in memory and avoid leaks

- Cleared variables after gathering from multiple nodes to avoid memory leak

- Separated common runSim() commands into preRun() (issue #83)

- Fixed bugs in net.modifyStims() method

## Version 0.5.6

- Only load neuroml libraries and functions if installed to avoid error when importing sim

- Disable subcellular connectivity since wasn't modifying the synMechs correctly. 

## Version 0.5.5

- New example using Allen Institute cells showing how to save large net and reload for simulation

- Improved export/import from/to NeuroML2 (issue #12)

- All structures (including Dict and ODict) can now  be saved and loaded via json

- Added option to use separate simConfig when loading data from file

- saveData() calls gatherData() if required 

- saveData() returns string with full path of saved file (issue #127)

- Fixed bugs so its possible to create and save Python structure independently of NEURON objects

- Fixed bug that created 2 instead of 1 NetStims per cell

- Fixed bug regarding mutable default args in Python funcs

- Fixed bug so NetStim stim params are set to default if missing 

## Version 0.5.4

- Access to nested dictionaries via dot notation (secs.soma.geom) using new inherited classes Dict() and ODict() (issue #123)

- 'hSection' replaced with 'hSec' 

- Added sim.popAvgRates() to calculate and optionally print population avg rates 

- Functions to modify cells, conns or stims also update sim.allCells (issue #59)

- Fixed bug so can modify funcs now accept lists of strings (issue #59)

- Fixed bug when recording traces of relative cell indices of populations across multiple nodes

## Version 0.5.3

- Functions to modify parameters of cells, conns and stims in an instantiated network (issue #59)

- Added label of param rule used to create cells, conns and stims, so can modify later  (issue #59)

- Ordered sim.net.allCells by gid

- Option to save figures with same name as data

- Added support for VClamp list params (issue #32)

- Fixed bug when creating pops consisiting of lists of cells 

## Version 0.5.2

- Fixed bug that gave error since trying to import removed module default.py

## Version 0.5.1

- Easier and more consistent format for high-level specifications (issue #103):

	- replaced default.py with specs.py which defines classes NetParams and SimConfig

	- netParams and simConfig are now objects of class NetParams and SimConfig, respectively

	- Can use object methods to add params, eg. netParams.addPopParams(label, params)

	- All structures within netParams and simConfig are now OrderedDicts so can be referenced by label/key

	- If no label is assigned, then an increasing number is automatically used as label

	- Split netParams.stimParams into netParams.stimSourceParams and netParams.stimTargetParams (both OrderedDicts)

	- Simplified/clarified keys: 'conditions' -> 'conds', 'sections' -> 'secs', 'preTags' -> 'preConds', 'postTags' -> 'postConds' 

	- Added netParams.importCellParams() to simplify  

- Added sim wrappers and modified names of existing ones to make consistent

- Selectively save data to file: netParams, net, simConfig and/or simData (issue #30)

- Added functions to load netParams, net, simConfig and/or simData from file (issue #30)

- Added 'rerun' option to plotTraces() 

- Added function to get cell object by gid, sim.cellByGid(gid)  

- Fixed bug that was slowing down STDP by creating new h.Section() -- now uses existing.

- Fixed bug so vinit gets set for all segments in a section.

- Fixed bug related to readArgs() when running from IPYnotebook.

- Fixed bug related to plasticity in cells with V not in section (eg. Izhi2007a)

## Version 0.5.0

- Added option 'dataSaveInclude' to select what data to save to file (issue #30)

- Added sim.net.allPops which contains all cellGids of each when running on >1 nodes (issue #30)

- Connectivity matrix can now be grouped by numeric tags in intervals (eg. cortical depth y in 50 um intervals) (issue #92)

- Added support for all stims (VClamp, SEClamp, AlphaSynapse, etc) and can specify any of the stim params (amp, dur, delay,etc) as a function (eg. 'uniform(a,b)' or '2*post_ynorm') (issue #32)

- Fixed bugs so plotRaster() is identical when running on >1 nodes, and is ordered by gid correctly 

- Fixed bug so can have multiple plot function calls even when one of them is False 

## Version 0.4.9

- Modified format of simConfig analysis options to make it equivalent to calling analysis functions (issue #69)

- Improved plotRaster() function to add customizable options (select cells, time range, order, overlay histogram, and others) (issue #39)

- Improved plotTraces() function to add customizable options (select cells, time range, arrage by cell or trace, and others) (issue #39)

- Improved plot2Dnet() function to add customizable options (select cells, show connections, and others) (issue #39)

- Added spikeHist() function to plot spike histogram with customizable options (select cells, time range, bin size, and others) (issue #63)

- Added plotConn() function to plot spike histogram with multiple customizable options (select cells, feature, order, and others) (issue #39)

- Added option to save figure, save figure data, specify figure size, and show figure to all analysis/plotting functions (issue #39)

- Fixed bug when generating function-based random probability values -- made random stream independent 

- Fixed bug when generating density-based random cell locations -- made random stream independent (issue #93)


## Version 0.4.8

- Removed framework and init modules, and consolidated in sim module (so just need: 'from netpyne import sim')

- Added option to specify weight scale factor separately for each cell model, and for NetStims (issue #69)

- Conn rules can now have list of synMechs (eg. [AMPA, NMDA]) and synMechWeightFactor (eg. [1.0, 0.1]) (issue #69)

- Conn rules allow list of weights, delays and/or locs for each synMech in list (issue #69)

- Conn rules allow synsPerConn and loc to be described functionally (at the cell connection level) (eg. 'uniform(5,2)') (issue #69)

- Conn rules allow list of weights, delays, and/or locs when synsPerConn > 1 (issue #69)

- Conn rules allow 2D list of weights, delays, and/or locs when have list of synMechs and synsPerConn > 1 (issue #69)

- Conn rules allow list of sections or sectionList when synsPerConn > 1; synMechs distributed uniformly (loc list not allowed) (issue #69)

- Extended fromList connectivity function so can also provide synapse locs (issue #69)

- Added separate wrapper sim functions to create and simulate the network  

- Sim functions use simConfig and netParams from __main__ as default (if not specified) 

- Connections between NetStims and cells are included in conn list (issue #69)

- Fixed bug so can create Python and NEURON objects for connections independently (issue #69)


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

- Fixed bug: h.dt now set to value of simConfig.dt

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