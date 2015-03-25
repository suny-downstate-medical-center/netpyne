"""
globals.py 

list of model objects (paramaters and variables) to be shared across modules
Can modified manually or via arguments from main.py

Version: 2015feb12 by salvadord
"""

###############################################################################
### IMPORT MODULES
###############################################################################

from pylab import array, inf, zeros, seed
from neuron import h # Import NEURON
from izhi import pyramidal, fastspiking, lowthreshold, thalamocortical, reticular # Import Izhikevich model
from nsloc import nsloc # NetStim with location unit type
import server # Server for plexon interface
from time import time
from math import radians
import hashlib
def id32(obj): return int(hashlib.md5(obj).hexdigest()[0:8],16)# hash(obj) & 0xffffffff # for random seeds (bitwise AND to retain only lower 32 bits)


## MPI
pc = h.ParallelContext() # MPI: Initialize the ParallelContext class
nhosts = int(pc.nhost()) # Find number of hosts
rank = int(pc.id())     # rank 0 will be the master

if rank==0: 
    pc.gid_clear()
    print('\nSetting parameters...')

###############################################################################
### CELL AND POPULATION PARAMETERS
###############################################################################

# Set population and receptor quantities
scale = 1 # Size of simulation in thousands of cells

popnames = ['PMd', 'ASC', 'EDSC', 'IDSC', 'ER2', 'IF2', 'IL2', 'ER5', 'EB5', 'IF5', 'IL5', 'ER6', 'IF6', 'IL6']
popclasses =  [-1,  -1,     1,      2,     1,     2,     3,     1,     1,     2,     3,     1,     2,     3] # Izhikevich population type
popEorI =     [ 0,   0,     0,      1,     0,     1,     1,     0,     0,     1,     1,     0,     1,     1] # Whether it's excitatory or inhibitory
popratios =  [96,   64,    64,     64,   150,    25,    25,   168,    72,    40,    40,   192,    32,    32] # Cell population numbers 
popyfrac =   [[-1,-1], [-1,-1], [-1,-1], [-1,-1], [0.1,0.31], [0.1,0.31], [0.1,0.31], [0.31,0.52], [0.52,0.77], [0.31,0.77], [0.31,0.77], [0.77,1.0], [0.77,1.0], [0.77,1.0]] # data from Weiler et. al 2008 (updated from Ben's excel sheet)

receptornames = ['AMPA', 'NMDA', 'GABAA', 'GABAB', 'opsin'] # Names of the different receptors
npops = len(popnames) # Number of populations
nreceptors = len(receptornames) # Number of receptors
popGidStart = [] # gid starts for each popnames
popGidEnd= [] # gid starts for each popnames
popnumbers = []
PMdinput = 'targetSplit' # 'Plexon', 'spikes', 'SSM', 'targetSplit'

    
# Define params for each cell: cellpops, cellnames, cellclasses, EorI 
cellpops = [] # Store list of populations for each cell -- e.g. 1=ER2 vs. 2=IF2
cellnames = [] # Store list of names for each cell -- e.g. 'ER2' vs. 'IF2'
cellclasses = [] # Store list of classes types for each cell -- e.g. pyramidal vs. interneuron
EorI = [] # Store list of excitatory/inhibitory for each cell
popnumbers = scale*array(popratios) # Number of neurons in each population
if PMdinput == 'Plexon' and 'PMd' in popnames:    
    popratios[popnames.index('PMd')] = server.numPMd
    popnumbers[popnames.index('PMd')] = server.numPMd # Number of PMds is fixed.
ncells = int(sum(popnumbers))# Calculate the total number of cells 
for c in range(len(popnames)):
    start = sum(popnumbers[:c])
    popGidStart.append(start)
    popGidEnd.append(start + popnumbers[c] - 1)
for pop in range(npops): # Loop over each population
    for c in range(int(popnumbers[pop])): # Loop over each cell in that population
        cellpops.append(pop) # Append this cell's population type to the list
        cellnames.append(popnames[pop]) # Append this cell's population type to the list
        cellclasses.append(popclasses[pop]) # Just use integers to index them
        EorI.append(popEorI[pop]) # Append this cell's excitatory/inhibitory state to the list
cellpops = array(cellpops) 
cellnames = array(cellnames)
EorI = array(EorI)


