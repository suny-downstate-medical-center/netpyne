# header
'''Simulation to run a simple random network of excitatory 1 compartment Hodgkin-Huxley-ish p.cells based on Gillies and
Starrett example on forum.  See readme.txt and exercises.txt'''
import sys
from neuron import h
h.load_file('stdrun.hoc')
import datetime
import params as p
import scipy

# top level calls: read command line to pick up changes to params and to determine if called with -mpi
ismpi = (p.nhost > 1) # assume that if only using 1 node it's to do viewing/debugging/analysis interactively
from hhcell import hhcell
import network
## important that any calls that depend on params happen after commandline params are picked up
[r.Random123_globalindex(p.runid) for r in p.randomizers] # can reset to prior p.runid to rerun
## main run; this is the main call from top level -- will only be called if under MPI: if ismpi:runseq()
network.runseq()
print "DONE"
