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

#------------------------------------------------------------------------------
# Import simulation-related functions from sim subpackage
#------------------------------------------------------------------------------

# import wrapper functions
from .simFuncs import * 

# import wrapper functions
from .wrappers import create, simulate, analyze, createSimulate, \
	createSimulateAnalyze, load, loadSimulate, loadSimulateAnalyze, \
	createExportNeuroML2, importNeuroML2SimulateAnalyze 


#------------------------------------------------------------------------------
# Import classes and functions from other subpackages (so available via sim)
#------------------------------------------------------------------------------

# import cell classes
from ..cell import CompartCell, PointCell, NML2Cell, NML2SpikeSource

# import Network and Pop classes
from ..network import Network, Pop

# import analysis-related module
from .. import analysis

# import testing related functions
from .. import tests
from ..tests.checks import checkOutput
from ..tests.tests import SimTestObj

# import export/import-related functions
from .. import conversion 
from ..conversion.neuromlFormat import * 