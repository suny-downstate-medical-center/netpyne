"""
Module related to saving

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from builtins import range
from builtins import open
from future import standard_library
standard_library.install_aliases()

# required to make json saving work in Python 2/3
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

import os
from time import time
from datetime import datetime
import pickle as pk
from . import gather
from . import utils


#------------------------------------------------------------------------------
# Save JSON (Python 2/3 compatible)
#------------------------------------------------------------------------------
def saveJSON(fileName, data):
    """
    Function for/to <short description of `netpyne.sim.save.saveJSON`>

    Parameters
    ----------
    fileName : <type>
        <Short description of fileName>
        **Default:** *required*

    data : <type>
        <Short description of data>
        **Default:** *required*


    """


    import json, io
    from .utils import NpSerializer

    with io.open(fileName, 'w', encoding='utf8') as fileObj:
        str_ = json.dumps(data,
                          indent=4, sort_keys=True,
                          separators=(',', ': '), ensure_ascii=False,
                          cls=NpSerializer)
        fileObj.write(to_unicode(str_))


#------------------------------------------------------------------------------
# Save data
#------------------------------------------------------------------------------
def saveData(include=None, filename=None):
    """
    Function for/to <short description of `netpyne.sim.save.saveData`>

    Parameters
    ----------
    include : <``None``?>
        <Short description of include>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    filename : <``None``?>
        <Short description of filename>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>


    """


    from .. import sim

    if sim.rank == 0 and not getattr(sim.net, 'allCells', None) and not getattr(sim, 'allSimData', None): needGather = True
    else: needGather = False
    if needGather: gather.gatherData()

    if filename: sim.cfg.filename = filename

    if sim.rank == 0:
        sim.timing('start', 'saveTime')
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
        if 'netParams' in include:
            sim.net.params.__dict__.pop('_labelid', None)
            net['params'] = utils.replaceFuncObj(sim.net.params.__dict__)
        if 'net' in include: include.extend(['netPops', 'netCells'])
        if 'netCells' in include and hasattr(sim.net, 'allCells'): net['cells'] = sim.net.allCells
        if 'netPops' in include and hasattr(sim.net, 'allPops'): net['pops'] = sim.net.allPops
        if net: dataSave['net'] = net
        if 'simConfig' in include: dataSave['simConfig'] = sim.cfg.__dict__
        if 'simData' in include:
            if 'LFP' in sim.allSimData:
                sim.allSimData['LFP'] = sim.allSimData['LFP'].tolist()
            dataSave['simData'] = sim.allSimData


        if dataSave:
            if sim.cfg.timestampFilename:
                timestamp = time()
                timestampStr = '-' + datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S')
            else:
                timestampStr = ''

            filePath = sim.cfg.filename + timestampStr
            # Save to pickle file
            if sim.cfg.savePickle:
                import pickle
                dataSave = utils.replaceDictODict(dataSave)
                print(('Saving output as %s ... ' % (filePath + '.pkl')))
                with open(filePath+'.pkl', 'wb') as fileObj:
                    pickle.dump(dataSave, fileObj)
                print('Finished saving!')

            # Save to dpk file
            if sim.cfg.saveDpk:
                import gzip
                print(('Saving output as %s ... ' % (filePath+'.dpk')))
                #fn=filePath #.split('.')
                gzip.open(filePath, 'wb').write(pk.dumps(dataSave)) # write compressed string
                print('Finished saving!')

            # Save to json file
            if sim.cfg.saveJson:
                # Make it work for Python 2+3 and with Unicode
                print(('Saving output as %s ... ' % (filePath+'.json ')))
                #dataSave = utils.replaceDictODict(dataSave)  # not required since json saves as dict
                sim.saveJSON(filePath+'.json', dataSave)
                print('Finished saving!')

            # Save to mat file
            if sim.cfg.saveMat:
                from scipy.io import savemat
                print(('Saving output as %s ... ' % (filePath+'.mat')))
                savemat(filePath+'.mat', utils.tupleToList(utils.replaceNoneObj(dataSave)))  # replace None and {} with [] so can save in .mat format
                print('Finished saving!')

            # Save to HDF5 file (uses very inefficient hdf5storage module which supports dicts)
            if sim.cfg.saveHDF5:
                dataSaveUTF8 = utils._dict2utf8(utils.replaceNoneObj(dataSave)) # replace None and {} with [], and convert to utf
                import hdf5storage
                print(('Saving output as %s... ' % (filePath+'.hdf5')))
                hdf5storage.writes(dataSaveUTF8, filename=filePath+'.hdf5')
                print('Finished saving!')

            # Save to CSV file (currently only saves spikes)
            if sim.cfg.saveCSV:
                if 'simData' in dataSave:
                    import csv
                    print(('Saving output as %s ... ' % (filePath+'.csv')))
                    writer = csv.writer(open(filePath+'.csv', 'wb'))
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
                sim.timing('stop', 'saveTime')
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
            return os.getcwd() + '/' + filePath

        else:
            print('Nothing to save')


#------------------------------------------------------------------------------
# Save distributed data using HDF5 (only conns for now)
#------------------------------------------------------------------------------
def distributedSaveHDF5():
    """
    Function for/to <short description of `netpyne.sim.save.distributedSaveHDF5`>


    """


    from .. import sim
    import h5py

    if sim.rank == 0: sim.timing('start', 'saveTimeHDF5')

    sim.compactConnFormat()
    conns = [[cell.gid]+conn for cell in sim.net.cells for conn in cell.conns]
    conns = sim.copyRemoveItemObj(conns, keystart='h', newval=[])
    connFormat = ['postGid']+sim.cfg.compactConnFormat
    with h5py.File(sim.cfg.filename+'.h5', 'w') as hf:
        hf.create_dataset('conns', data = conns)
        hf.create_dataset('connsFormat', data = connFormat)

    if sim.rank == 0: sim.timing('stop', 'saveTimeHDF5')


#------------------------------------------------------------------------------
# Convert connections in long dict format to compact list format
#------------------------------------------------------------------------------
def compactConnFormat():
    """
    Function for/to <short description of `netpyne.sim.save.compactConnFormat`>


    """


    from .. import sim

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

#------------------------------------------------------------------------------
# Gathers data in master and saves it mid run
#------------------------------------------------------------------------------
def intervalSave(t):
    """
    Function for/to <short description of `netpyne.sim.save.intervalSave`>

    Parameters
    ----------
    t : <type>
        <Short description of t>
        **Default:** *required*


    """


    from .. import sim
    from ..specs import Dict
    import pickle, os
    import numpy as np

    sim.pc.barrier()

    # create folder if missing
    if sim.rank == 0:
        if hasattr(sim.cfg, 'intervalFolder'):
            targetFolder = sim.cfg.intervalFolder
        else:
            targetFolder = os.path.dirname(sim.cfg.filename)

        if targetFolder and not os.path.exists(targetFolder):
            try:
                os.mkdir(targetFolder)
            except OSError:
                print(' Could not create target folder: %s' % (targetFolder))

    gatherLFP=True
    simDataVecs = ['spkt','spkid','stims']+list(sim.cfg.recordTraces.keys())
    singleNodeVecs = ['t']

    netPopsCellGids = {popLabel: list(pop.cellGids) for popLabel,pop in sim.net.pops.items()}

    # gather only sim data
    nodeData = {'simData': sim.simData}
    if hasattr(sim.cfg, 'saveWeights'):
        if sim.cfg.saveWeights:
            nodeData['simData']['allWeights']= sim.allWeights
            simDataVecs = simDataVecs + ['allWeights']
    data = [None]*sim.nhosts
    data[0] = {}
    for k,v in nodeData.items():
        data[0][k] = v
    gather = sim.pc.py_alltoall(data)
    sim.pc.barrier()
    if sim.rank == 0: # simData
        print('  Gathering only sim data in master...')
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
            sim.allSimData['spkt'], sim.allSimData['spkid'] = zip(*sorted(zip(sim.allSimData['spkt'], sim.allSimData['spkid']))) # sort spks
            sim.allSimData['spkt'], sim.allSimData['spkid'] = list(sim.allSimData['spkt']), list(sim.allSimData['spkid'])

        name = targetFolder + '/data_{:0.0f}.pkl'.format(t)
        with open(name, 'wb') as f:
            pickle.dump(dict(sim.allSimData), f, protocol=2)

        # clean to avoid mem leaks
        for node in gather:
            if node:
                node.clear()
                del node
        for item in data:
            if item:
                item.clear()
                del item

    sim.pc.barrier()
    for k, v in sim.simData.items():
        if k in ['spkt', 'spkid', 'stims']:
            v.resize(0)

    if hasattr(sim.cfg, 'saveWeights'):
        if sim.cfg.saveWeights:
            sim.allWeights = []


#------------------------------------------------------------------------------
# Save data in each node
#------------------------------------------------------------------------------
def saveDataInNodes(filename=None, saveLFP=True, removeTraces=False, dataDir=None):
    """
    Function to save simulation data by node rather than as a whole

    Parameters
    ----------
    filename : str
        The name to use for the saved files.
        **Default:** ``None``

    saveLFP : bool
        Whether to save any LFP data.
        **Default:** ``True`` saves LFP data.
        **Options:** ``False`` does not save LFP data.

    removeTraces : bool
        Whether to remove traces data before saving.
        **Default:** ``False`` does not remove the trace data.
        **Options:** ``True`` removes the trace data.

    dataDir : str
        Name of the directory where data files will be saved.
        **Default:** ``None`` saves to the default directory.

    """

    from .. import sim
    from ..specs import Dict, ODict

    sim.timing('start', 'saveInNodeTime')
    import os

    # create folder if missing
    if not dataDir:
        dataDir = sim.cfg.filename + '_node_data'

    if not os.path.exists(dataDir):
        os.makedirs(dataDir, exist_ok=True)

    sim.pc.barrier()
    if sim.rank == 0:
        print('\nSaving an output file for each node in: %s' % (dataDir))

    # saving data
    dataSave = {}

    dataSave['netpyne_version'] = sim.version(show=False)
    dataSave['netpyne_changeset'] = sim.gitChangeset(show=False)

    simDataVecs = ['spkt', 'spkid', 'stims'] + list(sim.cfg.recordTraces.keys())
    singleNodeVecs = ['t']

    saveSimData = {}

    if saveLFP:
        simData = sim.simData
    else:
        simData = {k: v for k, v in sim.simData.items() if k not in ['LFP']}

    for k in list(simData.keys()):  # initialize all keys of allSimData dict
        saveSimData[k] = {}

    for key, val in simData.items():  # update simData dics of dics of h.Vector
            if key in simDataVecs:          # simData dicts that contain Vectors
                if isinstance(val, dict):
                    for cell, val2 in val.items():
                        if isinstance(val2, dict):
                            saveSimData[key].update({cell: {}})
                            for stim, val3 in val2.items():
                                saveSimData[key][cell].update({stim: list(val3)}) # udpate simData dicts which are dicts of dicts of Vectors (eg. ['stim']['cell_1']['backgrounsd']=h.Vector)
                        else:
                            saveSimData[key].update({cell: list(val2)})  # udpate simData dicts which are dicts of Vectors (eg. ['v']['cell_1']=h.Vector)
                else:
                    saveSimData[key] = list(saveSimData[key]) + list(val) # udpate simData dicts which are Vectors
            elif key in singleNodeVecs:
                if sim.rank == 0:
                    saveSimData[key] = list(val)
            else:
                saveSimData[key] = val           # update simData dicts which are not Vectors

    dataSave['simData'] = saveSimData
    dataSave['cells'] = sim.net.cells
    dataSave['pops'] = sim.net.pops

    if removeTraces:
        for k in sim.cfg.recordTraces.keys():
            del sim.simData[k]

    if getattr(sim.net.params, 'version', None): dataSave['netParams_version'] = sim.net.params.version

    if dataSave:
        if sim.cfg.timestampFilename:
            timestamp = time()
            timestampStr = '-' + datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S')
        else:
            timestampStr = ''

        if not filename:
            filename = sim.cfg.filename
        filePath = filename + timestampStr
        
        # Save to pickle file
        if sim.cfg.savePickle:
            import pickle
            dataSave = utils.replaceDictODict(dataSave)
            fileName = filePath + '_node_' + str(sim.rank) + '.pkl'
            print(('  Saving output as: %s ... ' % (fileName)))
            with open(os.path.join(dataDir, fileName), 'wb') as fileObj:
                pickle.dump(dataSave, fileObj)

        # Save to json file
        if sim.cfg.saveJson:
            fileName = filePath + '_node_' + str(sim.rank) + '.json'
            print(('  Saving output as: %s ... ' % (fileName)))
            sim.saveJSON(os.path.join(dataDir, fileName), dataSave)

        # Save timing
        sim.pc.barrier()
        if sim.rank == 0:
            if sim.cfg.timing:
                sim.timing('stop', 'saveInNodeTime')
                print(('  Done; saving time = %0.2f s.' % sim.timingData['saveInNodeTime']))
            if sim.cfg.timing and sim.cfg.saveTiming:
                import pickle
                with open('timing.pkl', 'wb') as file: pickle.dump(sim.timing, file)
