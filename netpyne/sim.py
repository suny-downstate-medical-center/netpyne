"""
sim.py 

Contains functions related to the simulation (eg. setupRecording, runSim) 

Contributors: salvadordura@gmail.com
"""

import sys
from time import time
from datetime import datetime
import cPickle as pk
import hashlib 
from neuron import h, init # Import NEURON
import framework as f

###############################################################################
# initialize variables and MPI
###############################################################################

def initialize(netParams = {}, simConfig = {}, net = None):
    f.simData = {}  # used to store output simulation data (spikes etc)
    f.fih = []  # list of func init handlers
    f.rank = 0  # initialize rank
    f.timing = {}  # dict to store timing

    createParallelContext()  # iniitalize PC, nhosts and rank
    
    setSimCfg(simConfig)  # set simulation configuration
    
    if f.rank==0: 
        timing('start', 'initialTime')
        timing('start', 'totalTime')

    if net:
        setNet(f.net)  # set existing external network
    else: 
        setNet(f.Network())  # or create new network

    if netParams: 
        setNetParams(netParams)  # set network parameters

    readArgs()  # read arguments from commandline

    timing('stop', 'initialTime')
    


###############################################################################
# Set network object to use in simulation
###############################################################################
def setNet(net):
    f.net = net

###############################################################################
# Set network params to use in simulation
###############################################################################
def setNetParams(params):
    for paramName, paramValue in f.default.netParams.iteritems():  # set default values
        if paramName not in params:
            params[paramName] = paramValue
    f.net.params = params

###############################################################################
# Set simulation config
###############################################################################
def setSimCfg(cfg):
    for paramName, paramValue in f.default.simConfig.iteritems():  # set default values
        if paramName not in cfg:
            cfg[paramName] = paramValue

    for cell in cfg['plotCells']:  # add all cells of plotCell to recordCells
        if cell not in cfg['recordCells']:
            cfg['recordCells'].append(cell)

    f.cfg = cfg

def loadSimCfg(paramFile):
    pass

def loadSimParams(paramFile):
    pass

###############################################################################
# Create parallel context
###############################################################################
def createParallelContext():
    f.pc = h.ParallelContext() # MPI: Initialize the ParallelContext class
    f.pc.done()
    f.nhosts = int(f.pc.nhost()) # Find number of hosts
    f.rank = int(f.pc.id())     # rank or node number (0 will be the master)

    if f.rank==0: 
        f.pc.gid_clear()

###############################################################################
# Hash function to obtain random value
###############################################################################
def id32(obj): 
    return int(hashlib.md5(obj).hexdigest()[0:8],16)  # convert 8 first chars of md5 hash in base 16 to int


###############################################################################
### Replace item with specific key from dict or list (used to remove h objects)
###############################################################################
def copyReplaceItemObj(obj, keystart, newval, objCopy='ROOT'):
    if type(obj) == list:
        if objCopy=='ROOT': 
            objCopy = []
        for item in obj:
            if type(item) in [list]:
                objCopy.append([])
                copyReplaceItemObj(item, keystart, newval, objCopy[-1])
            elif type(item) in [dict]:
                objCopy.append({})
                copyReplaceItemObj(item, keystart, newval, objCopy[-1])
            else:
                objCopy.append(item)

    elif type(obj) == dict:
        if objCopy == 'ROOT':
            objCopy = {}
        for key,val in obj.iteritems():
            if type(val) in [list]:
                objCopy[key] = [] 
                copyReplaceItemObj(val, keystart, newval, objCopy[key])
            elif type(val) in [dict]:
                objCopy[key] = {}
                copyReplaceItemObj(val, keystart, newval, objCopy[key])
            elif key.startswith(keystart):
                objCopy[key] = newval
            else:
                objCopy[key] = val
    return objCopy

###############################################################################
### Replace item with specific key from dict or list (used to remove h objects)
###############################################################################
def replaceItemObj(obj, keystart, newval):
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


###############################################################################
### Replace functions from dict or list with function string (so can be pickled)
###############################################################################
def replaceFuncObj(obj):
    if type(obj) == list:
        for item in obj:
            if type(item) in [list, dict]:
                replaceFuncObj(item)

    elif type(obj) == dict:
        for key,val in obj.iteritems():
            if type(val) in [list, dict]:
                replaceFuncObj(val)
            if hasattr(val,'func_name'):
                #line = inspect.getsource(val)
                #startInd = line.find('lambda')
                #endInd = min([line[startInd:].find(c) for c in [']', '}', '\n', '\''] if line[startInd:].find(c)>0])
                #funcSource = line[startInd:startInd+endInd]
                obj[key] = 'func' # funcSource
    return obj


