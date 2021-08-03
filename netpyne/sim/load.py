"""
Module for loading of data and simulations

"""

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
from netpyne.logger import logger

#------------------------------------------------------------------------------
# Load data from file
#------------------------------------------------------------------------------
def _loadFile(filename):
    from .. import sim
    import os

    def _byteify(data, ignore_dicts = False):
        # if this is a unicode string, return its string representation
        if isinstance(data, basestring):
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
    ext = os.path.basename(filename).split('.')[-1]

    # load pickle file
    if ext == 'pkl':
        import pickle
        logger.info('Loading file %s ... ' % (filename))
        with open(filename, 'rb') as fileObj:
            if sys.version_info[0] == 2:
                data = pickle.load(fileObj)
            else:
                data = pickle.load(fileObj, encoding='latin1')

    # load dpk file
    elif ext == 'dpk':
        import gzip
        logger.warning('Loading file %s ... ' % (filename))
        #fn=sim.cfg.filename #.split('.')
        #gzip.open(fn, 'wb').write(pk.dumps(dataSave)) # write compressed string
        logger.warning('NOT IMPLEMENTED!')

    # load json file
    elif ext == 'json':
        import json
        logger.info('Loading file %s ... ' % (filename))
        with open(filename, 'r') as fileObj:
            data = json.load(fileObj) # works with py2 and py3
    # load mat file
    elif ext == 'mat':
        from scipy.io import loadmat
        logger.info('Loading file %s ... ' % (filename))
        dataraw = loadmat(filename, struct_as_record=False, squeeze_me=True)
        data = utils._mat2dict(dataraw)
        #savemat(sim.cfg.filename+'.mat', replaceNoneObj(dataSave))  # replace None and {} with [] so can save in .mat format
        logger.info('Finished saving!')

    # load HDF5 file (uses very inefficient hdf5storage module which supports dicts)
    elif ext == 'saveHDF5':
        #dataSaveUTF8 = _dict2utf8(replaceNoneObj(dataSave)) # replace None and {} with [], and convert to utf
        import hdf5storage
        logger.warning('Loading file %s ... ' % (filename))
        #hdf5storage.writes(dataSaveUTF8, filename=sim.cfg.filename+'.hdf5')
        logger.warning('NOT IMPLEMENTED!')

    # load CSV file (currently only saves spikes)
    elif ext == 'csv':
        import csv
        logger.warning('Loading file %s ... ' % (filename))
        writer = csv.writer(open(sim.cfg.filename+'.csv', 'wb'))
        #for dic in dataSave['simData']:
        #    for values in dic:
        #        writer.writerow(values)
        logger.warning('NOT IMPLEMENTED!')

    # load Dat file(s)
    elif ext == 'dat':
        logger.warning('Loading file %s ... ' % (filename))
        logger.warning('NOT IMPLEMENTED!')
        # traces = sim.cfg.recordTraces
        # for ref in traces.keys():
        #     for cellid in sim.allSimData[ref].keys():
        #         dat_file_name = '%s_%s.dat'%(ref,cellid)
        #         dat_file = open(dat_file_name, 'w')
        #         trace = sim.allSimData[ref][cellid]
        #         logger.info("Saving %i points of data on: %s:%s to %s"%(len(trace),ref,cellid,dat_file_name))
        #         for i in range(len(trace)):
        #             dat_file.write('%s\t%s\n'%((i*sim.cfg.dt/1000),trace[i]/1000))

    else:
        logger.warning('Format not recognized for file %s'%(filename))
        return

    if hasattr(sim, 'rank') and sim.rank == 0 and hasattr(sim, 'cfg') and sim.cfg.timing:
        sim.timing('stop', 'loadFileTime')
        logger.timing('  Done; file loading time = %0.2f s' % sim.timingData['loadFileTime'])


    return data


#------------------------------------------------------------------------------
# Load simulation config from file
#------------------------------------------------------------------------------
def loadSimCfg(filename, data=None, setLoaded=True):
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
    logger.info('Loading simConfig...')
    if 'simConfig' in data:
        if setLoaded:
            setup.setSimCfg(data['simConfig'])
        else:
            return specs.SimConfig(data['simConfig'])
    else:
        logger.warning('  simConfig not found in file %s'%(filename))
    pass


#------------------------------------------------------------------------------
# Load netParams from cell
#------------------------------------------------------------------------------
def loadNetParams(filename, data=None, setLoaded=True):
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


    if not data: data = _loadFile(filename)
    logger.info('Loading netParams...')
    if 'net' in data and 'params' in data['net']:
        if setLoaded:
            setup.setNetParams(data['net']['params'])
        else:
            return specs.NetParams(data['net']['params'])
    else:
        logger.warning('netParams not found in file %s'%(filename))

    pass


