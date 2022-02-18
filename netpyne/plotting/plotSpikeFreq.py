# Generate a spike frequency plot

import numpy as np
import matplotlib.patches as mpatches
from numbers import Number
from ..analysis.utils import exception, _smooth1d
from ..analysis.tools import loadData
from .plotter import LinesPlotter


@exception
def plotSpikeFreq(
    freqData=None, 
    axis=None, 
    timeRange=None, 
    popNumCells=None, 
    popLabels=None, 
    popColors=None, 
    binSize=5, 
    norm=False, 
    smooth=None, 
    filtFreq=None, 
    filtOrder=3,
    legend=True, 
    colorList=None, 
    returnPlotter=False, 
    **kwargs):
    """Function to produce a line plot of cell spiking frequency

    NetPyNE Options
    ---------------
    include : str, int, list
        Cells and/or NetStims to return information from.
        
        *Default:* ``['allCells', 'eachPop']`` includes average of all cells and each population of cells
        
        *Options:* 
        (1) ``'all'`` includes all cells and all NetStims, 
        (2) ``'allNetStims'`` includes all NetStims but no cells, 
        (3) a *str* which matches a popLabel includes all cells in that pop,
        (4) a *str* which matches a NetStim name includes that NetStim, 
        (5) an *int* includes the cell with that global identifier (GID), 
        (6) a *list* of *ints* includes the cells with those GIDS,
        (7) a *list* with two items, the first of which is a *str* matching a popLabel and the second of which is an *int* (or a *list* of *ints*), includes the relative cell(s) from that population (e.g. (``['popName', [0, 1]]``) includes the first two cells in popName.

    sim : NetPyNE sim object
        The *sim object* from which to get data.
        
        *Default:* ``None`` uses the current NetPyNE sim object

    Parameters
    ----------
    freqData : list, tuple, dict, str
        The data necessary to plot the raster (spike times and spike indices, at minimum). 

        *Default:* ``None`` uses ``analysis.prepareRaster`` to produce ``rasterData`` using the current NetPyNE sim object.

        *Options:* if a *list* or a *tuple*, the first item must be a *list* of spike times and the second item must be a *list* the same length of spike indices (the id of the cell corresponding to that spike time).  Optionally, a third item may be a *list* of *ints* representing the number of cells in each population (in lieu of ``popNumCells``).  Optionally, a fourth item may be a *list* of *strs* representing the population names (in lieu of ``popLabels``). 
        
        If a *dict* it must have keys ``'spkTimes'`` and ``'spkInds'`` and may optionally include ``'popNumCells'`` and ``'popLabels'``.
        
        If a *str* it must represent a file path to previously saved data.
        
    axis : matplotlib axis
        The axis to plot into, allowing overlaying of plots.
        
        *Default:* ``None`` produces a new figure and axis.

    timeRange : list
        Time range to include in the raster: ``[min, max]``.
        
        *Default:* ``None`` uses the entire simulation

    popNumCells : list
        A *list* of *ints* representing the number of cells in each population.
        
        *Default:* ``None`` puts all cells into a single population.

    popLabels : list
        A *list* of *strs* of population names.  Must be the same length as ``popNumCells``.
        
        *Default:* ``None`` uses generic names.

    popColors : dict
        A *dict* of ``popLabels`` and their desired color.
        
        *Default:* ``None`` draws from the NetPyNE default colorList.

    binSize : int
        Size of bin in ms to use for spike histogram.

        *Default:* ``5``

    norm : bool
        Whether to normalize the data.

        *Default:* ``False``

    smooth : int
        Window width for smoothing.
        
        *Default:* ``None`` does not smooth the data

    filtFreq : int or list
        Frequency for low-pass filter (int) or frequencies for bandpass filter in a list: [low, high]
        
        *Default:* ``None`` does not filter the data

    filtOrder : int
        Order of the filter defined by `filtFreq`.

        *Default:* ``3``    

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
    freqPlot : *matplotlib figure*
        By default, returns the *figure*.  If ``returnPlotter`` is ``True``, instead returns the NetPyNE MetaFig.
        
    """

    # If there is no input data, get the data from the NetPyNE sim object
    if freqData is None:
        if 'sim' not in kwargs:
            from .. import sim
        else:
            sim = kwargs['sim']

        freqData = sim.analysis.prepareSpikeHist(
            timeRange=timeRange,
            binSize=binSize, 
            **kwargs)

    # Ensure that include is a list if it is in kwargs
    if 'include' in kwargs:
        include = kwargs['include']
    else:
        include = ['eachPop', 'allCells']

    print('Plotting spike frequency...')

    # If input is a file name, load data from the file
    if type(freqData) == str:
        freqData = loadData(freqData)

    # If input is a dictionary, pull the data out of it
    if type(freqData) == dict:
    
        spkTimes = freqData['spkTimes']
        spkInds = freqData['spkInds']

        if not popNumCells:
            popNumCells = freqData.get('popNumCells')
        if not popLabels:
            popLabels = freqData.get('popLabels')

        numNetStims = freqData.get('numNetStims', 0)

        axisArgs = freqData.get('axisArgs')
        axisArgs['ylabel'] = 'Spike frequency (Hz)'
        legendLabels = freqData.get('legendLabels')
    
    # If input is a list or tuple, the first item is spike times, the second is spike indices
    elif type(freqData) == list or type(freqData) == tuple:
        spkTimes = freqData[0]
        spkInds = freqData[1]
        axisArgs = None
        legendLabels = None
        
        # If there is a third item, it should be popNumCells
        if not popNumCells:
            try: popNumCells = freqData[2]
            except: pass
        
        # If there is a fourth item, it should be popLabels 
        if not popLabels:
            try: popLabels = freqData[3]
            except: pass
    
    # If there is no info about pops, generate info for a single pop
    if not popNumCells:
        popNumCells = [max(spkInds)]
        if popLabels:
            popLabels = [str(popLabels[0])]
        else:
            popLabels = ['population']

    # If there is info about pop numbers, but not labels, generate the labels
    elif not popLabels:
        popLabels = ['pop_' + str(index) for index, pop in enumerate(popNumCells)]
        
    # If there is info about pop numbers and labels, make sure they are the same size
    if len(popNumCells) != len(popLabels):
        raise Exception('In plotSpikeHist, popNumCells (' + str(len(popNumCells)) + ') and popLabels (' + str(len(popLabels)) + ') must be the same size')

    # Replace 'eachPop' with list of pops
    if 'eachPop' in include:
        include.remove('eachPop')
        for popLabel in popLabels: 
            include.append(popLabel)

    # Create a dictionary with the color for each pop
    if not colorList:
        from .plotter import colorList    
    popColorsTemp = {popLabel: colorList[ipop%len(colorList)] for ipop, popLabel in enumerate(popLabels)} 
    if popColors: 
        popColorsTemp.update(popColors)
    popColors = popColorsTemp

    # Create a list to link cells to their populations
    indPop = []
    popGids = []
    for popLabel, popNumCell in zip(popLabels, popNumCells):
        popGids.append(np.arange(len(indPop), len(indPop) + int(popNumCell)))
        indPop.extend(int(popNumCell) * [popLabel])

    # Create a dictionary to link cells to their population
    cellGids = list(set(spkInds))
    gidPops = {cellGid: indPop[cellGid] for cellGid in cellGids}  
    
    # Set the time range appropriately
    if 'timeRange' in freqData:
        timeRange = freqData['timeRange']
    if timeRange is None:
        timeRange = [0, np.ceil(max(spkTimes))]

    # Bin the data using Numpy
    histoData = np.histogram(spkTimes, bins=np.arange(timeRange[0], timeRange[1], binSize))
    histoBins = histoData[1]
    histoCount = histoData[0]
    histoTime = histoData[1][:-1]+binSize/2

    # Convert to firing frequency
    histoCount = histoCount * (1000.0 / binSize) / (len(cellGids)+numNetStims)

    # Optionally filter
    if filtFreq:
        from scipy import signal
        fs = 1000.0/binSize
        nyquist = fs/2.0
        if isinstance(filtFreq, list): # bandpass
            Wn = [filtFreq[0]/nyquist, filtFreq[1]/nyquist]
            b, a = signal.butter(filtOrder, Wn, btype='bandpass')
        elif isinstance(filtFreq, Number): # lowpass
            Wn = filtFreq/nyquist
            b, a = signal.butter(filtOrder, Wn)
        histoCount = signal.filtfilt(b, a, histoCount)

    # Optionally normalize
    if norm:
        histoCount /= max(histoCount)

    # Optionally smooth
    if smooth:
        histoCount = _smooth1d(histoCount, smooth)[:len(histoT)]

    # Create a dictionary with the inputs for a lines plot
    plotData = {}
    plotData['x']           = histoTime
    plotData['y']           = histoCount
    plotData['color']       = popColors
    plotData['marker']      = None
    plotData['markersize']  = None
    plotData['linewidth']   = 1.0
    plotData['alpha']       = 1.0
    
    # If a kwarg matches a histogram input key, use the kwarg value instead of the default
    for kwarg in list(kwargs.keys()):
        if kwarg in plotData:
            plotData[kwarg] = kwargs[kwarg]
            kwargs.pop(kwarg)

    # Create a dictionary to hold axis inputs
    if not axisArgs:
        axisArgs = {}
        axisArgs['title'] = 'Spike frequency'
        axisArgs['xlabel'] = 'Time (ms)'
        axisArgs['ylabel'] = 'Frequency (Hz)'
        axisArgs['xlim']   = timeRange
        axisArgs['ylim']   = None

    # If a kwarg matches an axis input key, use the kwarg value instead of the default
    for kwarg in list(kwargs.keys()):
        if kwarg in axisArgs.keys():
            axisArgs[kwarg] = kwargs[kwarg]
            kwargs.pop(kwarg)

    # create Plotter object
    linesPlotter = LinesPlotter(data=plotData, kind='spikeFreq', axis=axis, **axisArgs, **kwargs)
    metaFig = linesPlotter.metafig

    # Set up a dictionary of population colors
    if not popColors:
        colorList = colorList
        popColors = {popLabel: colorList[ipop % len(colorList)] for ipop, popLabel in enumerate(popLabels)}

    # Create the labels and handles for the legend
    # (use rectangles instead of markers because some markers don't show up well)
    labels = []
    handles = []

    # Deal with the sum of all population spiking (allCells)
    if 'allCells' not in include:
        linesPlotter.y = []
        linesPlotter.color = []
    else:
        linesPlotter.y = [linesPlotter.y]
        allCellsColor = 'black'
        if 'allCellsColor' in kwargs:
            allCellsColor = kwargs['allCellsColor']
        linesPlotter.color = [allCellsColor]
        labels.append('All cells')
        handles.append(mpatches.Rectangle((0, 0), 1, 1, fc=allCellsColor))

    # Handle individual pops and grouped pops
    for subset in include:

        # if it's a single population
        if type(subset) != list:

            for popIndex, popLabel in enumerate(popLabels):

                if popLabel == subset:
                
                    # Get GIDs for this population
                    currentGids = popGids[popIndex]

                    # Use GIDs to get a spiketimes list for this population
                    spkinds, spkts = list(zip(*[(spkgid, spkt) for spkgid, spkt in zip(spkInds, spkTimes) if spkgid in currentGids]))

                    # Bin the data using Numpy
                    histoData = np.histogram(spkts, bins=np.arange(timeRange[0], timeRange[1], binSize))
                    histoCount = histoData[0]

                    # Convert to firing frequency
                    histoCount = histoCount * (1000.0 / binSize) / (len(currentGids))

                    # Optionally filter
                    if filtFreq:
                        from scipy import signal
                        fs = 1000.0/binSize
                        nyquist = fs/2.0
                        if isinstance(filtFreq, list): # bandpass
                            Wn = [filtFreq[0]/nyquist, filtFreq[1]/nyquist]
                            b, a = signal.butter(filtOrder, Wn, btype='bandpass')
                        elif isinstance(filtFreq, Number): # lowpass
                            Wn = filtFreq/nyquist
                            b, a = signal.butter(filtOrder, Wn)
                        histoCount = signal.filtfilt(b, a, histoCount)

                    # Optionally normalize
                    if norm:
                        histoCount /= max(histoCount)

                    # Optionally smooth
                    if smooth:
                        histoCount = _smooth1d(histoCount, smooth)[:len(histoT)]

                    # Append the population spiketimes list to linesPlotter.x
                    linesPlotter.y.append(histoCount)

                    # Append the population color to linesPlotter.color
                    linesPlotter.color.append(popColors[popLabel])

                    # Append the legend labels and handles
                    if legendLabels:
                        labels.append(legendLabels[popIndex])
                    else:
                        labels.append(popLabel)
                    handles.append(mpatches.Rectangle((0, 0), 1, 1, fc=popColors[popLabel]))

        # if it's a group of populations
        else:

            allGids = []
            groupLabel = None
            groupColor = None

            for popIndex, popLabel in enumerate(popLabels):

                if popLabel in subset:
                
                    # Get GIDs for this population
                    currentGids = popGids[popIndex]
                    allGids.extend(currentGids)

                    if not groupLabel:
                        groupLabel = popLabel
                    else:
                        groupLabel += ', ' + popLabel

                    if not groupColor:
                        groupColor = popColors[popLabel]

            # Use GIDs to get a spiketimes list for this population
            spkinds, spkts = list(zip(*[(spkgid, spkt) for spkgid, spkt in zip(spkInds, spkTimes) if spkgid in allGids]))

            # Bin the data using Numpy
            histoData = np.histogram(spkts, bins=np.arange(timeRange[0], timeRange[1], binSize))
            histoCount = histoData[0]

            # Convert to firing frequency
            histoCount = histoCount * (1000.0 / binSize) / (len(allGids))

            # Optionally filter
            if filtFreq:
                from scipy import signal
                fs = 1000.0/binSize
                nyquist = fs/2.0
                if isinstance(filtFreq, list): # bandpass
                    Wn = [filtFreq[0]/nyquist, filtFreq[1]/nyquist]
                    b, a = signal.butter(filtOrder, Wn, btype='bandpass')
                elif isinstance(filtFreq, Number): # lowpass
                    Wn = filtFreq/nyquist
                    b, a = signal.butter(filtOrder, Wn)
                histoCount = signal.filtfilt(b, a, histoCount)

            # Optionally normalize
            if norm:
                histoCount /= max(histoCount)

            # Optionally smooth
            if smooth:
                histoCount = _smooth1d(histoCount, smooth)[:len(histoT)]

            # Append the population spiketimes list to linesPlotter.x
            linesPlotter.y.append(histoCount)

            # Append the population color to linesPlotter.color
            linesPlotter.color.append(groupColor)

            # Append the legend labels and handles
            labels.append(groupLabel)
            handles.append(mpatches.Rectangle((0, 0), 1, 1, fc=groupColor))


    # Set up the default legend settings
    legendKwargs = {}
    legendKwargs['title'] = 'Populations'
    legendKwargs['bbox_to_anchor'] = (1.025, 1)
    legendKwargs['loc'] = 2
    legendKwargs['borderaxespad'] = 0.0
    legendKwargs['handlelength'] = 0.5
    legendKwargs['fontsize'] = 'small'

    # add legend
    if legend:
            
        # Add the legend
        linesPlotter.addLegend(handles, labels, **legendKwargs, **kwargs)
        
        # Adjust the plot to make room for the legend
        rightOffset = 0.8
        maxLabelLen = max([len(label) for label in popLabels])
        linesPlotter.fig.subplots_adjust(right=(rightOffset - 0.012 * maxLabelLen))

    # Generate the figure
    freqPlot = linesPlotter.plot(**axisArgs, **kwargs)

    # Default is to return the figure, but you can also return the plotter
    if returnPlotter:
        return metaFig
    else:
        return freqPlot