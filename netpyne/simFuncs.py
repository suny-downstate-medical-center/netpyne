"""
simFunc.py 

Contains functions related to the simulation (eg. setupRecording, runSim) 

Contributors: salvadordura@gmail.com
"""

__all__ = []
__all__.extend(['initialize', 'setNet', 'setNetParams', 'setSimCfg', 'createParallelContext', 'setupRecording', 'clearAll']) # init and setup
__all__.extend(['runSim', 'runSimWithIntervalFunc', '_gatherAllCellTags', '_gatherCells', 'gatherData'])  # run and gather
__all__.extend(['saveData', 'loadSimCfg', 'loadNetParams', 'loadNet', 'loadSimData', 'loadAll']) # saving and loading
__all__.extend(['popAvgRates', 'id32', 'copyReplaceItemObj', 'clearObj', 'replaceItemObj', 'replaceNoneObj', 'replaceFuncObj', 'replaceDictODict', 'readArgs', 'getCellsList', 'cellByGid',\
'timing',  'version', 'gitversion', 'loadBalance'])  # misc/utilities

import sys
from time import time
from datetime import datetime
import cPickle as pk
import hashlib 
from numbers import Number
from copy import copy
from specs import Dict, ODict
from collections import OrderedDict
import math
from neuron import h, init # Import NEURON
try:
    import neuroml
    from pyneuroml import pynml
    
    __all__.extend(['exportNeuroML2'])  # export
    __all__.extend(['importNeuroML2'])  # import
    neuromlExists = True
except:
    print('(Note: NeuroML import failed; import/export functions will not be available)')
    neuromlExists = False

import sim, specs

import pprint
pp = pprint.PrettyPrinter(depth=6)


###############################################################################
# initialize variables and MPI
###############################################################################
def initialize (netParams = None, simConfig = None, net = None):
    if netParams is None: netParams = {} # If not specified, initialize as empty dict
    if simConfig is None: simConfig = {} # If not specified, initialize as empty dict
    if hasattr(simConfig, 'popParams') or hasattr(netParams, 'duration'):
        print('Error: seems like the sim.initialize() arguments are in the wrong order, try initialize(netParams, simConfig)')
        sys.exit()

    sim.simData = Dict()  # used to store output simulation data (spikes etc)
    sim.fih = []  # list of func init handlers
    sim.rank = 0  # initialize rank
    sim.timingData = Dict()  # dict to store timing

    sim.createParallelContext()  # iniitalize PC, nhosts and rank
    
    sim.setSimCfg(simConfig)  # set simulation configuration
    
    if sim.rank==0: 
        sim.timing('start', 'initialTime')
        sim.timing('start', 'totalTime')

    if net:
        sim.setNet(net)  # set existing external network
    else: 
        sim.setNet(sim.Network())  # or create new network

    sim.setNetParams(netParams)  # set network parameters

    #sim.readArgs()  # read arguments from commandline

    sim.timing('stop', 'initialTime')


###############################################################################
# Set network object to use in simulation
###############################################################################
def setNet (net):
    sim.net = net

###############################################################################
# Set network params to use in simulation
###############################################################################
def setNetParams (params):
    if params and isinstance(params, specs.NetParams):
        sim.net.params = params
    elif params and isinstance(params, dict):
        sim.net.params = specs.NetParams(params)
    else:
        sim.net.params = specs.NetParams()

###############################################################################
# Set simulation config
###############################################################################
def setSimCfg (cfg):
    if cfg and isinstance(cfg, specs.SimConfig):
        sim.cfg = cfg  # set 
    elif cfg and isinstance(cfg, dict):
        sim.cfg = specs.SimConfig(cfg) # fill in with dict
    else:
        sim.cfg = specs.SimConfig()  # create new object


###############################################################################
# Create parallel context
###############################################################################
def createParallelContext ():
    sim.pc = h.ParallelContext() # MPI: Initialize the ParallelContext class
    sim.pc.done()
    sim.nhosts = int(sim.pc.nhost()) # Find number of hosts
    sim.rank = int(sim.pc.id())     # rank or node number (0 will be the master)

    if sim.rank==0: 
        sim.pc.gid_clear()


###############################################################################
# Load netParams from cell
###############################################################################
def loadNetParams (filename, data=None):
    if not data: data = _loadFile(filename)
    print('Loading netParams...')
    if 'net' in data and 'params' in data['net']:
        setNetParams(data['net']['params'])
    else:
        print('netParams not found in file %s'%(filename))

    pass


###############################################################################
# Load cells and pops from file and create NEURON objs
###############################################################################
def loadNet (filename, data=None, instantiate=True):
    if not data: data = _loadFile(filename)
    if 'net' in data and 'cells' in data['net'] and 'pops' in data['net']:
        sim.timing('start', 'loadNetTime')
        print('Loading net...')
        sim.net.allPops = data['net']['pops']
        sim.net.allCells = data['net']['cells']
        if instantiate:
            if sim.cfg.createPyStruct:
                for popLoadLabel, popLoad in data['net']['pops'].iteritems():
                    pop = sim.Pop(popLoadLabel, popLoad['tags'])
                    pop.cellGids = popLoad['cellGids']
                    sim.net.pops[popLoadLabel] = pop
                for cellLoad in data['net']['cells']:
                    # create new Cell object and add attributes, but don't create sections or associate gid yet
                    cell = sim.Cell(gid=cellLoad['gid'], tags=cellLoad['tags'], create=False, associateGid=False)  
                    cell.secs = cellLoad['secs']
                    cell.conns = cellLoad['conns']
                    cell.stims = cellLoad['stims']
                    sim.net.cells.append(cell)
                print('  Created %d cells' % (len(sim.net.cells)))
                print('  Created %d connections' % (sum([len(c.conns) for c in sim.net.cells])))
                print('  Created %d stims' % (sum([len(c.stims) for c in sim.net.cells])))

                # only create NEURON objs, if there is Python struc (fix so minimal Python struct is created)
                if sim.cfg.createNEURONObj:  
                    if sim.cfg.verbose: print("  Adding NEURON objects...")
                    # create NEURON sections, mechs, syns, etc; and associate gid
                    for cell in sim.net.cells:
                        prop = {'secs': cell.secs}
                        cell.createNEURONObj(prop)  # use same syntax as when creating based on high-level specs 
                        cell.associateGid()  # can only associate once the hSection obj has been created
                    # create all NEURON Netcons, NetStims, etc
                    for cell in sim.net.cells:
                        cell.addStimsNEURONObj()  # add stims first so can then create conns between netstims
                        cell.addConnsNEURONObj()

                    print('  Added NEURON objects to %d cells' % (len(sim.net.cells)))

            if sim.cfg.timing: sim.timing('stop', 'loadNetTime')
            print('  Done; re-instantiate net time = %0.2f s' % sim.timingData['loadNetTime'])
    else:
        print('  netCells and/or netPops not found in file %s'%(filename))


###############################################################################
# Load simulation config from file
###############################################################################
def loadSimCfg (filename, data=None):
    if not data: data = _loadFile(filename)
    print('Loading simConfig...')
    if 'simConfig' in data:
        setSimCfg(data['simConfig'])
    else:
        print('  simConfig not found in file %s'%(filename))

    pass


###############################################################################
# Load netParams from cell
###############################################################################
def loadSimData (filename, data=None):
    if not data: data = _loadFile(filename)
    print('Loading simData...')
    if 'simData' in data:
        sim.allSimData = data['simData']
    else:
        print('  simData not found in file %s'%(filename))

    pass


###############################################################################
# Load all data in file
###############################################################################
def loadAll (filename, data=None):
    if not data: data = _loadFile(filename)
    loadSimCfg(filename, data=data)
    loadNetParams(filename, data=data)
    loadNet(filename, data=data)
    loadSimData(filename, data=data)

    
###############################################################################
# Load data from file
###############################################################################
def _loadFile (filename):
    
    if sim.cfg.timing: sim.timing('start', 'loadFileTime')
    ext = filename.split('.')[1]

    # load pickle file
    if ext == 'pkl':
        import pickle
        print('Loading file %s ... ' % (filename))
        with open(filename, 'r') as fileObj:
            data = pickle.load(fileObj)

    # load dpk file
    elif ext == 'dpk':
        import gzip
        print('Loading file %s ... ' % (filename))
        #fn=sim.cfg.filename #.split('.')
        #gzip.open(fn, 'wb').write(pk.dumps(dataSave)) # write compressed string
        print('NOT IMPLEMENTED!')

    # load json file
    elif ext == 'json':
        import json
        print('Loading file %s ... ' % (filename))
        with open(filename, 'r') as fileObj:
            data = json.load(fileObj, object_pairs_hook=OrderedDict)

    # load mat file
    elif ext == 'mat':
        from scipy.io import savemat 
        print('Loading file %s ... ' % (filename))
        #savemat(sim.cfg.filename+'.mat', replaceNoneObj(dataSave))  # replace None and {} with [] so can save in .mat format
        print('Finished saving!')

    # load HDF5 file (uses very inefficient hdf5storage module which supports dicts)
    elif ext == 'saveHDF5':
        #dataSaveUTF8 = _dict2utf8(replaceNoneObj(dataSave)) # replace None and {} with [], and convert to utf
        import hdf5storage
        print('Loading file %s ... ' % (filename))
        #hdf5storage.writes(dataSaveUTF8, filename=sim.cfg.filename+'.hdf5')
        print('NOT IMPLEMENTED!')

    # load CSV file (currently only saves spikes)
    elif ext == 'csv':
        import csv
        print('Loading file %s ... ' % (filename))
        writer = csv.writer(open(sim.cfg.filename+'.csv', 'wb'))
        #for dic in dataSave['simData']:
        #    for values in dic:
        #        writer.writerow(values)
        print('NOT IMPLEMENTED!')

    # load Dat file(s) 
    elif ext == 'dat': 
        print('Loading file %s ... ' % (filename))
        print('NOT IMPLEMENTED!')
        # traces = sim.cfg.recordTraces
        # for ref in traces.keys():
        #     for cellid in sim.allSimData[ref].keys():
        #         dat_file_name = '%s_%s.dat'%(ref,cellid)
        #         dat_file = open(dat_file_name, 'w')
        #         trace = sim.allSimData[ref][cellid]
        #         print("Saving %i points of data on: %s:%s to %s"%(len(trace),ref,cellid,dat_file_name))
        #         for i in range(len(trace)):
        #             dat_file.write('%s\t%s\n'%((i*sim.cfg.dt/1000),trace[i]/1000))

    else:
        print('Format not recognized for file %s'%(filename))
        return 

    if sim.cfg.timing: sim.timing('stop', 'loadFileTime')
    print('  Done; file loading time = %0.2f s' % sim.timingData['loadFileTime'])
   

    return data

