"""
Package of classes to define high-level model specifications

"""

from __future__ import unicode_literals        #Importing unicode_literals from __future__
from __future__ import print_function          #Importing print_function from __future__
from __future__ import division                #Importing division from __future__
from __future__ import absolute_import         #Importing absolute_import from __future__

from future import standard_library            #Importing standard_library from future
standard_library.install_aliases()
from .dicts import Dict, ODict                 #Importing Dict, ODict from .dicts
from .netParams import NetParams, CellParams   #Importing NetParams, CellParams from .netParams
from .simConfig import SimConfig               #Importing SimConfig from .simConfig