###############################################################################
### Replace None from dict or list with [](so can be saved to .mat)
###############################################################################
def replaceNoneObj(obj):
    if type(obj) == list:
        for item in obj:
            if type(item) in [list, dict]:
                replaceNoneObj(item)

    elif type(obj) == dict:
        for key,val in obj.iteritems():
            if type(val) in [list, dict]:
                replaceNoneObj(val)
            if val == None:
                obj[key] = []
            elif val == {}:
                obj[key] = [] # also replace empty dicts with empty list
    return obj

###############################################################################
### Convert dict strings to utf8 so can be saved in HDF5 format
###############################################################################
def dict2utf8(obj):
#unidict = {k.decode('utf8'): v.decode('utf8') for k, v in strdict.items()}
    import collections
    if isinstance(obj, basestring):
        return obj.decode('utf8')
    elif isinstance(obj, collections.Mapping):
        return dict(map(dict2utf8, obj.iteritems()))
    elif isinstance(obj, collections.Iterable):
        return type(obj)(map(dict2utf8, obj))
    else:
        return obj

###############################################################################
### Update model parameters from command-line arguments - UPDATE for sim and f.net f.params
###############################################################################
def readArgs():
    for argv in sys.argv[1:]: # Skip first argument, which is file name
        arg = argv.replace(' ','').split('=') # ignore spaces and find varname and value
        harg = arg[0].split('.')+[''] # Separate out variable name; '' since if split fails need to still have an harg[1]
        if len(arg)==2:
            if hasattr(f.s.params,arg[0]) or hasattr(f.s.params,harg[1]): # Check that variable exists
                if arg[0] == 'outfilestem':
                    exec('s.'+arg[0]+'="'+arg[1]+'"') # Actually set variable 
                    if f.rank==0: # messages only come from Master  
                        print('  Setting %s=%s' %(arg[0],arg[1]))
                else:
                    exec('p.'+argv) # Actually set variable            
                    if f.rank==0: # messages only come from Master  
                        print('  Setting %s=%r' %(arg[0],eval(arg[1])))
            else: 
                sys.tracebacklimit=0
                raise Exception('Reading args from commandline: Variable "%s" not found' % arg[0])
        elif argv=='-mpi':   f.ismpi = True
        else: pass # ignore -python 


###############################################################################
### Setup Recording
###############################################################################
def setupRecording():
    timing('start', 'setrecordTime')
    # set initial v of cells
    f.fih = []
    for cell in f.net.cells:
        f.fih.append(h.FInitializeHandler(cell.initV))

    # spike recording
    f.pc.spike_record(-1, f.simData['spkt'], f.simData['spkid']) # -1 means to record from all cells on this node

    # stim spike recording
    if f.cfg['recordStim']:
        f.simData['stims'] = {}
        for cell in f.net.cells: 
            cell.recordStimSpikes()

    # intrinsic cell variables recording
    if f.cfg['recordCells']:
        for key in f.cfg['recordTraces'].keys(): f.simData[key] = {}  # create dict to store traces
        for entry in f.cfg['recordCells']:  # for each entry in recordCells
            if entry == 'all':  # record all cells
                for cell in f.net.cells: cell.recordTraces()
                break
            elif isinstance(entry, str):  # if str, record 1st cell of this population
                if f.rank == 0:  # only record on node 0
                    for pop in f.net.pops:
                        if pop.tags['popLabel'] == entry and pop.cellGids:
                            gid = pop.cellGids[0]
                            for cell in f.net.cells: 
                                if cell.gid == gid: cell.recordTraces()
            elif isinstance(entry, int):  # if int, record from cell with this gid
                for cell in f.net.cells: 
                    if cell.gid == entry: cell.recordTraces()
    timing('stop', 'setrecordTime')