###############################################################################
# Clear all sim objects in memory
###############################################################################
def clearAll():
    # clean up
    sim.pc.barrier() 
    sim.pc.gid_clear()                    # clear previous gid settings

    # clean cells and simData in all nodes
    sim.clearObj([cell.__dict__ for cell in sim.net.cells])
    sim.clearObj([stim for stim in sim.simData['stims']])
    for key in sim.simData.keys(): del sim.simData[key]  
    for c in sim.net.cells: del c
    for p in sim.net.pops: del p
    del sim.net.params
    
    
    # clean cells and simData gathered in master node
    if sim.rank == 0:
        sim.clearObj([cell.__dict__ for cell in sim.net.allCells])
        sim.clearObj([stim for stim in sim.allSimData['stims']])
        for key in sim.allSimData.keys(): del sim.allSimData[key]
        for c in sim.net.allCells: del c
        for p in sim.net.allPops: del p
        del sim.net.allCells
        del sim.allSimData

        import matplotlib
        matplotlib.pyplot.clf()
        matplotlib.pyplot.close()

    del sim.net

    import gc; gc.collect()



###############################################################################
# Hash function to obtain random value
###############################################################################
def id32 (obj): 
    return int(hashlib.md5(obj).hexdigest()[0:8],16)  # convert 8 first chars of md5 hash in base 16 to int
    

###############################################################################
### Replace item with specific key from dict or list (used to remove h objects)
###############################################################################
def copyReplaceItemObj (obj, keystart, newval, objCopy='ROOT'):
    if type(obj) == list:
        if objCopy=='ROOT': 
            objCopy = []
        for item in obj:
            if type(item) in [list]:
                objCopy.append([])
                copyReplaceItemObj(item, keystart, newval, objCopy[-1])
            elif type(item) in [dict, Dict]:
                objCopy.append({})
                copyReplaceItemObj(item, keystart, newval, objCopy[-1])
            else:
                objCopy.append(item)

    elif type(obj) in [dict, Dict]:
        if objCopy == 'ROOT':
            objCopy = Dict() 
        for key,val in obj.iteritems():
            if type(val) in [list]:
                objCopy[key] = [] 
                copyReplaceItemObj(val, keystart, newval, objCopy[key])
            elif type(val) in [dict, Dict]:
                objCopy[key] = {}
                copyReplaceItemObj(val, keystart, newval, objCopy[key])
            elif key.startswith(keystart):
                objCopy[key] = newval
            else:
                objCopy[key] = val
    return objCopy


###############################################################################
### Recursively remove items of an object (used to avoid mem leaks)
###############################################################################
def clearObj (obj):
    if type(obj) == list:
        for item in obj:
            if type(item) in [list, dict, Dict, ODict]:
                clearObj(item)
            del item
                
    elif type(obj) in [dict, Dict, ODict]:
        for key in obj.keys():
            val = obj[key]
            if type(val) in [list, dict, Dict, ODict]:
                clearObj(val)
            del obj[key]
    return obj

###############################################################################
### Replace item with specific key from dict or list (used to remove h objects)
###############################################################################
def replaceItemObj (obj, keystart, newval):
    if type(obj) == list:
        for item in obj:
            if type(item) in [list, dict]:
                replaceItemObj(item, keystart, newval)

    elif type(obj) == dict:
        for key,val in obj.iteritems():
            if type(val) in [list, dict]:
                replaceItemObj(val, keystart, newval)
            if key.startswith(keystart):
                obj[key] = newval
    return obj


###############################################################################
### Replace functions from dict or list with function string (so can be pickled)
###############################################################################
def replaceFuncObj (obj):
    if type(obj) == list:
        for item in obj:
            if type(item) in [list, dict]:
                replaceFuncObj(item)

    elif type(obj) == dict:
        for key,val in obj.iteritems():
            if type(val) in [list, dict]:
                replaceFuncObj(val)
            if 'func_name' in dir(val): #hasattr(val,'func_name'):  # avoid hasattr() since it creates key in Dicts() 
                obj[key] = 'func' # funcSource
    return obj


###############################################################################
### Replace None from dict or list with [](so can be saved to .mat)
###############################################################################
def replaceNoneObj (obj):
    if type(obj) == list:# or type(obj) == tuple:
        for item in obj:
            if type(item) in [list, dict, Dict, ODict]:
                replaceNoneObj(item)

    elif type(obj) in [dict, Dict, ODict]:
        for key,val in obj.iteritems():
            if type(val) in [list, dict, Dict, ODict]:
                replaceNoneObj(val)
            if val == None:
                obj[key] = []
            elif val == {}:
                obj[key] = [] # also replace empty dicts with empty list
    return obj


###############################################################################
### Replace Dict with dict and Odict with OrderedDict
###############################################################################
def replaceDictODict (obj):
    if type(obj) == list:
        for item in obj:
            if type(item) == Dict:
                item = item.todict()
            elif type(item) == ODict:
                item = item.toOrderedDict()
            if type(item) in [list, dict, OrderedDict]:
                replaceDictODict(item)

    elif type(obj) in [dict, OrderedDict, Dict, ODict]:
        for key,val in obj.iteritems():
            if type(val) == Dict:
                obj[key] = val.todict()
            elif type(val) == ODict:
                obj[key] = val.toOrderedDict()
            if type(val) in [list, dict, OrderedDict]:
                replaceDictODict(val)       

    # elif type(obj) == Dict:
    #     obj = obj.todict()
    #     for key,val in obj.iteritems():
    #         if type(val) in [list, dict, Dict, ODict]:
    #             replaceDictODict(val)

    # elif type(obj) == ODict:
    #     print obj.keys()
    #     obj = obj.toOrderedDict()
    #     for key,val in obj.iteritems():
    #         if type(val) in [list, dict, Dict, ODict]:
    #             replaceDictODict(val)

    # elif type(obj) == dict:
    #     for key,val in obj.iteritems():
    #         if type(val) in [list, dict, Dict, ODict]:
    #             replaceDictODict(val)
    return obj

###############################################################################
### Replace tuples with str
###############################################################################
def tupleToStr (obj):
    if type(obj) == list:
        for item in obj:
            if type(item) in [list, dict]:
                tupleToStr(item)
            elif type(item) == tuple:
                obj[obj.index(item)] = str(item)

    elif type(obj) == dict or type(obj) == ODict:
        for key,val in obj.iteritems():
            if type(val) in [list, dict, ODict]:
                tupleToStr(val)
            elif type(val) == tuple:
                obj[key] = str(val) # also replace empty dicts with empty list
    return obj


###############################################################################
### Convert dict strings to utf8 so can be saved in HDF5 format
###############################################################################
def _dict2utf8 (obj):
#unidict = {k.decode('utf8'): v.decode('utf8') for k, v in strdict.items()}
    #print obj
    import collections
    if isinstance(obj, basestring):
        return obj.decode('utf8')
    elif isinstance(obj, collections.Mapping):
        for key in obj.keys():
            if isinstance(key, Number):
                obj[str(key).decode('utf8')] = obj[key]
                obj.pop(key)
        return dict(map(_dict2utf8, obj.iteritems()))
    elif isinstance(obj, collections.Iterable):
        return type(obj)(map(_dict2utf8, obj))
    else:
        return obj


###############################################################################
### Convert dict strings to utf8 so can be saved in HDF5 format
###############################################################################
def cellByGid(gid):
    cell = next((c for c in sim.net.cells if c.gid==gid), None)
    return cell


###############################################################################
### Update model parameters from command-line arguments - UPDATE for sim and sim.net sim.params
###############################################################################
def readArgs ():
    for argv in sys.argv[1:]: # Skip first argument, which is file name
        arg = argv.replace(' ','').split('=') # ignore spaces and find varname and value
        harg = arg[0].split('.')+[''] # Separate out variable name; '' since if split fails need to still have an harg[1]
        if len(arg)==2:
            if hasattr(sim.net.params,arg[0]) or hasattr(sim.s.params,harg[1]): # Check that variable exists
                if arg[0] == 'outfilestem':
                    exec('s.'+arg[0]+'="'+arg[1]+'"') # Actually set variable 
                    if sim.rank==0: # messages only come from Master  
                        print('  Setting %s=%s' %(arg[0],arg[1]))
                else:
                    exec('p.'+argv) # Actually set variable            
                    if sim.rank==0: # messages only come from Master  
                        print('  Setting %s=%r' %(arg[0],eval(arg[1])))
            else: 
                sys.tracebacklimit=0
                raise Exception('Reading args from commandline: Variable "%s" not found' % arg[0])
        elif argv=='-mpi':   sim.ismpi = True
        else: pass # ignore -python 


