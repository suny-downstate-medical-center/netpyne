"""
analysis/rxd.py

Functions to plot and analyze RxD-related results

Contributors: salvadordura@gmail.com
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from netpyne import __gui__

if __gui__:
    import matplotlib.pyplot as plt
    from matplotlib_scalebar import scalebar
from .utils import exception, _showFigure, _saveFigData

import numpy as np


# -------------------------------------------------------------------------------------------------------------------
## Plot interactive raster 
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotRaster(showFig=False):
    from .. import sim
    from bokeh.plotting import figure
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import layout

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

    fig = figure(title="Raster Plot", tools=TOOLS)

    spkt = sim.allSimData['spkt']
    spkid = sim.allSimData['spkid']
    fig.scatter(spkt, spkid, size=1, legend="all spikes")

    plot_layout = layout(fig, sizing_mode='scale_both')
    html = file_html(plot_layout, CDN, title="Raster Plot")

    if showFig:
        show(fig)

    return html


# -------------------------------------------------------------------------------------------------------------------
## Plot interactive dipole 
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotDipole(expData={'x':[], 'y':[]}, showFig=False):
    '''
    expData: experimental data; a dict with ['x'] and ['y'] 1-d vectors (either lists or np.arrays) of same length
    showFig: show output figure in web browser (default: None)
    '''
    from .. import sim
    from bokeh.plotting import figure, show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import layout
 
    TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

    fig = figure(title="Dipole Plot", tools=TOOLS)

    fig.line(expData['x'], expData['y'], legend="Experiment")

    plot_layout = layout(fig, sizing_mode='scale_both')
    html = file_html(plot_layout, CDN, title="Dipole Plot")

    if showFig:
        show(fig)

    return html
