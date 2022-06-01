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
def plotLFPPSD(
    PSDData=None,
    axis=None,     
    timeRange=None,
    electrodes=['avg', 'all'],
    pop=None, 
    separation=1.0,
    roundOffset=True,
    NFFT=256,
    noverlap=128, 
    nperseg=256,
    minFreq=1, 
    maxFreq=100, 
    stepFreq=1, 
    smooth=0,
    logy=False, 
    normSignal=False,
    normPSD=False, 
    filtFreq=False, 
    filtOrder=3, 
    detrend=False, 
    transformMethod='morlet',
    orderInverse=True,
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
    PSDData : dict, str
        The data necessary to plot the LFP PSD. 

        *Default:* ``None`` uses ``analysis.preparePSD`` to produce ``PSDData`` using the current NetPyNE sim object.
        
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
        A population name to calculate PSD from.
        
        *Default:* ``None`` uses all populations.

    separation : float
        Use to increase or decrease distance between signals on the plot.
    
        *Default:* ``1.0``

    roundOffset : bool
        Attempts to line up PSD signals with gridlines
    
        *Default:* ``True``

    NFFT : int (power of 2)
        Number of data points used in each block for the PSD and time-freq FFT.
        **Default:** ``256``

    noverlap : int (<nperseg)
        Number of points of overlap between segments for PSD and time-freq.
        **Default:** ``128``

    nperseg : int
        Length of each segment for time-freq.
        **Default:** ``256``

    minFreq : float
        Minimum frequency shown in plot for PSD and time-freq.
        **Default:** ``1``

    maxFreq : float
        Maximum frequency shown in plot for PSD and time-freq.
        **Default:** ``100``

    stepFreq : float
        Step frequency.
        **Default:** ``1``

    smooth : int
        Window size for smoothing LFP; no smoothing if ``0``
        **Default:** ``0``

    logy : bool
        Whether to use a log axis.

        *Default:* ``False`` 
    
    normSignal : bool
        Whether to normalize the LFP data.

        *Default:* ``False``

    normPSD : bool
        Whether to normalize the PSD data.

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

    transformMethod : str
        The transformation method to use, either 'morlet' or 'fft'.

        *Default:* ``'morlet'`` 

    orderInverse : bool
        Whether to invert the order of plotting.

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
    LFPPSDPlot : *matplotlib figure*
        By default, returns the *figure*.  If ``returnPlotter`` is ``True``, instead returns the NetPyNE MetaFig.
        
    """


    # If there is no input data, get the data from the NetPyNE sim object
    if PSDData is None:
        if 'sim' not in kwargs:
            from .. import sim
        else:
            sim = kwargs['sim']

        PSDData = sim.analysis.preparePSD(
            PSDData=PSDData, 
            sim=sim,
            timeRange=timeRange,
            electrodes=electrodes,
            pop=pop,
            NFFT=NFFT,
            noverlap=noverlap, 
            nperseg=nperseg, 
            minFreq=minFreq, 
            maxFreq=maxFreq, 
            stepFreq=stepFreq, 
            smooth=smooth, 
            logy=logy, 
            normSignal=normSignal, 
            normPSD=normPSD, 
            filtFreq=filtFreq, 
            filtOrder=filtOrder, 
            detrend=detrend, 
            transformMethod=transformMethod,
            **kwargs
            )

    print('Plotting LFP power spectral density (PSD)...')

    # If input is a dictionary, pull the data out of it
    if type(PSDData) == dict:
    
        freqs = PSDData['psdFreqs']
        freq = freqs[0]
        psds = PSDData['psdSignal']
        names = PSDData['psdNames']
        colors = PSDData.get('colors')
        linewidths = PSDData.get('linewidths')
        alphas = PSDData.get('alphas')
        axisArgs = PSDData.get('axisArgs')

    # Set up colors, linewidths, and alphas for the plots
    if not colors:
        if not colorList:
            from .plotter import colorList
        colors = colorList[0:len(psds)]

    if not linewidths:
        linewidths = [1.0 for name in names]

    if not alphas:
        alphas = [1.0 for name in names]
    
    # Create a dictionary to hold axis inputs
    if not axisArgs:
        axisArgs = {}
        title = 'LFP Power Spectral Density'
        if pop:
            title += ' - Population: ' + pop
        axisArgs['title'] = title
        axisArgs['xlabel'] = 'Frequency (Hz)'
        axisArgs['ylabel'] = 'Power (mVˆ2 / Hz )'

    axisArgs['grid'] = {'which': 'both'}

    # Link colors to traces, make avg plot black, add separation to traces
    plotColors = []
    legendLabels = []
    colorIndex = 0
    offset = np.absolute(psds).max() * separation

    if roundOffset:
        sigfigs = 1
        if type(roundOffset) == int:
            sigfigs = roundOffset
        offset = round(offset, sigfigs - int(math.floor(math.log10(abs(offset)))) - 1)
    
    for index, (name, psd) in enumerate(zip(names, psds)):
        legendLabels.append(name)
        if orderInverse:
            psds[index] = index * offset - psd
            axisArgs['invert_yaxis'] = True
        else:
            psds[index] = index * offset + psd
        if name == 'avg':
            plotColors.append('black')
        else:
            plotColors.append(colors[colorIndex])
            colorIndex += 1

    # Create a dictionary with the inputs for a line plot
    linesData = {}
    linesData['x'] = freq
    linesData['y'] = psds
    linesData['color'] = plotColors
    linesData['marker'] = None
    linesData['markersize'] = None
    linesData['linewidth'] = None
    linesData['alpha'] = None
    linesData['label'] = legendLabels

    # If a kwarg matches a lines input key, use the kwarg value instead of the default
    for kwarg in list(kwargs.keys()):
        if kwarg in linesData:
            linesData[kwarg] = kwargs[kwarg]
            kwargs.pop(kwarg)

    # create Plotter object
    linesPlotter = LinesPlotter(data=linesData, kind='LFPPSD', axis=axis, **axisArgs, **kwargs)
    metaFig = linesPlotter.metafig

    # remove the y-axis tick labels
    # linesPlotter.axis.get_yaxis().set_ticklabels([])

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

    # Generate the figure
    PSDPlot = linesPlotter.plot(**axisArgs, **kwargs)

    # Default is to return the figure, but you can also return the plotter
    if returnPlotter:
        return metaFig
    else:
        return PSDPlot