###############################################################################
### Setup Recording
###############################################################################
def setupRecording ():
    timing('start', 'setrecordTime')
    # set initial v of cells
    sim.fih = []
    for cell in sim.net.cells:
        sim.fih.append(h.FInitializeHandler(cell.initV))

    # spike recording
    sim.simData.update({name:h.Vector(1e4).resize(0) for name in ['spkt','spkid']})  # initialize
    sim.pc.spike_record(-1, sim.simData['spkt'], sim.simData['spkid']) # -1 means to record from all cells on this node

    # stim spike recording
    if 'plotRaster' in sim.cfg.analysis:
        if isinstance(sim.cfg.analysis['plotRaster'],dict) and 'include' in sim.cfg.analysis['plotRaster']:
            netStimPops = [popLabel for popLabel,pop in sim.net.pops.iteritems() if pop.tags['cellModel']=='NetStim']+['allNetStims']
            for item in sim.cfg.analysis['plotRaster']['include']:
                if item in netStimPops: 
                    sim.cfg.recordStim = True
                    break

    if 'plotSpikeHist' in sim.cfg.analysis:
        if sim.cfg.analysis['plotSpikeHist']==True:
            sim.cfg.recordStim = True

        elif (isinstance(sim.cfg.analysis['plotSpikeHist'],dict) and 'include' in sim.cfg.analysis['plotSpikeHist']) :
            netStimPops = [popLabel for popLabel,pop in sim.net.pops.iteritems() if pop.tags['cellModel']=='NetStim']+['allNetStims', 'eachPop']
            for item in sim.cfg.analysis['plotSpikeHist']['include']:
                if item in netStimPops: 
                    sim.cfg.recordStim = True
                    break
                  
    if sim.cfg.recordStim:
        sim.simData['stims'] = Dict()
        for cell in sim.net.cells: 
            cell.recordStimSpikes()

    # intrinsic cell variables recording
    if sim.cfg.recordTraces:
        # get list of cells from argument of plotTraces function
        if 'plotTraces' in sim.cfg.analysis and 'include' in sim.cfg.analysis['plotTraces']:
            cellsPlot = getCellsList(sim.cfg.analysis['plotTraces']['include'])
        else:
            cellsPlot = []

        # get actual cell objects to record from, both from recordCell and plotCell lists
        cellsRecord = getCellsList(sim.cfg.recordCells)+cellsPlot

        for key in sim.cfg.recordTraces.keys(): sim.simData[key] = Dict()  # create dict to store traces
        for cell in cellsRecord: cell.recordTraces()  # call recordTraces function for each cell
    
    timing('stop', 'setrecordTime')

    return sim.simData


###############################################################################
### Get cells list for recording based on set of conditions
###############################################################################
def getCellsList(include):

    if sim.nhosts > 1 and any(isinstance(cond, tuple) for cond in include): # Gather tags from all cells 
        allCellTags = sim._gatherAllCellTags()  
    else:
        allCellTags = {cell.gid: cell.tags for cell in sim.net.cells}

    cellGids = []
    cells = []
    for condition in include:
        if condition in ['all', 'allCells']:  # all cells + Netstims 
            cells = list(sim.net.cells)
            return cells

        elif isinstance(condition, int):  # cell gid 
            cellGids.append(condition)
        
        elif isinstance(condition, str):  # entire pop
            cellGids.extend(list(sim.net.pops[condition].cellGids)) 
            #[c.gid for c in sim.net.cells if c.tags['popLabel']==condition])
        
        elif isinstance(condition, tuple):  # subset of a pop with relative indices
            cellsPop = [gid for gid,tags in allCellTags.iteritems() if tags['popLabel']==condition[0]]
            if isinstance(condition[1], list):
                cellGids.extend([gid for i,gid in enumerate(cellsPop) if i in condition[1]])
            elif isinstance(condition[1], int):
                cellGids.extend([gid for i,gid in enumerate(cellsPop) if i==condition[1]])

    cellGids = list(set(cellGids))  # unique values
    cells = [cell for cell in sim.net.cells if cell.gid in cellGids]
    return cells


###############################################################################
### Commands required just before running simulation
###############################################################################
def preRun():
    if sim.cfg.cache_efficient:
        h('objref cvode')
        h('cvode = new CVode()')
        h.cvode.cache_efficient(0)

    h.dt = sim.cfg.dt  # set time step
    for key,val in sim.cfg.hParams.iteritems(): setattr(h, key, val) # set other h global vars (celsius, clamp_resist)
    sim.pc.set_maxstep(10)
    mindelay = sim.pc.allreduce(sim.pc.set_maxstep(10), 2) # flag 2 returns minimum value
    if sim.rank==0 and sim.cfg.verbose: print('Minimum delay (time-step for queue exchange) is %.2f'%(mindelay))
    
    # reset all netstims so runs are always equivalent
    for cell in sim.net.cells:
        for stim in cell.stims:
            if 'hRandom' in stim:
                stim['hRandom'].Random123(cell.gid, sim.id32('%d'%(stim['seed'])))
                stim['hRandom'].negexp(1)


###############################################################################
### Run Simulation
###############################################################################
def runSim ():
    sim.pc.barrier()
    timing('start', 'runTime')
    preRun()
    init()

    if sim.rank == 0: print('\nRunning...')
    sim.pc.psolve(sim.cfg.duration)
    
    sim.pc.barrier() # Wait for all hosts to get to this point
    timing('stop', 'runTime')
    if sim.rank==0: 
        print('  Done; run time = %0.2f s; real-time ratio: %0.2f.' % 
            (sim.timingData['runTime'], sim.cfg.duration/1000/sim.timingData['runTime']))


###############################################################################
### Run Simulation
###############################################################################
def runSimWithIntervalFunc (interval, func):
    sim.pc.barrier()
    timing('start', 'runTime')
    preRun()
    init()
    if sim.rank == 0: print('\nRunning...')

    while round(h.t) < sim.cfg.duration:
        sim.pc.psolve(min(sim.cfg.duration, h.t+interval))
        func(h.t) # function to be called at intervals

    sim.pc.barrier() # Wait for all hosts to get to this point
    timing('stop', 'runTime')
    if sim.rank==0: 
        print('  Done; run time = %0.2f s; real-time ratio: %0.2f.' % 
            (sim.timingData['runTime'], sim.cfg.duration/1000/sim.timingData['runTime']))
                

###############################################################################
### Gather tags from cells
###############################################################################
def _gatherAllCellTags ():
    data = [{cell.gid: cell.tags for cell in sim.net.cells}]*sim.nhosts  # send cells data to other nodes
    gather = sim.pc.py_alltoall(data)  # collect cells data from other nodes (required to generate connections)
    sim.pc.barrier()
    allCellTags = {}
    for dataNode in gather:         
        allCellTags.update(dataNode)
    
    # clean to avoid mem leaks
    for node in gather: 
        if node:
            node.clear()
            del node
    for item in data:
        if item: 
            item.clear()
            del item

    return allCellTags


###############################################################################
### Gather data from nodes
###############################################################################
def gatherData ():
    timing('start', 'gatherTime')
    ## Pack data from all hosts
    if sim.rank==0: 
        print('\nGathering data...')

    simDataVecs = ['spkt','spkid','stims']+sim.cfg.recordTraces.keys()
    if sim.nhosts > 1:  # only gather if >1 nodes 
        netPopsCellGids = {popLabel: list(pop.cellGids) for popLabel,pop in sim.net.pops.iteritems()}
        nodeData = {'netCells': [c.__getstate__() for c in sim.net.cells], 'netPopsCellGids': netPopsCellGids, 'simData': sim.simData} 
        data = [None]*sim.nhosts
        data[0] = {}
        for k,v in nodeData.iteritems():
            data[0][k] = v 
        gather = sim.pc.py_alltoall(data)

        sim.pc.barrier()  
        if sim.rank == 0:
            allCells = []
            allPops = ODict()
            for popLabel,pop in sim.net.pops.iteritems(): allPops[popLabel] = pop.__getstate__() # can't use dict comprehension for OrderedDict
            allPopsCellGids = {popLabel: [] for popLabel in netPopsCellGids}
            sim.allSimData = Dict()

            for k in gather[0]['simData'].keys():  # initialize all keys of allSimData dict
                sim.allSimData[k] = {}

            # fill in allSimData taking into account if data is dict of h.Vector (code needs improvement to be more generic)
            for node in gather:  # concatenate data from each node
                allCells.extend(node['netCells'])  # extend allCells list
                for popLabel,popCellGids in node['netPopsCellGids'].iteritems():
                    allPopsCellGids[popLabel].extend(popCellGids)
                    
                for key,val in node['simData'].iteritems():  # update simData dics of dics of h.Vector 
                    if key in simDataVecs:          # simData dicts that contain Vectors
                        if isinstance(val,dict):                
                            for cell,val2 in val.iteritems():
                                if isinstance(val2,dict):       
                                    sim.allSimData[key].update(Dict({cell:Dict()}))
                                    for stim,val3 in val2.iteritems():
                                        sim.allSimData[key][cell].update({stim:list(val3)}) # udpate simData dicts which are dicts of dicts of Vectors (eg. ['stim']['cell_1']['backgrounsd']=h.Vector)
                                else:
                                    sim.allSimData[key].update({cell:list(val2)})  # udpate simData dicts which are dicts of Vectors (eg. ['v']['cell_1']=h.Vector)
                        else:                                   
                            sim.allSimData[key] = list(sim.allSimData[key])+list(val) # udpate simData dicts which are Vectors
                    else: 
                        sim.allSimData[key].update(val)           # update simData dicts which are not Vectors

            sim.net.allCells =  sorted(allCells, key=lambda k: k['gid']) 
            
            for popLabel,pop in allPops.iteritems():
                pop['cellGids'] = sorted(allPopsCellGids[popLabel])
            sim.net.allPops = allPops
    

        # clean to avoid mem leaks
        for node in gather: 
            if node:
                node.clear()
                del node
        for item in data:
            if item: 
                item.clear()
                del item

    else:  # if single node, save data in same format as for multiple nodes for consistency
        if sim.cfg.createNEURONObj:
            sim.net.allCells = [Dict(c.__getstate__()) for c in sim.net.cells]
        else:
            sim.net.allCells = [c.__dict__ for c in sim.net.cells]
        sim.net.allPops = ODict()
        for popLabel,pop in sim.net.pops.iteritems(): sim.net.allPops[popLabel] = pop.__getstate__() # can't use dict comprehension for OrderedDict
        sim.allSimData = Dict() 
        for k in sim.simData.keys():  # initialize all keys of allSimData dict
                sim.allSimData[k] = Dict()
        for key,val in sim.simData.iteritems():  # update simData dics of dics of h.Vector 
                if key in simDataVecs:          # simData dicts that contain Vectors
                    if isinstance(val,dict):                
                        for cell,val2 in val.iteritems():
                            if isinstance(val2,dict):       
                                sim.allSimData[key].update(Dict({cell:Dict()}))
                                for stim,val3 in val2.iteritems():
                                    sim.allSimData[key][cell].update({stim:list(val3)}) # udpate simData dicts which are dicts of dicts of Vectors (eg. ['stim']['cell_1']['backgrounsd']=h.Vector)
                            else:
                                sim.allSimData[key].update({cell:list(val2)})  # udpate simData dicts which are dicts of Vectors (eg. ['v']['cell_1']=h.Vector)
                    else:                                   
                        sim.allSimData[key] = list(sim.allSimData[key])+list(val) # udpate simData dicts which are Vectors
                else: 
                    sim.allSimData[key].update(val)           # update simData dicts which are not Vectors

    ## Print statistics
    if sim.rank == 0:
        timing('stop', 'gatherTime')
        if sim.cfg.timing: print('  Done; gather time = %0.2f s.' % sim.timingData['gatherTime'])

        print('\nAnalyzing...')
        sim.totalSpikes = len(sim.allSimData['spkt'])   
        sim.totalConnections = sum([len(cell['conns']) for cell in sim.net.allCells])   
        sim.numCells = len(sim.net.allCells)

        if sim.totalSpikes > 0:
            sim.firingRate = float(sim.totalSpikes)/sim.numCells/sim.cfg.duration*1e3 # Calculate firing rate 
        else: 
            sim.firingRate = 0
        if sim.numCells > 0:
            sim.connsPerCell = sim.totalConnections/float(sim.numCells) # Calculate the number of connections per cell
        else:
            sim.connsPerCell = 0
         
        print('  Cells: %i' % (sim.numCells) ) 
        print('  Connections: %i (%0.2f per cell)' % (sim.totalConnections, sim.connsPerCell))
        if sim.timingData.get('runTime'): 
            print('  Spikes: %i (%0.2f Hz)' % (sim.totalSpikes, sim.firingRate))
            print('  Simulated time: %0.1f s; %i workers' % (sim.cfg.duration/1e3, sim.nhosts))
            print('  Run time: %0.2f s' % (sim.timingData['runTime']))
            
        return sim.allSimData


