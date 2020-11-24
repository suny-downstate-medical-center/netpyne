"""
NetPyNE (Networks using Python and NEURON) is a Python package to facilitate the development, simulation, parallelization, analysis, and optimization of biological neuronal networks using the NEURON simulator.

NetPyNE consists of a number of sub-packages and modules.
"""

__version__ = '0.9.8'
import os, sys
display = os.getenv('DISPLAY')
nogui = (sys.argv.count('-nogui')>0)

__gui__ = True

if nogui:  # completely disables graphics (avoids importing matplotlib)
    __gui__ = False

elif not display or len(display) == 0:  # if no display env available (e.g. clusters) uses 'Agg' backend to plot
    import matplotlib
    matplotlib.use('Agg')

