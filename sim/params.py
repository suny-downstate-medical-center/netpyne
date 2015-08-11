"""
sim.py 

list of model objects (paramaters and variables) to be shared across modules
Can modified manually or via arguments from main.py

Version: 2015may26 by salvadordura@gmail.com
"""

from pylab import array, inf
from neuron import h # Import NEURON

loadNetParams = 0  # either load network params from file or set them here (and save to file)
loadSimParams = 0  # either load sim params from file or set them here (and save to file)


###############################################################################
### SET NETWORK PARAMETERS
###############################################################################

if loadNetParams:  # load network params from file
    pass
else:  # set network params manually
    # Store equivalence between names and values so can be used as indices
    #AMPA=0; NMDA=1; GABAA=2; GABAB=3; # synaptic receptors
    AMPA=0; NMDA=0; GABAA=0; GABAB=0;   # synaptic receptors
    E=0; I=1  # excitatory vs inhibitory
    IT=0; PT=1; CT=2; HTR=3; Pva=4; Sst=5; numTopClass=6  # cell/pop top class 
    L4=0; other=1; Vip=2; Nglia=3; Basket=4; Chand=5; Marti=6; L4Sst=7  # cell/pop sub class
    Izhi2007a=0; Izhi2007b=1; Friesen=2; HH=3  # types of cell model

    ## Position parameters
    scale = 1 # Size of simulation in thousands of cells
    cortthaldist=3000 # Distance from relay nucleus to cortex -- ~1 cm = 10,000 um (check)
    corticalthick = 1740 # cortical thickness/depth


    ## Background input parameters
    useBackground = True # Whether or not to use background stimuli
    backgroundRate = 5 # Rate of stimuli (in Hz)
    backgroundRateMin = 0.1 # Rate of stimuli (in Hz)
    backgroundNumber = 1e10 # Number of spikes
    backgroundNoise = 1 # Fractional noise
    backgroundWeight = 0.1*array([1,0.1]) # Weight for background input for E cells and I cells
    backgroundReceptor = NMDA # Which receptor to stimulate


    # Population and conn params to reproduce different types of sim
    #simType = 'mpiHHTut' # 'mpiHHTut' or 'M1model'
    simType = 'M1model' # 'mpiHHTut' or 'M1model'


    # mpiHHTut
    if simType == 'mpiHHTut':
        ncell   = 100  
        popType = 'Basic'
        popParams = []

                    # popid,    cell model, num cells
        popParams.append([0,    HH,         ncell]) # 
        
        ## Connectivity parameters
        connType = 'random'
        numReceptors = 1
        maxcons   = 20                   # number of connections onto each cell
        weight    = 0.004                # weight of each connection
        delaymean = 13.0                 # mean of delays
        delayvar  = 1.4                  # variance of delays
        delaymin  = 0.2                  # miniumum delays
        threshold = 10.0                 # threshold 


    # yfrac-based M1 model
    elif simType == 'M1model':
        popType = 'Yfrac'
        popParams = []

                       # popid, cell model,     EorI, topClass, subClass, yfracRange,     density,                
        popParams.append([0,    Izhi2007b,      E,    IT,       other,    [0.1, 0.26],    lambda x:2e3*x]) #  L2/3 IT
        popParams.append([1,    Izhi2007b,      E,    IT,       other,    [0.26, 0.31],   lambda x:2e3*x]) #  L4 IT
        popParams.append([2,    Izhi2007b,      E,    IT,       other,    [0.31, 0.52],   lambda x:2e3*x]) #  L5A IT
        popParams.append([3,    Izhi2007b,      E,    IT,       other,    [0.52, 0.77],   lambda x:1e3*x]) #  L5B IT
        popParams.append([4,    Izhi2007b,      E,    PT,       other,    [0.52, 0.77],   lambda x:1e3]) #  L5B PT
        popParams.append([5,    Izhi2007b,      E,    IT,       other,    [0.77, 1.0],    lambda x:1e3]) #  L6 IT
        popParams.append([6,    Izhi2007b,      I,    Pva,      Basket,   [0.1, 0.31],    lambda x:0.5e3]) #  L2/3 Pva (FS)
        popParams.append([7,    Izhi2007b,      I,    Sst,      Marti,    [0.1, 0.31],    lambda x:0.5e3]) #  L2/3 Sst (LTS)
        popParams.append([8,    Izhi2007b,      I,    Pva,      Basket,   [0.31, 0.77],   lambda x:0.5e3]) #  L5 Pva (FS)
        popParams.append([9,    Izhi2007b,      I,    Sst,      Marti,    [0.31, 0.77],   lambda x:0.5e3]) #  L5 Sst (LTS)
        popParams.append([10,   Izhi2007b,      I,    Pva,      Basket,   [0.77, 1.0],    lambda x:0.5e3]) #  L6 Pva (FS)
        popParams.append([11,   Izhi2007b,      I,    Sst,      Marti,    [0.77, 1.0],    lambda x:0.5e3]) #  L6 Sst (LTS)

        
        ## Connectivity parameters
        connType = 'yfrac'
        numReceptors = 1 
        useconnprobdata = True # Whether or not to use connectivity data
        useconnweightdata = True # Whether or not to use weight data
        mindelay = 2 # Minimum connection delay, in ms
        velocity = 100 # Conduction velocity in um/ms (e.g. 50 = 0.05 m/s)
        modelsize = 1000*scale # Size of network in um (~= 1000 neurons/column where column = 500um width)
        sparseness = 0.1 # fraction of cells represented (num neurons = density * modelsize * sparseness)
        scaleconnweight = 0.00025*array([[2, 1], [2, 0.1]]) # Connection weights for EE, EI, IE, II synapses, respectively
        receptorweight = [1, 1, 1, 1, 1] # Scale factors for each receptor
        scaleconnprob = 1/scale*array([[1, 1], [1, 1]]) # scale*1* Connection probabilities for EE, EI, IE, II synapses, respectively -- scale for scale since size fixed
        connfalloff = 100*array([2, 3]) # Connection length constants in um for E and I synapses, respectively
        toroidal = False # Whether or not to have toroidal topology


        # class variables to store matrix of connection probabilities (constant or function) for pre and post cell topClass
        connProbs=[[(lambda x: 0)]*numTopClass]*numTopClass
        connProbs[IT][IT]   = (lambda x,y: 0.1*x+0.01/y)  # example of yfrac-dep function (x=presyn yfrac, y=postsyn yfrac)
        connProbs[IT][PT]   = (lambda x,y: 0.02*x if (x>0.5 and x<0.8) else 0)
        connProbs[IT][CT]   = (lambda x,y: 0.1)  # constant function
        connProbs[IT][Pva]  = (lambda x,y: 0.1)
        connProbs[IT][Sst]  = (lambda x,y: 0.1)
        connProbs[PT][IT]   = (lambda x,y: 0)
        connProbs[PT][PT]   = (lambda x,y: 0.1)
        connProbs[PT][CT]   = (lambda x,y: 0)
        connProbs[PT][Pva]  = (lambda x,y: 0.1)
        connProbs[PT][Sst]  = (lambda x,y: 0.1)
        connProbs[CT][IT]   = (lambda x,y: 0.1)
        connProbs[CT][PT]   = (lambda x,y: 0)
        connProbs[CT][CT]   = (lambda x,y: 0.1)
        connProbs[CT][Pva]  = (lambda x,y: 0.1)
        connProbs[CT][Sst]  = (lambda x,y: 0.1)
        connProbs[Pva][IT]  = (lambda x,y: 0.1)
        connProbs[Pva][PT]  = (lambda x,y: 0.1)
        connProbs[Pva][CT]  = (lambda x,y: 0.1)
        connProbs[Pva][Pva] = (lambda x,y: 0.1)
        connProbs[Pva][Sst] = (lambda x,y: 0.1)
        connProbs[Sst][IT]  = (lambda x,y: 0.1)
        connProbs[Sst][PT]  = (lambda x,y: 0.1)
        connProbs[Sst][CT]  = (lambda x,y: 0.1)
        connProbs[Sst][Pva] = (lambda x,y: 0.1)
        connProbs[Sst][Sst] = (lambda x,y: 0.1)

        # class variables to store matrix of connection weights (constant or function) for pre and post cell topClass
        #connWeights=zeros((numTopClass,numTopClass,numReceptors))
        connWeights=[[[(lambda x,y: 0)]*numReceptors]*numTopClass]*numTopClass    
        connWeights[IT][IT][AMPA]   = (lambda x,y: 1)
        connWeights[IT][PT][AMPA]   = (lambda x,y: 1)
        connWeights[IT][CT][AMPA]   = (lambda x,y: 1)
        connWeights[IT][Pva][AMPA]  = (lambda x,y: 1)
        connWeights[IT][Sst][AMPA]  = (lambda x,y: 1)
        connWeights[PT][IT][AMPA]   = (lambda x,y: 0)
        connWeights[PT][PT][AMPA]   = (lambda x,y: 1)
        connWeights[PT][CT][AMPA]   = (lambda x,y: 0)
        connWeights[PT][Pva][AMPA]  = (lambda x,y: 1)
        connWeights[PT][Sst][AMPA]  = (lambda x,y: 1)
        connWeights[CT][IT][AMPA]   = (lambda x,y: 1)
        connWeights[CT][PT][AMPA]   = (lambda x,y: 0)
        connWeights[CT][CT][AMPA]   = (lambda x,y: 1)
        connWeights[CT][Pva][AMPA]  = (lambda x,y: 1)
        connWeights[CT][Sst][AMPA]  = (lambda x,y: 1)
        connWeights[Pva][IT][GABAA]  = (lambda x,y: 1)
        connWeights[Pva][PT][GABAA]  = (lambda x,y: 1)
        connWeights[Pva][CT][GABAA]  = (lambda x,y: 1)
        connWeights[Pva][Pva][GABAA] = (lambda x,y: 1)
        connWeights[Pva][Sst][GABAA] = (lambda x,y: 1)
        connWeights[Sst][IT][GABAB]  = (lambda x,y: 1)
        connWeights[Sst][PT][GABAB]  = (lambda x,y: 1)
        connWeights[Sst][CT][GABAB]  = (lambda x,y: 1)
        connWeights[Sst][Pva][GABAB] = (lambda x,y: 1)
        connWeights[Sst][Sst][GABAB] = (lambda x,y: 1)



