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

# import NEURON module
from neuron import h

# import simulation-related functions
from .simFuncs import * 

# import cell classes
from .cell import CompartCell, PointCell, NML2Cell, NML2SpikeSource

# import Network and Pop classes
from .network import Network 
from .pop import Pop 

# import analysis-related module
import analysis

# import wrapper functions
from .wrappers import *

# import utility module
from . import utils

# import testing related functions
from . import tests
from .tests.checks import checkOutput
from .tests.tests import SimTestObj

# import export/import-related functions
from .. import conversion 
try:
	from .conversion.neuromlFormat import exportNeuroML2, importNeuroML2
except:
	pass
