"""
simFunc.py 

Contains functions related to the simulation (eg. setupRecording, runSim) 

Contributors: salvadordura@gmail.com
"""

__all__ = []
__all__.extend(['initialize', 'setNet', 'setNetParams', 'setSimCfg', 'createParallelContext', 'setupRecording']) # init and setup
__all__.extend(['runSim', 'runSimWithIntervalFunc', '_gatherAllCellTags', '_gatherCells', 'gatherData'])  # run and gather
__all__.extend(['saveData', 'loadSimCfg', 'loadNetParams', 'loadNet', 'loadSimData', 'loadAll']) # saving and loading
__all__.extend(['exportNeuroML2'])  # export/import
__all__.extend(['popAvgRates', 'id32', 'copyReplaceItemObj', 'replaceNoneObj', 'replaceFuncObj', 'readArgs', 'getCellsList', 'cellByGid',\
'timing',  'version', 'gitversion'])  # misc/utilities

import sys
from time import time
from datetime import datetime
import cPickle as pk
import hashlib 
from numbers import Number
from copy import copy
#from collections import OrderedDict
from specs import Dict, ODict
from neuron import h, init # Import NEURON

import sim, specs


###############################################################################
# initialize variables and MPI
###############################################################################
def initialize (netParams = {}, simConfig = {}, net = None):
    if hasattr(simConfig, 'popParams') or hasattr(netParams, 'duration'):
        print 'Error: seems like the sim.initialize() arguments are in the wrong order, try initialize(netParams, simConfig)'
        sys.exit()

    sim.simData = Dict()  # used to store output simulation data (spikes etc)
    sim.fih = []  # list of func init handlers
    sim.rank = 0  # initialize rank
    sim.timingData = Dict()  # dict to store timing

    sim.createParallelContext()  # iniitalize PC, nhosts and rank
    
    sim.setSimCfg(simConfig)  # set simulation configuration
    
    if sim.rank==0: 
        sim.timing('start', 'initialTime')
        sim.timing('start', 'totalTime')

    if net:
        sim.setNet(net)  # set existing external network
    else: 
        sim.setNet(sim.Network())  # or create new network

    if netParams: 
        sim.setNetParams(netParams)  # set network parameters

    #sim.readArgs()  # read arguments from commandline

    sim.timing('stop', 'initialTime')


###############################################################################
# Set network object to use in simulation
###############################################################################
def setNet (net):
    sim.net = net

###############################################################################
# Set network params to use in simulation
###############################################################################
def setNetParams (params):
    if params and isinstance(params, specs.NetParams):
        sim.net.params = params
    elif params and isinstance(params, dict):
        sim.net.params = specs.NetParams(params)
    else:
        sim.net.params = specs.NetParams()

###############################################################################
# Set simulation config
###############################################################################
def setSimCfg (cfg):
    if cfg and isinstance(cfg, specs.SimConfig):
        sim.cfg = cfg  # set 
    elif cfg and isinstance(cfg, dict):
        sim.cfg = specs.SimConfig(cfg) # fill in with dict
    else:
        sim.cfg = specs.SimConfig()  # create new object


###############################################################################
# Create parallel context
###############################################################################
def createParallelContext ():
    sim.pc = h.ParallelContext() # MPI: Initialize the ParallelContext class
    sim.pc.done()
    sim.nhosts = int(sim.pc.nhost()) # Find number of hosts
    sim.rank = int(sim.pc.id())     # rank or node number (0 will be the master)

    if sim.rank==0: 
        sim.pc.gid_clear()


###############################################################################
# Load netParams from cell
###############################################################################
def loadNetParams (filename, data=None):
    if not data: data = _loadFile(filename)
    print 'Loading netParams...'
    if 'net' in data and 'params' in data['net']:
        setNetParams(data['net']['params'])
    else:
        print 'netParams not found in file %s'%(filename)

    pass