###############################################################################
### SET SIMULATION PARAMETERS
###############################################################################

if loadSimParams:  # load network params from file
    pass
else:
    ## Recording 
    if simType == 'mpiHHTut':
        recdict = {'Vsoma':'soma(0.5)._ref_v'}
    elif simType == 'M1model':
        recdict = {'V':'sec(0.5)._ref_v', 'u':'m._ref_u', 'I':'m._ref_i'}


    # Simulation parameters
    duration = tstop = 1*1e3 # Duration of the simulation, in ms
    h.dt = 0.5 # Internal integration timestep to use
    recordStep = 10 # Step size in ms to save data (eg. V traces, LFP, etc)
    saveFileStep = 1000 # step size in ms to save data to disk
    randseed = 1 # Random seed to use


    ## Saving and plotting parameters
    outfilestem = '' # filestem to save fitness result
    savemat = True # Whether or not to write spikes etc. to a .mat file
    savetxt = False # save spikes and conn to txt file
    savedpk = True # save to a .dpk pickled file
    recordTraces = True  # whether to record cell traces or not
    #lfppops = [[ER2], [ER5], [EB5], [ER6]] # Populations for calculating the LFP from
    saveBackground = False # save background (NetStims) inputs
    verbose = 0 # Whether to write nothing (0), diagnostic information on events (1), or everything (2) a file directly from izhi.mod
    filename = '../data/m1ms'  # Set file output name
    plotraster = True # Whether or not to plot a raster
    plotpsd = False # plot power spectral density
    maxspikestoplot = 3e8 # Maximum number of spikes to plot
    plotconn = False # whether to plot conn matrix
    plotweightchanges = False # whether to plot weight changes (shown in conn matrix)
    plot3darch = False # plot 3d architecture


    ## Stimulus parameters
    usestims = False # Whether or not to use stimuli at all
    ltptimes  = [5, 10] # Pre-microstim touch times
    ziptimes = [10, 15] # Pre-microstim touch times

