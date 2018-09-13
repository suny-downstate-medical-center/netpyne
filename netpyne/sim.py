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
from .simFuncs import *
from .neuromlFuncs import *
from .wrappers import *
from .analysis import analysis
from .network.network import Network
from .cell import CompartCell, PointCell, NML2Cell, NML2SpikeSource
from .pop import Pop
from . import utils
from neuron import h
from . import tests
from .tests.checks import checkOutput
from .tests.tests import SimTestObj
