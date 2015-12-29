"""
shared.py 

Contains all the model shared variables and modules.
It is imported as "s" from all other file,  so that any variable or module can be referenced from any module using s.varName

Contributors: salvadordura@gmail.com
"""

import sim
import analysis
from network import Network
from cell import Cell, PointNeuron, Izhi2003b, Izhi2007b, clausIzhi2007b, HH, Pop
