# Generate plots of CSD PSD and related analyses


from ..analysis.utils import exception
import numpy as np
import math
from .plotter import LinesPlotter
from .plotter import MultiPlotter


@exception
def plotCSDPSD(
    PSDData=None,
    axis=None,
    timeRange=None,
    electrodes=['avg', 'all'],
    pop=None,
    separation=1.0,
    roundOffset=True,
    minFreq=1, 
    maxFreq=100, 
    stepFreq=1, 
    normSignal=False, 
    normPSD=False, 
    transformMethod='morlet',
    orderInverse=True,
    legend=True,
    colorList=None,
    returnPlotter=False,
    **kwargs):

    """Function to produce a plot of CSD Power Spectral Density (PSD) data

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

    separation : float
        Use to increase or decrease distance between signals on the plot.
    
        *Default:* ``1.0``

    roundOffset : bool
        Attempts to line up PSD signals with gridlines
    
        *Default:* ``True``

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

    Returns
    -------
    CSDPSDPlot : *matplotlib figure*
        By default, returns the *figure*.  If ``returnPlotter`` is ``True``, instead returns the NetPyNE MetaFig.
    """


    # If there is no input data, get the data from the NetPyNE sim object
    if PSDData is None:
        if 'sim' not in kwargs:
            from .. import sim
        else:
            sim = kwargs['sim']

        PSDData = sim.analysis.prepareCSDPSD(
            CSDData=None, 
            sim=sim,
            timeRange=timeRange,
            electrodes=electrodes,
            pop=pop,
            minFreq=minFreq, 
            maxFreq=maxFreq, 
            stepFreq=stepFreq, 
            normSignal=normSignal, 
            normPSD=normPSD, 
            transformMethod=transformMethod,
            **kwargs
        )

            # CSDData=None, 
            # sim=None,
            # timeRange=None,
            # electrodes=['avg', 'all'], 
            # pop=None,
            # minFreq=1, 
            # maxFreq=100, 
            # stepFreq=1, 
            # normSignal=False, 
            # normPSD=False, 
            # transformMethod='morlet', 
            # **kwargs
            # ):

    print('Plotting CSD power spectral density (PSD)...')

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
        title = 'CSD Power Spectral Density'
        if pop:
            title += ' - Population: ' + pop
        axisArgs['title'] = title
        axisArgs['xlabel'] = 'Frequency (Hz)'
        axisArgs['ylabel'] = 'Power (mVˆ2 / Hz) -- NOTE: CORRECT??'  ## ensure this is correct?


    if axis != 'multi':
        axisArgs['grid'] = {'which': 'both'}


    # Link colors to traces, make avg plot black, add separation to traces
    plotColors = []
    legendLabels = []
    colorIndex = 0
    offset = np.absolute(psds).max() * separation

    if axis == 'multi':
        offset = 0
        roundOffset = False

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
    if axis != 'multi':
        plotter = LinesPlotter(data=linesData, kind='CSDPSD', axis=axis, **axisArgs, **kwargs)
    else:
        plotter = MultiPlotter(data=linesData, kind='CSDPSD', metaFig=None, **axisArgs, **kwargs)
        ### NOTE: only kind='LFPPSD' exists for MultiPlotter in plotter.py --> ?? 


    metaFig = plotter.metafig

    # Set up the default legend settings
    legendKwargs = {}
    legendKwargs['title'] = 'Electrodes'
    legendKwargs['loc'] = 'upper right'
    legendKwargs['fontsize'] = 'small'

    # add the legend
    if legend:
        axisArgs['legend'] = legendKwargs

    # Generate the figure
    PSDPlot = plotter.plot(**axisArgs, **kwargs)


    # Default is to return the figure, but you can also return the plotter
    if returnPlotter:
        return metaFig
    else:
        return PSDPlot













