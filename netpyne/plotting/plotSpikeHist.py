# Generate a spike histogram

import numpy as np
import matplotlib.patches as mpatches
from ..analysis.utils import exception #, loadData
from ..analysis.tools import loadData
from .plotter import HistPlotter


@exception
def plotSpikeHist(
    histData=None, 
    popNumCells=None, 
    popLabels=None, 
    popColors=None, 
    axis=None, 
    legend=True, 
    colorList=None, 
    returnPlotter=False,
    histType='step',
    binSize=50, 
    stacked=False,
    cumulative=False,
    log=False,
    density=False,
    **kwargs):
    """Function to produce a histogram of cell spiking, grouped by population

    Parameters
    ----------
    histData : list, tuple, dict, str
        the data necessary to plot the spike histogram (spike times and spike indices, at minimum).  

        *Default:* ``None`` uses ``analysis.prepareSpikeHist`` to produce ``histData`` using the current NetPyNE sim object.

        *Options:* if a *list* or a *tuple*, the first item must be a *list* of spike times and the second item must be a *list* the same length of spike indices (the id of the cell corresponding to that spike time).  Optionally, a third item may be a *list* of *ints* representing the number of cells in each population (in lieu of ``popNumCells``).  Optionally, a fourth item may be a *list* of *strs* representing the population names (in lieu of ``popLabels``). 
        
        If a *dict* it must have keys ``'spkTimes'`` and ``'spkInds'`` and may optionally include ``'popNumCells'`` and ``'popLabels'``.
        
        If a *str* it must represent a file path to previously saved data.
        
    popNumCells : list
        a *list* of *ints* representing the number of cells in each population.
        
        *Default:* ``None`` puts all cells into a single population.

    popLabels : list
        a *list* of *strs* of population names.  Must be the same length as ``popNumCells``.
        
        *Default:* ``None`` uses generic names.

    popColors : dict
        a *dict* of ``popLabels`` and their desired color.
        
        *Default:* ``None`` draws from the NetPyNE default colorList.

    axis : matplotlib axis
        the axis to plot into, allowing overlaying of plots.
        
        *Default:* ``None`` produces a new figure and axis.

    legend : bool
        whether or not to add a legend to the plot.
        
        *Default:* ``True`` adds a legend.

    colorList : list
        a *list* of colors to draw from when plotting.
        
        *Default:* ``None`` uses the default NetPyNE colorList.

    returnPlotter : bool
        whether to return the figure or the NetPyNE Plotter object.
        
        *Default:* ``False`` returns the figure.

    histType : str
        type of histogram to produce.

        *Default:* ``'step'`` produces an unfilled histogram plot.

        *Options:* ``'bar'`` produces a side-by-side bar plot, ``'barstacked'`` produces a stacked bar plot, ``'stepfilled'`` produces a filled histogram. 
    
    binSize : int
        the width of bins to use (in ms)

        *Default:* ``50`` 

    stacked : bool
        whether to stack the spikes from different populations.

        *Default:* ``False`` does not stack the spikes. 
    
    cumulative : bool
        whether to produce a cumulative spike histogram.
    
        *Default:* ``False`` does not sum the spikes.
    
    log : bool
        whether to take the log of spike values.

        *Default:* ``False`` does not take the log.
    
    density : bool
        whether to normalize the spike data.

        *Default:* ``False`` does not normalize the data.


    Plot Options
    ------------
    title : str
        the axis title.

        *Default:* ``'Histogram Plot of Spiking'``
    
    xlabel : str
        label for x-axis.

        *Default:* ``'Time (ms)'``

    ylabel : str
        label for y-axis.
        
        *Default:* ``'Cells'``

    linewidth : int
        line width for the plots.
        
        *Default:* ``2.0``

    alpha : int
        The opacity of the plots.

        *Default:* ``1.0``

    legendKwargs : dict
        a *dict* containing any or all legend kwargs.  These include ``'title'``, ``'loc'``, ``'fontsize'``, ``'bbox_to_anchor'``, ``'borderaxespad'``, and ``'handlelength'``.

    rcParams : dict
        a *dict* containing any or all matplotlib rcParams.  To see all options, execute ``import matplotlib; print(matplotlib.rcParams)`` in Python.  Any options in this *dict* will be used for this current figure and then returned to their prior settings.

    overwrite : bool
        whether to overwrite existing figure files.

        *Default:* ``True`` overwrites the figure file

        *Options:* ``False`` adds a number to the file name to prevent overwriting


    NetPyNE Options
    ---------------
    include : list
        cells and/or NetStims to return information from
        
        include=['eachPop', 'allCells'],   # ['eachPop', 'allCells']

        *Default:* ``['eachPop', 'allCells']`` includes each population as well as a sum of spiking across all populations.
        
        *Options:* 
        A list with the names of populations to include.  Including 'eachPop' automatically plots all populations.  Including 'allCells' adds a histogram of the sum of spiking across all populations.

    timeRange : list
        time range to include in the raster: ``[min, max]``.
        
        *Default:* ``None`` uses the entire simulation

    popRates : bool
        whether to include the spiking rates in the plot title and legend.
        
        *Default:* ``True`` includes detailed pop information on plot.
        
        *Options:* 
        ``False`` only includes pop names.
        ``'minimal'`` includes minimal pop information.

    saveData : bool
        whether to save to a file the data used to create the figure.
        
        *Default:* ``False`` does not save the data to file

    fileName : str
        if ``saveData`` is ``True``, this is the name of the saved file.
        
        *Default:* ``None`` a file name is automatically generated.

    fileDesc : str
        an additional *str* to include in the file name just before the file extension.

        *Default:* ``None`` includes no extra text in the file name.

    fileType : str
        the type of file to save the data to.

        *Default:* ``json`` saves the file in JSON format.

        *Options:* ``pkl`` saves the file in Python Pickle format.

    fileDir : str
        the directory to save the data to.

        *Default:* ``None`` saves to the current directory.


    sim : NetPyNE sim object
        the *sim object* from which to get data.
        
        *Default:* ``None`` uses the current NetPyNE sim object
    

    Returns
    -------
    histPlot : *matplotlib figure*
        By default, returns the *figure*.  If ``returnPlotter`` is ``True``, instead returns the NetPyNE *Plotter object* used.


    Examples
    --------
    There are many options available in plotSpikeHist.  To run a variety of examples, enter the following::

        from netpyne.plotting.examples import plotRasterSim, plotRasterExamples
        sim = plotRasterSim()
        
    """

    # Ensure that include is a list if it is in kwargs
    if 'include' in kwargs:
        include = kwargs['include']
        if type(include) != list:
            include = [include]
            kwargs['include'] = include
    else:
        include = ['eachPop', 'allCells']

    # If there is no input data, get the data from the NetPyNE sim object
    if histData is None:
        if 'sim' not in kwargs:
            from .. import sim
        else:
            sim = kwargs['sim']

        histData = sim.analysis.prepareSpikeHist(legend=legend, popLabels=popLabels, **kwargs)

    print('Plotting spike histogram...')

    # If input is a file name, load data from the file
    if type(histData) == str:
        histData = loadData(histData)

    # If input is a dictionary, pull the data out of it
    if type(histData) == dict:
    
        spkTimes = histData['spkTimes']
        spkInds = histData['spkInds']

        if not popNumCells:
            popNumCells = histData.get('popNumCells')
        if not popLabels:
            popLabels = histData.get('popLabels')

        axisArgs = histData.get('axisArgs')
        legendLabels = histData.get('legendLabels')
    
    # If input is a list or tuple, the first item is spike times, the second is spike indices
    elif type(histData) == list or type(histData) == tuple:
        spkTimes = histData[0]
        spkInds = histData[1]
        axisArgs = None
        legendLabels = None
        
        # If there is a third item, it should be popNumCells
        if not popNumCells:
            try: popNumCells = histData[2]
            except: pass
        
        # If there is a fourth item, it should be popLabels 
        if not popLabels:
            try: popLabels = histData[3]
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
    if 'timeRange' in kwargs:
        timeRange = kwargs['timeRange']
    elif 'timeRange' in histData:
        timeRange = histData['timeRange']
    else:
        timeRange = [0, np.ceil(max(spkTimes))]

    # Bin the data using Numpy
    histoData = np.histogram(spkTimes, bins=np.arange(timeRange[0], timeRange[1], binSize))
    histoBins = histoData[1]
    histoCount = histoData[0]

    # Check for a couple kwargs
    alpha = None
    if 'alpha' in kwargs:
        alpha = kwargs['alpha']

    # Create a dictionary with the inputs for a histogram plot
    plotData = {}
    plotData['x']           = spkTimes
    plotData['bins']        = histoBins 
    plotData['range']       = histData.get('range', None) 
    plotData['density']     = density
    plotData['weights']     = histData.get('weights', None) 
    plotData['cumulative']  = cumulative 
    plotData['bottom']      = histData.get('bottom', None) 
    plotData['histtype']    = histType 
    plotData['align']       = histData.get('align', 'mid')
    plotData['orientation'] = histData.get('orientation', 'vertical') 
    plotData['rwidth']      = histData.get('rwidth', None)
    plotData['log']         = log
    plotData['color']       = histData.get('color', None)
    plotData['alpha']       = alpha
    plotData['label']       = histData.get('label', None)
    plotData['stacked']     = stacked
    plotData['data']        = histData.get('data', None)

    # If we use a kwarg, we add it to the list to be removed from kwargs
    kwargDels = []

    # If a kwarg matches a histogram input key, use the kwarg value instead of the default
    for kwarg in kwargs:
        if kwarg in histData:
            histData[kwarg] = kwargs[kwarg]
            kwargDels.append(kwarg)

    # Create a dictionary to hold axis inputs
    if not axisArgs:
        axisArgs = {}
        axisArgs['title'] = 'Histogram Plot of Spiking'
        axisArgs['xlabel'] = 'Time (ms)'
        axisArgs['ylabel'] = 'Number of Spikes'
        axisArgs['xlim']   = timeRange
        axisArgs['ylim']   = None

    # If a kwarg matches an axis input key, use the kwarg value instead of the default
    for kwarg in kwargs:
        if kwarg in axisArgs.keys():
            axisArgs[kwarg] = kwargs[kwarg]
            kwargDels.append(kwarg)
    
    # Delete any kwargs that have been used
    for kwargDel in kwargDels:
        kwargs.pop(kwargDel)

    # create Plotter object
    histPlotter = HistPlotter(data=plotData, kind='histogram', axis=axis, **axisArgs, **kwargs)
    multiFig = histPlotter.multifig

    # add legend
    if legend:

        # Set up a dictionary of population colors
        if not popColors:
            colorList = colorList
            popColors = {popLabel: colorList[ipop % len(colorList)] for ipop, popLabel in enumerate(popLabels)}

        # Create the labels and handles for the legend
        # (use rectangles instead of markers because some markers don't show up well)
        labels = []
        handles = []

        # Remove the sum of all population spiking when stacking
        if stacked or histType == 'barstacked':
            if 'allCells' in include:
                include.remove('allCells')

        # Deal with the sum of all population spiking (allCells)
        if 'allCells' not in include:
            histPlotter.x = []
            histPlotter.color = []
        else:
            histPlotter.x = [histPlotter.x]
            allCellsColor = 'black'
            if 'allCellsColor' in kwargs:
                allCellsColor = kwargs['allCellsColor']
            histPlotter.color = [allCellsColor]
            labels.append('All cells')
            handles.append(mpatches.Rectangle((0, 0), 1, 1, fc=allCellsColor))

        # Go through each population
        for popIndex, popLabel in enumerate(popLabels):
            
            # Get GIDs for this population
            currentGids = popGids[popIndex]

            # Use GIDs to get a spiketimes list for this population
            spkinds, spkts = list(zip(*[(spkgid, spkt) for spkgid, spkt in zip(spkInds, spkTimes) if spkgid in currentGids]))

            # Append the population spiketimes list to histPlotter.x
            histPlotter.x.append(spkts)

            # Append the population color to histPlotter.color
            histPlotter.color.append(popColors[popLabel])

            # Append the legend labels and handles
            if legendLabels:
                labels.append(legendLabels[popIndex])
            else:
                labels.append(popLabel)
            handles.append(mpatches.Rectangle((0, 0), 1, 1, fc=popColors[popLabel]))

        # Set up the default legend settings
        legendKwargs = {}
        legendKwargs['title'] = 'Populations'
        legendKwargs['bbox_to_anchor'] = (1.025, 1)
        legendKwargs['loc'] = 2
        legendKwargs['borderaxespad'] = 0.0
        legendKwargs['handlelength'] = 0.5
        legendKwargs['fontsize'] = 'small'

        # If 'legendKwargs' is found in kwargs, use those values instead of the defaults
        if 'legendKwargs' in kwargs:
            legendKwargs_input = kwargs['legendKwargs']
            kwargs.pop('legendKwargs')
            for key, value in legendKwargs_input:
                if key in legendKwargs:
                    legendKwargs[key] = value
            
        # Add the legend
        histPlotter.addLegend(handles, labels, **legendKwargs)
        
        # Adjust the plot to make room for the legend
        rightOffset = 0.8
        maxLabelLen = max([len(label) for label in popLabels])
        histPlotter.fig.subplots_adjust(right=(rightOffset - 0.012 * maxLabelLen))


    # Generate the figure
    histPlot = histPlotter.plot(**axisArgs, **kwargs)

    if axis is None:
        multiFig.finishFig(**kwargs)

    # Default is to return the figure, but you can also return the plotter
    if returnPlotter:
        return histPlotter
    else:
        return histPlot