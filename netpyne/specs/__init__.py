"""
specs/__init__.py

Set of classes use to define high-level model specifications

Contributors: salvadordura@gmail.com
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from .dicts import Dict, ODict
from .netParams import NetParams, CellParams
from .simConfig import SimConfig
