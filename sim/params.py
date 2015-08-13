"""
sim.py 

list of model objects (paramaters and variables) to be shared across modules
Can modified manually or via arguments from main.py

Contributors: salvadordura@gmail.com
"""

from pylab import array, inf
from neuron import h # Import NEURON

loadNetParams = 0  # either load network params from file or set them here (and save to file)
loadSimParams = 0  # either load sim params from file or set them here (and save to file)

net = {}  # dictionary to store network params
sim = {}  # dictionary to store simulation params

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
    net['scale'] = 1 # Size of simulation in thousands of cells
    net['cortthaldist']=3000 # Distance from relay nucleus to cortex -- ~1 cm = 10,000 um (check)
    net['corticalthick'] = 1740 # cortical thickness/depth


    ## Background input parameters
    net['useBackground'] = True # Whether or not to use background stimuli
    net['backgroundRate'] = 5 # Rate of stimuli (in Hz)
    net['backgroundRateMin'] = 0.1 # Rate of stimuli (in Hz)
    net['backgroundNumber'] = 1e10 # Number of spikes
    net['backgroundNoise'] = 1 # Fractional noise
    net['backgroundWeight'] = 0.1*array([1,0.1]) # Weight for background input for E cells and I cells
    net['backgroundReceptor'] = NMDA # Which receptor to stimulate


    # simType is used to select between the population and conn params for different types of models (simple HH vs M1 izhikevich)
    simType = 'mpiHHTut' # 'mpiHHTut' or 'M1model'
    #simType = 'M1model' # 'mpiHHTut' or 'M1model'


    # mpiHHTut
    if simType == 'mpiHHTut':
        net['ncell']   = 100  
        net['popType'] = 'Basic' # REMOVE - infer from net dict keys
        net['popParams'] = []

                    # popid,    cell model, num cells
        net['popParams'].append([0,    HH,         net['ncell']]) # 
        
        ## Connectivity parameters
        net['connType'] = 'random'
        net['numReceptors'] = 1
        net['maxcons']   = 20                   # number of connections onto each cell
        net['weight']    = 0.004                # weight of each connection
        net['delaymean'] = 13.0                 # mean of delays
        net['delayvar']  = 1.4                  # variance of delays
        net['delaymin']  = 0.2                  # miniumum delays
        net['threshold'] = 10.0                 # threshold 


    # yfrac-based M1 model
    elif simType == 'M1model':
        net['popType'] = 'Yfrac'
        net['popParams'] = []

                       # popid, cell model,     EorI, topClass, subClass, yfracRange,     density,                
        net['popParams'].append([0,    Izhi2007b,      E,    IT,       other,    [0.1, 0.26],    lambda x:2e3*x]) #  L2/3 IT
        net['popParams'].append([1,    Izhi2007b,      E,    IT,       other,    [0.26, 0.31],   lambda x:2e3*x]) #  L4 IT
        net['popParams'].append([2,    Izhi2007b,      E,    IT,       other,    [0.31, 0.52],   lambda x:2e3*x]) #  L5A IT
        net['popParams'].append([3,    Izhi2007b,      E,    IT,       other,    [0.52, 0.77],   lambda x:1e3*x]) #  L5B IT
        net['popParams'].append([4,    Izhi2007b,      E,    PT,       other,    [0.52, 0.77],   lambda x:1e3]) #  L5B PT
        net['popParams'].append([5,    Izhi2007b,      E,    IT,       other,    [0.77, 1.0],    lambda x:1e3]) #  L6 IT
        net['popParams'].append([6,    Izhi2007b,      I,    Pva,      Basket,   [0.1, 0.31],    lambda x:0.5e3]) #  L2/3 Pva (FS)
        net['popParams'].append([7,    Izhi2007b,      I,    Sst,      Marti,    [0.1, 0.31],    lambda x:0.5e3]) #  L2/3 Sst (LTS)
        net['popParams'].append([8,    Izhi2007b,      I,    Pva,      Basket,   [0.31, 0.77],   lambda x:0.5e3]) #  L5 Pva (FS)
        net['popParams'].append([9,    Izhi2007b,      I,    Sst,      Marti,    [0.31, 0.77],   lambda x:0.5e3]) #  L5 Sst (LTS)
        net['popParams'].append([10,   Izhi2007b,      I,    Pva,      Basket,   [0.77, 1.0],    lambda x:0.5e3]) #  L6 Pva (FS)
        net['popParams'].append([11,   Izhi2007b,      I,    Sst,      Marti,    [0.77, 1.0],    lambda x:0.5e3]) #  L6 Sst (LTS)

        
        ## Connectivity parameters
        net['connType'] = 'yfrac'
        net['numReceptors'] = 1 
        net['useconnprobdata'] = True # Whether or not to use connectivity data
        net['useconnweightdata'] = True # Whether or not to use weight data
        net['mindelay'] = 2 # Minimum connection delay, in ms
        net['velocity'] = 100 # Conduction velocity in um/ms (e.g. 50 = 0.05 m/s)
        net['modelsize'] = 1000*net['scale'] # Size of network in um (~= 1000 neurons/column where column = 500um width)
        net['sparseness'] = 0.1 # fraction of cells represented (num neurons = density * modelsize * sparseness)
        net['scaleconnweight'] = 0.00025*array([[2, 1], [2, 0.1]]) # Connection weights for EE, EI, IE, II synapses, respectively
        net['receptorweight'] = [1, 1, 1, 1, 1] # Scale factors for each receptor
        net['scaleconnprob'] = 1/net['scale']*array([[1, 1], [1, 1]]) # scale*1* Connection probabilities for EE, EI, IE, II synapses, respectively -- scale for scale since size fixed
        net['connfalloff'] = 100*array([2, 3]) # Connection length constants in um for E and I synapses, respectively
        net['toroidal'] = False # Whether or not to have toroidal topology


        # class variables to store matrix of connection probabilities (constant or function) for pre and post cell topClass
        net['connProbs']=[[(lambda x: 0)]*numTopClass]*numTopClass
        net['connProbs'][IT][IT]   = (lambda x,y: 0.1*x+0.01/y)  # example of yfrac-dep function (x=presyn yfrac, y=postsyn yfrac)
        net['connProbs'][IT][PT]   = (lambda x,y: 0.02*x if (x>0.5 and x<0.8) else 0)
        net['connProbs'][IT][CT]   = (lambda x,y: 0.1)  # constant function
        net['connProbs'][IT][Pva]  = (lambda x,y: 0.1)
        net['connProbs'][IT][Sst]  = (lambda x,y: 0.1)
        net['connProbs'][PT][IT]   = (lambda x,y: 0)
        net['connProbs'][PT][PT]   = (lambda x,y: 0.1)
        net['connProbs'][PT][CT]   = (lambda x,y: 0)
        net['connProbs'][PT][Pva]  = (lambda x,y: 0.1)
        net['connProbs'][PT][Sst]  = (lambda x,y: 0.1)
        net['connProbs'][CT][IT]   = (lambda x,y: 0.1)
        net['connProbs'][CT][PT]   = (lambda x,y: 0)
        net['connProbs'][CT][CT]   = (lambda x,y: 0.1)
        net['connProbs'][CT][Pva]  = (lambda x,y: 0.1)
        net['connProbs'][CT][Sst]  = (lambda x,y: 0.1)
        net['connProbs'][Pva][IT]  = (lambda x,y: 0.1)
        net['connProbs'][Pva][PT]  = (lambda x,y: 0.1)
        net['connProbs'][Pva][CT]  = (lambda x,y: 0.1)
        net['connProbs'][Pva][Pva] = (lambda x,y: 0.1)
        net['connProbs'][Pva][Sst] = (lambda x,y: 0.1)
        net['connProbs'][Sst][IT]  = (lambda x,y: 0.1)
        net['connProbs'][Sst][PT]  = (lambda x,y: 0.1)
        net['connProbs'][Sst][CT]  = (lambda x,y: 0.1)
        net['connProbs'][Sst][Pva] = (lambda x,y: 0.1)
        net['connProbs'][Sst][Sst] = (lambda x,y: 0.1)

        # class variables to store matrix of connection weights (constant or function) for pre and post cell topClass
        #connWeights=zeros((numTopClass,numTopClass,numReceptors))
        net['connWeights']=[[[(lambda x,y: 0)]*net['numReceptors']]*numTopClass]*numTopClass    
        net['connWeights'][IT][IT][AMPA]   = (lambda x,y: 1)
        net['connWeights'][IT][PT][AMPA]   = (lambda x,y: 1)
        net['connWeights'][IT][CT][AMPA]   = (lambda x,y: 1)
        net['connWeights'][IT][Pva][AMPA]  = (lambda x,y: 1)
        net['connWeights'][IT][Sst][AMPA]  = (lambda x,y: 1)
        net['connWeights'][PT][IT][AMPA]   = (lambda x,y: 0)
        net['connWeights'][PT][PT][AMPA]   = (lambda x,y: 1)
        net['connWeights'][PT][CT][AMPA]   = (lambda x,y: 0)
        net['connWeights'][PT][Pva][AMPA]  = (lambda x,y: 1)
        net['connWeights'][PT][Sst][AMPA]  = (lambda x,y: 1)
        net['connWeights'][CT][IT][AMPA]   = (lambda x,y: 1)
        net['connWeights'][CT][PT][AMPA]   = (lambda x,y: 0)
        net['connWeights'][CT][CT][AMPA]   = (lambda x,y: 1)
        net['connWeights'][CT][Pva][AMPA]  = (lambda x,y: 1)
        net['connWeights'][CT][Sst][AMPA]  = (lambda x,y: 1)
        net['connWeights'][Pva][IT][GABAA]  = (lambda x,y: 1)
        net['connWeights'][Pva][PT][GABAA]  = (lambda x,y: 1)
        net['connWeights'][Pva][CT][GABAA]  = (lambda x,y: 1)
        net['connWeights'][Pva][Pva][GABAA] = (lambda x,y: 1)
        net['connWeights'][Pva][Sst][GABAA] = (lambda x,y: 1)
        net['connWeights'][Sst][IT][GABAB]  = (lambda x,y: 1)
        net['connWeights'][Sst][PT][GABAB]  = (lambda x,y: 1)
        net['connWeights'][Sst][CT][GABAB]  = (lambda x,y: 1)
        net['connWeights'][Sst][Pva][GABAB] = (lambda x,y: 1)
        net['connWeights'][Sst][Sst][GABAB] = (lambda x,y: 1)