# Assign numbers to each of the different variables so they can be used in the other functions
# initializes the following variables:
# PMd, ASC, EDSC, ER2, IF2, IL2, ER5, EB5, IF5, IL5, ER6, IF6, IL6, AMPA, NMDA, GABAA, GABAB, opsin, Epops, Ipops, allpops 
for i,name in enumerate(popnames): exec(name+'=i') # Set population names to the integers
for i,name in enumerate(receptornames): exec(name+'=i') # Set population names to the integers
allpops = array(range(npops)) # Create an array with all the population numbers
Epops = allpops[array(popEorI)==0] # Pick out numbers corresponding to excitatory populations
Ipops = allpops[array(popEorI)==1] # Pick out numbers corresponding to inhibitory populations


# for creating natural and artificial stimuli (need to import after init of population and receptor indices)
from stimuli import touch, stimmod, makestim 


# Define connectivity matrix (copied out of network.hoc; correct as of 11mar26)
connprobs=zeros((npops,npops))
connprobs[ER2,ER2]=0.2 # weak by wiring matrix in (Weiler et al., 2008)
connprobs[ER2,EB5]=0.8*2 # strong by wiring matrix in (Weiler et al., 2008)
connprobs[ER2,ER5]=0.8*2 # strong by wiring matrix in (Weiler et al., 2008)
connprobs[ER2,IL5]=0.51 # L2/3 E -> L5 LTS I (justified by (Apicella et al., 2012)
connprobs[ER2,ER6]=0 # none by wiring matrix in (Weiler et al., 2008)
connprobs[ER2,IL2]=0.51
connprobs[ER2,IF2]=0.43
connprobs[EB5,ER2]=0 # none by wiring matrix in (Weiler et al., 2008)
connprobs[EB5,EB5]=0.04 * 4 # set using (Kiritani et al., 2012) Fig. 6D, Table 1, value x 4 
connprobs[EB5,ER5]=0 # set using (Kiritani et al., 2012) Fig. 6D, Table 1 
connprobs[EB5,ER6]=0 # none by suggestion of Ben and Gordon over phone
connprobs[EB5,IL5]=0 # ruled out by (Apicella et al., 2012) Fig. 7
connprobs[EB5,IF5]=0.43 # CK: was 0.43 but perhaps the cause of the blow-up?
connprobs[ER5,ER2]=0.2 # weak by wiring matrix in (Weiler et al., 2008)
connprobs[ER5,EB5]=0.21 * 4 # set using (Kiritani et al., 2012) Fig. 6D, Table 1, value x 4
connprobs[ER5,ER5]=0.11 * 4 # set using (Kiritani et al., 2012) Fig. 6D, Table 1, value x 4 
connprobs[ER5,ER6]=0.2 # weak by wiring matrix in (Weiler et al., 2008)
connprobs[ER5,IL5]=0 # ruled out by (Apicella et al., 2012) Fig. 7
connprobs[ER5,IF5]=0.43
connprobs[ER6,ER2]=0 # none by wiring matrix in (Weiler et al., 2008)
connprobs[ER6,EB5]=0.2 # weak by wiring matrix in (Weiler et al., 2008)
connprobs[ER6,ER5]=0.2 # weak by wiring matrix in (Weiler et al., 2008)
connprobs[ER6,ER6]=0.2 # weak by wiring matrix in (Weiler et al., 2008)
connprobs[ER6,IL6]=0.51
connprobs[ER6,IF6]=0.43
connprobs[IL2,ER2]=0.35
connprobs[IL2,IL2]=0.09
connprobs[IL2,IF2]=0.53
connprobs[IF2,ER2]=0.44
connprobs[IF2,IL2]=0.34
connprobs[IF2,IF2]=0.62
connprobs[IL5,EB5]=0.35
connprobs[IL5,ER5]=0.35
connprobs[IL5,IL5]=0.09
connprobs[IL5,IF5]=0.53
connprobs[IF5,EB5]=0.44
connprobs[IF5,ER5]=0.44
connprobs[IF5,IL5]=0.34
connprobs[IF5,IF5]=0.62
connprobs[IL6,ER6]=0.35
connprobs[IL6,IL6]=0.09
connprobs[IL6,IF6]=0.53
connprobs[IF6,ER6]=0.44
connprobs[IF6,IL6]=0.34
connprobs[IF6,IF6]=0.62
connprobs[ASC,ER2]=0.6 
connprobs[EB5,EDSC]=1.0 #0.6
connprobs[EB5,IDSC]=0.0 # hard-wire so receives same input as EB5->EDSC 
connprobs[IDSC,EDSC]=0.0 # hard-wire so projects to antagonist muscle subpopulation
connprobs[PMd,ER5]=0.0