###############################################################################
### Run Simulation
###############################################################################
def runSim():
    f.pc.barrier()
    timing('start', 'runTime')
    if f.rank == 0:
        print('\nRunning...')
        runstart = time() # See how long the run takes
    h.dt = f.cfg['dt']
    f.pc.set_maxstep(10)
    mindelay = f.pc.allreduce(f.pc.set_maxstep(10), 2) # flag 2 returns minimum value
    if f.rank==0 and f.cfg['verbose']: print 'Minimum delay (time-step for queue exchange) is ',mindelay
    
    # reset all netstims so runs are always equivalent
    for cell in f.net.cells:
        for stim in cell.stims:
            if 'hRandom' in stim:
                stim['hRandom'].Random123(cell.gid, f.sim.id32('%d'%(f.cfg['seeds']['stim'])))
                stim['hRandom'].negexp(1)

    init()
    f.pc.psolve(f.cfg['duration'])
    if f.rank==0: 
        runtime = time()-runstart # See how long it took
        print('  Done; run time = %0.2f s; real-time ratio: %0.2f.' % (runtime, f.cfg['duration']/1000/runtime))
    f.pc.barrier() # Wait for all hosts to get to this point
    timing('stop', 'runTime')


###############################################################################
### Run Simulation
###############################################################################
def runSimWithIntervalFunc(interval, func):
    f.pc.barrier()
    timing('start', 'runTime')
    if f.rank == 0:
        print('\nRunning...')
        runstart = time() # See how long the run takes
    h.dt = f.cfg['dt']
    f.pc.set_maxstep(10)
    mindelay = f.pc.allreduce(f.pc.set_maxstep(10), 2) # flag 2 returns minimum value
    if f.rank==0 and f.cfg['verbose']: print 'Minimum delay (time-step for queue exchange) is ',mindelay
    
    # reset all netstims so runs are always equivalent
    for cell in f.net.cells:
        for stim in cell.stims:
            stim['hRandom'].Random123(cell.gid, f.sim.id32('%d'%(f.cfg['seeds']['stim'])))
            stim['hRandom'].negexp(1)

    init()

    #progUpdate = 1000  # update every second
    while round(h.t) < f.cfg['duration']:
        f.pc.psolve(min(f.cfg['duration'], h.t+interval))
        #if f.cfg['verbose'] and (round(h.t) % progUpdate):
            #print(' Sim time: %0.1f s (%d %%)' % (h.t/1e3, int(h.t/f.cfg['duration']*100)))
        func(h.t) # function to be called at intervals

    if f.rank==0: 
        runtime = time()-runstart # See how long it took
        print('  Done; run time = %0.2f s; real-time ratio: %0.2f.' % (runtime, f.cfg['duration']/1000/runtime))
    f.pc.barrier() # Wait for all hosts to get to this point
    timing('stop', 'runTime')
                


###############################################################################
### Gather tags from cells
###############################################################################
def gatherAllCellTags():
    data = [{cell.gid: cell.tags for cell in f.net.cells}]*f.nhosts  # send cells data to other nodes
    gather = f.pc.py_alltoall(data)  # collect cells data from other nodes (required to generate connections)
    f.pc.barrier()
    allCellTags = {}
    for dataNode in gather:         
        allCellTags.update(dataNode)
    del gather, data  # removed unnecesary variables
    return allCellTags



