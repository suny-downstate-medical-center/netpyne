"""
sim.py 

list of model objects (paramaters and variables) to be shared across modules
Can modified manually or via arguments from main.py

Contributors: salvadordura@gmail.com
"""

import sys
from pylab import mean, zeros, concatenate, vstack, array
from time import time
from datetime import datetime
import pickle
import cPickle as pk
from neuron import h, init # Import NEURON
import analysis

class Simulation(object):

    ###############################################################################
    # initialize variables and 
    ###############################################################################
    def __init__(self, params=None, net=None):
        self.simdata = {}
        self.simdataVecs = ['spkt', 'spkid']
        self.lastGid = 0  # keep track of las cell gid
        self.fih = []  # list of func init handlers
        self.params = params
        self.net = net
        self.initMPI()


    def id32(obj): 
        return int(hashlib.md5(obj).hexdigest()[0:8],16)# hash(obj) & 0xffffffff # for random seeds (bitwise AND to retain only lower 32 bits)

    ###############################################################################
    # Init MPI
    ###############################################################################
    def initMPI:
        self.pc = h.ParallelContext() # MPI: Initialize the ParallelContext class
        self.nhosts = int(pc.nhost()) # Find number of hosts
        self.rank = int(pc.id())     # rank 0 will be the master

        if self.rank==0: 
            print('\nSetting parameters...')
            pc.gid_clear()


    ###############################################################################
    ### Update model parameters from command-line arguments
    ###############################################################################
    def readArgs(self):
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
    def setupRecording(self):
        # spike recording
        self.pc.spike_record(-1, self.simdata['spkt'], self.simdata['spkid']) # -1 means to record from all cells on this node

        # background inputs recording
        if self.params['saveBackground']:
            for c in self.net.cells:
                self.backgroundSpikevecs=[] # A list for storing actual cell voltages (WARNING, slow!)
                self.backgroundRecorders=[] # And for recording spikes
                backgroundSpikevec = h.Vector() # Initialize vector
                self.backgroundSpikevecs.append(backgroundSpikevec) # Keep all those vectors
                backgroundRecorder = h.NetCon(c.backgroundSource, None)
                backgroundRecorder.record(backgroundSpikevec) # Record simulation time
                self.backgroundRecorders.append(backgroundRecorder)

        # intrinsic cell variables recording
        if self.params['recordTraces']:
            #s.simdataVecs.extend(p.sim['recdict'].keys())
            for k in self.params['recdict'].keys(): self.simdata[k] = {}
            for c in self.net.cells: 
                c.record()

    ###############################################################################
    ### Run Simulation
    ###############################################################################
    def runSim(self):
        if self.rank == 0:
            print('\nRunning...')
            runstart = time() # See how long the run takes
        self.pc.set_maxstep(10)
        mindelay = self.pc.allreduce(self.pc.set_maxstep(10), 2) # flag 2 returns minimum value
        if self.rank==0: print 'Minimum delay (time-step for queue exchange) is ',mindelay
        init() # 
        #h.cvode.event(s.savestep,savenow)
        self.pc.psolve(p.sim['tstop'])
        if self.rank==0: 
            runtime = time()-runstart # See how long it took
            print('  Done; run time = %0.1f s; real-time ratio: %0.2f.' % (runtime, self.params['duration']/1000/runtime))
        self.pc.barrier() # Wait for all hosts to get to this point



    ###############################################################################
    ### Gather data from nodes
    ###############################################################################
    def gatherData(self):
        ## Pack data from all hosts
        if self.rank==0: 
            print('\nGathering spikes...')
            gatherstart = time() # See how long it takes to plot

        # extend simdata dictionary to save relevant data in each node
        nodePops = [[y.__dict__[x] for x in y.__dict__ if not x in ['density']] for y in self.net.pops]
        nodeCells = [[y.__dict__[x] for x in y.__dict__ if not x in ['soma', 'stim', 'sec', 'm', 'syns', 'backgroundSyn', 'backgroundSource', 'backgroundConn', 'backgroundRand']] for y in s.cells]
        nodeConns = [[y.__dict__[x] for x in y.__dict__ if not x in ['netcon', 'connWeights', 'connProbs']] for y in self.net.conns]
        self.simdata.update({'pops': nodePops, 'cells': nodeCells, 'conns': nodeConns})
        if p.sim['saveBackground']:
            nodeBackground = [(self.net.cells[i].gid, self.backgroundSpikevecs[i]) for i in range(self.net.cells)]
            self.simdata.update({'background': nodeBackground})  

        # gather simdata from all nodes
        data=[None]*self.nhosts # using None is important for mem and perf of pc.alltoall() when data is sparse
        data[0]={} # make a new dict
        for k,v in self.simdata.iteritems():   data[0][k] = v 
        gather=s.pc.py_alltoall(data)
        s.pc.barrier()
        #for v in s.simdata.itervalues(): v.resize(0) # 
        if s.rank==0: 
            s.allsimdata = {}
            [s.allsimdata.update({k : concatenate([array(d[k]) for d in gather])}) for k in s.simdataVecs] # concatenate spikes
            for k in [x for x in gather[0].keys() if x not in s.simdataVecs]: # concatenate other dict fields
                tmp = []
                for d in gather: tmp.extend(d[k]) 
                s.allsimdata.update({k: array(tmp, dtype=object)})  # object type so can be saved in .mat format
            if not s.allsimdata.has_key('run'): s.allsimdata.update({'run':{'recordStep':p.sim['recordStep'], 'dt':h.dt, 'randseed':p.sim['randseed'], 'duration':p.sim['duration']}}) # add run params
            s.allsimdata.update({'t':h.t, 'walltime':datetime.now().ctime()})

            gathertime = time()-gatherstart # See how long it took
            print('  Done; gather time = %0.1f s.' % gathertime)

        ## Print statistics
        if s.rank == 0:
            print('\nAnalyzing...')
            s.totalspikes = len(s.allsimdata['spkt'])    
            s.totalconnections = len(s.allsimdata['conns'])
            s.ncells = len(s.allsimdata['cells'])

            s.firingrate = float(s.totalspikes)/s.ncells/p.sim['duration']*1e3 # Calculate firing rate 
            s.connspercell = s.totalconnections/float(s.ncells) # Calculate the number of connections per cell
            print('  Run time: %0.1f s (%i-s sim; %i scale; %i cells; %i workers)' % (gathertime, p.sim['duration']/1e3, p.net['scale'], s.ncells, s.nhosts))
            print('  Spikes: %i (%0.2f Hz)' % (s.totalspikes, s.firingrate))
            print('  Connections: %i (%0.2f per cell)' % (s.totalconnections, s.connspercell))
     

    ###############################################################################
    ### Save data
    ###############################################################################
    def saveData():
        if s.rank == 0:
            print('Saving output as %s...' % p.sim['filename'])
            # Save to dpk file
            if p.sim['savedpk']:
                import os,gzip
                fn=p.sim['filename'].split('.')
                file='{}{:d}.{}'.format(fn[0],int(round(h.t)),fn[1]) # insert integer time into the middle of file name
                gzip.open(file, 'wb').write(pk.dumps(s.allsimdata)) # write compressed string
                print 'Wrote file {}/{} of size {:.3f} MB'.format(os.getcwd(),file,os.path.getsize(file)/1e6)
      
            # Save to mat file
            if p.sim['savemat']:
                savestart = time() # See how long it takes to save
                from scipy.io import savemat # analysis:ignore -- because used in exec() statement
                savemat(p.sim['filename'], s.allsimdata)  # check if looks ok in matlab
                savetime = time()-savestart # See how long it took to save
                print('  Done; time = %0.1f s' % savetime)

            # check shelves

