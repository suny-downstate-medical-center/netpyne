"""
shared.py 

Contains all the model shared variables and modules (except params.py). It is imported as "s" from all other file, 
so that any variable or module can be referenced from any file using s.varName

Contributors: salvadordura@gmail.com
"""

from neuron import h, init # Import NEURON
from time import time
import hashlib
import sim
import analysis
from network import Network
from cell import Pop, Izhi2007a, Izhi2007b, HH
from conn import Synapse,  RandConn, YfracConn
