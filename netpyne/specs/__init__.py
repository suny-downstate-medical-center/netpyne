"""
Package of classes to define high-level model specifications

"""

from .dicts import Dict, ODict
try:
    from netpyne.batchtools import NetpyneRunner
    from netpyne.batchtools.comm import Comm
    _batch_specs = NetpyneRunner()
    SimConfig = _batch_specs.SimConfig()
    comm = Comm()
    comm.initialize()
except:
    from .simConfig import SimConfig
    _batch_specs = None
from .netParams import CellParams, NetParams

