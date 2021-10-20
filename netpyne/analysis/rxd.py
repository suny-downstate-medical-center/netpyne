"""
Module for plotting and analysis of reaction/diffusion-related results

"""

from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

try:
    basestring
except NameError:
    basestring = str

from future import standard_library
standard_library.install_aliases()
from netpyne import __gui__

if __gui__:
    import matplotlib.pyplot as plt
    from matplotlib_scalebar.scalebar import ScaleBar
from .utils import exception, _showFigure, _saveFigData
from netpyne.logger import logger

# -------------------------------------------------------------------------------------------------------------------
## Plot RxD concentration
# -------------------------------------------------------------------------------------------------------------------
@exception
def plotRxDConcentration(speciesLabel, regionLabel, plane='xy', figSize=(5,10), clim=None, fontSize=10, scalebar=False, title=True, showFig=True, saveFig=True, **kwargs):
    """
    Function to plot reaction-diffusion concentrations

    Parameters
    ----------
    speciesLabel : <type>
        <Short description of speciesLabel>
        **Default:** *required*

    regionLabel : <type>
        <Short description of regionLabel>
        **Default:** *required*

    plane : str
        <Short description of plane>
        **Default:** ``'xy'``
        **Options:** ``<option>`` <description of option>

    figSize : tuple
        <Short description of figSize>
        **Default:** ``(5, 10)``
        **Options:** ``<option>`` <description of option>

    fontSize : int
        <Short description of fontSize>
        **Default:** ``10``
        **Options:** ``<option>`` <description of option>

    scalebar : bool
        <Short description of scalebar>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    title : bool
        <Short description of title>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    showFig : bool
        <Short description of showFig>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    saveFig : bool
        <Short description of saveFig>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>


    """



    from .. import sim

    logger.info('Plotting RxD concentration ...')

    # set font size
    plt.rcParams.update({'font.size': fontSize})

    species = sim.net.rxd['species'][speciesLabel]['hObj']
    region = sim.net.rxd['regions'][regionLabel]['hObj']
    plane2mean = {'xz': 1, 'xy': 2}

    extent = []
    extent.append(sim.net.rxd['regions'][regionLabel][plane[0] + 'lo'])
    extent.append(sim.net.rxd['regions'][regionLabel][plane[0] + 'hi'])
    extent.append(sim.net.rxd['regions'][regionLabel][plane[1] + 'lo'])
    extent.append(sim.net.rxd['regions'][regionLabel][plane[1] + 'hi'])

    vmin = None
    vmax = None
    if clim is not None:
        vmin = clim[0]
        vmax = clim[1]

    fig = plt.figure(figsize=figSize)
    plt.imshow(species[region].states3d[:].mean(plane2mean[plane]).T, interpolation='nearest', origin='upper', extent=extent, vmin=vmin, vmax=vmax)
    import numpy as np
    logger.info('  min: ' + str(np.min(species[region].states3d[:].mean(plane2mean[plane]).T)))
    logger.info('  max: '+ str(np.max(species[region].states3d[:].mean(plane2mean[plane]).T)))

    ax = plt.gca()
    if scalebar:
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        sb = ScaleBar(1e-6)
        sb.location = 'lower left'
        ax.add_artist(sb)

    cb = plt.colorbar(label='[' + species.name + '] (mM)')
    plt.xlabel(plane[0] + ' location (um)')
    plt.ylabel(plane[1] + ' location (um)')
    
    if saveFig == 'movie':
        from neuron import h
        cb.ax.set_title('Time = ' + str(round(h.t, 1)), fontsize=fontSize)

    if title:
        plt.title('RxD: ' + species.name +  ' concentration')
    plt.tight_layout()

    # show fig
    if showFig: _showFigure()

    # save figure
    if saveFig:
        if isinstance(saveFig, basestring):
            if saveFig == 'movie':
                filename = sim.cfg.filename + '_rxd_concentration_movie_' + str(round(h.t, 1)) + '.png'
            else:
                filename = saveFig
        else:
            filename = sim.cfg.filename + '_rxd_concentration.png'
        plt.savefig(filename)

    return fig, {'data': species[region].states3d[:].mean(plane2mean[plane])}