###############################################################################
# Load cells and pops from file and create NEURON objs
###############################################################################
def loadNet (filename, data=None, instantiate=True):
    if not data: data = _loadFile(filename)
    if 'net' in data and 'cells' in data['net'] and 'pops' in data['net']:
        sim.timing('start', 'loadNetTime')
        print 'Loading net...'
        sim.net.allPops = data['net']['pops']
        sim.net.allCells = data['net']['cells']
        if instantiate:
            if sim.cfg.createPyStruct:
                for popLoadLabel, popLoad in data['net']['pops'].iteritems():
                    pop = sim.Pop(popLoadLabel, popLoad['tags'])
                    pop.cellGids = popLoad['cellGids']
                    sim.net.pops[popLoadLabel] = pop
                for cellLoad in data['net']['cells']:
                    # create new Cell object and add attributes, but don't create sections or associate gid yet
                    cell = sim.Cell(gid=cellLoad['gid'], tags=cellLoad['tags'], create=False, associateGid=False)  
                    cell.secs = cellLoad['secs']
                    cell.conns = cellLoad['conns']
                    cell.stims = cellLoad['stims']
                    sim.net.cells.append(cell)
                print '  Created %d cells' % (len(data['net']['cells']))

                # only create NEURON objs, if there is Python struc (fix so minimal Python struct is created)
                if sim.cfg.createNEURONObj:  
                    if sim.cfg.verbose: print "  Adding NEURON objects..."
                    # create NEURON sections, mechs, syns, etc; and associate gid
                    for cell in sim.net.cells:
                        prop = {'secs': cell.secs}
                        cell.createNEURONObj(prop)  # use same syntax as when creating based on high-level specs 
                        cell.associateGid()  # can only associate once the hSection obj has been created
                    # create all NEURON Netcons, NetStims, etc
                    for cell in sim.net.cells:
                        cell.addStimsNEURONObj()  # add stims first so can then create conns between netstims
                        cell.addConnsNEURONObj()

                    print '  Added NEURON objects to %d cells' % (len(sim.net.cells))

            if sim.cfg.timing: sim.timing('stop', 'loadNetTime')
            print('  Done; re-instantiate net time = %0.2f s' % sim.timingData['loadNetTime'])
    else:
        print '  netCells and/or netPops not found in file %s'%(filename)


###############################################################################
# Load simulation config from file
###############################################################################
def loadSimCfg (filename, data=None):
    if not data: data = _loadFile(filename)
    print 'Loading simConfig...'
    if 'simConfig' in data:
        setSimCfg(data['simConfig'])
    else:
        print '  simConfig not found in file %s'%(filename)

    pass


###############################################################################
# Load netParams from cell
###############################################################################
def loadSimData (filename, data=None):
    if not data: data = _loadFile(filename)
    print 'Loading simData...'
    if 'simData' in data:
        sim.allSimData = data['simData']
    else:
        print '  simData not found in file %s'%(filename)

    pass


###############################################################################
# Load all data in file
###############################################################################
def loadAll (filename, data=None):
    if not data: data = _loadFile(filename)
    loadSimCfg(filename, data=data)
    loadNetParams(filename, data=data)
    loadNet(filename, data=data)
    loadSimData(filename, data=data)

    
###############################################################################
# Load data from file
###############################################################################
def _loadFile (filename):
    
    if sim.cfg.timing: sim.timing('start', 'loadFileTime')
    ext = filename.split('.')[1]

    # load pickle file
    if ext == 'pkl':
        import pickle
        print('Loading file %s ... ' % (filename))
        with open(filename, 'r') as fileObj:
            data = pickle.load(fileObj)

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
        #with open(sim.cfg.filename+'.json', 'w') as fileObj:
        #    json.dump(dataSave, fileObj)
        print('NOT IMPLEMENTED!')

    # load mat file
    elif ext == 'mat':
        from scipy.io import savemat 
        print('Loading file %s ... ' % (filename))
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
        print 'Format not recognized for file %s'%(filename)
        return 

    if sim.cfg.timing: sim.timing('stop', 'loadFileTime')
    print('  Done; file loading time = %0.2f s' % sim.timingData['loadFileTime'])
   

    return data


###############################################################################
# Hash function to obtain random value
###############################################################################
def id32 (obj): 
    return int(hashlib.md5(obj).hexdigest()[0:8],16)  # convert 8 first chars of md5 hash in base 16 to int


###############################################################################
### Replace item with specific key from dict or list (used to remove h objects)
###############################################################################
def copyReplaceItemObj (obj, keystart, newval, objCopy='ROOT'):
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
def _replaceItemObj (obj, keystart, newval):
    if type(obj) == list:
        for item in obj:
            if type(item) in [list, dict]:
                _replaceItemObj(item, keystart, newval)

    elif type(obj) == dict:
        for key,val in obj.iteritems():
            if type(val) in [list, dict]:
                _replaceItemObj(val, keystart, newval)
            if key.startswith(keystart):
                obj[key] = newval
    return obj


