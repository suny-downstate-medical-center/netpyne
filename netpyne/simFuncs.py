"""
simFunc.py
Contains functions related to the simulation (eg. setupRecording, runSim)
Contributors: salvadordura@gmail.com
"""

__all__ = []
__all__.extend(['initialize', 'setNet', 'setNetParams', 'setSimCfg', 'createParallelContext', 'setupRecording', 'setupRecordLFP', 'calculateLFP', 'clearAll', 'setGlobals']) # init and setup
__all__.extend(['preRun', 'runSim', 'runSimWithIntervalFunc', '_gatherAllCellTags', '_gatherAllCellConnPreGids', '_gatherCells', 'gatherData'])  # run and gather
__all__.extend(['saveData', 'loadSimCfg', 'loadNetParams', 'loadNet', 'loadSimData', 'loadAll', 'ijsonLoad', 'compactConnFormat', 'distributedSaveHDF5', 'loadHDF5']) # saving and loading
__all__.extend(['popAvgRates', 'id32', 'copyReplaceItemObj', 'clearObj', 'replaceItemObj', 'replaceNoneObj', 'replaceFuncObj', 'replaceDictODict', 
    'readCmdLineArgs', 'getCellsList', 'cellByGid','timing',  'version', 'gitChangeset', 'loadBalance','_init_stim_randomizer', 'decimalToFloat', 'unique',
    'rename'])  # misc/utilities

import sys
import os
import numpy as np
from time import time
from datetime import datetime
import pickle as pk
import hashlib
from numbers import Number
from copy import copy
from .specs import Dict, ODict
from collections import OrderedDict
from neuron import h, init # Import NEURON
from . import specs

###############################################################################
# initialize variables and MPI
###############################################################################
def initialize (netParams = None, simConfig = None, net = None):
    from . import sim

    if netParams is None: netParams = {} # If not specified, initialize as empty dict
    if simConfig is None: simConfig = {} # If not specified, initialize as empty dict
    if hasattr(simConfig, 'popParams') or hasattr(netParams, 'duration'):
        print('Error: seems like the sim.initialize() arguments are in the wrong order, try initialize(netParams, simConfig)')
        sys.exit()

    # for testing validation
    # if simConfig.exitOnError:
    #sys.exit()

    sim.simData = Dict()  # used to store output simulation data (spikes etc)
    sim.fih = []  # list of func init handlers
    sim.rank = 0  # initialize rank
    sim.nextHost = 0  # initialize next host
    sim.timingData = Dict()  # dict to store timing

    sim.createParallelContext()  # inititalize PC, nhosts and rank
    sim.cvode = h.CVode()

    sim.setSimCfg(simConfig)  # set simulation configuration

    if sim.rank==0:
        sim.timing('start', 'initialTime')
        sim.timing('start', 'totalTime')

    if net:
        sim.setNet(net)  # set existing external network
    else:
        sim.setNet(sim.Network())  # or create new network

    sim.setNetParams(netParams)  # set network parameters

    if sim.cfg.enableRxD:
        try:
            global rxd
            from neuron import crxd as rxd 
            sim.net.rxd = {'species': {}, 'regions': {}}  # dictionary for rxd  
        except:
            print('cRxD module not available')

    if sim.nhosts > 1: sim.cfg.checkErrors = False  # turn of error chceking if using multiple cores

    if hasattr(sim.cfg, 'checkErrors') and sim.cfg.checkErrors: # whether to validate the input parameters
        try:
            simTestObj = sim.SimTestObj(sim.cfg.checkErrorsVerbose)
            simTestObj.simConfig = sim.cfg
            simTestObj.netParams = sim.net.params
            simTestObj.runTests()
        except:
            print("\nAn exception occurred during the error checking process...")
            
    sim.timing('stop', 'initialTime')


###############################################################################
# Set network object to use in simulation
###############################################################################
def setNet (net):
    from . import sim
    sim.net = net


###############################################################################
# Set network params to use in simulation
###############################################################################
def setNetParams (params):
    from . import sim

    if params and isinstance(params, specs.NetParams):
        paramsDict = replaceKeys(params.todict(), 'popLabel', 'pop')  # for backward compatibility
        sim.net.params = specs.NetParams(paramsDict)  # convert back to NetParams obj
    elif params and isinstance(params, dict):
        params = replaceKeys(params, 'popLabel', 'pop')  # for backward compatibility
        sim.net.params = specs.NetParams(params)
    else:
        sim.net.params = specs.NetParams()

###############################################################################
# Set simulation config
###############################################################################
def setSimCfg (cfg):
    from . import sim

    if cfg and isinstance(cfg, specs.SimConfig):
        sim.cfg = cfg  # set
    elif cfg and isinstance(cfg, dict):
        sim.cfg = specs.SimConfig(cfg) # fill in with dict
    else:
        sim.cfg = specs.SimConfig()  # create new object

    if sim.cfg.simLabel and sim.cfg.saveFolder:
        sim.cfg.filename = sim.cfg.saveFolder+'/'+sim.cfg.simLabel


###############################################################################
# Create parallel context
###############################################################################
def createParallelContext ():
    from . import sim

    sim.pc = h.ParallelContext() # MPI: Initialize the ParallelContext class
    sim.pc.done()
    sim.nhosts = int(sim.pc.nhost()) # Find number of hosts
    sim.rank = int(sim.pc.id())     # rank or node number (0 will be the master)

    if sim.rank==0:
        sim.pc.gid_clear()


###############################################################################
# Load netParams from cell
###############################################################################
def loadNetParams (filename, data=None, setLoaded=True):
    if not data: data = _loadFile(filename)
    print('Loading netParams...')
    if 'net' in data and 'params' in data['net']:
        if setLoaded:
            setNetParams(data['net']['params'])
        else:
            return specs.NetParams(data['net']['params'])
    else:
        print(('netParams not found in file %s'%(filename)))

    pass


###############################################################################
# Convert compact (list-based) to long (dict-based) conn format
###############################################################################
def compactToLongConnFormat(cells, connFormat):
    
    formatIndices = {key: connFormat.index(key) for key in connFormat}
    try:
        for cell in cells:
            for iconn, conn in enumerate(cell['conns']):
                cell['conns'][iconn] = {key: conn[index] for key,index in formatIndices.items()}
        return cells
    except:
        print("Error converting conns from compact to long format")
        return cells


