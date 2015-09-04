"""
sim.py 

Contains functions related to the simulation (eg. setupRecording, runSim) 

Contributors: salvadordura@gmail.com
"""

import sys
from pylab import mean, zeros, concatenate, vstack, array
from time import time
from datetime import datetime
import pickle
import cPickle as pk
import hashlib 
from neuron import h, init # Import NEURON
import shared as s

###############################################################################
# initialize variables and MPI
###############################################################################

def initialize(simConfig = None, netParams = None, net = None):
    s.simdata = {}  # used to store output simulation data (spikes etc)
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


def id32(obj): 
    return int(hashlib.md5(obj).hexdigest()[0:8],16)# hash(obj) & 0xffffffff # for random seeds (bitwise AND to retain only lower 32 bits)


###############################################################################
### Replacee item with specific key from dict or list (used to remove h objects)
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
    s.pc.spike_record(-1, s.simdata['spkt'], s.simdata['spkid']) # -1 means to record from all cells on this node

    # background inputs recording
    if s.params['saveBackground']:
        for c in s.net.cells:
            backgroundSpikevecs=[] # A list for storing actual cell voltages (WARNING, slow!)
            backgroundRecorders=[] # And for recording spikes
            backgroundSpikevec = h.Vector() # Initialize vector
            backgroundSpikevecs.append(backgroundSpikevec) # Keep all those vectors
            backgroundRecorder = h.NetCon(c.backgroundSource, None)
            backgroundRecorder.record(backgroundSpikevec) # Record simulation time
            backgroundRecorders.append(backgroundRecorder)

    # intrinsic cell variables recording
    if s.params['recordTraces']:
        #s.simdataVecs.extend(s.params['recdict'].keys())
        for k in s.params['recdict'].keys(): s.simdata[k] = {}
        for c in s.net.cells: 
            c.record()

###############################################################################
### Run Simulation
###############################################################################
def runSim():
    if s.rank == 0:
        print('\nRunning...')
        runstart = time() # See how long the run takes
    s.pc.set_maxstep(10)
    mindelay = s.pc.allreduce(s.pc.set_maxstep(10), 2) # flag 2 returns minimum value
    if s.rank==0: print 'Minimum delay (time-step for queue exchange) is ',mindelay
    init() # 
    #h.cvode.event(s.savestep,savenow)
    s.pc.psolve(s.params['tstop'])
    if s.rank==0: 
        runtime = time()-runstart # See how long it took
        print('  Done; run time = %0.1f s; real-time ratio: %0.2f.' % (runtime, s.params['duration']/1000/runtime))
    s.pc.barrier() # Wait for all hosts to get to this point



###############################################################################
### Gather data from nodes
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


def gatherData():
    ## Pack data from all hosts
    if s.rank==0: 
        print('\nGathering spikes...')
        gatherstart = time() # See how long it takes to plot

    # extend s.simdata dictionary to save relevant data in each node
    nodePops = [[y.__dict__[x] for x in y.__dict__ if not x in ['density']] for y in s.net.pops]
    nodeCells = [[y.__dict__[x] for x in y.__dict__ if not x in ['soma', 'stim', 'sec', 'm', 'syns', 'backgroundSyn', 'backgroundSource', 'backgroundConn', 'backgroundRand']] for y in s.net.cells]
    nodeConns = [[y.__dict__[x] for x in y.__dict__ if not x in ['s.netcon', 'connWeights', 'connProbs']] for y in s.net.conns]
    s.simdata.update({'pops': nodePops, 'cells': nodeCells, 'conns': nodeConns})
    if s.params['saveBackground']:
        nodeBackground = [(s.net.cells[i].gid, s.backgroundSpikevecs[i]) for i in range(s.net.cells)]
        s.simdata.update({'background': nodeBackground})  

    # gather s.simdata from all nodes
    data=[None]*s.nhosts # using None is important for mem and perf of s.pc.alltoall() when data is sparse
    data[0]={} # make a new dict
    for k,v in s.simdata.iteritems():   data[0][k] = v 
    gather=s.pc.py_alltoall(data)
    s.pc.barrier()
    #for v in s.simdata.itervalues(): v.resize(0) # 
    if s.rank==0: 
        allsimdata = {}
        [allsimdata.update({k : concatenate([array(d[k]) for d in gather])}) for k in s.simdataVecs] # concatenate spikes
        for k in [x for x in gather[0].keys() if x not in s.s.simdataVecs]: # concatenate other dict fields
            tmp = []
            for d in gather: tmp.extend(d[k]) 
            allsimdata.update({k: array(tmp, dtype=object)})  # object type so can be saved in .mat format
        if not allsimdata.has_key('run'): allsimdata.update({'run':{'recordStep':s.params['recordStep'], 'dt':h.dt, 'randseed':s.params['randseed'], 'duration':s.params['duration']}}) # add run s.params
        allsimdata.update({'t':h.t, 'walltime':datetime.now().ctime()})

        gathertime = time()-gatherstart # See how long it took
        print('  Done; gather time = %0.1f s.' % gathertime)

    ## Print statistics
    if s.rank == 0:
        print('\nAnalyzing...')
        s.totalspikes = len(s.alls.simdata['spkt'])    
        s.totalconnections = len(s.alls.simdata['conns'])
        s.ncells = len(s.alls.simdata['cells'])

        s.firingrate = float(s.totalspikes)/s.ncells/s.params['duration']*1e3 # Calculate firing rate 
        s.connspercell = s.totalconnections/float(s.ncells) # Calculate the number of connections per cell
        print('  Run time: %0.1f s (%i-s sim; %i scale; %i cells; %i workers)' % (gathertime, s.params['duration']/1e3, s.params['scale'], s.ncells, s.nhosts))
        print('  Spikes: %i (%0.2f Hz)' % (s.totalspikes, s.firingrate))
        print('  Connections: %i (%0.2f per cell)' % (s.totalconnections, s.connspercell))
 

###############################################################################
### Save data
###############################################################################
def saveData():
    if s.rank == 0:
        print('Saving output as %s...' % s.params['filename'])
        # Save to dpk file
        if s.params['savedpk']:
            import os,gzip
            fn=s.params['filename'].split('.')
            file='{}{:d}.{}'.format(fn[0],int(round(h.t)),fn[1]) # insert integer time into the middle of file name
            gzip.open(file, 'wb').write(pk.dumps(s.alls.simdata)) # write compressed string
            print 'Wrote file {}/{} of size {:.3f} MB'.format(os.getcwd(),file,os.path.getsize(file)/1e6)
  
        # Save to mat file
        if s.params['savemat']:
            savestart = time() # See how long it takes to save
            from scipy.io import savemat # analysis:ignore -- because used in exec() statement
            savemat(s.params['filename'], s.alls.simdata)  # check if looks ok in matlab
            savetime = time()-savestart # See how long it took to save
            print('  Done; time = %0.1f s' % savetime)

        # Save to pickle file