###############################################################################
### Replace functions from dict or list with function string (so can be pickled)
###############################################################################
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
                #line = inspect.getsource(val)
                #startInd = line.find('lambda')
                #endInd = min([line[startInd:].find(c) for c in [']', '}', '\n', '\''] if line[startInd:].find(c)>0])
                #funcSource = line[startInd:startInd+endInd]
                obj[key] = 'func' # funcSource
    return obj


###############################################################################
### Replace None from dict or list with [](so can be saved to .mat)
###############################################################################
def replaceNoneObj (obj):
    if type(obj) == list:# or type(obj) == tuple:
        for item in obj:
            if type(item) in [list, dict]:#, tuple]:
                replaceNoneObj(item)

    elif type(obj) == dict or type(obj) == ODict:
        for key,val in obj.iteritems():
            if type(val) in [list, dict, ODict]:
                replaceNoneObj(val)
            if val == None:
                obj[key] = []
            elif val == {}:
                obj[key] = [] # also replace empty dicts with empty list
    return obj


###############################################################################
### Replace None from dict or list with [](so can be saved to .mat)
###############################################################################
def tupleToStr (obj):
    if type(obj) == list:
        for item in obj:
            if type(item) in [list, dict]:
                tupleToStr(item)
            elif type(item) == tuple:
                obj[obj.index(item)] = str(item)

    elif type(obj) == dict or type(obj) == ODict:
        for key,val in obj.iteritems():
            if type(val) in [list, dict, ODict]:
                tupleToStr(val)
            elif type(val) == tuple:
                obj[key] = str(val) # also replace empty dicts with empty list
    return obj


###############################################################################
### Convert dict strings to utf8 so can be saved in HDF5 format
###############################################################################
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


###############################################################################
### Convert dict strings to utf8 so can be saved in HDF5 format
###############################################################################
def cellByGid(gid):
    cell = next((c for c in sim.net.cells if c.gid==gid), None)
    return cell


###############################################################################
### Update model parameters from command-line arguments - UPDATE for sim and sim.net sim.params
###############################################################################
def readArgs ():
    for argv in sys.argv[1:]: # Skip first argument, which is file name
        arg = argv.replace(' ','').split('=') # ignore spaces and find varname and value
        harg = arg[0].split('.')+[''] # Separate out variable name; '' since if split fails need to still have an harg[1]
        if len(arg)==2:
            if hasattr(sim.net.params,arg[0]) or hasattr(sim.s.params,harg[1]): # Check that variable exists
                if arg[0] == 'outfilestem':
                    exec('s.'+arg[0]+'="'+arg[1]+'"') # Actually set variable 
                    if sim.rank==0: # messages only come from Master  
                        print('  Setting %s=%s' %(arg[0],arg[1]))
                else:
                    exec('p.'+argv) # Actually set variable            
                    if sim.rank==0: # messages only come from Master  
                        print('  Setting %s=%r' %(arg[0],eval(arg[1])))
            else: 
                sys.tracebacklimit=0
                raise Exception('Reading args from commandline: Variable "%s" not found' % arg[0])
        elif argv=='-mpi':   sim.ismpi = True
        else: pass # ignore -python 


