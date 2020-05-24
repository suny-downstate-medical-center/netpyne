"""
sim/utils.py

Helper functions related to the simulation

Private methods: _mat2dict, _dict2utf8, decimalToFloat, tupleToList, replaceDictODict, replaceNoneObj


Contributors: salvadordura@gmail.com
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import



from builtins import next
from builtins import dict
from builtins import map
from builtins import str
try:
    basestring
except NameError:
    basestring = str
from future import standard_library
standard_library.install_aliases()
from time import time
import hashlib
import array
from numbers import Number
from collections import OrderedDict
from neuron import h# Import NEURON
from ..specs import Dict, ODict



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
def getCellsList (include, returnGids=False):
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
            cellsPop = [gid for gid,tags in allCellTags.items() if tags['pop']==condition[0]]
            cellsPop = list(set(cellsPop))
            cellsPop.sort()

            if isinstance(condition[1], list):
                cellGids.extend([gid for i,gid in enumerate(cellsPop) if i in condition[1]])
            elif isinstance(condition[1], int):
                cellGids.extend([gid for i,gid in enumerate(cellsPop) if i==condition[1]])

    cellGids = list(set(cellGids))  # unique values
    if returnGids:
        return cellGids
    else:
        cells = [cell for cell in sim.net.cells if cell.gid in cellGids]
        return cells


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
    from netpyne import __version__
    if show:
        print(__version__)
    return __version__


#------------------------------------------------------------------------------
# Print github version
#------------------------------------------------------------------------------
def gitChangeset (show=True):
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
# Hash function for string
#------------------------------------------------------------------------------
def hashStr (obj):
    #return hash(obj) & 0xffffffff  # hash func
    return int(hashlib.md5(obj.encode('utf-8')).hexdigest()[0:8],16)  # convert 8 first chars of md5 hash in base 16 to int


#------------------------------------------------------------------------------
# Hash function for list of values
#------------------------------------------------------------------------------
def hashList(obj):
    return int(hashlib.md5(array.array(chr(ord('L')), obj)).hexdigest()[0:8],16)


#------------------------------------------------------------------------------
# Initialize the stim randomizer
#------------------------------------------------------------------------------
def _init_stim_randomizer(rand, stimType, gid, seed):
    from .. import sim

    rand.Random123(sim.hashStr(stimType), gid, seed)


#------------------------------------------------------------------------------
# Fast function to find unique elements in sequence and preserve order
#------------------------------------------------------------------------------
def unique(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


#------------------------------------------------------------------------------
# Check memory 
#------------------------------------------------------------------------------
def checkMemory ():
    from .. import sim
    
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


#------------------------------------------------------------------------------
# Replace item with specific key from dict or list (used to remove h objects)
#------------------------------------------------------------------------------
def copyReplaceItemObj (obj, keystart, newval, objCopy='ROOT', exclude_list=[]):
    if type(obj) == list:
        if objCopy=='ROOT':
            objCopy = []
        for item in obj:
            if isinstance(item, list):
                objCopy.append([])
                copyReplaceItemObj(item, keystart, newval, objCopy[-1], exclude_list)
            elif isinstance(item, (dict, Dict)):
                objCopy.append({})
                copyReplaceItemObj(item, keystart, newval, objCopy[-1], exclude_list)
            else:
                objCopy.append(item)

    elif isinstance(obj, (dict, Dict)):
        if objCopy == 'ROOT':
            objCopy = Dict()
        for key,val in obj.items():
            if type(val) in [list]:
                objCopy[key] = []
                copyReplaceItemObj(val, keystart, newval, objCopy[key], exclude_list)
            elif isinstance(val, (dict, Dict)):
                objCopy[key] = {}
                copyReplaceItemObj(val, keystart, newval, objCopy[key], exclude_list)
            elif key.startswith(keystart) and key not in exclude_list:
                objCopy[key] = newval
            else:
                objCopy[key] = val
    return objCopy


#------------------------------------------------------------------------------
# Remove item with specific key from dict or list (used to remove h objects)
#------------------------------------------------------------------------------
def copyRemoveItemObj (obj, keystart,  objCopy='ROOT', exclude_list=[]):
    if type(obj) == list:
        if objCopy=='ROOT':
            objCopy = []
        for item in obj:
            if isinstance(item, list):
                objCopy.append([])
                copyRemoveItemObj(item, keystart, objCopy[-1], exclude_list)
            elif isinstance(item, (dict, Dict)):
                objCopy.append({})
                copyRemoveItemObj(item, keystart,  objCopy[-1], exclude_list)
            else:
                objCopy.append(item)

    elif isinstance(obj, (dict, Dict)):
        if objCopy == 'ROOT':
            objCopy = Dict()
        for key,val in obj.items():
            if type(val) in [list]:
                objCopy[key] = []
                copyRemoveItemObj(val, keystart, objCopy[key], exclude_list)
            elif isinstance(val, (dict, Dict)):
                objCopy[key] = {}
                copyRemoveItemObj(val, keystart, objCopy[key], exclude_list)
            elif key.startswith(keystart) and key not in exclude_list:
                objCopy.pop(key, None)
            else:
                objCopy[key] = val
    return objCopy


#------------------------------------------------------------------------------
# Replace item with specific key from dict or list (used to remove h objects)
#------------------------------------------------------------------------------
def replaceItemObj (obj, keystart, newval, exclude_list=[]):
    if type(obj) == list:
        for item in obj:
            if type(item) in [list, dict]:
                replaceItemObj(item, keystart, newval, exclude_list)

    elif type(obj) == dict:
        for key,val in obj.items():
            if type(val) in [list, dict]:
                replaceItemObj(val, keystart, newval, exclude_list)
            if key.startswith(keystart) and key not in exclude_list:
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
        for key in list(obj.keys()):
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
        for key,val in obj.items():
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
        for key,val in obj.items():
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
        for key,val in obj.items():
            if type(val) == Dict:
                obj[key] = val.todict()
            elif type(val) == ODict:
                obj[key] = val.toOrderedDict()
            if type(val) in [list, dict, OrderedDict]:
                replaceDictODict(val)

    return obj


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
        for key,val in obj.items():
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
        for key,val in obj.items():
            if isinstance(val, (list, dict)):
                decimalToFloat(val)
            elif type(val) == Decimal:
                obj[key] = float(val) # also replace empty dicts with empty list
    return obj


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
        for key in list(obj.keys()):
            val = obj[key]
            if isinstance(val, (list, dict, Dict, ODict)):
                clearObj(val)
            del obj[key]
    return obj


#------------------------------------------------------------------------------
# Support funcs to load from mat
#------------------------------------------------------------------------------
def _mat2dict(obj): 
    """
    A recursive function which constructs from matobjects nested dictionaries
    Enforce lists for conns, synMechs and stims even if 1 element (matlab converts to dict otherwise)
    """
    
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
# Convert dict strings to utf8 so can be saved in HDF5 format
#------------------------------------------------------------------------------
def _dict2utf8 (obj):
#unidict = {k.decode('utf8'): v.decode('utf8') for k, v in strdict.items()}
    #print obj
    import collections
    if isinstance(obj, basestring):
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


#------------------------------------------------------------------------------
# Clear all sim objects in memory
#------------------------------------------------------------------------------
def clearAll ():
    from .. import sim

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
    
#------------------------------------------------------------------------------
# Create a subclass of json.JSONEncoder to convert numpy types in Python types
#------------------------------------------------------------------------------
import json
import numpy as np

class NpSerializer(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpSerializer, self).default(obj)
