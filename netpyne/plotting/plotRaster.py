# Generate a raster plot

import matplotlib.patches as mpatches
from ..analysis.utils import exception, loadData
from .plotter import ScatterPlotter


#@exception
def plotRaster(rasterData=None, popNumCells=None, popLabels=None, popColors=None, axis=None, legend=True,    colorList=None, orderInverse=False, returnPlotter=False, sim=None, **kwargs):
    """
    Function to produce a raster plot of cell spiking, grouped by population


    Parameters
    ----------
    rasterData : list, tuple, dict, str
        The data necessary to plot the raster.  If a list or a tuple, the first item should be a list of spike times and the second item should be a list the same length of spike indices (the id of the cell corresponding to the spike time).  Optionally, the third item may be a list with of string population labels corresponding to the list index (this list must be at least as long as the largest spike index).
        If rasterData is a dictionary, it must have keys 'spkTimes' and 'spkInds' and may optionally have 'indPops'.
        If rasterData is a string representing a file path, rasterData is loaded from the file.
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

    popNumCells : list
        A list of integers with the number of cells in each population.  Must be the same length as popLabels.
        **Default:** ``None`` attempts to use the names from indPop

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

    # If there is no input, get the data from the NetPyNE sim object
    if rasterData is None:
        if sim is None:
            from .. import sim
        rasterData = sim.analysis.prepareRaster(legend=legend, popLabels=popLabels, **kwargs)

    print('Plotting raster...')

    # If input is a file name, load data from the file
    if type(rasterData) == str:
        rasterData = loadData(rasterData)

    # If input is a dictionary, pull the data out of it
    if type(rasterData) == dict:
    
        spkTimes = rasterData['spkTimes']
        spkInds = rasterData['spkInds']

        if not popNumCells:
            popNumCells = rasterData.get('popNumCells')
        if not popLabels:
            popLabels = rasterData.get('popLabels')

        axisArgs = rasterData.get('axisArgs')
        legendLabels = rasterData.get('legendLabels')
    
    # If input is a list or tuple, the first item is spike times, the second is spike indices
    elif type(rasterData) == list or type(rasterData) == tuple:
        spkTimes = rasterData[0]
        spkInds = rasterData[1]
        axisArgs = None
        legendLabels = None
        
        # If there is a third item, it should be popNumCells
        if not popNumCells:
            try: popNumCells = rasterData[2]
            except: pass
        
        # If there is a fourth item, it should be popLabels 
        if not popLabels:
            try: popLabels = rasterData[3]
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
        raise Exception('In plotRaster, popNumCells and popLabels must be the same size')

    # Create a dictionary with the color for each pop
    if not colorList:
        from .plotter import colorList    
    popColorsTemp = {popLabel: colorList[ipop%len(colorList)] for ipop, popLabel in enumerate(popLabels)} 
    if popColors: 
        popColorsTemp.update(popColors)
    popColors = popColorsTemp

    # Create a list to link cells to their populations
    indPop = []
    for popLabel, popNumCell in zip(popLabels, popNumCells):
        indPop.extend(int(popNumCell) * [popLabel])

    # Create a dictionary to link cells to their population color
    cellGids = list(set(spkInds))
    gidColors = {cellGid: popColors[indPop[cellGid]] for cellGid in cellGids}  
    
    # Create a list of spkColors to be fed into the scatter plot
    spkColors = [gidColors[spkInd] for spkInd in spkInds]

    # Create a dictionary with the inputs for a scatter plot
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

    # If we use a kwarg, we add it to the list to be removed from kwargs
    kwargDels = []

    # If a kwarg matches a scatter input key, use the kwarg value instead of the default
    for kwarg in kwargs:
        if kwarg in scatterData:
            scatterData[kwarg] = kwargs[kwarg]
            kwargDels.append(kwarg)

    # Create a dictionary to hold axis inputs
    if not axisArgs:
        axisArgs = {}
        axisArgs['title'] = 'Raster Plot of Spiking'
        axisArgs['xlabel'] = 'Time (ms)'
        axisArgs['ylabel'] = 'Cells'

    # If a kwarg matches an axis input key, use the kwarg value instead of the default
    for kwarg in kwargs:
        if kwarg in axisArgs.keys():
            axisArgs[kwarg] = kwargs[kwarg]
            kwargDels.append(kwarg)
    
    # Delete any kwargs that have been used
    for kwargDel in kwargDels:
        kwargs.pop(kwargDel)

    # create Plotter object
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

        # If 'legendKwargs' is found in kwargs, use those values instead of the defaults
        if 'legendKwargs' in kwargs:
            legendKwargs = kwargs['legendKwargs']
            kwargs.pop('legendKwargs')
        else:
            legendKwargs = {}
            legendKwargs['title'] = 'Populations'
            legendKwargs['bbox_to_anchor'] = (1.025, 1)
            legendKwargs['loc'] = 2
            legendKwargs['borderaxespad'] = 0.0
            legendKwargs['handlelength'] = 0.5
            legendKwargs['fontsize'] = 'small'

        rasterPlotter.addLegend(handles, labels, **legendKwargs)
        
        # Adjust the plot to make room for the legend
        rightOffset = 0.8
        maxLabelLen = max([len(label) for label in popLabels])
        rasterPlotter.fig.subplots_adjust(right=(rightOffset - 0.012 * maxLabelLen))

    # It is often useful to invert the ordering of cells, so positions match the legend
    if orderInverse: 
        rasterPlotter.axis.invert_yaxis()

    # Generate the figure
    rasterPlot = rasterPlotter.plot(**axisArgs, **kwargs)

    # Default is to return the figure, but you can also return the plotter
    if returnPlotter:
        return rasterPlotter
    else:
        return rasterPlot