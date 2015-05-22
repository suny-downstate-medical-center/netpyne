"""
globals.py 

list of model objects (paramaters and variables) to be shared across modules
Can modified manually or via arguments from main.py

Version: 2015feb12 by salvadord
"""

###############################################################################
### IMPORT MODULES AND INIT MPI
###############################################################################

from pylab import array, inf, zeros, seed, rand, transpose, sqrt, exp, arange,mod
from neuron import h # Import NEURON
import izhi
from time import time
import hashlib
import stimuli as stim

def id32(obj): return int(hashlib.md5(obj).hexdigest()[0:8],16)# hash(obj) & 0xffffffff # for random seeds (bitwise AND to retain only lower 32 bits)

## MPI
pc = h.ParallelContext() # MPI: Initialize the ParallelContext class
nhosts = int(pc.nhost()) # Find number of hosts
rank = int(pc.id())     # rank 0 will be the master

if rank==0: 
    pc.gid_clear()
    print('\nSetting parameters...')


###############################################################################
### LABELS CLASS
###############################################################################

# Class to store equivalence between names and values so can be used as indices
class Labels:
    AMPA=0; NMDA=1; GABAA=2; GABAB=3; opsin=4; numReceptors=5  # synaptic receptors
    E=0; I=1  # excitatory vs inhibitory
    IT=0; PT=1; CT=2; HTR=3; Pva=4; Sst=5; numTopClass=6  # cell/pop top class 
    L4=0; other=1; Vip=2; Nglia=3; Basket=4; Chand=5; Marti=6; L4Sst=7  # cell/pop sub class
    Izhi2007=0; Friesen=1; HH=2  # types of cell model

l = Labels() # instantiate object of class Labels











###############################################################################
### Instantiate network populations (objects of class 'Pop')
###############################################################################

pops = []  # list to store populations ('Pop' objects)

            # popid,    EorI,   topClass,   subClass,   yfracRange,     density,                cellModel
pops.append(Pop(0,      l.E,    l.IT,       l.other,    [0.1, 0.26],    lambda x:2e3*x,        l.Izhi2007)) #  L2/3 IT
pops.append(Pop(1,      l.E,    l.IT,       l.other,    [0.26, 0.31],   lambda x:2e3*x,        l.Izhi2007)) #  L4 IT
pops.append(Pop(2,      l.E,    l.IT,       l.other,    [0.31, 0.52],   lambda x:2e3*x,        l.Izhi2007)) #  L5A IT
pops.append(Pop(3,      l.E,    l.IT,       l.other,    [0.52, 0.77],   lambda x:1e3*x,        l.Izhi2007)) #  L5B IT
pops.append(Pop(4,      l.E,    l.PT,       l.other,    [0.52, 0.77],   lambda x:1e3,          l.Izhi2007)) #  L5B PT
pops.append(Pop(5,      l.E,    l.IT,       l.other,    [0.77, 1.0],    lambda x:1e3,          l.Izhi2007)) #  L6 IT
pops.append(Pop(6,      l.I,    l.Pva,      l.Basket,   [0.1, 0.31],    lambda x:0.5e3,        l.Izhi2007)) #  L2/3 Pva (FS)
pops.append(Pop(7,      l.I,    l.Sst,      l.Marti,    [0.1, 0.31],    lambda x:0.5e3,        l.Izhi2007)) #  L2/3 Sst (LTS)
pops.append(Pop(8,      l.I,    l.Pva,      l.Basket,   [0.31, 0.77],   lambda x:0.5e3,        l.Izhi2007)) #  L5 Pva (FS)
pops.append(Pop(9,      l.I,    l.Sst,      l.Marti,    [0.31, 0.77],   lambda x:0.5e3,        l.Izhi2007)) #  L5 Sst (LTS)
pops.append(Pop(10,     l.I,    l.Pva,      l.Basket,   [0.77, 1.0],    lambda x:0.5e3,        l.Izhi2007)) #  L6 Pva (FS)
pops.append(Pop(11,     l.I,    l.Sst,      l.Marti,    [0.77, 1.0],    lambda x:0.5e3,        l.Izhi2007)) #  L6 Sst (LTS)


###############################################################################
### SET SIMULATION AND NETWORK PARAMETERS
###############################################################################

## Simulation parameters
scale = 1 # Size of simulation in thousands of cells
duration = 1*1e3 # Duration of the simulation, in ms
h.dt = 0.5 # Internal integration timestep to use
saveStep = 10 # Step size in ms to save data (eg. V traces, LFP, etc)
saveFileStep = 1000 # step size in ms to save data to disk
progupdate = 5000 # How frequently to update progress, in ms
randseed = 1 # Random seed to use
limitmemory = False # Whether or not to limit RAM usage


