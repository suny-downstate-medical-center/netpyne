"""
NetPyNE (Networks using Python and NEURON) is a Python package to facilitate the development, simulation, parallelization, analysis, and optimization of biophysical neuronal networks using the NEURON simulator.

NetPyNE consists of a number of sub-packages and modules.
"""

__version__ = '0.9.8'
import os, sys
display = os.getenv('DISPLAY')
nogui = (sys.argv.count('-nogui') > 0)

# If '-nogui' was included in the terminal command, graphics are completely disabled (avoids importing matplotlib)
__gui__ = True
if nogui:  
    __gui__ = False

# if no display env is available (e.g. on clusters), 'Agg' is used as the matplotlib backend for plotting
elif not display or len(display) == 0:  
    import matplotlib
    matplotlib.use('Agg')

from netpyne import analysis
from netpyne import batch
from netpyne import cell
from netpyne import conversion
from netpyne import metadata
from netpyne import network
from netpyne import sim
from netpyne import specs
from netpyne import support
from netpyne import tests
from netpyne import plotting