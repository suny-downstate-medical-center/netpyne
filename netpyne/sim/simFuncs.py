"""
simFunc.py
Contains functions related to the simulation (eg. setupRecording, runSim)
Contributors: salvadordura@gmail.com
"""






# load.py
__all__.extend([ 'loadSimCfg', 'loadNetParams', 'loadNet', 'loadSimData', 'loadAll', 'ijsonLoad', \
 'loadHDF5']) 

# utils.py
 'copyReplaceItemObj', 'copyRemoveItemObj', 
'replaceItemObj', 'replaceNoneObj', 'replaceFuncObj', 'replaceDictODict', 
'timing',  'version', 'gitChangeset'
 'decimalToFloat', 'unique', 'rename',
 'clearAll', 'clearObj'

 'id32',
'_init_stim_randomizer', 
'cellByGid',
'getCellsList',



#------------------------------------------------------------------------------
# Load netParams from cell
#------------------------------------------------------------------------------
def loadNetParams (filename, data=None, setLoaded=True):
    if not data: data = _loadFile(filename)
    print('Loading netParams...')
    if 'net' in data and 'params' in data['net']:
        if setLoaded:
            setNetParams(data['net']['params'])
        else:
            return specs.NetParams(data['net']['params'])
    else:
        print('netParams not found in file %s'%(filename))

    pass


#------------------------------------------------------------------------------
# Convert compact (list-based) to long (dict-based) conn format
#------------------------------------------------------------------------------
def compactToLongConnFormat(cells, connFormat):
    
    formatIndices = {key: connFormat.index(key) for key in connFormat}
    try:
        for cell in cells:
            for iconn, conn in enumerate(cell['conns']):
                cell['conns'][iconn] = {key: conn[index] for key,index in formatIndices.iteritems()}
        return cells
    except:
        print("Error converting conns from compact to long format")
        return cells


#------------------------------------------------------------------------------
# Load cells and pops from file and create NEURON objs
#------------------------------------------------------------------------------
def loadNet (filename, data=None, instantiate=True, compactConnFormat=False):
    from .. import sim

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
                cellsNode = [data['net']['cells'][i] for i in xrange(int(sim.rank), len(data['net']['cells']), sim.nhosts) if i in instantiate]
            else:
                cellsNode = [data['net']['cells'][i] for i in xrange(int(sim.rank), len(data['net']['cells']), sim.nhosts)]
            if sim.cfg.createPyStruct:
                for popLoadLabel, popLoad in data['net']['pops'].iteritems():
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
                    sim.pc.barrier()
                    for cell in sim.net.cells:
                        try:
                            cell.addStimsNEURONObj()  # add stims first so can then create conns between netstims
                            cell.addConnsNEURONObj()
                        except:
                            if sim.cfg.verbose: ' Unable to load instantiate cell conns or stims'

                    print('  Added NEURON objects to %d cells' % (len(sim.net.cells)))

            if sim.rank == 0 and sim.cfg.timing:
                sim.timing('stop', 'loadNetTime')
                print('  Done; re-instantiate net time = %0.2f s' % sim.timingData['loadNetTime'])
    else:
        print('  netCells and/or netPops not found in file %s'%(filename))


#------------------------------------------------------------------------------
# Load simulation config from file
#------------------------------------------------------------------------------
def loadSimCfg (filename, data=None, setLoaded=True):
    if not data: data = _loadFile(filename)
    print('Loading simConfig...')
    if 'simConfig' in data:
        if setLoaded:
            setSimCfg(data['simConfig'])
        else:
            return specs.SimConfig(data['simConfig'])
    else:
        print('  simConfig not found in file %s'%(filename))
    pass


#------------------------------------------------------------------------------
# Load netParams from cell
#------------------------------------------------------------------------------
def loadSimData (filename, data=None):
    from .. import sim

    if not data: data = _loadFile(filename)
    print('Loading simData...')
    if 'simData' in data:
        sim.allSimData = data['simData']
    else:
        print('  simData not found in file %s'%(filename))

    pass


#------------------------------------------------------------------------------
# Load all data in file
#------------------------------------------------------------------------------
def loadAll (filename, data=None, instantiate=True, createNEURONObj=True):
    from .. import sim 

    if not data: data = _loadFile(filename)
    loadSimCfg(filename, data=data)
    sim.cfg.createNEURONObj = createNEURONObj  # set based on argument
    loadNetParams(filename, data=data)
    if hasattr(sim.cfg, 'compactConnFormat'): 
        connFormat = sim.cfg.compactConnFormat
    else:
        print 'Error: no connFormat provided in simConfig'
        sys.exit()
    loadNet(filename, data=data, instantiate=instantiate, compactConnFormat=connFormat)
    loadSimData(filename, data=data)


