# Generate a raster plot

import matplotlib.patches as mpatches
from ..analysis.utils import colorList, exception
from .plotter import ScatterPlotter

#@exception
def plotRaster(rasterData=None, axis=None, legend=True, popRates=True, orderInverse=False, popColors=None, **kwargs):

    if rasterData is None:
        from .. import sim
        rasterData = sim.analysis.prepareRaster(**kwargs)

    print('Plotting raster...')

    dataKeys = ['spkTimes', 'spkInds', 'cellGids', 'numNetStims', 'include', 'timeRange', 'maxSpikes', 'orderBy', 'popLabels', 'popLabelRates', 'gidPops']

    popLabels = rasterData['popLabels']
    spkInds = rasterData['spkInds']
    spkTimes = rasterData['spkTimes']
    spkColors = None


    # dict with color for each pop
    popColorsTmp = {popLabel: colorList[ipop%len(colorList)] for ipop,popLabel in enumerate(popLabels)} 
    if popColors: 
        popColorsTmp.update(popColors)
    popColors = popColorsTmp
    
    if len(rasterData['cellGids']) > 0:
        
        cellGids = rasterData['cellGids']
        gidPops = rasterData['gidPops']
        gidColors = {cellGid: popColors[gidPops[cellGid]] for cellGid in cellGids}  
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

    axisArgs = {}
    axisArgs['title'] = 'Raster Plot of Spiking'
    axisArgs['xlabel'] = 'Time (ms)'
    axisArgs['ylabel'] = 'Cells'

    rasterPlotter = ScatterPlotter(data=scatterData, axis=axis, **axisArgs, **kwargs)
    rasterPlotter.type = 'raster'
    rasterPlot = rasterPlotter.plot(**axisArgs)

    if legend:

        popLabels = rasterData['popLabels']
        if popLabels:
            popColors = {popLabel: colorList[ipop % len(colorList)] for ipop, popLabel in enumerate(popLabels)}

        labels = []
        handles = []
        for ipop, popLabel in enumerate(popLabels):
            labels.append(rasterData['popLabelRates'][ipop] if popRates else popLabel)
            handles.append(mpatches.Rectangle((0,0),1,1,fc=popColors[popLabel]))

        legendKwargs = {}
        legendKwargs['bbox_to_anchor'] = (1.025, 1)
        legendKwargs['loc'] = 2
        legendKwargs['borderaxespad'] = 0.0
        legendKwargs['handlelength'] = 1.0
        legendKwargs['fontsize'] = 'medium'

        rasterPlotter.addLegend(handles, labels, **legendKwargs)

        rightOffset = 0.8 if popRates else 0.9
        maxLabelLen = max([len(label) for label in rasterData['popLabels']])
        rasterPlotter.fig.subplots_adjust(right=(rightOffset-0.012*maxLabelLen))

    if orderInverse: 
        rasterPlotter.axis.invert_yaxis()

    rasterPlot = rasterPlotter.plot(**axisArgs)

    return rasterPlotter
