"""
Module for utilities related to simulation

"""

from netpyne.support.recxelectrode import RecXElectrode

try:
    basestring
except NameError:
    basestring = str

from time import time
import hashlib
import array
import sys
from numbers import Number
from collections import OrderedDict
from neuron import h  # Import NEURON
from ..specs import Dict, ODict

# ------------------------------------------------------------------------------
# Load python module
# ------------------------------------------------------------------------------
def loadPythonModule(path):
    import importlib, types, os

    loader = importlib.machinery.SourceFileLoader(os.path.basename(path).split('.')[0], path)
    module = types.ModuleType(loader.name)
    loader.exec_module(module)
    return module


# ------------------------------------------------------------------------------
# Convert dict strings to utf8 so can be saved in HDF5 format
# ------------------------------------------------------------------------------
def cellByGid(gid):
    """
    Function for/to <short description of `netpyne.sim.utils.cellByGid`>

    Parameters
    ----------
    gid : <type>
        <Short description of gid>
        **Default:** *required*


    """

    from .. import sim

    cell = next((c for c in sim.net.cells if c.gid == gid), None)
    return cell


# ------------------------------------------------------------------------------
# Get cells list for recording based on set of conditions
# ------------------------------------------------------------------------------
def getCellsList(include, returnGids=False):
    """
    Function for/to <short description of `netpyne.sim.utils.getCellsList`>

    Parameters
    ----------
    include : <type>
        <Short description of include>
        **Default:** *required*

    returnGids : bool
        <Short description of returnGids>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>


    """

    from .. import sim

    if sim.nhosts > 1 and any(
        isinstance(cond, tuple) or isinstance(cond, list) for cond in include
    ):  # Gather tags from all cells
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
            cellsPop = [gid for gid, tags in allCellTags.items() if tags['pop'] == condition[0]]
            cellsPop = list(set(cellsPop))
            cellsPop.sort()

            if isinstance(condition[1], list):
                cellGids.extend([gid for i, gid in enumerate(cellsPop) if i in condition[1]])
            elif isinstance(condition[1], int):
                cellGids.extend([gid for i, gid in enumerate(cellsPop) if i == condition[1]])

    cellGids = list(set(cellGids))  # unique values
    if returnGids:
        return cellGids
    else:
        cells = [cell for cell in sim.net.cells if cell.gid in cellGids]
        return cells


# ------------------------------------------------------------------------------
# Timing - Stop Watch
# ------------------------------------------------------------------------------
def timing(mode, processName):
    """
    Function for/to <short description of `netpyne.sim.utils.timing`>

    Parameters
    ----------
    mode : <type>
        <Short description of mode>
        **Default:** *required*

    processName : <type>
        <Short description of processName>
        **Default:** *required*


    """

    from .. import sim

    if not hasattr(sim, 'timingData'):
        sim.timingData = {}

    if hasattr(sim.cfg, 'timing'):
        if sim.cfg.timing:
            if hasattr(sim, 'rank'):
                if sim.rank == 0:
                    if mode == 'start':
                        sim.timingData[processName] = time()
                    elif mode == 'stop' and processName in sim.timingData:
                        sim.timingData[processName] = time() - sim.timingData[processName]
            else:
                if mode == 'start':
                    sim.timingData[processName] = time()
                elif mode == 'stop' and processName in sim.timingData:
                    sim.timingData[processName] = time() - sim.timingData[processName]


# ------------------------------------------------------------------------------
# Print netpyne version
# ------------------------------------------------------------------------------
def version(show=True):
    """
    Function for/to <short description of `netpyne.sim.utils.version`>

    Parameters
    ----------
    show : bool
        <Short description of show>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>


    """

    from netpyne import __version__

    if show:
        print(__version__)
    return __version__


# ------------------------------------------------------------------------------
# Print github version
# ------------------------------------------------------------------------------
def gitChangeset(show=True):
    """
    Function for/to <short description of `netpyne.sim.utils.gitChangeset`>

    Parameters
    ----------
    show : bool
        <Short description of show>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>


    """

    import netpyne, os, subprocess

    currentPath = os.getcwd()
    try:
        netpynePath = os.path.dirname(netpyne.__file__)
        os.chdir(netpynePath)
        if show:
            os.system('git log -1')
        # get changeset (need to remove initial tag+num and ending '\n')
        # changeset = subprocess.check_output(["git", "describe"]).split('-')[2][1:-1]
        changeset = subprocess.check_output(["git", "describe"], stderr=subprocess.DEVNULL).split('-')[2][1:-1]
    except:
        changeset = ''

    os.chdir(currentPath)

    return changeset