###############################################################################
# Load cells and pops from file and create NEURON objs
###############################################################################
def loadNet (filename, data=None, instantiate=True, compactConnFormat=False):
    from . import sim

    if not data: data = _loadFile(filename)
    if 'net' in data and 'cells' in data['net'] and 'pops' in data['net']:
        if sim.rank == 0:
            sim.timing('start', 'loadNetTime')
            print('Loading net...')
            if compactConnFormat: 
                compactToLongConnFormat(data['net']['cells'], compactConnFormat) # convert loaded data to long format 
            sim.net.allPops = data['net']['pops']
            sim.net.allCells = data['net']['cells']
        if instantiate:
            # calculate cells to instantiate in this node
            if isinstance(instantiate, list):
                cellsNode = [data['net']['cells'][i] for i in range(int(sim.rank), len(data['net']['cells']), sim.nhosts) if i in instantiate]
            else:
                cellsNode = [data['net']['cells'][i] for i in range(int(sim.rank), len(data['net']['cells']), sim.nhosts)]
            if sim.cfg.createPyStruct:
                for popLoadLabel, popLoad in data['net']['pops'].items():
                    pop = sim.Pop(popLoadLabel, popLoad['tags'])
                    pop.cellGids = popLoad['cellGids']
                    sim.net.pops[popLoadLabel] = pop
                for cellLoad in cellsNode:
                    # create new CompartCell object and add attributes, but don't create sections or associate gid yet
                    # TO DO: assumes CompartCell -- add condition to load PointCell
                    cell = sim.CompartCell(gid=cellLoad['gid'], tags=cellLoad['tags'], create=False, associateGid=False)
                    try:
                        if sim.cfg.saveCellSecs:
                            cell.secs = Dict(cellLoad['secs'])
                        else:
                            createNEURONObjorig = sim.cfg.createNEURONObj
                            sim.cfg.createNEURONObj = False  # avoid creating NEURON Objs now; just needpy struct
                            cell.create()
                            sim.cfg.createNEURONObj = createNEURONObjorig
                    except:
                        if sim.cfg.verbose: print(' Unable to load cell secs')

                    try:
                        cell.conns = [Dict(conn) for conn in cellLoad['conns']]
                    except:
                        if sim.cfg.verbose: print(' Unable to load cell conns')

                    try:
                        cell.stims = [Dict(stim) for stim in cellLoad['stims']]
                    except:
                        if sim.cfg.verbose: print(' Unable to load cell stims')

                    sim.net.cells.append(cell)
                print(('  Created %d cells' % (len(sim.net.cells))))
                print(('  Created %d connections' % (sum([len(c.conns) for c in sim.net.cells]))))
                print(('  Created %d stims' % (sum([len(c.stims) for c in sim.net.cells]))))

                # only create NEURON objs, if there is Python struc (fix so minimal Python struct is created)
                if sim.cfg.createNEURONObj:
                    if sim.cfg.verbose: print("  Adding NEURON objects...")
                    # create NEURON sections, mechs, syns, etc; and associate gid
                    for cell in sim.net.cells:
                        prop = {'secs': cell.secs}
                        cell.createNEURONObj(prop)  # use same syntax as when creating based on high-level specs
                        cell.associateGid()  # can only associate once the hSection obj has been created
                    # create all NEURON Netcons, NetStims, etc
                    sim.pc.barrier()
                    for cell in sim.net.cells:
                        try:
                            cell.addStimsNEURONObj()  # add stims first so can then create conns between netstims
                            cell.addConnsNEURONObj()
                        except:
                            if sim.cfg.verbose: ' Unable to load instantiate cell conns or stims'

                    print(('  Added NEURON objects to %d cells' % (len(sim.net.cells))))

            if sim.rank == 0 and sim.cfg.timing:
                sim.timing('stop', 'loadNetTime')
                print(('  Done; re-instantiate net time = %0.2f s' % sim.timingData['loadNetTime']))
    else:
        print(('  netCells and/or netPops not found in file %s'%(filename)))


###############################################################################
# Load simulation config from file
###############################################################################
def loadSimCfg (filename, data=None, setLoaded=True):
    if not data: data = _loadFile(filename)
    print('Loading simConfig...')
    if 'simConfig' in data:
        if setLoaded:
            setSimCfg(data['simConfig'])
        else:
            return specs.SimConfig(data['simConfig'])
    else:
        print(('  simConfig not found in file %s'%(filename)))
    pass


###############################################################################
# Load netParams from cell
###############################################################################
def loadSimData (filename, data=None):
    from . import sim
    if not data: 
        data = _loadFile(filename)
    print('Loading simData...')
    if 'simData' in data:
        sim.allSimData = data['simData']
        print('done')
    else:
        print(6)
        print(('  simData not found in file %s'%(filename)))
    pass


###############################################################################
# Load all data in file
###############################################################################
def loadAll (filename, data=None, instantiate=True, createNEURONObj=True):
    from . import sim 
    if not data: data = _loadFile(filename)
    
    loadSimCfg(filename, data=data)
    sim.cfg.createNEURONObj = createNEURONObj  # set based on argument
    loadNetParams(filename, data=data)
    if hasattr(sim.cfg, 'compactConnFormat'): 
        connFormat = sim.cfg.compactConnFormat
    else:
        print('Error: no connFormat provided in simConfig')
        sys.exit()
    loadNet(filename, data=data, instantiate=instantiate, compactConnFormat=connFormat)
    loadSimData(filename, data=data)


###############################################################################
# Fast function to find unique elements in sequence and preserve order
###############################################################################
def unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


###############################################################################
# Support funcs to load from mat
###############################################################################
def _mat2dict(obj): 
    '''
    A recursive function which constructs from matobjects nested dictionaries
    Enforce lists for conns, synMechs and stims even if 1 element (matlab converts to dict otherwise)
    '''
    import scipy.io as spio
    import numpy as np

    if isinstance(obj, dict):
        out = {}
        for key in obj:
            if isinstance(obj[key], spio.matlab.mio5_params.mat_struct):
                if key in ['conns', 'stims', 'synMechs']:
                    out[key] = [_mat2dict(obj[key])]  # convert to 1-element list
                else:
                    out[key] = _mat2dict(obj[key])
            elif isinstance(obj[key], np.ndarray):
                out[key] = _mat2dict(obj[key])
            else:
                out[key] = obj[key]

    elif isinstance(obj, spio.matlab.mio5_params.mat_struct):
        out = {}
        for key in obj._fieldnames:
            val = obj.__dict__[key]
            if isinstance(val, spio.matlab.mio5_params.mat_struct):
                if key in ['conns', 'stims', 'synMechs']:
                    out[key] = [_mat2dict(val)]  # convert to 1-element list
                else:
                    out[key] = _mat2dict(val)
            elif isinstance(val, np.ndarray):
                out[key] = _mat2dict(val)
            else:
                out[key] = val

    elif isinstance(obj, np.ndarray):
        out = []
        for item in obj:
            if isinstance(item, spio.matlab.mio5_params.mat_struct) or isinstance(item, np.ndarray):
                out.append(_mat2dict(item))
            else:
                out.append(item)

    else:
        out = obj

    return out


###############################################################################
# Load data from file
###############################################################################
def _loadFile (filename):
    from . import sim
    import os

    def _byteify(data, ignore_dicts = False):
        # if this is a unicode string, return its string representation
        if isinstance(data, str):
            return data.encode('utf-8')
        # if this is a list of values, return list of byteified values
        if isinstance(data, list):
            return [ _byteify(item, ignore_dicts=True) for item in data ]
        # if this is a dictionary, return dictionary of byteified keys and values
        # but only if we haven't already byteified it
        if isinstance(data, dict) and not ignore_dicts:
            return OrderedDict({
                _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
                for key, value in data.items()
            })
        # if it's anything else, return it in its original form
        return data

    if hasattr(sim, 'cfg') and sim.cfg.timing: sim.timing('start', 'loadFileTime')
    ext = os.path.basename(filename).split('.')[1]

    # load pickle file
    if ext == 'pkl':
        import pickle
        print(('Loading file %s ... ' % (filename)))
        with open(filename, 'rb') as fileObj:
            if sys.version_info[0] == 2:
                data = pickle.load(fileObj)
            else:
                data = pickle.load(fileObj, encoding='latin1')

    # load dpk file
    elif ext == 'dpk':
        import gzip
        print(('Loading file %s ... ' % (filename)))
        #fn=sim.cfg.filename #.split('.')
        #gzip.open(fn, 'wb').write(pk.dumps(dataSave)) # write compressed string
        print('NOT IMPLEMENTED!')

    # load json file
    elif ext == 'json':
        import json
        print(('Loading file %s ... ' % (filename)))
        with open(filename, 'r') as fileObj:
            data = json.load(fileObj)

    # load mat file
    elif ext == 'mat':
        from scipy.io import loadmat
        print(('Loading file %s ... ' % (filename)))
        dataraw = loadmat(filename, struct_as_record=False, squeeze_me=True)
        data = _mat2dict(dataraw)
        #savemat(sim.cfg.filename+'.mat', replaceNoneObj(dataSave))  # replace None and {} with [] so can save in .mat format
        print('Finished saving!')

    # load HDF5 file (uses very inefficient hdf5storage module which supports dicts)
    elif ext == 'saveHDF5':
        #dataSaveUTF8 = _dict2utf8(replaceNoneObj(dataSave)) # replace None and {} with [], and convert to utf
        import hdf5storage
        print(('Loading file %s ... ' % (filename)))
        #hdf5storage.writes(dataSaveUTF8, filename=sim.cfg.filename+'.hdf5')
        print('NOT IMPLEMENTED!')

    # load CSV file (currently only saves spikes)
    elif ext == 'csv':
        import csv
        print(('Loading file %s ... ' % (filename)))
        writer = csv.writer(open(sim.cfg.filename+'.csv', 'wb'))
        #for dic in dataSave['simData']:
        #    for values in dic:
        #        writer.writerow(values)
        print('NOT IMPLEMENTED!')

    # load Dat file(s)
    elif ext == 'dat':
        print(('Loading file %s ... ' % (filename)))
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
        print(('Format not recognized for file %s'%(filename)))
        return

    if hasattr(sim, 'rank') and sim.rank == 0 and hasattr(sim, 'cfg') and sim.cfg.timing:
        sim.timing('stop', 'loadFileTime')
        print(('  Done; file loading time = %0.2f s' % sim.timingData['loadFileTime']))


    return data

