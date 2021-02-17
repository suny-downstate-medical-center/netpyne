# Generate a raster plot

import matplotlib.patches as mpatches
from ..analysis.utils import exception
from .plotter import colorList, ScatterPlotter

#@exception
def plotRaster(rasterData=None, axis=None, legend=True, popColors=None, popLabels=None, colorList=colorList, orderInverse=False, returnPlotter=False, **kwargs):
    """
    prepare Raster
    ['include', 'sim', 'timeRange', 'maxSpikes', 'orderBy', 'popRates', 'saveData', 'fileName', 'fileDesc', 'fileType']

    include=['allCells'], sim=None, timeRange=None, maxSpikes=1e8, orderBy='gid', popRates=True, saveData=False, fileName=None, fileDesc=None, fileType=None
    """

    if rasterData is None:
        from .. import sim
        rasterData = sim.analysis.prepareRaster(legend=legend, popLabels=popLabels, **kwargs)

    print('Plotting raster...')

    dataKeys = ['spkTimes', 'spkInds', 'indPop', 'cellGids', 'numNetStims', 'include', 'timeRange', 'maxSpikes', 'orderBy', 'popLabels', 'axisArgs', 'legendLabels']

    if type(rasterData) == dict:
        spkTimes = rasterData['spkTimes']
        spkInds = rasterData['spkInds']
        indPop = rasterData.get('indPop')
        cellGids = rasterData.get('cellGids')
        axisArgs = rasterData.get('axisArgs')
        legendLabels = rasterData.get('legendLabels')
    elif type(rasterData) == list or type(rasterData) == tuple:
        spkTimes = rasterData[0]
        spkInds = rasterData[1]
        try:
            indPop = rasterData[2]
        except:
            indPop = None
        cellGids = None
        axisArgs = None
        legendLabels = None

    if not popLabels:
        if 'popLabels' in rasterData:
            popLabels = rasterData['popLabels']
        elif indPop:
            popLabels = [str(spkPop) for spkPop in list(set(indPop))]
        else:
            popLabels = ['Population']
            indPop = ['Population' for spkInd in spkInds]
    elif indPop:
        spkPopLabels = list(set(indPop))
        indPop = [popLabels[spkPopLabels.index(spkPop)] for spkPop in indPop]

    # dict with color for each pop
    popColorsTemp = {popLabel: colorList[ipop%len(colorList)] for ipop, popLabel in enumerate(popLabels)} 
    if popColors: 
        popColorsTemp.update(popColors)
    popColors = popColorsTemp
    
    if not cellGids:
        cellGids = list(set(spkInds))

    gidColors = {cellGid: popColors[indPop[cellGid]] for cellGid in cellGids}  
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
            handles.append(mpatches.Rectangle((0, 0), 1, 1, fc=popColors[popLabel]))

        legendKwargs = {}
        legendKwargs['title'] = 'Populations'
        legendKwargs['bbox_to_anchor'] = (1.025, 1)
        legendKwargs['loc'] = 2
        legendKwargs['borderaxespad'] = 0.0
        legendKwargs['handlelength'] = 0.5
        legendKwargs['fontsize'] = 'small'

        rasterPlotter.addLegend(handles, labels, **legendKwargs)

        popRates = False
        if 'popRates' in kwargs:
            popRates = kwargs['popRates']
    
        rightOffset = 0.8
        maxLabelLen = max([len(label) for label in popLabels])
        rasterPlotter.fig.subplots_adjust(right=(rightOffset-0.012*maxLabelLen))

    if orderInverse: 
        rasterPlotter.axis.invert_yaxis()

    rasterPlot = rasterPlotter.plot(**axisArgs)

    if returnPlotter:
        return rasterPlotter
    else:
        return rasterPlot