#------------------------------------------------------------------------------
# Fast function to find unique elements in sequence and preserve order
#------------------------------------------------------------------------------
def unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


#------------------------------------------------------------------------------
# Support funcs to load from mat
#------------------------------------------------------------------------------
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


#------------------------------------------------------------------------------
# Load data from file
#------------------------------------------------------------------------------
def _loadFile (filename):
    from .. import sim
    import os

    def _byteify(data, ignore_dicts = False):
        # if this is a unicode string, return its string representation
        if isinstance(data, unicode):
            return data.encode('utf-8')
        # if this is a list of values, return list of byteified values
        if isinstance(data, list):
            return [ _byteify(item, ignore_dicts=True) for item in data ]
        # if this is a dictionary, return dictionary of byteified keys and values
        # but only if we haven't already byteified it
        if isinstance(data, dict) and not ignore_dicts:
            return OrderedDict({
                _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
                for key, value in data.iteritems()
            })
        # if it's anything else, return it in its original form
        return data

    if hasattr(sim, 'cfg') and sim.cfg.timing: sim.timing('start', 'loadFileTime')
    ext = os.path.basename(filename).split('.')[1]

    # load pickle file
    if ext == 'pkl':
        import pickle
        print('Loading file %s ... ' % (filename))
        with open(filename, 'rb') as fileObj:
            if sys.version_info[0] == 2:
                data = pickle.load(fileObj)
            else:
                data = pickle.load(fileObj, encoding='latin1')

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
            data = json.load(fileObj, object_hook=_byteify)

    # load mat file
    elif ext == 'mat':
        from scipy.io import loadmat
        print('Loading file %s ... ' % (filename))
        dataraw = loadmat(filename, struct_as_record=False, squeeze_me=True)
        data = _mat2dict(dataraw)
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

    if hasattr(sim, 'rank') and sim.rank == 0 and hasattr(sim, 'cfg') and sim.cfg.timing:
        sim.timing('stop', 'loadFileTime')
        print('  Done; file loading time = %0.2f s' % sim.timingData['loadFileTime'])


    return data

#------------------------------------------------------------------------------
# Clear all sim objects in memory
#------------------------------------------------------------------------------
def clearAll ():
    from .. import sim

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
        matplotlib.pyplot.close('all')

    del sim.net

    import gc; gc.collect()



#------------------------------------------------------------------------------
# Hash function to obtain random value
#------------------------------------------------------------------------------
def id32 (obj):
    #return hash(obj) & 0xffffffff  # hash func
    return int(hashlib.md5(obj.encode('utf-8')).hexdigest()[0:8],16)  # convert 8 first chars of md5 hash in base 16 to int


#------------------------------------------------------------------------------
# Initialize the stim randomizer
#------------------------------------------------------------------------------
def _init_stim_randomizer(rand, stimType, gid, seed):
    from .. import sim

    rand.Random123(sim.id32(stimType), gid, seed)


#------------------------------------------------------------------------------
# Replace item with specific key from dict or list (used to remove h objects)
#------------------------------------------------------------------------------
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
        for key,val in obj.iteritems():
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


#------------------------------------------------------------------------------
# Remove item with specific key from dict or list (used to remove h objects)
#------------------------------------------------------------------------------
def copyRemoveItemObj (obj, keystart,  objCopy='ROOT'):
    if type(obj) == list:
        if objCopy=='ROOT':
            objCopy = []
        for item in obj:
            if isinstance(item, list):
                objCopy.append([])
                copyRemoveItemObj(item, keystart, objCopy[-1])
            elif isinstance(item, (dict, Dict)):
                objCopy.append({})
                copyRemoveItemObj(item, keystart,  objCopy[-1])
            else:
                objCopy.append(item)

    elif isinstance(obj, (dict, Dict)):
        if objCopy == 'ROOT':
            objCopy = Dict()
        for key,val in obj.iteritems():
            if type(val) in [list]:
                objCopy[key] = []
                copyRemoveItemObj(val, keystart, objCopy[key])
            elif isinstance(val, (dict, Dict)):
                objCopy[key] = {}
                copyRemoveItemObj(val, keystart, objCopy[key])
            elif key.startswith(keystart):
                objCopy.pop(key, None)
            else:
                objCopy[key] = val
    return objCopy