###############################################################################
### SET SIMULATION PARAMETERS
###############################################################################

if loadSimParams:  # load network params from file
    pass
else:
    ## Recording 
    if simType == 'mpiHHTut':
        sim['recdict'] = {'Vsoma':'soma(0.5)._ref_v'}
    elif simType == 'M1model':
        sim['recdict'] = {'V':'sec(0.5)._ref_v', 'u':'m._ref_u', 'I':'m._ref_i'}


    # Simulation parameters
    sim['duration'] = sim['tstop'] = 1*1e3 # Duration of the simulation, in ms
    h.dt = sim['dt'] = 0.5 # Internal integration timestep to use
    sim['recordStep'] = 10 # Step size in ms to save data (eg. V traces, LFP, etc)
    sim['saveFileStep'] = 1000 # step size in ms to save data to disk
    sim['randseed'] = 1 # Random seed to use


    ## Saving and plotting parameters
    sim['filename'] = '../data/m1ms'  # Set file output name
    sim['savemat'] = True # Whether or not to write spikes etc. to a .mat file
    sim['savetxt'] = False # save spikes and conn to txt file
    sim['savedpk'] = True # save to a .dpk pickled file
    sim['recordTraces'] = True  # whether to record cell traces or not
    #lfppops = [[ER2], [ER5], [EB5], [ER6]] # Populations for calculating the LFP from
    sim['saveBackground'] = False # save background (NetStims) inputs
    sim['verbose'] = 0 # Whether to write nothing (0), diagnostic information on events (1), or everything (2) a file directly from izhi.mod
    sim['plotraster'] = True # Whether or not to plot a raster
    sim['plotpsd'] = False # plot power spectral density
    sim['maxspikestoplot'] = 3e8 # Maximum number of spikes to plot
    sim['plotconn'] = False # whether to plot conn matrix
    sim['plotweightchanges'] = False # whether to plot weight changes (shown in conn matrix)
    sim['plot3darch'] = False # plot 3d architecture


    ## Stimulus parameters
    sim['usestims'] = False # Whether or not to use stimuli at all
    sim['ltptimes']  = [5, 10] # Pre-microstim touch times
    sim['ziptimes'] = [10, 15] # Pre-microstim touch times

