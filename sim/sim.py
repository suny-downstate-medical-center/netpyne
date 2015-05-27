"""
sim.py 

list of model objects (paramaters and variables) to be shared across modules
Can modified manually or via arguments from main.py

Version: 2015may26 by salvadordura@gmail.com
"""

import sys
from pylab import mean, zeros, concatenate, vstack, array
from time import time
from datetime import datetime
import pickle
import cPickle as pk
import itertools
from neuron import h, init # Import NEURON
import params as p
import shared as s

###############################################################################
### Update model parameters from command-line arguments
###############################################################################
def readArgs():
    for argv in sys.argv[1:]: # Skip first argument, which is file name
        arg = argv.replace(' ','').split('=') # ignore spaces and find varname and value
        harg = arg[0].split('.')+[''] # Separate out variable name; '' since if split fails need to still have an harg[1]
        if len(arg)==2:
            if hasattr(p,arg[0]) or hasattr(p,harg[1]): # Check that variable exists
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

    # background inputs
    if p.saveBackground:
        for c in s.cells:
            s.backgroundSpikevecs=[] # A list for storing actual cell voltages (WARNING, slow!)
            s.backgroundRecorders=[] # And for recording spikes
            backgroundSpikevec = h.Vector() # Initialize vector
            s.backgroundSpikevecs.append(backgroundSpikevec) # Keep all those vectors
            backgroundRecorder = h.NetCon(c.backgroundSource, None)
            backgroundRecorder.record(backgroundSpikevec) # Record simulation time
            s.backgroundRecorders.append(backgroundRecorder)



    # ## intrinsic cell variables recording
    # for c in s.cells: c.record()

    # ## Set up LFP recording
    # s.lfptime = [] # List of times that the LFP was recorded at
    # s.nlfps = len(s.lfppops) # Number of distinct LFPs to calculate
    # s.hostlfps = [] # Voltages for calculating LFP
    # s.lfpcellids = [[] for pop in range(s.nlfps)] # Create list of lists of cell IDs
    # for c in range(s.cellsperhost): # Loop over each cell and decide which LFP population, if any, it belongs to
    #     gid = s.gidVec[c] # Get this cell's GID
    #     for pop in range(s.nlfps): # Loop over each LFP population
    #         thispop = s.cellpops[gid] # Population of this cell
    #         if sum(s.lfppops[pop]==thispop)>0: # There's a match
    #             s.lfpcellids[pop].append(gid) # Flag this cell as belonging to this LFP population



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
    s.pc.psolve(p.tstop)
    if s.rank==0: 
        runtime = time()-runstart # See how long it took
        print('  Done; run time = %0.1f s; real-time ratio: %0.2f.' % (runtime, p.duration/1000/runtime))
    s.pc.barrier() # Wait for all hosts to get to this point



###############################################################################
### Gather data from nodes
###############################################################################
def gatherData():
    ## Pack data from all hosts
    if s.rank==0: 
        print('\nGathering spikes...')
        gatherstart = time() # See how long it takes to plot

    # extend simdata dictionary to save relevant data in each node
    nodePops = [[y.__dict__[x] for x in y.__dict__] for y in s.pops]
    nodeCells = [[y.__dict__[x] for x in y.__dict__ if not x in ['m', 'dummy', 'soma', 'syns', 'stim', 'backgroundSyn', 'backgroundSource', 'backgroundConn']] for y in s.cells]
    nodeConns = [[y.__dict__[x] for x in y.__dict__ if not x in ['netcon']] for y in s.conns]
    s.simdata.update({'pops': nodePops, 'cells': nodeCells, 'conns': nodeConns})
    if p.saveBackground:
        nodeBackground = [(s.cells[i].gid, s.backgroundSpikevecs[i]) for i in range(s.cells)]
        s.simdata.update({'background': nodeBackground})  

    # gather simdata from all nodes
    data=[None]*s.nhosts # using None is important for mem and perf of pc.alltoall() when data is sparse
    data[0]={} # make a new dict
    for k,v in s.simdata.iteritems():   data[0][k] = v 
    gather=s.pc.py_alltoall(data)
    s.pc.barrier()
    #for v in s.simdata.itervalues(): v.resize(0)
    if s.rank==0: 
        s.allsimdata = {}
        [s.allsimdata.update({k : concatenate([array(d[k]) for d in gather])}) for k in ['spkt', 'spkid']] # concatenate spikes
        for k in [x for x in gather[0].keys() if x not in ['spkt', 'spkid']]: # concatenate other dict fields
            tmp = []
            for d in gather: tmp.extend(d[k]) 
            s.allsimdata.update({k: array(tmp, dtype=object)})  # object type so can be saved in .mat format
        if not s.allsimdata.has_key('run'): s.allsimdata.update({'run':{'saveStep':p.saveStep, 'dt':h.dt, 'randseed':p.randseed, 'duration':p.duration}}) # add run params
        # 'recdict':recdict, 'Vrecc': Vrecc}}) # save major run attributes
        s.allsimdata.update({'t':h.t, 'walltime':datetime.now().ctime()})

        gathertime = time()-gatherstart # See how long it took
        print('  Done; gather time = %0.1f s.' % gathertime)

    ## Print statistics
    if s.rank == 0:
        print('\nAnalyzing...')
        s.totalspikes = len(s.allsimdata['spkt'])    
        s.totalconnections = len(s.allsimdata['conns'])
        s.ncells = len(s.allsimdata['cells'])

        s.firingrate = float(s.totalspikes)/s.ncells/p.duration*1e3 # Calculate firing rate 
        s.connspercell = s.totalconnections/float(s.ncells) # Calculate the number of connections per cell
        print('  Run time: %0.1f s (%i-s sim; %i scale; %i cells; %i workers)' % (gathertime, p.duration/1e3, p.scale, s.ncells, s.nhosts))
        print('  Spikes: %i (%0.2f Hz)' % (s.totalspikes, s.firingrate))
        print('  Connections: %i (%0.2f per cell)' % (s.totalconnections, s.connspercell))
 

###############################################################################
### Save data
###############################################################################
def saveData():
    if s.rank == 0:
        # Save to dpk file
        if p.savedpk:
            import os,gzip
            fn=p.filename.split('.')
            file='{}{:d}.{}'.format(fn[0],int(round(h.t)),fn[1]) # insert integer time into the middle of file name
            gzip.open(file, 'wb').write(pk.dumps(s.allsimdata)) # write compressed string
            print 'Wrote file {}/{} of size {:.3f} MB'.format(os.getcwd(),file,os.path.getsize(file)/1e6)
  
        # Save to mat file
        if p.savemat:
            print('Saving output as %s...' % p.filename)
            savestart = time() # See how long it takes to save
            from scipy.io import savemat # analysis:ignore -- because used in exec() statement
            savemat(p.filename, s.allsimdata)  # check if looks ok in matlab
            savetime = time()-savestart # See how long it took to save
            print('  Done; time = %0.1f s' % savetime)