###############################################################################
### Calculate and print avg pop rates
###############################################################################
def popAvgRates(trange = None, show = True):
    if not hasattr(sim, 'allSimData') or 'spkt' not in sim.allSimData:
        print 'Error: sim.allSimData not available; please call sim.gatherData()'
        return None

    spkts = sim.allSimData['spkt']
    spkids = sim.allSimData['spkid']

    if not trange: 
        trange = [0, sim.cfg.duration]
    else:
        spkids,spkts = zip(*[(spkid,spkt) for spkid,spkt in zip(spkids,spkts) if trange[0] <= spkt <= trange[1]])

    avgRates = Dict()
    for pop in sim.net.allPops:
        numCells = float(len(sim.net.allPops[pop]['cellGids']))
        if numCells > 0:
            tsecs = float((trange[1]-trange[0]))/1000.0
            avgRates[pop] = len([spkid for spkid in spkids if sim.net.allCells[int(spkid)]['tags']['popLabel']==pop])/numCells/tsecs
            print '%s : %.3f Hz'%(pop, avgRates[pop])
    return avgRates


###############################################################################
### Calculate and print load balance
###############################################################################
def loadBalance():
    computation_time = sim.pc.step_time()
    max_comp_time = sim.pc.allreduce(computation_time, 2)
    min_comp_time = sim.pc.allreduce(computation_time, 3)
    avg_comp_time = sim.pc.allreduce(computation_time, 1)/sim.nhosts
    load_balance = avg_comp_time/max_comp_time

    print 'node:',sim.rank,' comp_time:',computation_time
    if sim.rank==0:
        print 'max_comp_time:', max_comp_time
        print 'min_comp_time:', min_comp_time
        print 'avg_comp_time:', avg_comp_time
        print 'load_balance:',load_balance
        print '\nspike exchange time (run_time-comp_time): ', sim.timingData['runTime'] - max_comp_time

    return [max_comp_time, min_comp_time, avg_comp_time, load_balance]


###############################################################################
### Gather data from nodes
###############################################################################
def _gatherCells ():
    ## Pack data from all hosts
    if sim.rank==0: 
        print('\nUpdating sim.net.allCells...')

    if sim.nhosts > 1:  # only gather if >1 nodes 
        nodeData = {'netCells': [c.__getstate__() for c in sim.net.cells]} 
        data = [None]*sim.nhosts
        data[0] = {}
        for k,v in nodeData.iteritems():
            data[0][k] = v 
        gather = sim.pc.py_alltoall(data)
        sim.pc.barrier()  
        if sim.rank == 0:
            allCells = []
         
            # fill in allSimData taking into account if data is dict of h.Vector (code needs improvement to be more generic)
            for node in gather:  # concatenate data from each node
                allCells.extend(node['netCells'])  # extend allCells list
            sim.net.allCells =  sorted(allCells, key=lambda k: k['gid']) 
        
        # clean to avoid mem leaks
        for node in gather: 
            if node:
                node.clear()
                del node
        for item in data:
            if item: 
                item.clear()
                del item
                 
    else:  # if single node, save data in same format as for multiple nodes for consistency
        sim.net.allCells = [c.__getstate__() for c in sim.net.cells]
      

###############################################################################
### Save data
###############################################################################
def saveData (include = None):

    if sim.rank == 0 and not getattr(sim.net, 'allCells', None): needGather = True
    else: needGather = False
    if needGather: gatherData()

    if sim.rank == 0:
        timing('start', 'saveTime')

        if not include: include = sim.cfg.saveDataInclude
        dataSave = {}
        net = {}

        if 'netParams' in include: net['params'] = replaceFuncObj(sim.net.params.__dict__)
        if 'net' in include: include.extend(['netPops', 'netCells'])
        if 'netCells' in include: net['cells'] = sim.net.allCells
        if 'netPops' in include: net['pops'] = sim.net.allPops
        if net: dataSave['net'] = net
        if 'simConfig' in include: dataSave['simConfig'] = sim.cfg.__dict__
        if 'simData' in include: dataSave['simData'] = sim.allSimData
        
        if dataSave:
            if sim.cfg.timestampFilename: 
                timestamp = time()
                timestampStr = datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S')
                sim.cfg.filename = sim.cfg.filename+'-'+timestampStr

            # Save to pickle file
            if sim.cfg.savePickle:
                import pickle
                dataSave = replaceDictODict(dataSave)
                print('Saving output as %s ... ' % (sim.cfg.filename+'.pkl'))
                with open(sim.cfg.filename+'.pkl', 'wb') as fileObj:
                    pickle.dump(dataSave, fileObj)
                print('Finished saving!')

            # Save to dpk file
            if sim.cfg.saveDpk:
                import gzip
                print('Saving output as %s ... ' % (sim.cfg.filename+'.dpk'))
                fn=sim.cfg.filename #.split('.')
                gzip.open(fn, 'wb').write(pk.dumps(dataSave)) # write compressed string
                print('Finished saving!')

            # Save to json file
            if sim.cfg.saveJson:
                import json
                #dataSave = replaceDictODict(dataSave)  # not required since json saves as dict
                print('Saving output as %s ... ' % (sim.cfg.filename+'.json '))
                with open(sim.cfg.filename+'.json', 'w') as fileObj:
                    json.dump(dataSave, fileObj)
                print('Finished saving!')

            # Save to mat file
            if sim.cfg.saveMat:
                from scipy.io import savemat 
                print('Saving output as %s ... ' % (sim.cfg.filename+'.mat'))
                savemat(sim.cfg.filename+'.mat', tupleToStr(replaceNoneObj(dataSave)))  # replace None and {} with [] so can save in .mat format
                print('Finished saving!')

            # Save to HDF5 file (uses very inefficient hdf5storage module which supports dicts)
            if sim.cfg.saveHDF5:
                dataSaveUTF8 = _dict2utf8(replaceNoneObj(dataSave)) # replace None and {} with [], and convert to utf
                import hdf5storage
                print('Saving output as %s... ' % (sim.cfg.filename+'.hdf5'))
                hdf5storage.writes(dataSaveUTF8, filename=sim.cfg.filename+'.hdf5')
                print('Finished saving!')

            # Save to CSV file (currently only saves spikes)
            if sim.cfg.saveCSV:
                if 'simData' in dataSave:
                    import csv
                    print('Saving output as %s ... ' % (sim.cfg.filename+'.csv'))
                    writer = csv.writer(open(sim.cfg.filename+'.csv', 'wb'))
                    for dic in dataSave['simData']:
                        for values in dic:
                            writer.writerow(values)
                    print('Finished saving!')

            # Save to Dat file(s) 
            if sim.cfg.saveDat:
                traces = sim.cfg.recordTraces
                for ref in traces.keys():
                    for cellid in sim.allSimData[ref].keys():
                        dat_file_name = '%s_%s.dat'%(ref,cellid)
                        dat_file = open(dat_file_name, 'w')
                        trace = sim.allSimData[ref][cellid]
                        print("Saving %i points of data on: %s:%s to %s"%(len(trace),ref,cellid,dat_file_name))
                        for i in range(len(trace)):
                            dat_file.write('%s\t%s\n'%((i*sim.cfg.dt/1000),trace[i]/1000))

                print('Finished saving!')

            # Save timing
            if sim.cfg.timing: 
                timing('stop', 'saveTime')
                print('  Done; saving time = %0.2f s.' % sim.timingData['saveTime'])
            if sim.cfg.timing and sim.cfg.saveTiming: 
                import pickle
                with open('timing.pkl', 'wb') as file: pickle.dump(sim.timing, file)


            # clean to avoid mem leaks
            for key in dataSave.keys(): 
                del dataSave[key]
            del dataSave

            # return full path
            import os
            return os.getcwd()+'/'+sim.cfg.filename

        else: 
            print('Nothing to save')


###############################################################################
### Timing - Stop Watch
###############################################################################
def timing (mode, processName):
    if sim.rank == 0 and sim.cfg.timing:
        if mode == 'start':
            sim.timingData[processName] = time() 
        elif mode == 'stop':
            sim.timingData[processName] = time() - sim.timingData[processName]
            

###############################################################################
### Print netpyne version
###############################################################################
def version():
    import netpyne 
    print(netpyne.__version__)


###############################################################################
### Print github version
###############################################################################
def gitversion():
    import netpyne,os
    currentPath = os.getcwd()
    netpynePath = os.path.dirname(netpyne.__file__)
    os.system('cd '+netpynePath+' ; git log -1; '+'cd '+currentPath) 


###############################################################################
### Print github version
###############################################################################
def checkMemory():
    # print memory diagnostic info
    if sim.rank == 0: # and checkMemory:
        import resource
        print '\nMEMORY -----------------------'
        print 'Sections: '
        print h.topology()
        print 'NetCons: '
        print len(h.List("NetCon"))
        print 'NetStims:'
        print len(h.List("NetStim"))
        print '\n Memory usage: %s \n' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # import objgraph
        # objgraph.show_most_common_types()
        print '--------------------------------\n'