# ------------------------------------------------------------------------------
# Print git info: branch, source_dir, version
# ------------------------------------------------------------------------------
def gitInfo(show=True):
    """
    Function for/to <short description of `netpyne.sim.utils.gitInfo`>

    Parameters
    ----------
    show : bool
        <Short description of show>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    """
    import netpyne, os, subprocess

    loc = os.path.dirname(netpyne.__file__)
    vers, branch = (
        subprocess.check_output(['git', '-C', loc, 'rev-parse', 'HEAD', '--abbrev-ref', 'HEAD'])
        .decode('utf-8')
        .split()
    )
    orig = subprocess.check_output(['git', '-C', loc, 'remote', 'get-url', 'origin']).decode('utf-8').strip()
    if show:
        print(f'NetPyNE branch "{branch}" from {loc} (version:{vers[:8]} origin:{orig})')
    else:
        return [branch, loc, vers, orig]


# ------------------------------------------------------------------------------
# Hash function for string
# ------------------------------------------------------------------------------
def hashStr(obj):
    """
    Function for/to <short description of `netpyne.sim.utils.hashStr`>

    Parameters
    ----------
    obj : <type>
        <Short description of obj>
        **Default:** *required*


    """

    # return hash(obj) & 0xffffffff  # hash func
    return int(
        hashlib.md5(obj.encode('utf-8')).hexdigest()[0:8], 16
    )  # convert 8 first chars of md5 hash in base 16 to int


# ------------------------------------------------------------------------------
# Hash function for list of values
# ------------------------------------------------------------------------------
def hashList(obj):
    """
    Function for/to <short description of `netpyne.sim.utils.hashList`>

    Parameters
    ----------
    obj : <type>
        <Short description of obj>
        **Default:** *required*


    """

    return int(hashlib.md5(array.array(chr(ord('L')), obj)).hexdigest()[0:8], 16)


# ------------------------------------------------------------------------------
# Hash function for file (md5 hex)
# ------------------------------------------------------------------------------
def fileDigest(file):
    fileStr = open(file,'rb').read()
    return hashlib.md5(fileStr).hexdigest()


# ------------------------------------------------------------------------------
# Initialize the stim randomizer
# ------------------------------------------------------------------------------
def _init_stim_randomizer(rand, stimType, gid, seed):
    from .. import sim

    rand.Random123(sim.hashStr(stimType), gid, seed)


# ------------------------------------------------------------------------------
# Fast function to find unique elements in sequence and preserve order
# ------------------------------------------------------------------------------
def unique(seq):
    """
    Function for/to <short description of `netpyne.sim.utils.unique`>

    Parameters
    ----------
    seq : <type>
        <Short description of seq>
        **Default:** *required*


    """

    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


# ------------------------------------------------------------------------------
# Check memory
# ------------------------------------------------------------------------------
def checkMemory():
    """
    Function for/to <short description of `netpyne.sim.utils.checkMemory`>


    """

    from .. import sim

    # print memory diagnostic info
    if sim.rank == 0:  # and checkMemory:
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


# ------------------------------------------------------------------------------
# Replace item with specific key from dict or list (used to remove h objects)
# ------------------------------------------------------------------------------
def copyReplaceItemObj(obj, keystart, newval, objCopy='ROOT', exclude_list=[]):
    """
    Function for/to <short description of `netpyne.sim.utils.copyReplaceItemObj`>

    Parameters
    ----------
    obj : <type>
        <Short description of obj>
        **Default:** *required*

    keystart : <type>
        <Short description of keystart>
        **Default:** *required*

    newval : <type>
        <Short description of newval>
        **Default:** *required*

    objCopy : str
        <Short description of objCopy>
        **Default:** ``'ROOT'``
        **Options:** ``<option>`` <description of option>

    exclude_list : list
        <Short description of exclude_list>
        **Default:** ``[]``
        **Options:** ``<option>`` <description of option>


    """

    if type(obj) == list:
        if objCopy == 'ROOT':
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
        for key, val in obj.items():
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