###############################################################################
# Clear all sim objects in memory
###############################################################################
def clearAll ():
    from . import sim

    # clean up
    sim.pc.barrier()
    sim.pc.gid_clear()                    # clear previous gid settings

    # clean cells and simData in all nodes
    sim.clearObj([cell.__dict__ if hasattr(cell, '__dict__') else cell for cell in sim.net.cells])
    if 'stims' in list(sim.simData.keys()):
        sim.clearObj([stim for stim in sim.simData['stims']])
    for key in list(sim.simData.keys()): del sim.simData[key]
    for c in sim.net.cells: del c
    for p in sim.net.pops: del p
    del sim.net.params


    # clean cells and simData gathered in master node
    if sim.rank == 0:
        if hasattr(sim.net, 'allCells'):
            sim.clearObj([cell.__dict__ if hasattr(cell, '__dict__') else cell for cell in sim.net.allCells])
        if hasattr(sim, 'allSimData') and 'stims' in list(sim.allSimData.keys()):
            sim.clearObj([stim for stim in sim.allSimData['stims']])
        for key in list(sim.allSimData.keys()): del sim.allSimData[key]
        for c in sim.net.allCells: del c
        for p in sim.net.allPops: del p
        del sim.net.allCells
        del sim.allSimData

        import matplotlib
        matplotlib.pyplot.clf()
        matplotlib.pyplot.close('all')

    del sim.net

    import gc; gc.collect()



###############################################################################
# Hash function to obtain random value
###############################################################################
def id32 (obj):
    #return hash(obj) & 0xffffffff  # hash func
    return int(hashlib.md5(obj.encode('utf-8')).hexdigest()[0:8],16)  # convert 8 first chars of md5 hash in base 16 to int


###############################################################################
# Initialize the stim randomizer
###############################################################################
def _init_stim_randomizer(rand, stimType, gid, seed):
    from . import sim

    rand.Random123(sim.id32(stimType), gid, seed)


###############################################################################
### Replace item with specific key from dict or list (used to remove h objects)
###############################################################################
def copyReplaceItemObj (obj, keystart, newval, objCopy='ROOT'):
    if type(obj) == list:
        if objCopy=='ROOT':
            objCopy = []
        for item in obj:
            if isinstance(item, list):
                objCopy.append([])
                copyReplaceItemObj(item, keystart, newval, objCopy[-1])
            elif isinstance(item, (dict, Dict)):
                objCopy.append({})
                copyReplaceItemObj(item, keystart, newval, objCopy[-1])
            else:
                objCopy.append(item)

    elif isinstance(obj, (dict, Dict)):
        if objCopy == 'ROOT':
            objCopy = Dict()
        for key,val in obj.items():
            if type(val) in [list]:
                objCopy[key] = []
                copyReplaceItemObj(val, keystart, newval, objCopy[key])
            elif isinstance(val, (dict, Dict)):
                objCopy[key] = {}
                copyReplaceItemObj(val, keystart, newval, objCopy[key])
            elif key.startswith(keystart):
                objCopy[key] = newval
            else:
                objCopy[key] = val
    return objCopy


###############################################################################
### Rename objects
###############################################################################
def rename (obj, old, new, label=None):
    try:
        return obj.rename(old, new, label)
    except:
        if type(obj) == dict and old in obj:
            obj[new] = obj.pop(old)  # replace
            return True
        else:
            return False



###############################################################################
### Recursively remove items of an object (used to avoid mem leaks)
###############################################################################
def clearObj (obj):
    if type(obj) == list:
        for item in obj:
            if isinstance(item, (list, dict, Dict, ODict)):
                clearObj(item)
            del item

    elif isinstance(obj, (dict, Dict, ODict)):
        for key in list(obj.keys()):
            val = obj[key]
            if isinstance(val, (list, dict, Dict, ODict)):
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
        for key,val in obj.items():
            if type(val) in [list, dict]:
                replaceItemObj(val, keystart, newval)
            if key.startswith(keystart):
                obj[key] = newval
    return obj


###############################################################################
### Recursivele replace dict keys
###############################################################################
def replaceKeys (obj, oldkey, newkey):
    if type(obj) == list:
        for item in obj:
            if isinstance(item, (list, dict, Dict, ODict, OrderedDict)):
                replaceKeys(item, oldkey, newkey)

    elif isinstance(obj, (dict, Dict, ODict, OrderedDict)):
        for key in list(obj.keys()):
            val = obj[key]
            if isinstance(val, (list, dict, Dict, ODict, OrderedDict)):
                replaceKeys(val, oldkey, newkey)
            if key == oldkey:
                obj[newkey] = obj.pop(oldkey)
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
        for key,val in obj.items():
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
            if isinstance(item, (list, dict, Dict, ODict)):
                replaceNoneObj(item)

    elif isinstance(obj, (dict, Dict, ODict)):
        for key,val in obj.items():
            if isinstance(val, (list, dict, Dict, ODict)):
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
        for key,val in obj.items():
            if type(val) == Dict:
                obj[key] = val.todict()
            elif type(val) == ODict:
                obj[key] = val.toOrderedDict()
            if type(val) in [list, dict, OrderedDict]:
                replaceDictODict(val)

    return obj

###############################################################################
### Replace tuples with str
###############################################################################
def tupleToList (obj):
    if type(obj) == list:
        for item in obj:
            if type(item) in [list, dict]:
                tupleToList(item)
            elif type(item) == tuple:
                obj[obj.index(item)] = list(item)

    elif isinstance(obj, (dict, ODict)):
        for key,val in obj.items():
            if isinstance(val, (list, dict, ODict)):
                tupleToList(val)
            elif type(val) == tuple:
                obj[key] = list(val) # also replace empty dicts with empty list
    return obj


###############################################################################
### Replace Decimal with float
###############################################################################
def decimalToFloat (obj):
    from decimal import Decimal
    if type(obj) == list:
        for i,item in enumerate(obj):
            if type(item) in [list, dict, tuple]:
                decimalToFloat(item)
            elif type(item) == Decimal:
                obj[i] = float(item)

    elif isinstance(obj, dict):
        for key,val in obj.items():
            if isinstance(val, (list, dict)):
                decimalToFloat(val)
            elif type(val) == Decimal:
                obj[key] = float(val) # also replace empty dicts with empty list
    return obj


###############################################################################
### Convert dict strings to utf8 so can be saved in HDF5 format
###############################################################################
def _dict2utf8 (obj):
#unidict = {k.decode('utf8'): v.decode('utf8') for k, v in strdict.items()}
    #print obj
    import collections
    if isinstance(obj, str):
        return obj.decode('utf8')
    elif isinstance(obj, collections.Mapping):
        for key in list(obj.keys()):
            if isinstance(key, Number):
                obj[str(key).decode('utf8')] = obj[key]
                obj.pop(key)
        return dict(list(map(_dict2utf8, iter(obj.items()))))
    elif isinstance(obj, collections.Iterable):
        return type(obj)(list(map(_dict2utf8, obj)))
    else:
        return obj


###############################################################################
### Convert dict strings to utf8 so can be saved in HDF5 format
###############################################################################
def cellByGid (gid):
    from . import sim

    cell = next((c for c in sim.net.cells if c.gid==gid), None)
    return cell


