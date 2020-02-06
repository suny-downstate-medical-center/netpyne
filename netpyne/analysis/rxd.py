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

# -------------------------------------------------------------------------------------------------------------------
## Plot RxD concentration
# -------------------------------------------------------------------------------------------------------------------
@exception
def plotRxDConcentration(speciesLabel, regionLabel, plane='xy', fontSize=12, showFig=True):
    from .. import sim
    # set font size
    plt.rcParams.update({'font.size': fontSize})

    species = sim.net.rxd['species'][speciesLabel]['hObj']
    region = sim.net.rxd['regions'][regionLabel]['hObj']
    fig=plt.figure(figsize=(4,10))
    plane2mean = {'xz': 1, 'xy': 2}
    plt.imshow(species[region].states3d[:].mean(plane2mean[plane]).T, interpolation='nearest', origin='upper')  #  extent=k[extracellular].extent('xy')
    sb = scalebar.ScaleBar(1e-6)
    sb.location='lower left'
    ax = plt.gca()
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    plt.xlabel(plane[0])
    plt.ylabel(plane[1])
    ax.add_artist(sb)
    plt.colorbar(label="$%s^+$ (mM)"%(species.name))

    # show fig 
    if showFig: _showFigure()
    
    return fig, {'data': species[region].states3d[:].mean(plane2mean[plane])}


