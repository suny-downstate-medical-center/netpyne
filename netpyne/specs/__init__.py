"""
Package of classes to define high-level model specifications

"""

from .dicts import Dict, ODict
from .simConfig import SimConfig
try:# this SimConfig occurs before Runner_SimConfig
    from netpyne.batchtools import Runner_SimConfig as SimConfig # inherits and replaces prior class
    from netpyne.batchtools import comm
    _batch_specs = True
    comm.initialize()
except Exception as e:
    #from .simConfig import SimConfig
    _batch_specs = False
from .netParams import CellParams, NetParams