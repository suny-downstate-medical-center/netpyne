"""
Module for loading of data and simulations

"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from builtins import open
from builtins import range

# required to make json saving work in Python 2/3
try:
    to_unicode = unicode
except NameError:
    to_unicode = str
try:
    basestring
except NameError:
    basestring = str

from future import standard_library

standard_library.install_aliases()
import sys
from collections import OrderedDict
from ..specs import Dict, ODict
from .. import specs
from . import utils
from . import setup

# ------------------------------------------------------------------------------
# Load data from file
# ------------------------------------------------------------------------------
def _loadFile(filename):
    from .. import sim
    import os

    def _byteify(data, ignore_dicts=False):
        # if this is a unicode string, return its string representation
        if isinstance(data, basestring):
            return data.encode('utf-8')
        # if this is a list of values, return list of byteified values
        if isinstance(data, list):
            return [_byteify(item, ignore_dicts=True) for item in data]
        # if this is a dictionary, return dictionary of byteified keys and values
        # but only if we haven't already byteified it
        if isinstance(data, dict) and not ignore_dicts:
            return OrderedDict(
                {_byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True) for key, value in data.items()}
            )
        # if it's anything else, return it in its original form
        return data

    if hasattr(sim, 'cfg') and sim.cfg.timing:
        sim.timing('start', 'loadFileTime')
    ext = os.path.basename(filename).split('.')[-1]

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
        # fn=sim.cfg.filename #.split('.')
        # gzip.open(fn, 'wb').write(pk.dumps(dataSave)) # write compressed string
        print('NOT IMPLEMENTED!')

    # load json file
    elif ext == 'json':
        import json

        print(('Loading file %s ... ' % (filename)))
        with open(filename, 'r') as fileObj:
            data = json.load(fileObj)  # works with py2 and py3
    # load mat file
    elif ext == 'mat':
        from scipy.io import loadmat

        print(('Loading file %s ... ' % (filename)))
        dataraw = loadmat(filename, struct_as_record=False, squeeze_me=True)
        data = utils._mat2dict(dataraw)
        # savemat(sim.cfg.filename+'.mat', replaceNoneObj(dataSave))  # replace None and {} with [] so can save in .mat format
        print('Finished saving!')

    # load HDF5 file (uses very inefficient hdf5storage module which supports dicts)
    elif ext == 'saveHDF5':
        # dataSaveUTF8 = _dict2utf8(replaceNoneObj(dataSave)) # replace None and {} with [], and convert to utf
        import hdf5storage

        print(('Loading file %s ... ' % (filename)))
        # hdf5storage.writes(dataSaveUTF8, filename=sim.cfg.filename+'.hdf5')
        print('NOT IMPLEMENTED!')

    # load CSV file (currently only saves spikes)
    elif ext == 'csv':
        import csv

        print(('Loading file %s ... ' % (filename)))
        writer = csv.writer(open(sim.cfg.filename + '.csv', 'wb'))
        # for dic in dataSave['simData']:
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
        print(('Format not recognized for file %s' % (filename)))
        return

    if hasattr(sim, 'rank') and sim.rank == 0 and hasattr(sim, 'cfg') and sim.cfg.timing:
        sim.timing('stop', 'loadFileTime')
        print(('  Done; file loading time = %0.2f s' % sim.timingData['loadFileTime']))

    return data


# ------------------------------------------------------------------------------
# Load simulation config from file
# ------------------------------------------------------------------------------
def loadSimCfg(filename, data=None, variable='simConfig', setLoaded=True):
    """
    Function for/to <short description of `netpyne.sim.load.loadSimCfg`>

    Parameters
    ----------
    filename : <type>
        <Short description of filename>
        **Default:** *required*

    data : <``None``?>
        <Short description of data>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    setLoaded : bool
        <Short description of setLoaded>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>


    """

    if not data:
        data = _loadFile(filename)
    print('Loading simConfig...')
    if variable in data:
        rawSimConfig = data[variable]
        if setLoaded:
            setup.setSimCfg(rawSimConfig)
        else:
            return specs.SimConfig(rawSimConfig)
    else:
        print(f'  {variable} not found in file {filename}')
    pass


# ------------------------------------------------------------------------------
# Load netParams from cell
# ------------------------------------------------------------------------------
def loadNetParams(filename, data=None, variable=None, setLoaded=True):
    """
    Function for/to <short description of `netpyne.sim.load.loadNetParams`>

    Parameters
    ----------
    filename : <type>
        <Short description of filename>
        **Default:** *required*

    data : <``None``?>
        <Short description of data>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    setLoaded : bool
        <Short description of setLoaded>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>


    """

    if not data:
        data = _loadFile(filename)
    print('Loading netParams...')
    if variable is not None and variable in data:
        rawNetParams = data[variable]
    elif 'net' in data and 'params' in data['net']:
        rawNetParams = data['net']['params']
    else:
        print(('netParams not found in file %s' % (filename)))
        return

    if setLoaded:
        setup.setNetParams(rawNetParams)
    else:
        return specs.NetParams(rawNetParams)


# ------------------------------------------------------------------------------
# Load cells and pops from file and create NEURON objs
# ------------------------------------------------------------------------------
def loadNet(filename, data=None, instantiate=True, compactConnFormat=False):
    """
    Function for/to <short description of `netpyne.sim.load.loadNet`>

    Parameters
    ----------
    filename : <type>
        <Short description of filename>
        **Default:** *required*

    data : <``None``?>
        <Short description of data>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    instantiate : bool
        <Short description of instantiate>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    compactConnFormat : bool
        <Short description of compactConnFormat>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>


    """

    from .. import sim

    if not data:
        data = _loadFile(filename)
    if not hasattr(sim, 'net'):
        sim.initialize()

    if 'net' in data and 'cells' in data['net'] and 'pops' in data['net']:
        loadNow = True
        if hasattr(sim, 'rank'):
            if sim.rank != 0:
                loadNow = False
        if loadNow:
            sim.timing('start', 'loadNetTime')
            print('Loading net...')
            if compactConnFormat:
                compactToLongConnFormat(data['net']['cells'], compactConnFormat)  # convert loaded data to long format
            sim.net.allPops = data['net']['pops']

            loadedPops = data['net']['pops']
            if loadedPops is ODict:
                sim.net.allPops = loadedPops
            else:
                # if populations order is not preserved (for example if loaded from JSON), need to sort them again
                sim.net.allPops = ODict()
                loadedPops = list(loadedPops.items())

                def sort(popKeyValue):
                    # the assumption while sorting is that populations order corresponds to cell gids in this population
                    cellGids = popKeyValue[1]['cellGids']
                    if len(cellGids) > 0:
                        return cellGids[0]
                    else:
                        return -1

                loadedPops.sort(key=sort)

                for pop in loadedPops:
                    sim.net.allPops[pop[0]] = pop[1]

            sim.net.allCells = data['net']['cells']
        if instantiate:
            try:
                # calculate cells to instantiate in this node
                if hasattr(sim, 'rank'):
                    if isinstance(instantiate, list):
                        cellsNode = [
                            data['net']['cells'][i]
                            for i in range(int(sim.rank), len(data['net']['cells']), sim.nhosts)
                            if i in instantiate
                        ]
                    else:
                        cellsNode = [
                            data['net']['cells'][i]
                            for i in range(int(sim.rank), len(data['net']['cells']), sim.nhosts)
                        ]
                else:
                    if isinstance(instantiate, list):
                        cellsNode = [
                            data['net']['cells'][i] for i in range(0, len(data['net']['cells']), 1) if i in instantiate
                        ]
                    else:
                        cellsNode = [data['net']['cells'][i] for i in range(0, len(data['net']['cells']), 1)]
            except:
                print('Unable to instantiate network...')

            try:
                if sim.cfg.createPyStruct:
                    for popLoadLabel, popLoad in data['net']['pops'].items():
                        pop = sim.Pop(popLoadLabel, popLoad['tags'])
                        pop.cellGids = popLoad['cellGids']
                        sim.net.pops[popLoadLabel] = pop
                    for cellLoad in cellsNode:
                        # create new cell object and add attributes, but don't create sections or associate gid yet
                        secs = cellLoad.get('secs', None)
                        gid = cellLoad['gid']
                        tags = cellLoad['tags']
                        if secs:
                            cell = sim.CompartCell(gid, tags, create=False, associateGid=False)
                            cell.secs = Dict(secs)
                            cell.create(createNEURONObj=False)  # avoid creating NEURON Objs now; just need pystruct
                        else:
                            tags['params'] = cellLoad['params']
                            cell = sim.PointCell(gid, tags, create=False, associateGid=False)

                        try:
                            cell.conns = [Dict(conn) for conn in cellLoad['conns']]
                        except:
                            if sim.cfg.verbose:
                                print(' Unable to load cell conns')

                        try:
                            cell.stims = [Dict(stim) for stim in cellLoad['stims']]
                        except:
                            if sim.cfg.verbose:
                                print(' Unable to load cell stims')

                        sim.net.cells.append(cell)
                    print(('  Created %d cells' % (len(sim.net.cells))))
                    print(('  Created %d connections' % (sum([len(c.conns) for c in sim.net.cells]))))
                    print(('  Created %d stims' % (sum([len(c.stims) for c in sim.net.cells]))))
            except Exception as e:
                print(f'Unable to create Python structure: {e}')

            try:
                # only create NEURON objs, if there is Python struc (fix so minimal Python struct is created)
                if sim.cfg.createNEURONObj:
                    if sim.cfg.verbose:
                        print("  Adding NEURON objects...")
                    # create NEURON sections, mechs, syns, etc; and associate gid
                    for cell in sim.net.cells:
                        if cell.secs:
                            prop = {'secs': cell.secs}
                            # TODO: `cell.secs` should probably be deepcopied to avoid potential "ghost" errors later in `CompartCell.createNEURONObj()`
                            # but currently deepcopying of ODict fails
                        cell.createNEURONObj(prop)  # use same syntax as when creating based on high-level specs
                        cell.associateGid()  # can only associate once the hSection obj has been created
                    # create all NEURON Netcons, NetStims, etc
                    sim.pc.barrier()
                    for cell in sim.net.cells:
                        try:
                            cell.addStimsNEURONObj()  # add stims first so can then create conns between netstims
                            cell.addConnsNEURONObj()
                        except:
                            if sim.cfg.verbose:
                                'Unable to load instantiate cell conns or stims'

                    print(('  Added NEURON objects to %d cells' % (len(sim.net.cells))))
            except Exception as e:
                print(f'Unable to create NEURON objects: {e}')

            if loadNow and sim.cfg.timing:  # if sim.rank == 0 and sim.cfg.timing:
                sim.timing('stop', 'loadNetTime')
                print(('  Done; re-instantiate net time = %0.2f s' % sim.timingData['loadNetTime']))
    else:
        print(('  netCells and/or netPops not found in file %s' % (filename)))


# ------------------------------------------------------------------------------
# Load simData from file
# ------------------------------------------------------------------------------
def loadSimData(filename, data=None):
    """
    Function to load simulation data from a file

    Parameters
    ----------
    filename : str
        The path and name of the file where the data is stored.
        **Default:** *required*

    data : dict
        A dictionary containing a `simData` key.
        **Default:** ``None``

    """

    from .. import sim

    if not data:
        data = _loadFile(filename)

    print('Loading simData...')

    if 'simData' in data:
        sim.allSimData = data['simData']
    else:
        print(('  simData not found in file %s' % (filename)))

    if 'net' in data:
        if 'recXElectrode' in data['net']:
            from netpyne.support.recxelectrode import RecXElectrode

            xElectrode = data['net']['recXElectrode']
            if False == isinstance(xElectrode, RecXElectrode):
                xElectrode = RecXElectrode.fromJSON(xElectrode)
            sim.net.recXElectrode = xElectrode


# ------------------------------------------------------------------------------
# Load all data in file
# ------------------------------------------------------------------------------
def loadAll(filename, data=None, instantiate=True, createNEURONObj=True):
    """
    Function for/to <short description of `netpyne.sim.load.loadAll`>

    Parameters
    ----------
    filename : <type>
        <Short description of filename>
        **Default:** *required*

    data : <``None``?>
        <Short description of data>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    instantiate : bool
        <Short description of instantiate>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    createNEURONObj : bool
        <Short description of createNEURONObj>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>


    """

    from .. import sim

    if not data:
        data = _loadFile(filename)
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


def loadFromIndexFile(index):
    return loadModel(index, loadMechs=False)


def loadModel(path, loadMechs=True, ignoreMechAlreadyExistsError=False):

    import __main__
    import json
    from .. import sim

    import os

    originalDir = os.getcwd()

    absPath = os.path.abspath(path)

    if os.path.isdir(absPath):
        # if no index file specified explicitly, use default
        index = os.path.join(absPath, 'index.npjson')
        dir = absPath
    else:
        index = absPath
        dir = os.path.dirname(absPath)

    print(f'Loading model from {index} ... ')
    with open(index, 'r') as fileObj:
        indexData = json.load(fileObj)

        if loadMechs:
            modFolder = indexData.get('mod_folder')
            if modFolder:
                modFolderPath = os.path.join(dir, modFolder)
                __processMod(modFolderPath, ignoreMechAlreadyExistsError)

        os.chdir(dir)

        configFile = indexData.get('simConfig')
        if not configFile:
            raise Exception("Model index is missing 'simConfig' attribute")
        print(f'\n    Loading simConfig: {configFile} ... ')

        if configFile[-3:] == '.py':
            cfgModule = sim.loadPythonModule(configFile)
            configVar = indexData.get('simConfig_variable', 'cfg')
            cfg = getattr(cfgModule, configVar)
        else:
            configVar = indexData.get('simConfig_variable', 'simConfig')
            cfg = sim.loadSimCfg(configFile, variable=configVar, setLoaded=False)

        netParamsFile = indexData.get('netParams')
        if not netParamsFile:
            raise Exception("Model index is missing 'netParams' attribute")
        print(f'\n    Loading netParams: {netParamsFile} ... ')

        if netParamsFile[-3:] == '.py':
            __main__.cfg = cfg  # this is often required by netParams

            netParamsModule = sim.loadPythonModule(netParamsFile)
            paramsVar = indexData.get('netParams_variable', 'netParams')
            netParams = getattr(netParamsModule, paramsVar)
        else:
            paramsVar = indexData.get('netParams_variable', None)
            netParams = sim.loadNetParams(netParamsFile, variable=paramsVar, setLoaded=False)

        os.chdir(originalDir)

    return cfg, netParams


def __processMod(modFolderPath, ignoreMechAlreadyExistsError):
    import os, subprocess, shutil, time, glob
    import neuron
    from neuron import h

    if not os.path.exists(modFolderPath):
        print(f"Warning: specified 'mod_folder' path {modFolderPath} doesn't exist")
        return

    originalDir = os.getcwd()
    os.chdir(modFolderPath)
    shutil.rmtree('x86_64', ignore_errors=True)

    if not ignoreMechAlreadyExistsError:
        # compile and load all the mods from folder. If some of them already exist,
        # it will raise the error
        subprocess.call(["nrnivmodl"])
        neuron.load_mechanisms(os.path.abspath('.'))
    else:
        # parse mod files and load only those not yet loaded
        mods = glob.glob("*.mod")

        alreadyLoadedMods = []
        for file in mods:
            name = __extractModelName(file)
            try:
                getattr(h, name)
                alreadyLoadedMods.append(file)
            except:
                pass

        modsToLoad = set(mods) - set(alreadyLoadedMods)
        if len(modsToLoad) > 0:
            # compile into dir other than x86_64 to bypass possibly cached data
            tmpDir = f'tmp_{os.getpid()}_{time.time()}'
            os.mkdir(tmpDir)
            os.chdir(tmpDir)
            modsToLoad = list(map(lambda path: f'../{path}', modsToLoad))
            subprocess.call(['nrnivmodl'] + list(modsToLoad))
            neuron.load_mechanisms(os.path.abspath('.'))
            os.chdir('..')
            os.system(f'rm -rf {tmpDir}')

    os.chdir(originalDir)

def __extractModelName(modFile):
    import re
    lines = []
    with open(modFile, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.split(':')[0] # drop code comments
        for modType in ['suffix', 'point_process', 'artificial_cell']:
            if (modType + ' ') in line.lower():
                partWithName = re.split(modType, line, flags=re.IGNORECASE)[1]
                partWithName = partWithName.replace("}", " ") # for the case like "NEURON {SUFFIX NAME}"
                name = partWithName.strip().split(" ")[0]
                return name
    return None


# ------------------------------------------------------------------------------
# Convert compact (list-based) to long (dict-based) conn format
# ------------------------------------------------------------------------------
def compactToLongConnFormat(cells, connFormat):
    """
    Function for/to <short description of `netpyne.sim.load.compactToLongConnFormat`>

    Parameters
    ----------
    cells : <type>
        <Short description of cells>
        **Default:** *required*

    connFormat : <type>
        <Short description of connFormat>
        **Default:** *required*


    """

    formatIndices = {key: connFormat.index(key) for key in connFormat}
    try:
        for cell in cells:
            for iconn, conn in enumerate(cell['conns']):
                cell['conns'][iconn] = {key: conn[index] for key, index in formatIndices.items()}
        return cells
    except:
        print("Error converting conns from compact to long format")
        return cells


# ------------------------------------------------------------------------------
# load HDF5 (conns for now)
# ------------------------------------------------------------------------------
def loadHDF5(filename):
    """
    Function for/to <short description of `netpyne.sim.load.loadHDF5`>

    Parameters
    ----------
    filename : <type>
        <Short description of filename>
        **Default:** *required*


    """

    from .. import sim
    import h5py

    if sim.rank == 0:
        timing('start', 'loadTimeHDF5')

    connsh5 = h5py.File(filename, 'r')
    conns = [list(x) for x in connsh5['conns']]
    connsFormat = list(connsh5['connsFormat'])

    if sim.rank == 0:
        timing('stop', 'loadTimeHDF5')

    return conns, connsFormat


# ------------------------------------------------------------------------------
# Load cell tags and conns using ijson (faster!)
# ------------------------------------------------------------------------------
def ijsonLoad(
    filename,
    tagsGidRange=None,
    connsGidRange=None,
    loadTags=True,
    loadConns=True,
    tagFormat=None,
    connFormat=None,
    saveTags=None,
    saveConns=None,
):
    """
    Function for/to <short description of `netpyne.sim.load.ijsonLoad`>

    Parameters
    ----------
    filename : <type>
        <Short description of filename>
        **Default:** *required*

    tagsGidRange : <``None``?>
        <Short description of tagsGidRange>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    connsGidRange : <``None``?>
        <Short description of connsGidRange>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    loadTags : bool
        <Short description of loadTags>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    loadConns : bool
        <Short description of loadConns>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    tagFormat : <``None``?>
        <Short description of tagFormat>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    connFormat : <``None``?>
        <Short description of connFormat>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    saveTags : <``None``?>
        <Short description of saveTags>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    saveConns : <``None``?>
        <Short description of saveConns>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>


    """

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

    with open(filename, 'rb') as fd:
        start = time()
        print('Loading data ...')
        objs = ijson.items(fd, 'net.cells.item')
        if loadTags and loadConns:
            print('Storing tags and conns ...')
            for cell in objs:
                if tagsGidRange == None or cell['gid'] in tagsGidRange:
                    print('Cell gid: %d' % (cell['gid']))
                    if tagFormat:
                        tags[int(cell['gid'])] = [cell['tags'][param] for param in tagFormat]
                    else:
                        tags[int(cell['gid'])] = cell['tags']
                    if connsGidRange == None or cell['gid'] in connsGidRange:
                        if connFormat:
                            conns[int(cell['gid'])] = [[conn[param] for param in connFormat] for conn in cell['conns']]
                        else:
                            conns[int(cell['gid'])] = cell['conns']
        elif loadTags:
            print('Storing tags ...')
            if tagFormat:
                tags.update(
                    {
                        int(cell['gid']): [cell['tags'][param] for param in tagFormat]
                        for cell in objs
                        if tagsGidRange == None or cell['gid'] in tagsGidRange
                    }
                )
            else:
                tags.update(
                    {
                        int(cell['gid']): cell['tags']
                        for cell in objs
                        if tagsGidRange == None or cell['gid'] in tagsGidRange
                    }
                )
        elif loadConns:
            print('Storing conns...')
            if connFormat:
                conns.update(
                    {
                        int(cell['gid']): [[conn[param] for param in connFormat] for conn in cell['conns']]
                        for cell in objs
                        if connsGidRange == None or cell['gid'] in connsGidRange
                    }
                )
            else:
                conns.update(
                    {
                        int(cell['gid']): cell['conns']
                        for cell in objs
                        if connsGidRange == None or cell['gid'] in connsGidRange
                    }
                )

        print('time ellapsed (s): ', time() - start)

    tags = utils.decimalToFloat(tags)
    conns = utils.decimalToFloat(conns)

    if saveTags and tags:
        outFilename = saveTags if isinstance(saveTags, basestring) else 'filename'[:-4] + '_tags.json'
        print('Saving tags to %s ...' % (outFilename))
        sim.saveJSON(outFilename, {'tags': tags})
    if saveConns and conns:
        outFilename = saveConns if isinstance(saveConns, basestring) else 'filename'[:-4] + '_conns.json'
        print('Saving conns to %s ...' % (outFilename))
        sim.saveJSON(outFilename, {'conns': conns})

    return tags, conns
