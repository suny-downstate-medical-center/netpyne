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