###############################################################################
### Read simConfig and netParams from command line arguments
###############################################################################
def readCmdLineArgs (simConfigDefault='cfg.py', netParamsDefault='netParams.py'):
    from . import sim
    import imp, __main__

    if len(sys.argv) > 1:
        print('\nReading command line arguments using syntax: python file.py [simConfig=filepath] [netParams=filepath]')

    cfgPath = None
    netParamsPath = None

    # read simConfig and netParams paths
    for arg in sys.argv:
        if arg.startswith('simConfig='):
            cfgPath = arg.split('simConfig=')[1]
            cfg = sim.loadSimCfg(cfgPath, setLoaded=False)
            __main__.cfg = cfg
        elif arg.startswith('netParams='):
            netParamsPath = arg.split('netParams=')[1]
            if netParamsPath.endswith('.json'):
                netParams = sim.loadNetParams(netParamsPath,  setLoaded=False)
            elif netParamsPath.endswith('py'):
                netParamsModule = imp.load_source(os.path.basename(netParamsPath).split('.')[0], netParamsPath)
                netParams = netParamsModule.netParams
                print('Importing netParams from %s' %(netParamsPath))

    if not cfgPath:
        try:
            cfgModule = imp.load_source('cfg', simConfigDefault)
            cfg = cfgModule.cfg
            __main__.cfg = cfg
        except:
            print('\nWarning: Could not load cfg from command line path or from default cfg.py')
            cfg = None

    if not netParamsPath:
        try:
            netParamsModule = imp.load_source('netParams', netParamsDefault)
            netParams = netParamsModule.netParams
        except:
            print('\nWarning: Could not load netParams from command line path or from default netParams.py')
            netParams = None

    return cfg, netParams

###############################################################################
### Calculate LFP (fucntion called at every time step)      
###############################################################################
def calculateLFP():
    from . import sim    

    # Set pointers to i_membrane in each cell (required form LFP calc )        
    for cell in sim.net.compartCells:
        cell.setImembPtr()

    # compute 
    saveStep = int(np.floor(h.t / sim.cfg.recordStep))
    for cell in sim.net.compartCells: # compute ecp only from the biophysical cells
        gid = cell.gid
        im = cell.getImemb() # in nA
        tr = sim.net.recXElectrode.getTransferResistance(gid)  # in MOhm
        ecp = np.dot(tr,im) # in mV (= R * I = MOhm * nA)
        if sim.cfg.saveLFPCells: 
            sim.simData['LFPCells'][gid][saveStep-1, :] = ecp  # contribution of individual cells (stored optionally)
        sim.simData['LFP'][saveStep-1, :] += ecp  # sum of all cells


###############################################################################
### Setup LFP Recording
###############################################################################
def setupRecordLFP():
    from . import sim
    from netpyne.support.recxelectrode import RecXElectrode
    
    nsites = len(sim.cfg.recordLFP)
    saveSteps = int(np.ceil(sim.cfg.duration/sim.cfg.recordStep))
    sim.simData['LFP'] = np.zeros((saveSteps, nsites))
    if sim.cfg.saveLFPCells:
        for c in sim.net.cells:
            sim.simData['LFPCells'][c.gid] = np.zeros((saveSteps, nsites))
    
    if not sim.net.params.defineCellShapes: sim.net.defineCellShapes()  # convert cell shapes (if not previously done already)
    sim.net.calcSegCoords()  # calculate segment coords for each cell
    sim.net.recXElectrode = RecXElectrode(sim)  # create exctracellular recording electrode
    
    if sim.cfg.createNEURONObj:
        for cell in sim.net.compartCells:
            nseg = cell._segCoords['p0'].shape[1]
            sim.net.recXElectrode.calcTransferResistance(cell.gid, cell._segCoords)  # transfer resistance for each cell
            cell.imembPtr = h.PtrVector(nseg)  # pointer vector
            cell.imembPtr.ptr_update_callback(cell.setImembPtr)   # used for gathering an array of  i_membrane values from the pointer vector
            cell.imembVec = h.Vector(nseg)

        sim.cvode.use_fast_imem(1)   # make i_membrane_ a range variable
        

###############################################################################
### Setup Recording
###############################################################################
def setupRecording ():
    from . import sim

    timing('start', 'setrecordTime')

    # spike recording
    sim.simData.update({name:h.Vector(1e4).resize(0) for name in ['spkt','spkid']})  # initialize
    sim.pc.spike_record(-1, sim.simData['spkt'], sim.simData['spkid']) # -1 means to record from all cells on this node

    # stim spike recording
    if 'plotRaster' in sim.cfg.analysis:
        if isinstance(sim.cfg.analysis['plotRaster'],dict) and 'include' in sim.cfg.analysis['plotRaster']:
            netStimLabels = list(sim.net.params.stimSourceParams.keys())+['allNetStims']
            for item in sim.cfg.analysis['plotRaster']['include']:
                if item in netStimLabels:
                    sim.cfg.recordStim = True
                    break

    if 'plotSpikeHist' in sim.cfg.analysis:
        if sim.cfg.analysis['plotSpikeHist']==True:
            sim.cfg.recordStim = True

        elif (isinstance(sim.cfg.analysis['plotSpikeHist'],dict) and 'include' in sim.cfg.analysis['plotSpikeHist']) :
            netStimLabels = list(sim.net.params.stimSourceParams.keys())+['allNetStims','eachPop']
            for item in sim.cfg.analysis['plotSpikeHist']['include']:
                if item in netStimLabels:
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

        for key in list(sim.cfg.recordTraces.keys()): sim.simData[key] = Dict()  # create dict to store traces
        for cell in cellsRecord: cell.recordTraces()  # call recordTraces function for each cell

        # record h.t
        if sim.cfg.recordTime and len(sim.simData) > 0:
            try:
                sim.simData['t'] = h.Vector() #sim.cfg.duration/sim.cfg.recordStep+1).resize(0)
                sim.simData['t'].record(h._ref_t, sim.cfg.recordStep)
            except:
                if sim.cfg.verbose: 'Error recording h.t (could be due to no sections existing)'

        # print recorded traces
        cat = 0
        total = 0
        for key in sim.simData:
            if sim.cfg.verbose: print(("   Recording: %s:"%key))
            if len(sim.simData[key])>0: cat+=1
            for k2 in sim.simData[key]:
                if sim.cfg.verbose: print(("      %s"%k2))
                total+=1
        print(("Recording %s traces of %s types on node %i"%(total, cat, sim.rank)))


    # set LFP recording
    if sim.cfg.recordLFP:
        setupRecordLFP()

    timing('stop', 'setrecordTime')

    return sim.simData


###############################################################################
### Get cells list for recording based on set of conditions
###############################################################################
def getCellsList (include):
    from . import sim

    if sim.nhosts > 1 and any(isinstance(cond, tuple) or isinstance(cond,list) for cond in include): # Gather tags from all cells
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

        elif isinstance(condition, tuple) or isinstance(condition, list):  # subset of a pop with relative indices
            cellsPop = [gid for gid,tags in allCellTags.items() if tags['pop']==condition[0]]

            if isinstance(condition[1], list):
                cellGids.extend([gid for i,gid in enumerate(cellsPop) if i in condition[1]])
            elif isinstance(condition[1], int):
                cellGids.extend([gid for i,gid in enumerate(cellsPop) if i==condition[1]])

    cellGids = list(set(cellGids))  # unique values
    cells = [cell for cell in sim.net.cells if cell.gid in cellGids]
    return cells


###############################################################################
### Get cells list for recording based on set of conditions
###############################################################################
def setGlobals ():
    from . import sim

    hParams = sim.cfg.hParams
    # iterate globals dic in each cellParams
    cellGlobs = {k:v for k,v in hParams.items()}
    for cellRuleName, cellRule in sim.net.params.cellParams.items():
        for k,v in cellRule.get('globals', {}).items():
            if k not in cellGlobs:
                cellGlobs[k] = v
            elif cellGlobs[k] != v and sim.cfg.verbose:
                if k == 'v_init':
                    wrongVinit = [s['vinit'] for s in list(cellRule['secs'].values()) if 'vinit' in s and s['vinit'] == v and s['vinit'] != cellGlobs[k]] # check if set inside secs (set by default during import)
                    if len(wrongVinit) == len(cellRule['secs']):
                        print("\nWarning: global variable %s=%s differs from that set for each section in cellParams rule %s: %s" % (k, str(cellGlobs[k]), cellRuleName, str(v)))
                    else: # no need since v_inits set in each sec during import
                        print("\nWarning: global variable %s=%s differs from that defined (not used) in the 'globals' of cellParams rule %s: %s" % (k, str(cellGlobs[k]), cellRuleName, str(v)))
                else:
                    print("\nWarning: global variable %s=%s differs from that defined (not used) in the 'globals' of cellParams rule %s: %s" % (k, str(cellGlobs[k]), cellRuleName, str(v)))
    
    # add tstop as global (for ease of transition with standard NEURON)
    cellGlobs['tstop'] = float(sim.cfg.duration)

    # h global params
    if sim.cfg.verbose and len(cellGlobs) > 0:
        print('\nSetting h global variables ...')
    for key,val in cellGlobs.items():
        try:
            h('%s=%s'%(key,val))
            if sim.cfg.verbose: print(('  h.%s = %s' % (key, str(val))))
        except:
            print('\nError: could not set global %s = %s' % (key, str(val)))


