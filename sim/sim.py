from neuron import h # Import NEURON
import sys
from numpy import mean, zeros
from time import time
import pickle
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
### Gather data from nodes
###############################################################################
def gatherData():
    ## Pack data from all hosts
    if s.rank==0: 
        print('\nGathering spikes...')
        gatherstart = time() # See how long it takes to plot

    data=[None]*s.nhosts # using None is important for mem and perf of pc.alltoall() when data is sparse
    data[0]={} # make a new dict
    for k,v in s.simdata.iteritems():   data[0][k] = v 
    gather=s.pc.py_alltoall(data)
    s.pc.barrier()
    for v in s.simdata.itervalues(): v.resize(0)
    if s.rank==0: 
        gdict = {}
        [gdict.update(d) for d in gather] # this will now repeated needlessly overwrite 'spkt' and 'spkid'
        gdict.update({'spkt' : concatenate([d['spkt']  for d in gather]), 
               'spkid': concatenate([d['spkid'] for d in gather])})
        if not gdict.has_key('run'): gdict.update({'run':{'saveStep':s.saveStep, 'dt':h.dt, 'randseed':s.randseed, 'duration':s.duration}}) # eventually save full params (p)
                                                 # 'recdict':recdict, 'Vrecc': Vrecc}}) # save major run attributes
        gdict.update({'t':h.t, 'walltime':datetime.now().ctime()})

        gathertime = time()-gatherstart # See how long it took
        print('  Done; gather time = %0.1f s.' % gathertime)
    #s.pc.barrier()

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