# ------------------------------------------------------------------------------
# Remove item with specific key from dict or list (used to remove h objects)
# ------------------------------------------------------------------------------
def copyRemoveItemObj(obj, keystart, objCopy='ROOT', exclude_list=[]):
    """
    Function for/to <short description of `netpyne.sim.utils.copyRemoveItemObj`>

    Parameters
    ----------
    obj : <type>
        <Short description of obj>
        **Default:** *required*

    keystart : <type>
        <Short description of keystart>
        **Default:** *required*

    objCopy : str
        <Short description of objCopy>
        **Default:** ``'ROOT'``
        **Options:** ``<option>`` <description of option>

    exclude_list : list
        <Short description of exclude_list>
        **Default:** ``[]``
        **Options:** ``<option>`` <description of option>


    """

    if type(obj) == list:
        if objCopy == 'ROOT':
            objCopy = []
        for item in obj:
            if isinstance(item, list):
                objCopy.append([])
                copyRemoveItemObj(item, keystart, objCopy[-1], exclude_list)
            elif isinstance(item, (dict, Dict)):
                objCopy.append({})
                copyRemoveItemObj(item, keystart, objCopy[-1], exclude_list)
            else:
                objCopy.append(item)

    elif isinstance(obj, (dict, Dict)):
        if objCopy == 'ROOT':
            objCopy = Dict()
        for key, val in obj.items():
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


# ------------------------------------------------------------------------------
# Replace item with specific key from dict or list (used to remove h objects)
# ------------------------------------------------------------------------------
def replaceItemObj(obj, keystart, newval, exclude_list=[]):
    """
    Function for/to <short description of `netpyne.sim.utils.replaceItemObj`>

    Parameters
    ----------
    obj : <type>
        <Short description of obj>
        **Default:** *required*

    keystart : <type>
        <Short description of keystart>
        **Default:** *required*

    newval : <type>
        <Short description of newval>
        **Default:** *required*

    exclude_list : list
        <Short description of exclude_list>
        **Default:** ``[]``
        **Options:** ``<option>`` <description of option>


    """

    if type(obj) == list:
        for item in obj:
            if type(item) in [list, dict]:
                replaceItemObj(item, keystart, newval, exclude_list)

    elif type(obj) == dict:
        for key, val in obj.items():
            if type(val) in [list, dict]:
                replaceItemObj(val, keystart, newval, exclude_list)
            if key.startswith(keystart) and key not in exclude_list:
                obj[key] = newval
    return obj


# ------------------------------------------------------------------------------
# Recursivele replace dict keys
# ------------------------------------------------------------------------------
def replaceKeys(obj, oldkey, newkey):
    """
    Function for/to <short description of `netpyne.sim.utils.replaceKeys`>

    Parameters
    ----------
    obj : <type>
        <Short description of obj>
        **Default:** *required*

    oldkey : <type>
        <Short description of oldkey>
        **Default:** *required*

    newkey : <type>
        <Short description of newkey>
        **Default:** *required*


    """

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


# ------------------------------------------------------------------------------
# Replace functions from dict or list with function string (so can be pickled)
# ------------------------------------------------------------------------------
def replaceFuncObj(obj):
    """
    Function for/to <short description of `netpyne.sim.utils.replaceFuncObj`>

    Parameters
    ----------
    obj : <type>
        <Short description of obj>
        **Default:** *required*


    """

    if type(obj) == list:
        for item in obj:
            if type(item) in [list, dict]:
                replaceFuncObj(item)

    elif type(obj) == dict:
        for key, val in obj.items():
            if type(val) in [list, dict]:
                replaceFuncObj(val)
            if 'func_name' in dir(val):  # hasattr(val,'func_name'):  # avoid hasattr() since it creates key in Dicts()
                obj[key] = 'func'  # funcSource
    return obj


