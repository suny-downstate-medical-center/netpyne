"""
sim/save.py

Functions related to saving 

Contributors: salvadordura@gmail.com
"""

from time import time
from datetime import datetime
import pickle as pk
from . import gather
from . import utils

#------------------------------------------------------------------------------
# Save data
#------------------------------------------------------------------------------
def saveData (include = None, filename = None):
    from .. import sim

    if sim.rank == 0 and not getattr(sim.net, 'allCells', None): needGather = True
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
                timestampStr = '-' + datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S')
            else:
                timestampStr = ''
            
            filePath = sim.cfg.filename + timestampStr
            # Save to pickle file
            if sim.cfg.savePickle:
                import pickle
                dataSave = utils.replaceDictODict(dataSave)
                print(('Saving output as %s ... ' % (filePath+'.pkl')))
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
                import json
                #dataSave = utils.replaceDictODict(dataSave)  # not required since json saves as dict
                print(('Saving output as %s ... ' % (filePath+'.json ')))
                with open(filePath+'.json', 'w') as fileObj:
                    json.dump(dataSave, fileObj)
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
def intervalSave (t):
    from .. import sim
    from ..specs import Dict
    import pickle
    
    sim.pc.barrier()    
    
    gatherLFP=True
    simDataVecs = ['spkt','spkid','stims']+list(sim.cfg.recordTraces.keys())
    singleNodeVecs = ['t']
        
    netPopsCellGids = {popLabel: list(pop.cellGids) for popLabel,pop in sim.net.pops.items()}

    # gather only sim data
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
            sim.allSimData['spkt'], sim.allSimData['spkid'] = zip(*sorted(zip(sim.allSimData['spkt'], sim.allSimData['spkid']))) # sort spks
            sim.allSimData['spkt'], sim.allSimData['spkid'] = list(sim.allSimData['spkt']), list(sim.allSimData['spkid'])

        name = 'temp/data_{:4.0f}.pkl'.format(t)
        with open(name, 'wb') as f:
            pickle.dump(sim.allSimData, f, protocol=2)

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

