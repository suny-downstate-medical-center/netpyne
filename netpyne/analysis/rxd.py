"""
analysis/rxd.py

Functions to plot and analyze RxD-related results

Contributors: salvadordura@gmail.com
"""

from netpyne import __gui__

if __gui__:
    import matplotlib.pyplot as plt
from .utils import exception, _showFigure

# -------------------------------------------------------------------------------------------------------------------
## Plot RxD concentration
# -------------------------------------------------------------------------------------------------------------------
@exception
def plotRxDConcentration(speciesLabel, regionLabel, plane='xy', showFig=True):
    from .. import sim
    species = sim.net.rxd['species'][speciesLabel]
    region = sim.net.rxd['regions'][regionLabel]
    fig=plt.figure(figsize=(4,10))
    plane2mean = {'xz': 1, 'xy': 2}
    plt.imshow(species[region].states3d[:].mean(plane2mean[plane]).T, interpolation='nearest', origin='upper')  #  extent=k[extracellular].extent('xy')
    #sb = scalebar.ScaleBar(1e-6)
    #sb.location='lower left'
    ax = plt.gca()
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    plt.xlabel(plane[0])
    plt.ylabel(plane[1])
    #ax.add_artist(sb)
    plt.colorbar(label="$%s^+$ (mM)"%(species.name))

    # show fig 
    if showFig: _showFigure()
    
    return fig, {}