#------------------------------------------------------------------------------
# Replace Dict with dict and Odict with OrderedDict
# ------------------------------------------------------------------------------
def replaceDictODict(obj):
    """
    Function for/to <short description of `netpyne.sim.utils.replaceDictODict`>

    Parameters
    ----------
    obj : <type>
        <Short description of obj>
        **Default:** *required*


    """

    if type(obj) in [list, tuple]:
        new = []
        for ind, item in enumerate(obj):
            if type(item) == Dict:
                item = item.todict()
            elif type(item) == ODict:
                item = item.toOrderedDict()
            else:
                item = replaceDictODict(item)

            new.append(item)

    elif type(obj) in [dict, OrderedDict, Dict, ODict]:
        new = dict() if type(obj) in [dict, Dict] else OrderedDict()
        for key, val in obj.items():
            if type(val) == Dict:
                val = val.todict()
            elif type(val) == ODict:
                val = val.toOrderedDict()
            else:
                val = replaceDictODict(val)

            new[key] = val
    else:
        new = obj

    return new

# ------------------------------------------------------------------------------
# Rename objects
# ------------------------------------------------------------------------------
def rename(obj, old, new, label=None):
    """
    Function for/to <short description of `netpyne.sim.utils.rename`>

    Parameters
    ----------
    obj : <type>
        <Short description of obj>
        **Default:** *required*

    old : <type>
        <Short description of old>
        **Default:** *required*

    new : <type>
        <Short description of new>
        **Default:** *required*

    label : <``None``?>
        <Short description of label>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>


    """

    try:
        return obj.rename(old, new, label)
    except:
        if type(obj) == dict and old in obj:
            obj[new] = obj.pop(old)  # replace
            return True
        else:
            return False


# ------------------------------------------------------------------------------
# Replace tuples with str
# ------------------------------------------------------------------------------
def tupleToList(obj):
    """
    Function for/to <short description of `netpyne.sim.utils.tupleToList`>

    Parameters
    ----------
    obj : <type>
        <Short description of obj>
        **Default:** *required*


    """

    if type(obj) == list:
        for item in obj:
            if type(item) in [list, dict]:
                tupleToList(item)
            elif type(item) == tuple:
                obj[obj.index(item)] = list(item)

    elif isinstance(obj, (dict, ODict)):
        for key, val in obj.items():
            if isinstance(val, (list, dict, ODict)):
                tupleToList(val)
            elif type(val) == tuple:
                obj[key] = list(val)  # also replace empty dicts with empty list
    return obj


# ------------------------------------------------------------------------------
# Replace Decimal with float
# ------------------------------------------------------------------------------
def decimalToFloat(obj):
    """
    Function for/to <short description of `netpyne.sim.utils.decimalToFloat`>

    Parameters
    ----------
    obj : <type>
        <Short description of obj>
        **Default:** *required*


    """

    from decimal import Decimal

    if type(obj) == list:
        for i, item in enumerate(obj):
            if type(item) in [list, dict, tuple]:
                decimalToFloat(item)
            elif type(item) == Decimal:
                obj[i] = float(item)

    elif isinstance(obj, dict):
        for key, val in obj.items():
            if isinstance(val, (list, dict)):
                decimalToFloat(val)
            elif type(val) == Decimal:
                obj[key] = float(val)  # also replace empty dicts with empty list
    return obj


# ------------------------------------------------------------------------------
# Recursively remove items of an object (used to avoid mem leaks)
# ------------------------------------------------------------------------------
def clearObj(obj):
    """
    Function for/to <short description of `netpyne.sim.utils.clearObj`>

    Parameters
    ----------
    obj : <type>
        <Short description of obj>
        **Default:** *required*


    """

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


# ------------------------------------------------------------------------------
# Support funcs to load from mat
#------------------------------------------------------------------------------

def _ensureMatCompatible(obj):
    """
    Function for/to <short description of `netpyne.sim.utils._ensureMatCompatible`>

    Parameters
    ----------
    obj : <type>
        <Short description of obj>
        **Default:** *required*


    """


    if type(obj) == list:# or type(obj) == tuple:
        for item in obj:
            if isinstance(item, (list, dict, Dict, ODict)):
                _ensureMatCompatible(item)

    elif isinstance(obj, (dict, Dict, ODict)):
        for key,val in obj.items():
            if isinstance(val, (list, dict, Dict, ODict)):
                _ensureMatCompatible(val)
            if val is None:
                obj[key] = '__np_none__'
            elif isinstance(val, list) and len(val) > 0 and all(isinstance(s, str) for s in val):
                # string arrays get corrupted while saving to mat, so converting it to csv beforehand
                elements = ','.join(val)
                obj[key] = f'[{elements}]'
    return obj