###############################################################################
### Setup Recording
###############################################################################
def setupRecording ():
    timing('start', 'setrecordTime')
    # set initial v of cells
    sim.fih = []
    for cell in sim.net.cells:
        sim.fih.append(h.FInitializeHandler(cell.initV))

    # spike recording
    sim.simData.update({name:h.Vector(1e4).resize(0) for name in ['spkt','spkid']})  # initialize
    sim.pc.spike_record(-1, sim.simData['spkt'], sim.simData['spkid']) # -1 means to record from all cells on this node

    # stim spike recording
    if 'plotRaster' in sim.cfg.analysis:
        if isinstance(sim.cfg.analysis['plotRaster'],dict) and 'include' in sim.cfg.analysis['plotRaster']:
            netStimPops = [popLabel for popLabel,pop in sim.net.pops.iteritems() if pop.tags['cellModel']=='NetStim']+['allNetStims']
            for item in sim.cfg.analysis['plotRaster']['include']:
                if item in netStimPops: 
                    sim.cfg.recordStim = True
                    break

    if 'plotSpikeHist' in sim.cfg.analysis:
        if sim.cfg.analysis['plotSpikeHist']==True:
            sim.cfg.recordStim = True

        elif (isinstance(sim.cfg.analysis['plotSpikeHist'],dict) and 'include' in sim.cfg.analysis['plotSpikeHist']) :
            netStimPops = [popLabel for popLabel,pop in sim.net.pops.iteritems() if pop.tags['cellModel']=='NetStim']+['allNetStims', 'eachPop']
            for item in sim.cfg.analysis['plotSpikeHist']['include']:
                if item in netStimPops: 
                    sim.cfg.recordStim = True
                    break
                  
    if sim.cfg.recordStim:
        sim.simData['stims'] = Dict()
        for cell in sim.net.cells: 
            cell.recordStimSpikes()

    # intrinsic cell variables recording
    if sim.cfg.recordTraces:
        # get list of cells from argument of plotTraces function
        if 'plotTraces' in sim.cfg.analysis and 'include' in sim.cfg.analysis['plotTraces']:
            cellsPlot = getCellsList(sim.cfg.analysis['plotTraces']['include'])
        else:
            cellsPlot = [] 

        # get actual cell objects to record from, both from recordCell and plotCell lists
        cellsRecord = getCellsList(sim.cfg.recordCells)+cellsPlot

        for key in sim.cfg.recordTraces.keys(): sim.simData[key] = Dict()  # create dict to store traces
        for cell in cellsRecord: cell.recordTraces()  # call recordTraces function for each cell
    
    timing('stop', 'setrecordTime')

    return sim.simData


###############################################################################
### Get cells list for recording based on set of conditions
###############################################################################
def getCellsList(include):
    allCells = sim.net.cells
    cellGids = []
    cells = []
    for condition in include:
        if condition == 'all':  # all cells + Netstims 
            cellGids = [c.gid for c in allCells]
            cells = list(allCells)
            return cells

        elif condition == 'allCells':  # all cells 
            cellGids = [c.gid for c in allCells]
            cells = list(allCells)

        elif isinstance(condition, int):  # cell gid 
            cellGids.append(condition)
        
        elif isinstance(condition, str):  # entire pop
            cellGids.extend([c.gid for c in allCells if c.tags['popLabel']==condition])
        
        elif isinstance(condition, tuple):  # subset of a pop with relative indices
            cellsPop = [c.gid for c in allCells if c.tags['popLabel']==condition[0]]
            if isinstance(condition[1], list):
                cellGids.extend([gid for i,gid in enumerate(cellsPop) if i in condition[1]])
            elif isinstance(condition[1], int):
                cellGids.extend([gid for i,gid in enumerate(cellsPop) if i==condition[1]])

    cellGids = list(set(cellGids))  # unique values
    cells = [cell for cell in allCells if cell.gid in cellGids]
    return cells


###############################################################################
### Run Simulation
###############################################################################
def runSim ():
    sim.pc.barrier()
    timing('start', 'runTime')
    if sim.rank == 0:
        print('\nRunning...')
        runstart = time() # See how long the run takes
    h.dt = sim.cfg.dt  # set time step
    for key,val in sim.cfg.hParams.iteritems(): setattr(h, key, val) # set other h global vars (celsius, clamp_resist)
    sim.pc.set_maxstep(10)
    mindelay = sim.pc.allreduce(sim.pc.set_maxstep(10), 2) # flag 2 returns minimum value
    if sim.rank==0 and sim.cfg.verbose: print 'Minimum delay (time-step for queue exchange) is ',mindelay
    
    # reset all netstims so runs are always equivalent
    for cell in sim.net.cells:
        for stim in cell.stims:
            if 'hRandom' in stim:
                stim['hRandom'].Random123(cell.gid, sim.id32('%d'%(stim['seed'])))
                stim['hRandom'].negexp(1)

    init()
    sim.pc.psolve(sim.cfg.duration)
    if sim.rank==0: 
        runtime = time()-runstart # See how long it took
        print('  Done; run time = %0.2f s; real-time ratio: %0.2f.' % (runtime, sim.cfg.duration/1000/runtime))
    sim.pc.barrier() # Wait for all hosts to get to this point
    timing('stop', 'runTime')