###############################################################################
### Commands required just before running simulation
###############################################################################
def preRun ():
    from . import sim

    # set initial v of cells
    for cell in sim.net.cells:
       sim.fih.append(h.FInitializeHandler(0, cell.initV))

    # cvode variables
    sim.cvode.active(int(sim.cfg.cvode_active))
    sim.cvode.cache_efficient(int(sim.cfg.cache_efficient))
    sim.cvode.atol(sim.cfg.cvode_atol)

    # set h global params
    sim.setGlobals()

    # set h.dt
    h.dt = sim.cfg.dt

    # set v_init if doesn't exist
    if 'v_init' not in sim.cfg.hParams: sim.cfg.hParams['v_init'] = -65.0

    # parallelcontext vars
    sim.pc.set_maxstep(10)
    mindelay = sim.pc.allreduce(sim.pc.set_maxstep(10), 2) # flag 2 returns minimum value
    if sim.rank==0 and sim.cfg.verbose: print(('Minimum delay (time-step for queue exchange) is %.2f'%(mindelay)))
    sim.pc.setup_transfer()  # setup transfer of source_var to target_var

    # handler for printing out time during simulation run
    if sim.rank == 0 and sim.cfg.printRunTime:
        def printRunTime():
            for i in range(int(sim.cfg.printRunTime*1000.0), int(sim.cfg.duration), int(sim.cfg.printRunTime*1000.0)):
                sim.cvode.event(i, 'print ' + str(i/1000.0) + ',"s"')

        sim.printRunTime = printRunTime
        sim.fih.append(h.FInitializeHandler(1, sim.printRunTime))

    # set global index used by all instances of the Random123 instances of Random
    if sim.cfg.rand123GlobalIndex is not None: 
        rand = h.Random()
        rand.Random123_globalindex(int(sim.cfg.rand123GlobalIndex))

    # reset all netstim randomizers so runs are always equivalent
    for cell in sim.net.cells:
        if cell.tags.get('cellModel') == 'NetStim':
            #cell.hRandom.Random123(sim.id32('NetStim'), cell.gid, cell.params['seed'])
            _init_stim_randomizer(cell.hRandom, 'NetStim', cell.gid, cell.params['seed'])
            cell.hRandom.negexp(1)
            cell.hPointp.noiseFromRandom(cell.hRandom)
        pop = sim.net.pops[cell.tags['pop']]
        if 'originalFormat' in pop.tags and pop.tags['originalFormat'] == 'NeuroML2_SpikeSource':
            if sim.cfg.verbose: print("== Setting random generator in NeuroML spike generator")
            cell.initRandom()
        else:
            for stim in cell.stims:
                if 'hRandom' in stim:
                    #stim['hRandom'].Random123(sim.id32(stim['source']), cell.gid, stim['seed'])
                    _init_stim_randomizer(stim['hRandom'], stim['type'], cell.gid, stim['seed'])
                    stim['hRandom'].negexp(1)
                    # Check if noiseFromRandom is in stim['hNetStim']; see https://github.com/Neurosim-lab/netpyne/issues/219
                    if not isinstance(stim['hNetStim'].noiseFromRandom, dict):
                        stim['hNetStim'].noiseFromRandom(stim['hRandom'])

    # handler for recording LFP
    if sim.cfg.recordLFP:
        def recordLFPHandler():
            for i in np.arange(sim.cfg.recordStep, sim.cfg.duration+sim.cfg.recordStep, sim.cfg.recordStep):
                sim.cvode.event(i, sim.calculateLFP)

        sim.recordLFPHandler = recordLFPHandler
        sim.fih.append(h.FInitializeHandler(0, sim.recordLFPHandler))  # initialize imemb


###############################################################################
### Run Simulation
###############################################################################
def runSim ():
    from . import sim

    sim.pc.barrier()
    timing('start', 'runTime')
    preRun()
    
    h.finitialize(float(sim.cfg.hParams['v_init']))

    if sim.rank == 0: print(('\nRunning simulation for %s ms...'%sim.cfg.duration))
    sim.pc.psolve(sim.cfg.duration)

    sim.pc.barrier() # Wait for all hosts to get to this point
    timing('stop', 'runTime')
    if sim.rank==0:
        print(('  Done; run time = %0.2f s; real-time ratio: %0.2f.' %
            (sim.timingData['runTime'], sim.cfg.duration/1000/sim.timingData['runTime'])))


###############################################################################
### Run Simulation
###############################################################################
def runSimWithIntervalFunc (interval, func):
    from . import sim

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
        print(('  Done; run time = %0.2f s; real-time ratio: %0.2f.' %
            (sim.timingData['runTime'], sim.cfg.duration/1000/sim.timingData['runTime'])))


###############################################################################
### Gather tags from cells
###############################################################################
def _gatherAllCellTags ():
    from . import sim

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
### Gather tags from cells
###############################################################################
def _gatherAllCellConnPreGids ():
    from . import sim

    data = [{cell.gid: [conn['preGid'] for conn in cell.conns] for cell in sim.net.cells}]*sim.nhosts  # send cells data to other nodes
    gather = sim.pc.py_alltoall(data)  # collect cells data from other nodes (required to generate connections)
    sim.pc.barrier()
    allCellConnPreGids = {}
    for dataNode in gather:
        allCellConnPreGids.update(dataNode)

    # clean to avoid mem leaks
    for node in gather:
        if node:
            node.clear()
            del node
    for item in data:
        if item:
            item.clear()
            del item

    return allCellConnPreGids