###############################################################################
### Get connection centric network representation as used in NeuroML2
###############################################################################  
def _convertNetworkRepresentation (net, gids_vs_pop_indices):

    nn = {}

    for np_pop in net.pops.values(): 
        print("Adding conns for: %s"%np_pop.tags)
        if not np_pop.tags['cellModel'] ==  'NetStim':
            for cell in net.cells:
                if cell.gid in np_pop.cellGids:
                    popPost, indexPost = gids_vs_pop_indices[cell.gid]
                    #print("Cell %s: %s\n    %s[%i]\n"%(cell.gid,cell.tags,popPost, indexPost))
                    for conn in cell.conns:
                        preGid = conn['preGid']
                        if not preGid == 'NetStim':
                            popPre, indexPre = gids_vs_pop_indices[preGid]
                            loc = conn['loc']
                            weight = conn['weight']
                            delay = conn['delay']
                            sec = conn['sec']
                            synMech = conn['synMech']
                            threshold = conn['threshold']

                            if sim.cfg.verbose: print("      Conn %s[%i]->%s[%i] with %s, w: %s, d: %s"%(popPre, indexPre,popPost, indexPost, synMech, weight, delay))

                            projection_info = (popPre,popPost,synMech)
                            if not projection_info in nn.keys():
                                nn[projection_info] = []

                            nn[projection_info].append({'indexPre':indexPre,'indexPost':indexPost,'weight':weight,'delay':delay})
                        else:
                            #print("      Conn NetStim->%s[%s] with %s"%(popPost, indexPost, '??'))
                            pass
                                
    return nn                 


###############################################################################
### Get stimulations in representation as used in NeuroML2
###############################################################################  
def _convertStimulationRepresentation (net,gids_vs_pop_indices, nml_doc):

    stims = {}

    for np_pop in net.pops.values(): 
        if not np_pop.tags['cellModel'] ==  'NetStim':
            print("Adding stims for: %s"%np_pop.tags)
            for cell in net.cells:
                if cell.gid in np_pop.cellGids:
                    pop, index = gids_vs_pop_indices[cell.gid]
                    #print("    Cell %s:\n    Tags:  %s\n    Pop:   %s[%i]\n    Stims: %s\n    Conns: %s\n"%(cell.gid,cell.tags,pop, index,cell.stims,cell.conns))
                    for stim in cell.stims:
                        ref = stim['source']
                        rate = stim['rate']
                        noise = stim['noise']
                        
                        netstim_found = False
                        for conn in cell.conns:
                            if conn['preGid'] == 'NetStim' and conn['preLabel'] == ref:
                                assert(not netstim_found)
                                netstim_found = True
                                synMech = conn['synMech']
                                threshold = conn['threshold']
                                delay = conn['delay']
                                weight = conn['weight']
                                
                        assert(netstim_found)
                        name_stim = 'NetStim_%s_%s_%s_%s_%s'%(ref,pop,rate,noise,synMech)

                        stim_info = (name_stim, pop, rate, noise,synMech)
                        if not stim_info in stims.keys():
                            stims[stim_info] = []


                        stims[stim_info].append({'index':index,'weight':weight,'delay':delay,'threshold':threshold})   

    #print(stims)
    return stims