###############################################################################
### Run Simulation
###############################################################################
def runSimWithIntervalFunc (interval, func):
    sim.pc.barrier()
    timing('start', 'runTime')
    if sim.rank == 0:
        print('\nRunning...')
        runstart = time() # See how long the run takes
    h.dt = sim.cfg.dt
    sim.pc.set_maxstep(10)
    mindelay = sim.pc.allreduce(sim.pc.set_maxstep(10), 2) # flag 2 returns minimum value
    if sim.rank==0 and sim.cfg.verbose: print 'Minimum delay (time-step for queue exchange) is ',mindelay
    
    # reset all netstims so runs are always equivalent
    for cell in sim.net.cells:
        for stim in cell.stims:
            stim['hRandom'].Random123(cell.gid, sim.id32('%d'%(sim.cfg.seeds['stim'])))
            stim['hRandom'].negexp(1)

    init()

    #progUpdate = 1000  # update every second
    while round(h.t) < sim.cfg.duration:
        sim.pc.psolve(min(sim.cfg.duration, h.t+interval))
        #if sim.cfg.verbose and (round(h.t) % progUpdate):
            #print(' Sim time: %0.1f s (%d %%)' % (h.t/1e3, int(h.t/f.cfg.duration*100)))
        func(h.t) # function to be called at intervals

    if sim.rank==0: 
        runtime = time()-runstart # See how long it took
        print('  Done; run time = %0.2f s; real-time ratio: %0.2f.' % (runtime, sim.cfg.duration/1000/runtime))
    sim.pc.barrier() # Wait for all hosts to get to this point
    timing('stop', 'runTime')
                

###############################################################################
### Gather tags from cells
###############################################################################
def _gatherAllCellTags ():
    data = [{cell.gid: cell.tags for cell in sim.net.cells}]*sim.nhosts  # send cells data to other nodes
    gather = sim.pc.py_alltoall(data)  # collect cells data from other nodes (required to generate connections)
    sim.pc.barrier()
    allCellTags = {}
    for dataNode in gather:         
        allCellTags.update(dataNode)
    del gather, data  # removed unnecesary variables
    return allCellTags


