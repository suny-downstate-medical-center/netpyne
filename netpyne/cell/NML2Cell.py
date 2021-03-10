"""
Module containing a NeuroML2 cell class

"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from copy import deepcopy
from neuron import h # Import NEURON
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
    Class for/to <short description of `netpyne.cell.NML2Cell.NML2Cell`>

    """

    ''' Might this be useful to show better name for cell when psection() called?
    def __str__():
        return "%s"%self.tags['cellType']
    '''

    pass