# Define weights (copied out of network.hoc on 11mar27)
connweights=zeros((npops,npops,nreceptors))
connweights[ER2,ER2,AMPA]=0.66
connweights[ER2,EB5,AMPA]=0.36
connweights[ER2,ER5,AMPA]=0.93
connweights[ER2,IL5,AMPA]=0.36
connweights[ER2,ER6,AMPA]=0
connweights[ER2,IL2,AMPA]=0.23
connweights[ER2,IF2,AMPA] = 0.23
connweights[EB5,ER2,AMPA]=0# ruled out based on Ben and Gordon conversation
connweights[EB5,EB5,AMPA]=0.66
connweights[EB5,ER5,AMPA]=0 # pulled from Fig. 6D, Table 1 of (Kiritani et al., 2012)
connweights[EB5,ER6,AMPA]=0# ruled out based on Ben and Gordon conversation
connweights[EB5,IL5,AMPA]=0 # ruled out by (Apicella et al., 2012) Fig. 7
connweights[EB5,IF5,AMPA]=0.23#(Apicella et al., 2012) Fig. 7F (weight = 1/2 x weight for ER5->IF5)
connweights[ER5,ER2,AMPA]=0.66
connweights[ER5,EB5,AMPA]=0.66
connweights[ER5,ER5,AMPA]=0.66
connweights[ER5,ER6,AMPA]=0.66
connweights[ER5,IL5,AMPA]=0# ruled out by (Apicella et al., 2012) Fig. 7
connweights[ER5,IF5,AMPA]=0.46# (Apicella et al., 2012) Fig. 7E (weight = 2 x weight for EB5->IF5)
connweights[ER6,ER2,AMPA]=0
connweights[ER6,EB5,AMPA]=0.66
connweights[ER6,ER5,AMPA]=0.66
connweights[ER6,ER6,AMPA]=0.66
connweights[ER6,IL6,AMPA]=0.23
connweights[ER6,IF6,AMPA]=0.23
connweights[IL2,ER2,GABAB]=0.83
connweights[IL2,IL2,GABAB]=1.5
connweights[IL2,IF2,GABAB]=1.5
connweights[IF2,ER2,GABAA]=1.5
connweights[IF2,IL2,GABAA]=1.5
connweights[IF2,IF2,GABAA]=1.5
connweights[IL5,EB5,GABAB]=0.83
connweights[IL5,ER5,GABAB]=0.83
connweights[IL5,IL5,GABAB]=1.5
connweights[IL5,IF5,GABAB]=1.5
connweights[IF5,EB5,GABAA]=1.5
connweights[IF5,ER5,GABAA]=1.5
connweights[IF5,IL5,GABAA]=1.5
connweights[IF5,IF5,GABAA]=1.5
connweights[IL6,ER6,GABAB]=0.83
connweights[IL6,IL6,GABAB]=1.5
connweights[IL6,IF6,GABAB]=1.5
connweights[IF6,ER6,GABAA]=1.5
connweights[IF6,IL6,GABAA]=1.5
connweights[IF6,IF6,GABAA]=1.5
connweights[ASC,ER2,AMPA]=2.0
connweights[EB5,EDSC,AMPA]=2.0
connweights[EB5,IDSC,AMPA]=0.5
connweights[IDSC,EDSC,GABAA]=1.0 
connweights[PMd,ER5,AMPA]=1.0


###############################################################################
### SET SIMULATION AND NETWORK PARAMETERS
###############################################################################

## Simulation parameters
trainTime = 20*1e3 # duration of traininig phase, in ms
testTime = 1*1e3 # duration of testing/evaluation phase, in ms
duration = 1*1e3 # Duration of the simulation, in ms
h.dt = 0.5 # Internal integration timestep to use
loopstep = 10 # Step size in ms for simulation loop -- not coincidentally the step size for the LFP
progupdate = 5000 # How frequently to update progress, in ms
randseed = 1 # Random seed to use
limitmemory = False # Whether or not to limit RAM usage