#------------------------------------------------------------------------------
# Rename objects
#------------------------------------------------------------------------------
def rename (obj, old, new, label=None):
    try:
        return obj.rename(old, new, label)
    except:
        if type(obj) == dict and old in obj:
            obj[new] = obj.pop(old)  # replace
            return True
        else:
            return False



#------------------------------------------------------------------------------
# Recursively remove items of an object (used to avoid mem leaks)
#------------------------------------------------------------------------------
def clearObj (obj):
    if type(obj) == list:
        for item in obj:
            if isinstance(item, (list, dict, Dict, ODict)):
                clearObj(item)
            del item

    elif isinstance(obj, (dict, Dict, ODict)):
        for key in obj.keys():
            val = obj[key]
            if isinstance(item, (dict, Dict))(val, (list, dict, Dict, ODict)):
                clearObj(val)
            del obj[key]
    return obj

#------------------------------------------------------------------------------
# Replace item with specific key from dict or list (used to remove h objects)
#------------------------------------------------------------------------------
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


#------------------------------------------------------------------------------
# Recursivele replace dict keys
#------------------------------------------------------------------------------
def replaceKeys (obj, oldkey, newkey):
    if type(obj) == list:
        for item in obj:
            if isinstance(item, (list, dict, Dict, ODict, OrderedDict)):
                replaceKeys(item, oldkey, newkey)

    elif isinstance(obj, (dict, Dict, ODict, OrderedDict)):
        for key in obj.keys():
            val = obj[key]
            if isinstance(val, (list, dict, Dict, ODict, OrderedDict)):
                replaceKeys(val, oldkey, newkey)
            if key == oldkey:
                obj[newkey] = obj.pop(oldkey)
    return obj


#------------------------------------------------------------------------------
# Replace functions from dict or list with function string (so can be pickled)
#------------------------------------------------------------------------------
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


#------------------------------------------------------------------------------
# Replace None from dict or list with [](so can be saved to .mat)
#------------------------------------------------------------------------------
def replaceNoneObj (obj):
    if type(obj) == list:# or type(obj) == tuple:
        for item in obj:
            if isinstance(item, (list, dict, Dict, ODict)):
                replaceNoneObj(item)

    elif isinstance(obj, (dict, Dict, ODict)):
        for key,val in obj.iteritems():
            if isinstance(val, (list, dict, Dict, ODict)):
                replaceNoneObj(val)
            if val == None:
                obj[key] = []
            elif val == {}:
                obj[key] = [] # also replace empty dicts with empty list
    return obj


#------------------------------------------------------------------------------
# Replace Dict with dict and Odict with OrderedDict
#------------------------------------------------------------------------------
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

    return obj

#------------------------------------------------------------------------------
# Replace tuples with str
#------------------------------------------------------------------------------
def tupleToList (obj):
    if type(obj) == list:
        for item in obj:
            if type(item) in [list, dict]:
                tupleToList(item)
            elif type(item) == tuple:
                obj[obj.index(item)] = list(item)

    elif isinstance(obj, (dict, ODict)):
        for key,val in obj.iteritems():
            if isinstance(val, (list, dict, ODict)):
                tupleToList(val)
            elif type(val) == tuple:
                obj[key] = list(val) # also replace empty dicts with empty list
    return obj


#------------------------------------------------------------------------------
# Replace Decimal with float
#------------------------------------------------------------------------------
def decimalToFloat (obj):
    from decimal import Decimal
    if type(obj) == list:
        for i,item in enumerate(obj):
            if type(item) in [list, dict, tuple]:
                decimalToFloat(item)
            elif type(item) == Decimal:
                obj[i] = float(item)

    elif isinstance(obj, dict):
        for key,val in obj.iteritems():
            if isinstance(val, (list, dict)):
                decimalToFloat(val)
            elif type(val) == Decimal:
                obj[key] = float(val) # also replace empty dicts with empty list
    return obj


#------------------------------------------------------------------------------
# Convert dict strings to utf8 so can be saved in HDF5 format
#------------------------------------------------------------------------------
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


#------------------------------------------------------------------------------
# Convert dict strings to utf8 so can be saved in HDF5 format
#------------------------------------------------------------------------------
def cellByGid (gid):
    from .. import sim

    cell = next((c for c in sim.net.cells if c.gid==gid), None)
    return cell





