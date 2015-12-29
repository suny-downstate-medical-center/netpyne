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
import shared as s

###############################################################################
# initialize variables and MPI
###############################################################################

def initialize(simConfig = None, netParams = None, net = None):
    s.simData = {}  # used to store output simulation data (spikes etc)
    s.gidVec =[] # Empty list for storing GIDs (index = local id; value = gid)
    s.gidDic = {} # Empty dict for storing GIDs (key = gid; value = local id) -- ~x6 faster than gidVec.index()  
    s.lastGid = 0  # keep track of las cell gid
    s.fih = []  # list of func init handlers

    if net:
        setNet(s.net)  # set existing external network
    else: 
        setNet(s.Network())  # or create new network

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
    s.net = net

###############################################################################
# Set network params to use in simulation
###############################################################################
def setNetParams(params):
    s.net.params = params

###############################################################################
# Set simulation config
###############################################################################
def setSimCfg(cfg):
    s.cfg = cfg

def loadSimCfg(paramFile):
    pass

def loadSimParams(paramFile):
    pass

###############################################################################
# Create parallel context
###############################################################################
def createParallelContext():
    s.pc = h.ParallelContext() # MPI: Initialize the ParallelContext class
    s.nhosts = int(s.pc.nhost()) # Find number of hosts
    s.rank = int(s.pc.id())     # rank 0 will be the master

    if s.rank==0: 
        s.pc.gid_clear()


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
### Update model parameters from command-line arguments - UPDATE for sim and s.net s.params
###############################################################################
def readArgs():
    for argv in sys.argv[1:]: # Skip first argument, which is file name
        arg = argv.replace(' ','').split('=') # ignore spaces and find varname and value
        harg = arg[0].split('.')+[''] # Separate out variable name; '' since if split fails need to still have an harg[1]
        if len(arg)==2:
            if hasattr(s.s.params,arg[0]) or hasattr(s.s.params,harg[1]): # Check that variable exists
                if arg[0] == 'outfilestem':
                    exec('s.'+arg[0]+'="'+arg[1]+'"') # Actually set variable 
                    if s.rank==0: # messages only come from Master  
                        print('  Setting %s=%s' %(arg[0],arg[1]))
                else:
                    exec('p.'+argv) # Actually set variable            
                    if s.rank==0: # messages only come from Master  
                        print('  Setting %s=%r' %(arg[0],eval(arg[1])))
            else: 
                sys.tracebacklimit=0
                raise Exception('Reading args from commandline: Variable "%s" not found' % arg[0])
        elif argv=='-mpi':   s.ismpi = True
        else: pass # ignore -python 


###############################################################################
### Setup Recording
###############################################################################
def setupRecording():
    # spike recording
    s.pc.spike_record(-1, s.simData['spkt'], s.simData['spkid']) # -1 means to record from all cells on this node

    # stim spike recording
    if s.cfg['recordStim']:
        s.simData['stims'] = {}
        for cell in s.net.cells: 
            cell.recordStimSpikes()

    # intrinsic cell variables recording
    if s.cfg['recordTraces']:
        for key in s.cfg['recdict'].keys(): s.simData[key] = {}
        for cell in s.net.cells: 
            cell.recordTraces()


###############################################################################
### Run Simulation
###############################################################################
def runSim():
    s.pc.barrier()
    if s.rank == 0:
        print('\nRunning...')
        runstart = time() # See how long the run takes
    s.pc.set_maxstep(10)
    mindelay = s.pc.allreduce(s.pc.set_maxstep(10), 2) # flag 2 returns minimum value
    if s.rank==0: print 'Minimum delay (time-step for queue exchange) is ',mindelay
    init() # 
    #h.cvode.event(s.savestep,savenow)
    s.pc.psolve(s.cfg['tstop'])
    if s.rank==0: 
        runtime = time()-runstart # See how long it took
        print('  Done; run time = %0.1f s; real-time ratio: %0.2f.' % (runtime, s.cfg['duration']/1000/runtime))
    s.pc.barrier() # Wait for all hosts to get to this point