## Saving and plotting parameters
outfilestem = '' # filestem to save fitness result
savemat = True # Whether or not to write spikes etc. to a .mat file
armMinimalSave = False # save only arm data and spikes (for target reaching evol opt)
savetxt = False # save spikes and conn to txt file
savelfps = False # Whether or not to save LFPs
lfppops = [[ER2], [ER5], [EB5], [ER6]] # Populations for calculating the LFP from
savebackground = False # save background (NetStims) inputs
saveraw = False # Whether or not to record raw voltages etc.
verbose = 0 # Whether to write nothing (0), diagnostic information on events (1), or everything (2) a file directly from izhi.mod
filename = '../data/m1ms'  # Set file output name
plotraster = False # Whether or not to plot a raster
plotpsd = False # plot power spectral density
maxspikestoplot = 3e8 # Maximum number of spikes to plot
plotconn = False # whether to plot conn matrix
plotweightchanges = True # whether to plot weight changes (shown in conn matrix)
plot3darch = False # plot 3d architecture


## Connection parameters
useconnprobdata = True # Whether or not to use INTF6 connectivity data
useconnweightdata = True # Whether or not to use INTF6 weight data
mindelay = 2 # Minimum connection delay, in ms
velocity = 100 # Conduction velocity in um/ms (e.g. 50 = 0.05 m/s)
modelsize = 10000 # 1000*scale # 500 Size of network in um (~= 1000 neurons/column where column = 500um width)
scaleconnweight = 4*array([[2, 1], [2, 0.1]]) # Connection weights for EE, EI, IE, II synapses, respectively
receptorweight = [1, 1, 1, 1, 1] # Scale factors for each receptor
scaleconnprob = 200/scale*array([[1, 1], [1, 1]]) # scale*1* Connection probabilities for EE, EI, IE, II synapses, respectively -- scale for scale since size fixed
connfalloff = 100*array([2, 3]) # Connection length constants in um for E and I synapses, respectively
toroidal = True # Whether or not to have toroidal topology
if useconnprobdata == False: connprobs = array(connprobs>0,dtype='int') # Optionally cnvert from float data into binary yes/no
if useconnweightdata == False: connweights = array(connweights>0,dtype='int') # Optionally convert from float data into binary yes/no


## Position parameters
cortthaldist=3000 # CK: WARNING, KLUDGY -- Distance from relay nucleus to cortex -- ~1 cm = 10,000 um
corticalthick = 1740


## STDP and RL parameters
usestdp = True # Whether or not to use STDP
useRL = True #True # Where or not to use RL
plastConnsType = 0 # predefined sets of plastic connections (use with evol alg)
plastConns = [[ASC,ER2], [EB5,EDSC], [ER2,ER5], [ER5,EB5]] # list of plastic connections
stdpFactor = 0.001 # multiplier for stdprates
stdprates = stdpFactor * array([[1, -1.3], [0, 0]])#0.1*array([[0.025, -0.025], [0.025, -0.025]])#([[0, 0], [0, 0]]) # STDP potentiation/depression rates for E->anything and I->anything, e.g. [0,:] is pot/dep for E cells
RLfactor = 10
RLrates = RLfactor*array([[0.25, -0.25], [0.0, 0.0]]) # RL potentiation/depression rates for E->anything and I->anything, e.g. [0,:] is pot/dep for E cells
RLinterval = 50 # interval between sending reward/critic signal (set equal to motorCmdWin/2)(ms)
timeoflastRL = -inf # Never RL
stdpwin = 10 # length of stdp window (ms) (scholarpedia=10; Frem13=20(+),40(-))
eligwin = 50 # length of RL eligibility window (ms) (Frem13=500ms)
useRLexp = 1 # Use binary or exp decaying eligibility trace
useRLsoft = 1 # Use soft thresholding 
maxweight = 50 # Maximum synaptic weight
timebetweensaves = 5*1e3 # How many ms between saving weights(can't be smaller than loopstep)
timeoflastsave = -inf # Never saved
weightchanges = [] # to periodically store weigth changes