if neuromlExists:

    ###############################################################################
    ### Export synapses to NeuroML2
    ############################################################################### 
    def _export_synapses (net, nml_doc):

        for id,syn in net.params.synMechParams.iteritems():

            print('Exporting details of syn: %s'%syn)
            if syn['mod'] == 'Exp2Syn':
                syn0 = neuroml.ExpTwoSynapse(id=id, 
                                             gbase='1uS',
                                             erev='%smV'%syn['e'],
                                             tau_rise='%sms'%syn['tau1'],
                                             tau_decay='%sms'%syn['tau2'])

                nml_doc.exp_two_synapses.append(syn0)
            elif syn['mod'] == 'ExpSyn':
                syn0 = neuroml.ExpOneSynapse(id=id, 
                                             gbase='1uS',
                                             erev='%smV'%syn['e'],
                                             tau_decay='%sms'%syn['tau'])

                nml_doc.exp_one_synapses.append(syn0)
            else:
                raise Exception("Cannot yet export synapse type: %s"%syn['mod'])

    hh_nml2_chans = """

    <neuroml xmlns="http://www.neuroml.org/schema/neuroml2"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:schemaLocation="http://www.neuroml.org/schema/neuroml2  https://raw.githubusercontent.com/NeuroML/NeuroML2/master/Schemas/NeuroML2/NeuroML_v2beta3.xsd"   
             id="kChan">
             
        <ionChannelHH id="leak_hh" conductance="10pS" type="ionChannelPassive">
            
            <notes>Single ion channel in NeuroML2 format: passive channel providing a leak conductance </notes>
            
        </ionChannelHH>
        
        <ionChannelHH id="na_hh" conductance="10pS" species="na">
            
            <notes>Single ion channel in NeuroML2 format: standard Sodium channel from the Hodgkin Huxley model</notes>

            <gateHHrates id="m" instances="3">
                <forwardRate type="HHExpLinearRate" rate="1per_ms" midpoint="-40mV" scale="10mV"/>
                <reverseRate type="HHExpRate" rate="4per_ms" midpoint="-65mV" scale="-18mV"/>
            </gateHHrates>

            <gateHHrates id="h" instances="1">
                <forwardRate type="HHExpRate" rate="0.07per_ms" midpoint="-65mV" scale="-20mV"/>
                <reverseRate type="HHSigmoidRate" rate="1per_ms" midpoint="-35mV" scale="10mV"/>
            </gateHHrates>

        </ionChannelHH>

        <ionChannelHH id="k_hh" conductance="10pS" species="k">
            
            <notes>Single ion channel in NeuroML2 format: standard Potassium channel from the Hodgkin Huxley model</notes>

            <gateHHrates id="n" instances="4">
                <forwardRate type="HHExpLinearRate" rate="0.1per_ms" midpoint="-55mV" scale="10mV"/>
                <reverseRate type="HHExpRate" rate="0.125per_ms" midpoint="-65mV" scale="-80mV"/>
            </gateHHrates>
                
        </ionChannelHH>
        

    </neuroml>
    """

    ###############################################################################
    ### Export generated structure of network to NeuroML 2 
    ###############################################################################         
    def exportNeuroML2 (reference, connections=True, stimulations=True):

        net = sim.net
        
        print("Exporting network to NeuroML 2, reference: %s"%reference)
        
        import neuroml
        import neuroml.writers as writers

        nml_doc = neuroml.NeuroMLDocument(id='%s'%reference)
        nml_net = neuroml.Network(id='%s'%reference)
        nml_doc.networks.append(nml_net)

        import netpyne
        nml_doc.notes = 'NeuroML 2 file exported from NetPyNE v%s'%(netpyne.__version__)

        gids_vs_pop_indices ={}
        populations_vs_components = {}

        for cell_name in net.params.cellParams.keys():
            cell_param_set = net.params.cellParams[cell_name]
            print("---------------  Adding a cell %s: \n%s"%(cell_name,cell_param_set))
            print("Adding a cell %s: \n%s"%(cell_name,pp.pprint(cell_param_set.todict())))
            
            # Single section; one known mechanism...
            soma = cell_param_set.secs.soma
            if len(cell_param_set.secs) == 1 \
               and soma is not None\
               and len(soma.mechs) == 0 \
               and len(soma.pointps) == 1:
                   
                pproc = soma.pointps.values()[0]
                cell_id = 'CELL_%s_%s'%(cell_param_set.conds.cellModel,cell_param_set.conds.cellType)
                if len(cell_param_set.conds.cellModel)==0:
                    cell_id = 'CELL_%s_%s'%(pproc.mod,cell_param_set.conds.cellType)
                print("Assuming abstract cell with behaviour set by single point process: %s!"%pproc)
                
                if pproc.mod == 'Izhi2007b':
                    izh = neuroml.Izhikevich2007Cell(id=cell_id)
                    izh.a = '%s per_ms'%pproc.a
                    izh.b = '%s nS'%pproc.b
                    izh.c = '%s mV'%pproc.c
                    izh.d = '%s pA'%pproc.d
                    
                    izh.v0 = '%s mV'%pproc.vr # Note: using vr for v0
                    izh.vr = '%s mV'%pproc.vr
                    izh.vt = '%s mV'%pproc.vt
                    izh.vpeak = '%s mV'%pproc.vpeak
                    izh.C = '%s pF'%(pproc.C*100)
                    izh.k = '%s nS_per_mV'%pproc.k
                    
                    nml_doc.izhikevich2007_cells.append(izh)
                else:
                    print("Unknown point process: %s; can't convert to NeuroML 2 equivalent!"%pproc.mod)
                    exit(1)
            else:
                print("Assuming normal cell with behaviour set by ion channel mechanisms!")
                
                cell_id = 'CELL_%s_%s'%(cell_param_set.conds.cellModel,cell_param_set.conds.cellType)
                
                cell = neuroml.Cell(id=cell_id)
                cell.notes = "Cell exported from NetPyNE:\n%s"%cell_param_set
                cell.morphology = neuroml.Morphology(id='morph_%s'%cell_id)
                cell.biophysical_properties = neuroml.BiophysicalProperties(id='biophys_%s'%cell_id)
                mp = neuroml.MembraneProperties()
                cell.biophysical_properties.membrane_properties = mp
                ip = neuroml.IntracellularProperties()
                cell.biophysical_properties.intracellular_properties = ip
                
                count = 0

                import neuroml.nml.nml
                chans_doc = neuroml.nml.nml.parseString(hh_nml2_chans)
                chans_added = []
                
                nml_segs = {}
                
                parentDistal = neuroml.Point3DWithDiam(x=0,y=0,z=0,diameter=0)
                
                for np_sec_name in cell_param_set.secs.keys():
                    
                    parent_seg = None
                    
                    np_sec = cell_param_set.secs[np_sec_name]
                    nml_seg = neuroml.Segment(id=count,name=np_sec_name)
                    nml_segs[np_sec_name] = nml_seg
                    
                    if len(np_sec.topol)>0:
                        parent_seg = nml_segs[np_sec.topol.parentSec]
                        nml_seg.parent = neuroml.SegmentParent(segments=parent_seg.id)
                        
                        if not (np_sec.topol.parentX == 1.0 and  np_sec.topol.childX == 0):
                            print("Currently only support cell topol with parentX == 1.0 and childX == 0")
                            exit(1)
                    
                    if not (len(np_sec.geom.pt3d)==2 or len(np_sec.geom.pt3d)==0):
                        print("Currently only support cell geoms with 2 pt3ds (or 0 and diam/L specified): %s"%np_sec.geom)
                        exit(1)
                     
                    if len(np_sec.geom.pt3d)==0:
                        
                        if parent_seg == None:
                            nml_seg.proximal = neuroml.Point3DWithDiam(x=parentDistal.x,
                                                              y=parentDistal.y,
                                                              z=parentDistal.z,
                                                              diameter=np_sec.geom.diam)
                        
                        nml_seg.distal = neuroml.Point3DWithDiam(x=parentDistal.x,
                                                              y=(parentDistal.y+np_sec.geom.L),
                                                              z=parentDistal.z,
                                                              diameter=np_sec.geom.diam)
                    else:
                    
                        prox = np_sec.geom.pt3d[0]

                        nml_seg.proximal = neuroml.Point3DWithDiam(x=prox[0],
                                                                  y=prox[1],
                                                                  z=prox[2],
                                                                  diameter=prox[3])
                        dist = np_sec.geom.pt3d[1]
                        nml_seg.distal = neuroml.Point3DWithDiam(x=dist[0],
                                                                  y=dist[1],
                                                                  z=dist[2],
                                                                  diameter=dist[3])
                              
                    nml_seg_group = neuroml.SegmentGroup(id='%s_group'%np_sec_name)
                    nml_seg_group.members.append(neuroml.Member(segments=count))
                    cell.morphology.segment_groups.append(nml_seg_group)
                    
                        
                    cell.morphology.segments.append(nml_seg)
                    
                    count+=1
                
                    ip.resistivities.append(neuroml.Resistivity(value="%s ohm_cm"%np_sec.geom.Ra, 
                                                               segment_groups=nml_seg_group.id))
                           
                    '''
                    See https://github.com/Neurosim-lab/netpyne/issues/130
                    '''
                    cm = np_sec.geom.cm
                    if isinstance(cm,dict) and len(cm)==0:
                        cm = 1
                    mp.specific_capacitances.append(neuroml.SpecificCapacitance(value="%s uF_per_cm2"%cm, 
                                                               segment_groups=nml_seg_group.id))
                                                               
                                                               
                    mp.init_memb_potentials.append(neuroml.InitMembPotential(value="%s mV"%'-65'))
                                                               
                    mp.spike_threshes.append(neuroml.SpikeThresh(value="%s mV"%'0'))
                                                               
                    for mech_name in np_sec.mechs.keys():
                        mech = np_sec.mechs[mech_name]
                        if mech_name == 'hh':
                            
                            for chan in chans_doc.ion_channel_hhs:
                                if (chan.id == 'leak_hh' or chan.id == 'na_hh' or chan.id == 'k_hh'):
                                    if not chan.id in chans_added:
                                        nml_doc.ion_channel_hhs.append(chan)
                                        chans_added.append(chan.id)
                            
                            
                            leak_cd = neuroml.ChannelDensity(id='leak_%s'%nml_seg_group.id,
                                                        ion_channel='leak_hh',
                                                        cond_density='%s S_per_cm2'%mech.gl,
                                                        erev='%s mV'%mech.el,
                                                        ion='non_specific')
                            mp.channel_densities.append(leak_cd)
                            
                            k_cd = neuroml.ChannelDensity(id='k_%s'%nml_seg_group.id,
                                                        ion_channel='k_hh',
                                                        cond_density='%s S_per_cm2'%mech.gkbar,
                                                        erev='%s mV'%'-77',
                                                        ion='k')
                            mp.channel_densities.append(k_cd)
                            
                            na_cd = neuroml.ChannelDensity(id='na_%s'%nml_seg_group.id,
                                                        ion_channel='na_hh',
                                                        cond_density='%s S_per_cm2'%mech.gnabar,
                                                        erev='%s mV'%'50',
                                                        ion='na')
                            mp.channel_densities.append(na_cd)
                                    
                        elif mech_name == 'pas':
                                        
                            for chan in chans_doc.ion_channel_hhs:
                                if (chan.id == 'leak_hh'):
                                    if not chan.id in chans_added:
                                        nml_doc.ion_channel_hhs.append(chan)
                                        chans_added.append(chan.id)
                                        
                            leak_cd = neuroml.ChannelDensity(id='leak_%s'%nml_seg_group.id,
                                                        ion_channel='leak_hh',
                                                        cond_density='%s mS_per_cm2'%mech.g,
                                                        erev='%s mV'%mech.e,
                                                        ion='non_specific')
                            mp.channel_densities.append(leak_cd)
                        else:
                            print("Currently NML2 export only supports mech hh, not: %s"%mech_name)
                            exit(1)

                    
                nml_doc.cells.append(cell)
                
            
        for np_pop in net.pops.values(): 
            index = 0
            print("Adding population: %s"%np_pop.tags)
            positioned = len(np_pop.cellGids)>0
            type = 'populationList'
            if not np_pop.tags['cellModel'] ==  'NetStim':
                comp_id = 'CELL_%s_%s'%(np_pop.tags['cellModel'],np_pop.tags['cellType'])
                pop = neuroml.Population(id=np_pop.tags['popLabel'],component=comp_id, type=type)
                populations_vs_components[pop.id]=pop.component
                nml_net.populations.append(pop)

                for cell in net.cells:
                    if cell.gid in np_pop.cellGids:
                        gids_vs_pop_indices[cell.gid] = (np_pop.tags['popLabel'],index)
                        inst = neuroml.Instance(id=index)
                        index+=1
                        pop.instances.append(inst)
                        inst.location = neuroml.Location(cell.tags['x'],cell.tags['y'],cell.tags['z'])
                
                pop.size = index
                
        _export_synapses(net, nml_doc)

        if connections:
            nn = _convertNetworkRepresentation(net, gids_vs_pop_indices)

            for proj_info in nn.keys():

                prefix = "NetConn"
                popPre,popPost,synMech = proj_info

                projection = neuroml.Projection(id="%s_%s_%s_%s"%(prefix,popPre, popPost,synMech), 
                                  presynaptic_population=popPre, 
                                  postsynaptic_population=popPost, 
                                  synapse=synMech)
                index = 0      
                for conn in nn[proj_info]:
                    if sim.cfg.verbose: print("Adding conn %s"%conn)
                    connection = neuroml.ConnectionWD(id=index, \
                                pre_cell_id="../%s/%i/%s"%(popPre, conn['indexPre'], populations_vs_components[popPre]), \
                                pre_segment_id=0, \
                                pre_fraction_along=0.5,
                                post_cell_id="../%s/%i/%s"%(popPost, conn['indexPost'], populations_vs_components[popPost]), \
                                post_segment_id=0,
                                post_fraction_along=0.5,
                                delay = '%s ms'%conn['delay'],
                                weight = conn['weight'])
                    index+=1

                    projection.connection_wds.append(connection)

                nml_net.projections.append(projection)

        if stimulations:
            stims = _convertStimulationRepresentation(net, gids_vs_pop_indices, nml_doc)

            for stim_info in stims.keys():
                name_stim, post_pop, rate, noise, synMech = stim_info

                print("Adding stim: %s"%[stim_info])

                if noise==0:
                    source = neuroml.SpikeGenerator(id=name_stim,period="%ss"%(1./rate))
                    nml_doc.spike_generators.append(source)
                elif noise==1:
                    source = neuroml.SpikeGeneratorPoisson(id=name_stim,average_rate="%s Hz"%(rate))
                    nml_doc.spike_generator_poissons.append(source)
                else:
                    raise Exception("Noise = %s is not yet supported!"%noise)


                stim_pop = neuroml.Population(id='Pop_%s'%name_stim,component=source.id,size=len(stims[stim_info]))
                nml_net.populations.append(stim_pop)


                proj = neuroml.Projection(id="NetConn_%s__%s"%(name_stim, post_pop), 
                      presynaptic_population=stim_pop.id, 
                      postsynaptic_population=post_pop, 
                      synapse=synMech)

                nml_net.projections.append(proj)

                count = 0
                for stim in stims[stim_info]:
                    #print("  Adding stim: %s"%stim)

                    connection = neuroml.ConnectionWD(id=count, \
                            pre_cell_id="../%s[%i]"%(stim_pop.id, count), \
                            pre_segment_id=0, \
                            pre_fraction_along=0.5,
                            post_cell_id="../%s/%i/%s"%(post_pop, stim['index'], populations_vs_components[post_pop]), \
                            post_segment_id=0,
                            post_fraction_along=0.5,
                            delay = '%s ms'%stim['delay'],
                            weight = stim['weight'])
                    count+=1

                    proj.connection_wds.append(connection)


        nml_file_name = '%s.net.nml'%reference

        writers.NeuroMLWriter.write(nml_doc, nml_file_name)


        import pyneuroml.lems

        pyneuroml.lems.generate_lems_file_for_neuroml("Sim_%s"%reference, 
                                   nml_file_name, 
                                   reference, 
                                   sim.cfg.duration, 
                                   sim.cfg.dt, 
                                   'LEMS_%s.xml'%reference,
                                   '.',
                                   copy_neuroml = False,
                                   include_extra_files = [],
                                   gen_plots_for_all_v = False,
                                   gen_plots_for_only_populations = populations_vs_components.keys(),
                                   gen_saves_for_all_v = False,
                                   plot_all_segments = False, 
                                   gen_saves_for_only_populations = populations_vs_components.keys(),
                                   save_all_segments = False,
                                   seed=1234)
                               
                               
                
    ###############################################################################
    ### Class for handling NeuroML2 constructs and generating the equivalent in 
    ### NetPyNE's internal representation
    ############################################################################### 

          #### NOTE: commented out because generated error when running via mpiexec
          ####       maybe find way to check if exectued via mpi 

    from neuroml.hdf5.DefaultNetworkHandler import DefaultNetworkHandler


    class NetPyNEBuilder(DefaultNetworkHandler):

        cellParams = OrderedDict()
        popParams = OrderedDict()
        
        pop_ids_vs_seg_ids_vs_segs = {}
        pop_ids_vs_components = {}
        pop_ids_vs_use_segment_groups_for_neuron = {}
        pop_ids_vs_ordered_segs = {}
        pop_ids_vs_cumulative_lengths = {}

        projection_infos = OrderedDict()
        connections = OrderedDict()

        popStimSources = {}
        stimSources = {}
        popStimLists = {}
        stimLists = {}

        gids = OrderedDict()
        next_gid = 0

        def __init__(self, netParams):
            self.netParams = netParams

        def finalise(self):

            for popParam in self.popParams.keys():
                self.netParams.addPopParams(popParam, self.popParams[popParam])

            for cellParam in self.cellParams.keys():
                self.netParams.addCellParams(cellParam, self.cellParams[cellParam])

            for proj_id in self.projection_infos.keys():
                projName, prePop, postPop, synapse = self.projection_infos[proj_id]

                self.netParams.addSynMechParams(synapse, {'mod': synapse})

            for stimName in self.stimSources.keys():
                self.netParams.addStimSourceParams(stimName,self.stimSources[stimName])
                self.netParams.addStimTargetParams(stimName,self.stimLists[stimName])

        def _get_prox_dist(self, seg, seg_ids_vs_segs):
            prox = None
            if seg.proximal:
                prox = seg.proximal
            else: 
                parent_seg = seg_ids_vs_segs[seg.parent.segments]
                prox = parent_seg.distal

            dist = seg.distal
            if prox.x==dist.x and prox.y==dist.y and prox.z==dist.z:

                if prox.diameter==dist.diameter:
                    dist.y = prox.diameter
                else:
                    raise Exception('Unsupported geometry in segment: %s of cell %s'%(seg.name,cell.id))
                
            return prox, dist

        #
        #  Overridden from DefaultNetworkHandler
        #    
        def handlePopulation(self, population_id, component, size, component_obj):

            self.log.info("A population: %s with %i of %s (%s)"%(population_id,size,component,component_obj))
            
            self.pop_ids_vs_components[population_id] = component_obj

            assert(component==component_obj.id)

            popInfo=OrderedDict()
            popInfo['popLabel'] = population_id
            popInfo['cellModel'] = component
            popInfo['cellType'] = component
            popInfo['cellsList'] = []

            self.popParams[population_id] = popInfo

            from neuroml import Cell
            if isinstance(component_obj,Cell):
                
                cell = component_obj
                cellRule = {'conds':{'cellType': component, 'cellModel': component},  'secs': {}, 'secLists':{}}  # cell rule dict
                
                seg_ids_vs_segs = cell.get_segment_ids_vs_segments()
                seg_grps_vs_nrn_sections = {}
                seg_grps_vs_nrn_sections['all'] = []
                                
                use_segment_groups_for_neuron = False
                
                for seg_grp in cell.morphology.segment_groups:
                    if hasattr(seg_grp,'neuro_lex_id') and seg_grp.neuro_lex_id == "sao864921383":
                        use_segment_groups_for_neuron = True
                        cellRule['secs'][seg_grp.id] = {'geom': {'pt3d':[]}, 'mechs': {}, 'ions':{}} 
                        for prop in seg_grp.properties:
                            if prop.tag=="numberInternalDivisions":
                                cellRule['secs'][seg_grp.id]['geom']['nseg'] = int(prop.value)
                        #seg_grps_vs_nrn_sections[seg_grp.id] = seg_grp.id
                        seg_grps_vs_nrn_sections['all'].append(seg_grp.id)
                        
                self.pop_ids_vs_use_segment_groups_for_neuron[population_id] = use_segment_groups_for_neuron
                    
                
                if not use_segment_groups_for_neuron:
                    for seg in cell.morphology.segments:
                    
                        seg_grps_vs_nrn_sections['all'].append(seg.name)
                        cellRule['secs'][seg.name] = {'geom': {'pt3d':[]}, 'mechs': {}, 'ions':{}} 
                    
                        prox, dist = self._get_prox_dist(seg, seg_ids_vs_segs)

                        cellRule['secs'][seg.name]['geom']['pt3d'].append((prox.x,prox.y,prox.z,prox.diameter))
                        cellRule['secs'][seg.name]['geom']['pt3d'].append((dist.x,dist.y,dist.z,dist.diameter))

                        if seg.parent:
                            parent_seg = seg_ids_vs_segs[seg.parent.segments]
                            cellRule['secs'][seg.name]['topol'] = {'parentSec': parent_seg.name, 'parentX': float(seg.parent.fraction_along), 'childX': 0}
                
                
                else:
                    ordered_segs, cumulative_lengths = cell.get_ordered_segments_in_groups(cellRule['secs'].keys(),include_cumulative_lengths=True)
                    self.pop_ids_vs_ordered_segs[population_id] = ordered_segs
                    self.pop_ids_vs_cumulative_lengths[population_id] = cumulative_lengths
                    
                    for section in cellRule['secs'].keys():
                        #print("ggg %s: %s"%(section,ordered_segs[section]))
                        for seg in ordered_segs[section]:
                            prox, dist = self._get_prox_dist(seg, seg_ids_vs_segs)
                            
                            if seg.id == ordered_segs[section][0].id:
                                cellRule['secs'][section]['geom']['pt3d'].append((prox.x,prox.y,prox.z,prox.diameter))
                                if seg.parent:
                                    parent_seg = seg_ids_vs_segs[seg.parent.segments]
                                    parent_sec = None
                                    #TODO: optimise
                                    for sec in ordered_segs.keys():
                                        if parent_seg.id in [s.id for s in ordered_segs[sec]]:
                                            parent_sec = sec
                                    fract = float(seg.parent.fraction_along)
                                    
                                    assert(fract==1.0 or fract==0.0)
                                    
                                    cellRule['secs'][section]['topol'] = {'parentSec': parent_sec, 'parentX':fract , 'childX': 0}
                                
                            cellRule['secs'][section]['geom']['pt3d'].append((dist.x,dist.y,dist.z,dist.diameter))
                        

                    
                for seg_grp in cell.morphology.segment_groups:
                    seg_grps_vs_nrn_sections[seg_grp.id] = []

                    if not use_segment_groups_for_neuron:
                        for member in seg_grp.members:
                            seg_grps_vs_nrn_sections[seg_grp.id].append(seg_ids_vs_segs[member.segments].name)

                    for inc in seg_grp.includes:
                        
                        if not use_segment_groups_for_neuron:
                            for section_name in seg_grps_vs_nrn_sections[inc.segment_groups]:
                                seg_grps_vs_nrn_sections[seg_grp.id].append(section_name)
                        else:
                            seg_grps_vs_nrn_sections[seg_grp.id].append(inc.segment_groups)
                            if not cellRule['secLists'].has_key(seg_grp.id): cellRule['secLists'][seg_grp.id] = []
                            cellRule['secLists'][seg_grp.id].append(inc.segment_groups)

                    if not seg_grp.neuro_lex_id or seg_grp.neuro_lex_id !="sao864921383":
                        cellRule['secLists'][seg_grp.id] = seg_grps_vs_nrn_sections[seg_grp.id]
                    
                
                for cm in cell.biophysical_properties.membrane_properties.channel_densities:
                    group = 'all' if not cm.segment_groups else cm.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        gmax = pynml.convert_to_units(cm.cond_density,'S_per_cm2')
                        if cm.ion_channel=='pas':
                            mech = {'g':gmax}
                        else:
                            mech = {'gmax':gmax}
                        erev = pynml.convert_to_units(cm.erev,'mV')
                        
                        cellRule['secs'][section_name]['mechs'][cm.ion_channel] = mech
                        
                        if cm.ion and cm.ion == 'non_specific':
                            mech['e'] = erev
                        else:
                            if not cellRule['secs'][section_name]['ions'].has_key(cm.ion):
                                cellRule['secs'][section_name]['ions'][cm.ion] = {}
                            cellRule['secs'][section_name]['ions'][cm.ion]['e'] = erev
                            
                for vi in cell.biophysical_properties.membrane_properties.init_memb_potentials:
                    
                    group = 'all' if not vi.segment_groups else vi.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        cellRule['secs'][section_name]['vinit'] = pynml.convert_to_units(vi.value,'mV')
                            
                for sc in cell.biophysical_properties.membrane_properties.specific_capacitances:
                    
                    group = 'all' if not sc.segment_groups else sc.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        cellRule['secs'][section_name]['geom']['cm'] = pynml.convert_to_units(sc.value,'uF_per_cm2')
                            
                for ra in cell.biophysical_properties.intracellular_properties.resistivities:
                    
                    group = 'all' if not ra.segment_groups else ra.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        cellRule['secs'][section_name]['geom']['Ra'] = pynml.convert_to_units(ra.value,'ohm_cm')
                        
                for specie in cell.biophysical_properties.intracellular_properties.species:
                    
                    group = 'all' if not specie.segment_groups else specie.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        cellRule['secs'][section_name]['ions'][specie.ion]['init_ext_conc'] = pynml.convert_to_units(specie.initial_ext_concentration,'mM')
                        cellRule['secs'][section_name]['ions'][specie.ion]['init_int_conc'] = pynml.convert_to_units(specie.initial_concentration,'mM')
                        
                        cellRule['secs'][section_name]['mechs'][specie.concentration_model] = {}
                        
                
                self.cellParams[component] = cellRule
                
                #for cp in self.cellParams.keys():
                #    pp.pprint(self.cellParams[cp])
                    
                self.pop_ids_vs_seg_ids_vs_segs[population_id] = seg_ids_vs_segs

            else:

                cellRule = {'label': component, 'conds': {'cellType': component, 'cellModel': component},  'sections': {}}

                soma = {'geom': {}, 'pointps':{}}  # soma properties
                default_diam = 10
                soma['geom'] = {'diam': default_diam, 'L': default_diam}
                
                # TODO: add correct hierarchy to Schema for baseCellMembPotCap etc. and use this...
                if hasattr(component_obj,'C'):
                    capTotSI = pynml.convert_to_units(component_obj.C,'F')
                    area = math.pi * default_diam * default_diam
                    specCapNeu = 10e13 * capTotSI / area
                    
                    #print("c: %s, area: %s, sc: %s"%(capTotSI, area, specCapNeu))
                    
                    soma['geom']['cm'] = specCapNeu
                else:
                    
                    soma['geom']['cm'] = 318.319
                    #print("sc: %s"%(soma['geom']['cm']))
                
                soma['pointps'][component] = {'mod':component}
                cellRule['secs'] = {'soma': soma}  # add sections to dict
                self.cellParams[component] = cellRule

            self.gids[population_id] = [-1]*size


        def _convert_to_nrn_section_location(self, population_id, seg_id, fract_along):
            
            if not self.pop_ids_vs_seg_ids_vs_segs.has_key(population_id) or not self.pop_ids_vs_seg_ids_vs_segs[population_id].has_key(seg_id):
                return 'soma', 0.5
            
            if not self.pop_ids_vs_use_segment_groups_for_neuron[population_id]:
                
                return self.pop_ids_vs_seg_ids_vs_segs[population_id][seg_id].name, fract_along
            else:
                fract_sec = -1
                for sec in self.pop_ids_vs_ordered_segs[population_id].keys():
                    ind = 0
                    for seg in self.pop_ids_vs_ordered_segs[population_id][sec]:
                        if seg.id == seg_id:
                            nrn_sec = sec
                            if len(self.pop_ids_vs_ordered_segs[population_id][sec])==1:
                                fract_sec = fract_along
                            else:
                                lens = self.pop_ids_vs_cumulative_lengths[population_id][sec]
                                to_start = 0.0 if ind==0 else lens[ind-1]
                                to_end = lens[ind]
                                tot = lens[-1]
                                print to_start, to_end, tot, ind, seg, seg_id
                                fract_sec = (to_start + fract_along *(to_end-to_start))/(tot)
                            
                        ind+=1
                print("=============  Converted %s:%s on pop %s to %s on %s"%(seg_id, fract_along, population_id, nrn_sec, fract_sec))
                return nrn_sec, fract_sec  

        #
        #  Overridden from DefaultNetworkHandler
        #    
        def handleLocation(self, id, population_id, component, x, y, z):
            DefaultNetworkHandler.printLocationInformation(self,id, population_id, component, x, y, z)

            cellsList = self.popParams[population_id]['cellsList']

            cellsList.append({'cellLabel':id, 'x': x if x else 0, 'y': y if y else 0 , 'z': z if z else 0})
            self.gids[population_id][id] = self.next_gid
            self.next_gid+=1

        #
        #  Overridden from DefaultNetworkHandler
        #
        def handleProjection(self, projName, prePop, postPop, synapse, hasWeights=False, hasDelays=False):


            self.log.info("A projection: "+projName+" from "+prePop+" -> "+postPop+" with syn: "+synapse)
            self.projection_infos[projName] = (projName, prePop, postPop, synapse)
            self.connections[projName] = []

        #
        #  Overridden from DefaultNetworkHandler
        #  
        def handleConnection(self, projName, id, prePop, postPop, synapseType, \
                                                        preCellId, \
                                                        postCellId, \
                                                        preSegId = 0, \
                                                        preFract = 0.5, \
                                                        postSegId = 0, \
                                                        postFract = 0.5, \
                                                        delay = 0, \
                                                        weight = 1):


            pre_seg_name, pre_fract = self._convert_to_nrn_section_location(prePop,preSegId,preFract)
            post_seg_name, post_fract = self._convert_to_nrn_section_location(postPop,postSegId,postFract)

            self.log.info("A connection "+str(id)+" of: "+projName+": "+prePop+"["+str(preCellId)+"]."+pre_seg_name+"("+str(pre_fract)+")" \
                                  +" -> "+postPop+"["+str(postCellId)+"]."+post_seg_name+"("+str(post_fract)+")"+", syn: "+ str(synapseType) \
                                  +", weight: "+str(weight)+", delay: "+str(delay))
                                  
            self.connections[projName].append( (self.gids[prePop][preCellId], pre_seg_name,pre_fract, \
                                                self.gids[postPop][postCellId], post_seg_name, post_fract, \
                                                delay, weight) )



        #
        #  Overridden from DefaultNetworkHandler
        #    
        def handleInputList(self, inputListId, population_id, component, size):
            DefaultNetworkHandler.printInputInformation(self,inputListId, population_id, component, size)
            
            
            self.popStimSources[inputListId] = {'label': inputListId, 'type': component}
            self.popStimLists[inputListId] = {'source': inputListId, 
                        'conds': {'popLabel':population_id}}
            
            # TODO: build just one stimLists/stimSources entry for the inputList
            # Issue: how to specify the sec/loc per individual stim??
            '''
            self.stimSources[inputListId] = {'label': inputListId, 'type': component}
            self.stimLists[inputListId] = {
                        'source': inputListId, 
                        'sec':'soma', 
                        'loc': 0.5, 
                        'conds': {'popLabel':population_id, 'cellList': []}}'''


        #
        #  Overridden from DefaultNetworkHandler
        #   
        def handleSingleInput(self, inputListId, id, cellId, segId = 0, fract = 0.5):
            
            pop_id = self.popStimLists[inputListId]['conds']['popLabel']
            nrn_sec, nrn_fract = self._convert_to_nrn_section_location(pop_id,segId,fract)
            
            #seg_name = self.pop_ids_vs_seg_ids_vs_segs[pop_id][segId].name if self.pop_ids_vs_seg_ids_vs_segs.has_key(pop_id) else 'soma'
            
            stimId = "%s_%s_%s_%s_%s"%(inputListId,pop_id,cellId,nrn_sec,(str(fract)).replace('.','_'))
            
            self.stimSources[stimId] = {'label': stimId, 'type': self.popStimSources[inputListId]['type']}
            self.stimLists[stimId] = {'source': stimId, 
                        'sec':nrn_sec, 
                        'loc': nrn_fract, 
                        'conds': {'popLabel':pop_id, 'cellList': [cellId]}}
                        
            
            print("Input: %s[%s] on %s, cellId: %i, seg: %i (nrn: %s), fract: %f (nrn: %f); ref: %s" % (inputListId,id,pop_id,cellId,segId,nrn_sec,fract,nrn_fract,stimId))
            
            # TODO: build just one stimLists/stimSources entry for the inputList
            # Issue: how to specify the sec/loc per individual stim??
            #self.stimLists[inputListId]['conds']['cellList'].append(cellId)
            #self.stimLists[inputListId]['conds']['secList'].append(seg_name)
            #self.stimLists[inputListId]['conds']['locList'].append(fract)

    ###############################################################################
    # Import network from NeuroML2
    ###############################################################################
    def importNeuroML2(fileName, simConfig):

        netParams = specs.NetParams()

        import pprint
        pp = pprint.PrettyPrinter(indent=4)

        print("Importing NeuroML 2 network from: %s"%fileName)

        nmlHandler = None

        if fileName.endswith(".nml"):

            import logging
            logging.basicConfig(level=logging.DEBUG, format="%(name)-19s %(levelname)-5s - %(message)s")

            from neuroml.hdf5.NeuroMLXMLParser import NeuroMLXMLParser

            nmlHandler = NetPyNEBuilder(netParams)     

            currParser = NeuroMLXMLParser(nmlHandler) # The HDF5 handler knows of the structure of NeuroML and calls appropriate functions in NetworkHandler

            currParser.parse(fileName)

            nmlHandler.finalise()

            print('Finished import: %s'%nmlHandler.gids)
            print('Connections: %s'%nmlHandler.connections)


        sim.initialize(netParams, simConfig)  # create network object and set cfg and net params

        #pp.pprint(netParams)
        #pp.pprint(simConfig)

        sim.net.createPops()  
        cells = sim.net.createCells()                 # instantiate network cells based on defined populations  


        # Check gids equal....
        for popLabel,pop in sim.net.pops.iteritems():
            #print("%s: %s, %s"%(popLabel,pop, pop.cellGids))
            for gid in pop.cellGids:
                assert(gid in nmlHandler.gids[popLabel])
            
        for proj_id in nmlHandler.projection_infos.keys():
            projName, prePop, postPop, synapse = nmlHandler.projection_infos[proj_id]
            print("Creating connections for %s: %s->%s via %s"%(projName, prePop, postPop, synapse))
            
            preComp = nmlHandler.pop_ids_vs_components[prePop]
            
            from neuroml import Cell
            
            if isinstance(preComp,Cell):
                if len(preComp.biophysical_properties.membrane_properties.spike_threshes)>0:
                    st = preComp.biophysical_properties.membrane_properties.spike_threshes[0]
                    # Ensure threshold is same everywhere on cell
                    assert(st.segment_groups=='all')
                    assert(len(preComp.biophysical_properties.membrane_properties.spike_threshes)==1)
                    threshold = pynml.convert_to_units(st.value,'mV')
                else:
                    threshold = 0
            elif hasattr(preComp,'thresh'):
                threshold = pynml.convert_to_units(preComp.thresh,'mV')
            else:
                threshold = 0

            for conn in nmlHandler.connections[projName]:
                
                pre_id, pre_seg, pre_fract, post_id, post_seg, post_fract, delay, weight = conn
                
                connParam = {'delay':delay,'weight':weight,'synsPerConn':1, 'sec':post_seg, 'loc':post_fract, 'threshold':threshold}
                
                connParam['synMech'] = synapse

                if post_id in sim.net.lid2gid:  # check if postsyn is in this node's list of gids
                    sim.net._addCellConn(connParam, pre_id, post_id)

        #conns = sim.net.connectCells()                # create connections between cells based on params
        stims = sim.net.addStims()                    # add external stimulation to cells (IClamps etc)
        simData = sim.setupRecording()              # setup variables to record for each cell (spikes, V traces, etc)
        sim.runSim()                      # run parallel Neuron simulation  
        sim.gatherData()                  # gather spiking data and cell info from each node
        sim.saveData()                    # save params, cell info and sim output to file (pickle,mat,txt,etc)
        sim.analysis.plotData()               # plot spike raster
        '''
        h('forall psection()')
        h('forall  if (ismembrane("na_ion")) { print "Na ions: ", secname(), ": ena: ", ena, ", nai: ", nai, ", nao: ", nao } ')
        h('forall  if (ismembrane("k_ion")) { print "K ions: ", secname(), ": ek: ", ek, ", ki: ", ki, ", ko: ", ko } ')
        h('forall  if (ismembrane("ca_ion")) { print "Ca ions: ", secname(), ": eca: ", eca, ", cai: ", cai, ", cao: ", cao } ')'''

        return nmlHandler.gids
