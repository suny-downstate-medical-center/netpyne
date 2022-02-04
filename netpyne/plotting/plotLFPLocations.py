# Generate plots of LFP (local field potentials) and related analyses

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import math
from ..analysis.utils import exception #, loadData
from ..analysis.tools import loadData
from .plotter import LinesPlotter
from .plotter import ImagePlotter
from .plotter import MultiFigure
import numpy as np



#@exception
def plotLFPLocations(
    sim=None,
    axis=None, 
    electrodes=['all'],
    includeAxon=True,
    returnPlotter=False,
    **kwargs):

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

    cvals = [] # used to store total transfer resistance

    for cell in sim.net.compartCells:
        trSegs = list(np.sum(sim.net.recXElectrode.getTransferResistance(cell.gid)*1e3, axis=0)) # convert from Mohm to kilohm
        if not includeAxon:
            i = 0
            for secName, sec in cell.secs.items():
                nseg = sec['hObj'].nseg #.geom.nseg
                if 'axon' in secName:
                    for j in range(i,i+nseg): del trSegs[j]
                i+=nseg
        cvals.extend(trSegs)

    includePost = [c.gid for c in sim.net.compartCells]
    
    fig = sim.plotting.plotShape(includePost=includePost, showElectrodes=electrodes, cvals=cvals, includeAxon=includeAxon, **kwargs)[0]

    return fig




