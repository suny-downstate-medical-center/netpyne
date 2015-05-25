

###############################################################################
### IMPORT MODULES
###############################################################################

from neuron import h, init # Import NEURON
from pylab import seed, rand, sqrt, exp, transpose, ceil, concatenate, array, zeros, ones, vstack, show, disp, mean, inf, concatenate
from time import time, sleep
import pickle
import warnings

import params as p  # Import all shared variables and parameters
import shared as s

warnings.filterwarnings('error')


###############################################################################
### Instantiate network populations (objects of class 'Pop')
###############################################################################
def createPops():
    s.pops = []  # list to store populations ('Pop' objects)
    for popParam in p.popParams: # for each set of population parameters 
        s.pops.append(s.Pop(*popParam))  # instantiate a new object of class Pop and add to list pop


###############################################################################
### Create Cells
###############################################################################
def createCells():
    s.pc.barrier()
    if s.rank==0: print("\nCreating simulation of %i cell populations for %0.1f s on %i hosts..." % (len(s.pops),p.duration/1000.,s.nhosts)) 
    s.gidVec=[] # Empty list for storing GIDs (index = local id; value = gid)
    s.gidDic = {} # Empty dict for storing GIDs (key = gid; value = local id) -- ~x6 faster than gidVec.index()  
    s.cells = []
    for ipop in s.pops: # For each pop instantiate the network cells (objects of class 'Cell')
        newCells = ipop.createCells() # create cells for this pop using Pop method
        s.cells.extend(newCells)  # add to list of cells
        s.pc.barrier()
        if s.rank==0 and p.verbose: print('Instantiated %d cells of population %d'%(ipop.numCells, ipop.popgid))           
    s.simdata.update({name:h.Vector(1e4).resize(0) for name in ['spkt','spkid']})
    print('  Number of cells on node %i: %i ' % (s.rank,len(s.cells)))            
    

###############################################################################
### Connect Cells
###############################################################################
def connectCells():
    # Instantiate network connections (objects of class 'Conn') - connects object cells based on pre and post cell's type, class and yfrac
    if s.rank==0: print('Making connections...'); connstart = time()
    if p.connType == 'yfrac':
        s.conns = []  # list to store connections
        data = [s.cells]*s.nhosts  # send cells data to other nodes
        gather = s.pc.py_alltoall(data)  # collect cells data from other nodes (required to generate connections)
        s.pc.barrier()
        allCells = []
        for x in gather:    allCells.extend(x)  # concatenate cells data from all nodes
        allCellsGids = [x.gid for x in allCells] # order gids
        allCells = [x for (y,x) in sorted(zip(allCellsGids,allCells))]
        for ipost in s.cells: # for each postsynaptic cell in this node
            newConns = s.Conn.connectYfrac(allCells, ipost)  # calculate all connections
            s.conns.extend(newConns)  # add to list of connections in this node
        del gather, data  # removed unnecesary variables
        print('  Number of connections on host %i: %i ' % (s.rank, len(s.conns)))
        s.pc.barrier()
        if s.rank==0: conntime = time()-connstart; print('  Done; time = %0.1f s' % conntime) # See how long it took


###############################################################################
### Add background inputs
###############################################################################
def addBackground():
    if s.rank==0: print('Creating background inputs...')
    s.backgroundsources=[] # Create empty list for storing synapses
    s.backgroundrands=[] # Create random number generators
    s.backgroundconns=[] # Create input connections
    s.backgroundgid=[] # Target cell gid for each input
    if p.savebackground:
        s.backgroundspikevecs=[] # A list for storing actual cell voltages (WARNING, slow!)
        s.backgroundrecorders=[] # And for recording spikes
    for c in s.cells: 
        gid = c.gid
        backgroundrand = h.Random()
        backgroundrand.MCellRan4(gid,gid*2)
        backgroundrand.negexp(1)
        s.backgroundrands.append(backgroundrand)
        backgroundsource = h.NetStim() # Create a NetStim
        backgroundsource.interval = p.backgroundrate**-1*1e3 # Take inverse of the frequency and then convert from Hz^-1 to ms
        backgroundsource.noiseFromRandom(backgroundrand) # Set it to use this random number generator
        backgroundsource.noise = p.backgroundnoise # Fractional noise in timing
        backgroundsource.number = p.backgroundnumber # Number of spikes
        s.backgroundsources.append(backgroundsource) # Save this NetStim
        s.backgroundgid.append(gid) # append cell gid associated to this netstim
        backgroundconn = h.NetCon(backgroundsource, c.m) # Connect this noisy input to a cell
        for r in range(p.numReceptors): backgroundconn.weight[r]=0 # Initialize weights to 0, otherwise get memory leaks
        backgroundconn.weight[p.backgroundreceptor] = p.backgroundweight[c.EorI] # Specify the weight -- 1 is NMDA receptor for smoother, more summative activation
        backgroundconn.delay=2 # Specify the delay in ms -- shouldn't make a spot of difference
        s.backgroundconns.append(backgroundconn) # Save this connnection
        if p.savebackground:
            backgroundspikevec = h.Vector() # Initialize vector
            s.backgroundspikevecs.append(backgroundspikevec) # Keep all those vectors
            backgroundrecorder = h.NetCon(backgroundsource, None)
            backgroundrecorder.record(backgroundspikevec) # Record simulation time
            s.backgroundrecorders.append(backgroundrecorder)
    print('  Number created on host %i: %i' % (s.rank, len(s.backgroundsources)))
    s.pc.barrier()


