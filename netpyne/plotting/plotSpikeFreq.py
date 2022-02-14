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
    popNumCells=None, 
    popLabels=None, 
    popColors=None, 
    axis=None, 
    legend=True, 
    colorList=None, 
    returnPlotter=False,
    binSize=5, 
    norm=False, 
    smooth=None, 
    filtFreq=None, 
    filtOrder=3, 
    **kwargs):
    """
    Function to produce a plot of cell spiking frequency, grouped by population
        
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
    if freqData is None:
        if 'sim' not in kwargs:
            from .. import sim
        else:
            sim = kwargs['sim']

        freqData = sim.analysis.prepareSpikeHist(legend=legend, popLabels=popLabels, **kwargs)

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
    if 'timeRange' in kwargs:
        timeRange = kwargs['timeRange']
    elif 'timeRange' in freqData:
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
    
    # If we use a kwarg, we add it to the list to be removed from kwargs
    kwargDels = []

    # If a kwarg matches an input key, use the kwarg value instead of the default
    for kwarg in kwargs:
        if kwarg in plotData:
            plotData[kwarg] = kwargs[kwarg]
            kwargDels.append(kwarg)

    # Create a dictionary to hold axis inputs
    if not axisArgs:
        axisArgs = {}
        axisArgs['title'] = 'Spike frequency'
        axisArgs['xlabel'] = 'Time (ms)'
        axisArgs['ylabel'] = 'Frequency (Hz)'
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
    linesPlotter = LinesPlotter(data=plotData, kind='spikeFreq', axis=axis, **axisArgs, **kwargs)
    multiFig = linesPlotter.multifig

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

    # Go through each population
    for popIndex, popLabel in enumerate(popLabels):

        if popLabel in include:
        
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

    # add legend
    if legend:
            
        # Add the legend
        linesPlotter.addLegend(handles, labels, **legendKwargs)
        
        # Adjust the plot to make room for the legend
        rightOffset = 0.8
        maxLabelLen = max([len(label) for label in popLabels])
        linesPlotter.fig.subplots_adjust(right=(rightOffset - 0.012 * maxLabelLen))



    # Generate the figure
    freqPlot = linesPlotter.plot(**axisArgs, **kwargs)

    if axis is None:
        multiFig.finishFig(**kwargs)

    # Default is to return the figure, but you can also return the plotter
    if returnPlotter:
        return linesPlotter
    else:
        return freqPlot