"""
shared.py 

Contains all the model shared variables and modules (except params.py). It is imported as "s" from all other file, 
so that any variable or module can be referenced from any file using s.varName

Contributors: salvadordura@gmail.com
"""

###############################################################################
### IMPORT MODULES AND INIT MPI
###############################################################################

from neuron import h, init # Import NEURON
from time import time
import hashlib
import sim
import network
import analysis
from cell import Pop, Izhi2007a, Izhi2007b, HH
from conn import RandConn, YfracConn

def id32(obj): return int(hashlib.md5(obj).hexdigest()[0:8],16)# hash(obj) & 0xffffffff # for random seeds (bitwise AND to retain only lower 32 bits)

## MPI
pc = h.ParallelContext() # MPI: Initialize the ParallelContext class
nhosts = int(pc.nhost()) # Find number of hosts
rank = int(pc.id())     # rank 0 will be the master

if rank==0: 
    print('\nSetting parameters...')
    pc.gid_clear()


## global/shared containers (most are instantiated in network.py or sim.py)
simdata = {}
simdataVecs = ['spkt', 'spkid']
lastGid = 0  # keep track of las cell gid
fih = []  # list of func init handlers