#------------------------------------------------------------------------------
# Load cells and pops from file and create NEURON objs
#------------------------------------------------------------------------------
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

    if not data: data = _loadFile(filename)
    if not hasattr(sim, 'net'): sim.initialize()

    if 'net' in data and 'cells' in data['net'] and 'pops' in data['net']:
        loadNow = True
        if hasattr(sim, 'rank'):
            if sim.rank != 0:
                loadNow = False
        if loadNow:
            sim.timing('start', 'loadNetTime')
            logger.info('Loading net...')
            if compactConnFormat:
                compactToLongConnFormat(data['net']['cells'], compactConnFormat) # convert loaded data to long format
            sim.net.allPops = data['net']['pops']
            sim.net.allCells = data['net']['cells']
        if instantiate:
            try:
                # calculate cells to instantiate in this node
                if hasattr(sim, 'rank'):
                    if isinstance(instantiate, list):
                        cellsNode = [data['net']['cells'][i] for i in range(int(sim.rank), len(data['net']['cells']), sim.nhosts) if i in instantiate]
                    else:
                        cellsNode = [data['net']['cells'][i] for i in range(int(sim.rank), len(data['net']['cells']), sim.nhosts)]
                else:
                    if isinstance(instantiate, list):
                        cellsNode = [data['net']['cells'][i] for i in range(0, len(data['net']['cells']), 1) if i in instantiate]
                    else:
                        cellsNode = [data['net']['cells'][i] for i in range(0, len(data['net']['cells']), 1)]
            except:
                logger.warning('Unable to instantiate network...')
            
            try:
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
                            logger.debug(' Unable to load cell secs')

                        try:
                            cell.conns = [Dict(conn) for conn in cellLoad['conns']]
                        except:
                            logger.debug(' Unable to load cell conns')

                        try:
                            cell.stims = [Dict(stim) for stim in cellLoad['stims']]
                        except:
                            logger.debug(' Unable to load cell stims')

                        sim.net.cells.append(cell)
                    logger.info('  Created %d cells' % (len(sim.net.cells)))
                    logger.info('  Created %d connections' % (sum([len(c.conns) for c in sim.net.cells])))
                    logger.info('  Created %d stims' % (sum([len(c.stims) for c in sim.net.cells])))
            except:
                logger.warning('Unable to create Python structure...')

            try:
                # only create NEURON objs, if there is Python struc (fix so minimal Python struct is created)
                if sim.cfg.createNEURONObj:
                    logger.debug("  Adding NEURON objects...")
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
                            logger.debug('  Unable to load instantiate cell conns or stims')

                    logger.info('  Added NEURON objects to %d cells' % (len(sim.net.cells)))
            except:
                logger.warning('Unable to create NEURON objects...')

            if loadNow and sim.cfg.timing:  #if sim.rank == 0 and sim.cfg.timing:
                sim.timing('stop', 'loadNetTime')
                logger.timing('  Done; re-instantiate net time = %0.2f s' % sim.timingData['loadNetTime'])
    else:
        logger.warning('  netCells and/or netPops not found in file %s'%(filename))


#------------------------------------------------------------------------------
# Load simData from file
#------------------------------------------------------------------------------
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
    
    logger.info('Loading simData...')
    
    if 'simData' in data:
        sim.allSimData = data['simData']
    else:
        logger.warning('  simData not found in file %s'%(filename))

    if 'net' in data:
        try:
            sim.net.recXElectrode = data['net']['recXElectrode']
        except:
            pass
    pass


#------------------------------------------------------------------------------
# Load all data in file
#------------------------------------------------------------------------------
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

    if not data: data = _loadFile(filename)
    loadSimCfg(filename, data=data)
    sim.cfg.createNEURONObj = createNEURONObj  # set based on argument
    loadNetParams(filename, data=data)
    if hasattr(sim.cfg, 'compactConnFormat'):
        connFormat = sim.cfg.compactConnFormat
    else:
        logger.warning('Error: no connFormat provided in simConfig')
        sys.exit()
    loadNet(filename, data=data, instantiate=instantiate, compactConnFormat=connFormat)
    loadSimData(filename, data=data)


#------------------------------------------------------------------------------
# Convert compact (list-based) to long (dict-based) conn format
#------------------------------------------------------------------------------
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
                cell['conns'][iconn] = {key: conn[index] for key,index in formatIndices.items()}
        return cells
    except:
        logger.warning("Error converting conns from compact to long format")
        return cells


#------------------------------------------------------------------------------
# load HDF5 (conns for now)
#------------------------------------------------------------------------------
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
        logger.info('Loading data ...')
        objs = ijson.items(fd, 'net.cells.item')
        if loadTags and loadConns:
            logger.info('Storing tags and conns ...')
            for cell in objs:
                if tagsGidRange==None or cell['gid'] in tagsGidRange:
                    logger.info('Cell gid: %d'%(cell['gid']))
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
            logger.info('Storing tags ...')
            if tagFormat:
                tags.update({int(cell['gid']): [cell['tags'][param] for param in tagFormat] for cell in objs if tagsGidRange==None or cell['gid'] in tagsGidRange})
            else:
                tags.update({int(cell['gid']): cell['tags'] for cell in objs if tagsGidRange==None or cell['gid'] in tagsGidRange})
        elif loadConns:
            logger.info('Storing conns...')
            if connFormat:
                conns.update({int(cell['gid']): [[conn[param] for param in connFormat] for conn in cell['conns']] for cell in objs if connsGidRange==None or cell['gid'] in connsGidRange})
            else:
                conns.update({int(cell['gid']): cell['conns'] for cell in objs if connsGidRange==None or cell['gid'] in connsGidRange})

        logger.info('time ellapsed (s): ', time() - start)

    tags = utils.decimalToFloat(tags)
    conns = utils.decimalToFloat(conns)

    if saveTags and tags:
        outFilename = saveTags if isinstance(saveTags, basestring) else 'filename'[:-4]+'_tags.json'
        logger.info('Saving tags to %s ...' % (outFilename))
        sim.saveJSON(outFilename, {'tags': tags})
    if saveConns and conns:
        outFilename = saveConns if isinstance(saveConns, basestring) else 'filename'[:-4]+'_conns.json'
        logger.info('Saving conns to %s ...' % (outFilename))
        sim.saveJSON(outFilename, {'conns': conns})

    return tags, conns