###############################################################################
### Gather data from nodes
###############################################################################
def gatherData():
    timing('start', 'gatherTime')
    ## Pack data from all hosts
    if f.rank==0: 
        print('\nGathering spikes...')

    simDataVecs = ['spkt','spkid','stims']+f.cfg['recordTraces'].keys()
    if f.nhosts > 1:  # only gather if >1 nodes 
        nodeData = {'netCells': [c.__getstate__() for c in f.net.cells], 'simData': f.simData} 
        data = [None]*f.nhosts
        data[0] = {}
        for k,v in nodeData.iteritems():
            data[0][k] = v 
        gather = f.pc.py_alltoall(data)
        f.pc.barrier()  
        if f.rank == 0:
            allCells = []
            f.allSimData = {} 
            for k in gather[0]['simData'].keys():  # initialize all keys of allSimData dict
                f.allSimData[k] = {}
            # fill in allSimData taking into account if data is dict of h.Vector (code needs improvement to be more generic)
            for node in gather:  # concatenate data from each node
                allCells.extend(node['netCells'])  # extend allCells list
                for key,val in node['simData'].iteritems():  # update simData dics of dics of h.Vector 
                    if key in simDataVecs:          # simData dicts that contain Vectors
                        if isinstance(val,dict):                
                            for cell,val2 in val.iteritems():
                                if isinstance(val2,dict):       
                                    f.allSimData[key].update({cell:{}})
                                    for stim,val3 in val2.iteritems():
                                        f.allSimData[key][cell].update({stim:list(val3)}) # udpate simData dicts which are dicts of dicts of Vectors (eg. ['stim']['cell_1']['backgrounsd']=h.Vector)
                                else:
                                    f.allSimData[key].update({cell:list(val2)})  # udpate simData dicts which are dicts of Vectors (eg. ['v']['cell_1']=h.Vector)
                        else:                                   
                            f.allSimData[key] = list(f.allSimData[key])+list(val) # udpate simData dicts which are Vectors
                    else: 
                        f.allSimData[key].update(val)           # update simData dicts which are not Vectors
            f.net.allCells = allCells
    
    else:  # if single node, save data in same format as for multiple nodes for consistency
        f.net.allCells = [c.__getstate__() for c in f.net.cells]
        #f.allSimData = f.simData
        f.allSimData = {} 
        for k in f.simData.keys():  # initialize all keys of allSimData dict
                f.allSimData[k] = {}
        for key,val in f.simData.iteritems():  # update simData dics of dics of h.Vector 
                if key in simDataVecs:          # simData dicts that contain Vectors
                    if isinstance(val,dict):                
                        for cell,val2 in val.iteritems():
                            if isinstance(val2,dict):       
                                f.allSimData[key].update({cell:{}})
                                for stim,val3 in val2.iteritems():
                                    f.allSimData[key][cell].update({stim:list(val3)}) # udpate simData dicts which are dicts of dicts of Vectors (eg. ['stim']['cell_1']['backgrounsd']=h.Vector)
                            else:
                                f.allSimData[key].update({cell:list(val2)})  # udpate simData dicts which are dicts of Vectors (eg. ['v']['cell_1']=h.Vector)
                    else:                                   
                        f.allSimData[key] = list(f.allSimData[key])+list(val) # udpate simData dicts which are Vectors
                else: 
                    f.allSimData[key].update(val)           # update simData dicts which are not Vectors

    ## Print statistics
    if f.rank == 0:
        timing('stop', 'gatherTime')
        if f.cfg['timing']: print('  Done; gather time = %0.2f s.' % f.timing['gatherTime'])

        print('\nAnalyzing...')
        f.totalSpikes = len(f.allSimData['spkt'])   
        f.totalConnections = sum([len(cell['conns']) for cell in f.net.allCells])   
        f.numCells = len(f.net.allCells)

        f.firingRate = float(f.totalSpikes)/f.numCells/f.cfg['duration']*1e3 # Calculate firing rate 
        f.connsPerCell = f.totalConnections/float(f.numCells) # Calculate the number of connections per cell
        if f.cfg['timing']: print('  Run time: %0.2f s' % (f.timing['runTime']))
        print('  Simulated time: %i-s; %i cells; %i workers' % (f.cfg['duration']/1e3, f.numCells, f.nhosts))
        print('  Spikes: %i (%0.2f Hz)' % (f.totalSpikes, f.firingRate))
        print('  Connections: %i (%0.2f per cell)' % (f.totalConnections, f.connsPerCell))

 

