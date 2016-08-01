"""
specs.py 
NetParams is a class containing a set of network parameters using a standardized structure
SimConfig is a class containing a set of simulation configurations using a standardized structure
Contributors: salvadordura@gmail.com
"""

from collections import OrderedDict
from netpyne import utils

###############################################################################
# Dict class (allows dot notation for dicts)
###############################################################################

class Dict(dict):

    __slots__ = []#'todict', 'fromdict', 'dotify', 'undotify']

    def __init__(*args, **kwargs):
        self = args[0]
        args = args[1:]
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        if args:
            self.update(self.dotify(args[0]))
        if len(kwargs):
            self.update(self.dotify(kwargs))
   
    # def __contains__(self, k):
    #     try:
    #         print k
    #         print self
    #         #print hasattr(self, k)
    #         print dict.__contains__(self, k)
    #         #return hasattr(self, k) or dict.__contains__(self, k)
    #         return dict.__contains__(self, k)
    #     except:
    #         return False
    
    # only called if k not found in normal places 
    def __getattr__(self, k):
        try:
            # Throws exception if not in prototype chain
            return object.__getattribute__(self, k)
        except AttributeError:
            try:
                return self[k]
            except KeyError:
                raise AttributeError(k)
    
    def __setattr__(self, k, v):
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                self[k] = v
            except:
                raise AttributeError(k)
        else:
            object.__setattr__(self, k, v)
    
    def __delattr__(self, k):
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                del self[k]
            except KeyError:
                raise AttributeError(k)
        else:
            object.__delattr__(self, k)
    
    def todict(self):
        return self.undotify(self)

    def fromdict(self, d):
        d = self.dotify(d) 
        for k,v in d.iteritems():
            self[k] = v
    
    def __repr__(self):
        keys = self.keys()
        args = ', '.join(['%s: %r' % (key, self[key]) for key in keys])
        return '{%s}' % (args)
    

    def dotify(self, x):
        if isinstance(x, dict):
            return Dict( (k, self.dotify(v)) for k,v in x.iteritems() )
        elif isinstance(x, (list, tuple)):
            return type(x)( self.dotify(v) for v in x )
        else:
            return x

    def undotify(self, x): 
        if isinstance(x, dict):
            return dict( (k, self.undotify(v)) for k,v in x.iteritems() )
        elif isinstance(x, (list, tuple)):
            return type(x)( self.undotify(v) for v in x )
        else:
            return x

    def __missing__(self, key):
        if not key.startswith('_ipython'):
            value = self[key] = Dict()
            return value

    def __getstate__ (self):
        return self.todict()

    def __setstate__ (self, d):
        self = self.fromdict(d)


###############################################################################
# ODict class (allows dot notation for ordered dicts)
###############################################################################