###############################################################################
### Gather data from nodes
###############################################################################
def gatherData (gatherLFP = True):
    from . import sim

    timing('start', 'gatherTime')
    ## Pack data from all hosts
    if sim.rank==0:
        print('\nGathering data...')

    # flag to avoid saving sections data for each cell (saves gather time and space; cannot inspect cell secs or re-simulate)
    if not sim.cfg.saveCellSecs:
        for cell in sim.net.cells:
            cell.secs = None
            cell.secLists = None

    # flag to avoid saving conns data for each cell (saves gather time and space; cannot inspect cell conns or re-simulate)
    if not sim.cfg.saveCellConns:
        for cell in sim.net.cells:
            cell.conns = []

    # Store conns in a compact list format instead of a long dict format (cfg.compactConnFormat contains list of keys to include)
    elif sim.cfg.compactConnFormat:
        sim.compactConnFormat()
            
    # remove data structures used to calculate LFP 
    if gatherLFP and sim.cfg.recordLFP and hasattr(sim.net, 'compartCells') and sim.cfg.createNEURONObj:
        for cell in sim.net.compartCells:
            try:
                del cell.imembVec
                del cell.imembPtr
                del cell._segCoords
            except:
                pass
        for pop in list(sim.net.pops.values()):
            try:
                del pop._morphSegCoords
            except:
                pass

    simDataVecs = ['spkt','spkid','stims']+list(sim.cfg.recordTraces.keys())
    singleNodeVecs = ['t']
    if sim.nhosts > 1:  # only gather if >1 nodes
        netPopsCellGids = {popLabel: list(pop.cellGids) for popLabel,pop in sim.net.pops.items()}

        # gather only sim data
        if getattr(sim.cfg, 'gatherOnlySimData', False):
            nodeData = {'simData': sim.simData}
            data = [None]*sim.nhosts
            data[0] = {}
            for k,v in nodeData.items():
                data[0][k] = v
            gather = sim.pc.py_alltoall(data)
            sim.pc.barrier()

            if sim.rank == 0: # simData
                print('  Gathering only sim data...')
                sim.allSimData = Dict()
                for k in list(gather[0]['simData'].keys()):  # initialize all keys of allSimData dict
                    if gatherLFP and k == 'LFP':
                        sim.allSimData[k] = np.zeros((gather[0]['simData']['LFP'].shape))
                    else:
                        sim.allSimData[k] = {}

                for key in singleNodeVecs: # store single node vectors (eg. 't')
                    sim.allSimData[key] = list(nodeData['simData'][key])

                # fill in allSimData taking into account if data is dict of h.Vector (code needs improvement to be more generic)
                for node in gather:  # concatenate data from each node
                    for key,val in node['simData'].items():  # update simData dics of dics of h.Vector
                        if key in simDataVecs:          # simData dicts that contain Vectors
                            if isinstance(val, dict):
                                for cell,val2 in val.items():
                                    if isinstance(val2,dict):
                                        sim.allSimData[key].update(Dict({cell:Dict()}))
                                        for stim,val3 in val2.items():
                                            sim.allSimData[key][cell].update({stim:list(val3)}) # udpate simData dicts which are dicts of dicts of Vectors (eg. ['stim']['cell_1']['backgrounsd']=h.Vector)
                                    else:
                                        sim.allSimData[key].update({cell:list(val2)})  # udpate simData dicts which are dicts of Vectors (eg. ['v']['cell_1']=h.Vector)
                            else:
                                sim.allSimData[key] = list(sim.allSimData[key])+list(val) # udpate simData dicts which are Vectors
                        elif gatherLFP and key == 'LFP':
                            sim.allSimData[key] += np.array(val)
                        elif key not in singleNodeVecs:
                            sim.allSimData[key].update(val)           # update simData dicts which are not Vectors

                if len(sim.allSimData['spkt']) > 0:
                    sim.allSimData['spkt'], sim.allSimData['spkid'] = list(zip(*sorted(zip(sim.allSimData['spkt'], sim.allSimData['spkid'])))) # sort spks

                sim.net.allPops = ODict() # pops
                for popLabel,pop in sim.net.pops.items(): sim.net.allPops[popLabel] = pop.__getstate__() # can't use dict comprehension for OrderedDict

                sim.net.allCells = [c.__dict__ for c in sim.net.cells]

        # gather cells, pops and sim data
        else:
            nodeData = {'netCells': [c.__getstate__() for c in sim.net.cells], 'netPopsCellGids': netPopsCellGids, 'simData': sim.simData}
            data = [None]*sim.nhosts
            data[0] = {}
            for k,v in nodeData.items():
                data[0][k] = v
            
            #print data
            gather = sim.pc.py_alltoall(data)
            sim.pc.barrier()
            if sim.rank == 0:
                allCells = []
                allPops = ODict()
                for popLabel,pop in sim.net.pops.items(): allPops[popLabel] = pop.__getstate__() # can't use dict comprehension for OrderedDict
                allPopsCellGids = {popLabel: [] for popLabel in netPopsCellGids}
                sim.allSimData = Dict()

                for k in list(gather[0]['simData'].keys()):  # initialize all keys of allSimData dict
                    if gatherLFP and k == 'LFP':
                        sim.allSimData[k] = np.zeros((gather[0]['simData']['LFP'].shape))
                    else:
                        sim.allSimData[k] = {}

                for key in singleNodeVecs:  # store single node vectors (eg. 't')
                    sim.allSimData[key] = list(nodeData['simData'][key])

                # fill in allSimData taking into account if data is dict of h.Vector (code needs improvement to be more generic)
                for node in gather:  # concatenate data from each node
                    allCells.extend(node['netCells'])  # extend allCells list
                    for popLabel,popCellGids in node['netPopsCellGids'].items():
                        allPopsCellGids[popLabel].extend(popCellGids)

                    for key,val in node['simData'].items():  # update simData dics of dics of h.Vector
                        if key in simDataVecs:          # simData dicts that contain Vectors
                            if isinstance(val,dict):
                                for cell,val2 in val.items():
                                    if isinstance(val2,dict):
                                        sim.allSimData[key].update(Dict({cell:Dict()}))
                                        for stim,val3 in val2.items():
                                            sim.allSimData[key][cell].update({stim:list(val3)}) # udpate simData dicts which are dicts of dicts of Vectors (eg. ['stim']['cell_1']['backgrounsd']=h.Vector)
                                    else:
                                        sim.allSimData[key].update({cell:list(val2)})  # udpate simData dicts which are dicts of Vectors (eg. ['v']['cell_1']=h.Vector)
                            else:
                                sim.allSimData[key] = list(sim.allSimData[key])+list(val) # udpate simData dicts which are Vectors
                        elif gatherLFP and key == 'LFP':
                            sim.allSimData[key] += np.array(val)
                        elif key not in singleNodeVecs:
                            sim.allSimData[key].update(val)           # update simData dicts which are not Vectors

                if len(sim.allSimData['spkt']) > 0:
                    sim.allSimData['spkt'], sim.allSimData['spkid'] = list(zip(*sorted(zip(sim.allSimData['spkt'], sim.allSimData['spkid'])))) # sort spks

                sim.net.allCells =  sorted(allCells, key=lambda k: k['gid'])

                for popLabel,pop in allPops.items():
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
        for popLabel,pop in sim.net.pops.items(): sim.net.allPops[popLabel] = pop.__getstate__() # can't use dict comprehension for OrderedDict
        sim.allSimData = Dict()
        for k in list(sim.simData.keys()):  # initialize all keys of allSimData dict
            sim.allSimData[k] = Dict()
        for key,val in sim.simData.items():  # update simData dics of dics of h.Vector
                if key in simDataVecs+singleNodeVecs:          # simData dicts that contain Vectors
                    if isinstance(val,dict):
                        for cell,val2 in val.items():
                            if isinstance(val2,dict):
                                sim.allSimData[key].update(Dict({cell:Dict()}))
                                for stim,val3 in val2.items():
                                    sim.allSimData[key][cell].update({stim:list(val3)}) # udpate simData dicts which are dicts of dicts of Vectors (eg. ['stim']['cell_1']['backgrounsd']=h.Vector)
                            else:
                                sim.allSimData[key].update({cell:list(val2)})  # udpate simData dicts which are dicts of Vectors (eg. ['v']['cell_1']=h.Vector)
                    else:
                        sim.allSimData[key] = list(sim.allSimData[key])+list(val) # udpate simData dicts which are Vectors
                else:
                    sim.allSimData[key] = val           # update simData dicts which are not Vectors

    ## Print statistics
    sim.pc.barrier()
    if sim.rank == 0:
        timing('stop', 'gatherTime')
        if sim.cfg.timing: print(('  Done; gather time = %0.2f s.' % sim.timingData['gatherTime']))

        print('\nAnalyzing...')
        sim.totalSpikes = len(sim.allSimData['spkt'])
        sim.totalSynapses = sum([len(cell['conns']) for cell in sim.net.allCells])
        if sim.cfg.createPyStruct:
            if sim.cfg.compactConnFormat:
                preGidIndex = sim.cfg.compactConnFormat.index('preGid') if 'preGid' in sim.cfg.compactConnFormat else 0
                sim.totalConnections = sum([len(set([conn[preGidIndex] for conn in cell['conns']])) for cell in sim.net.allCells])
            else:
                sim.totalConnections = sum([len(set([conn['preGid'] for conn in cell['conns']])) for cell in sim.net.allCells])
        else:
            sim.totalConnections = sim.totalSynapses
        sim.numCells = len(sim.net.allCells)

        if sim.totalSpikes > 0:
            sim.firingRate = float(sim.totalSpikes)/sim.numCells/sim.cfg.duration*1e3 # Calculate firing rate
        else:
            sim.firingRate = 0
        if sim.numCells > 0:
            sim.connsPerCell = sim.totalConnections/float(sim.numCells) # Calculate the number of connections per cell
            sim.synsPerCell = sim.totalSynapses/float(sim.numCells) # Calculate the number of connections per cell
        else:
            sim.connsPerCell = 0
            sim.synsPerCell = 0

        print(('  Cells: %i' % (sim.numCells) ))
        print(('  Connections: %i (%0.2f per cell)' % (sim.totalConnections, sim.connsPerCell)))
        if sim.totalSynapses != sim.totalConnections:
            print(('  Synaptic contacts: %i (%0.2f per cell)' % (sim.totalSynapses, sim.synsPerCell)))
        if 'runTime' in sim.timingData:
            print(('  Spikes: %i (%0.2f Hz)' % (sim.totalSpikes, sim.firingRate)))
            if sim.cfg.printPopAvgRates and not sim.cfg.gatherOnlySimData:
                sim.allSimData['popRates'] = sim.popAvgRates()
            print(('  Simulated time: %0.1f s; %i workers' % (sim.cfg.duration/1e3, sim.nhosts)))
            print(('  Run time: %0.2f s' % (sim.timingData['runTime'])))

            sim.allSimData['avgRate'] = sim.firingRate  # save firing rate

        return sim.allSimData