###############################################################################
### Save data
###############################################################################
def saveData():
    if f.rank == 0:
        timing('start', 'saveTime')
        dataSave = {'netParams': replaceFuncObj(f.net.params), 'simConfig': f.cfg, 'simData': f.allSimData, 'netCells': f.net.allCells}

        #dataSave = {'netParams': replaceFuncObj(f.net.params), 'simConfig': f.cfg,  'netCells': f.net.allCells}


        if 'timestampFilename' in f.cfg:  # add timestamp to filename
            if f.cfg['timestampFilename']: 
                timestamp = time()
                timestampStr = datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S')
                f.cfg['filename'] = f.cfg['filename']+'-'+timestampStr

        # Save to pickle file
        if f.cfg['savePickle']:
            import pickle
            print('Saving output as %s ... ' % (f.cfg['filename']+'.pkl'))
            with open(f.cfg['filename']+'.pkl', 'wb') as fileObj:
                pickle.dump(dataSave, fileObj)
            print('Finished saving!')

        # Save to dpk file
        if f.cfg['saveDpk']:
            import gzip
            print('Saving output as %s ... ' % (f.cfg['filename']+'.dpk'))
            fn=f.cfg['filename'] #.split('.')
            gzip.open(fn, 'wb').write(pk.dumps(dataSave)) # write compressed string
            print('Finished saving!')

        # Save to json file
        if f.cfg['saveJson']:
            import json
            print('Saving output as %s ... ' % (f.cfg['filename']+'.json '))
            with open(f.cfg['filename']+'.json', 'w') as fileObj:
                json.dump(dataSave, fileObj)
            print('Finished saving!')

        # Save to mat file
        if f.cfg['saveMat']:
            from scipy.io import savemat 
            print('Saving output as %s ... ' % (f.cfg['filename']+'.mat'))
            savemat(f.cfg['filename']+'.mat', replaceNoneObj(dataSave))  # replace None and {} with [] so can save in .mat format
            print('Finished saving!')

        # Save to HDF5 file (uses very inefficient hdf5storage module which supports dicts)
        if f.cfg['saveHDF5']:
            dataSaveUTF8 = dict2utf8(replaceNoneObj(dataSave)) # replace None and {} with [], and convert to utf
            import hdf5storage
            print('Saving output as %s... ' % (f.cfg['filename']+'.hdf5'))
            hdf5storage.writes(dataSaveUTF8, filename=f.cfg['filename']+'.hdf5')
            print('Finished saving!')

        # Save to CSV file (currently only saves spikes)
        if f.cfg['saveCSV']:
            import csv
            print('Saving output as %s ... ' % (f.cfg['filename']+'.csv'))
            writer = csv.writer(open(f.cfg['filename']+'.csv', 'wb'))
            for dic in dataSave['simData']:
                for values in dic:
                    writer.writerow(values)
            print('Finished saving!')

        # Save to Dat file(s) 
        if f.cfg['saveDat']:
            traces = f.cfg['recordTraces']
            for ref in traces.keys():
                for cellid in f.allSimData[ref].keys():
                    dat_file_name = '%s_%s.dat'%(ref,cellid)
                    dat_file = open(dat_file_name, 'w')
                    trace = f.allSimData[ref][cellid]
                    print("Saving %i points of data on: %s:%s to %s"%(len(trace),ref,cellid,dat_file_name))
                    for i in range(len(trace)):
                        dat_file.write('%s\t%s\n'%((i*f.cfg['dt']/1000),trace[i]/1000))

            print('Finished saving!')


        # Save timing
        timing('stop', 'saveTime')
        if f.cfg['timing'] and f.cfg['saveTiming']: 
            import pickle
            with open('timing.pkl', 'wb') as file: pickle.dump(f.timing, file)

###############################################################################
### Timing - Stop Watch
###############################################################################
def timing(mode, processName):
    if f.rank == 0 and f.cfg['timing']:
        if mode == 'start':
            f.timing[processName] = time() 
        elif mode == 'stop':
            f.timing[processName] = time() - f.timing[processName]
            

###############################################################################
### Get connection centric network representation as used in NeuroML2
###############################################################################  
def _convertNetworkRepresentation(net, gids_vs_pop_indices):

    nn = {}

    for np_pop in net.pops: 
        print("Adding conns for: %s"%np_pop.tags)
        if not np_pop.tags['cellModel'] ==  'NetStim':
            for cell in net.cells:
                if cell.gid in np_pop.cellGids:
                    popPost, indexPost = gids_vs_pop_indices[cell.gid]
                    print("Cell %s: %s\n    %s[%i]\n"%(cell.gid,cell.tags,popPost, indexPost))
                    for conn in cell.conns:
                        preGid = conn['preGid']
                        popPre, indexPre = gids_vs_pop_indices[preGid]
                        loc = conn['loc']
                        weight = conn['weight']
                        delay = conn['delay']
                        sec = conn['sec']
                        synMech = conn['synMech']
                        threshold = conn['threshold']

                        print("      Conn %s[%i]->%s[%i] with %s"%(popPre, indexPre,popPost, indexPost, synMech))

                        projection_info = (popPre,popPost,synMech)
                        if not projection_info in nn.keys():
                            nn[projection_info] = []

                        nn[projection_info].append({'indexPre':indexPre,'indexPost':indexPost,'weight':weight,'delay':delay})
    return nn                 


