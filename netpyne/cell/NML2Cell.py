"""
cell/NML2Cell.py 

Contains pointCell class 

Contributors: salvadordura@gmail.com
"""

from copy import deepcopy
from neuron import h # Import NEURON
from specs import Dict
import numpy as np
from .compartCell import CompartCell


###############################################################################
#
# NeuroML2 CELL CLASS 
#
###############################################################################

class NML2Cell (CompartCell):
    ''' Class for NeuroML2 neuron models: No different than CompartCell '''
    
    ''' Might this be useful to show better name for cell when psection() called?
    def __str__():
        return "%s"%self.tags['cellType']
    '''
        