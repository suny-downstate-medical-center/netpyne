"""
MODEL

A large-scale network simulation for exploring traveling waves, stimuli,
and STDs. Built solely in Python, using Izhikevich neurons and with MPI
support. Runs in real-time with over 8000 cells when appropriately
parallelized.
M1 model extended to interface with Plexon-recorded PMd data, virtual arm,
and reinforcement learning

Usage:
    python model.py # Run simulation, optionally plot a raster
    python simmovie.py # Show a movie of the results
    python model.py scale=20 # Run simulation, set scale=20

MPI usage:
    mpiexec -n 4 nrniv -python -mpi model.py

Version: 2014feb21 by cliffk
2014sep19 modified by salvadord and giljael
"""


###############################################################################
### IMPORT MODULES
###############################################################################

from neuron import h, init # Import NEURON
from pylab import seed, rand, sqrt, exp, transpose, ceil, concatenate, array, zeros, ones, vstack, show, disp, mean, inf, concatenate
from time import time, sleep
from datetime import datetime
import pickle
import warnings
import analysis
import shared as s # Import all shared variables and parameters
warnings.filterwarnings('error')


###############################################################################
### Sequences of commands to run full model
###############################################################################
# standard sequence
def runSeq():
    verystart=time() # store initial time
    createCells()
    connectCells() 
    addBackground()
    addStimulation()
    setupRecording()
    runSim()
    gatherData()
    #saveData()
    #plotData()

    #s.pc.runworker() # MPI: Start simulations running on each host (add to simcontrol module)
    #s.pc.done() # MPI: Close MPI
    totaltime = time()-verystart # See how long it took in total
    print('\nDone; total time = %0.1f s.' % totaltime)



###############################################################################
### Create Cells
###############################################################################
def createCells():
    ## Print diagnostic information
    s.pc.barrier()
    if s.rank==0: print("\nCreating simulation of %i cell populations for %0.1f s on %i hosts..." % (len(s.pops),s.duration/1000.,s.nhosts)) 
    # Instantiate network cells (objects of class 'Cell')
    s.gidVec=[] # Empty list for storing GIDs (index = local id; value = gid)
    s.gidDic = {} # Empty dict for storing GIDs (key = gid; value = local id) -- ~x6 faster than gidVec.index()  
    s.cells = []
    for ipop in s.pops:
        newCells = ipop.createCells(s) # create cells for this pop using Pop method
        s.cells.extend(newCells)  # add to list of cells
        s.pc.barrier()
        if s.rank==0 and s.verbose: print('Instantiated %d cells of population %d'%(ipop.numCells, ipop.popgid))           
    s.simdata.update({name:h.Vector(1e4).resize(0) for name in ['spkt','spkid']})
    print('  Number of cells on node %i: %i ' % (s.rank,len(s.cells)))            
    

###############################################################################
### Connect Cells
###############################################################################
def connectCells():
    # Instantiate network connections (objects of class 'Conn') - connects object cells based on pre and post cell's type, class and yfrac
    if s.rank==0: print('Making connections...'); connstart = time()
    s.conns = []  # list to store connections
    data = [s.cells]*s.nhosts  # send cells data to other nodes
    gather = s.pc.py_alltoall(data)  # collect cells data from other nodes (required to generate connections)
    s.pc.barrier()
    allCells = []
    for x in gather:    allCells.extend(x)  # concatenate cells data from all nodes
    for ipost in s.cells: # for each postsynaptic cell in this node
        newConns = s.Conn.connect(allCells, ipost, s)  # calculate all connections
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
    if s.savebackground:
        s.backgroundspikevecs=[] # A list for storing actual cell voltages (WARNING, slow!)
        s.backgroundrecorders=[] # And for recording spikes
    for c in s.cells: 
        gid = c.gid
        backgroundrand = h.Random()
        backgroundrand.MCellRan4(gid,gid*2)
        backgroundrand.negexp(1)
        s.backgroundrands.append(backgroundrand)
        backgroundsource = h.NetStim() # Create a NetStim
        backgroundsource.interval = s.backgroundrate**-1*1e3 # Take inverse of the frequency and then convert from Hz^-1 to ms
        backgroundsource.noiseFromRandom(backgroundrand) # Set it to use this random number generator
        backgroundsource.noise = s.backgroundnoise # Fractional noise in timing
        backgroundsource.number = s.backgroundnumber # Number of spikes
        s.backgroundsources.append(backgroundsource) # Save this NetStim
        s.backgroundgid.append(gid) # append cell gid associated to this netstim
        backgroundconn = h.NetCon(backgroundsource, c.m) # Connect this noisy input to a cell
        for r in range(s.l.numReceptors): backgroundconn.weight[r]=0 # Initialize weights to 0, otherwise get memory leaks
        backgroundconn.weight[s.backgroundreceptor] = s.backgroundweight[c.EorI] # Specify the weight -- 1 is NMDA receptor for smoother, more summative activation
        backgroundconn.delay=2 # Specify the delay in ms -- shouldn't make a spot of difference
        s.backgroundconns.append(backgroundconn) # Save this connnection
        if s.savebackground:
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
    if s.usestims:
        s.stimstruct = [] # For saving
        s.stimrands=[] # Create input connections
        s.stimsources=[] # Create empty list for storing synapses
        s.stimconns=[] # Create input connections
        s.stimtimevecs = [] # Create array for storing time vectors
        s.stimweightvecs = [] # Create array for holding weight vectors
        if s.saveraw: 
            s.stimspikevecs=[] # A list for storing actual cell voltages (WARNING, slow!)
            s.stimrecorders=[] # And for recording spikes
        for stim in range(len(s.stimpars)): # Loop over each stimulus type
            ts = s.stimpars[stim] # Stands for "this stimulus"
            ts.loc = ts.loc * s.modelsize # scale cell locations to model size
            stimvecs = s.makestim(ts.isi, ts.var, ts.width, ts.weight, ts.sta, ts.fin, ts.shape) # Time-probability vectors
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