#------------------------------------------------------------------------------
# Get cells list for recording based on set of conditions
#------------------------------------------------------------------------------
def getCellsList (include):
    from .. import sim

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

        elif isinstance(condition, basestring):  # entire pop
            cellGids.extend(list(sim.net.pops[condition].cellGids))

        elif isinstance(condition, tuple) or isinstance(condition, list):  # subset of a pop with relative indices
            cellsPop = [gid for gid,tags in allCellTags.iteritems() if tags['pop']==condition[0]]

            if isinstance(condition[1], list):
                cellGids.extend([gid for i,gid in enumerate(cellsPop) if i in condition[1]])
            elif isinstance(condition[1], int):
                cellGids.extend([gid for i,gid in enumerate(cellsPop) if i==condition[1]])

    cellGids = list(set(cellGids))  # unique values
    cells = [cell for cell in sim.net.cells if cell.gid in cellGids]
    return cells





#------------------------------------------------------------------------------
# load HDF5 (conns for now)
#------------------------------------------------------------------------------
def loadHDF5(filename):
    from .. import sim
    import h5py

    if sim.rank == 0: timing('start', 'loadTimeHDF5')

    connsh5 = h5py.File(filename, 'r')
    conns = [list(x) for x in connsh5['conns']]
    connsFormat = list(connsh5['connsFormat'])

    if sim.rank == 0: timing('stop', 'loadTimeHDF5')

    return conns, connsFormat



#------------------------------------------------------------------------------
# Load cell tags and conns using ijson (faster!) 
#------------------------------------------------------------------------------
def ijsonLoad(filename, tagsGidRange=None, connsGidRange=None, loadTags=True, loadConns=True, tagFormat=None, connFormat=None, saveTags=None, saveConns=None):
    # requires: 1) pip install ijson, 2) brew install yajl
    from .. import sim
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
        print 'Loading data ...'
        objs = ijson.items(fd, 'net.cells.item')
        if loadTags and loadConns:
            print 'Storing tags and conns ...'
            for cell in objs:
                if tagsGidRange==None or cell['gid'] in tagsGidRange:
                    print 'Cell gid: %d'%(cell['gid'])
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
            print 'Storing tags ...'
            if tagFormat:
                tags.update({int(cell['gid']): [cell['tags'][param] for param in tagFormat] for cell in objs if tagsGidRange==None or cell['gid'] in tagsGidRange})
            else:
                tags.update({int(cell['gid']): cell['tags'] for cell in objs if tagsGidRange==None or cell['gid'] in tagsGidRange})
        elif loadConns:             
            print 'Storing conns...'
            if connFormat:
                conns.update({int(cell['gid']): [[conn[param] for param in connFormat] for conn in cell['conns']] for cell in objs if connsGidRange==None or cell['gid'] in connsGidRange})
            else:
                conns.update({int(cell['gid']): cell['conns'] for cell in objs if connsGidRange==None or cell['gid'] in connsGidRange})

        print 'time ellapsed (s): ', time() - start

    tags = sim.decimalToFloat(tags)
    conns = sim.decimalToFloat(conns)

    if saveTags and tags:
        outFilename = saveTags if isinstance(saveTags, str) else 'filename'[:-4]+'_tags.json'
        print 'Saving tags to %s ...' % (outFilename)
        with open(outFilename, 'w') as fileObj: json.dump({'tags': tags}, fileObj) 
    if saveConns and conns:
        outFilename = saveConns if isinstance(saveConns, str) else 'filename'[:-4]+'_conns.json'
        print 'Saving conns to %s ...' % (outFilename)
        with open(outFilename, 'w') as fileObj: json.dump({'conns': conns}, fileObj)

    return tags, conns





#------------------------------------------------------------------------------
# Timing - Stop Watch
#------------------------------------------------------------------------------
def timing (mode, processName):
    from .. import sim

    if sim.rank == 0 and sim.cfg.timing:
        if mode == 'start':
            sim.timingData[processName] = time()
        elif mode == 'stop':
            sim.timingData[processName] = time() - sim.timingData[processName]


#------------------------------------------------------------------------------
# Print netpyne version
#------------------------------------------------------------------------------
def version (show=True):
    from .. import sim
    from netpyne import __version__
    if show:
        print(__version__)
    return __version__


#------------------------------------------------------------------------------
# Print github version
#------------------------------------------------------------------------------
def gitChangeset (show=True):
    from .. import sim
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

#------------------------------------------------------------------------------
# Print github version
#------------------------------------------------------------------------------
def checkMemory ():
    from .. import sim
    
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
