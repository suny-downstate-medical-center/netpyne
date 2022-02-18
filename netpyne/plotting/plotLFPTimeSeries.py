# Generate plots of LFP (local field potentials) and related analyses

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import math
from ..analysis.utils import exception #, loadData
from ..analysis.tools import loadData
from .plotter import LinesPlotter
from .plotter import ImagePlotter
from .plotter import MetaFigure
import numpy as np


@exception
def plotLFPTimeSeries(
    LFPData=None, 
    axis=None, 
    timeRange=None,
    electrodes=['avg', 'all'], 
    pop=None,
    separation=1.0, 
    logy=False, 
    normSignal=False, 
    filtFreq=False, 
    filtOrder=3, 
    detrend=False, 
    orderInverse=True,
    overlay=False,
    scalebar=True,
    legend=True,
    colorList=None,
    returnPlotter=False,
    **kwargs):
    """Function to produce a line plot of LFP electrode signals

    NetPyNE Options
    ---------------
    sim : NetPyNE sim object
        The *sim object* from which to get data.
        
        *Default:* ``None`` uses the current NetPyNE sim object

    Parameters
    ----------
    LFPData : dict, str
        The data necessary to plot the LFP signals. 

        *Default:* ``None`` uses ``analysis.prepareLFP`` to produce ``LFPData`` using the current NetPyNE sim object.
        
        If a *str* it must represent a file path to previously saved data.
        
    axis : matplotlib axis
        The axis to plot into, allowing overlaying of plots.
        
        *Default:* ``None`` produces a new figure and axis.

    timeRange : list
        Time range to include in the raster: ``[min, max]``.
        
        *Default:* ``None`` uses the entire simulation

    electrodes : list
        A *list* of the electrodes to plot from.
        
        *Default:* ``['avg', 'all']`` plots each electrode as well as their average

    pop : str
        A population name to calculate signals from.
        
        *Default:* ``None`` uses all populations.

    separation : float
        Use to increase or decrease distance between signals on the plot.
    
        *Default:* ``1.0``

    logy : bool
        Whether to use a log axis.

        *Default:* ``False`` 
    
    normSignal : bool
        Whether to normalize the data.

        *Default:* ``False``

    filtFreq : int or list
        Frequency for low-pass filter (int) or frequencies for bandpass filter in a list: [low, high]
        
        *Default:* ``None`` does not filter the data

    filtOrder : int
        Order of the filter defined by `filtFreq`.

        *Default:* ``3``    

    detrend : bool
        Whether to detrend the data.

        *Default:* ``False``

    orderInverse : bool
        Whether to invert the order of plotting.

        *Default:* ``True``

    overlay : bool
        Option to label signals with a color-matched overlay.

        *Default:* ``False``

    scalebar : bool
        Whether to to add a scalebar to the plot.

        *Default:* ``True``

    legend : bool
        Whether or not to add a legend to the plot.
        
        *Default:* ``True`` adds a legend.

    colorList : list
        A *list* of colors to draw from when plotting.
        
        *Default:* ``None`` uses the default NetPyNE colorList.

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

    legendKwargs : dict
        a *dict* containing any or all legend kwargs.  These include ``'title'``, ``'loc'``, ``'fontsize'``, ``'bbox_to_anchor'``, ``'borderaxespad'``, and ``'handlelength'``.

    rcParams : dict
        a *dict* containing any or all matplotlib rcParams.  To see all options, execute ``import matplotlib; print(matplotlib.rcParams)`` in Python.  Any options in this *dict* will be used for this current figure and then returned to their prior settings.

    title : str
        the axis title
    
    xlabel : str
        label for x-axis
    
    ylabel : str
        label for y-axis

    linewidth : int
        line width

    alpha : float
        line opacity (0-1)

    
    Returns
    -------
    LFPTimeSeriesPlot : *matplotlib figure*
        By default, returns the *figure*.  If ``returnPlotter`` is ``True``, instead returns the NetPyNE MetaFig.
        
    """
    

    # If there is no input data, get the data from the NetPyNE sim object
    if LFPData is None:
        if 'sim' not in kwargs:
            from .. import sim
        else:
            sim = kwargs['sim']

        LFPData = sim.analysis.prepareLFP(
            sim=sim,
            timeRange=timeRange,
            electrodes=electrodes, 
            pop=pop,
            LFPData=LFPData, 
            logy=logy, 
            normSignal=normSignal, 
            filtFreq=filtFreq, 
            filtOrder=filtOrder, 
            detrend=detrend, 
            **kwargs
            )

    print('Plotting LFP time series...')

    # If input is a dictionary, pull the data out of it
    if type(LFPData) == dict:
    
        t = LFPData['t']
        lfps = LFPData['electrodes']['lfps']
        names = LFPData['electrodes']['names']
        locs = LFPData['electrodes']['locs']
        colors = LFPData.get('colors')
        linewidths = LFPData.get('linewidths')
        alphas = LFPData.get('alphas')
        axisArgs = LFPData.get('axisArgs')

    # Set up colors, linewidths, and alphas for the plots
    if not colors:
        if not colorList:
            from .plotter import colorList
        colors = colorList[0:len(lfps)]

    if not linewidths:
        linewidths = [1.0 for lfp in lfps]

    if not alphas:
        alphas = [1.0 for lfp in lfps]

    # Create a dictionary to hold axis inputs
    if not axisArgs:
        axisArgs = {}
        title = 'LFP Time Series Plot'
        if pop:
            title += ' - Population: ' + pop
        axisArgs['title'] = title
        axisArgs['xlabel'] = 'Time (ms)'
        axisArgs['ylabel'] = 'LFP Signal (uV)'

    # Link colors to traces, make avg plot black, add separation to traces
    plotColors = []
    legendLabels = []
    colorIndex = 0
    offset = np.absolute(lfps).max() * separation

    for index, (name, lfp) in enumerate(zip(names, lfps)):
        legendLabels.append(name)
        lfps[index] = index * offset + lfp
        if orderInverse:
            lfps[index] = index * offset - lfp
            axisArgs['invert_yaxis'] = True
        else:
            lfps[index] = index * offset + lfp
        if name == 'avg':
            plotColors.append('black')
        else:
            plotColors.append(colors[colorIndex])
            colorIndex += 1

    # Create a dictionary with the inputs for a line plot
    linesData = {}
    linesData['x'] = t
    linesData['y'] = lfps
    linesData['color'] = plotColors
    linesData['marker'] = None
    linesData['markersize'] = None
    linesData['linewidth'] = linewidths
    linesData['alpha'] = alphas
    linesData['label'] = legendLabels

    # If a kwarg matches a lines input key, use the kwarg value instead of the default
    for kwarg in list(kwargs.keys()):
        if kwarg in linesData:
            linesData[kwarg] = kwargs[kwarg]
            kwargs.pop(kwarg)

    # create Plotter object
    linesPlotter = LinesPlotter(data=linesData, kind='LFPTimeSeries', axis=axis, **axisArgs, **kwargs)
    metaFig = linesPlotter.metafig

    # Set up the default legend settings
    legendKwargs = {}
    legendKwargs['title'] = 'Electrodes'
    #legendKwargs['bbox_to_anchor'] = (1.025, 1)
    legendKwargs['loc'] = 'upper right'
    #legendKwargs['borderaxespad'] = 0.0
    #legendKwargs['handlelength'] = 0.5
    legendKwargs['fontsize'] = 'small'
    legendKwargs['title_fontsize'] = 'small'
    
    # add the legend
    if legend:
        axisArgs['legend'] = legendKwargs

    # add the scalebar
    if scalebar:
        #axisArgs['scalebar'] = True
        args = {}
        args['hidey'] = True
        args['matchy'] = True 
        args['hidex'] = False 
        args['matchx'] = False 
        args['sizex'] = 0 
        args['sizey'] = 1.0 
        args['ymax'] = 0.25 * offset 
        #args['labely'] = 'test'
        args['unitsy'] = '$\mu$V' 
        args['scaley'] = 1000.0
        args['loc'] = 3
        args['pad'] = 0.5 
        args['borderpad'] = 0.5 
        args['sep'] = 3 
        args['prop'] = None 
        args['barcolor'] = "black" 
        args['barwidth'] = 2
        args['space'] = 0.25 * offset

        axisArgs['scalebar'] = args

    if overlay:
        kwargs['tightLayout'] = False
        for index, name in enumerate(names):
            linesPlotter.axis.text(t[0]-0.07*(t[-1]-t[0]), (index*offset), name, color=plotColors[index], ha='center', va='center', fontsize='large', fontweight='bold')
        linesPlotter.axis.spines['top'].set_visible(False)
        linesPlotter.axis.spines['right'].set_visible(False)
        linesPlotter.axis.spines['left'].set_visible(False)
        if len(names) > 1:
            linesPlotter.fig.text(0.05, 0.4, 'LFP electrode', color='k', ha='left', va='bottom', fontsize='large', rotation=90)

    # Generate the figure
    LFPTimeSeriesPlot = linesPlotter.plot(**axisArgs, **kwargs)

    # Default is to return the figure, but you can also return the plotter
    if returnPlotter:
        return metaFig
    else:
        return LFPTimeSeriesPlot