## Saving and plotting parameters
outfilestem = '' # filestem to save fitness result
savemat = True # Whether or not to write spikes etc. to a .mat file
savetxt = False # save spikes and conn to txt file
savelfps = False # Whether or not to save LFPs
#lfppops = [[ER2], [ER5], [EB5], [ER6]] # Populations for calculating the LFP from
savebackground = False # save background (NetStims) inputs
saveraw = False # Whether or not to record raw voltages etc.
verbose = 0 # Whether to write nothing (0), diagnostic information on events (1), or everything (2) a file directly from izhi.mod
filename = '../data/m1ms'  # Set file output name
plotraster = False # Whether or not to plot a raster
plotpsd = False # plot power spectral density
maxspikestoplot = 3e8 # Maximum number of spikes to plot
plotconn = False # whether to plot conn matrix
plotweightchanges = False # whether to plot weight changes (shown in conn matrix)
plot3darch = False # plot 3d architecture


## Connection parameters
useconnprobdata = True # Whether or not to use INTF6 connectivity data
useconnweightdata = True # Whether or not to use INTF6 weight data
mindelay = 2 # Minimum connection delay, in ms
velocity = 100 # Conduction velocity in um/ms (e.g. 50 = 0.05 m/s)
modelsize = 1000*scale # Size of network in um (~= 1000 neurons/column where column = 500um width)
sparseness = 0.1 # fraction of cells represented (num neurons = density * modelsize * sparseness)
scaleconnweight = 4*array([[2, 1], [2, 0.1]]) # Connection weights for EE, EI, IE, II synapses, respectively
receptorweight = [1, 1, 1, 1, 1] # Scale factors for each receptor
scaleconnprob = 1/scale*array([[1, 1], [1, 1]]) # scale*1* Connection probabilities for EE, EI, IE, II synapses, respectively -- scale for scale since size fixed
connfalloff = 100*array([2, 3]) # Connection length constants in um for E and I synapses, respectively
toroidal = False # Whether or not to have toroidal topology
if useconnprobdata == False: connprobs = array(connprobs>0,dtype='int') # Optionally cnvert from float data into binary yes/no
if useconnweightdata == False: connweights = array(connweights>0,dtype='int') # Optionally convert from float data into binary yes/no


## Position parameters
cortthaldist=3000 # CK: WARNING, KLUDGY -- Distance from relay nucleus to cortex -- ~1 cm = 10,000 um
corticalthick = 1740 # rename to corticalThick


## STDP and RL parameters
usestdp = True # Whether or not to use STDP
plastConnsType = 0 # predefined sets of plastic connections (use with evol alg)
#plastConns = [[EB5,EDSC], [ER2,ER5], [ER5,EB5]] # list of plastic connections
stdpFactor = 0.001 # multiplier for stdprates
stdprates = stdpFactor * array([[1, -1.3], [0, 0]])#0.1*array([[0.025, -0.025], [0.025, -0.025]])#([[0, 0], [0, 0]]) # STDP potentiation/depression rates for E->anything and I->anything, e.g. [0,:] is pot/dep for E cells
stdpwin = 10 # length of stdp window (ms) (scholarpedia=10; Frem13=20(+),40(-))
maxweight = 50 # Maximum synaptic weight
timebetweensaves = 5*1e3 # How many ms between saving weights(can't be smaller than loopstep)
timeoflastsave = -inf # Never saved
weightchanges = [] # to periodically store weigth changes


## Background input parameters
usebackground = True # Whether or not to use background stimuli
backgroundrate = 100 # Rate of stimuli (in Hz)
backgroundrateMin = 0.1 # Rate of stimuli (in Hz)
backgroundnumber = 1e10 # Number of spikes
backgroundnoise = 1 # Fractional noise
backgroundweight = 2.0*array([1,0.1]) # Weight for background input for E cells and I cells
backgroundreceptor = l.NMDA # Which receptor to stimulate


## Stimulus parameters
usestims = False # Whether or not to use stimuli at all
ltptimes  = [5, 10] # Pre-microstim touch times
ziptimes = [10, 15] # Pre-microstim touch times
stimpars = [stim.stimmod(stim.touch,name='LTP',sta=ltptimes[0],fin=ltptimes[1]), stim.stimmod(stim.touch,name='ZIP',sta=ziptimes[0],fin=ziptimes[1])] # Turn classes into instances

# global/shared containers
simdata = {}
lastGid = 0  # keep track of las cell gid

## Peform a mini-benchmarking test for future time estimates
if rank==0:
    print('Benchmarking...')
    benchstart = time()
    for i in range(int(1.36e6)): tmp=0 # Number selected to take 0.1 s on my machine
    performance = 1/(10*(time() - benchstart))*100
    print('  Running at %0.0f%% default speed (%0.0f%% total)' % (performance, performance*nhosts))



