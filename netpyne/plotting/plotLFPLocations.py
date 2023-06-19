# Generate plots of LFP (local field potentials) and related analyses

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import math
from ..analysis.utils import exception  # , loadData
from ..analysis.tools import loadData
from .plotter import LinesPlotter
from .plotter import ImagePlotter
from .plotter import MetaFigure
import numpy as np


@exception
def plotLFPLocations(sim=None, axis=None, electrodes=['all'], includeAxon=True, returnPlotter=False, **kwargs):
    """Function to produce a plot of LFP electrode locations

    NetPyNE Options
    ---------------
    sim : NetPyNE sim object
        The *sim object* from which to get data.

        *Default:* ``None`` uses the current NetPyNE sim object

    Parameters
    ----------
    axis : matplotlib axis
        The axis to plot into, allowing overlaying of plots.

        *Default:* ``None`` produces a new figure and axis.

    electrodes : list
        A *list* of the electrodes to plot from.

        *Default:* ``['all']`` plots each electrode

    includeAxon : bool
        Whether to include axons.

        *Default:* ``True``

    returnPlotter : bool
        Whether to return the figure or the NetPyNE MetaFig object.

        *Default:* ``False`` returns the figure.


    Plot Options
    ------------
    showFig : bool
        Whether to show the figure.

        *Default:* ``False``

    saveFig : bool
        Whether to save the figure.

        *Default:* ``False``

    overwrite : bool
        whether to overwrite existing figure files.

        *Default:* ``True`` overwrites the figure file

        *Options:* ``False`` adds a number to the file name to prevent overwriting


    Returns
    -------
    LFPLocationsPlot : *matplotlib figure*
        By default, returns the *figure*.  If ``returnPlotter`` is ``True``, instead returns the NetPyNE MetaFig.

    """

    print('Plotting LFP electrode locations...')

    if 'sim' not in kwargs:
        from .. import sim
    else:
        sim = kwargs['sim']

    if 'rcParams' in kwargs:
        rcParams = kwargs['rcParams']
    else:
        rcParams = None

    # electrode selection
    if 'all' in electrodes:
        electrodes.remove('all')
        electrodes.extend(list(range(int(sim.net.recXElectrode.nsites))))

    cvals = []  # used to store total transfer resistance

    for cell in sim.net.compartCells:
        trSegs = list(
            np.sum(sim.net.recXElectrode.getTransferResistance(cell.gid) * 1e3, axis=0)
        )  # convert from Mohm to kilohm
        if not includeAxon:
            i = 0
            for secName, sec in cell.secs.items():
                nseg = sec['hObj'].nseg  # .geom.nseg
                if 'axon' in secName:
                    for j in range(i, i + nseg):
                        del trSegs[j]
                i += nseg
        cvals.extend(trSegs)

    includePost = [c.gid for c in sim.net.compartCells]

    fig, data = sim.plotting.plotShape(
        axis=axis,
        includePost=includePost,
        showElectrodes=electrodes,
        cvals=cvals,
        includeAxon=includeAxon,
        kind='LFPLocations',
        **kwargs
    )

    if returnPlotter:
        return fig.metafig
    else:
        return fig
