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


    # renormalize the dipole and save
    def baseline_renormalize():
        # N_pyr cells in grid. This is PER LAYER
        N_pyr = sim.cfg.N_pyr_x * sim.cfg.N_pyr_y
        # dipole offset calculation: increasing number of pyr cells (L2 and L5, simultaneously)
        # with no inputs resulted in an aggregate dipole over the interval [50., 1000.] ms that
        # eventually plateaus at -48 fAm. The range over this interval is something like 3 fAm
        # so the resultant correction is here, per dipole
        # dpl_offset = N_pyr * 50.207
        dpl_offset = {
            # these values will be subtracted
            'L2': N_pyr * 0.0443,
            'L5': N_pyr * -49.0502
            # 'L5': N_pyr * -48.3642,
            # will be calculated next, this is a placeholder
            # 'agg': None,
        }
        
        # L2 dipole offset can be roughly baseline shifted over the entire range of t
        dpl = {'L2': np.array(sim.simData['dipole']['L2']),
            'L5': np.array(sim.simData['dipole']['L5'])}
        dpl['L2'] -= dpl_offset['L2']

        # L5 dipole offset should be different for interval [50., 500.] and then it can be offset
        # slope (m) and intercept (b) params for L5 dipole offset
        # uncorrected for N_cells
        # these values were fit over the range [37., 750.)
        m = 3.4770508e-3
        b = -51.231085
        # these values were fit over the range [750., 5000]
        t1 = 750.
        m1 = 1.01e-4
        b1 = -48.412078

        t = sim.simData['t']

        # piecewise normalization
        dpl['L5'][t <= 37.] -= dpl_offset['L5']
        dpl['L5'][(t > 37.) & (t < t1)] -= N_pyr * (m * t[(t > 37.) & (t < t1)] + b)
        dpl['L5'][t >= t1] -= N_pyr * (m1 * t[t >= t1] + b1)
        # recalculate the aggregate dipole based on the baseline normalized ones
        dpl['agg'] = dpl['L2'] + dpl['L5']

        return dpl

    # convolve with a hamming window
    def hammfilt(x, winsz):
        from pylab import convolve
        from numpy import hamming
        win = hamming(winsz)
        win /= sum(win)
        return convolve(x,win,'same')

    # baseline renormalize
    dpl = baseline_renormalize()
    
    # convert units from fAm to nAm, rescale and smooth
    for key in dpl.keys():
        dpl[key] *= 1e-6 * sim.cfg.dipole_scalefctr
        dpl[key] = hammfilt(dpl[key], sim.cfg.dipole_smooth_win/sim.cfg.dt)

    fig.line(expData['x'], expData['y'], legend="Experiment")

    fig.line(sim.simData['t'], dpl['L2'], legend="L2Pyr")
    fig.line(sim.simData['t'], dpl['L5'], legend="L5Pyr")
    fig.line(sim.simData['t'], dpl['L2']+dpl['L5'], legend="Aggreagate")


    plot_layout = layout(fig, sizing_mode='scale_both')
    html = file_html(plot_layout, CDN, title="Dipole Plot")

    if showFig:
        show(fig)

    return html
