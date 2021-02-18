# Generate a raster plot

import matplotlib.patches as mpatches
from ..analysis.utils import exception
from .plotter import ScatterPlotter

#@exception
def plotRaster(rasterData=None, axis=None, legend=True, popColors=None, popLabels=None, colorList=None, orderInverse=False, returnPlotter=False, **kwargs):
    """
    Function to produce a raster plot of cell spiking, grouped by population


    Parameters
    ----------
    rasterData : list, tuple, dict
        The data necessary to plot the raster.  If a list or a tuple, the first item should be a list of spike times and the second item should be a list the same length of spike indices (the id of the cell corresponding to the spike time).  Optionally, the third item may be a list with of string population labels corresponding to the list index (this list must be at least as long as the largest spike index).
        If rasterData is a dictionary, it must have keys 'spkTimes' and 'spkInds' and may optionally have 'indPops'.
        **Default:** ``None`` uses analysis.prepareRaster to produce rasterData using the current sim.

    axis : matplotlib axis
        The axis to plot into, allowing overlaying of plots.
        **Default:** ``None`` produces a new figure and axis

    legend : bool
        Whether or not to add a legend to the plot.
        **Default:** ``True`` adds a legend

    popColors : list
        A list of colors to use for the populations.  Must be the same length as the number of populations (i.e. the number of unique strings in indPop).
        **Default:** ``None`` draws from the NetPyNE default colorList

    popLabels : list
        A list of strings with alternate names for the populations.  Must be the same length as the number of populations (i.e. the number of unique strings in indPop).
        **Default:** ``None`` uses the names from indPop

    colorList : list
        A list of colors to draw from in plotting.
        **Default:** ``None`` uses the default NetPyNE colorList

    orderInverse : bool
        Whether or not to invert the y axis (useful if populations are defined top-down).
        **Default:** ``False`` does not invert the y axis

    returnPlotter : bool
        Whether to return the figure or the NetPyNE plotter object.
        **Default:** ``False`` returns the figure


    Keyword Arguments
    -----------------
    sim : NetPyNE sim object
        **Default:** ``None`` uses the current NetPyNE sim object

    include : string, int, list
        Cells and/or NetStims to return information for
        **Default:** ``'allCells'`` includes all cells
        **Options:** 
        (1) ``'all'`` includes all cells and all NetStims, 
        (2) ``'allNetStims'`` includes all NetStims but no cells, 
        (3) a string which matches a pop name includes all cells in that pop,
        (4) a string which matches a NetStim name includes that NetStim, 
        (5) an int includes the cell with that global identifier (GID), 
        (6) a list of ints includes the cells with those GIDS,
        (7) a list with two items, the first of which is a string matching a pop name and the second of which is an int or a list of ints, includes the relative cell(s) from that population (e.g. (``'popName', [0, 1]``) includes the first two cells in popName, which are not likely to be the cells with GID 0 and 1)

    timeRange : list
        Time range to include in the raster: [min, max]
        **Default:** ``None`` uses the entire simulation

    maxSpikes : int
        The maximum number of spikes to include (by reducing the max time range)
        **Default:** ``1e8``

    orderBy : str
        How to order the cells along the y axis
        **Default:** ``'gid'``
        **Options:** any NetPyNe cell tag, e.g. 'pop', 'x', 'ynorm' 

    popRates : bool
        Whether to include the spiking rates in the plot title/legend
        **Default:** ``True`` includes detailed pop information on plot
        **Options:** ``False`` only includes pop names,
        ``'minimal'`` includes only spiking rates on legend

    saveData : bool
        Whether to save to a file the data used to create the figure
        **Default:** ``False`` does not save the data to file

    fileName : str
        If saveData is True, this is the name of the saved file
        **Default:** ``None`` a file name is automatically generated

    fileDesc : str
        An additional string to include in the file name just before the file extension
        **Default:** ``None``

    fileType : str
        The type of file to save the data to
        **Default:** ``json`` saves the file in JSON format
        **Options:** ``pkl`` saves the file in Python Pickle format


    Other Parameters
    ----------------
    title : str
        Axis title
        **Default:** ``'Raster Plot of Spiking'``
    
    xlabel : str
        **Default:** ``'Time (ms)'``
    
    ylabel : str
        **Default:** ``'Cells'``

    s : int
        Marker size
        **Default:** ``5``

    marker : str
        Marker symbol
        **Default:** ``'|'``

    linewidth : int
        Line width
        **Default:** ``2``

    cmap
        **Default:** ``None``
    
    norm
        **Default:** ``None``
    
    alpha
        **Default:** ``None``
    
    linewidths
        **Default:** ``None``

    title : str
        Legend title
        **Default:** ``'Populations'``
        **Options:** ``None`` don't add a legend title

    bbox_to_anchor : tuple
        **Default:** ``(1.025, 1)``

    loc : int, str
        **Default:** ``2``

    borderaxespad : float
        **Default:** ``0.0``

    handlelength : float
        **Default:** ``0.5``

    fontsize: int, str
        **Default:** ``'small'``


    Returns
    -------
    rasterPlot : matplotlib figure
        By default, returns the figure.  If ``returnPlotter`` is ``True``, instead returns the NetPyNE plotter object used.


    Examples
    --------
    There are many options available in plotRaster.
    

    """

    if rasterData is None:
        from .. import sim
        rasterData = sim.analysis.prepareRaster(legend=legend, popLabels=popLabels, **kwargs)

    print('Plotting raster...')

    dataKeys = ['spkTimes', 'spkInds', 'indPops', 'cellGids', 'numNetStims', 'include', 'timeRange', 'maxSpikes', 'orderBy', 'popLabels', 'axisArgs', 'legendLabels']

    if type(rasterData) == dict:
        spkTimes = rasterData['spkTimes']
        spkInds = rasterData['spkInds']
        indPops = rasterData.get('indPops')
        cellGids = rasterData.get('cellGids')
        axisArgs = rasterData.get('axisArgs')
        legendLabels = rasterData.get('legendLabels')
    elif type(rasterData) == list or type(rasterData) == tuple:
        spkTimes = rasterData[0]
        spkInds = rasterData[1]
        try:
            indPops = rasterData[2]
        except:
            indPops = None
        cellGids = None
        axisArgs = None
        legendLabels = None

    if not popLabels:
        if 'popLabels' in rasterData:
            popLabels = rasterData['popLabels']
        elif indPops:
            # get a unique set of popLabels which maintain their order
            popLabels = list(dict.fromkeys(indPops))
        else:
            popLabels = ['Population']
            indPops = ['Population' for spkInd in spkInds]
    elif indPops:
        indPopLabels = list(dict.fromkeys(indPops))
        if len(indPopLabels) != len(popLabels):
            raise Exception('In plotRaster, the length of popLabels must equal the number of unique pops in indPops.')
        indPops = [popLabels[indPopLabels.index(indPop)] for indPop in indPops]

    # dict with color for each pop
    if not colorList:
        from .plotter import colorList    
    popColorsTemp = {popLabel: colorList[ipop%len(colorList)] for ipop, popLabel in enumerate(popLabels)} 
    if popColors: 
        popColorsTemp.update(popColors)
    popColors = popColorsTemp
    
    if not cellGids:
        cellGids = list(set(spkInds))

    gidColors = {cellGid: popColors[indPops[cellGid]] for cellGid in cellGids}  
    spkColors = [gidColors[spkInd] for spkInd in spkInds]

    scatterData = {}
    scatterData['x'] = spkTimes
    scatterData['y'] = spkInds
    scatterData['c'] = spkColors
    scatterData['s'] = 5
    scatterData['marker'] = '|'
    scatterData['linewidth'] = 2
    scatterData['cmap'] = None
    scatterData['norm'] = None
    scatterData['alpha'] = None
    scatterData['linewidths'] = None

    for kwarg in kwargs:
        if kwarg in scatterData:
            scatterData[kwarg] = kwargs[kwarg]

    if not axisArgs:
        axisArgs = {}
        axisArgs['title'] = 'Raster Plot of Spiking'
        axisArgs['xlabel'] = 'Time (ms)'
        axisArgs['ylabel'] = 'Cells'

    # check kwargs for axis arguments
    kwargDels = []
    for kwarg in kwargs:
        if kwarg in axisArgs.keys():
            axisArgs[kwarg] = kwargs[kwarg]
            kwargDels.append(kwarg)
    for kwargDel in kwargDels:
        kwargs.pop(kwargDel)

    # create plotter object
    rasterPlotter = ScatterPlotter(data=scatterData, axis=axis, **axisArgs, **kwargs)
    rasterPlotter.type = 'raster'

    # add legend
    if legend:

        if popLabels:
            if not popColors:
                colorList = colorList
                popColors = {popLabel: colorList[ipop % len(colorList)] for ipop, popLabel in enumerate(popLabels)}

        labels = []
        handles = []
        for ipop, popLabel in enumerate(popLabels):
            if legendLabels:
                labels.append(legendLabels[ipop])
            else:
                labels.append(popLabel)
            # legend uses rectangles instead of markers because some markers don't show up well:
            handles.append(mpatches.Rectangle((0, 0), 1, 1, fc=popColors[popLabel]))

        legendKwargs = {}
        legendKwargs['title'] = 'Populations'
        legendKwargs['bbox_to_anchor'] = (1.025, 1)
        legendKwargs['loc'] = 2
        legendKwargs['borderaxespad'] = 0.0
        legendKwargs['handlelength'] = 0.5
        legendKwargs['fontsize'] = 'small'

        rasterPlotter.addLegend(handles, labels, **legendKwargs)
    
        rightOffset = 0.8
        maxLabelLen = max([len(label) for label in popLabels])
        # Need to improve offset:
        rasterPlotter.fig.subplots_adjust(right=(rightOffset-0.012*maxLabelLen))

    if orderInverse: 
        rasterPlotter.axis.invert_yaxis()

    rasterPlot = rasterPlotter.plot(**axisArgs)

    if returnPlotter:
        return rasterPlotter
    else:
        return rasterPlot