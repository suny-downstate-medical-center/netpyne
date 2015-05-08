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
from izhi import RS, IB, CH, LTS, FS, TC, RTN # Import Izhikevich model
from nsloc import nsloc # NetStim with location unit type
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

# Class to store equivalence between names and values so can be used as indices
# class Dicts:
#     # can use dicts
#     EorI = {'E': 0, 'I':1}
#     topClass = {'IT': 0, 'PT': 1, 'CT': 2, 'HTR':3, 'Pva':4, 'Sst':5}
#     subClass = {'L4':0, 'other':1, 'Vip':2, 'Nglia':3, 'Basket':4, 'Chand':5, 'Marti':6, 'L4Sst':7} 
#     model = {'Izhi2007':0, 'Friesen':1, 'HH':2}

#     # or maybe simply variable names
#     E=0, I=1
#     IT=0, PT=1, CT=2, HTR=3, Pva=4, Sst=5
#     L4=0, other=1, Vip=2, Nglia=3, Basket=4, Chand=5, Marti=6, L4Sst=7
#     Izhi2007=0, Friesen=1, HH=2 

# d = Dicts()

# or single dict
d = {'E': 0, 'I':1, \
    'IT': 0, 'PT': 1, 'CT': 2, 'HTR':3, 'Pva':4, 'Sst':5, \
    'L4':0, 'other':1, 'Vip':2, 'Nglia':3, 'Basket':4, 'Chand':5, 'Marti':6, 'L4Sst':7, \
    'Izhi2007':0, 'Friesen':1, 'HH':2}


###############################################################################
### CELL CLASS
###############################################################################

# definition of python class ‘Cell' used to instantiate individual neurons
# based on (Harrison & Sheperd, 2105)
class Cell:
    def __init__(self, gid, EorI, topClass, subClass, yfrac, xloc, yloc, model):
        self.gid = gid  # global cell id 
        self.popid = popid  # id of population
        self.EorI = EorI # excitatory or inhibitory 
        self.topClass = topClass # top-level class (IT, PT, CT,...) 
        self.subClass = subClass # subclass (L4, Basket, ...)
        self.yfrac = yfrac  # normalized cortical depth
        self.xloc = xloc  # normalized x location 
        self.yloc = yloc  # normalized y location 
        self.model = model  # type of model (eg. Izhikevich, Friesen, HH ...)
        #self.[other properties] = 

        # instantiate actual cell model (eg. Izhi2007 point process, or HH MC)
        if model == d['Izhi2007']:
            dummy = h.Section()
            if topClass in range(0,3): # if excitatory cell use RS
                self.m = RS(0, gid)
            elif topClass == d['Pva']: # if Pva use FS
                self.m = FS(0, gid)
            elif topClass == d['Sst']: # if Sst us LTS
                self.m = LTS(0, gid)
        else:
            print('Selected cell model %d not yet implemented' % (model))


###############################################################################
### POP CLASS
###############################################################################

# definition of python class ‘Pop’ used to instantiate the network population
class Pop:
    def __init__(self, gid, EorI, topClass, subClass, yfracRange, ratio, model):
        self.gid = gid
        self.type = topClass
        self.topClass = topClass
        self.subClass = subClass
        self.yfracRange = yfracRange
        self.ratio = ratio
        self.model = model
        self.cellgids = []

    def createCells(self, lastGid, scale):
        cells = []
        gid = lastGid
        seed(id32('%d' % randseed)) # Reset random number generator
        randLocs = rand(scale*self.ratio, 3) # Create random x,y,z locations
        for i in range(scale*self.ratio):
            gid = gid + 1
            yfrac =  self.yfracRange[0] + (sel.yfracRange[1] - sel.yfracRange[0]) *  
            self.cellgid.append(gid)  # add gid list of cells belonging to this population
            cells.append(Cell(gid, self.type, self.topClass, self.subClass, yfrac, randLocs[i,1], randLocs[i,2], self.model))

        return cells


###############################################################################
### CONN CLASS
###############################################################################

# definition of python class 'Conn' to store and calcualte connections
class Conn:
  def __init__(cellPre, cellPost):
    self.preid = cellPre.gid
    self.postid = cellPost.gid
    self.weight = connWeight(cellPre, cellPost)
    self.delay = connDelay(cellPre, cellPost)

  def connectWeight(cellPre, cellPost):
    [calculate as a func of cellPre.type, cellPre.class, cellPre.yfrac, cellPost.type, cellPost.class, cellPost.yfrac]
  return weight

  def connectDelay(cellPre, cellPost):
    [calculate as a func of cellPre.type, cellPre.class, cellPre.yfrac, cellPost.type, cellPost.class, cellPost.yfrac]
  return delay



# # Instantiation of objects of class ‘Pop’ (network populations)
# E_IT_2 = Pop('E', 'IT, [0.1,0.31])
# or pops[0] = Pop('E', 'IT, [0.1,0.31])

# # Instantiation of objects of class ‘Cell’ (network cells) based on ‘Pop’ objects
# for ipop in pops:
#  cells.append(pops[ipop].createCells)

# # Connect object cells based on pre and post cell's type, class and yfrac
# for ipre in cells:
#  for ipost in cells:
#    conn[i] = Conn(cells[ipre], cells[ipost]



###############################################################################
### SET SIMULATION AND NETWORK PARAMETERS
###############################################################################

## Simulation parameters
duration = 1*1e3 # Duration of the simulation, in ms
h.dt = 0.5 # Internal integration timestep to use
loopstep = 10 # Step size in ms for simulation loop -- not coincidentally the step size for the LFP
progupdate = 5000 # How frequently to update progress, in ms
randseed = 1 # Random seed to use
limitmemory = False # Whether or not to limit RAM usage


## Saving and plotting parameters
outfilestem = '' # filestem to save fitness result
savemat = True # Whether or not to write spikes etc. to a .mat file
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
plotweightchanges = False # whether to plot weight changes (shown in conn matrix)
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
corticalthick = 1740 # rename to corticalThick


## STDP and RL parameters
usestdp = True # Whether or not to use STDP
plastConnsType = 0 # predefined sets of plastic connections (use with evol alg)
plastConns = [[EB5,EDSC], [ER2,ER5], [ER5,EB5]] # list of plastic connections
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
backgroundreceptor = NMDA # Which receptor to stimulate


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