###############################################################################
### Gather data from nodes
###############################################################################
def gatherData ():
    timing('start', 'gatherTime')
    ## Pack data from all hosts
    if sim.rank==0: 
        print('\nGathering spikes...')

    simDataVecs = ['spkt','spkid','stims']+sim.cfg.recordTraces.keys()
    if sim.nhosts > 1:  # only gather if >1 nodes 
        netPopsCellGids = {popLabel: list(pop.cellGids) for popLabel,pop in sim.net.pops.iteritems()}
        nodeData = {'netCells': [c.__getstate__() for c in sim.net.cells], 'netPopsCellGids': netPopsCellGids, 'simData': sim.simData} 
        data = [None]*sim.nhosts
        data[0] = {}
        for k,v in nodeData.iteritems():
            data[0][k] = v 
        gather = sim.pc.py_alltoall(data)
        sim.pc.barrier()  
        if sim.rank == 0:
            allCells = []
            allPops = ODict()
            for popLabel,pop in sim.net.pops.iteritems(): allPops[popLabel] = pop.__getstate__() # can't use dict comprehension for OrderedDict
            allPopsCellGids = {popLabel: [] for popLabel in netPopsCellGids}
            sim.allSimData = Dict()

            for k in gather[0]['simData'].keys():  # initialize all keys of allSimData dict
                sim.allSimData[k] = {}

            # fill in allSimData taking into account if data is dict of h.Vector (code needs improvement to be more generic)
            for node in gather:  # concatenate data from each node
                allCells.extend(node['netCells'])  # extend allCells list
                for popLabel,popCellGids in node['netPopsCellGids'].iteritems():
                    allPopsCellGids[popLabel].extend(popCellGids)
                    
                for key,val in node['simData'].iteritems():  # update simData dics of dics of h.Vector 
                    if key in simDataVecs:          # simData dicts that contain Vectors
                        if isinstance(val,dict):                
                            for cell,val2 in val.iteritems():
                                if isinstance(val2,dict):       
                                    sim.allSimData[key].update(Dict({cell:Dict()}))
                                    for stim,val3 in val2.iteritems():
                                        sim.allSimData[key][cell].update({stim:list(val3)}) # udpate simData dicts which are dicts of dicts of Vectors (eg. ['stim']['cell_1']['backgrounsd']=h.Vector)
                                else:
                                    sim.allSimData[key].update({cell:list(val2)})  # udpate simData dicts which are dicts of Vectors (eg. ['v']['cell_1']=h.Vector)
                        else:                                   
                            sim.allSimData[key] = list(sim.allSimData[key])+list(val) # udpate simData dicts which are Vectors
                    else: 
                        sim.allSimData[key].update(val)           # update simData dicts which are not Vectors

            sim.net.allCells =  sorted(allCells, key=lambda k: k['gid']) 
            
            for popLabel,pop in allPops.iteritems():
                pop['cellGids'] = sorted(allPopsCellGids[popLabel])
            sim.net.allPops = allPops
    
    else:  # if single node, save data in same format as for multiple nodes for consistency
        sim.net.allCells = [c.__getstate__() for c in sim.net.cells]
        sim.net.allPops = ODict()
        for popLabel,pop in sim.net.pops.iteritems(): sim.net.allPops[popLabel] = pop.__getstate__() # can't use dict comprehension for OrderedDict
        sim.allSimData = Dict() 
        for k in sim.simData.keys():  # initialize all keys of allSimData dict
                sim.allSimData[k] = Dict()
        for key,val in sim.simData.iteritems():  # update simData dics of dics of h.Vector 
                if key in simDataVecs:          # simData dicts that contain Vectors
                    if isinstance(val,dict):                
                        for cell,val2 in val.iteritems():
                            if isinstance(val2,dict):       
                                sim.allSimData[key].update(Dict({cell:Dict()}))
                                for stim,val3 in val2.iteritems():
                                    sim.allSimData[key][cell].update({stim:list(val3)}) # udpate simData dicts which are dicts of dicts of Vectors (eg. ['stim']['cell_1']['backgrounsd']=h.Vector)
                            else:
                                sim.allSimData[key].update({cell:list(val2)})  # udpate simData dicts which are dicts of Vectors (eg. ['v']['cell_1']=h.Vector)
                    else:                                   
                        sim.allSimData[key] = list(sim.allSimData[key])+list(val) # udpate simData dicts which are Vectors
                else: 
                    sim.allSimData[key].update(val)           # update simData dicts which are not Vectors

    ## Print statistics
    if sim.rank == 0:
        timing('stop', 'gatherTime')
        if sim.cfg.timing: print('  Done; gather time = %0.2f s.' % sim.timingData['gatherTime'])

        print('\nAnalyzing...')
        sim.totalSpikes = len(sim.allSimData['spkt'])   
        sim.totalConnections = sum([len(cell['conns']) for cell in sim.net.allCells])   
        sim.numCells = len(sim.net.allCells)

        if sim.totalSpikes > 0:
            sim.firingRate = float(sim.totalSpikes)/sim.numCells/sim.cfg.duration*1e3 # Calculate firing rate 
        else: 
            sim.firingRate = 0
        if sim.numCells > 0:
            sim.connsPerCell = sim.totalConnections/float(sim.numCells) # Calculate the number of connections per cell
        else:
            sim.connsPerCell = 0
        if sim.cfg.timing: print('  Run time: %0.2f s' % (sim.timingData['runTime']))
        print('  Simulated time: %0.1f s; %i cells; %i workers' % (sim.cfg.duration/1e3, sim.numCells, sim.nhosts))
        print('  Spikes: %i (%0.2f Hz)' % (sim.totalSpikes, sim.firingRate))
        print('  Connections: %i (%0.2f per cell)' % (sim.totalConnections, sim.connsPerCell))

        return sim.allSimData


###############################################################################
### Calculate and print avg pop rates
###############################################################################
def popAvgRates(trange = None, show = True):
    if not hasattr(sim, 'allSimData') or 'spkt' not in sim.allSimData:
        print 'Error: sim.allSimData not available; please call sim.gatherData()'
        return None

    spkts = sim.allSimData['spkt']
    spkids = sim.allSimData['spkid']

    if not trange: 
        trange = [0, sim.cfg.duration]
    else:
        spkids,spkts = zip(*[(spkid,spkt) for spkid,spkt in zip(spkids,spkts) if trange[0] <= spkt <= trange[1]])

    avgRates = Dict()
    for pop in sim.net.allPops:
        numCells = float(len(sim.net.allPops[pop]['cellGids']))
        if numCells > 0:
            tsecs = float((trange[1]-trange[0]))/1000.0
            avgRates[pop] = len([spkid for spkid in spkids if sim.net.allCells[int(spkid)]['tags']['popLabel']==pop])/numCells/tsecs
            print '%s : %.3f Hz'%(pop, avgRates[pop])
    return avgRates



