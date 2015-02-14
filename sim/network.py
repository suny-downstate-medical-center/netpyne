"""
MODEL

A large-scale network simulation for exploring traveling waves, stimuli,
and STDP. Built solely in Python, using Izhikevich neurons and with MPI
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
import shared as s
from izhi import pyramidal, fastspiking, lowthreshold, thalamocortical, reticular # Import Izhikevich model
from nsloc import nsloc # NetStim with location unit type
from pylab import seed, rand, sqrt, exp, transpose, concatenate

def id32(obj): return hash(obj) & 0xffffffff # bitwise AND to retain only lower 32 bits, for consistency with 32-bit processors


###############################################################################
### CREATE MODEL
###############################################################################
def runSeq():
    createNetwork() 
    addStimulation()
    addBackground()
    setupSim()
    runSim()
    finalizeSim()
    saveData()
    plotData()


###############################################################################
### Create Network
###############################################################################

def createNetwork():
    ## Set cell types
    celltypes=[]
    for c in range(g.ncells): # Loop over each cell. ncells is all cells in the network.
        if g.cellclasses[c]==1: celltypes.append(g.pyramidal) # Append a pyramidal cell
        elif g.cellclasses[c]==2: celltypes.append(g.fastspiking) # Append a fast-spiking interneuron
        elif g.cellclasses[c]==3: celltypes.append(g.lowthreshold) # Append a low-threshold-spiking interneuron
        elif g.cellclasses[c]==4: celltypes.append(g.thalamocortical) # Append a thalamocortical cell
        elif g.cellclasses[c]==5: celltypes.append(g.reticular) # Append a thalamocortical cell
        elif g.cellclasses[c]==-1: celltypes.append(g.nsloc) # Append a nsloc
        else: raise Exception('Undefined cell class "%s"' % g.cellclasses[c]) # No match? Cause an error


    ## Set positions
    seed(id32('%d'%g.randseed)) # Reset random number generator
    xlocs = g.modelsize*rand(g.ncells) # Create random x locations
    ylocs = g.modelsize*rand(g.ncells) # Create random y locations
    zlocs = rand(g.ncells) # Create random z locations
    for c in range(g.ncells): 
        zlocs[c] = g.corticalthick * (zlocs[c]*(g.popyfrac[g.cellclasses[c]][1]-g.popyfrac[g.cellclasses[c]][0])) # calculate based on yfrac for population and corticalthick 


    ## Actually create the cells
    ninnclDic = len(g.innclDic) # number of PMd created in this worker
    for c in xrange(int(g.rank), g.ncells, g.nhosts):
        g.dummies.append(h.Section()) # Create fake sections
        gid = c
        if g.cellnames[gid] == 'PMd':
            cell = celltypes[gid](cellid = gid) # create an NSLOC
            g.inncl.append(h.NetCon(None, cell))  # This netcon receives external spikes
            g.innclDic[gid - g.ncells - g.numPMd] = ninnclDic # This dictionary works in case that PMd's gid starts from 0.
            ninnclDic += 1
        elif g.cellnames[gid] == 'ASC':
            cell = celltypes[gid](cellid = gid) #create an NSLOC    
        else: 
            if g.cellclasses[gid]==3: 
                cell = fastspiking(g.dummies[g.cellsperhost], vt=-47, cellid=gid) # Don't use LTS cell, but instead a FS cell with a low threshold
            else: 
                cell = celltypes[gid](g.dummies[g.cellsperhost], cellid=gid) # Create a new cell of the appropriate type (celltypes[gid]) and store it
            if g.verbosity>0: g.cells[-1].useverbose(g.verbosity, g.filename+'log.txt') # Turn on diagnostic to file
        g.cells.append(cell) 
        g.gidVec.append(gid) # index = local id; value = global id
        g.gidDic[gid] = g.cellsperhost # key = global id; value = local id -- used to get local id because gid.index() too slow!
        g.pc.set_gid2node(gid, g.rank)

        spikevec = h.Vector()
        g.hostspikevecs.append(spikevec)
        spikerecorder = h.NetCon(cell, None)
        spikerecorder.record(spikevec)
        g.spikerecorders.append(spikerecorder)
        g.pc.cell(gid, g.spikerecorders[g.cellsperhost])
        g.cellsperhost += 1 # contain cell numbers per host including PMd and P
    print('  Number of cells on node %i: %i ' % (g.rank,len(g.cells)))
    g.pc.barrier()


    ## Calculate distances and probabilities
    if g.rank==0: print('Calculating connection probabilities (est. time: %i s)...' % (g.performance*g.cellsperhost**2/3e4))
    conncalcstart = g.time() # See how long connecting the cells takes
    nPostCells = 0
    for c in range(g.cellsperhost): # Loop over all postsynaptic cells on this host (has to be postsynaptic because of gid_connect)
        gid = gidVec[c] # Increment global identifier       
        if cellnames[gid] == 'PMd' or cellnames[gid] == 'ASC':
            # There are no presynaptic connections for PMd or ASC.
            continue
        nPostCells += 1
        if toroidal: 
            xpath=(abs(xlocs-xlocs[gid]))**2
            xpath2=(modelsize-abs(xlocs-xlocs[gid]))**2
            xpath[xpath2<xpath]=xpath2[xpath2<xpath]
            ypath=(abs(ylocs-ylocs[gid]))**2
            ypath2=(modelsize-abs(ylocs-ylocs[gid]))**2
            ypath[ypath2<ypath]=ypath2[ypath2<ypath]
            distances = sqrt(xpath + ypath) # Calculate all pairwise distances
        else: distances = sqrt((xlocs-xlocs[gid])**2 + (ylocs-ylocs[gid])**2) # Calculate all pairwise distances
        allconnprobs = scaleconnprob[EorI,EorI[gid]] * connprobs[cellpops,cellpops[gid]] * exp(-distances/connfalloff[EorI]) # Calculate pairwise probabilities
        allconnprobs[gid] = 0 # Prohibit self-connections using the cell's GID
        seed(id32('%d'%(randseed+gid))) # Reset random number generator  
        allrands = rand(ncells) # Create an array of random numbers for checking each connection  
        if usePlexon:
            for c in xrange(p.popGidStart[p.PMd], p.popGidEnd[p.PMd] + 1):
                allrands[c] = 1
        if cellnames[gid] == 'ER5': 
                PMdId = (gid % numPMd) + ncells - numPMd
                allconnprobs[PMdId] = connprobs[p.PMd,p.ER5] # to make this connected to ER5
                allrands[PMdId] = 0 # to make this connect to ER5
                distances[PMdId] = 300 # to make delay 5 in conndata[3] 
        makethisconnection = allconnprobs>allrands # Perform test to see whether or not this connection should be made
        preids = array(makethisconnection.nonzero()[0],dtype='int') # Return True elements of that array for presynaptic cell IDs
        postids = array(gid+zeros(len(preids)),dtype='int') # Post-synaptic cell IDs
        conndata[0].append(preids) # Append pre-cell ID
        conndata[1].append(postids) # Append post-cell ID
        conndata[2].append(distances[preids]) # Distances
        conndata[3].append(mindelay + distances[preids]/float(velocity)) # Calculate the delays
        wt1 = scaleconnweight[EorI[preids],EorI[postids]] # N weight scale factors -- WARNING, might be flipped
        wt2 = connweights[cellpops[preids],cellpops[postids],:] # NxM inter-population weights
        wt3 = receptorweight[:] # M receptor weights
        finalweights = transpose(wt1*transpose(wt2*wt3)) # Multiply out population weights with receptor weights to get NxM matrix
        conndata[4].append(finalweights) # Initialize weights to 0, otherwise get memory leaks
    for pp in range(nconnpars): conndata[pp] = array(concatenate([conndata[pp][c] for c in range(nPostCells)])) # Turn pre- and post- cell IDs lists into vectors
    nconnections = len(conndata[0]) # Find out how many connections we're going to make
    conncalctime = time()-conncalcstart # See how long it took
    if g.rank==0: print('  Done; time = %0.1f s' % conncalctime)


    ## Actually make connections
    if g.rank==0: print('Making connections (est. time: %i s)...' % (performance*nconnections/9e2))
    print('  Number of connections on host %i: %i' % (g.rank, nconnections))
    connstart = time() # See how long connecting the cells takes
    for con in range(nconnections): # Loop over each connection
        pregid = conndata[0][con] # GID of presynaptic cell    
        pstgid = conndata[1][con] # Index of postsynaptic cell
        pstid = gidDic[pstgid]# Index of postynaptic cell -- convert from GID to local
        newcon = pc.gid_connect(pregid, cells[pstid]) # Create a connection
        newcon.delay = conndata[3][con] # Set delay
        for r in range(p.nreceptors): newcon.weight[r] = conndata[4][con][r] # Set weight of connection
        connlist.append(newcon) # Connect the two cells
        if usestdp: # Using STDP?
            if sum(abs(stdprates[EorI[pregid],:]))>0 or sum(abs(RLrates[EorI[pregid],:]))>0: # Don't create an STDP connection if the learning rates are zero
                for r in range(p.nreceptors): # Need a different STDP instances for each receptor
                    if newcon.weight[r]>0: # Only make them for nonzero connections
                        stdpmech = h.STDP(0,sec=dummies[pstid]) # Create STDP adjuster
                        stdpmech.hebbwt = stdprates[EorI[pregid],0] # Potentiation rate
                        stdpmech.antiwt = stdprates[EorI[pregid],1] # Depression rate
                        stdpmech.wmax = maxweight # Maximum synaptic weight
                        precon = pc.gid_connect(pregid,stdpmech); precon.weight[0] = 1 # Send presynaptic spikes to the STDP adjuster
                        pstcon = pc.gid_connect(pstgid,stdpmech); pstcon.weight[0] = -1 # Send postsynaptic spikes to the STDP adjuster
                        h.setpointer(connlist[-1]._ref_weight[r],'synweight',stdpmech) # Associate the STDP adjuster with this weight
                        stdpmechs.append(stdpmech) # Save STDP adjuster
                        precons.append(precon) # Save presynaptic spike source
                        pstcons.append(pstcon) # Save postsynaptic spike source
                        stdpconndata.append([pregid,pstgid,r]) # Store presynaptic cell ID, postsynaptic, and receptor
                        if useRL: # using RL
                            stdpmech.RLon = 1 # make sure RL is on
                            stdpmech.RLhebbwt = RLrates[EorI[pregid],0] # Potentiation rate
                            stdpmech.RLantiwt = RLrates[EorI[pregid],1] # Depression rate
                            stdpmech.tauhebb = stdpmech.tauanti = stdpwin # stdp window length (ms)
                            stdpmech.RLwindhebb = stdpmech.RLwindhebb = eligwin # RL eligibility trace window length (ms)
                            stdpmech.useRLexp = useRLexp # RL 
                            stdpmech.softthresh = useRLsoft # RL soft-thresholding
                        else:
                            stdpmech.RLon = 0 # make sure RL is off
                 
    nstdpconns = len(stdpconndata) # Get number of STDP connections
    conntime = time()-connstart # See how long it took
    if usestdp: print('  Number of STDP connections on host %i: %i' % (g.rank, nstdpconns))
    if g.rank==0: print('  Done; time = %0.1f s' % conntime)


###############################################################################
### Add stimulation
###############################################################################

## IMPLEMENT STIMULATION
def addStimulation():
    if usestims:
        for stim in range(len(stimpars)): # Loop over each stimulus type
            ts = stimpars[stim] # Stands for "this stimulus"
            ts.loc = ts.loc * modelsize # scale cell locations to model size
            stimvecs = makestim(ts.isi, ts.var, ts.width, ts.weight, ts.sta, ts.fin, ts.shape) # Time-probability vectors
            stimstruct.append([ts.name, stimvecs]) # Store for saving later
            stimtimevecs.append(h.Vector().from_python(stimvecs[0]))
            
            for c in range(cellsperhost):
                gid = cellsperhost*int(g.rank)+c # For deciding E or I    
                seed(id32('%d'%(randseed+gid))) # Reset random number generator for this cell
                if ts.fraction>rand(): # Don't do it for every cell necessarily
                    if any(cellpops[gid]==ts.pops) and xlocs[gid]>=ts.loc[0,0] and xlocs[gid]<=ts.loc[0,1] and ylocs[gid]>=ts.loc[1,0] and ylocs[gid]<=ts.loc[1,1]:
                        
                        maxweightincrease = 20 # Otherwise could get infinitely high, infinitely close to the stimulus
                        distancefromstimulus = sqrt(sum((array([xlocs[gid], ylocs[gid]])-modelsize*ts.falloff[0])**2))
                        fallofffactor = min(maxweightincrease,(ts.falloff[1]/distancefromstimulus)**2)
                        stimweightvecs.append(h.Vector().from_python(stimvecs[1]*fallofffactor)) # Scale by the fall-off factor
                        
                        stimrand = h.Random()
                        stimrand.MCellRan4() # If everything has the same seed, should happen at the same time
                        stimrand.negexp(1)
                        stimrand.seq(id32('%d'%(randseed+gid))*1e3) # Set the sequence i.e. seed
                        stimrands.append(stimrand)
                        
                        stimsource = h.NetStim() # Create a NetStim
                        stimsource.interval = ts.rate**-1*1e3 # Interval between spikes
                        stimsource.number = 1e9 # Number of spikes
                        stimsource.noise = ts.noise # Fractional noise in timing
                        stimsource.noiseFromRandom(stimrand) # Set it to use this random number generator
                        stimsources.append(stimsource) # Save this NetStim
                        
                        stimconn = h.NetCon(stimsource, cells[c]) # Connect this noisy input to a cell
                        for r in range(p.nreceptors): stimconn.weight[r]=0 # Initialize weights to 0, otherwise get memory leaks
                        stimweightvecs[-1].play(stimconn._ref_weight[0], stimtimevecs[-1]) # Play most-recently-added vectors into weight
                        stimconn.delay=mindelay # Specify the delay in ms -- shouldn't make a spot of difference
                        stimconns.append(stimconn) # Save this connnection
        
                        if saveraw:
                            stimspikevec = h.Vector() # Initialize vector
                            stimspikevecs.append(stimspikevec) # Keep all those vectors
                            stimrecorder = h.NetCon(stimsource, None)
                            stimrecorder.record(stimspikevec) # Record simulation time
                            stimrecorders.append(stimrecorder)
        print('  Number of stimuli created on host %i: %i' % (g.rank, len(stimsources)))


###############################################################################
### Add background inputs
###############################################################################
def addBackground():
    if g.rank==0: print('Creating background inputs...')
    for c in range(cellsperhost): 
        gid = gidVec[c]
        if cellnames[gid] == 'ASC' or cellnames[gid] == 'DSC' or cellnames[gid] == 'PMd': # These pops won't receive background stimulations.
            continue 
        backgroundrand = h.Random()
        backgroundrand.MCellRan4(gid,gid*2)
        backgroundrand.negexp(1)
        backgroundrands.append(backgroundrand)
        
        backgroundsource = h.NetStim() # Create a NetStim
        backgroundsource.interval = backgroundrate**-1*1e3 # Take inverse of the frequency and then convert from Hz^-1 to ms
        backgroundsource.number = backgroundnumber # Number of spikes
        backgroundsource.noise = backgroundnoise # Fractional noise in timing
        backgroundsource.noiseFromRandom(backgroundrand) # Set it to use this random number generator
        backgroundsources.append(backgroundsource) # Save this NetStim
        
        backgroundconn = h.NetCon(backgroundsource, cells[c]) # Connect this noisy input to a cell
        for r in range(p.nreceptors): backgroundconn.weight[r]=0 # Initialize weights to 0, otherwise get memory leaks
        backgroundconn.weight[backgroundreceptor] = backgroundweight[EorI[gid]] # Specify the weight -- 1 is NMDA receptor for smoother, more summative activation
        backgroundconn.delay=2 # Specify the delay in ms -- shouldn't make a spot of difference
        backgroundconns.append(backgroundconn) # Save this connnection
        
        if saveraw:
            backgroundspikevec = h.Vector() # Initialize vector
            backgroundspikevecs.append(backgroundspikevec) # Keep all those vectors
            backgroundrecorder = h.NetCon(backgroundsource, None)
            backgroundrecorder.record(backgroundspikevec) # Record simulation time
            backgroundrecorders.append(backgroundrecorder)
    print('  Number created on host %i: %i' % (g.rank, len(backgroundsources)))
    pc.barrier()


###############################################################################
### Setup Simulation
###############################################################################
def setupSim():
    global nstdpconns

    ## Initialize STDP -- just for recording
    if usestdp:
        if g.rank==0: print('\nSetting up STDP...')
        if usestdp:
            weightchanges = [[] for ps in range(nstdpconns)] # Create an empty list for each STDP connection -- warning, slow with large numbers of connections!
        for ps in range(nstdpconns): weightchanges[ps].append([0, stdpmechs[ps].synweight]) # Time of save (0=initial) and the weight


    ## Set up LFP recording
    for c in range(cellsperhost): # Loop over each cell and decide which LFP population, if any, it belongs to
        gid = gidVec[c] # Get this cell's GID
        if cellnames[gid] == 'ASC' or cellnames[gid] == 'PMd': # 'ER2' won't be fired by background stimulations.
                continue 
        for pop in range(nlfps): # Loop over each LFP population
            thispop = cellpops[gid] # Population of this cell
            if sum(lfppops[pop]==thispop)>0: # There's a match
                lfpcellids[pop].append(gid) # Flag this cell as belonging to this LFP population


    ## Set up raw recording
    if saveraw: 
        if g.rank==0: print('\nSetting up raw recording...')
        nquantities = 4 # Number of variables from each cell to record from
        # Later this part should be modified because NSLOC doesn't have V, u and I.
        for c in range(cellsperhost):
            gid = gidVec[c] # Get this cell's GID
            if cellnames[gid] == 'ASC' or cellnames[gid] == 'PMd': # NSLOC doesn't have V, u and I
                continue 
            recvecs = [h.Vector() for q in range(nquantities)] # Initialize vectors
            recvecs[0].record(h._ref_t) # Record simulation time
            recvecs[1].record(cells[c]._ref_V) # Record cell voltage
            recvecs[2].record(cells[c]._ref_u) # Record cell recovery variable
            recvecs[3].record(cells[c]._ref_I) # Record cell current
            rawrecordings.append(recvecs) # Keep all those vectors


    ## Set up virtual arm
    if useArm != 'None':
            arm.setup()#duration, loopstep, RLinterval, pc, scale, popnumbers, p)


    ## Communication setup for plexon input
    if usePlexon:
        h('''
            objref cvode
            cvode = new CVode()
            tstop = 0
        ''')

        if isOriginal == 0: # With communication program
            if g.rank == 0: 
                server= server.Manager() # isDp in config.py = 0
                server.start() # launch sever process
                print "Server process completed and callback function initalized"
            e = server.Event() # Queue callback function in the NEURON queue

        
        # Wait for external spikes for PMd from Plexon  
            if g.rank == 0:
                if isCommunication == 1:
                    getServerInfo() # show parameters of the server process
                    print "[Waiting for spikes; run the client on Windows machine...]"
                    while queue.empty(): # only Rank 0 is waiting for spikes in the queue.
                        pass
            pc.barrier() # other workers are waiting here.


###############################################################################
### Run Simulation
###############################################################################
def runSim():
    global timeoflastsave

    if g.rank == 0:
        print('\nRunning...')
    runstart = time() # See how long the run takes
    pc.set_maxstep(10) # MPI: Set the maximum integration time in ms -- not very important
    init() # Initialize the simulation

    while round(h.t) < duration:
        pc.psolve(min(duration,h.t+loopstep)) # MPI: Get ready to run the simulation (it isn't actually run until pc.runworker() is called I think)
        if simMode == 0:
            if g.rank==0 and (round(h.t) % progupdate)==0: print('  t = %0.1f s (%i%%; time remaining: %0.1f s)' % (h.t/1e3, int(h.t/duration*100), (duration-h.t)*(time()-runstart)/h.t))
        else:
            if g.rank==0: print('  t = %0.1f s (%i%%; time remaining: %0.1f s)' % (h.t/1e3, int(h.t/duration*100), (duration-h.t)*(time()-runstart)/h.t))

        # Calculate LFP -- WARNING, need to think about how to optimize
        if savelfps:
            lfptime.append(h.t) # Append current time
            tmplfps = zeros((nlfps)) # Create empty array for storing LFP voltages
            for pop in range(nlfps):
                for c in range(len(lfpcellids[pop])):
                    id = gidDic[lfpcellids[pop][c]]# Index of postynaptic cell -- convert from GID to local
                    tmplfps[pop] += cells[id].V # Add voltage to LFP estimate
                if verbose:
                    if server.np.isnan(tmplfps[pop]) or server.np.isinf(tmplfps[pop]):
                        print "Nan or inf"
            hostlfps.append(tmplfps) # Add voltages

        # Periodic weight saves
        if usestdp: 
            timesincelastsave = h.t - timeoflastsave
            if timesincelastsave>=timebetweensaves:
                timeoflastsave = h.t
                for ps in range(nstdpconns):
                    if stdpmechs[ps].synweight != weightchanges[ps][-1][-1]: # Only store connections that changed; [ps] = this connection; [-1] = last entry; [-1] = weight
                        weightchanges[ps].append([timeoflastsave, stdpmechs[ps].synweight])
        

        ## Virtual arm 
        if useArm != 'None':
            armStart = time()
            arm.run(h.t, pc, cells, gidVec, gidDic, cellsperhost, hostspikevecs) # run virtual arm apparatus (calculate command, move arm, feedback)
            if useRL and (h.t - timeoflastRL >= RLinterval): # if time for next RL
                vec = h.Vector()
                if g.rank == 0:
                    critic = arm.RLcritic() # get critic signal (-1, 0 or 1)
                    pc.broadcast(vec.from_python([critic]), 0) # convert python list to hoc vector for broadcast data received from arm
                    print critic
                else: # other workers
                    pc.broadcast(vec, 0)
                    critic = vec.to_python()[0]
                if critic != 0: # if critic signal indicates punishment (-1) or reward (+1)
                    for stdp in stdpmechs: # for all connections in stdp conn list
                        pass
                        stdp.reward_punish(float(critic)) # run stdp.mod method to update syn weights based on RL
            # Synaptic scaling?
        
            armDur = time() - armStart
            #print(' Arm time = %0.4f s' % armDur)


        ## Time adjustment for online mode simulation
        if usePlexon and simMode == 1:                   
            # To avoid izhi cell's over shooting when h.t moves forward because sim is slow.
            for c in range(cellsperhost): 
                gid = gidVec[c]
                if cellnames[gid] == 'PMd': # 'PMds don't have t0 variable.
                    continue
                cells[c].t0 = newCurrTime.value - h.dt             
            dtSave = h.dt # save original dt
            h.dt = newCurrTime.value - h.t # new dt
            active = h.cvode.active()
            if active != 0:
                h.cvode.active(0)         
            h.fadvance() # Integrate with new dt
            if active != 0:
                h.cvode.active(1)         
            h.dt = dtSave # Restore orignal dt   
                
    runtime = time()-runstart # See how long it took
    if g.rank==0: print('  Done; run time = %0.1f s; real-time ratio: %0.2f.' % (runtime, duration/1000/runtime))
    pc.barrier() # Wait for all hosts to get to this point


###############################################################################
### Finalize Simulation  (gather data from nodes, etc.)
###############################################################################
def finalizeSim():
    ## Pack data from all hosts
    if g.rank==0: print('\nGathering spikes...')
    gatherstart = time() # See how long it takes to plot
    for host in range(nhosts): # Loop over hosts
        if host==g.rank: # Only act on a single host
            hostspikecells=array([])
            hostspiketimes=array([])
            for c in range(len(hostspikevecs)):
                thesespikes = array(hostspikevecs[c]) # Convert spike times to an array
                nthesespikes = len(thesespikes) # Find out how many of spikes there were for this cell
                hostspiketimes = concatenate((hostspiketimes, thesespikes)) # Add spikes from this cell to the list
                #hostspikecells = concatenate((hostspikecells, (c+host*cellsperhost)*ones(nthesespikes))) # Add this cell's ID to the list
                hostspikecells = concatenate((hostspikecells, gidVec[c]*ones(nthesespikes))) # Add this cell's ID to the list
                if saveraw:
                    for q in range(nquantities):
                        rawrecordings[c][q] = array(rawrecordings[c][q])
            messageid=pc.pack([hostspiketimes, hostspikecells, hostlfps, conndata, stdpconndata, weightchanges, rawrecordings]) # Create a mesage ID and store this value
            pc.post(host,messageid) # Post this message


    ## Unpack data from all hosts
    if g.rank==0: # Only act on a single host
        allspikecells = array([])
        allspiketimes = array([])
        lfps = zeros((len(lfptime),nlfps)) # Create an empty array for appending LFP data; first entry is for time
        allconnections = [array([]) for i in range(nconnpars)] # Store all connections
        allconnections[nconnpars-1] = zeros((0,p.nreceptors)) # Create an empty array for appending connections
        allstdpconndata = zeros((0,3)) # Create an empty array for appending STDP connection data
        if usestdp: weightchanges = []
        if saveraw: allraw = []
        for host in range(nhosts): # Loop over hosts
            pc.take(host) # Get the last message
            hostdata = pc.upkpyobj() # Unpack them
            allspiketimes = concatenate((allspiketimes, hostdata[0])) # Add spikes from this cell to the list
            allspikecells = concatenate((allspikecells, hostdata[1])) # Add this cell's ID to the list
            if savelfps: lfps += array(hostdata[2]) # Sum LFP voltages
            for pp in range(nconnpars): allconnections[pp] = concatenate((allconnections[pp], hostdata[3][pp])) # Append pre/post synapses
            if usestdp and len(hostdata[4]): # Using STDP and at least one STDP connection
                allstdpconndata = concatenate((allstdpconndata, hostdata[4])) # Add data on STDP connections
                for ps in range(len(hostdata[4])): weightchanges.append(hostdata[5][ps]) # "ps" stands for "plastic synapse"
            if saveraw:
                for c in range(len(hostdata[6])): allraw.append(hostdata[6][c]) # Append cell-by-cell

        totalspikes = len(allspiketimes) # Keep a running tally of the number of spikes
        totalconnections = len(allconnections[0]) # Total number of connections
        totalstdpconns = len(allstdpconndata) # Total number of STDP connections
        

        # Record input spike times
        if saveraw and usebackground:
            allbackgroundspikecells=array([])
            allbackgroundspiketimes=array([])
            for c in range(len(backgroundspikevecs)):
                thesespikes = array(backgroundspikevecs[c])
                allbackgroundspiketimes = concatenate((allbackgroundspiketimes, thesespikes)) # Add spikes from this stimulator to the list
                allbackgroundspikecells = concatenate((allbackgroundspikecells, c+zeros(len(thesespikes)))) # Add this cell's ID to the list
            backgrounddata = transpose(vstack([allbackgroundspikecells,allbackgroundspiketimes]))
        else: backgrounddata = [] # For saving s no error
        
        if saveraw and usestims:
            allstimspikecells=array([])
            allstimspiketimes=array([])
            for c in range(len(stimspikevecs)):
                thesespikes = array(stimspikevecs[c])
                allstimspiketimes = concatenate((allstimspiketimes, thesespikes)) # Add spikes from this stimulator to the list
                allstimspikecells = concatenate((allstimspikecells, c+zeros(len(thesespikes)))) # Add this cell's ID to the list
            stimspikedata = transpose(vstack([allstimspikecells,allstimspiketimes]))
        else: stimspikedata = [] # For saving so no error
    gathertime = time()-gatherstart # See how long it took
    if g.rank==0: print('  Done; gather time = %0.1f s.' % gathertime)
    pc.barrier()

    print 'min delay for node ',g.rank,' is ', pc.set_maxstep(10)
    mindelay = pc.allreduce(pc.set_maxstep(10), 2) # flag 2 returns minimum value
    if g.rank==0: print 'Minimum delay (time-step for queue exchange) is ',mindelay

    ## Run and clean up
    pc.runworker() # MPI: Start simulations running on each host
    pc.done() # MPI: Close MPI


    ## Finalize virtual arm (eg. close pipes, saved data)
    if useArm != 'None':
      arm.close()


    # terminate the server process
    if usePlexon:
      if isOriginal == 0:
          server.stop()

    ## Print statistics
    print('\nAnalyzing...')
    firingrate = float(totalspikes)/ncells/duration*1e3 # Calculate firing rate -- confusing but cool Python trick for iterating over a list
    connspercell = totalconnections/float(ncells) # Calculate the number of connections per cell
    print('  Run time: %0.1f s (%i-s sim; %i scale; %i cells; %i workers)' % (runtime, duration/1e3, scale, ncells, nhosts))
    print('  Spikes: %i (%0.2f Hz)' % (totalspikes, firingrate))
    print('  Connections: %i (%i STDP; %0.2f per cell)' % (totalconnections, totalstdpconns, connspercell))
    print('  Mean connection distance: %0.2f um' % mean(allconnections[2]))
    print('  Mean connection delay: %0.2f ms' % mean(allconnections[3]))


###############################################################################
### Save data
###############################################################################
def saveData():
    ## Save to txt file (spikes and conn)
    if savetxt: 
        filename = 'data/m1ms-spk.txt'
        fd = open(filename, "w")
        for c in range(len(allspiketimes)):
            print >> fd, int(allspikecells[c]), allspiketimes[c], p.popNamesDic[cellnames[int(allspikecells[c])]]
        fd.close()
        print "[Spikes are stored in", filename, "]"

        if verbose:
            filename = 'm1ms-conn.txt'
            fd = open(filename, "w")
            for c in range(len(allconnections[0])):
                print >> fd, int(allconnections[0][c]), int(allconnections[1][c]), allconnections[2][c], allconnections[3][c], allconnections[4][c] 
            fd.close()
            print "[Connections are stored in", filename, "]"

    ## Save to mat file
    if savemat:
        print('Saving output as %s...' % filename)
        savestart = time() # See how long it takes to save
        from scipy.io import savemat # analysis:ignore -- because used in exec() statement
        
        # Save simulation code
        filestosave = ['model.py','cellpopdata.py', 'izhi.py', 'izhi.mod', 'stdp.mod', 'nsloc.py', 'nsloc.mod'] # Files to save
        simcode = [argv, filestosave] # Start off with input parameters, if any, and then the list of files being saved
        for f in range(len(filestosave)): # Loop over each file
            fobj = open(filestosave[f]) # Open it for reading
            simcode.append(fobj.readlines()) # Append to list of code to save
            fobj.close() # Close file object
        
        # Tidy variables
        spikedata = vstack([allspikecells,allspiketimes]).T # Put spike data together
        connections = vstack([allconnections[0],allconnections[1]]).T # Put connection data together
        distances = allconnections[2] # Pull out distances
        delays = allconnections[3] # Pull out delays
        weights = allconnections[4] # Pull out weights
        stdpdata = allstdpconndata # STDP connection data
        if usestims: stimdata = [vstack(stimstruct[c][1]).T for c in range(len(stimstruct))] # Only pull out vectors, not text, in stimdata

        # Save variables
        info = {'timestamp':datetime.today().strftime("%d %b %Y %H:%M:%S"), 'runtime':runtime, 'arguments':argv[:], 'popnames':p.popnames, 'popEorI':p.popEorI} # Save date, runtime, and input arguments
        variablestosave = ['info', 'simcode', 'spikedata', 'cellpops', 'cellnames', 'cellclasses', 'xlocs', 'ylocs', 'zlocs', 'connections', 'distances', 'delays', 'weights', 'EorI']
        if savelfps:  variablestosave.extend(['lfptime', 'lfps'])   
        if usestdp: variablestosave.extend(['stdpdata', 'weightchanges'])
        if saveraw: variablestosave.extend(['backgrounddata', 'stimspikedata', 'allraw'])
        if usestims: variablestosave.extend(['stimdata'])
        savecommand = "savemat(filename, {"
        for var in range(len(variablestosave)): savecommand += "'" + variablestosave[var] + "':" + variablestosave[var] + ", " # Create command out of all the variables
        savecommand = savecommand[:-2] + "}, oned_as='column')" # Omit final comma-space and complete command
        exec(savecommand) # Actually perform the save
        
        savetime = time()-savestart # See how long it took to save
        print('  Done; time = %0.1f s' % savetime)


###############################################################################
### Plot data
###############################################################################
def plotData():
    ## Plotting
    if plotraster: # Whether or not to plot
        if (totalspikes>maxspikestoplot): 
            disp('  Too many spikes (%i vs. %i)' % (totalspikes, maxspikestoplot)) # Plot raster, but only if not too many spikes
        elif nhosts>1: 
            disp('  Plotting raster despite using too many cores (%i)' % nhosts) 
            analysis.plotraster(allspiketimes, allspikecells, EorI, ncells, connspercell, backgroundweight, firingrate, duration)
        else: 
            print('Plotting raster...')
            analysis.plotraster(allspiketimes, allspikecells, EorI, ncells, connspercell, backgroundweight, firingrate, duration)

    if plotconn:
        print('Plotting connectivity matrix...')
        analysis.plotconn(p)

    if plotweightchanges:
        print('Plotting weight changes...')
        analysis.plotweightchanges(p, allconnections, allstdpconndata, weightchanges)

    show()


