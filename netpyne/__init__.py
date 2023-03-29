"""
NetPyNE (Networks using Python and NEURON) is a Python package to facilitate the development, simulation, parallelization, analysis, and optimization of biological neuronal networks using the NEURON simulator.

NetPyNE consists of a number of sub-packages and modules.
"""

__version__ = '1.0.3.1_osbv2'
import os, sys

display = os.getenv('DISPLAY')
nogui = sys.argv.count('-nogui') > 0

__gui__ = True

if nogui:  # completely disables graphics (avoids importing matplotlib)
    __gui__ = False

elif not display or len(display) == 0:  # if no display env available (e.g. clusters) uses 'Agg' backend to plot
    import matplotlib

    matplotlib.use('Agg')

from netpyne import analysis
from netpyne import batch
from netpyne import cell
from netpyne import conversion
from netpyne import metadata
from netpyne import network
from netpyne import plotting
from netpyne import sim
from netpyne import specs
from netpyne import support
from netpyne import tests