def _restoreFromMat(obj):
    """
    Function for/to <short description of `netpyne.sim.utils._restoreFromMat`>

    Parameters
    ----------
    obj : <type>
        <Short description of obj>
        **Default:** *required*


    """


    if type(obj) == list:
        for item in obj:
            if isinstance(item, (list, dict, Dict, ODict)):
                _restoreFromMat(item)

    elif isinstance(obj, (dict, Dict, ODict)):
        for key,val in obj.items():
            if isinstance(val, (list, dict, Dict, ODict)):
                _restoreFromMat(val)
            if val == '__np_none__':
                obj[key] = None
            elif isinstance(val, str) and val.startswith('[') and val.endswith(']'):
                obj[key] = val[1:-1].split(',')
    return obj

def _mat2dict(obj, parentKey=None):
    """
    A recursive function which constructs from matobjects nested dictionaries
    Enforce lists for conns, synMechs and stims even if 1 element (matlab converts to dict otherwise)
    """

    from scipy.io.matlab.mio5_params import mat_struct
    import numpy as np

    isMatStruct = isinstance(obj, mat_struct)
    if isinstance(obj, (dict, mat_struct)):
        out = {}
        if isMatStruct: fieldNames = obj._fieldnames
        else: fieldNames = obj

        keysOfLists = ['conns', 'stims', 'synMechs', 'cells', 'cellGids', 'include']
        if parentKey == 'tags':
            keysOfLists.append('label')
        for key in fieldNames:
            if isMatStruct: val = obj.__dict__[key]
            else: val = obj[key]

            if isinstance(val, mat_struct):
                if key in keysOfLists:
                    out[key] = [_mat2dict(val, parentKey=key)]  # convert to 1-element list
                else:
                    out[key] = _mat2dict(val, parentKey=key)
            elif isinstance(val, np.ndarray):
                out[key] = _mat2dict(val, parentKey=key)
            elif key in keysOfLists: # isinstance(val, Number) and 
                out[key] = [val]   # convert to 1-element list
            else:
                out[key] = val

    elif isinstance(obj, np.ndarray):
        out = []
        for item in obj:
            if isinstance(item, mat_struct) or isinstance(item, np.ndarray):
                out.append(_mat2dict(item))
            else:
                out.append(item)

    else:
        out = obj

    return out


# ------------------------------------------------------------------------------
# Support funcs to save in HDF5 format
# ------------------------------------------------------------------------------
def _ensureHDF5Compatible(obj):
    import collections

    if isinstance(obj, basestring):
        return obj
    elif isinstance(obj, collections.Mapping):
        for key in list(obj.keys()):
            if isinstance(key, Number):
                obj[str(key)] = obj.pop(key)
        return dict(list(map(_ensureHDF5Compatible, iter(obj.items()))))
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, collections.Iterable):
        return type(obj)(list(map(_ensureHDF5Compatible, obj)))
    else:
        return obj


