"""
sim.py 

Contains functions related to the simulation (eg. setupRecording, runSim) 

Contributors: salvadordura@gmail.com
"""

import sys
from pylab import mean, zeros, concatenate, vstack, array
from time import time
from datetime import datetime
import inspect
import cPickle as pk
import hashlib 
from neuron import h, init # Import NEURON
import framework as f

###############################################################################
# initialize variables and MPI
###############################################################################

def initialize(simConfig = None, netParams = None, net = None):
    f.simData = {}  # used to store output simulation data (spikes etc)
    f.gidVec =[] # Empty list for storing GIDs (index = local id; value = gid)
    f.gidDic = {} # Empty dict for storing GIDs (key = gid; value = local id) -- ~x6 faster than gidVec.index()  
    f.lastGid = 0  # keep track of las cell gid
    f.fih = []  # list of func init handlers

    if net:
        setNet(f.net)  # set existing external network
    else: 
        setNet(f.Network())  # or create new network

    if simConfig:
        setSimCfg(simConfig)  # set simulation configuration

    if netParams: 
        setNetParams(netParams)  # set network parameters

    createParallelContext()  # iniitalize PC, nhosts and rank
    readArgs()  # read arguments from commandline


###############################################################################
# Set network object to use in simulation
###############################################################################
def setNet(net):
    f.net = net

###############################################################################
# Set network params to use in simulation
###############################################################################
def setNetParams(params):
    f.net.params = params

###############################################################################
# Set simulation config
###############################################################################
def setSimCfg(cfg):
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
    f.nhosts = int(f.pc.nhost()) # Find number of hosts
    f.rank = int(f.pc.id())     # rank 0 will be the master

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
                line = inspect.getsource(val)
                startInd = line.find('lambda')
                endInd = min([line[startInd:].find(c) for c in [']', '}', '\n', '\''] if line[startInd:].find(c)>0])
                funcSource = line[startInd:startInd+endInd]
                obj[key] = funcSource
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
    # spike recording
    f.pc.spike_record(-1, f.simData['spkt'], f.simData['spkid']) # -1 means to record from all cells on this node

    # stim spike recording
    if f.cfg['recordStim']:
        f.simData['stims'] = {}
        for cell in f.net.cells: 
            cell.recordStimSpikes()

    # intrinsic cell variables recording
    if f.cfg['recordTraces']:
        for key in f.cfg['recdict'].keys(): f.simData[key] = {}
        for cell in f.net.cells: 
            cell.recordTraces()


###############################################################################
### Run Simulation
###############################################################################
def runSim():
    f.pc.barrier()
    if f.rank == 0:
        print('\nRunning...')
        runstart = time() # See how long the run takes
    f.pc.set_maxstep(10)
    mindelay = f.pc.allreduce(f.pc.set_maxstep(10), 2) # flag 2 returns minimum value
    if f.rank==0: print 'Minimum delay (time-step for queue exchange) is ',mindelay
    init() # 
    #h.cvode.event(f.savestep,savenow)
    f.pc.psolve(f.cfg['tstop'])
    if f.rank==0: 
        runtime = time()-runstart # See how long it took
        print('  Done; run time = %0.1f s; real-time ratio: %0.2f.' % (runtime, f.cfg['duration']/1000/runtime))
    f.pc.barrier() # Wait for all hosts to get to this point




###############################################################################
### Gather tags from cells
###############################################################################
def gatherAllCellTags():
    data = [{cell.gid: cell.tags for cell in f.net.cells}]*s.nhosts  # send cells data to other nodes
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
    ## Pack data from all hosts
    if f.rank==0: 
        print('\nGathering spikes...')
        gatherstart = time() # See how long it takes to plot

    nodeData = {'netCells': [c.__getstate__() for c in f.net.cells], 'simData': f.simData} 
    data = [None]*s.nhosts
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
        #### REPLACE CODE BELOW TO MAKE GENERIC - CHECK FOR DICT VS H.VECTOR AND UPDATE ALLSIMDATA ACCORDINGLY ####
        for node in gather:  # concatenate data from each node
            allCells.extend(node['netCells'])  # extend allCells list
            for key,val in node['simData'].iteritems():  # update simData dics of dics of h.Vector 
                if key in f.cfg['simDataVecs']:          # simData dicts that contain Vectors
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


    ## Print statistics
    if f.rank == 0:
        gathertime = time()-gatherstart # See how long it took
        print('  Done; gather time = %0.1f f.' % gathertime)

        print('\nAnalyzing...')
        f.totalSpikes = len(f.allSimData['spkt'])   
        f.totalConnections = sum([len(cell['conns']) for cell in f.net.allCells])   
        f.numCells = len(f.net.allCells)

        f.firingRate = float(f.totalSpikes)/s.numCells/s.cfg['duration']*1e3 # Calculate firing rate 
        f.connsPerCell = f.totalConnections/float(f.numCells) # Calculate the number of connections per cell
        print('  Run time: %0.1f s (%i-s sim; %i cells; %i workers)' % (gathertime, f.cfg['duration']/1e3, f.numCells, f.nhosts))
        print('  Spikes: %i (%0.2f Hz)' % (f.totalSpikes, f.firingRate))
        print('  Connections: %i (%0.2f per cell)' % (f.totalConnections, f.connsPerCell))
 

###############################################################################
### Save data
###############################################################################
def saveData():
    if f.rank == 0:
        
        dataSave = {'simConfig': f.cfg, 'netParams': replaceFuncObj(f.net.params), 'netCells': f.net.allCells, 'simData': f.allSimData}
        # Save to pickle file
        if f.cfg['savePickle']:
            import pickle
            print('Saving output as %s...' % f.cfg['filename']+'.pkl')
            with open(f.cfg['filename']+'.pkl', 'wb') as fileObj:
                pickle.dump(dataSave, fileObj)
            print('Finished saving!')

        # Save to json file
        if f.cfg['saveJson']:
            import json
            print('Saving output as %s...' % f.cfg['filename']+'.json')
            with open(f.cfg['filename']+'.json', 'w') as fileObj:
                json.dump(dataSave, fileObj)
            pass

        # Save to mat file
        if f.cfg['saveMat']:
            from scipy.io import savemat 
            print('Saving output as %s...' % f.cfg['filename']+'.mat')
            savemat(f.cfg['filename']+'.mat', replaceNoneObj(dataSave))  # replace None and {} with [] so can save in .mat format
            print('Finished saving!')

        # Save to dpk file
        if f.cfg['saveDpk']:
            import os,gzip
            fn=s.params['filename'].split('.')
            fn='{}{:d}.{}'.format(fn[0],int(round(h.t)),fn[1]) # insert integer time into the middle of file name
            gzip.open(fn, 'wb').write(pk.dumps(f.alls.simData)) # write compressed string
            print 'Wrote file {}/{} of size {:.3f} MB'.format(os.getcwd(),fn,os.path.getsize(file)/1e6)

          