###############################################################################
### Gather tags from cells
###############################################################################
def gatherAllCellTags():
    data = [{cell.gid: cell.tags for cell in s.net.cells}]*s.nhosts  # send cells data to other nodes
    gather = s.pc.py_alltoall(data)  # collect cells data from other nodes (required to generate connections)
    s.pc.barrier()
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
    if s.rank==0: 
        print('\nGathering spikes...')
        gatherstart = time() # See how long it takes to plot

    nodeData = {'netCells': [c.__getstate__() for c in s.net.cells], 'simData': s.simData} 
    data = [None]*s.nhosts
    data[0] = {}
    for k,v in nodeData.iteritems():
        data[0][k] = v 
    gather = s.pc.py_alltoall(data)
    s.pc.barrier()
    if s.rank == 0:
        allCells = []
        s.allSimData = {} 
        for k in gather[0]['simData'].keys():  # initialize all keys of allSimData dict
            s.allSimData[k] = {}
        #### REPLACE CODE BELOW TO MAKE GENERIC - CHECK FOR DICT VS H.VECTOR AND UPDATE ALLSIMDATA ACCORDINGLY ####
        for node in gather:  # concatenate data from each node
            allCells.extend(node['netCells'])  # extend allCells list
            for key,val in node['simData'].iteritems():  # update simData dics of dics of h.Vector 
                if key in s.cfg['simDataVecs']:          # simData dicts that contain Vectors
                    if isinstance(val,dict):                
                        for cell,val2 in val.iteritems():
                            if isinstance(val2,dict):       
                                s.allSimData[key].update({cell:{}})
                                for stim,val3 in val2.iteritems():
                                    s.allSimData[key][cell].update({stim:list(val3)}) # udpate simData dicts which are dicts of dicts of Vectors (eg. ['stim']['cell_1']['backgrounsd']=h.Vector)
                            else:
                                s.allSimData[key].update({cell:list(val2)})  # udpate simData dicts which are dicts of Vectors (eg. ['v']['cell_1']=h.Vector)
                    else:                                   
                        s.allSimData[key] = list(s.allSimData[key])+list(val) # udpate simData dicts which are Vectors
                else: 
                    s.allSimData[key].update(val)           # update simData dicts which are not Vectors
        s.net.allCells = allCells


    ## Print statistics
    if s.rank == 0:
        gathertime = time()-gatherstart # See how long it took
        print('  Done; gather time = %0.1f s.' % gathertime)

        print('\nAnalyzing...')
        s.totalSpikes = len(s.allSimData['spkt'])   
        s.totalConnections = sum([len(cell['conns']) for cell in s.net.allCells])   
        s.numCells = len(s.net.allCells)

        s.firingRate = float(s.totalSpikes)/s.numCells/s.cfg['duration']*1e3 # Calculate firing rate 
        s.connsPerCell = s.totalConnections/float(s.numCells) # Calculate the number of connections per cell
        print('  Run time: %0.1f s (%i-s sim; %i cells; %i workers)' % (gathertime, s.cfg['duration']/1e3, s.numCells, s.nhosts))
        print('  Spikes: %i (%0.2f Hz)' % (s.totalSpikes, s.firingRate))
        print('  Connections: %i (%0.2f per cell)' % (s.totalConnections, s.connsPerCell))
 

###############################################################################
### Save data
###############################################################################
def saveData():
    if s.rank == 0:
        
        dataSave = {'simConfig': s.cfg, 'netParams': replaceFuncObj(s.net.params), 'netCells': s.net.allCells, 'simData': s.allSimData}
        # Save to pickle file
        if s.cfg['savePickle']:
            import pickle
            print('Saving output as %s...' % s.cfg['filename']+'.pkl')
            with open(s.cfg['filename']+'.pkl', 'wb') as f:
                pickle.dump(dataSave, f)
            print('Finished saving!')

        # Save to json file
        if s.cfg['saveJson']:
            import json
            print('Saving output as %s...' % s.cfg['filename']+'.json')
            with open(s.cfg['filename']+'.json', 'w') as f:
                json.dump(dataSave, f)
            pass

        # Save to mat file
        if s.cfg['saveMat']:
            from scipy.io import savemat 
            print('Saving output as %s...' % s.cfg['filename']+'.mat')
            savemat(s.cfg['filename']+'.mat', replaceNoneObj(dataSave))  # replace None and {} with [] so can save in .mat format
            print('Finished saving!')

        # Save to dpk file
        if s.cfg['saveDpk']:
            import os,gzip
            fn=s.params['filename'].split('.')
            file='{}{:d}.{}'.format(fn[0],int(round(h.t)),fn[1]) # insert integer time into the middle of file name
            gzip.open(file, 'wb').write(pk.dumps(s.alls.simData)) # write compressed string
            print 'Wrote file {}/{} of size {:.3f} MB'.format(os.getcwd(),file,os.path.getsize(file)/1e6)

          