class ODict(OrderedDict):
   
    def __init__(self, *args, **kwargs):
        super(ODict, self).__init__(*args, **kwargs)

    def __contains__(self, k):
        try:
            return hasattr(self, k) or dict.__contains__(self, k)
        except:
            return False
    
    # only called if k not found in normal places 
    def __getattr__(self, k):
        try:
            # Throws exception if not in prototype chain
            return super(ODict, self).__getattr__(k)
        except AttributeError:
            try:
                return super(ODict, self).__getitem__(k)
            except KeyError:
                raise AttributeError(k)

    
    def __setattr__(self, k, v):
        if k.startswith('_OrderedDict'):
            super(ODict, self).__setattr__(k,v)
        else:
            try:
                super(ODict, self).__setitem__(k,v)
            except:
                raise AttributeError(k)
    

    def __getitem__(self, k):
        return super(ODict, self).__getitem__(k)

    
    def __setitem__(self, k, v):
        super(ODict, self).__setitem__(k,v)

    def __delattr__(self, k):
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                super(ODict, self).__delattr__(k)
            except KeyError:
                raise AttributeError(k)
        else:
            object.__delattr__(self, k)
    
    def toOrderedDict(self):
        return self.undotify(self)

    def fromOrderedDict(self, d):
        d = self.dotify(d) 
        for k,v in d.iteritems():
            self[k] = v
    
    def __repr__(self):
        keys = self.keys()
        args = ', '.join(['%s: %r' % (key, self[key]) for key in keys])
        return '{%s}' % (args)
    

    def dotify(self, x):
        if isinstance(x, OrderedDict):
            return ODict( (k, self.dotify(v)) for k,v in x.iteritems() )
        elif isinstance(x, dict):
            return Dict( (k, self.dotify(v)) for k,v in x.iteritems() )
        elif isinstance(x, (list, tuple)):
            return type(x)( self.dotify(v) for v in x )
        else:
            return x

    def undotify(self, x):  
        if isinstance(x, OrderedDict):
            return OrderedDict( (k, self.undotify(v)) for k,v in x.iteritems() ) 
        elif isinstance(x, dict):
            return dict( (k, self.undotify(v)) for k,v in x.iteritems() )
        elif isinstance(x, (list, tuple)):
            return type(x)( self.undotify(v) for v in x )
        else:
            return x

    # def __missing__(self, key):
    #     if not key.startswith('_ipython'):
    #         value = self[key] = Dict()
    #         return value

    def __getstate__ (self):
        return self.toOrderedDict()

    def __setstate__ (self, d):
        self = self.fromOrderedDict(d)


###############################################################################
# NETWORK PARAMETERS CLASS
###############################################################################

class NetParams (object):

    def __init__(self, netParamsDict=None):
        self._labelid = 0
        # General network parameters
        self.scale = 1   # scale factor for number of cells 
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
        self.cellParams = ODict()

        # Population params dict
        self.popParams = ODict()  # create list of populations - each item will contain dict with pop params
        self.popTagsCopiedToCells = ['cellModel', 'cellType']

        # Synaptic mechanism params dict
        self.synMechParams = ODict()        

        # Connectivity params dict
        self.connParams = ODict()  

        # Subcellular connectivity params dict
        self.subConnParams = ODict()  

        # Stimulation source and target params dicts
        self.stimSourceParams = ODict()  
        self.stimTargetParams = ODict() 

        # fill in params from dict passed as argument
        if netParamsDict:
            for k,v in netParamsDict.iteritems(): 
                setattr(self, k, v)

    def addCellParams(self, label=None, params=None):
        if not label: 
            label = int(self._labelid)
            self._labelid += 1
        self.cellParams[label] = Dict(params)

    def addPopParams(self, label=None, params=None):
        if not label: 
            label = int(self._labelid)
            self._labelid += 1
        self.popParams[label] = Dict(params)

    def addSynMechParams(self, label=None, params=None):
        if not label: 
            label = int(self._labelid)
            self._labelid += 1
        self.synMechParams[label] = Dict(params)

    def addConnParams(self, label=None, params=None):
        if not label: 
            label = int(self._labelid)
            self._labelid += 1
        self.connParams[label] = Dict(params)

    def addSubConnParams(self, label=None, params=None):
        if not label: 
            label = int(self._labelid)
            self._labelid += 1
        self.subConnParams[label] = Dict(params)

    def addStimSourceParams(self, label=None, params=None):
        if not label: 
            label = int(self._labelid)
            self._labelid += 1
        self.stimSourceParams[label] = Dict(params)

    def addStimTargetParams(self, label=None, params=None):
        if not label: 
            label = int(self._labelid)
            self._labelid += 1
        self.stimTargetParams[label] = Dict(params)

    def importCellParams(self, label, conds, fileName, cellName, cellArgs=None, importSynMechs=False):
        if cellArgs is None: cellArgs = {}
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
        self.includeParamsLabel = True  # include label of param rule that created that cell, conn or stim
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
        self.analysis = ODict()

        # fill in params from dict passed as argument
        if simConfigDict:
            for k,v in simConfigDict.iteritems(): 
                setattr(self, k, v)

    def addAnalysis(self, func, params):
        self.analysis[func] =  params