###############################################################################
### Add stimulation
###############################################################################
def addStimulation():
    if p.usestims:
        s.stimuli.setStimParams()
        s.stimstruct = [] # For saving
        s.stimrands=[] # Create input connections
        s.stimsources=[] # Create empty list for storing synapses
        s.stimconns=[] # Create input connections
        s.stimtimevecs = [] # Create array for storing time vectors
        s.stimweightvecs = [] # Create array for holding weight vectors
        if p.saveraw: 
            s.stimspikevecs=[] # A list for storing actual cell voltages (WARNING, slow!)
            s.stimrecorders=[] # And for recording spikes
        for stim in range(len(s.stimuli.stimpars)): # Loop over each stimulus type
            ts = s.stimuli.stimpars[stim] # Stands for "this stimulus"
            ts.loc = ts.loc * s.modelsize # scale cell locations to model size
            stimvecs = s.stimuli.makestim(ts.isi, ts.var, ts.width, ts.weight, ts.sta, ts.fin, ts.shape) # Time-probability vectors
            s.stimstruct.append([ts.name, stimvecs]) # Store for saving later
            s.stimtimevecs.append(h.Vector().from_python(stimvecs[0]))
            for c in s.cells:
                gid = c.gid #s.cellsperhost*int(s.rank)+c # For deciding E or I    
                seed(s.id32('%d'%(s.randseed+gid))) # Reset random number generator for this cell
                if ts.fraction>rand(): # Don't do it for every cell necessarily
                    if any(s.cellpops[gid]==ts.pops) and s.xlocs[gid]>=ts.loc[0,0] and s.xlocs[gid]<=ts.loc[0,1] and s.ylocs[gid]>=ts.loc[1,0] and s.ylocs[gid]<=ts.loc[1,1]:
                        maxweightincrease = 20 # Otherwise could get infinitely high, infinitely close to the stimulus
                        distancefromstimulus = sqrt(sum((array([s.xlocs[gid], s.ylocs[gid]])-s.modelsize*ts.falloff[0])**2))
                        fallofffactor = min(maxweightincrease,(ts.falloff[1]/distancefromstimulus)**2)
                        s.stimweightvecs.append(h.Vector().from_python(stimvecs[1]*fallofffactor)) # Scale by the fall-off factor
                        stimrand = h.Random()
                        stimrand.MCellRan4() # If everything has the same seed, should happen at the same time
                        stimrand.negexp(1)
                        stimrand.seq(s.id32('%d'%(s.randseed+gid))*1e3) # Set the sequence i.e. seed
                        s.stimrands.append(stimrand)
                        stimsource = h.NetStim() # Create a NetStim
                        stimsource.interval = ts.rate**-1*1e3 # Interval between spikes
                        stimsource.number = 1e9 # Number of spikes
                        stimsource.noise = ts.noise # Fractional noise in timing
                        stimsource.noiseFromRandom(stimrand) # Set it to use this random number generator
                        s.stimsources.append(stimsource) # Save this NetStim
                        stimconn = h.NetCon(stimsource, s.cells[c]) # Connect this noisy input to a cell
                        for r in range(s.nreceptors): stimconn.weight[r]=0 # Initialize weights to 0, otherwise get memory leaks
                        s.stimweightvecs[-1].play(stimconn._ref_weight[0], s.stimtimevecs[-1]) # Play most-recently-added vectors into weight
                        stimconn.delay=s.mindelay # Specify the delay in ms -- shouldn't make a spot of difference
                        s.stimconns.append(stimconn) # Save this connnection
                        if s.saveraw:# and c <=100:
                            stimspikevec = h.Vector() # Initialize vector
                            s.stimspikevecs.append(stimspikevec) # Keep all those vectors
                            stimrecorder = h.NetCon(stimsource, None)
                            stimrecorder.record(stimspikevec) # Record simulation time
                            s.stimrecorders.append(stimrecorder)
        print('  Number of stimuli created on host %i: %i' % (s.rank, len(s.stimsources)))









