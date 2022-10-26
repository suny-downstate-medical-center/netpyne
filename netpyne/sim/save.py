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
from time import time, sleep
from datetime import datetime
import pickle as pk
from . import gather
from . import utils
from ..specs import Dict, ODict


#------------------------------------------------------------------------------
# Save JSON (Python 2/3 compatible)
#------------------------------------------------------------------------------
def saveJSON(fileName, data, checkFileTimeout=0):
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

    checkFileTimeout: timeout (sec)
        if >0 then will check if file exists before continuing 
        at 0.1 ms intervals for the timeout specified in secs


    """


    import json, io
    from .utils import NpSerializer

    with io.open(fileName, 'w', encoding='utf-8') as fileObj:
        str_ = json.dumps(data,
                          indent=4, sort_keys=True,
                          separators=(',', ': '), ensure_ascii=False,
                          cls=NpSerializer)
        fileObj.write(to_unicode(str_))


    if checkFileTimeout>0:
        sleepTime = 0.1
        timeoutCyles = checkFileTimeout / sleepTime 
        cycles = 0
        while not os.path.exists(fileName) and cycles <= timeOutCycles:
            sleep(sleepTime)
            


#------------------------------------------------------------------------------
# Save data
#------------------------------------------------------------------------------
def saveData(include=None, filename=None, saveLFP=True):
    """
    Function to save simulation data to file

    Parameters
    ----------
    include : list
        What data to save
        **Default:** ``sim.cfg.saveDataInclude``
        **Options:** The list may include any combination of the following: ``'simData'``, ``'simConfig'``, ``'netParams'``, ``'net'``.

    filename : str
        Path and file name to save data to
        **Default:** ``None``

    """

    from .. import sim
    if sim.cfg.validateDataSaveOptions() is False:
        return []

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
        synMechStringFuncs = None
        cellParamStringFuncs = None

        dataSave['netpyne_version'] = sim.version(show=False)
        dataSave['netpyne_changeset'] = sim.gitChangeset(show=False)

        if getattr(sim.net.params, 'version', None): dataSave['netParams_version'] = sim.net.params.version
        if 'netParams' in include:
            # exclude from dataSave but keep in synMechParams later, for integrity
            cellParamStringFuncs = sim.net.params.__dict__.pop('_cellParamStringFuncs', None)
            synMechStringFuncs = sim.net.params.__dict__.pop('_synMechStringFuncs', None)
            sim.net.params.__dict__.pop('_labelid', None)
            net['params'] = utils.replaceFuncObj(sim.net.params.__dict__)
        if 'net' in include: include.extend(['netPops', 'netCells'])
        if 'netCells' in include and hasattr(sim.net, 'allCells'): net['cells'] = sim.net.allCells
        if 'netPops' in include and hasattr(sim.net, 'allPops'): net['pops'] = sim.net.allPops
        if net: dataSave['net'] = net
        if 'simConfig' in include: dataSave['simConfig'] = sim.cfg.__dict__
        if 'simData' in include:
            if saveLFP:
                if 'LFP' in sim.allSimData:
                    sim.allSimData['LFP'] = sim.allSimData['LFP'].tolist()
                    if hasattr(sim.net, 'recXElectrode'):
                        dataSave['net']['recXElectrode'] = sim.net.recXElectrode
            dataSave['simData'] = sim.allSimData

        savedFiles = []
        if dataSave:
            if sim.cfg.timestampFilename:
                timestamp = time()
                timestampStr = '-' + datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S')
            else:
                timestampStr = ''

            filePath = sim.cfg.filename + '_data' + timestampStr
            if hasattr(sim.cfg, 'saveFolder') and sim.cfg.saveFolder:
                filePath = os.path.join(sim.cfg.saveFolder, sim.cfg.filename + '_data' + timestampStr) 
                if hasattr(sim.cfg, 'simLabel') and sim.cfg.simLabel:
                    filePath = os.path.join(sim.cfg.saveFolder, sim.cfg.simLabel + '_data' + timestampStr)

            # create folder if missing
            targetFolder = os.path.dirname(filePath)
            if targetFolder and not os.path.exists(targetFolder):
                try:
                    os.mkdir(targetFolder)
                except OSError:
                    print(' Could not create target folder: %s' % (targetFolder))
            
            # Save to pickle file
            if sim.cfg.savePickle:
                import pickle
                path = filePath + '.pkl'
                dataSave = utils.replaceDictODict(dataSave)
                print(f'Saving output as {path} ... ')
                with open(path, 'wb') as fileObj:
                    pickle.dump(dataSave, fileObj)
                savedFiles.append(path)
                print('Finished saving!')

            # Save to dpk file
            if sim.cfg.saveDpk:
                import gzip
                path = filePath + '.dpk'
                print(f'Saving output as {path} ... ')
                #fn=filePath #.split('.')
                gzip.open(path, 'wb').write(pk.dumps(dataSave)) # write compressed string
                savedFiles.append(path)
                print('Finished saving!')

            # Save to json file
            if sim.cfg.saveJson:
                path = filePath + '.json'
                # Make it work for Python 2+3 and with Unicode
                print(f'Saving output as {path} ... ')
                #dataSave = utils.replaceDictODict(dataSave)  # not required since json saves as dict
                sim.saveJSON(path, dataSave, checkFileTimeout=5)
                savedFiles.append(path)
                print('Finished saving!')

            # Save to mat file
            if sim.cfg.saveMat:
                from scipy.io import savemat
                path = filePath + '.mat'
                print(f'Saving output as {path} ... ')
                dataSave = utils.replaceDictODict(dataSave)
                dataSave = utils._ensureMatCompatible(dataSave)
                savemat(path, utils.tupleToList(dataSave), long_field_names=True)
                savedFiles.append(path)
                print('Finished saving!')

            # Save to HDF5 file (uses very inefficient hdf5storage module which supports dicts)
            if sim.cfg.saveHDF5:
                recXElectrode = dataSave['net'].get('recXElectrode')
                if recXElectrode:
                    dataSave['net']['recXElectrode'] = recXElectrode.toJSON()
                dataSaveUTF8 = utils._dict2utf8(dataSave)
                keys = list(dataSaveUTF8.keys())
                dataSaveUTF8['keys'] = keys
                import hdf5storage
                path = filePath + '.hdf5'
                print(f'Saving output as {path} ... ')
                if os.path.exists(path):
                    # remove already existing file since `hdf5storage` concatenates new data by default 
                    os.remove(path)
                hdf5storage.writes(dataSaveUTF8, filename=path)
                savedFiles.append(path)
                print('Finished saving!')

            # Save to CSV file (currently only saves spikes)
            if sim.cfg.saveCSV:
                if 'simData' in dataSave:
                    import csv
                    path = filePath + '.csv'
                    print(f'Saving output as {path} ... ')
                    writer = csv.writer(open(path, 'wb'))
                    for dic in dataSave['simData']:
                        for values in dic:
                            writer.writerow(values)
                    savedFiles.append(path)
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
                        dat_file.close()
                        savedFiles.append(dat_file_name)

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

        else:
            print('Nothing to save')

        if synMechStringFuncs:
            sim.net.params._synMechStringFuncs = synMechStringFuncs
        if cellParamStringFuncs:
            sim.net.params._cellParamStringFuncs = cellParamStringFuncs

        return savedFiles


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

_previousIntervalSaveFile = None

#------------------------------------------------------------------------------
# Gathers data in master and saves it mid run
#------------------------------------------------------------------------------
def intervalSave(simTime, gatherLFP=True):
    """
    Function to save data at a specific time point in the simulation

    Parameters
    ----------
    simTime : number
        The time at which to save the data
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
        elif hasattr(sim.cfg, 'saveFolder'):
            targetFolder = os.path.join(sim.cfg.saveFolder, 'interval_data')
        else:
            targetFolder = 'interval_data'

        if targetFolder and not os.path.exists(targetFolder):
            try:
                os.makedirs(targetFolder)
            except OSError:
                print(' Could not create target folder: %s' % (targetFolder))

        include = sim.cfg.saveDataInclude
    
    singleNodeVecs = ['t']
    simDataVecs = ['spkt','spkid','stims']+list(sim.cfg.recordTraces.keys())

    netPopsCellGids = {popLabel: list(pop.cellGids) for popLabel,pop in sim.net.pops.items()}

    nodeData = {'netCells': [c.__getstate__() for c in sim.net.cells], 'netPopsCellGids': netPopsCellGids, 'simData': sim.simData}
    if gatherLFP and hasattr(sim.net, 'recXElectrode'):
        nodeData['xElectrodeTransferResistances'] = sim.net.recXElectrode.transferResistances

    if hasattr(sim.cfg, 'saveWeights') and sim.cfg.saveWeights:
        nodeData['simData']['allWeights']= sim.allWeights
        simDataVecs = simDataVecs + ['allWeights']

    data = [None]*sim.nhosts
    data[0] = {}
    for k,v in nodeData.items():
        data[0][k] = v

    gather = sim.pc.py_alltoall(data)
    sim.pc.barrier()
    if sim.rank == 0:
        allCells = []
        allPops = ODict()
        for popLabel,pop in sim.net.pops.items(): allPops[popLabel] = pop.__getstate__() # can't use dict comprehension for OrderedDict
        allPopsCellGids = {popLabel: [] for popLabel in netPopsCellGids}
        sim.allSimData = Dict()
        allResistances = {}

        for k in list(gather[0]['simData'].keys()):  # initialize all keys of allSimData dict
            if gatherLFP and k == 'LFP':
                sim.allSimData[k] = np.zeros((gather[0]['simData']['LFP'].shape))
            elif gatherLFP and k == 'LFPPops':
                sim.allSimData[k] = {p: np.zeros(gather[0]['simData']['LFP'].shape) for p in gather[0]['simData']['LFPPops'].keys()}
            elif sim.cfg.recordDipolesHNN and k == 'dipole':
                for dk in sim.cfg.recordDipolesHNN:
                    sim.allSimData[k][dk] = np.zeros(len(gather[0]['simData']['dipole'][dk]))
            elif sim.cfg.recordDipole and k == 'dipoleSum':
                sim.allSimData[k] = np.zeros(gather[0]['simData']['dipoleSum'].shape)
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
                        for key2,val2 in val.items():
                            if isinstance(val2,dict):
                                sim.allSimData[key].update(Dict({key2:Dict()}))
                                for stim,val3 in val2.items():
                                    sim.allSimData[key][key2].update({stim:list(val3)}) # udpate simData dicts which are dicts of dicts of Vectors (eg. ['stim']['cell_1']['backgrounsd']=h.Vector)
                            elif key == 'dipole':
                                sim.allSimData[key][key2] = np.add(sim.allSimData[key][key2],val2.as_numpy()) # add together dipole values from each node
                            else:
                                sim.allSimData[key].update({key2:list(val2)})  # udpate simData dicts which are dicts of Vectors (eg. ['v']['cell_1']=h.Vector)
                    else:
                        sim.allSimData[key] = list(sim.allSimData[key])+list(val) # udpate simData dicts which are Vectors
                elif gatherLFP and key == 'LFP':
                    sim.allSimData[key] += np.array(val)
                elif gatherLFP and key == 'LFPPops':
                    for p in val:
                        sim.allSimData[key][p] += np.array(val[p])
                elif key == 'dipoleSum':
                    sim.allSimData[key] += val
                elif key not in singleNodeVecs:
                    sim.allSimData[key].update(val)           # update simData dicts which are not Vectors
                if 'xElectrodeTransferResistances' in node:
                    allResistances.update(node['xElectrodeTransferResistances'])

        if len(sim.allSimData['spkt']) > 0:
            sim.allSimData['spkt'], sim.allSimData['spkid'] = zip(*sorted(zip(sim.allSimData['spkt'], sim.allSimData['spkid']))) # sort spks
            sim.allSimData['spkt'], sim.allSimData['spkid'] = list(sim.allSimData['spkt']), list(sim.allSimData['spkid'])

        sim.net.allCells =  sorted(allCells, key=lambda k: k['gid'])

        for popLabel,pop in allPops.items():
            pop['cellGids'] = sorted(allPopsCellGids[popLabel])
        sim.net.allPops = allPops

        if gatherLFP and hasattr(sim.net, 'recXElectrode'):
            sim.net.recXElectrode.transferResistances = allResistances
    
    if sim.rank == 0: # simData
        print('  Saving data at intervals... {:0.0f} ms'.format(simTime))

        # clean to avoid mem leaks
        for node in gather:
            if node:
                node.clear()
                del node
        for item in data:
            if item:
                item.clear()
                del item

        name = os.path.join(targetFolder, 'interval_{:0.0f}.pkl'.format(simTime))
        
        dataSave = {}
        net = {}

        dataSave['netpyne_version'] = sim.version(show=False)
        dataSave['netpyne_changeset'] = sim.gitChangeset(show=False)

        if getattr(sim.net.params, 'version', None): dataSave['netParams_version'] = sim.net.params.version
        if 'netParams' in include:
            sim.net.params.__dict__.pop('_labelid', None)
            net['params'] = utils.replaceFuncObj(sim.net.params.__dict__)
        if 'net' in include: 
            include.extend(['netPops', 'netCells'])
        if 'netCells' in include and hasattr(sim.net, 'allCells'): net['cells'] = sim.net.allCells
        if 'netPops' in include and hasattr(sim.net, 'allPops'): net['pops'] = sim.net.allPops
        if net: dataSave['net'] = net
        if 'simConfig' in include: dataSave['simConfig'] = sim.cfg.__dict__
        if 'simData' in include:
            if 'LFP' in sim.allSimData:
                sim.allSimData['LFP'] = sim.allSimData['LFP'].tolist()
                if hasattr(sim.net, 'recXElectrode'):
                    dataSave['net']['recXElectrode'] = sim.net.recXElectrode
            dataSave['simData'] = dict(sim.allSimData)

        dataSave = utils.replaceDictODict(dataSave)

        with open(name, 'wb') as fileObj:
            pickle.dump(dataSave, fileObj, protocol=2)

            # clean-up data saved on previous interval
            previous = sim.save._previousIntervalSaveFile
            if previous is not None and os.path.exists(previous):
                os.remove(previous)
            sim.save._previousIntervalSaveFile = name

    sim.pc.barrier()