###############################################################################
### Get stimulations in representation as used in NeuroML2
###############################################################################  
def _convertStimulationRepresentation(net,gids_vs_pop_indices, nml_doc):

    stims = {}

    for np_pop in net.pops: 
        if not np_pop.tags['cellModel'] ==  'NetStim':
            print("Adding stims for: %s"%np_pop.tags)
            for cell in net.cells:
                if cell.gid in np_pop.cellGids:
                    pop, index = gids_vs_pop_indices[cell.gid]
                    print("    Cell %s: %s\n    %s[%i]\n    %s\n"%(cell.gid,cell.tags,pop, index,cell.stims))
                    for stim in cell.stims:
                        '''
                        [{'noise': 0, 'weight': 0.1, 'popLabel': 'background', 'number': 1000000000000.0, 'rate': 10, 
                        'sec': 'soma', 'synMech': 'NMDA', 'threshold': 10.0, 'weightIndex': 0, 'loc': 0.5, 
                        'hRandom': <hoc.HocObject object at 0x7fda27f1fd20>, 'hNetcon': <hoc.HocObject object at 0x7fda27f1fdb0>, 
                        'hNetStim': <hoc.HocObject object at 0x7fda27f1fd68>, 'delay': 0, 'source': 'random'}]'''
                        ref = stim['popLabel']
                        rate = stim['rate']
                        synMech = stim['synMech']
                        threshold = stim['threshold']
                        delay = stim['delay']
                        weight = stim['weight']
                        noise = stim['noise']

                        name_stim = 'NetStim_%s_%s_%s_%s_%s'%(ref,pop,rate,noise,synMech)

                        stim_info = (name_stim, pop, rate, noise,synMech)
                        if not stim_info in stims.keys():
                            stims[stim_info] = []


                        stims[stim_info].append({'index':index,'weight':weight,'delay':delay,'threshold':threshold})   

    print stims             
    return stims


###############################################################################
### Export synapses to NeuroML2
############################################################################### 
def _export_synapses(net, nml_doc):

    import neuroml

    for syn in net.params['synMechParams']:

        print('Exporting details of syn: %s'%syn)
        if syn['mod'] == 'Exp2Syn':
            syn0 = neuroml.ExpTwoSynapse(id=syn['label'], 
                                         gbase='1uS',
                                         erev='%smV'%syn['e'],
                                         tau_rise='%sms'%syn['tau1'],
                                         tau_decay='%sms'%syn['tau2'])

            nml_doc.exp_two_synapses.append(syn0)
        elif syn['mod'] == 'ExpSyn':
            syn0 = neuroml.ExpOneSynapse(id=syn['label'], 
                                         gbase='1uS',
                                         erev='%smV'%syn['e'],
                                         tau_decay='%sms'%syn['tau'])

            nml_doc.exp_one_synapses.append(syn0)
        else:
            raise Exception("Cannot yet export synapse type: %s"%syn['mod'])