## Background input parameters
usebackground = True # Whether or not to use background stimuli
backgroundrateTrain = 50 # background input for training phase
backgroundrateTest = 150 # background input for testing phase
backgroundrate = 100 # Rate of stimuli (in Hz)
backgroundrateMin = 0.1 # Rate of stimuli (in Hz)
backgroundnumber = 1e10 # Number of spikes
backgroundnoise = 1 # Fractional noise
backgroundweight = 2.0*array([1,0.1]) # Weight for background input for E cells and I cells
backgroundreceptor = NMDA # Which receptor to stimulate

## Virtual arm parameters
useArm =  'dummyArm' # what type of arm to use: 'randomOutput', 'dummyArm' (simple python arm), 'musculoskeletal' (C++ full arm model)
animArm = False # shows arm animation
graphsArm = False # shows graphs (arm trajectory etc) when finisheds
targetid = 1 # initial target 
minRLerror = 0.002 # minimum error change for RL (m)
armLen = [0.4634 - 0.173, 0.7169 - 0.4634] # elbow - shoulder from MSM;radioulnar - elbow from MSM;  
nMuscles = 4 # number of muscles
startAng = [0.62,1.53] # starting shoulder and elbow angles (rad) = natural rest position
targetDist = 0.15 # target distance from center (15 cm)
# motor command encoding
initArmMovement = 100 # time after which to start moving arm (adds initial delay to avoid using initial burst of activity due to background noise init)
motorCmdStartCell = popGidStart[EDSC] # start cell for motor command
motorCmdEndCell = popGidStart[EDSC] + popnumbers[EDSC] # end cell for motor command
cmdmaxrate = scale*20.0 # maximum spikes for motor command (normalizing value)
cmdmaxrateTest = scale*20.0 # maximum spikes for motor command (normalizing value)
cmdtimewin = 100 # spike time window for motor command (ms)
antagInh = 0 # antagonist muscle inhibition
# proprioceptive encoding
pStart = popGidStart[ASC] 
numPcells = popnumbers[ASC] # number of proprioceptive (P) cells to encode shoulder and elbow angles
minPval = radians(-30) # min angle to encode
maxPval = radians(135) # max angle to encode
minPrate = 0.1 # firing rate when angle not within range
maxPrate = 200 # firing rate when angle within range
# exploratory movements
explorMovs = 0 # exploratory movements; 1 = noise to EDSC+IDSC; 2 = noise to E5B
explorMovsFactor = 10 # max factor by which to multiply specific muscle groups to enforce explor movs (only used if explorMovs=1)
explorMovsDur = 1000 # max duration of each excitation to each muscle during exploratory movments
backgroundrateExplor = 1000 # rate for background input for exploratory movements (changed during sim)
backgroundweightExplor = 4.0 # weight for background input for exploratory movements (fixed)
backgroundnoiseExplor = 0.1 # Fractional noise in timing durin explor mov
explorCellsFraction = 0.05 # fraction of E5B cells to be activated at a time during explor movs
timeoflastexplor = -inf # time when last exploratory movement was updated
# reset arm every trial
trialReset = True # whether to reset the arm after every trial time
timeoflastreset = 0 # time when arm was last reseted (start from center etc. to simulate trials)


## PMd inputs 
if PMdinput == 'Plexon':
    vec = h.Vector() # temporary Neuron vectors
    emptyVec = h.Vector()
    inncl = h.List() # used to store the plexon-interfaced PMd Netcons
    innclDic = {} # dictionary to relate global and local PMd netcons
if PMdinput == 'targetSplit':
    trialTargets = [] # target id for each trial
    targetPMdInputs = [] # PMd units active for each trial
    maxPMdRate = 0.1
    minPMdRate = 0.1
    PMdNoiseRatio = 0.1 


## Stimulus parameters
usestims = False # Whether or not to use stimuli at all
ltptimes  = [5, 10] # Pre-microstim touch times
ziptimes = [10, 15] # Pre-microstim touch times
stimpars = [stimmod(touch,name='LTP',sta=ltptimes[0],fin=ltptimes[1]), stimmod(touch,name='ZIP',sta=ziptimes[0],fin=ziptimes[1])] # Turn classes into instances



## Peform a mini-benchmarking test for future time estimates
if rank==0:
    print('Benchmarking...')
    benchstart = time()
    for i in range(int(1.36e6)): tmp=0 # Number selected to take 0.1 s on my machine
    performance = 1/(10*(time() - benchstart))*100
    print('  Running at %0.0f%% default speed (%0.0f%% total)' % (performance, performance*nhosts))



