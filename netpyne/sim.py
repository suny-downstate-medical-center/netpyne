"""
sim.py 

Contains all the model shared variables and modules.
It is imported as "sim" from all other file,  so that any variable or module can be referenced from any module using sim.varName

Contributors: salvadordura@gmail.com
"""

# check for -nogui option 
import sys
if '-nogui' in sys.argv:
    import netpyne
    netpyne.__gui__ = False

# import all required modules
from simFuncs import *
from wrappers import *
import analysis
from network import Network
from cell import Cell
from pop import Pop 
import utils
from neuron import h