# ------------------------------------------------------------------------------
# Clear all sim objects in memory
# ------------------------------------------------------------------------------
def clearAll():
    """
    Function to clear all sim objects in memory

    """

    from .. import sim
    import numpy as np

    # clean up
    sim.pc.barrier()
    #TODO are the references within containers cleared before the containers are?


    # clean cells and simData in all nodes
    if hasattr(sim, 'net'):
        sim.clearObj([cell.__dict__ if hasattr(cell, '__dict__') else cell for cell in sim.net.cells])
    if hasattr(sim, 'simData'):
        if 'stims' in list(sim.simData.keys()):
            sim.clearObj([stim for stim in sim.simData['stims']])

        for key in list(sim.simData.keys()):
            del sim.simData[key]

    if hasattr(sim, 'net'):
        for c in sim.net.cells:
            del c
        for p in sim.net.pops:
            del p
        del sim.net.params

    # clean cells and simData gathered in master node
    if hasattr(sim, 'rank'):
        if sim.rank == 0:
            if hasattr(sim, 'net'):
                if hasattr(sim.net, 'allCells'):
                    sim.clearObj([cell.__dict__ if hasattr(cell, '__dict__') else cell for cell in sim.net.allCells])
            if hasattr(sim, 'allSimData'):
                for key in list(sim.allSimData.keys()):
                    del sim.allSimData[key]

                if 'stims' in list(sim.allSimData.keys()):
                    sim.clearObj([stim for stim in sim.allSimData['stims']])

            if hasattr(sim.net, 'allCells'):
                for c in sim.net.allCells:
                    del c
                del sim.net.allCells
            if hasattr(sim.net, 'allPops'):
                for p in sim.net.allPops:
                    del p
                del sim.net.allPops

            if hasattr(sim, 'allSimData'):
                del sim.allSimData

            import matplotlib

            matplotlib.pyplot.clf()
            matplotlib.pyplot.close('all')

    if hasattr(sim, 'net'):
        if hasattr(sim.net, 'rxd'): # check that 'net' exists before checking sim.net.rxd
            sim.clearObj(sim.net.rxd)
            # clean rxd components
            if 'rxd' not in globals():
                try:
                    from neuron import crxd as rxd
                except:
                    pass
            # try:
            for r in rxd.rxd._all_reactions[:]:
                if r():
                    rxd.rxd._unregister_reaction(r)

            for s in rxd.species._all_species:
                if s():
                    s().__del__()

            rxd.region._all_regions = []
            rxd.region._region_count = 0
            rxd.region._c_region_lookup = None
            rxd.species._species_counts = 0
            rxd.section1d._purge_cptrs()
            rxd.initializer.has_initialized = False
            rxd.rxd.free_conc_ptrs()
            rxd.rxd.free_curr_ptrs()
            rxd.rxd.rxd_include_node_flux1D(0, None, None, None)
            rxd.species._has_1d = False
            rxd.species._has_3d = False
            rxd.rxd._zero_volume_indices = np.ndarray(0, dtype=np.int_)
            rxd.set_solve_type(dimension=1)
            # clear reactions in case next sim does not use rxd
            rxd.rxd.clear_rates()

            for obj in rxd.__dict__:
                sim.clearObj(obj)
        del sim.net
    import gc
    gc.collect()

    sim.pc.barrier()
    sim.pc.gid_clear()  # clear previous gid settings

def close(message=None, clear=True):
    """
    Function to close simulation

    """
    from .. import sim
    if clear:
        clearAll()
    else:
        sim.pc.barrier()
    sys.exit()


def checkConditions(conditions, against, cellGid=None):

    conditionsMet = 1
    for (condKey, condVal) in conditions.items():

        # gid matching will be processed in specific way
        gidCompare = False
        if (cellGid is not None) and (condKey == 'gid'):
            compareTo = cellGid
            gidCompare = True

        else:
            compareTo = against.get(condKey)

        if isinstance(condVal, list):
            if isinstance(condVal[0], Number):
                if gidCompare:
                    if compareTo not in condVal:
                        conditionsMet = 0
                        break
                elif compareTo < condVal[0] or compareTo > condVal[1]:
                    conditionsMet = 0
                    break
            elif isinstance(condVal[0], basestring):
                if compareTo not in condVal:
                    conditionsMet = 0
                    break
        elif isinstance(compareTo, list): # e.g. to match 'label', which may be list
            if condVal not in compareTo:
                conditionsMet = 0
                break
        elif compareTo != condVal:
            conditionsMet = 0
            break
    return conditionsMet


# ------------------------------------------------------------------------------
# Create a subclass of json.JSONEncoder to convert numpy types in Python types
# ------------------------------------------------------------------------------
import json
import numpy as np


class NpSerializer(json.JSONEncoder):
    """
    Class for/to <short description of `netpyne.sim.utils.NpSerializer`>


    """

    def default(self, obj):
        from neuron import hoc

        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, hoc.HocObject):
            return obj.to_python()
        elif isinstance(obj, RecXElectrode):
            return obj.toJSON()
        elif callable(obj):
            return obj.__name__
        else:
            return super(NpSerializer, self).default(obj)