###############################################################################
### Calculate and print avg pop rates
###############################################################################
def popAvgRates (trange = None, show = True):
    from . import sim

    if not hasattr(sim, 'allSimData') or 'spkt' not in sim.allSimData:
        print('Error: sim.allSimData not available; please call sim.gatherData()')
        return None

    spkts = sim.allSimData['spkt']
    spkids = sim.allSimData['spkid']

    if not trange:
        trange = [0, sim.cfg.duration]
    else:
        spkids,spkts = list(zip(*[(spkid,spkt) for spkid,spkt in zip(spkids,spkts) if trange[0] <= spkt <= trange[1]]))

    avgRates = Dict()
    for pop in sim.net.allPops:
        numCells = float(len(sim.net.allPops[pop]['cellGids']))
        if numCells > 0:
            tsecs = float((trange[1]-trange[0]))/1000.0
            avgRates[pop] = len([spkid for spkid in spkids if sim.net.allCells[int(spkid)]['tags']['pop']==pop])/numCells/tsecs
            print('   %s : %.3f Hz'%(pop, avgRates[pop]))

    return avgRates


###############################################################################
### Calculate and print load balance
###############################################################################
def loadBalance ():
    from . import sim

    computation_time = sim.pc.step_time()
    max_comp_time = sim.pc.allreduce(computation_time, 2)
    min_comp_time = sim.pc.allreduce(computation_time, 3)
    avg_comp_time = sim.pc.allreduce(computation_time, 1)/sim.nhosts
    load_balance = avg_comp_time/max_comp_time

    print('node:',sim.rank,' comp_time:',computation_time)
    if sim.rank==0:
        print('max_comp_time:', max_comp_time)
        print('min_comp_time:', min_comp_time)
        print('avg_comp_time:', avg_comp_time)
        print('load_balance:',load_balance)
        print('\nspike exchange time (run_time-comp_time): ', sim.timingData['runTime'] - max_comp_time)

    return [max_comp_time, min_comp_time, avg_comp_time, load_balance]


###############################################################################
### Gather data from nodes
###############################################################################
def _gatherCells ():
    from . import sim

    ## Pack data from all hosts
    if sim.rank==0:
        print('\nUpdating sim.net.allCells...')

    if sim.nhosts > 1:  # only gather if >1 nodes
        nodeData = {'netCells': [c.__getstate__() for c in sim.net.cells]}
        data = [None]*sim.nhosts
        data[0] = {}
        for k,v in nodeData.items():
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
### Save distributed data using HDF5 (only conns for now)
###############################################################################
def distributedSaveHDF5():
    from . import sim
    import h5py

    if sim.rank == 0: timing('start', 'saveTimeHDF5')

    sim.compactConnFormat()
    conns = [[cell.gid]+conn for cell in sim.net.cells for conn in cell.conns]
    conns = sim.copyReplaceItemObj(conns, keystart='h', newval=[]) 
    connFormat = ['postGid']+sim.cfg.compactConnFormat
    with h5py.File(sim.cfg.filename+'.h5', 'w') as hf:
        hf.create_dataset('conns', data = conns)
        hf.create_dataset('connsFormat', data = connFormat)

    if sim.rank == 0: timing('stop', 'saveTimeHDF5')

###############################################################################
### load HDF5 (conns for now)
###############################################################################
def loadHDF5(filename):
    from . import sim
    import h5py

    if sim.rank == 0: timing('start', 'loadTimeHDF5')

    connsh5 = h5py.File(filename, 'r')
    conns = [list(x) for x in connsh5['conns']]
    connsFormat = list(connsh5['connsFormat'])

    if sim.rank == 0: timing('stop', 'loadTimeHDF5')

    return conns, connsFormat


###############################################################################
### Save data
###############################################################################
def saveData (include = None):
    from . import sim

    if sim.rank == 0 and not getattr(sim.net, 'allCells', None): needGather = True
    else: needGather = False
    if needGather: gatherData()

    if sim.rank == 0:
        timing('start', 'saveTime')
        import os

        # copy source files
        if isinstance(sim.cfg.backupCfgFile, list) and len(sim.cfg.backupCfgFile) == 2:
            simName = sim.cfg.simLabel if sim.cfg.simLabel else os.path.basename(sim.cfg.filename)
            print(('Copying cfg file %s ... ' % simName))
            source = sim.cfg.backupCfgFile[0]
            targetFolder = sim.cfg.backupCfgFile[1]
            # make dir
            try:
                os.mkdir(targetFolder)
            except OSError:
                if not os.path.exists(targetFolder):
                    print(' Could not create target folder: %s' % (targetFolder))
            # copy file
            targetFile = targetFolder + '/' + simName + '_cfg.py'
            if os.path.exists(targetFile):
                print(' Removing prior cfg file' , targetFile)
                os.system('rm ' + targetFile)
            os.system('cp ' + source + ' ' + targetFile)


        # create folder if missing
        targetFolder = os.path.dirname(sim.cfg.filename)
        if targetFolder and not os.path.exists(targetFolder):
            try:
                os.mkdir(targetFolder)
            except OSError:
                print(' Could not create target folder: %s' % (targetFolder))

        # saving data
        if not include: include = sim.cfg.saveDataInclude
        dataSave = {}
        net = {}

        dataSave['netpyne_version'] = sim.version(show=False)
        dataSave['netpyne_changeset'] = sim.gitChangeset(show=False)
        
        if getattr(sim.net.params, 'version', None): dataSave['netParams_version'] = sim.net.params.version
        if 'netParams' in include: net['params'] = replaceFuncObj(sim.net.params.__dict__)
        if 'net' in include: include.extend(['netPops', 'netCells'])
        if 'netCells' in include: net['cells'] = sim.net.allCells
        if 'netPops' in include: net['pops'] = sim.net.allPops
        if net: dataSave['net'] = net
        if 'simConfig' in include: dataSave['simConfig'] = sim.cfg.__dict__
        if 'simData' in include: 
            if 'LFP' in sim.allSimData: 
                sim.allSimData['LFP'] = sim.allSimData['LFP'].tolist() 
            dataSave['simData'] = sim.allSimData


        if dataSave:
            if sim.cfg.timestampFilename:
                timestamp = time()
                timestampStr = datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S')
                sim.cfg.filename = sim.cfg.filename+'-'+timestampStr

            # Save to pickle file
            if sim.cfg.savePickle:
                import pickle
                dataSave = replaceDictODict(dataSave)
                print(('Saving output as %s ... ' % (sim.cfg.filename+'.pkl')))
                with open(sim.cfg.filename+'.pkl', 'wb') as fileObj:
                    pickle.dump(dataSave, fileObj)
                print('Finished saving!')

            # Save to dpk file
            if sim.cfg.saveDpk:
                import gzip
                print(('Saving output as %s ... ' % (sim.cfg.filename+'.dpk')))
                fn=sim.cfg.filename #.split('.')
                gzip.open(fn, 'wb').write(pk.dumps(dataSave)) # write compressed string
                print('Finished saving!')

            # Save to json file
            if sim.cfg.saveJson:
                import json
                #dataSave = replaceDictODict(dataSave)  # not required since json saves as dict
                print(('Saving output as %s ... ' % (sim.cfg.filename+'.json ')))
                with open(sim.cfg.filename+'.json', 'w') as fileObj:
                    json.dump(dataSave, fileObj)
                print('Finished saving!')

            # Save to mat file
            if sim.cfg.saveMat:
                from scipy.io import savemat
                print(('Saving output as %s ... ' % (sim.cfg.filename+'.mat')))
                savemat(sim.cfg.filename+'.mat', tupleToList(replaceNoneObj(dataSave)))  # replace None and {} with [] so can save in .mat format
                print('Finished saving!')

            # Save to HDF5 file (uses very inefficient hdf5storage module which supports dicts)
            if sim.cfg.saveHDF5:
                dataSaveUTF8 = _dict2utf8(replaceNoneObj(dataSave)) # replace None and {} with [], and convert to utf
                import hdf5storage
                print(('Saving output as %s... ' % (sim.cfg.filename+'.hdf5')))
                hdf5storage.writes(dataSaveUTF8, filename=sim.cfg.filename+'.hdf5')
                print('Finished saving!')

            # Save to CSV file (currently only saves spikes)
            if sim.cfg.saveCSV:
                if 'simData' in dataSave:
                    import csv
                    print(('Saving output as %s ... ' % (sim.cfg.filename+'.csv')))
                    writer = csv.writer(open(sim.cfg.filename+'.csv', 'wb'))
                    for dic in dataSave['simData']:
                        for values in dic:
                            writer.writerow(values)
                    print('Finished saving!')

            # Save to Dat file(s)
            if sim.cfg.saveDat:
                traces = sim.cfg.recordTraces
                for ref in list(traces.keys()):
                    for cellid in list(sim.allSimData[ref].keys()):
                        dat_file_name = '%s_%s.dat'%(ref,cellid)
                        dat_file = open(dat_file_name, 'w')
                        trace = sim.allSimData[ref][cellid]
                        print(("Saving %i points of data on: %s:%s to %s"%(len(trace),ref,cellid,dat_file_name)))
                        for i in range(len(trace)):
                            dat_file.write('%s\t%s\n'%((i*sim.cfg.dt/1000),trace[i]/1000))

                print('Finished saving!')

            # Save timing
            if sim.cfg.timing:
                timing('stop', 'saveTime')
                print(('  Done; saving time = %0.2f s.' % sim.timingData['saveTime']))
            if sim.cfg.timing and sim.cfg.saveTiming:
                import pickle
                with open('timing.pkl', 'wb') as file: pickle.dump(sim.timing, file)


            # clean to avoid mem leaks
            for key in list(dataSave.keys()):
                del dataSave[key]
            del dataSave

            # return full path
            import os
            return os.getcwd()+'/'+sim.cfg.filename

        else:
            print('Nothing to save')