###############################################################################
### Gather data from nodes
###############################################################################
def _gatherCells ():
    ## Pack data from all hosts
    if sim.rank==0: 
        print('\nUpdating sim.net.allCells...')

    if sim.nhosts > 1:  # only gather if >1 nodes 
        nodeData = {'netCells': [c.__getstate__() for c in sim.net.cells]} 
        data = [None]*sim.nhosts
        data[0] = {}
        for k,v in nodeData.iteritems():
            data[0][k] = v 
        gather = sim.pc.py_alltoall(data)
        sim.pc.barrier()  
        if sim.rank == 0:
            allCells = []
         
            # fill in allSimData taking into account if data is dict of h.Vector (code needs improvement to be more generic)
            for node in gather:  # concatenate data from each node
                allCells.extend(node['netCells'])  # extend allCells list
            sim.net.allCells =  sorted(allCells, key=lambda k: k['gid']) 
         
    else:  # if single node, save data in same format as for multiple nodes for consistency
        sim.net.allCells = [c.__getstate__() for c in sim.net.cells]
      

###############################################################################
### Save data
###############################################################################
def saveData (include = None):
    if sim.rank == 0:
        timing('start', 'saveTime')
        
        if not include: include = sim.cfg.saveDataInclude
        dataSave = {}
        net = {}

        if 'netParams' in include: net['params'] = replaceFuncObj(sim.net.params.__dict__)
        if 'netCells' in include: net['cells'] = sim.net.allCells
        if 'netPops' in include: net['pops'] = sim.net.allPops
        if net: dataSave['net'] = net
        if 'simConfig' in include: dataSave['simConfig'] = sim.cfg.__dict__
        if 'simData' in include: dataSave['simData'] = sim.allSimData

        if dataSave:
            if sim.cfg.timestampFilename: 
                timestamp = time()
                timestampStr = datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S')
                sim.cfg.filename = sim.cfg.filename+'-'+timestampStr

            # Save to pickle file
            if sim.cfg.savePickle:
                import pickle
                print('Saving output as %s ... ' % (sim.cfg.filename+'.pkl'))
                with open(sim.cfg.filename+'.pkl', 'wb') as fileObj:
                    pickle.dump(dataSave, fileObj)
                print('Finished saving!')

            # Save to dpk file
            if sim.cfg.saveDpk:
                import gzip
                print('Saving output as %s ... ' % (sim.cfg.filename+'.dpk'))
                fn=sim.cfg.filename #.split('.')
                gzip.open(fn, 'wb').write(pk.dumps(dataSave)) # write compressed string
                print('Finished saving!')

            # Save to json file
            if sim.cfg.saveJson:
                import json
                print('Saving output as %s ... ' % (sim.cfg.filename+'.json '))
                with open(sim.cfg.filename+'.json', 'w') as fileObj:
                    json.dump(dataSave, fileObj)
                print('Finished saving!')

            # Save to mat file
            if sim.cfg.saveMat:
                from scipy.io import savemat 
                print('Saving output as %s ... ' % (sim.cfg.filename+'.mat'))
                savemat(sim.cfg.filename+'.mat', tupleToStr(replaceNoneObj(dataSave)))  # replace None and {} with [] so can save in .mat format
                print('Finished saving!')

            # Save to HDF5 file (uses very inefficient hdf5storage module which supports dicts)
            if sim.cfg.saveHDF5:
                dataSaveUTF8 = _dict2utf8(replaceNoneObj(dataSave)) # replace None and {} with [], and convert to utf
                import hdf5storage
                print('Saving output as %s... ' % (sim.cfg.filename+'.hdf5'))
                hdf5storage.writes(dataSaveUTF8, filename=sim.cfg.filename+'.hdf5')
                print('Finished saving!')

            # Save to CSV file (currently only saves spikes)
            if sim.cfg.saveCSV:
                if 'simData' in dataSave:
                    import csv
                    print('Saving output as %s ... ' % (sim.cfg.filename+'.csv'))
                    writer = csv.writer(open(sim.cfg.filename+'.csv', 'wb'))
                    for dic in dataSave['simData']:
                        for values in dic:
                            writer.writerow(values)
                    print('Finished saving!')

            # Save to Dat file(s) 
            if sim.cfg.saveDat:
                traces = sim.cfg.recordTraces
                for ref in traces.keys():
                    for cellid in sim.allSimData[ref].keys():
                        dat_file_name = '%s_%s.dat'%(ref,cellid)
                        dat_file = open(dat_file_name, 'w')
                        trace = sim.allSimData[ref][cellid]
                        print("Saving %i points of data on: %s:%s to %s"%(len(trace),ref,cellid,dat_file_name))
                        for i in range(len(trace)):
                            dat_file.write('%s\t%s\n'%((i*sim.cfg.dt/1000),trace[i]/1000))

                print('Finished saving!')
        else: 
            print 'Nothing to save'


        # Save timing
        timing('stop', 'saveTime')
        if sim.cfg.timing and sim.cfg.saveTiming: 
            import pickle
            with open('timing.pkl', 'wb') as file: pickle.dump(sim.timing, file)