#------------------------------------------------------------------------------
# Save data in each node
#------------------------------------------------------------------------------
def saveDataInNodes(filename=None, saveLFP=True, removeTraces=False, saveFolder=None):
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

    saveFolder : str
        Name of the directory where data files will be saved.
        **Default:** ``None`` saves to the default directory.

    """

    from .. import sim
    from ..specs import Dict, ODict

    sim.timing('start', 'saveInNodeTime')
    import os


    # flag to avoid saving sections data for each cell (saves gather time and space; cannot inspect cell secs or re-simulate)
    if not sim.cfg.saveCellSecs:
        for cell in sim.net.cells:
            cell.secs = {}
            cell.secLists = None

    # flag to avoid saving conns data for each cell (saves gather time and space; cannot inspect cell conns or re-simulate)
    if not sim.cfg.saveCellConns:
        for cell in sim.net.cells:
            cell.conns = []

    # Store conns in a compact list format instead of a long dict format (cfg.compactConnFormat contains list of keys to include)
    elif sim.cfg.compactConnFormat:
        sim.compactConnFormat()

    # create folder if missing
    if not sim.cfg.simLabel:
        sim.cfg.simLabel = ''

    if not saveFolder: 
        if getattr(sim.cfg, 'saveFolder', None):  # NO saveFolder, YES sim.cfg.saveFolder
            saveFolder = os.path.join(sim.cfg.saveFolder, sim.cfg.simLabel+'_node_data')
        else:
            saveFolder = sim.cfg.simLabel+'_node_data'  # NO saveFolder, NO sim.cfg.saveFolder
    else:
            saveFolder = os.path.join(saveFolder, sim.cfg.simLabel+'_node_data')  # YES saveFolder

    if not os.path.exists(saveFolder):
        os.makedirs(saveFolder, exist_ok=True)

    sim.pc.barrier()
    if sim.rank == 0:
        print('\nSaving an output file for each node in: %s' % (saveFolder))

    # saving data
    dataSave = {}
    net = {}

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

    dataSave['simConfig'] = sim.cfg.__dict__
    dataSave['simData'] = saveSimData
    dataSave['cells'] = [c.__getstate__() for c in sim.net.cells] #sim.net.cells
    dataSave['pops'] = {}
    for popLabel, pop in sim.net.pops.items(): 
        dataSave['pops'][popLabel] = pop.__getstate__()
    dataSave['net'] = {}

    # Remove un-Pickleable hoc objects
    for cell in dataSave['cells']:
        if 'imembPtr' in cell:
            cell.pop('imembPtr')

    if saveLFP:
       if hasattr(sim.net, 'recXElectrode'):
           dataSave['net']['recXElectrode'] = sim.net.recXElectrode

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
            if hasattr(sim.cfg, 'simLabel'):
                filename = sim.cfg.simLabel
            else:
                filename = sim.cfg.filename
        filePath = filename + timestampStr

        # Save to pickle file
        if sim.cfg.savePickle:
            try:
                import pickle
                dataSave = utils.replaceDictODict(dataSave)
                fileName = filePath + '_node_' + str(sim.rank) + '.pkl'
                print(('  Saving output as: %s ... ' % (fileName)))
                with open(os.path.join(saveFolder, fileName), 'wb') as fileObj:
                    pickle.dump(dataSave, fileObj)
            except:
                print('Unable to save Pickle')

        # Save to json file
        if sim.cfg.saveJson:
            fileName = filePath + '_node_' + str(sim.rank) + '.json'
            print(('  Saving output as: %s ... ' % (fileName)))
            sim.saveJSON(os.path.join(saveFolder, fileName), dataSave)

        # Save timing
        sim.pc.barrier()
        if sim.rank == 0:
            if sim.cfg.timing:
                sim.timing('stop', 'saveInNodeTime')
                print(('  Done; saving time = %0.2f s.' % sim.timingData['saveInNodeTime']))
            if sim.cfg.timing and sim.cfg.saveTiming:
                import pickle
                with open('timing.pkl', 'wb') as file: pickle.dump(sim.timing, file)