###############################################################################
### Setup Recording
###############################################################################
def setupRecording():
    # ## spike recording
    s.pc.spike_record(-1, s.simdata['spkt'], s.simdata['spkid']) # -1 means to record from all cells on this node

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

    pass


###############################################################################
### Run Simulation
###############################################################################
def runSim():
    if s.rank == 0:
        print('\nRunning...')
        runstart = time() # See how long the run takes
    #h.tstop = s.duration
    s.pc.set_maxstep(10)
    mindelay = s.pc.allreduce(s.pc.set_maxstep(10), 2) # flag 2 returns minimum value
    if s.rank==0: print 'Minimum delay (time-step for queue exchange) is ',mindelay
    init() # diff with h.init()?
    #h.cvode.event(s.savestep,savenow)
    s.pc.psolve(s.duration)#h.tstop)
    #if s.rank==0: print('  t = %0.1f s (%i%%; time remaining: %0.1f s)' % (h.t/1e3, int(h.t/s.duration*100), (s.duration-h.t)*(time()-runstart)/h.t))      
    if s.rank==0: 
        s.runtime = time()-runstart # See how long it took
        print('  Done; run time = %0.1f s; real-time ratio: %0.2f.' % (s.runtime, s.duration/1000/s.runtime))
    s.pc.barrier() # Wait for all hosts to get to this point



###############################################################################
### Gather data from nodes
###############################################################################
def gatherData():
    ## Pack data from all hosts
    if s.rank==0: 
        print('\nGathering spikes...')
        gatherstart = time() # See how long it takes to plot

        data=[None]*s.nhosts # using None is important for mem and perf of pc.alltoall() when data is sparse
        data[0]={} # make a new dict
        for k,v in s.simdata.iteritems():  data[0][k] = v 
        gather=s.pc.py_alltoall(data)
        s.pc.barrier()
        for v in s.simdata.itervalues(): v.resize(0)

        gdict = {}
        [gdict.update(d) for d in gather] # this will now repeated needlessly overwrite 'spkt' and 'spkid'
        gdict.update({'spkt' : concatenate([d['spkt']  for d in gather]), 
               'spkid': concatenate([d['spkid'] for d in gather])})
        if not gdict.has_key('run'): gdict.update({'run':{'saveStep':s.saveStep, 'dt':h.dt, 'randseed':s.randseed, 'duration':s.duration}}) # eventually save full params (p)
                                                 # 'recdict':recdict, 'Vrecc': Vrecc}}) # save major run attributes
        gdict.update({'t':h.t, 'walltime':datetime.now().ctime()})

    if s.rank==0: 
        gathertime = time()-gatherstart # See how long it took
        print('  Done; gather time = %0.1f s.' % gathertime)
    s.pc.barrier()

    ## Print statistics
    if s.rank == 0:
        print('\nAnalyzing...')
        s.totalspikes = len(gdict['spkt'])    
        s.totalconnections = len(s.conns)
        s.ncells = len(s.cells)

        s.firingrate = float(s.totalspikes)/len(s.cells)/s.duration*1e3 # Calculate firing rate -- confusing but cool Python trick for iterating over a list
        s.connspercell = s.totalconnections/float(s.ncells) # Calculate the number of connections per cell
        print('  Run time: %0.1f s (%i-s sim; %i scale; %i cells; %i workers)' % (s.runtime, s.duration/1e3, s.scale, s.ncells, s.nhosts))
        print('  Spikes: %i (%0.2f Hz)' % (s.totalspikes, s.firingrate))
        print('  Connections: %i (%0.2f per cell)' % (s.totalconnections, s.connspercell))
        # print('  Mean connection distance: %0.2f um' % mean(s.allconnections[2]))
        # print('  Mean connection delay: %0.2f ms' % mean(s.allconnections[3]))