###############################################################################
### Timing - Stop Watch
###############################################################################
def timing (mode, processName):
    if sim.rank == 0 and sim.cfg.timing:
        if mode == 'start':
            sim.timingData[processName] = time() 
        elif mode == 'stop':
            sim.timingData[processName] = time() - sim.timingData[processName]
            

###############################################################################
### Print netpyne version
###############################################################################
def version():
    import netpyne 
    print netpyne.__version__


###############################################################################
### Print github version
###############################################################################
def gitversion():
    import netpyne,os
    currentPath = os.getcwd()
    netpynePath = os.path.dirname(netpyne.__file__)
    os.system('cd '+netpynePath+' ; git log -1; '+'cd '+currentPath) 


###############################################################################
### Get connection centric network representation as used in NeuroML2
###############################################################################  
def _convertNetworkRepresentation (net, gids_vs_pop_indices):

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
                        if not preGid == 'NetStim':
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
                        else:
                            print("      Conn NetStim->%s[%s] with %s"%(popPost, indexPost, '??'))
                                
    return nn                 


###############################################################################
### Get stimulations in representation as used in NeuroML2
###############################################################################  
def _convertStimulationRepresentation (net,gids_vs_pop_indices, nml_doc):

    stims = {}

    for np_pop in net.pops: 
        if not np_pop.tags['cellModel'] ==  'NetStim':
            print("Adding stims for: %s"%np_pop.tags)
            for cell in net.cells:
                if cell.gid in np_pop.cellGids:
                    pop, index = gids_vs_pop_indices[cell.gid]
                    print("    Cell %s:\n    Tags:  %s\n    Pop:   %s[%i]\n    Stims: %s\n    Conns: %s\n"%(cell.gid,cell.tags,pop, index,cell.stims,cell.conns))
                    for stim in cell.stims:
                        ref = stim['label']
                        rate = stim['rate']
                        noise = stim['noise']
                        
                        netstim_found = False
                        for conn in cell.conns:
                            if conn['preGid'] == 'NetStim' and conn['preLabel'] == ref:
                                assert(not netstim_found)
                                netstim_found = True
                                synMech = conn['synMech']
                                threshold = conn['threshold']
                                delay = conn['delay']
                                weight = conn['weight']
                                
                        assert(netstim_found)
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
def _export_synapses (net, nml_doc):

    import neuroml

    for syn in net.params.synMechParams:

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
def exportNeuroML2 (reference, connections=True, stimulations=True):

    net = sim.net
    
    print("Exporting network to NeuroML 2, reference: %s"%reference)
    # Only import libNeuroML if this method is called...
    import neuroml
    import neuroml.writers as writers

    nml_doc = neuroml.NeuroMLDocument(id='%s'%reference)
    nml_net = neuroml.Network(id='%s'%reference)
    nml_doc.networks.append(nml_net)

    import netpyne
    nml_doc.notes = 'NeuroML 2 file exported from NetPyNE v%s'%(netpyne.__version__)

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
            
            pop.size = index
            
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
                        pre_cell_id="../%s[%i]"%(stim_pop.id, count), \
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

    ls = LEMSSimulation('Sim_%s'%reference, sim.cfg.dt,sim.cfg.duration,reference)

    ls.include_neuroml2_file(nml_file_name)'''

    import pyneuroml.lems

    pyneuroml.lems.generate_lems_file_for_neuroml("Sim_%s"%reference, 
                               nml_file_name, 
                               reference, 
                               sim.cfg.duration, 
                               sim.cfg.dt, 
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






