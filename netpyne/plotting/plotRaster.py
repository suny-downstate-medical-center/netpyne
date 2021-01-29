# Generate a raster plot

def plotRaster(rasterData=None, axis=None, **kwargs):

    from .. import sim

    if rasterData is None:
        rasterData = sim.analysis.prepareRaster(**kwargs)

    print('Plotting raster...')

    dataKeys = ['spkTimes', 'spkInds', 'spkColors', 'cellGids', 'sortedGids', 'numNetStims', 'include', 'timeRange', 'maxSpikes', 'orderBy', 'orderInverse', 'spikeHist', 'syncLines']

    scatterData = {}
    scatterData['x'] = rasterData['spkTimes']
    scatterData['y'] = rasterData['spkInds']
    scatterData['c'] = rasterData['spkColors']
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


    rasterPlotter = sim.plotting.ScatterPlotter(data=scatterData, axis=axis, **kwargs)

    rasterPlotter.plot()

    return rasterPlotter