###############################################################################
### Save data
###############################################################################
def saveData():
    if s.rank == 0:
        ## Save to txt file (spikes and conn)
        if s.savetxt: 
            filename = '../data/m1ms-spk.txt'
            fd = open(filename, "w")
            for c in range(len(s.allspiketimes)):
                print >> fd, int(s.allspikecells[c]), s.allspiketimes[c], s.popNamesDic[s.cellnames[int(s.allspikecells[c])]]
            fd.close()
            print "[Spikes are stored in", filename, "]"

            if s.verbose:
                filename = 'm1ms-conn.txt'
                fd = open(filename, "w")
                for c in range(len(s.allconnections[0])):
                    print >> fd, int(s.allconnections[0][c]), int(s.allconnections[1][c]), s.allconnections[2][c], s.allconnections[3][c], s.allconnections[4][c] 
                fd.close()
                print "[Connections are stored in", filename, "]"

        ## Save to mat file
        if s.savemat:
            print('Saving output as %s...' % s.filename)
            savestart = time() # See how long it takes to save
            from scipy.io import savemat # analysis:ignore -- because used in exec() statement
            
            # Save simulation code
            filestosave = ['main.py', 'shared.py', 'network.py', 'izhi.py', 'izhi2007.mod', 'stdp.mod', 'nsloc.py', 'nsloc.mod'] # Files to save
            argv = [];
            simcode = [argv, filestosave] # Start off with input parameters, if any, and then the list of files being saved
            for f in range(len(filestosave)): # Loop over each file
                fobj = open(filestosave[f]) # Open it for reading
                simcode.append(fobj.readlines()) # Append to list of code to save
                fobj.close() # Close file object
            
            # Tidy variables
            spikedata = vstack([s.allspikecells,s.allspiketimes]).T # Put spike data together
            connections = vstack([s.allconnections[0],s.allconnections[1]]).T # Put connection data together
            distances = s.allconnections[2] # Pull out distances
            delays = s.allconnections[3] # Pull out delays
            weights = s.allconnections[4] # Pull out weights
            stdpdata = s.allstdpconndata # STDP connection data
            if s.usestims: stimdata = [vstack(s.stimstruct[c][1]).T for c in range(len(stimstruct))] # Only pull out vectors, not text, in stimdata

            # Save variables
            info = {'timestamp':datetime.today().strftime("%d %b %Y %H:%M:%S"), 'runtime':s.runtime, 'popnames':s.popnames, 'popEorI':s.popEorI} # Save date, runtime, and input arguments
            

            variablestosave = ['info', 'simcode', 'spikedata', 's.cellpops', 's.cellnames', 's.cellclasses', 's.xlocs', 's.ylocs', 's.zlocs', 'connections', 'distances', 'delays', 'weights', 's.EorI']
            
            if s.savelfps:  
                variablestosave.extend(['s.lfptime', 's.lfps'])   
            if s.usestdp: 
                variablestosave.extend(['stdpdata', 's.allweightchanges'])
            if s.savebackground:
                variablestosave.extend(['s.backgrounddata'])
            if s.saveraw: 
                variablestosave.extend(['s.stimspikedata', 's.allraw'])
            if s.usestims: variablestosave.extend(['stimdata'])
            savecommand = "savemat(s.filename, {"
            for var in range(len(variablestosave)): savecommand += "'" + variablestosave[var].replace('s.','') + "':" + variablestosave[var] + ", " # Create command out of all the variables
            savecommand = savecommand[:-2] + "}, oned_as='column')" # Omit final comma-space and complete command
            exec(savecommand) # Actually perform the save
            
            savetime = time()-savestart # See how long it took to save
            print('  Done; time = %0.1f s' % savetime)


###############################################################################
### Plot data
###############################################################################
def plotData():
    ## Plotting
    if s.rank == 0:
        if s.plotraster: # Whether or not to plot
            if (s.totalspikes>s.maxspikestoplot): 
                disp('  Too many spikes (%i vs. %i)' % (s.totalspikes, s.maxspikestoplot)) # Plot raster, but only if not too many spikes
            else: 
                print('Plotting raster...')
                analysis.plotraster()#allspiketimes, allspikecells, EorI, ncells, connspercell, backgroundweight, firingrate, duration)
        if s.plotconn:
            print('Plotting connectivity matrix...')
            analysis.plotconn()
        if s.plotpsd:
            print('Plotting power spectral density')
            analysis.plotpsd()
        if s.plotweightchanges:
            print('Plotting weight changes...')
            analysis.plotweightchanges()
            #analysis.plotmotorpopchanges()
        if s.plot3darch:
            print('Plotting 3d architecture...')
            analysis.plot3darch()

        show(block=False)



