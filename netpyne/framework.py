"""
framework.py 

Contains all the model shared variables and modules.
It is imported as "f" from all other file,  so that any variable or module can be referenced from any module using f.varName

Contributors: salvadordura@gmail.com
"""

import sim
import analysis
from network import Network
from cell import Cell, PointNeuron
from pop import Pop 
import utils
import default