###############################################################################
### Export generated structure of network to NeuroML 2 
###############################################################################         
def exportNeuroML2(reference, connections=True, stimulations=True):

    net = f.net
    
    print("Exporting network to NeuroML 2, reference: %s"%reference)
    # Only import libNeuroML if this method is called...
    import neuroml
    import neuroml.writers as writers

    nml_doc = neuroml.NeuroMLDocument(id='%s'%reference)
    nml_net = neuroml.Network(id='%s'%reference)
    nml_doc.networks.append(nml_net)

    nml_doc.notes = 'NeuroML 2 file exported from NetPyNE'

    gids_vs_pop_indices ={}
    populations_vs_components = {}

    for np_pop in net.pops: 
        index = 0
        print("Adding: %s"%np_pop.tags)
        positioned = len(np_pop.cellGids)>0
        type = 'populationList'
        if not np_pop.tags['cellModel'] ==  'NetStim':
            pop = neuroml.Population(id=np_pop.tags['popLabel'],component=np_pop.tags['cellModel'], type=type)
            populations_vs_components[pop.id]=pop.component
            nml_net.populations.append(pop)
            nml_doc.includes.append(neuroml.IncludeType('%s.cell.nml'%np_pop.tags['cellModel']))

            for cell in net.cells:
                if cell.gid in np_pop.cellGids:
                    gids_vs_pop_indices[cell.gid] = (np_pop.tags['popLabel'],index)
                    inst = neuroml.Instance(id=index)
                    index+=1
                    pop.instances.append(inst)
                    inst.location = neuroml.Location(cell.tags['x'],cell.tags['y'],cell.tags['z'])

    _export_synapses(net, nml_doc)

    if connections:
        nn = _convertNetworkRepresentation(net, gids_vs_pop_indices)

        for proj_info in nn.keys():

            prefix = "NetConn"
            popPre,popPost,synMech = proj_info

            projection = neuroml.Projection(id="%s_%s_%s_%s"%(prefix,popPre, popPost,synMech), 
                              presynaptic_population=popPre, 
                              postsynaptic_population=popPost, 
                              synapse=synMech)
            index = 0      
            for conn in nn[proj_info]:

                connection = neuroml.ConnectionWD(id=index, \
                            pre_cell_id="../%s/%i/%s"%(popPre, conn['indexPre'], populations_vs_components[popPre]), \
                            pre_segment_id=0, \
                            pre_fraction_along=0.5,
                            post_cell_id="../%s/%i/%s"%(popPost, conn['indexPost'], populations_vs_components[popPost]), \
                            post_segment_id=0,
                            post_fraction_along=0.5,
                            delay = '%s ms'%conn['delay'],
                            weight = conn['weight'])
                index+=1

                projection.connection_wds.append(connection)

            nml_net.projections.append(projection)

    if stimulations:
        stims = _convertStimulationRepresentation(net, gids_vs_pop_indices, nml_doc)

        for stim_info in stims.keys():
            name_stim, post_pop, rate, noise, synMech = stim_info

            print("Adding stim: %s"%[stim_info])

            if noise==0:
                source = neuroml.SpikeGenerator(id=name_stim,period="%ss"%(1./rate))
                nml_doc.spike_generators.append(source)
            elif noise==1:
                source = neuroml.SpikeGeneratorPoisson(id=name_stim,average_rate="%s Hz"%(rate))
                nml_doc.spike_generator_poissons.append(source)
            else:
                raise Exception("Noise = %s is not yet supported!"%noise)


            stim_pop = neuroml.Population(id='Pop_%s'%name_stim,component=source.id,size=len(stims[stim_info]))
            nml_net.populations.append(stim_pop)


            proj = neuroml.Projection(id="NetConn_%s__%s"%(name_stim, post_pop), 
                  presynaptic_population=stim_pop.id, 
                  postsynaptic_population=post_pop, 
                  synapse=synMech)

            nml_net.projections.append(proj)

            count = 0
            for stim in stims[stim_info]:
                print("  Adding stim: %s"%stim)

                connection = neuroml.ConnectionWD(id=count, \
                        pre_cell_id="../%s[%i]"%(stim_pop.id, stim['index']), \
                        pre_segment_id=0, \
                        pre_fraction_along=0.5,
                        post_cell_id="../%s/%i/%s"%(post_pop, stim['index'], populations_vs_components[post_pop]), \
                        post_segment_id=0,
                        post_fraction_along=0.5,
                        delay = '%s ms'%stim['delay'],
                        weight = stim['weight'])
                count+=1

                proj.connection_wds.append(connection)


    nml_file_name = '%s.net.nml'%reference

    writers.NeuroMLWriter.write(nml_doc, nml_file_name)

    '''
    from pyneuroml.lems import LEMSSimulation

    ls = LEMSSimulation('Sim_%s'%reference, f.cfg['dt'],f.cfg['duration'],reference)

    ls.include_neuroml2_file(nml_file_name)'''

    import pyneuroml.lems

    pyneuroml.lems.generate_lems_file_for_neuroml("Sim_%s"%reference, 
                               nml_file_name, 
                               reference, 
                               f.cfg['duration'], 
                               f.cfg['dt'], 
                               'LEMS_%s.xml'%reference,
                               '.',
                               copy_neuroml = False,
                               include_extra_files = [],
                               gen_plots_for_all_v = False,
                               gen_plots_for_only_populations = populations_vs_components.keys(),
                               gen_saves_for_all_v = False,
                               plot_all_segments = False, 
                               gen_saves_for_only_populations = populations_vs_components.keys(),
                               save_all_segments = False,
                               seed=1234)






