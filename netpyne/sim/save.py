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





 