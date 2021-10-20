from netpyne.logger import logger

# Generate a plot of traces

def plotTraces(
    tracesData=None, 
    timeRange=None,
    axis=None, 
    legend=True,
    colorList=None,
    returnPlotter=False, 
    **kwargs):
    """Function to plot recorded traces

    """

    # Ensure that include is a list if it is in kwargs
    include = None
    if 'include' in kwargs:
        include = kwargs['include']
        kwargs.pop('include')
        if type(include) != list:
            include = [include]

    # If there is no input data, get the data from the NetPyNE sim object
    if tracesData is None:
        if 'sim' not in kwargs:
            from .. import sim
        else:
            sim = kwargs['sim']

        tracesData = sim.analysis.prepareTraces(include=include, sim=sim, timeRange=timeRange, **kwargs)

    time = tracesData['time']
    traceData = tracesData['tracesData']
    traces = tracesData['traces']
    cells = tracesData['cells']
    pops = tracesData['pops']

    logger.info('traces: ' + traces)
    logger.info('cells: ' + cells)
    logger.info('pops: ' + pops)

    logger.info('Plotting traces ...')

    lineData = {}
    lineData['x'] = time
    lineData['y'] = traceData
    lineData['color'] = None
    lineData['marker'] = None
    lineData['markersize'] = None
    lineData['linewidth'] = None
    lineData['alpha'] = None

    for kwarg in kwargs:
        if kwarg in lineData:
            lineData[kwarg] = kwargs[kwarg]

    axisArgs = {}
    axisArgs['title'] = 'Traces Plot'
    axisArgs['xlabel'] = 'Time (ms)'
    axisArgs['ylabel'] = 'Measure'


    linePlotter = sim.plotting.LinePlotter(data=lineData, axis=axis, **axisArgs, **kwargs)

    tracesPlot = linePlotter.plot(**axisArgs)

    # if legend:
    #     labels = []
    #     handles = []
    #     for ipop, popLabel in enumerate(rasterData['popLabels']):
    #         labels.append(rasterData['popLabelRates'][ipop] if popRates else popLabel)
    #         handles.append(mpatches.Rectangle((0,0),1,1,fc=rasterData['popColors'][popLabel]))

    #     legendKwargs = {}
    #     legendKwargs['bbox_to_anchor'] = (1.025, 1)
    #     legendKwargs['loc'] = 2
    #     legendKwargs['borderaxespad'] = 0.0
    #     legendKwargs['handlelength'] = 1.0
    #     legendKwargs['fontsize'] = 'medium'

    #     rasterPlotter.addLegend(handles, labels, **legendKwargs)

    #     rightOffset = 0.8 if popRates else 0.9
    #     maxLabelLen = max([len(label) for label in rasterData['popLabels']])
    #     rasterPlotter.fig.subplots_adjust(right=(rightOffset-0.012*maxLabelLen))


    return linePlotter
