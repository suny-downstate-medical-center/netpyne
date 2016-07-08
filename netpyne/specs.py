"""
specs.py 
NetParams is a class containing a set of network parameters using a standardized structure
SimConfig is a class containing a set of simulation configurations using a standardized structure
Contributors: salvadordura@gmail.com
"""

from collections import OrderedDict
from netpyne import utils

###############################################################################
# NETWORK PARAMETERS CLASS
###############################################################################

class NetParams (object):

	def __init__(self, netParamsDict=None):
		self._labelid = 0
		# General network parameters
		self.scale = 1 	 # scale factor for number of cells 
		self.sizeX = 100 # x-dimension (horizontal length) size in um
		self.sizeY = 100 # y-dimension (vertical height or cortical depth) size in um
		self.sizeZ = 100 # z-dimension (horizontal depth) size in um


		## General connectivity parameters
		self.scaleConnWeight = 1 # Connection weight scale factor (NetStims not included)
		self.scaleConnWeightNetStims = 1 # Connection weight scale factor for NetStims
		self.scaleConnWeightModels = {} # Connection weight scale factor for each cell model eg. {'Izhi2007': 0.1, 'Friesen': 0.02}
		self.defaultWeight = 1  # default connection weight
		self.defaultDelay = 1  # default connection delay (ms)
		self.defaultThreshold = 10  # default Netcon threshold (mV)
		self.propVelocity = 500.0  # propagation velocity (um/ms)
		 
		# Cell params dict
		self.cellParams = OrderedDict()

		# Population params dict
		self.popParams = OrderedDict()  # create list of populations - each item will contain dict with pop params
		self.popTagsCopiedToCells = ['popLabel', 'cellModel', 'cellType']

		# Synaptic mechanism params dict
		self.synMechParams = OrderedDict()		

		# Connectivity params dict
		self.connParams = OrderedDict()  

		# Subcellular connectivity params dict
		self.subConnParams = OrderedDict()  

		# Stimulation source and target params dicts
		self.stimSourceParams = OrderedDict()  
		self.stimTargetParams = OrderedDict() 

		# fill in params from dict passed as argument
		if netParamsDict:
			for k,v in netParamsDict.iteritems(): 
				setattr(self, k, v)

	def addCellParams(self, label=None, params={}):
		if not label: 
			label = int(self._labelid)
			self._labelid += 1
		self.cellParams[label] = params

	def addPopParams(self, label=None, params={}):
		if not label: 
			label = int(self._labelid)
			self._labelid += 1
		self.popParams[label] = params

	def addSynMechParams(self, label=None, params={}):
		if not label: 
			label = int(self._labelid)
			self._labelid += 1
		self.synMechParams[label] = params

	def addConnParams(self, label=None, params={}):
		if not label: 
			label = int(self._labelid)
			self._labelid += 1
		self.connParams[label] = params

	def addSubConnParams(self, label=None, params={}):
		if not label: 
			label = int(self._labelid)
			self._labelid += 1
		self.subConnParams[label] = params

	def addStimSourceParams(self, label=None, params={}):
		if not label: 
			label = int(self._labelid)
			self._labelid += 1
		self.stimSourceParams[label] = params

	def addStimTargetParams(self, label=None, params={}):
		if not label: 
			label = int(self._labelid)
			self._labelid += 1
		self.stimTargetParams[label] = params

	def importCellParams(self, label, conds, fileName, cellName, cellArgs={}, importSynMechs=False):
		if not label: 
			label = int(self._labelid)
			self._labelid += 1
		secs, secLists, synMechs = utils.importCell(fileName, cellName, cellArgs)
		cellRule = {'conds': conds, 'secs': secs, 'secLists': secLists}
		self.addCellParams(label, cellRule)

		if importSynMechs:
			for synMech in synMechs: self.addSynMechParams(synMech.pop('label'), synMech)

		return self.cellParams[label]


###############################################################################
# SIMULATION CONFIGURATION CLASS
###############################################################################

class SimConfig (object):

	def __init__(self, simConfigDict = None):
		# Simulation parameters
		self.duration = self.tstop = 1*1e3 # Duration of the simulation, in ms
		self.dt = 0.025 # Internal integration timestep to use
		self.hParams = {'celsius': 6.3, 'clamp_resist': 0.001}  # parameters of h module 
		self.seeds = {'conn': 1, 'stim': 1, 'loc': 1} # Seeds for randomizers (connectivity, input stimulation and cell locations)
		self.createNEURONObj= True  # create HOC objects when instantiating network
		self.createPyStruct = True  # create Python structure (simulator-independent) when instantiating network
		self.timing = True  # show timing of each process
		self.saveTiming = False  # save timing data to pickle file
		self.verbose = False  # show detailed messages 

		# Recording 
		self.recordCells = []  # what cells to record from (eg. 'all', 5, or 'PYR')
		self.recordTraces = {}  # Dict of traces to record 
		self.recordStim = False  # record spikes of cell stims
		self.recordStep = 0.1 # Step size in ms to save data (eg. V traces, LFP, etc)

		# Saving
		self.saveDataInclude = ['netParams', 'netCells', 'netPops', 'simConfig', 'simData']
		self.filename = 'model_output'  # Name of file to save model output
		self.timestampFilename = False  # Add timestamp to filename to avoid overwriting
		self.savePickle = False # save to pickle file
		self.saveJson = False # save to json file
		self.saveMat = False # save to mat file
		self.saveCSV = False # save to txt file
		self.saveDpk = False # save to .dpk pickled file
		self.saveHDF5 = False # save to HDF5 file 
		self.saveDat = False # save traces to .dat file(s)

		# Analysis and plotting 
		self.analysis = OrderedDict()

		# fill in params from dict passed as argument
		if simConfigDict:
			for k,v in simConfigDict.iteritems(): 
				setattr(self, k, v)

	def addAnalysis(self, func, params):
		self.analysis[func] =  params