###############################################################################
### Load cell tags and conns using ijson (faster!) 
###############################################################################
def ijsonLoad(filename, tagsGidRange=None, connsGidRange=None, loadTags=True, loadConns=True, tagFormat=None, connFormat=None, saveTags=None, saveConns=None):
    # requires: 1) pip install ijson, 2) brew install yajl
    from . import sim
    import ijson.backends.yajl2_cffi as ijson
    import json
    from time import time

    tags, conns = {}, {}

    if connFormat:
        conns['format'] = connFormat
    if tagFormat:
        tags['format'] = tagFormat

    with open(filename, 'r') as fd:
        start = time()
        print('Loading data ...')
        objs = ijson.items(fd, 'net.cells.item')
        if loadTags and loadConns:
            print('Storing tags and conns ...')
            for cell in objs:
                if tagsGidRange==None or cell['gid'] in tagsGidRange:
                    print('Cell gid: %d'%(cell['gid']))
                    if tagFormat:
                        tags[int(cell['gid'])] = [cell['tags'][param] for param in tagFormat]
                    else:
                        tags[int(cell['gid'])] = cell['tags']
                    if connsGidRange==None or cell['gid'] in connsGidRange:
                        if connFormat:
                            conns[int(cell['gid'])] = [[conn[param] for param in connFormat] for conn in cell['conns']]
                        else:
                            conns[int(cell['gid'])] = cell['conns']
        elif loadTags:
            print('Storing tags ...')
            if tagFormat:
                tags.update({int(cell['gid']): [cell['tags'][param] for param in tagFormat] for cell in objs if tagsGidRange==None or cell['gid'] in tagsGidRange})
            else:
                tags.update({int(cell['gid']): cell['tags'] for cell in objs if tagsGidRange==None or cell['gid'] in tagsGidRange})
        elif loadConns:             
            print('Storing conns...')
            if connFormat:
                conns.update({int(cell['gid']): [[conn[param] for param in connFormat] for conn in cell['conns']] for cell in objs if connsGidRange==None or cell['gid'] in connsGidRange})
            else:
                conns.update({int(cell['gid']): cell['conns'] for cell in objs if connsGidRange==None or cell['gid'] in connsGidRange})

        print('time ellapsed (s): ', time() - start)

    tags = sim.decimalToFloat(tags)
    conns = sim.decimalToFloat(conns)

    if saveTags and tags:
        outFilename = saveTags if isinstance(saveTags, str) else 'filename'[:-4]+'_tags.json'
        print('Saving tags to %s ...' % (outFilename))
        with open(outFilename, 'w') as fileObj: json.dump({'tags': tags}, fileObj) 
    if saveConns and conns:
        outFilename = saveConns if isinstance(saveConns, str) else 'filename'[:-4]+'_conns.json'
        print('Saving conns to %s ...' % (outFilename))
        with open(outFilename, 'w') as fileObj: json.dump({'conns': conns}, fileObj)

    return tags, conns


###############################################################################
### Convet connections in long dict format to compact list format 
###############################################################################
def compactConnFormat():
    from . import sim

    if type(sim.cfg.compactConnFormat) is not list:
        if len(sim.net.params.stimTargetParams) > 0:  # if have stims, then require preLabel field
            sim.cfg.compactConnFormat = ['preGid', 'preLabel', 'sec', 'loc', 'synMech', 'weight', 'delay']
        else:
            sim.cfg.compactConnFormat = ['preGid', 'sec', 'loc', 'synMech', 'weight', 'delay']
    

    connFormat = sim.cfg.compactConnFormat
    for cell in sim.net.cells:
        newConns = [[conn[param] for param in connFormat] for conn in cell.conns]
        del cell.conns
        cell.conns = newConns
 


###############################################################################
### Timing - Stop Watch
###############################################################################
def timing (mode, processName):
    from . import sim

    if sim.rank == 0 and sim.cfg.timing:
        if mode == 'start':
            sim.timingData[processName] = time()
        elif mode == 'stop':
            sim.timingData[processName] = time() - sim.timingData[processName]


###############################################################################
### Print netpyne version
###############################################################################
def version (show=True):
    from . import sim
    from netpyne import __version__
    if show:
        print(__version__)
    return __version__


###############################################################################
### Print github version
###############################################################################
def gitChangeset (show=True):
    from . import sim
    import netpyne, os, subprocess 
    
    currentPath = os.getcwd()
    try:
        netpynePath = os.path.dirname(netpyne.__file__)
        os.chdir(netpynePath)
        if show: os.system('git log -1')
        # get changeset (need to remove initial tag+num and ending '\n')
        changeset = subprocess.check_output(["git", "describe"]).split('-')[2][1:-1]
    except: 
        changeset = ''

    os.chdir(currentPath)

    return changeset

###############################################################################
### Print github version
###############################################################################
def checkMemory ():
    from . import sim
    
    # print memory diagnostic info
    if sim.rank == 0: # and checkMemory:
        import resource
        print('\nMEMORY -----------------------')
        print('Sections: ')
        print(h.topology())
        print('NetCons: ')
        print(len(h.List("NetCon")))
        print('NetStims:')
        print(len(h.List("NetStim")))
        print('\n Memory usage: %s \n' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        # import objgraph
        # objgraph.show_most_common_types()
        print('--------------------------------\n')
