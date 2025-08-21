"""
Module containing a NeuroML2 cell class

"""

from copy import deepcopy
from neuron import h  # Import NEURON
import numpy as np
from .compartCell import CompartCell
from ..specs import Dict


###############################################################################
#
# NeuroML2 CELL CLASS
#
###############################################################################


class NML2Cell(CompartCell):
    """
    Class to hold a NeuroML2 cell

    """

    # Might this be useful to show better name for cell when psection() called?
    # def __str__():
    #     return "%s"%self.tags['cellType']

    pass
