"""
shared.py 

Contains all the model shared variables and modules (except params.py). It is imported as "s" from all other file, 
so that any variable or module can be referenced from any file using s.varName

Version: 2015may26 by salvadord
"""

###############################################################################
### IMPORT MODULES AND INIT MPI
###############################################################################

from neuron import h # Import NEURON
from time import time
import hashlib
import sim
import network
import analysis
import stimuli
from cell import BasicPop, YfracPop, Izhi2007, HH
from conn import RandConn, YfracConn

def id32(obj): return int(hashlib.md5(obj).hexdigest()[0:8],16)# hash(obj) & 0xffffffff # for random seeds (bitwise AND to retain only lower 32 bits)

## MPI
pc = h.ParallelContext() # MPI: Initialize the ParallelContext class
nhosts = int(pc.nhost()) # Find number of hosts
rank = int(pc.id())     # rank 0 will be the master

if rank==0: 
    pc.gid_clear()


## global/shared containers
simdata = {}
lastGid = 0  # keep track of las cell gid

## Peform a mini-benchmarking test for future time estimates
if rank==0:
    print('Benchmarking...')
    benchstart = time()
    for i in range(int(1.36e6)): tmp=0 # Number selected to take 0.1 s on my machine
    performance = 1/(10*(time() - benchstart))*100
    print('  Running at %0.0f%% default speed (%0.0f%% total)' % (performance, performance*nhosts))



