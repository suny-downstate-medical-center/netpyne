"""
analysis.py

Functions to plot and analyse results

Contributors: salvadordura@gmail.com
"""

from netpyne import __gui__

if __gui__:
    import matplotlib.pyplot as plt
    from matplotlib import gridspec
    from matplotlib import mlab
import numpy as np
import scipy
from numbers import Number
import math
import functools
from support.scalebar import add_scalebar

import warnings
warnings.filterwarnings("ignore")

colorList = [[0.42,0.67,0.84], [0.90,0.76,0.00], [0.42,0.83,0.59], [0.90,0.32,0.00],
            [0.34,0.67,0.67], [0.90,0.59,0.00], [0.42,0.82,0.83], [1.00,0.85,0.00],
            [0.33,0.67,0.47], [1.00,0.38,0.60], [0.57,0.67,0.33], [0.5,0.2,0.0],
            [0.71,0.82,0.41], [0.0,0.2,0.5], [0.70,0.32,0.10]]*3

# jet graded colors
# import matplotlib
# cmap = matplotlib.cm.get_cmap('jet')
# colorList = [cmap(x) for x in np.linspace(0,1,12)]

######################################################################################################################################################
## Exception decorator
######################################################################################################################################################
def exception(function):
    """
    A decorator that wraps the passed in function and prints exception should one occur
    """
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            # print 
            err = "There was an exception in %s():"%(function.__name__)
            print("%s \n %s"%(err,e))
            return -1
 
    return wrapper


######################################################################################################################################################
## Wrapper to run analysis functions in simConfig
######################################################################################################################################################
def plotData ():
    import sim

    ## Plotting
    if sim.rank == 0 and __gui__:
        sim.timing('start', 'plotTime')

        # Call analysis functions specified by user
        for funcName, kwargs in sim.cfg.analysis.iteritems():
            if kwargs == True: kwargs = {}
            elif kwargs == False: continue
            func = getattr(sim.analysis, funcName)  # get pointer to function
            out = func(**kwargs)  # call function with user arguments

        # Print timings
        if sim.cfg.timing:
            
            sim.timing('stop', 'plotTime')
            print('  Done; plotting time = %0.2f s' % sim.timingData['plotTime'])
            
            sim.timing('stop', 'totalTime')
            sumTime = sum([t for k,t in sim.timingData.iteritems() if k not in ['totalTime']])
            if sim.timingData['totalTime'] <= 1.2*sumTime:  # Print total time (only if makes sense)         
                print('\nTotal time = %0.2f s' % sim.timingData['totalTime'])

######################################################################################################################################################
## Round to n sig figures
######################################################################################################################################################
def _roundFigures(x, n):
    return round(x, -int(np.floor(np.log10(abs(x)))) + (n - 1)) 

######################################################################################################################################################
## show figure
######################################################################################################################################################
def _showFigure():
    try:
        plt.show(block=False)
    except:
        plt.show()


######################################################################################################################################################
## Save figure data
######################################################################################################################################################
def _saveFigData(figData, fileName=None, type=''):
    import sim

    if not fileName or not isinstance(fileName, basestring):
        fileName = sim.cfg.filename+'_'+type+'.pkl'

    if fileName.endswith('.pkl'): # save to pickle
        import pickle
        print('Saving figure data as %s ... ' % (fileName))
        with open(fileName, 'wb') as fileObj:
            pickle.dump(figData, fileObj)

    elif fileName.endswith('.json'):  # save to json
        import json
        print('Saving figure data as %s ... ' % (fileName))
        with open(fileName, 'w') as fileObj:
            json.dump(figData, fileObj)
    else: 
        print 'File extension to save figure data not recognized'


import numpy


######################################################################################################################################################
## Smooth 1d signal
######################################################################################################################################################
def _smooth1d(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=numpy.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=numpy.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(),s,mode='valid')
    return y[(window_len/2-1):-(window_len/2)]


######################################################################################################################################################
## Get subset of cells and netstims indicated by include list
######################################################################################################################################################
def getCellsInclude(include):
    import sim

    allCells = sim.net.allCells
    allNetStimLabels = sim.net.params.stimSourceParams.keys()
    cellGids = []
    cells = []
    netStimLabels = []
    for condition in include:
        if condition == 'all':  # all cells + Netstims 
            cellGids = [c['gid'] for c in allCells]
            cells = list(allCells)
            netStimLabels = list(allNetStimLabels)
            return cells, cellGids, netStimLabels

        elif condition == 'allCells':  # all cells 
            cellGids = [c['gid'] for c in allCells]
            cells = list(allCells)

        elif condition == 'allNetStims':  # all cells + Netstims 
            netStimLabels = list(allNetStimLabels)

        elif isinstance(condition, int):  # cell gid 
            cellGids.append(condition)
        
        elif isinstance(condition, basestring):  # entire pop
            if condition in allNetStimLabels:
                netStimLabels.append(condition)
            else:
                cellGids.extend([c['gid'] for c in allCells if c['tags']['pop']==condition])
        
        # subset of a pop with relative indices
        # when load from json gets converted to list (added as exception)
        elif (isinstance(condition, (list,tuple))  
        and len(condition)==2 
        and isinstance(condition[0], basestring) 
        and isinstance(condition[1], (list,int))):  
            cellsPop = [c['gid'] for c in allCells if c['tags']['pop']==condition[0]]
            if isinstance(condition[1], list):
                cellGids.extend([gid for i,gid in enumerate(cellsPop) if i in condition[1]])
            elif isinstance(condition[1], int):
                cellGids.extend([gid for i,gid in enumerate(cellsPop) if i==condition[1]])

        elif isinstance(condition, (list,tuple)):  # subset
            for subcond in condition:
                if isinstance(subcond, int):  # cell gid 
                    cellGids.append(subcond)
        
                elif isinstance(subcond, basestring):  # entire pop
                    if subcond in allNetStimLabels:
                        netStimLabels.append(subcond)
                    else:
                        cellGids.extend([c['gid'] for c in allCells if c['tags']['pop']==subcond])

    cellGids = sim.unique(cellGids)  # unique values
    cells = [cell for cell in allCells if cell['gid'] in cellGids]
    cells = sorted(cells, key=lambda k: k['gid'])

    return cells, cellGids, netStimLabels


######################################################################################################################################################
## Get subset of cells and netstims indicated by include list
######################################################################################################################################################
def getCellsIncludeTags(include, tags, tagsFormat=None):
    allCells = tags.copy()
    cellGids = []

    # using list with indices
    if tagsFormat or 'format' in allCells: 
        if not tagsFormat: tagsFormat = allCells.pop('format')
        popIndex = tagsFormat.index('pop')

        for condition in include:
            if condition in  ['all', 'allCells']:  # all cells 
                cellGids = allCells.keys()
                return cellGids

            elif isinstance(condition, int):  # cell gid 
                cellGids.append(condition)
            
            elif isinstance(condition, basestring):  # entire pop
                cellGids.extend([gid for gid,c in allCells.iteritems() if c[popIndex]==condition])
            
            elif isinstance(condition, tuple):  # subset of a pop with relative indices
                cellsPop = [gid for gid,c in allCells.iteritems() if c[popIndex]==condition[0]]
                if isinstance(condition[1], list):
                    cellGids.extend([gid for i,gid in enumerate(cellsPop) if i in condition[1]])
                elif isinstance(condition[1], int):
                    cellGids.extend([gid for i,gid in enumerate(cellsPop) if i==condition[1]])

    # using dict with keys
    else:
    
        for condition in include:
            if condition in  ['all', 'allCells']:  # all cells 
                cellGids = allCells.keys()
                return cellGids

            elif isinstance(condition, int):  # cell gid 
                cellGids.append(condition)
            
            elif isinstance(condition, basestring):  # entire pop
                cellGids.extend([gid for gid,c in allCells.iteritems() if c['pop']==condition])
            
            elif isinstance(condition, tuple):  # subset of a pop with relative indices
                cellsPop = [gid for gid,c in allCells.iteritems() if c['pop']==condition[0]]
                if isinstance(condition[1], list):
                    cellGids.extend([gid for i,gid in enumerate(cellsPop) if i in condition[1]])
                elif isinstance(condition[1], int):
                    cellGids.extend([gid for i,gid in enumerate(cellsPop) if i==condition[1]])

    cellGids = [int(x) for x in set(cellGids)]  # unique values

    return cellGids


######################################################################################################################################################
## Synchrony measure
######################################################################################################################################################
def syncMeasure ():
    import sim

    t0=-1 
    width=1 
    cnt=0
    for spkt in sim.allSimData['spkt']:
        if (spkt>=t0+width): 
            t0=spkt 
            cnt+=1
    return 1-cnt/(sim.cfg.duration/width)


######################################################################################################################################################
## Calculate avg and peak rate of different subsets of cells for specific time period
######################################################################################################################################################
@exception
def calculateRate (include = ['allCells', 'eachPop'], peakBin = 5, timeRange = None): 
    ''' 
    Calculate avg and peak rate of different subsets of cells for specific time period
        - include (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): List of data series to include. 
            Note: one line per item, not grouped (default: ['allCells', 'eachPop'])
        - timeRange ([start:stop]): Time range of spikes shown; if None shows all (default: None)
        - peakBin (int): Histogram bin size used to calculate peak firing rate; if None, peak rate not calculated (default: 5)
        - Returns list with rates
    '''

    import sim

    print('Calculating avg and peak firing rates ...')

    # Replace 'eachPop' with list of pops
    if 'eachPop' in include: 
        include.remove('eachPop')
        for pop in sim.net.allPops: include.append(pop)

    # time range
    if timeRange is None:
        timeRange = [0,sim.cfg.duration]

    avg, peak, histData = [], [], []

    # Plot separate line for each entry in include
    for iplot,subset in enumerate(include):
        cells, cellGids, netStimLabels = getCellsInclude([subset])
        numNetStims = 0

        # Select cells to include
        if len(cellGids) > 0:
            try:
                spkinds,spkts = zip(*[(spkgid,spkt) for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids])
            except:
                spkinds,spkts = [],[]
        else: 
            spkinds,spkts = [],[]

        # Add NetStim spikes
        spkts, spkinds = list(spkts), list(spkinds)
        numNetStims = 0
        if 'stims' in sim.allSimData:
            for netStimLabel in netStimLabels:
                netStimSpks = [spk for cell,stims in sim.allSimData['stims'].iteritems() \
                for stimLabel,stimSpks in stims.iteritems() for spk in stimSpks if stimLabel == netStimLabel]
                if len(netStimSpks) > 0:
                    lastInd = max(spkinds) if len(spkinds)>0 else 0
                    spktsNew = netStimSpks 
                    spkindsNew = [lastInd+1+i for i in range(len(netStimSpks))]
                    spkts.extend(spktsNew)
                    spkinds.extend(spkindsNew)
                    numNetStims += 1

        if peakBin:
            histo = np.histogram(spkts, bins = np.arange(timeRange[0], timeRange[1], peakBin))
            histoT = histo[1][:-1]+peakBin/2
            histoCount = histo[0] 

            histData.append(histoCount)

            histoCount = histoCount * float((1000.0 / peakBin)) / float((len(cellGids)+numNetStims)) # convert to firing rate
            peak.append(float(max(histoCount)))

        spktsRange = [spkt for spkt in spkts if timeRange[0] <= spkt <= timeRange[1]]
        avg.append(float(len(spktsRange)) / float((len(cellGids)+numNetStims)) / float((timeRange[1]-timeRange[0])) * 1000.0)

    return include, avg, peak


######################################################################################################################################################
## Plot avg and peak rates at different time periods 
######################################################################################################################################################
@exception
def plotRates (include =['allCells', 'eachPop'], peakBin = 5, timeRanges = None, timeRangeLabels = None, colors = None, figSize = ((5,5)), saveData = None, 
        ylim = None, saveFig = None, showFig = True):
    ''' 
    Calculate avg and peak rate of different subsets of cells for specific time period
        - include (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): List of data series to include. 
            Note: one line per item, not grouped (default: ['allCells', 'eachPop'])
        - timeRanges ([[start1:stop1], [start2:stop2]]): List of time range of spikes shown; if None shows all (default: None)
        - timeRangeLabels (['preStim', 'postStim']): List of labels for each time range period (default: None)
        - peakBin (int): Histogram bin size used to calculate peak firing rate; if None, peak rate not calculated (default: 5)
        - figSize ((width, height)): Size of figure (default: (10,8))
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure; 
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure (default: None)
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)

        - Returns figs
    '''
    import sim

    if not colors: colors = colorList

    avgs = []
    peaks = []
    if not timeRangeLabels:
        timeRangeLabels = ['%f-%f ms'%(t[0], t[1]) for t in timeRanges] #['period '+i for i in range(len(timeRanges))]

    for i, timeRange in enumerate(timeRanges):
        labels, avg, peak = sim.analysis.calculateRate(include=include, peakBin=peakBin, timeRange=timeRange)
        avgs.append(avg)
        peaks.append(peak)

    if showFig or saveFig:
        fig1,ax1 = plt.subplots(figsize=figSize)

        # avg
        fontsiz=14
        ax1.set_color_cycle(colors)
        ax1.plot(avgs, marker='o')
        #ax1.set_xlabel('Time period', fontsize=fontsiz)
        ax1.set_ylabel('Avg firing rate', fontsize=fontsiz)
        ax1.set_xticks(range(len(timeRangeLabels)))
        ax1.set_xticklabels(timeRangeLabels, fontsize=fontsiz)
        ax1.set_xlim(-0.5, len(avgs)-0.5)
        if ylim: ax1.set_ylim(ylim)
        ax1.legend(include)

        try:
            plt.tight_layout()
        except:
            pass

        # save figure
        if saveFig: 
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename+'_'+'avgRates.png'
            plt.savefig(filename)

        # show fig 
        if showFig: _showFigure()

        # peak
        fig2,ax2 = plt.subplots(figsize=figSize)
        ax2.set_color_cycle(colors)
        ax2.plot(peaks, marker='o')
        #ax2.set_xlabel('Time period', fontsize=fontsiz)
        ax2.set_ylabel('Peak firing rate', fontsize=fontsiz)
        ax2.set_xticks(range(len(timeRangeLabels)))
        ax2.set_xticklabels(timeRangeLabels)
        ax2.set_xlim(-0.5, len(peaks)-0.5)
        if ylim: ax2.set_ylim(ylim)
        ax2.legend(include)

        try:
            plt.tight_layout()
        except:
            pass

        # save figure
        if saveFig: 
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename+'_'+'peakRates.png'
            plt.savefig(filename)

        # show fig 
        if showFig: _showFigure()
    else:
        fig1, fig2 = None, None

        
    # save figure data
    if saveData:
        figData = {'includeList': includeList, 'timeRanges': timeRanges, 'avgs': avgs, 'peaks': peaks}

        _saveFigData(figData, saveData, 'raster')

    return fig1, fig2, avgs, peaks




######################################################################################################################################################
## Plot sync at different time periods 
######################################################################################################################################################
@exception
def plotSyncs (include =['allCells', 'eachPop'], timeRanges = None, timeRangeLabels = None, colors = None, figSize = ((5,5)), saveData = None, 
        saveFig = None, showFig = True):
    ''' 
    Calculate avg and peak rate of different subsets of cells for specific time period
        - include (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): List of data series to include. 
            Note: one line per item, not grouped (default: ['allCells', 'eachPop'])
        - timeRanges ([[start1:stop1], [start2:stop2]]): List of time range of spikes shown; if None shows all (default: None)
        - timeRangeLabels (['preStim', 'postStim']): List of labels for each time range period (default: None)
        - figSize ((width, height)): Size of figure (default: (10,8))
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure; 
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure (default: None)
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)

        - Returns figs
    '''
    import sim

    if not colors: colors = colorList

    syncs = []
    if not timeRangeLabels:
        timeRangeLabels = ['%f-%f ms'%(t[0], t[1]) for t in timeRanges] #['period '+i for i in range(len(timeRanges))]

    for i, timeRange in enumerate(timeRanges):
        print timeRange
        _, sync = sim.analysis.plotSpikeStats (include = include, timeRange = timeRange, stats = ['sync'], saveFig = False, showFig =False)
        print sync
        sync = [s[0] for s in sync]
        syncs.append(sync)

    fig1,ax1 = plt.subplots(figsize=figSize)

    # avg
    fontsiz=14
    ax1.set_color_cycle(colors)
    ax1.plot(syncs, marker='o')
    ax1.set_xlabel('Time period', fontsize=fontsiz)
    ax1.set_ylabel('Spiking synchrony', fontsize=fontsiz)
    ax1.set_xticks(range(len(timeRangeLabels)))
    ax1.set_xticklabels(timeRangeLabels)
    ax1.set_xlim(-0.5, len(syncs)-0.5)
    ax1.legend(include)

    # save figure
    if saveFig: 
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'sync.png'
        plt.savefig(filename)

    # show fig 
    if showFig: _showFigure()

    # save figure data
    if saveData:
        figData = {'includeList': includeList, 'timeRanges': timeRanges, 'syncs': syncs}

        _saveFigData(figData, saveData, 'raster')
 


    return fig1, syncs



######################################################################################################################################################
## Raster plot 
######################################################################################################################################################
@exception
def plotRaster (include = ['allCells'], timeRange = None, maxSpikes = 1e8, orderBy = 'gid', orderInverse = False, labels = 'legend', popRates = False,
        spikeHist = None, spikeHistBin = 5, syncLines = False, lw = 2, marker = '|', markerSize=5, popColors = None, figSize = (10,8), dpi = 100, saveData = None, saveFig = None, 
        showFig = True): 
    ''' 
    Raster plot of network cells 
        - include (['all',|'allCells',|'allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Cells to include (default: 'allCells')
        - timeRange ([start:stop]): Time range of spikes shown; if None shows all (default: None)
        - maxSpikes (int): maximum number of spikes that will be plotted  (default: 1e8)
        - orderBy ('gid'|'y'|'ynorm'|...): Unique numeric cell property to order y-axis by, e.g. 'gid', 'ynorm', 'y' (default: 'gid')
        - orderInverse (True|False): Invert the y-axis order (default: False)
        - labels = ('legend', 'overlay'): Show population labels in a legend or overlayed on one side of raster (default: 'legend')
        - popRates = (True|False): Include population rates (default: False)
        - spikeHist (None|'overlay'|'subplot'): overlay line over raster showing spike histogram (spikes/bin) (default: False)
        - spikeHistBin (int): Size of bin in ms to use for histogram (default: 5)
        - syncLines (True|False): calculate synchorny measure and plot vertical lines for each spike to evidence synchrony (default: False)
        - lw (integer): Line width for each spike (default: 2)
        - marker (char): Marker for each spike (default: '|')
        - popColors (dict): Dictionary with color (value) used for each population (key) (default: None)
        - figSize ((width, height)): Size of figure (default: (10,8))
        - dpi (int): Dots per inch to save fig (default: 100)
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure; 
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure (default: None)
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)

        - Returns figure handle
    '''

    import sim

    print('Plotting raster...')

    # Select cells to include
    cells, cellGids, netStimLabels = getCellsInclude(include)
    selectedPops = [cell['tags']['pop'] for cell in cells]
    popLabels = [pop for pop in sim.net.allPops if pop in selectedPops] # preserves original ordering
    if netStimLabels: popLabels.append('NetStims')
    popColorsTmp = {popLabel: colorList[ipop%len(colorList)] for ipop,popLabel in enumerate(popLabels)} # dict with color for each pop
    if popColors: popColorsTmp.update(popColors)
    popColors = popColorsTmp
    if len(cellGids) > 0:
        gidColors = {cell['gid']: popColors[cell['tags']['pop']] for cell in cells}  # dict with color for each gid
        try:
            spkgids,spkts = zip(*[(spkgid,spkt) for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids])
        except:
            spkgids, spkts = [], []
        spkgidColors = [gidColors[spkgid] for spkgid in spkgids]

    # Order by
    if len(cellGids) > 0:
        if isinstance(orderBy, basestring) and orderBy not in cells[0]['tags']:  # if orderBy property doesn't exist or is not numeric, use gid
            orderBy = 'gid'
        elif isinstance(orderBy, basestring) and not isinstance(cells[0]['tags'][orderBy], Number): 
            orderBy = 'gid'
        ylabelText = 'Cells (ordered by %s)'%(orderBy)   
    
        if orderBy == 'gid': 
            yorder = [cell[orderBy] for cell in cells]
            #sortedGids = {gid:i for i,(y,gid) in enumerate(sorted(zip(yorder,cellGids)))}
            sortedGids = [gid for y,gid in sorted(zip(yorder,cellGids))]

        elif isinstance(orderBy, basestring):
            yorder = [cell['tags'][orderBy] for cell in cells]
            #sortedGids = {gid:i for i,(y,gid) in enumerate(sorted(zip(yorder,cellGids)))}
            sortedGids = [gid for y,gid in sorted(zip(yorder,cellGids))]
        elif isinstance(orderBy, list) and len(orderBy) == 2:
            yorders = [[popLabels.index(cell['tags'][orderElem]) if orderElem=='pop' else cell['tags'][orderElem] 
                                    for cell in cells] for orderElem in orderBy] 
            #sortedGids = {gid:i for i,  in enumerate(sorted(zip(yorders[0], yorders[1], cellGids)))}
            sortedGids = [gid for (y0, y1, gid) in sorted(zip(yorders[0], yorders[1], cellGids))]

        #sortedGids = {gid:i for i, (y, gid) in enumerate(sorted(zip(yorder, cellGids)))}
        spkinds = [sortedGids.index(gid)  for gid in spkgids]

    else:
        spkts = []
        spkinds = []
        spkgidColors = []
        ylabelText = ''


    # Add NetStim spikes
    spkts,spkgidColors = list(spkts), list(spkgidColors)
    numCellSpks = len(spkts)
    numNetStims = 0
    for netStimLabel in netStimLabels:
        netStimSpks = [spk for cell,stims in sim.allSimData['stims'].iteritems() \
            for stimLabel,stimSpks in stims.iteritems() for spk in stimSpks if stimLabel == netStimLabel]
        if len(netStimSpks) > 0:
            lastInd = max(spkinds) if len(spkinds)>0 else 0
            spktsNew = netStimSpks 
            spkindsNew = [lastInd+1+i for i in range(len(netStimSpks))]
            spkts.extend(spktsNew)
            spkinds.extend(spkindsNew)
            for i in range(len(spktsNew)): 
                spkgidColors.append(popColors['NetStims'])
            numNetStims += 1
        else:
            pass
            #print netStimLabel+' produced no spikes'
    if len(cellGids)>0 and numNetStims: 
        ylabelText = ylabelText + ' and NetStims (at the end)'
    elif numNetStims:
        ylabelText = ylabelText + 'NetStims'

    if numCellSpks+numNetStims == 0:
        print 'No spikes available to plot raster'
        return None

    # Time Range
    if timeRange == [0,sim.cfg.duration]:
        pass
    elif timeRange is None:
        timeRange = [0,sim.cfg.duration]
    else:
        spkinds,spkts,spkgidColors = zip(*[(spkind,spkt,spkgidColor) for spkind,spkt,spkgidColor in zip(spkinds,spkts,spkgidColors) 
        if timeRange[0] <= spkt <= timeRange[1]])

    # Limit to maxSpikes
    if (len(spkts)>maxSpikes):
        print('  Showing only the first %i out of %i spikes' % (maxSpikes, len(spkts))) # Limit num of spikes
        if numNetStims: # sort first if have netStims
            spkts, spkinds, spkgidColors = zip(*sorted(zip(spkts, spkinds, spkgidColors)))
        spkts = spkts[:maxSpikes]
        spkinds = spkinds[:maxSpikes]
        spkgidColors = spkgidColors[:maxSpikes]
        timeRange[1] =  max(spkts)

    # Calculate spike histogram 
    if spikeHist:
        histo = np.histogram(spkts, bins = np.arange(timeRange[0], timeRange[1], spikeHistBin))
        histoT = histo[1][:-1]+spikeHistBin/2
        histoCount = histo[0]

    # Plot spikes
    fig,ax1 = plt.subplots(figsize=figSize)
    fontsiz = 12
    
    if spikeHist == 'subplot':
        gs = gridspec.GridSpec(2, 1,height_ratios=[2,1])
        ax1=plt.subplot(gs[0])
 
    ax1.scatter(spkts, spkinds, lw=lw, s=markerSize, marker=marker, color = spkgidColors) # Create raster  
    ax1.set_xlim(timeRange)
    
    # Plot stats
    gidPops = [cell['tags']['pop'] for cell in cells]
    popNumCells = [float(gidPops.count(pop)) for pop in popLabels] if numCellSpks else [0] * len(popLabels)
    totalSpikes = len(spkts)   
    totalConnections = sum([len(cell['conns']) for cell in cells])   
    numCells = len(cells) 
    firingRate = float(totalSpikes)/(numCells+numNetStims)/(timeRange[1]-timeRange[0])*1e3 if totalSpikes>0 else 0 # Calculate firing rate 
    connsPerCell = totalConnections/float(numCells) if numCells>0 else 0 # Calculate the number of connections per cell

    if popRates:
        avgRates = {}
        tsecs = (timeRange[1]-timeRange[0])/1e3 
        for i,(pop, popNum) in enumerate(zip(popLabels, popNumCells)):
            if numCells > 0 and pop != 'NetStims':
                if numCellSpks == 0:
                    avgRates[pop] = 0
                else:
                    avgRates[pop] = len([spkid for spkid in spkinds[:numCellSpks-1] if sim.net.allCells[sortedGids[int(spkid)]]['tags']['pop']==pop])/popNum/tsecs
        if numNetStims:
            popNumCells[-1] = numNetStims
            avgRates['NetStims'] = len([spkid for spkid in spkinds[numCellSpks:]])/numNetStims/tsecs 

    # Plot synchrony lines 
    if syncLines: 
        for spkt in spkts:
            ax1.plot((spkt, spkt), (0, len(cells)+numNetStims), 'r-', linewidth=0.1)
        plt.title('cells=%i syns/cell=%0.1f rate=%0.1f Hz sync=%0.2f' % (numCells,connsPerCell,firingRate,syncMeasure()), fontsize=fontsiz)
    else:
        plt.title('cells=%i syns/cell=%0.1f rate=%0.1f Hz' % (numCells,connsPerCell,firingRate), fontsize=fontsiz)

    # Axis
    ax1.set_xlabel('Time (ms)', fontsize=fontsiz)
    ax1.set_ylabel(ylabelText, fontsize=fontsiz)
    ax1.set_xlim(timeRange)
    ax1.set_ylim(-1, len(cells)+numNetStims+1)    

    # Add legend
    if popRates:
        popLabelRates = [popLabel + ' (%.3g Hz)'%(avgRates[popLabel]) for popLabel in popLabels if popLabel in avgRates]

    if labels == 'legend':
        for ipop,popLabel in enumerate(popLabels):
            label = popLabelRates[ipop] if popRates else popLabel
            plt.plot(0,0,color=popColors[popLabel],label=label)
        plt.legend(fontsize=fontsiz, bbox_to_anchor=(1.04, 1), loc=2, borderaxespad=0.)
        maxLabelLen = max([len(l) for l in popLabels])
        rightOffset = 0.85 if popRates else 0.9
        plt.subplots_adjust(right=(rightOffset-0.012*maxLabelLen))
    
    elif labels == 'overlay':
        ax = plt.gca()
        tx = 1.01
        margin = 1.0/numCells/2
        minSpacing = float(fontsiz) * 1.1 / float((0.8*figSize[1]*dpi))
        tys = [(float(popLen)/numCells)*(1-2*margin) for popLen in popNumCells]
        tysOffset = list(scipy.cumsum(tys))[:-1]
        tysOffset = [tysOffset[0]] +[tysOffset[i] + max(tysOffset[i+1]-tysOffset[i], minSpacing) for i in range(len(tysOffset)-1)]
        tysOffset.insert(0, 0)
        labels = popLabelRates if popRates else popLabels
        for ipop,(ty, tyOffset, popLabel) in enumerate(zip(tys, tysOffset, popLabels)):
            label = popLabelRates[ipop] if popRates else popLabel
            if orderInverse:
                finalty = 1.0 - (tyOffset + ty/2.0 + 0.01)
            else:
                finalty = tyOffset + ty/2.0 - 0.01
            plt.text(tx, finalty, label, transform=ax.transAxes, fontsize=fontsiz, color=popColors[popLabel])
        maxLabelLen = min(6, max([len(l) for l in labels]))
        plt.subplots_adjust(right=(0.95-0.011*maxLabelLen))

    # Plot spike hist
    if spikeHist == 'overlay':
        ax2 = ax1.twinx()
        ax2.plot (histoT, histoCount, linewidth=0.5)
        ax2.set_ylabel('Spike count', fontsize=fontsiz) # add yaxis label in opposite side
        ax2.set_xlim(timeRange)
    elif spikeHist == 'subplot':
        ax2=plt.subplot(gs[1])
        ax2.plot (histoT, histoCount, linewidth=1.0)
        ax2.set_xlabel('Time (ms)', fontsize=fontsiz)
        ax2.set_ylabel('Spike count', fontsize=fontsiz)
        ax2.set_xlim(timeRange)

    if orderInverse: plt.gca().invert_yaxis()

    # save figure data
    if saveData:
        figData = {'spkTimes': spkts, 'spkInds': spkinds, 'spkColors': spkgidColors, 'cellGids': cellGids, 'sortedGids': sortedGids, 'numNetStims': numNetStims, 
        'include': include, 'timeRange': timeRange, 'maxSpikes': maxSpikes, 'orderBy': orderBy, 'orderInverse': orderInverse, 'spikeHist': spikeHist,
        'syncLines': syncLines}

        _saveFigData(figData, saveData, 'raster')
 
    # save figure
    if saveFig: 
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'raster.png'
        plt.savefig(filename, dpi=dpi)

    # show fig 
    if showFig: _showFigure()

    return fig


######################################################################################################################################################
## Plot spike histogram
######################################################################################################################################################
@exception
def plotSpikeHist (include = ['allCells', 'eachPop'], timeRange = None, binSize = 5, overlay=True, graphType='line', yaxis = 'rate', 
    popColors = [], norm = False, dpi = 100, figSize = (10,8), smooth=None, filtFreq = False, filtOrder=3, axis = 'on', saveData = None, 
    saveFig = None, showFig = True, **kwargs): 
    ''' 
    Plot spike histogram
        - include (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): List of data series to include. 
            Note: one line per item, not grouped (default: ['allCells', 'eachPop'])
        - timeRange ([start:stop]): Time range of spikes shown; if None shows all (default: None)
        - binSize (int): Size in ms of each bin (default: 5)
        - overlay (True|False): Whether to overlay the data lines or plot in separate subplots (default: True)
        - graphType ('line'|'bar'): Type of graph to use (line graph or bar plot) (default: 'line')
        - yaxis ('rate'|'count'): Units of y axis (firing rate in Hz, or spike count) (default: 'rate')
        - popColors (dict): Dictionary with color (value) used for each population (key) (default: None)
        - figSize ((width, height)): Size of figure (default: (10,8))
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure;
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure;
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)

        - Returns figure handle
    '''

    import sim

    print('Plotting spike histogram...')

    # Replace 'eachPop' with list of pops
    if 'eachPop' in include: 
        include.remove('eachPop')
        for pop in sim.net.allPops: include.append(pop)

    # Y-axis label
    if yaxis == 'rate': 
        if norm:
            yaxisLabel = 'Normalized firing rate'
        else:
            yaxisLabel = 'Avg cell firing rate (Hz)'
    elif yaxis == 'count': 
        if norm:
            yaxisLabel = 'Normalized spike count'
        else:
            yaxisLabel = 'Spike count'
    else:
        print 'Invalid yaxis value %s', (yaxis)
        return


    # time range
    if timeRange is None:
        timeRange = [0,sim.cfg.duration]

    histData = []

    # create fig
    fig,ax1 = plt.subplots(figsize=figSize)
    fontsiz = 12
    
    # Plot separate line for each entry in include
    for iplot,subset in enumerate(include):
        cells, cellGids, netStimLabels = getCellsInclude([subset])
        numNetStims = 0

        # Select cells to include
        if len(cellGids) > 0:
            try:
                spkinds,spkts = zip(*[(spkgid,spkt) for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids])
            except:
                spkinds,spkts = [],[]
        else: 
            spkinds,spkts = [],[]

        # Add NetStim spikes
        spkts, spkinds = list(spkts), list(spkinds)
        numNetStims = 0
        if 'stims' in sim.allSimData:
            for netStimLabel in netStimLabels:
                netStimSpks = [spk for cell,stims in sim.allSimData['stims'].iteritems() \
                for stimLabel,stimSpks in stims.iteritems() for spk in stimSpks if stimLabel == netStimLabel]
                if len(netStimSpks) > 0:
                    lastInd = max(spkinds) if len(spkinds)>0 else 0
                    spktsNew = netStimSpks 
                    spkindsNew = [lastInd+1+i for i in range(len(netStimSpks))]
                    spkts.extend(spktsNew)
                    spkinds.extend(spkindsNew)
                    numNetStims += 1

        histo = np.histogram(spkts, bins = np.arange(timeRange[0], timeRange[1], binSize))
        histoT = histo[1][:-1]+binSize/2
        histoCount = histo[0] 

        if yaxis=='rate': 
            histoCount = histoCount * (1000.0 / binSize) / (len(cellGids)+numNetStims) # convert to firing rate

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

        if norm:
            histoCount /= max(histoCount)

        if smooth:
            histoCount = _smooth1d(histoCount, smooth)[:len(histoT)]
            
        histData.append(histoCount)

        color = popColors[subset] if subset in popColors else colorList[iplot%len(colorList)] 

        if not overlay: 
            plt.subplot(len(include),1,iplot+1)  # if subplot, create new subplot
            plt.title (str(subset), fontsize=fontsiz)
            color = 'blue'
   
        if graphType == 'line':
            plt.plot (histoT, histoCount, linewidth=1.0, color = color)
        elif graphType == 'bar':
            #plt.bar(histoT, histoCount, width = binSize, color = color, fill=False)
            plt.plot (histoT, histoCount, linewidth=1.0, color = color, ls='steps')

        if iplot == 0: 
            plt.xlabel('Time (ms)', fontsize=fontsiz)
            plt.ylabel(yaxisLabel, fontsize=fontsiz) # add yaxis in opposite side
        plt.xlim(timeRange)

    if len(include) < 5:  # if apply tight_layout with many subplots it inverts the y-axis
        try:
            plt.tight_layout()
        except:
            pass

    # Add legend
    if overlay:
        for i,subset in enumerate(include):
            color = popColors[subset] if subset in popColors else colorList[i%len(colorList)] 
            plt.plot(0,0,color=color,label=str(subset))
        plt.legend(fontsize=fontsiz, bbox_to_anchor=(1.04, 1), loc=2, borderaxespad=0.)
        maxLabelLen = min(10,max([len(str(l)) for l in include]))
        plt.subplots_adjust(right=(0.9-0.012*maxLabelLen))

    # Set axis or scaleber
    if axis == 'off':
        ax = plt.gca()
        scalebarLoc = kwargs.get('scalebarLoc', 7)
        round_to_n = lambda x, n, m: int(np.round(round(x, -int(np.floor(np.log10(abs(x)))) + (n - 1)) / m)) * m 
        sizex = round_to_n((timeRange[1]-timeRange[0])/10.0, 1, 50)
        add_scalebar(ax, hidex=False, hidey=True, matchx=False, matchy=True, sizex=sizex, sizey=None, 
                    unitsx='ms', unitsy='Hz', scalex=1, scaley=1, loc=scalebarLoc, pad=2, borderpad=0.5, sep=4, prop=None, barcolor="black", barwidth=3)  
        plt.axis(axis)

    # save figure data
    if saveData:
        figData = {'histData': histData, 'histT': histoT, 'include': include, 'timeRange': timeRange, 'binSize': binSize,
         'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}
    
        _saveFigData(figData, saveData, 'spikeHist')
 
    # save figure
    if saveFig: 
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'spikeHist.png'
        plt.savefig(filename, dpi=dpi)

    # show fig 
    if showFig: _showFigure()

    return fig, histData, histoT



######################################################################################################################################################
## Plot spike histogram
######################################################################################################################################################3
#@exception
def plotSpikeStats (include = ['allCells', 'eachPop'], statDataIn = {}, timeRange = None, graphType='boxplot', stats = ['rate', 'isicv'], bins = 50,
                 popColors = [], histlogy = False, histlogx = False, histmin = 0.0, density = False, includeRate0=False, legendLabels = None, normfit = False,
                 fontsize=14, histShading=True, xlim = None, dpi = 100, figSize = (6,8), saveData = None, saveFig = None, showFig = True, **kwargs): 
    ''' 
    Plot spike histogram
        - include (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): List of data series to include. 
            Note: one line per item, not grouped (default: ['allCells', 'eachPop'])
        - timeRange ([start:stop]): Time range of spikes shown; if None shows all (default: None)
        - graphType ('boxplot', 'histogram'): Type of graph to use (default: 'boxplot')
        - stats (['rate', |'isicv'| 'sync'| 'pairsync']): Measure to plot stats on (default: ['rate', 'isicv'])
        - bins (int or list of edges): Number of bins (if integer) of edges (if list) for histogram (default: 50)
        - popColors (dict): Dictionary with color (value) used for each population (key) (default: None)
        - figSize ((width, height)): Size of figure (default: (10,8))
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure;
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure;
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)

        - Returns figure handle and statData
    '''

    import sim

    print('Plotting spike stats...')

    # Set plot style
    colors = []
    params = {
        'axes.labelsize': 14,
        'font.size': 14,
        'legend.fontsize': 14,
        'xtick.labelsize': 14,
        'ytick.labelsize': 14,
        'text.usetex': False,
        }
    plt.rcParams.update(params)

    xlabels = {'rate': 'Rate (Hz)', 'isicv': 'Irregularity (ISI CV)', 'sync':  'Synchrony', ' pairsync': 'Pairwise synchrony'}

    # Replace 'eachPop' with list of pops
    if 'eachPop' in include: 
        include.remove('eachPop')
        for pop in sim.net.allPops: include.append(pop)

    # time range
    if timeRange is None:
        timeRange = [0,sim.cfg.duration]

    for stat in stats:
        # create fig
        fig,ax1 = plt.subplots(figsize=figSize)
        fontsiz = fontsize 
        xlabel = xlabels[stat]

        statData = []
        gidsData = []
        ynormsData = []

        # Calculate data for each entry in include
        for iplot,subset in enumerate(include):

            if stat in statDataIn:
                statData = statDataIn[stat]['statData']
                gidsData = statDataIn[stat].get('gidsData', [])
                ynormsData = statDataIn[stat].get('ynormsData', [])

            else:
                cells, cellGids, netStimLabels = getCellsInclude([subset])
                numNetStims = 0

                # Select cells to include
                if len(cellGids) > 0:
                    try:
                        spkinds,spkts = zip(*[(spkgid,spkt) for spkgid,spkt in 
                            zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids])
                    except:
                        spkinds,spkts = [],[]
                else: 
                    spkinds,spkts = [],[]

                # Add NetStim spikes
                spkts, spkinds = list(spkts), list(spkinds)
                numNetStims = 0
                if 'stims' in sim.allSimData:
                    for netStimLabel in netStimLabels:
                        netStimSpks = [spk for cell,stims in sim.allSimData['stims'].iteritems() \
                        for stimLabel,stimSpks in stims.iteritems() 
                            for spk in stimSpks if stimLabel == netStimLabel]
                        if len(netStimSpks) > 0:
                            lastInd = max(spkinds) if len(spkinds)>0 else 0
                            spktsNew = netStimSpks 
                            spkindsNew = [lastInd+1+i for i in range(len(netStimSpks))]
                            spkts.extend(spktsNew)
                            spkinds.extend(spkindsNew)
                            numNetStims += 1
                try:
                    spkts,spkinds = zip(*[(spkt, spkind) for spkt, spkind in zip(spkts, spkinds) 
                        if timeRange[0] <= spkt <= timeRange[1]])
                except:
                    pass

                # if scatter get gids and ynorm
                if graphType == 'scatter':    
                    if includeRate0:
                        gids = cellGids
                    else:
                        gids = set(spkinds)
                    ynorms = [sim.net.allCells[int(gid)]['tags']['ynorm'] for gid in gids]

                    gidsData.insert(0, gids)
                    ynormsData.insert(0, ynorms)

                # rate stats
                if stat == 'rate':
                    toRate = 1e3/(timeRange[1]-timeRange[0])
                    if includeRate0:
                        rates = [spkinds.count(gid)*toRate for gid in cellGids] \
                            if len(spkinds)>0 else [0]*len(cellGids) #cellGids] #set(spkinds)] 
                    else:
                        rates = [spkinds.count(gid)*toRate for gid in set(spkinds)] \
                            if len(spkinds)>0 else [0] #cellGids] #set(spkinds)] 

                    statData.insert(0, rates)


                # Inter-spike interval (ISI) coefficient of variation (CV) stats
                elif stat == 'isicv':
                    import numpy as np
                    spkmat = [[spkt for spkind,spkt in zip(spkinds,spkts) if spkind==gid] 
                        for gid in set(spkinds)]
                    isimat = [[t - s for s, t in zip(spks, spks[1:])] for spks in spkmat if len(spks)>10]
                    isicv = [np.std(x) / np.mean(x) if len(x)>0 else 0 for x in isimat] # if len(x)>0] 
                    statData.insert(0, isicv) 


                # synchrony
                elif stat in ['sync', 'pairsync']:
                    try: 
                        import pyspike  
                    except:
                        print "Error: plotSpikeStats() requires the PySpike python package \
                            to calculate synchrony (try: pip install pyspike)"
                        return 0
                    
                    spkmat = [pyspike.SpikeTrain([spkt for spkind,spkt in zip(spkinds,spkts) 
                        if spkind==gid], timeRange) for gid in set(spkinds)]
                    if stat == 'sync':
                        # (SPIKE-Sync measure)' # see http://www.scholarpedia.org/article/Measures_of_spike_train_synchrony
                        syncMat = [pyspike.spike_sync(spkmat)]
                        #graphType = 'bar'
                    elif stat == 'pairsync':
                        # (SPIKE-Sync measure)' # see http://www.scholarpedia.org/article/Measures_of_spike_train_synchrony
                        syncMat = np.mean(pyspike.spike_sync_matrix(spkmat), 0)
                        

                    statData.insert(0, syncMat)

            colors.insert(0, popColors[subset] if subset in popColors 
                else colorList[iplot%len(colorList)])  # colors in inverse order

        # if 'allCells' included make it black
        if include[0] == 'allCells':
            #if graphType == 'boxplot':
            colors.insert(len(include), (0.5,0.5,0.5))  # 
            del colors[0]

        # boxplot
        if graphType == 'boxplot':
            meanpointprops = dict(marker=(5,1,0), markeredgecolor='black', markerfacecolor='white')
            labels = legendLabels if legendLabels else include
            bp=plt.boxplot(statData, labels=labels, notch=False, sym='k+', meanprops=meanpointprops, 
                        whis=1.5, widths=0.6, vert=False, showmeans=True, patch_artist=True)
            plt.xlabel(xlabel, fontsize=fontsiz)
            plt.ylabel('Population', fontsize=fontsiz) 

            icolor=0
            borderColor = 'k'
            for i in range(0, len(bp['boxes'])):
                icolor = i
                bp['boxes'][i].set_facecolor(colors[icolor])
                bp['boxes'][i].set_linewidth(2)
                # we have two whiskers!
                bp['whiskers'][i*2].set_color(borderColor)
                bp['whiskers'][i*2 + 1].set_color(borderColor)
                bp['whiskers'][i*2].set_linewidth(2)
                bp['whiskers'][i*2 + 1].set_linewidth(2)
                bp['medians'][i].set_color(borderColor)
                bp['medians'][i].set_linewidth(3)
                # for f in bp['fliers']:
                #    f.set_color(colors[icolor])
                #    print f
                # and 4 caps to remove
                for c in bp['caps']:
                    c.set_color(borderColor)
                    c.set_linewidth(2)

            ax = plt.gca()
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.get_xaxis().tick_bottom()
            ax.get_yaxis().tick_left()
            ax.tick_params(axis='x', length=0)
            ax.tick_params(axis='y', direction='out')
            ax.grid(axis='x', color="0.9", linestyle='-', linewidth=1)
            ax.set_axisbelow(True)
            if xlim: ax.set_xlim(xlim)

        # histogram
        elif graphType == 'histogram':
            import numpy as np

            nmax = 0
            pdfmax = 0
            binmax = 0
            for i,data in enumerate(statData):  # fix 
                if histlogx:
                    histbins = np.logspace(np.log10(histmin), np.log10(max(data)), bins)
                else:
                    histbins = bins

                if histmin: # min value 
                    data = np.array(data)
                    data = data[data>histmin]
                
                # if histlogy:
                #     data = [np.log10(x) for x in data]

                if density:
                    weights = np.ones_like(data)/float(len(data)) 
                else: 
                    weights = np.ones_like(data)

                n, binedges,_ = plt.hist(data,  bins=histbins, histtype='step', color=colors[i], linewidth=2, weights=weights)#, normed=1)#, normed=density)# weights=weights)
                if histShading:
                    plt.hist(data, bins=histbins, alpha=0.05, color=colors[i], linewidth=0, weights=weights) 
                label = legendLabels[-i-1] if legendLabels else str(include[-i-1])
                if histShading:
                    plt.hist([-10], bins=histbins, fc=((colors[i][0], colors[i][1], colors[i][2],0.05)), edgecolor=colors[i], linewidth=2, label=label)
                else:
                    plt.hist([-10], bins=histbins, fc=((1,1,1),0), edgecolor=colors[i], linewidth=2, label=label)
                nmax = max(nmax, max(n))
                binmax = max(binmax, binedges[-1])
                if histlogx: 
                    plt.xscale('log')

                if normfit:
                    def lognorm(meaninput, stdinput, binedges, n, popLabel, color):
                        from scipy import stats 
                        M = float(meaninput) # Geometric mean == median
                        s = float(stdinput) # Geometric standard deviation
                        mu = np.log10(M) # Mean of log(X)
                        sigma = np.log10(s) # Standard deviation of log(X)                        
                        shape = sigma # Scipy's shape parameter
                        scale = np.power(10, mu) # Scipy's scale parameter
                        x = [(binedges[i]+binedges[i+1])/2.0 for i in range(len(binedges)-1)]  #np.linspace(histmin, 30, num=400) # values for x-axis
                        pdf = stats.lognorm.pdf(x, shape, loc=0, scale=scale) # probability distribution
                        R, p = scipy.stats.pearsonr(n, pdf)
                        print '    Pop %s rate: mean=%f, std=%f, lognorm mu=%f, lognorm sigma=%f, R=%.2f (p-value=%.2f)' % (popLabel, M, s, mu, sigma, R, p)
                        plt.semilogx(x, pdf, color=color, ls='dashed')
                        return pdf


                    fitmean = np.mean(data)
                    fitstd = np.std(data)
                    pdf=lognorm(fitmean, fitstd, binedges, n, label, colors[i])
                    pdfmax = max(pdfmax, max(pdf))
                    nmax = max(nmax, pdfmax)

                    # check normality of distribution
                    #W, p = scipy.stats.shapiro(data)
                    #print 'Pop %s rate: mean = %f, std = %f, normality (Shapiro-Wilk test) = %f, p-value = %f' % (include[i], mu, sigma, W, p)


            plt.xlabel(xlabel, fontsize=fontsiz)
            plt.ylabel('Probability of occurrence' if density else 'Frequency', fontsize=fontsiz)
            xmax = binmax
            plt.xlim(histmin, xmax)
            plt.ylim(0, 1.1*nmax if density else np.ceil(1.1*nmax)) #min(n[n>=0]), max(n[n>=0]))
            plt.legend(fontsize=fontsiz)

            # plt.show() # REMOVE!

            # if xlim: ax.set_xlim(xlim)

            #from IPython import embed; embed()

        # scatter
        elif graphType == 'scatter':
            from scipy import stats
            for i,(ynorms,data) in enumerate(zip(ynormsData, statData)):
                mean, binedges, _ = stats.binned_statistic(ynorms, data, 'mean', bins=bins)
                median, binedges, _ = stats.binned_statistic(ynorms, data, 'median', bins=bins)
                #p25 = lambda x: np.percentile(x, 25)
                #p75 = lambda x: np.percentile(x, 75)
                
                std, binedges, _ = stats.binned_statistic(ynorms, data, 'std', bins=bins)
                #per25, binedges, _ = stats.binned_statistic(ynorms, data, p25, bins=bins)
                #per75, binedges, _ = stats.binned_statistic(ynorms, data, p75, bins=bins)
                
                label = legendLabels[-i-1] if legendLabels else str(include[-i-1])
                if kwargs.get('differentColor', None):
                    threshold = kwargs['differentColor'][0]
                    newColor = kwargs['differentColor'][1] #
                    plt.scatter(ynorms[:threshold], data[:threshold], color=[6/255.0,8/255.0,(64+30)/255.0], label=label, s=2) #, [0/255.0,215/255.0,255/255.0], [88/255.0,204/255.0,20/255.0]
                    plt.scatter(ynorms[threshold:], data[threshold:], color=newColor, alpha= 0.2, s=2) #[88/255.0,204/255.0,20/255.0]
                else:
                    plt.scatter(ynorms, data, color=[0/255.0,215/255.0,255/255.0], label=label, s=2) #[88/255.0,204/255.0,20/255.0]
                binstep = binedges[1]-binedges[0]
                bincenters = [b+binstep/2 for b in binedges[:-1]] 
                plt.errorbar(bincenters, mean, yerr=std, color=[6/255.0,70/255.0,163/255.0], fmt = 'o-',capthick=1, capsize=5) #[44/255.0,53/255.0,127/255.0]
                #plt.errorbar(bincenters, mean, yerr=[mean-per25,per75-mean], fmt='go-',capthick=1, capsize=5)
            ylims=plt.ylim()
            plt.ylim(0,ylims[1])
            plt.xlabel('normalized y location (um)', fontsize=fontsiz)
            #plt.xlabel('avg rate (Hz)', fontsize=fontsiz)
            plt.ylabel(xlabel, fontsize=fontsiz)
            plt.legend(fontsize=fontsiz)

            #from IPython import embed; embed()

        # elif graphType == 'bar':
        #     print range(1, len(statData)+1), statData
        #     plt.bar(range(1, len(statData)+1), statData, tick_label=include[::-1], 
        #       orientation='horizontal', colors=colors)

        try:
            plt.tight_layout()
        except:
            pass

        # save figure data
        if saveData:
            figData = {'include': include, 'statData': statData, 'timeRange': timeRange, 'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}

            _saveFigData(figData, saveData, 'spikeStats_'+stat)

        # save figure
        if saveFig: 
            if isinstance(saveFig, basestring):
                filename = saveFig+'_'+'spikeStat_'+graphType+'_'+stat+'.png'
            else:
                filename = sim.cfg.filename+'_'+'spikeStat_'+graphType+'_'+stat+'.png'
            plt.savefig(filename, dpi=dpi)

        # show fig 
        if showFig: _showFigure()

    return fig, statData, gidsData, ynormsData



######################################################################################################################################################
## Plot spike histogram
######################################################################################################################################################
@exception
def plotRatePSD (include = ['allCells', 'eachPop'], timeRange = None, binSize = 5, maxFreq = 100, NFFT = 256, noverlap = 128, smooth = 0, overlay=True, ylim = None, 
    popColors = {}, figSize = (10,8), saveData = None, saveFig = None, showFig = True): 
    ''' 
    Plot firing rate power spectral density (PSD)
        - include (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): List of data series to include. 
            Note: one line per item, not grouped (default: ['allCells', 'eachPop'])
        - timeRange ([start:stop]): Time range of spikes shown; if None shows all (default: None)
        - binSize (int): Size in ms of spike bins (default: 5)
        - maxFreq (float): Maximum frequency to show in plot (default: 100)
        - NFFT (float): The number of data points used in each block for the FFT (power of 2) (default: 256)
        - smooth (int): Window size for smoothing; no smoothing if 0 (default: 0)
        - overlay (True|False): Whether to overlay the data lines or plot in separate subplots (default: True)
        - graphType ('line'|'bar'): Type of graph to use (line graph or bar plot) (default: 'line')
        - yaxis ('rate'|'count'): Units of y axis (firing rate in Hz, or spike count) (default: 'rate')
        - popColors (dict): Dictionary with color (value) used for each population (key) (default: None)
        - figSize ((width, height)): Size of figure (default: (10,8))
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure;
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure;
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)

        - Returns figure handle
    '''

    import sim

    print('Plotting firing rate power spectral density (PSD) ...')
    
    # Replace 'eachPop' with list of pops
    if 'eachPop' in include: 
        include.remove('eachPop')
        for pop in sim.net.allPops: include.append(pop)

    # time range
    if timeRange is None:
        timeRange = [0,sim.cfg.duration]

    histData = []

    # create fig
    fig,ax1 = plt.subplots(figsize=figSize)
    fontsiz = 12
    
    allPower, allSignal, allFreqs=[], [], []
    # Plot separate line for each entry in include
    for iplot,subset in enumerate(include):
        cells, cellGids, netStimLabels = getCellsInclude([subset])   
        numNetStims = 0

        # Select cells to include
        if len(cellGids) > 0:
            try:
                spkinds,spkts = zip(*[(spkgid,spkt) for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids])
            except:
                spkinds,spkts = [],[]
        else: 
            spkinds,spkts = [],[]


        # Add NetStim spikes
        spkts, spkinds = list(spkts), list(spkinds)
        numNetStims = 0
        if 'stims' in sim.allSimData:
            for netStimLabel in netStimLabels:
                netStimSpks = [spk for cell,stims in sim.allSimData['stims'].iteritems() \
                    for stimLabel,stimSpks in stims.iteritems() for spk in stimSpks if stimLabel == netStimLabel]
                if len(netStimSpks) > 0:
                    lastInd = max(spkinds) if len(spkinds)>0 else 0
                    spktsNew = netStimSpks 
                    spkindsNew = [lastInd+1+i for i in range(len(netStimSpks))]
                    spkts.extend(spktsNew)
                    spkinds.extend(spkindsNew)
                    numNetStims += 1

        histo = np.histogram(spkts, bins = np.arange(timeRange[0], timeRange[1], binSize))
        histoT = histo[1][:-1]+binSize/2
        histoCount = histo[0] 
        histoCount = histoCount * (1000.0 / binSize) / (len(cellGids)+numNetStims) # convert to rates

        histData.append(histoCount)

        color = popColors[subset] if isinstance(subset, (basestring, tuple)) and subset in popColors else colorList[iplot%len(colorList)] 

        if not overlay: 
            plt.subplot(len(include),1,iplot+1)  # if subplot, create new subplot
            title (str(subset), fontsize=fontsiz)
            color = 'blue'
        
        Fs = 1000.0/binSize # ACTUALLY DEPENDS ON BIN WINDOW!!! RATE NOT SPIKE!
        power = mlab.psd(histoCount, Fs=Fs, NFFT=NFFT, detrend=mlab.detrend_none, window=mlab.window_hanning, 
            noverlap=noverlap, pad_to=None, sides='default', scale_by_freq=None)

        if smooth:
            signal = _smooth1d(10*np.log10(power[0]), smooth)
        else:
            signal = 10*np.log10(power[0])
        freqs = power[1]

        allFreqs.append(freqs)
        allPower.append(power)
        allSignal.append(signal)

        plt.plot(freqs[freqs<maxFreq], signal[freqs<maxFreq], linewidth=1.5, color=color)

        plt.xlabel('Frequency (Hz)', fontsize=fontsiz)
        plt.ylabel('Power Spectral Density (dB/Hz)', fontsize=fontsiz) # add yaxis in opposite side
        plt.xlim([0, maxFreq])
        if ylim: plt.ylim(ylim)

    # if len(include) < 5:  # if apply tight_layout with many subplots it inverts the y-axis
    #     try:
    #         plt.tight_layout()
    #     except:
    #         pass

    # Add legend
    if overlay:
        for i,subset in enumerate(include):
            color = popColors[subset] if isinstance(subset, basestring) and subset in popColors else colorList[i%len(colorList)] 
            plt.plot(0,0,color=color,label=str(subset))
        plt.legend(fontsize=fontsiz, loc=1)#, bbox_to_anchor=(1.04, 1), loc=2, borderaxespad=0.)
        maxLabelLen = min(10,max([len(str(l)) for l in include]))
        #plt.subplots_adjust(right=(0.9-0.012*maxLabelLen))


    # save figure data
    if saveData:
        figData = {'histData': histData, 'histT': histoT, 'include': include, 'timeRange': timeRange, 'binSize': binSize,
         'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}
    
        _saveFigData(figData, saveData, 'spikeHist')
 
    # save figure
    if saveFig: 
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'spikePSD.png'
        plt.savefig(filename)

    # show fig 
    if showFig: _showFigure()

    return fig, allSignal, allPower, allFreqs



######################################################################################################################################################
## Plot recorded cell traces (V, i, g, etc.)
######################################################################################################################################################
@exception
def plotTraces (include = None, timeRange = None, overlay = False, oneFigPer = 'cell', rerun = False, colors = None, ylim = None, axis='on',
    figSize = (10,8), saveData = None, saveFig = None, showFig = True): 
    ''' 
    Plot recorded traces
        - include (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): List of cells for which to plot 
            the recorded traces (default: [])
        - timeRange ([start:stop]): Time range of spikes shown; if None shows all (default: None)
        - overlay (True|False): Whether to overlay the data lines or plot in separate subplots (default: False)
        - oneFigPer ('cell'|'trace'): Whether to plot one figure per cell (showing multiple traces) 
            or per trace (showing multiple cells) (default: 'cell')
        - rerun (True|False): rerun simulation so new set of cells gets recorded (default: False)
        - colors (list): List of normalized RGB colors to use for traces
        - ylim (list): Y-axis limits
        - axis ('on'|'off'): Whether to show axis or not; if not, then a scalebar is included (default: 'on')
        - figSize ((width, height)): Size of figure (default: (10,8))
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure; 
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure;
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)

        - Returns figure handles
    '''
    import sim

    print('Plotting recorded cell traces ...')

    if include is None:  # if none, record from whatever was recorded
        if 'plotTraces' in sim.cfg.analysis and 'include' in sim.cfg.analysis['plotTraces']:
            include = sim.cfg.analysis['plotTraces']['include'] + sim.cfg.recordCells
        else:
            include = sim.cfg.recordCells
            
    global colorList
    if isinstance(colors, list): 
        colorList2 = colors
    else:
        colorList2 = colorList

    # rerun simulation so new include cells get recorded from
    if rerun: 
        cellsRecord = [cell.gid for cell in sim.getCellsList(include)]
        for cellRecord in cellsRecord:
            if cellRecord not in sim.cfg.recordCells:
                sim.cfg.recordCells.append(cellRecord)
        sim.setupRecording()
        sim.simulate()

    tracesList = sim.cfg.recordTraces.keys()
    tracesList.sort()
    cells, cellGids, _ = getCellsInclude(include)
    gidPops = {cell['gid']: cell['tags']['pop'] for cell in cells}

    # time range
    if timeRange is None:
        timeRange = [0,sim.cfg.duration]

    recordStep = sim.cfg.recordStep

    figs = {}
    tracesData = []

    # Plot one fig per trace for given cell list
    def plotFigPerTrace(subGids):
        for itrace, trace in enumerate(tracesList):
            figs['_trace_'+str(trace)] = plt.figure(figsize=figSize) # Open a new figure
            fontsiz = 2
            for igid, gid in enumerate(subGids):
                if 'cell_'+str(gid) in sim.allSimData[trace]:
                    data = sim.allSimData[trace]['cell_'+str(gid)][int(timeRange[0]/recordStep):int(timeRange[1]/recordStep)]
                    t = np.arange(timeRange[0], timeRange[1]+recordStep, recordStep)
                    tracesData.append({'t': t, 'cell_'+str(gid)+'_'+trace: data})
                    color = colorList2[igid%len(colorList2)]
                    if not overlay:
                        plt.subplot(len(subGids),1,igid+1)
                        plt.ylabel(trace, fontsize=fontsiz)
                    plt.plot(t[:len(data)], data, linewidth=1.5, color=color, label='Cell %d, Pop %s '%(int(gid), gidPops[gid]))
                    plt.xlabel('Time (ms)', fontsize=fontsiz)
                    plt.xlim(timeRange)
                    if ylim: plt.ylim(ylim)
                    plt.title('Cell %d, Pop %s '%(int(gid), gidPops[gid]))
                    
            if axis == 'off':  # if no axis, add scalebar
                ax = plt.gca()
                sizex =  (timeRange[1]-timeRange[0])/20.0
                # yl = plt.ylim()
                # plt.ylim(yl[0]-0.2*(yl[1]-yl[0]), yl[1])
                add_scalebar(ax, hidex=False, hidey=True, matchx=False, matchy=True, sizex=sizex, sizey=None, 
                    unitsx='ms', unitsy='mV', scalex=1, scaley=1, loc=1, pad=-1, borderpad=0.5, sep=4, prop=None, barcolor="black", barwidth=3)   
                plt.axis(axis) 

            if overlay:
                #maxLabelLen = 10
                #plt.subplots_adjust(right=(0.9-0.012*maxLabelLen)) 
                #plt.legend(fontsize=fontsiz, bbox_to_anchor=(1.04, 1), loc=2, borderaxespad=0.)
                plt.legend()

    # Plot one fig per cell
    if oneFigPer == 'cell':
        for gid in cellGids:
            figs['_gid_'+str(gid)] = plt.figure(figsize=figSize) # Open a new figure
            fontsiz = 12
            for itrace, trace in enumerate(tracesList):
                if 'cell_'+str(gid) in sim.allSimData[trace]:
                    fullTrace = sim.allSimData[trace]['cell_'+str(gid)]
                    if isinstance(fullTrace, dict):
                        data = [fullTrace[key][int(timeRange[0]/recordStep):int(timeRange[1]/recordStep)] for key in fullTrace.keys()]
                        lenData = len(data[0])
                        data = np.transpose(np.array(data))
                    else:
                        data = fullTrace[int(timeRange[0]/recordStep):int(timeRange[1]/recordStep)]
                        lenData = len(data)
                    t = np.arange(timeRange[0], timeRange[1]+recordStep, recordStep)
                    tracesData.append({'t': t, 'cell_'+str(gid)+'_'+trace: data})
                    color = colorList2[itrace%len(colorList2)]
                    if not overlay:
                        plt.subplot(len(tracesList),1,itrace+1)
                        color = 'blue'
                    plt.plot(t[:lenData], data, linewidth=1.5, color=color, label=trace)
                    plt.xlabel('Time (ms)', fontsize=fontsiz)
                    plt.ylabel(trace, fontsize=fontsiz)
                    plt.xlim(timeRange)
                    if ylim: plt.ylim(ylim)
                    if itrace==0: plt.title('Cell %d, Pop %s '%(int(gid), gidPops[gid]))
                    
            if overlay: 
                #maxLabelLen = 10
                #plt.subplots_adjust(right=(0.9-0.012*maxLabelLen))
                plt.legend()#fontsize=fontsiz, bbox_to_anchor=(1.04, 1), loc=2, borderaxespad=0.)

            if axis == 'off':  # if no axis, add scalebar
                ax = plt.gca()
                sizex = timeRange[1]-timeRange[0]/20
                yl = plt.ylim()
                plt.ylim(yl[0]-0.2*(yl[1]-yl[0]), yl[1])  # leave space for scalebar?
                add_scalebar(ax, hidex=False, hidey=True, matchx=False, matchy=True,  sizex=sizex, sizey=None, 
                    unitsx='ms', unitsy='mV', scalex=1, scaley=1, loc=4, pad=10, borderpad=0.5, sep=3, prop=None, barcolor="black", barwidth=2)   
                plt.axis(axis)                 
            
    # Plot one fig per trace
    elif oneFigPer == 'trace':
        plotFigPerTrace(cellGids)

    # Plot one fig per trace for each population
    elif oneFigPer == 'popTrace':
        allPopGids = invertDictMapping(gidPops)
        for popLabel, popGids in allPopGids.iteritems():
            plotFigPerTrace(popGids)


    try:
        plt.tight_layout()
    except:
        pass

    #save figure data
    if saveData:
        figData = {'tracesData': tracesData, 'include': include, 'timeRange': timeRange, 'oneFigPer': oneFigPer,
         'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}
    
        _saveFigData(figData, saveData, 'traces')
 
    # save figure
    if saveFig: 
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'traces.png'
        if len(figs) > 1:
            for figLabel, figObj in figs.iteritems():
                plt.figure(figObj.number)
                plt.savefig(filename[:-4]+figLabel+filename[-4:])
        else:
            plt.savefig(filename)

    # show fig 
    if showFig: _showFigure()

    return figs

def invertDictMapping(d):
    """ Invert mapping of dictionary (i.e. map values to list of keys) """
    inv_map = {}
    for k, v in d.iteritems():
        inv_map[v] = inv_map.get(v, [])
        inv_map[v].append(k)
    return inv_map


######################################################################################################################################################
## Plot cell shape
######################################################################################################################################################
@exception
def plotShape (includePost = ['all'], includePre = ['all'], showSyns = False, showElectrodes = False, synStyle = '.', synSiz=3, dist=0.6, cvar=None, cvals=None, 
    iv=False, ivprops=None, includeAxon=True, bkgColor = None, figSize = (10,8), saveData = None, dpi = 300, saveFig = None, showFig = True): 
    ''' 
    Plot 3D cell shape using NEURON Interview PlotShape
        - includePre: (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): List of presynaptic cells to consider 
        when plotting connections (default: ['all'])
        - includePost: (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): List of cells to show shape of (default: ['all'])
        - showSyns (True|False): Show synaptic connections in 3D view (default: False)
        - showElectrodes (True|False): Show LFP electrodes in 3D view (default: False)
        - synStyle: Style of marker to show synapses (default: '.') 
        - dist: 3D distance (like zoom) (default: 0.6)
        - synSize: Size of marker to show synapses (default: 3)
        - cvar: ('numSyns'|'weightNorm') Variable to represent in shape plot (default: None)
        - cvals: List of values to represent in shape plot; must be same as num segments (default: None)
        - iv: Use NEURON Interviews (instead of matplotlib) to show shape plot (default: None)
        - ivprops: Dict of properties to plot using Interviews (default: None)
        - includeAxon: Include axon in shape plot (default: True)
        - bkgColor (list/tuple with 4 floats): RGBA list/tuple with bakcground color eg. (0.5, 0.2, 0.1, 1.0) (default: None) 
        - figSize ((width, height)): Size of figure (default: (10,8))
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure; 
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure;
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)

        - Returns figure handles
    '''

    import sim
    from neuron import h, gui

    print('Plotting 3D cell shape ...')

    cellsPreGids = [c.gid for c in sim.getCellsList(includePre)] if includePre else []
    cellsPost = sim.getCellsList(includePost)

    if not hasattr(sim.net, 'compartCells'): sim.net.compartCells = [c for c in cellsPost if type(c) is sim.CompartCell]
    sim.net.defineCellShapes()  # in case some cells had stylized morphologies without 3d pts

    if not iv: # plot using Python instead of interviews
        from mpl_toolkits.mplot3d import Axes3D
        from netpyne.support import morphology as morph # code adapted from https://github.com/ahwillia/PyNeuron-Toolbox
        
        # create secList from include
        
        secs = None

        # Set cvals and secs
        if not cvals and cvar:
            cvals = []
            secs = []
            # weighNorm
            if cvar == 'weightNorm':
                for cellPost in cellsPost:
                    cellSecs = cellPost.secs.values() if includeAxon else [s for s in cellPost.secs.values() if 'axon' not in s['hSec'].hname()] 
                    for sec in cellSecs:
                        if 'weightNorm' in sec:
                            secs.append(sec['hSec'])
                            cvals.extend(sec['weightNorm'])

                cvals = np.array(cvals)
                cvals = cvals/min(cvals)

            # numSyns
            elif cvar == 'numSyns':
                for cellPost in cellsPost:
                    cellSecs = cellPost.secs if includeAxon else {k:s for k,s in cellPost.secs.iteritems() if 'axon' not in s['hSec'].hname()}
                    for secLabel,sec in cellSecs.iteritems():
                        nseg=sec['hSec'].nseg
                        nsyns = [0] * nseg
                        secs.append(sec['hSec'])
                        conns = [conn for conn in cellPost.conns if conn['sec']==secLabel and conn['preGid'] in cellsPreGids]
                        for conn in conns: nsyns[int(round(conn['loc']*nseg))-1] += 1
                        cvals.extend(nsyns)

                cvals = np.array(cvals)

        if not secs: secs = [s['hSec'] for cellPost in cellsPost for s in cellPost.secs.values()]
        if not includeAxon:         
            secs = [sec for sec in secs if 'axon' not in sec.hname()]

        # Plot shapeplot
        cbLabels = {'numSyns': 'number of synapses', 'weightNorm': 'weight scaling'}
        fig=plt.figure(figsize=figSize)
        shapeax = plt.subplot(111, projection='3d')
        shapeax.elev=90 # 90 
        shapeax.azim=-90 # -90
        shapeax.dist=dist*shapeax.dist
        plt.axis('equal')
        cmap=plt.cm.jet  #plt.cm.rainbow #plt.cm.jet #YlOrBr_r
        morph.shapeplot(h,shapeax, sections=secs, cvals=cvals, cmap=cmap)
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        if not cvals==None and len(cvals)>0: 
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=np.min(cvals), vmax=np.max(cvals)))
            sm._A = []  # fake up the array of the scalar mappable
            cb = plt.colorbar(sm, fraction=0.15, shrink=0.5, pad=0.01, aspect=20)    
            if cvar: cb.set_label(cbLabels[cvar], rotation=90)

        if bkgColor:
            shapeax.w_xaxis.set_pane_color(bkgColor)
            shapeax.w_yaxis.set_pane_color(bkgColor)
            shapeax.w_zaxis.set_pane_color(bkgColor)
        #shapeax.grid(False)

        # Synapses
        if showSyns:
            synColor='red'
            for cellPost in cellsPost:
                for sec in cellPost.secs.values():
                    for synMech in sec['synMechs']:
                        morph.mark_locations(h, sec['hSec'], synMech['loc'], markspec=synStyle, color=synColor, markersize=synSiz)
        # Electrodes
        if showElectrodes:
            ax = plt.gca()
            colorOffset = 0
            if 'avg' in showElectrodes:
                showElectrodes.remove('avg')
                colorOffset = 1
            coords = sim.net.recXElectrode.pos.T[np.array(showElectrodes).astype(int),:]
            ax.scatter(coords[:,0],coords[:,1],coords[:,2], s=150, c=colorList[colorOffset:len(coords)+colorOffset],
                marker='v', depthshade=False, edgecolors='k', linewidth=2)
            for i in range(coords.shape[0]):
                ax.text(coords[i,0],coords[i,1],coords[i,2], '  '+str(showElectrodes[i]), fontweight='bold' )
            cb.set_label('Segment total transfer resistance to electrodes (kiloohm)', rotation=90, fontsize=12)

        #plt.title(str(includePre)+' -> '+str(includePost) + ' ' + str(cvar))
        shapeax.set_xticklabels([])

        # save figure
        if saveFig: 
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename+'_shape.png'
            plt.savefig(filename, dpi=dpi)

        # show fig 
        if showFig: _showFigure()

    else:  # Plot using Interviews
        # colors: 0 white, 1 black, 2 red, 3 blue, 4 green, 5 orange, 6 brown, 7 violet, 8 yellow, 9 gray
        fig = h.Shape()
        secList = h.SectionList()
        if not ivprops:
            ivprops = {'colorSecs': 1, 'colorSyns':2 ,'style': 'O', 'siz':5}
        
        for cell in [c for c in cellsPost]: 
            for sec in cell.secs.values():
                if 'axon' in sec['hSec'].hname() and not includeAxon: continue
                sec['hSec'].push()
                secList.append()
                h.pop_section()
                if showSyns:
                    for synMech in sec['synMechs']:
                        if synMech['hSyn']:
                            # find pre pop using conn[preGid]
                            # create dict with color for each pre pop; check if exists; increase color counter
                            # colorsPre[prePop] = colorCounter

                            # find synMech using conn['loc'], conn['sec'] and conn['synMech']
                            fig.point_mark(synMech['hSyn'], ivprops['colorSyns'], ivprops['style'], ivprops['siz']) 

        fig.observe(secList)
        fig.color_list(secList, ivprops['colorSecs'])
        fig.flush()
        fig.show(0) # show real diam
            # save figure
        if saveFig: 
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename+'_'+'shape.ps'
            fig.printfile(filename)


    return fig


######################################################################################################################################################
## Plot LFP (time-resolved, power spectral density, time-frequency and 3D locations)
######################################################################################################################################################
#@exception
def plotLFP (electrodes = ['avg', 'all'], plots = ['timeSeries', 'PSD', 'spectrogram', 'locations'], timeRange = None, NFFT = 256, noverlap = 128, 
    nperseg = 256, maxFreq = 100, smooth = 0, separation = 1.0, includeAxon=True, logx=False, logy=False, norm=False, dpi = 200, overlay=False, filtFreq = False, filtOrder=3, detrend=False,
    colors = None, figSize = (8,8), saveData = None, saveFig = None, showFig = True): 
    ''' 
    Plot LFP
        - electrodes (list): List of electrodes to include; 'avg'=avg of all electrodes; 'all'=each electrode separately (default: ['avg', 'all'])
        - plots (list): list of plot types to show (default: ['timeSeries', 'PSD', 'timeFreq', 'locations']) 
        - timeRange ([start:stop]): Time range of spikes shown; if None shows all (default: None)
        - NFFT (int, power of 2): Number of data points used in each block for the PSD and time-freq FFT (default: 256)
        - noverlap (int, <nperseg): Number of points of overlap between segments for PSD and time-freq (default: 128)
        - maxFreq (float): Maximum frequency shown in plot for PSD and time-freq (default: 100 Hz)
        - nperseg (int): Length of each segment for time-freq (default: 256)
        - smooth (int): Window size for smoothing LFP; no smoothing if 0 (default: 0)
        - separation (float): Separation factor between time-resolved LFP plots; multiplied by max LFP value (default: 1.0)
        - includeAxon (boolean): Whether to show the axon in the location plot (default: True)
        - figSize ((width, height)): Size of figure (default: (10,8))
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure; 
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure;
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)

        - Returns figure handles
    
    '''

    import sim
    from support.scalebar import add_scalebar

    print('Plotting LFP ...')

    if not colors: colors = colorList

    # time range
    if timeRange is None:
        timeRange = [0,sim.cfg.duration]

    lfp = np.array(sim.allSimData['LFP'])[int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep),:]

    if filtFreq:
        from scipy import signal
        fs = 1000.0/sim.cfg.recordStep
        nyquist = fs/2.0    
        if isinstance(filtFreq, list): # bandpass
            Wn = [filtFreq[0]/nyquist, filtFreq[1]/nyquist]
            b, a = signal.butter(filtOrder, Wn, btype='bandpass')
        elif isinstance(filtFreq, Number): # lowpass
            Wn = filtFreq/nyquist
            b, a = signal.butter(filtOrder, Wn)
        for i in range(lfp.shape[1]):
            lfp[:,i] = signal.filtfilt(b, a, lfp[:,i])

    if detrend:
        from scipy import signal
        for i in range(lfp.shape[1]):
            lfp[:,i] = signal.detrend(lfp[:,i])

    if norm:
        for i in range(lfp.shape[1]):
            offset = min(lfp[:,i])
            if offset <= 0:
                lfp[:,i] += abs(offset)
            lfp[:,i] /= max(lfp[:,i])

    # electrode selection
    if 'all' in electrodes:
        electrodes.remove('all')
        electrodes.extend(range(int(sim.net.recXElectrode.nsites)))

    # plotting
    figs = []
    fontsiz = 14
    maxPlots = 8.0
    
    data = {'lfp':lfp}  # returned data

    # time series -----------------------------------------
    if 'timeSeries' in plots:
        ydisp = np.absolute(lfp).max() * separation
        offset = 1.0*ydisp
        t = np.arange(timeRange[0], timeRange[1], sim.cfg.recordStep)

        if figSize:
            figs.append(plt.figure(figsize=figSize))

        for i,elec in enumerate(electrodes):
            if elec == 'avg':
                lfpPlot = np.mean(lfp, axis=1)
                color = 'k'
                lw=1.0
            elif isinstance(elec, Number) and elec <= sim.net.recXElectrode.nsites:
                lfpPlot = lfp[:, elec]
                color = colors[i%len(colors)]
                lw=1.0
            plt.plot(t, -lfpPlot+(i*ydisp), color=color, linewidth=lw)
            if len(electrodes) > 1:
                plt.text(timeRange[0]-0.07*(timeRange[1]-timeRange[0]), (i*ydisp), elec, color=color, ha='center', va='top', fontsize=fontsiz, fontweight='bold')

        ax = plt.gca()

        data['lfpPlot'] = lfpPlot
        data['ydisp'] =  ydisp
        data['t'] = t

        # format plot
        if len(electrodes) > 1:
            plt.text(timeRange[0]-0.14*(timeRange[1]-timeRange[0]), (len(electrodes)*ydisp)/2.0, 'LFP electrode', color='k', ha='left', va='bottom', fontsize=fontsiz, rotation=90)
            plt.ylim(-offset, (len(electrodes))*ydisp)
        else:       
            plt.suptitle('LFP Signal', fontsize=fontsiz, fontweight='bold')
        ax.invert_yaxis()
        plt.xlabel('time (ms)', fontsize=fontsiz)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        plt.subplots_adjust(bottom=0.1, top=1.0, right=1.0)

        # calculate scalebar size and add scalebar
        round_to_n = lambda x, n, m: int(np.ceil(round(x, -int(np.floor(np.log10(abs(x)))) + (n - 1)) / m)) * m 
        scaley = 1000.0  # values in mV but want to convert to uV
        m = 10.0
        sizey = 100/scaley
        while sizey > 0.25*ydisp:
            try:
                sizey = round_to_n(0.2*ydisp*scaley, 1, m) / scaley
            except:
                sizey /= 10.0
            m /= 10.0
        labely = '%.3g $\mu$V'%(sizey*scaley)#)[1:]
        if len(electrodes) > 1:
            add_scalebar(ax,hidey=True, matchy=False, hidex=False, matchx=False, sizex=0, sizey=-sizey, labely=labely, unitsy='$\mu$V', scaley=scaley, 
                loc=3, pad=0.5, borderpad=0.5, sep=3, prop=None, barcolor="black", barwidth=2)
        else:
            add_scalebar(ax, hidey=True, matchy=False, hidex=True, matchx=True, sizex=None, sizey=-sizey, labely=labely, unitsy='$\mu$V', scaley=scaley, 
                unitsx='ms', loc=3, pad=0.5, borderpad=0.5, sep=3, prop=None, barcolor="black", barwidth=2)
        # save figure
        if saveFig: 
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename+'_'+'lfp.png'
            plt.savefig(filename, dpi=dpi)

    # PSD ----------------------------------
    if 'PSD' in plots:
        if overlay:
            figs.append(plt.figure(figsize=figSize))
        else:
            numCols = np.round(len(electrodes) / maxPlots) + 1
            figs.append(plt.figure(figsize=(figSize[0]*numCols, figSize[1])))
            #import seaborn as sb

        allFreqs = []
        allSignal = []
        data['allFreqs'] = allFreqs
        data['allSignal'] = allSignal

        for i,elec in enumerate(electrodes):
            if not overlay:
                plt.subplot(np.ceil(len(electrodes)/numCols), numCols,i+1)
            if elec == 'avg':
                lfpPlot = np.mean(lfp, axis=1)
                color = 'k'
                lw=1.5
            elif isinstance(elec, Number) and elec <= sim.net.recXElectrode.nsites:
                lfpPlot = lfp[:, elec]
                color = colors[i%len(colors)]
                lw=1.5
            
            Fs = int(1000.0/sim.cfg.recordStep)
            power = mlab.psd(lfpPlot, Fs=Fs, NFFT=NFFT, detrend=mlab.detrend_none, window=mlab.window_hanning, 
                noverlap=noverlap, pad_to=None, sides='default', scale_by_freq=None)

            if smooth:
                signal = _smooth1d(10*np.log10(power[0]), smooth)
            else:
                signal = 10*np.log10(power[0])
            freqs = power[1]

            allFreqs.append(freqs)
            allSignal.append(signal)

            plt.plot(freqs[freqs<maxFreq], signal[freqs<maxFreq], linewidth=lw, color=color, label='Electrode %s'%(str(elec)))
            plt.xlim([0, maxFreq])
            if len(electrodes) > 1 and not overlay:
                plt.title('Electrode %s'%(str(elec)), fontsize=fontsiz-2)
            plt.ylabel('dB/Hz', fontsize=fontsiz)
            
            # ALTERNATIVE PSD CALCULATION USING WELCH
            # from http://joelyancey.com/lfp-python-practice/
            # from scipy import signal as spsig
            # Fs = int(1000.0/sim.cfg.recordStep)
            # maxFreq=100
            # f, psd = spsig.welch(lfpPlot, Fs, nperseg=100)
            # plt.semilogy(f,psd,'k')
            # sb.despine()
            # plt.xlim((0,maxFreq))
            # plt.yticks(size=fontsiz)
            # plt.xticks(size=fontsiz)
            # plt.ylabel('$uV^{2}/Hz$',size=fontsiz)

        # format plot
        plt.xlabel('Frequency (Hz)', fontsize=fontsiz)
        if overlay:
            plt.legend(fontsize=fontsiz)
        plt.tight_layout()
        plt.suptitle('LFP Power Spectral Density', fontsize=fontsiz, fontweight='bold') # add yaxis in opposite side
        plt.subplots_adjust(bottom=0.08, top=0.92)


        if logx:
            pass
        #from IPython import embed; embed()

        # save figure
        if saveFig: 
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename+'_'+'lfp_psd.png'
            plt.savefig(filename, dpi=dpi)

    # Spectrogram ------------------------------
    if 'spectrogram' in plots:
        import matplotlib.cm as cm
        numCols = np.round(len(electrodes) / maxPlots) + 1
        figs.append(plt.figure(figsize=(figSize[0]*numCols, figSize[1])))
        #t = np.arange(timeRange[0], timeRange[1], sim.cfg.recordStep)
            
        from scipy import signal as spsig
        logx_spec = []
        
        for i,elec in enumerate(electrodes):
            if elec == 'avg':
                lfpPlot = np.mean(lfp, axis=1)
            elif isinstance(elec, Number) and elec <= sim.net.recXElectrode.nsites:
                lfpPlot = lfp[:, elec]
            # creates spectrogram over a range of data 
            # from: http://joelyancey.com/lfp-python-practice/
            fs = int(1000.0/sim.cfg.recordStep)
            f, t_spec, x_spec = spsig.spectrogram(lfpPlot, fs=fs, window='hanning',
            detrend=mlab.detrend_none, nperseg=nperseg, noverlap=noverlap, nfft=NFFT,  mode='psd')
            x_mesh, y_mesh = np.meshgrid(t_spec*1000.0, f[f<maxFreq])
            logx_spec.append(10*np.log10(x_spec[f<maxFreq]))

        vmin = np.array(logx_spec).min()
        vmax = np.array(logx_spec).max()
        for i,elec in enumerate(electrodes):
            plt.subplot(np.ceil(len(electrodes)/numCols), numCols, i+1)
            if elec == 'avg':
                color = 'k'
                lw=1.0
            elif isinstance(elec, Number) and elec <= sim.net.recXElectrode.nsites:
                color = colorList[i%len(colorList)]
                lw=1.0
            plt.pcolormesh(x_mesh, y_mesh, logx_spec[i], cmap=cm.jet, vmin=vmin, vmax=vmax)
            plt.colorbar(label='dB/Hz')
            if logy:
                plt.yscale('log')
                plt.ylabel('Log-frequency (Hz)')
                if isinstance(logy, list):
                    yticks = tuple(logy)
                    plt.yticks(yticks, yticks)
            else:
                plt.ylabel('Frequency (Hz)')
            if len(electrodes) > 1:
                plt.title('Electrode %s'%(str(elec)), fontsize=fontsiz-2)

        plt.xlabel('time (ms)', fontsize=fontsiz)
        plt.tight_layout()
        plt.suptitle('LFP spectrogram', size=fontsiz, fontweight='bold')
        plt.subplots_adjust(bottom=0.08, top=0.90)
        
        # save figure
        if saveFig: 
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename+'_'+'lfp_timefreq.png'
            plt.savefig(filename, dpi=dpi)

    # locations ------------------------------
    if 'locations' in plots:
        cvals = [] # used to store total transfer resistance

        for cell in sim.net.compartCells:
            trSegs = list(np.sum(sim.net.recXElectrode.getTransferResistance(cell.gid)*1e3, axis=0)) # convert from Mohm to kilohm
            if not includeAxon:
                i = 0
                for secName, sec in cell.secs.iteritems():
                    nseg = sec['hSec'].nseg #.geom.nseg
                    if 'axon' in secName:
                        for j in range(i,i+nseg): del trSegs[j] 
                    i+=nseg
            cvals.extend(trSegs)  
            
        includePost = [c.gid for c in sim.net.compartCells]
        fig = sim.analysis.plotShape(includePost=includePost, showElectrodes=electrodes, cvals=cvals, includeAxon=includeAxon, dpi=dpi, saveFig=saveFig, showFig=showFig, figSize=figSize)
        figs.append(fig)


    #save figure data
    if saveData:
        figData = {'LFP': lfp, 'electrodes': electrodes, 'timeRange': timeRange,
         'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}
    
        _saveFigData(figData, saveData, 'lfp')


    # show fig 
    if showFig: _showFigure()

    return figs, data

######################################################################################################################################################
## Support function for plotConn() - calculate conn using data from sim object
######################################################################################################################################################

def __plotConnCalculateFromSim__(includePre, includePost, feature, orderBy, groupBy, groupByIntervalPre, groupByIntervalPost, synOrConn, synMech):

    import sim

    def list_of_dict_unique_by_key(seq, key):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if x[key] not in seen and not seen_add(x[key])]

    # adapt indices/keys based on compact vs long conn format
    if sim.cfg.compactConnFormat: 
        connsFormat = sim.cfg.compactConnFormat

        # set indices of fields to read compact format (no keys)
        missing = []
        preGidIndex = connsFormat.index('preGid') if 'preGid' in connsFormat else missing.append('preGid')
        synMechIndex = connsFormat.index('synMech') if 'synMech' in connsFormat else missing.append('synMech')
        weightIndex = connsFormat.index('weight') if 'weight' in connsFormat else missing.append('weight')
        delayIndex = connsFormat.index('delay') if 'delay' in connsFormat else missing.append('delay')
        preLabelIndex = connsFormat.index('preLabel') if 'preLabel' in connsFormat else -1
        
        if len(missing) > 0:
            print "  Error: cfg.compactConnFormat missing:"
            print missing
            return None, None, None 
    else:  
        # using long conn format (dict)
        preGidIndex = 'preGid' 
        synMechIndex = 'synMech'
        weightIndex = 'weight'
        delayIndex = 'delay'
        preLabelIndex = 'preLabel'

    # Calculate pre and post cells involved
    cellsPre, cellGidsPre, netStimPopsPre = getCellsInclude(includePre)
    if includePre == includePost:
        cellsPost, cellGidsPost, netStimPopsPost = cellsPre, cellGidsPre, netStimPopsPre 
    else:
        cellsPost, cellGidsPost, netStimPopsPost = getCellsInclude(includePost) 

    if isinstance(synMech, basestring): synMech = [synMech]  # make sure synMech is a list
    
    # Calculate matrix if grouped by cell
    if groupBy == 'cell': 
        if feature in ['weight', 'delay', 'numConns']: 
            connMatrix = np.zeros((len(cellGidsPre), len(cellGidsPost)))
            countMatrix = np.zeros((len(cellGidsPre), len(cellGidsPost)))
        else: 
            print 'Conn matrix with groupBy="cell" only supports features= "weight", "delay" or "numConns"'
            return fig
        cellIndsPre = {cell['gid']: ind for ind,cell in enumerate(cellsPre)}
        cellIndsPost = {cell['gid']: ind for ind,cell in enumerate(cellsPost)}

        # Order by
        if len(cellsPre) > 0 and len(cellsPost) > 0:
            if orderBy not in cellsPre[0]['tags'] or orderBy not in cellsPost[0]['tags']:  # if orderBy property doesn't exist or is not numeric, use gid
                orderBy = 'gid'
            elif not isinstance(cellsPre[0]['tags'][orderBy], Number) or not isinstance(cellsPost[0]['tags'][orderBy], Number): 
                orderBy = 'gid' 
        
            if orderBy == 'gid': 
                yorderPre = [cell[orderBy] for cell in cellsPre]
                yorderPost = [cell[orderBy] for cell in cellsPost]
            else:
                yorderPre = [cell['tags'][orderBy] for cell in cellsPre]
                yorderPost = [cell['tags'][orderBy] for cell in cellsPost]

            sortedGidsPre = {gid:i for i,(y,gid) in enumerate(sorted(zip(yorderPre,cellGidsPre)))}
            cellIndsPre = sortedGidsPre
            if includePre == includePost:
                sortedGidsPost = sortedGidsPre
                cellIndsPost = cellIndsPre
            else:
                sortedGidsPost = {gid:i for i,(y,gid) in enumerate(sorted(zip(yorderPost,cellGidsPost)))}
                cellIndsPost = sortedGidsPost


        # Calculate conn matrix
        for cell in cellsPost:  # for each postsyn cell

            if synOrConn=='syn':
                cellConns = cell['conns'] # include all synapses 
            else:
                cellConns = list_of_dict_unique_by_key(cell['conns'], preGidIndex)

            if synMech:
                cellConns = [conn for conn in cellConns if conn[synMechIndex] in synMech]

            for conn in cellConns:
                if conn[preGidIndex] != 'NetStim' and conn[preGidIndex] in cellIndsPre:
                    if feature in ['weight', 'delay']:
                        featureIndex = weightIndex if feature == 'weight' else delayIndex
                        if conn[preGidIndex] in cellIndsPre:
                            connMatrix[cellIndsPre[conn[preGidIndex]], cellIndsPost[cell['gid']]] += conn[featureIndex]
                    countMatrix[cellIndsPre[conn[preGidIndex]], cellIndsPost[cell['gid']]] += 1

        if feature in ['weight', 'delay']: connMatrix = connMatrix / countMatrix 
        elif feature in ['numConns']: connMatrix = countMatrix 

        pre, post = cellsPre, cellsPost 

    # Calculate matrix if grouped by pop
    elif groupBy == 'pop': 
        
        # get list of pops
        popsTempPre = list(set([cell['tags']['pop'] for cell in cellsPre]))
        popsPre = [pop for pop in sim.net.allPops if pop in popsTempPre]+netStimPopsPre
        popIndsPre = {pop: ind for ind,pop in enumerate(popsPre)}

        if includePre == includePost:
            popsPost = popsPre
            popIndsPost = popIndsPre
        else:
            popsTempPost = list(set([cell['tags']['pop'] for cell in cellsPost]))
            popsPost = [pop for pop in sim.net.allPops if pop in popsTempPost]+netStimPopsPost
            popIndsPost = {pop: ind for ind,pop in enumerate(popsPost)}
        
        # initialize matrices
        if feature in ['weight', 'strength']: 
            weightMatrix = np.zeros((len(popsPre), len(popsPost)))
        elif feature == 'delay': 
            delayMatrix = np.zeros((len(popsPre), len(popsPost)))
        countMatrix = np.zeros((len(popsPre), len(popsPost)))
        
        # calculate max num conns per pre and post pair of pops
        numCellsPopPre = {}
        for pop in popsPre:
            if pop in netStimPopsPre:
                numCellsPopPre[pop] = -1
            else:
                numCellsPopPre[pop] = len([cell for cell in cellsPre if cell['tags']['pop']==pop])

        if includePre == includePost:
            numCellsPopPost = numCellsPopPre
        else:
            numCellsPopPost = {}
            for pop in popsPost:
                if pop in netStimPopsPost:
                    numCellsPopPost[pop] = -1
                else:
                    numCellsPopPost[pop] = len([cell for cell in cellsPost if cell['tags']['pop']==pop])

        maxConnMatrix = np.zeros((len(popsPre), len(popsPost)))
        if feature == 'convergence': maxPostConnMatrix = np.zeros((len(popsPre), len(popsPost)))
        if feature == 'divergence': maxPreConnMatrix = np.zeros((len(popsPre), len(popsPost)))
        for prePop in popsPre:
            for postPop in popsPost: 
                if numCellsPopPre[prePop] == -1: numCellsPopPre[prePop] = numCellsPopPost[postPop]
                maxConnMatrix[popIndsPre[prePop], popIndsPost[postPop]] = numCellsPopPre[prePop]*numCellsPopPost[postPop]
                if feature == 'convergence': maxPostConnMatrix[popIndsPre[prePop], popIndsPost[postPop]] = numCellsPopPost[postPop]
                if feature == 'divergence': maxPreConnMatrix[popIndsPre[prePop], popIndsPost[postPop]] = numCellsPopPre[prePop]
        
        # Calculate conn matrix
        for cell in cellsPost:  # for each postsyn cell

            if synOrConn=='syn':
                cellConns = cell['conns'] # include all synapses 
            else:
                cellConns = list_of_dict_unique_by_key(cell['conns'], preGidIndex)

            if synMech:
                cellConns = [conn for conn in cellConns if conn[synMechIndex] in synMech]

            for conn in cellConns:
                if conn[preGidIndex] == 'NetStim':
                    prePopLabel = conn[preLabelIndex] if preLabelIndex in conn else 'NetStim'
                else:
                    preCell = next((cell for cell in cellsPre if cell['gid']==conn[preGidIndex]), None)
                    prePopLabel = preCell['tags']['pop'] if preCell else None
                
                if prePopLabel in popIndsPre:
                    if feature in ['weight', 'strength']: 
                        weightMatrix[popIndsPre[prePopLabel], popIndsPost[cell['tags']['pop']]] += conn[weightIndex]
                    elif feature == 'delay': 
                        delayMatrix[popIndsPre[prePopLabel], popIndsPost[cell['tags']['pop']]] += conn[delayIndex] 
                    countMatrix[popIndsPre[prePopLabel], popIndsPost[cell['tags']['pop']]] += 1    

        pre, post = popsPre, popsPost 
    
    # Calculate matrix if grouped by numeric tag (eg. 'y')
    elif groupBy in sim.net.allCells[0]['tags'] and isinstance(sim.net.allCells[0]['tags'][groupBy], Number):
        if not isinstance(groupByIntervalPre, Number) or not isinstance(groupByIntervalPost, Number):
            print 'groupByIntervalPre or groupByIntervalPost not specified'
            return

        # group cells by 'groupBy' feature (eg. 'y') in intervals of 'groupByInterval')
        cellValuesPre = [cell['tags'][groupBy] for cell in cellsPre]
        minValuePre = _roundFigures(groupByIntervalPre * np.floor(min(cellValuesPre) / groupByIntervalPre), 3)
        maxValuePre  = _roundFigures(groupByIntervalPre * np.ceil(max(cellValuesPre) / groupByIntervalPre), 3)        
        groupsPre = np.arange(minValuePre, maxValuePre, groupByIntervalPre)
        groupsPre = [_roundFigures(x,3) for x in groupsPre]

        if includePre == includePost:
            groupsPost = groupsPre       
        else:
            cellValuesPost = [cell['tags'][groupBy] for cell in cellsPost]
            minValuePost = _roundFigures(groupByIntervalPost * np.floor(min(cellValuesPost) / groupByIntervalPost), 3)
            maxValuePost  = _roundFigures(groupByIntervalPost * np.ceil(max(cellValuesPost) / groupByIntervalPost), 3)        
            groupsPost = np.arange(minValuePost, maxValuePost, groupByIntervalPost)
            groupsPost = [_roundFigures(x,3) for x in groupsPost]


        # only allow matrix sizes >= 2x2 [why?]
        # if len(groupsPre) < 2 or len(groupsPost) < 2: 
        #     print 'groupBy %s with groupByIntervalPre %s and groupByIntervalPost %s results in <2 groups'%(str(groupBy), str(groupByIntervalPre), str(groupByIntervalPre))
        #     return

        # set indices for pre and post groups
        groupIndsPre = {group: ind for ind,group in enumerate(groupsPre)}
        groupIndsPost = {group: ind for ind,group in enumerate(groupsPost)}
        
        # initialize matrices
        if feature in ['weight', 'strength']: 
            weightMatrix = np.zeros((len(groupsPre), len(groupsPost)))
        elif feature == 'delay': 
            delayMatrix = np.zeros((len(groupsPre), len(groupsPost)))
        countMatrix = np.zeros((len(groupsPre), len(groupsPost)))

        # calculate max num conns per pre and post pair of pops
        numCellsGroupPre = {}
        for groupPre in groupsPre:
            numCellsGroupPre[groupPre] = len([cell for cell in cellsPre if groupPre <= cell['tags'][groupBy] < (groupPre+groupByIntervalPre)])
        
        if includePre == includePost:
            numCellsGroupPost = numCellsGroupPre  
        else:
            numCellsGroupPost = {}
            for groupPost in groupsPost:
                numCellsGroupPost[groupPost] = len([cell for cell in cellsPost if groupPost <= cell['tags'][groupBy] < (groupPost+groupByIntervalPost)])


        maxConnMatrix = np.zeros((len(groupsPre), len(groupsPost)))
        if feature == 'convergence': maxPostConnMatrix = np.zeros((len(groupsPre), len(groupsPost)))
        if feature == 'divergence': maxPreConnMatrix = np.zeros((len(groupsPre), len(groupsPost)))
        for preGroup in groupsPre:
            for postGroup in groupsPost: 
                if numCellsGroupPre[preGroup] == -1: numCellsGroupPre[preGroup] = numCellsGroupPost[postGroup]
                maxConnMatrix[groupIndsPre[preGroup], groupIndsPost[postGroup]] = numCellsGroupPre[preGroup]*numCellsGroupPost[postGroup]
                if feature == 'convergence': maxPostConnMatrix[groupIndsPre[preGroup], groupIndsPost[postGroup]] = numCellsGroupPost[postGroup]
                if feature == 'divergence': maxPreConnMatrix[groupIndsPre[preGroup], groupIndsPost[postGroup]] = numCellsGroupPre[preGroup]
        
        # Calculate conn matrix
        for cell in cellsPost:  # for each postsyn cell
            if synOrConn=='syn':
                cellConns = cell['conns'] # include all synapses 
            else:
                cellConns = list_of_dict_unique_by_key(cell['conns'], preGidIndex)

            if synMech:
                cellConns = [conn for conn in cellConns if conn[synMechIndex] in synMech]

            for conn in cellConns:
                if conn[preGidIndex] == 'NetStim':
                    prePopLabel = -1  # maybe add in future
                else:
                    preCell = next((c for c in cellsPre if c['gid']==conn[preGidIndex]), None)
                    if preCell:
                        preGroup = _roundFigures(groupByIntervalPre * np.floor(preCell['tags'][groupBy] / groupByIntervalPre), 3)
                    else:
                        preGroup = None

                postGroup = _roundFigures(groupByIntervalPost * np.floor(cell['tags'][groupBy] / groupByIntervalPost), 3)
                if preGroup in groupIndsPre:
                    if feature in ['weight', 'strength']: 
                        weightMatrix[groupIndsPre[preGroup], groupIndsPost[postGroup]] += conn[weightIndex]
                    elif feature == 'delay': 
                        delayMatrix[groupIndsPre[preGroup], groupIndsPost[postGroup]] += conn[delayIndex] 
                    countMatrix[groupIndsPre[preGroup], groupIndsPost[postGroup]] += 1  

  
        pre, post = groupsPre, groupsPost 

    # no valid groupBy
    else:  
        print 'groupBy (%s) is not valid'%(str(groupBy))
        return

    # normalize by number of postsyn cells
    if groupBy != 'cell':
        if feature == 'weight': 
            connMatrix = weightMatrix / countMatrix  # avg weight per conn (fix to remove divide by zero warning) 
        elif feature == 'delay': 
            connMatrix = delayMatrix / countMatrix
        elif feature == 'numConns':
            connMatrix = countMatrix
        elif feature in ['probability', 'strength']:
            connMatrix = countMatrix / maxConnMatrix  # probability
            if feature == 'strength':
                connMatrix = connMatrix * weightMatrix  # strength
        elif feature == 'convergence':
            connMatrix = countMatrix / maxPostConnMatrix
        elif feature == 'divergence':
            connMatrix = countMatrix / maxPreConnMatrix



    return connMatrix, pre, post


######################################################################################################################################################
## Support function for plotConn() - calculate conn using data from files with short format (no keys)
######################################################################################################################################################

def __plotConnCalculateFromFile__(includePre, includePost, feature, orderBy, groupBy, groupByIntervalPre, groupByIntervalPost, synOrConn, synMech, connsFile, tagsFile):
    
    import sim
    import json
    from time import time    

    def list_of_dict_unique_by_key(seq, index):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if x[index] not in seen and not seen_add(x[index])]

    # load files with tags and conns
    start = time()
    tags, conns = None, None
    if tagsFile:
        print 'Loading tags file...'
        with open(tagsFile, 'r') as fileObj: tagsTmp = json.load(fileObj)['tags']
        tagsFormat = tagsTmp.pop('format', [])
        tags = {int(k): v for k,v in tagsTmp.iteritems()} # find method to load json with int keys?
        del tagsTmp
    if connsFile:
        print 'Loading conns file...'
        with open(connsFile, 'r') as fileObj: connsTmp = json.load(fileObj)['conns']
        connsFormat = connsTmp.pop('format', [])
        conns = {int(k): v for k,v in connsTmp.iteritems()}
        del connsTmp

    print 'Finished loading; total time (s): %.2f'%(time()-start)
         
    # find pre and post cells
    if tags and conns:
        cellGidsPre = getCellsIncludeTags(includePre, tags, tagsFormat)
        if includePre == includePost:
            cellGidsPost = cellGidsPre
        else:
            cellGidsPost = getCellsIncludeTags(includePost, tags, tagsFormat)
    else:
        print 'Error loading tags and conns from file' 
        return None, None, None


    # set indices of fields to read compact format (no keys)
    missing = []
    popIndex = tagsFormat.index('pop') if 'pop' in tagsFormat else missing.append('pop')
    preGidIndex = connsFormat.index('preGid') if 'preGid' in connsFormat else missing.append('preGid')
    synMechIndex = connsFormat.index('synMech') if 'synMech' in connsFormat else missing.append('synMech')
    weightIndex = connsFormat.index('weight') if 'weight' in connsFormat else missing.append('weight')
    delayIndex = connsFormat.index('delay') if 'delay' in connsFormat else missing.append('delay')
    preLabelIndex = connsFormat.index('preLabel') if 'preLabel' in connsFormat else -1
    
    if len(missing) > 0:
        print "Missing:"
        print missing
        return None, None, None 

    if isinstance(synMech, basestring): synMech = [synMech]  # make sure synMech is a list
    
    # Calculate matrix if grouped by cell
    if groupBy == 'cell': 
        print 'plotConn from file for groupBy=cell not implemented yet'
        return None, None, None 

    # Calculate matrix if grouped by pop
    elif groupBy == 'pop': 
        
        # get list of pops
        print '    Obtaining list of populations ...'
        popsPre = list(set([tags[gid][popIndex] for gid in cellGidsPre]))
        popIndsPre = {pop: ind for ind,pop in enumerate(popsPre)}
        netStimPopsPre = []  # netstims not yet supported
        netStimPopsPost = []

        if includePre == includePost:
            popsPost = popsPre
            popIndsPost = popIndsPre
        else:
            popsPost = list(set([tags[gid][popIndex] for gid in cellGidsPost]))
            popIndsPost = {pop: ind for ind,pop in enumerate(popsPost)}
        
        # initialize matrices
        if feature in ['weight', 'strength']: 
            weightMatrix = np.zeros((len(popsPre), len(popsPost)))
        elif feature == 'delay': 
            delayMatrix = np.zeros((len(popsPre), len(popsPost)))
        countMatrix = np.zeros((len(popsPre), len(popsPost)))
        
        # calculate max num conns per pre and post pair of pops
        print '    Calculating max num conns for each pair of population ...'
        numCellsPopPre = {}
        for pop in popsPre:
            if pop in netStimPopsPre:
                numCellsPopPre[pop] = -1
            else:
                numCellsPopPre[pop] = len([gid for gid in cellGidsPre if tags[gid][popIndex]==pop])

        if includePre == includePost:
            numCellsPopPost = numCellsPopPre
        else:
            numCellsPopPost = {}
            for pop in popsPost:
                if pop in netStimPopsPost:
                    numCellsPopPost[pop] = -1
                else:
                    numCellsPopPost[pop] = len([gid for gid in cellGidsPost if tags[gid][popIndex]==pop])

        maxConnMatrix = np.zeros((len(popsPre), len(popsPost)))
        if feature == 'convergence': maxPostConnMatrix = np.zeros((len(popsPre), len(popsPost)))
        if feature == 'divergence': maxPreConnMatrix = np.zeros((len(popsPre), len(popsPost)))
        for prePop in popsPre:
            for postPop in popsPost: 
                if numCellsPopPre[prePop] == -1: numCellsPopPre[prePop] = numCellsPopPost[postPop]
                maxConnMatrix[popIndsPre[prePop], popIndsPost[postPop]] = numCellsPopPre[prePop]*numCellsPopPost[postPop]
                if feature == 'convergence': maxPostConnMatrix[popIndsPre[prePop], popIndsPost[postPop]] = numCellsPopPost[postPop]
                if feature == 'divergence': maxPreConnMatrix[popIndsPre[prePop], popIndsPost[postPop]] = numCellsPopPre[prePop]
        
        # Calculate conn matrix
        print '    Calculating weights, strength, prob, delay etc matrices ...'
        for postGid in cellGidsPost:  # for each postsyn cell
            print '     cell %d'%(int(postGid))
            if synOrConn=='syn':
                cellConns = conns[postGid] # include all synapses 
            else:
                cellConns = list_of_dict_unique_by_index(conns[postGid], preGidIndex)

            if synMech:
                cellConns = [conn for conn in cellConns if conn[synMechIndex] in synMech]

            for conn in cellConns:
                if conn[preGidIndex] == 'NetStim':
                    prePopLabel = conn[preLabelIndex] if preLabelIndex >=0 else 'NetStims'
                else:
                    preCellGid = next((gid for gid in cellGidsPre if gid==conn[preGidIndex]), None)
                    prePopLabel = tags[preCellGid][popIndex] if preCellGid else None
                
                if prePopLabel in popIndsPre:
                    if feature in ['weight', 'strength']: 
                        weightMatrix[popIndsPre[prePopLabel], popIndsPost[tags[postGid][popIndex]]] += conn[weightIndex]
                    elif feature == 'delay': 
                        delayMatrix[popIndsPre[prePopLabel], popIndsPost[tags[postGid][popIndex]]] += conn[delayIndex] 
                    countMatrix[popIndsPre[prePopLabel], popIndsPost[tags[postGid][popIndex]]] += 1    

        pre, post = popsPre, popsPost 
    
    # Calculate matrix if grouped by numeric tag (eg. 'y')
    elif groupBy in sim.net.allCells[0]['tags'] and isinstance(sim.net.allCells[0]['tags'][groupBy], Number):
        print 'plotConn from file for groupBy=[arbitrary property] not implemented yet'
        return None, None, None 

    # no valid groupBy
    else:  
        print 'groupBy (%s) is not valid'%(str(groupBy))
        return

    if groupBy != 'cell':
        if feature == 'weight': 
            connMatrix = weightMatrix / countMatrix  # avg weight per conn (fix to remove divide by zero warning) 
        elif feature == 'delay': 
            connMatrix = delayMatrix / countMatrix
        elif feature == 'numConns':
            connMatrix = countMatrix
        elif feature in ['probability', 'strength']:
            connMatrix = countMatrix / maxConnMatrix  # probability
            if feature == 'strength':
                connMatrix = connMatrix * weightMatrix  # strength
        elif feature == 'convergence':
            connMatrix = countMatrix / maxPostConnMatrix
        elif feature == 'divergence':
            connMatrix = countMatrix / maxPreConnMatrix

    print '    plotting ...'
    return connMatrix, pre, post


######################################################################################################################################################
## Plot connectivity
######################################################################################################################################################
@exception
def plotConn (includePre = ['all'], includePost = ['all'], feature = 'strength', orderBy = 'gid', figSize = (10,10), groupBy = 'pop', groupByIntervalPre = None, groupByIntervalPost = None,
            graphType = 'matrix', synOrConn = 'syn', synMech = None, connsFile = None, tagsFile = None, clim = None, saveData = None, saveFig = None, showFig = True): 
    ''' 
    Plot network connectivity
        - includePre (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Cells to show (default: ['all'])
        - includePost (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Cells to show (default: ['all'])
        - feature ('weight'|'delay'|'numConns'|'probability'|'strength'|'convergence'|'divergence'): Feature to show in connectivity matrix; 
            the only features applicable to groupBy='cell' are 'weight', 'delay' and 'numConns';  'strength' = weight * probability (default: 'strength')
        - groupBy ('pop'|'cell'|'y'|: Show matrix for individual cells, populations, or by other numeric tag such as 'y' (default: 'pop')
        - groupByInterval (int or float): Interval of groupBy feature to group cells by in conn matrix, e.g. 100 to group by cortical depth in steps of 100 um   (default: None)
        - orderBy ('gid'|'y'|'ynorm'|...): Unique numeric cell property to order x and y axes by, e.g. 'gid', 'ynorm', 'y' (requires groupBy='cells') (default: 'gid')
        - graphType ('matrix','bar','pie'): Type of graph to represent data (default: 'matrix')
        - synOrConn ('syn'|'conn'): Use synapses or connections; note 1 connection can have multiple synapses (default: 'syn')
        - figSize ((width, height)): Size of figure (default: (10,10))
        - synMech (['AMPA', 'GABAA',...]): Show results only for these syn mechs (default: None)
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure; 
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure; 
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)

        - Returns figure handles
    '''
    
    import sim

    print('Plotting connectivity matrix...')

    if connsFile and tagsFile:
        connMatrix, pre, post = __plotConnCalculateFromFile__(includePre, includePost, feature, orderBy, groupBy, groupByIntervalPre, groupByIntervalPost, synOrConn, synMech, connsFile, tagsFile)
    else:
        connMatrix, pre, post = __plotConnCalculateFromSim__(includePre, includePost, feature, orderBy, groupBy, groupByIntervalPre, groupByIntervalPost, synOrConn, synMech)


    if connMatrix is None:
        print "Error calculating connMatrix in plotConn()"
        return None

    # matrix plot
    if graphType == 'matrix':
        # Create plot
        fig = plt.figure(figsize=figSize)
        fig.subplots_adjust(right=0.98) # Less space on right
        fig.subplots_adjust(top=0.96) # Less space on top
        fig.subplots_adjust(bottom=0.02) # Less space on bottom
        h = plt.axes()

        plt.imshow(connMatrix, interpolation='nearest', cmap='jet', vmin=np.nanmin(connMatrix), vmax=np.nanmax(connMatrix))  #_bicolormap(gap=0)

        # Plot grid lines
        plt.hold(True)
        if groupBy == 'cell':
            cellsPre, cellsPost = pre, post

            # Make pretty
            stepy = max(1, int(len(cellsPre)/10.0))
            basey = 100 if stepy>100 else 10
            stepy = max(1, int(basey * np.floor(float(stepy)/basey)))
            stepx = max(1, int(len(cellsPost)/10.0))
            basex = 100 if stepx>100 else 10
            stepx = max(1, int(basex * np.floor(float(stepx)/basex)))

            h.set_xticks(np.arange(0,len(cellsPost),stepx))
            h.set_yticks(np.arange(0,len(cellsPre),stepy))
            h.set_xticklabels(np.arange(0,len(cellsPost),stepx))
            h.set_yticklabels(np.arange(0,len(cellsPost),stepy))
            h.xaxis.set_ticks_position('top')
            plt.xlim(-0.5,len(cellsPost)-0.5)
            plt.ylim(len(cellsPre)-0.5,-0.5)

        elif groupBy == 'pop':
            popsPre, popsPost = pre, post

            for ipop, pop in enumerate(popsPre):
                plt.plot(np.array([0,len(popsPre)])-0.5,np.array([ipop,ipop])-0.5,'-',c=(0.7,0.7,0.7))
            for ipop, pop in enumerate(popsPost):
                plt.plot(np.array([ipop,ipop])-0.5,np.array([0,len(popsPost)])-0.5,'-',c=(0.7,0.7,0.7))

            # Make pretty
            h.set_xticks(range(len(popsPost)))
            h.set_yticks(range(len(popsPre)))
            h.set_xticklabels(popsPost)
            h.set_yticklabels(popsPre)
            h.xaxis.set_ticks_position('top')
            plt.xlim(-0.5,len(popsPost)-0.5)
            plt.ylim(len(popsPre)-0.5,-0.5)

        else:
            groupsPre, groupsPost = pre, post

            for igroup, group in enumerate(groupsPre):
                plt.plot(np.array([0,len(groupsPre)])-0.5,np.array([igroup,igroup])-0.5,'-',c=(0.7,0.7,0.7))
            for igroup, group in enumerate(groupsPost):
                plt.plot(np.array([igroup,igroup])-0.5,np.array([0,len(groupsPost)])-0.5,'-',c=(0.7,0.7,0.7))

            # Make pretty
            h.set_xticks([i-0.5 for i in range(len(groupsPost))])
            h.set_yticks([i-0.5 for i in range(len(groupsPre))])
            h.set_xticklabels([int(x) if x>1 else x for x in groupsPost])
            h.set_yticklabels([int(x) if x>1 else x for x in groupsPre])
            h.xaxis.set_ticks_position('top')
            plt.xlim(-0.5,len(groupsPost)-0.5)
            plt.ylim(len(groupsPre)-0.5,-0.5)

        if not clim: clim = [np.nanmin(connMatrix), np.nanmax(connMatrix)]
        plt.clim(clim[0], clim[1])
        plt.colorbar(label=feature, shrink=0.8) #.set_label(label='Fitness',size=20,weight='bold')
        plt.xlabel('post')
        h.xaxis.set_label_coords(0.5, 1.06)
        plt.ylabel('pre')
        plt.title ('Connection '+feature+' matrix', y=1.08)

    # stacked bar graph
    elif graphType == 'bar':
        if groupBy == 'pop':
            popsPre, popsPost = pre, post

            from netpyne.support import stackedBarGraph 
            SBG = stackedBarGraph.StackedBarGrapher()
    
            fig = plt.figure(figsize=figSize)
            ax = fig.add_subplot(111)
            SBG.stackedBarPlot(ax, connMatrix.transpose(), colorList, xLabels=popsPost, gap = 0.1, scale=False, xlabel='postsynaptic', ylabel = feature)
            plt.title ('Connection '+feature+' stacked bar graph')
            plt.legend(popsPre)
            plt.tight_layout()

        elif groupBy == 'cell':
            print 'Error: plotConn graphType="bar" with groupBy="cell" not implemented'

    elif graphType == 'pie':
        print 'Error: plotConn graphType="pie" not yet implemented'


    #save figure data
    if saveData:
        figData = {'connMatrix': connMatrix, 'feature': feature, 'groupBy': groupBy,
         'includePre': includePre, 'includePost': includePost, 'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}
    
        _saveFigData(figData, saveData, 'conn')
 
    # save figure
    if saveFig: 
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'conn_'+feature+'.png'
        plt.savefig(filename)

    # show fig 
    if showFig: _showFigure()

    return fig


######################################################################################################################################################
## Plot 2D representation of network cell positions and connections
######################################################################################################################################################
@exception
def plot2Dnet (include = ['allCells'], figSize = (12,12), view = 'xy', showConns = True, popColors = None, 
                tagsFile = None, saveData = None, saveFig = None, showFig = True): 
    ''' 
    Plot 2D representation of network cell positions and connections
        - include (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Cells to show (default: ['all'])
        - showConns (True|False): Whether to show connections or not (default: True)
        - figSize ((width, height)): Size of figure (default: (12,12))
        - view ('xy', 'xz'): Perspective view: front ('xy') or top-down ('xz')
        - popColors (dict): Dictionary with color (value) used for each population (key) (default: None)
        - saveData (None|'fileName'): File name where to save the final data used to generate the figure (default: None)
        - saveFig (None|'fileName'): File name where to save the figure;
            if set to True uses filename from simConfig (default: None)(default: None)
        - showFig (True|False): Whether to show the figure or not;
            if set to True uses filename from simConfig (default: None)

        - Returns figure handles
    '''
    import sim

    print('Plotting 2D representation of network cell locations and connections...')

    fig = plt.figure(figsize=figSize)

    # front view
    if view == 'xy':
        ycoord = 'y'
    elif view == 'xz':
        ycoord = 'z'

    if tagsFile:
        print 'Loading tags file...'
        import json
        with open(tagsFile, 'r') as fileObj: tagsTmp = json.load(fileObj)['tags']
        tagsFormat = tagsTmp.pop('format', [])
        tags = {int(k): v for k,v in tagsTmp.iteritems()} # find method to load json with int keys?
        del tagsTmp

        # set indices of fields to read compact format (no keys)
        missing = []
        popIndex = tagsFormat.index('pop') if 'pop' in tagsFormat else missing.append('pop')
        xIndex = tagsFormat.index('x') if 'x' in tagsFormat else missing.append('x')
        yIndex = tagsFormat.index('y') if 'y' in tagsFormat else missing.append('y')
        zIndex = tagsFormat.index('z') if 'z' in tagsFormat else missing.append('z')
        if len(missing) > 0:
            print "Missing:"
            print missing
            return None, None, None 

        # find pre and post cells
        if tags:
            cellGids = getCellsIncludeTags(include, tags, tagsFormat)
            popLabels = list(set([tags[gid][popIndex] for gid in cellGids]))
            
            # pop and cell colors
            popColorsTmp = {popLabel: colorList[ipop%len(colorList)] for ipop,popLabel in enumerate(popLabels)} # dict with color for each pop
            if popColors: popColorsTmp.update(popColors)
            popColors = popColorsTmp
            cellColors = [popColors[tags[gid][popIndex]] for gid in cellGids]
            
            # cell locations
            posX = [tags[gid][xIndex] for gid in cellGids]  # get all x positions
            if ycoord == 'y':
                posY = [tags[gid][yIndex] for gid in cellGids]  # get all y positions
            elif ycoord == 'z':
                posY = [tags[gid][zIndex] for gid in cellGids]  # get all y positions
        else:
            print 'Error loading tags from file' 
            return None

    else:
        cells, cellGids, _ = getCellsInclude(include)           
        selectedPops = [cell['tags']['pop'] for cell in cells]
        popLabels = [pop for pop in sim.net.allPops if pop in selectedPops] # preserves original ordering
        
        # pop and cell colors
        popColorsTmp = {popLabel: colorList[ipop%len(colorList)] for ipop,popLabel in enumerate(popLabels)} # dict with color for each pop
        if popColors: popColorsTmp.update(popColors)
        popColors = popColorsTmp
        cellColors = [popColors[cell['tags']['pop']] for cell in cells]

        # cell locations
        posX = [cell['tags']['x'] for cell in cells]  # get all x positions
        posY = [cell['tags'][ycoord] for cell in cells]  # get all y positions
    

    plt.scatter(posX, posY, s=60, color = cellColors) # plot cell soma positions
    if showConns and not tagsFile:
        for postCell in cells:
            for con in postCell['conns']:  # plot connections between cells
                if not isinstance(con['preGid'], basestring) and con['preGid'] in cellGids:
                    posXpre,posYpre = next(((cell['tags']['x'],cell['tags'][ycoord]) for cell in cells if cell['gid']==con['preGid']), None)  
                    posXpost,posYpost = postCell['tags']['x'], postCell['tags'][ycoord] 
                    color='red'
                    if con['synMech'] in ['inh', 'GABA', 'GABAA', 'GABAB']:
                        color = 'blue'
                    width = 0.1 #50*con['weight']
                    plt.plot([posXpre, posXpost], [posYpre, posYpost], color=color, linewidth=width) # plot line from pre to post
    
    plt.xlabel('x (um)')
    plt.ylabel(ycoord+' (um)') 
    plt.xlim([min(posX)-0.05*max(posX),1.05*max(posX)]) 
    plt.ylim([min(posY)-0.05*max(posY),1.05*max(posY)])
    fontsiz = 12

    for popLabel in popLabels:
        plt.plot(0,0,color=popColors[popLabel],label=popLabel)
    plt.legend(fontsize=fontsiz, bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
    ax = plt.gca()
    ax.invert_yaxis()

    # save figure data
    if saveData:
        figData = {'posX': posX, 'posY': posY, 'posX': cellColors, 'posXpre': posXpre, 'posXpost': posXpost, 'posYpre': posYpre, 'posYpost': posYpost,
         'include': include, 'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}
    
        _saveFigData(figData, saveData, '2Dnet')
 
    # save figure
    if saveFig: 
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'2Dnet.png'
        plt.savefig(filename)

    # show fig 
    if showFig: _showFigure()

    return fig

######################################################################################################################################################
## Calculate number of disynaptic connections
###################################################################################################################################################### 
@exception
def calculateDisynaptic(includePost = ['allCells'], includePre = ['allCells'], includePrePre = ['allCells'], 
        tags=None, conns=None, tagsFile=None, connsFile=None):

    import json
    from time import time
    import sim

    numDis = 0
    totCon = 0

    start = time()
    if tagsFile:
        print 'Loading tags file...'
        with open(tagsFile, 'r') as fileObj: tagsTmp = json.load(fileObj)['tags']
        tags = {int(k): v for k,v in tagsTmp.iteritems()}
        del tagsTmp
    if connsFile:
        print 'Loading conns file...'
        with open(connsFile, 'r') as fileObj: connsTmp = json.load(fileObj)['conns']
        conns = {int(k): v for k,v in connsTmp.iteritems()}
        del connsTmp
         
    print '  Calculating disynaptic connections...'
    # loading from json files    
    if tags and conns:
        cellsPreGids = getCellsIncludeTags(includePre, tags)
        cellsPrePreGids = getCellsIncludeTags(includePrePre, tags)
        cellsPostGids = getCellsIncludeTags(includePost, tags)

        preGidIndex = conns['format'].index('preGid') if 'format' in conns else 0
        for postGid in cellsPostGids:
            preGidsAll = [conn[preGidIndex] for conn in conns[postGid] if isinstance(conn[preGidIndex], Number) and conn[preGidIndex] in cellsPreGids+cellsPrePreGids]
            preGids = [gid for gid in preGidsAll if gid in cellsPreGids]
            for preGid in preGids:
                prePreGids = [conn[preGidIndex] for conn in conns[preGid] if conn[preGidIndex] in cellsPrePreGids]
                totCon += 1
                if not set(prePreGids).isdisjoint(preGidsAll):
                    numDis += 1

    else:
        if sim.cfg.compactConnFormat: 
            if 'preGid' in sim.cfg.compactConnFormat:
                preGidIndex = sim.cfg.compactConnFormat.index('preGid')  # using compact conn format (list)
            else:
                print '   Error: cfg.compactConnFormat does not include "preGid"'
                return -1
        else:  
            preGidIndex = 'preGid' # using long conn format (dict)

        _, cellsPreGids, _ =  getCellsInclude(includePre)
        _, cellsPrePreGids, _ = getCellsInclude(includePrePre)
        cellsPost, _, _ = getCellsInclude(includePost)

        for postCell in cellsPost:
            print postCell['gid']
            preGidsAll = [conn[preGidIndex] for conn in postCell['conns'] if isinstance(conn[preGidIndex], Number) and conn[preGidIndex] in cellsPreGids+cellsPrePreGids]
            preGids = [gid for gid in preGidsAll if gid in cellsPreGids]
            for preGid in preGids:
                preCell = sim.net.allCells[preGid]
                prePreGids = [conn[preGidIndex] for conn in preCell['conns'] if conn[preGidIndex] in cellsPrePreGids]
                totCon += 1
                if not set(prePreGids).isdisjoint(preGidsAll):
                    numDis += 1

    print '    Total disynaptic connections: %d / %d (%.2f%%)' % (numDis, totCon, float(numDis)/float(totCon)*100 if totCon>0 else 0.0)
    try:
        sim.allSimData['disynConns'] = numDis
    except:
        pass

    print '    time ellapsed (s): ', time() - start
    
    return numDis


######################################################################################################################################################
## Calculate normalized transfer entropy
######################################################################################################################################################
@exception
def nTE(cells1 = [], cells2 = [], spks1 = None, spks2 = None, timeRange = None, binSize = 20, numShuffle = 30):
    ''' 
    Calculate normalized transfer entropy
        - cells1 (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Subset of cells from which to obtain spike train 1 (default: [])
        - cells2 (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Subset of cells from which to obtain spike train 1 (default: [])
        - spks1 (list): Spike train 1; list of spike times; if omitted then obtains spikes from cells1 (default: None)
        - spks2 (list): Spike train 2; list of spike times; if omitted then obtains spikes from cells2 (default: None)
        - timeRange ([min, max]): Range of time to calculate nTE in ms (default: [0,cfg.duration])
        - binSize (int): Bin size used to convert spike times into histogram 
        - numShuffle (int): Number of times to shuffle spike train 1 to calculate TEshuffled; note: nTE = (TE - TEShuffled)/H(X2F|X2P)

        - Returns nTE (float): normalized transfer entropy 
    '''

    from neuron import h
    import netpyne
    import sim
    import os
            
    root = os.path.dirname(netpyne.__file__)
    
    if 'nte' not in dir(h): 
        try: 
            print ' Warning: support/nte.mod not compiled; attempting to compile from %s via "nrnivmodl support"'%(root)
            os.system('cd ' + root + '; nrnivmodl support')
            from neuron import load_mechanisms
            load_mechanisms(root)
            print ' Compilation of support folder mod files successful'
        except:
            print ' Error compiling support folder mod files'
            return

    h.load_file(root+'/support/nte.hoc') # nTE code (also requires support/net.mod)
    
    if not spks1:  # if doesnt contain a list of spk times, obtain from cells specified
        cells, cellGids, netStimPops = getCellsInclude(cells1)
        numNetStims = 0

        # Select cells to include
        if len(cellGids) > 0:
            try:
                spkts = [spkt for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids]
            except:
                spkts = []
        else: 
            spkts = []

        # Add NetStim spikes
        spkts = list(spkts)
        numNetStims = 0
        for netStimPop in netStimPops:
            if 'stims' in sim.allSimData:
                cellStims = [cellStim for cell,cellStim in sim.allSimData['stims'].iteritems() if netStimPop in cellStim]
                if len(cellStims) > 0:
                    spktsNew = [spkt for cellStim in cellStims for spkt in cellStim[netStimPop] ]
                    spkts.extend(spktsNew)
                    numNetStims += len(cellStims)

        spks1 = list(spkts)

    if not spks2:  # if doesnt contain a list of spk times, obtain from cells specified
        cells, cellGids, netStimPops = getCellsInclude(cells2)
        numNetStims = 0

        # Select cells to include
        if len(cellGids) > 0:
            try:
                spkts = [spkt for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids]
            except:
                spkts = []
        else: 
            spkts = []

        # Add NetStim spikes
        spkts = list(spkts)
        numNetStims = 0
        for netStimPop in netStimPops:
            if 'stims' in sim.allSimData:
                cellStims = [cellStim for cell,cellStim in sim.allSimData['stims'].iteritems() if netStimPop in cellStim]
                if len(cellStims) > 0:
                    spktsNew = [spkt for cellStim in cellStims for spkt in cellStim[netStimPop] ]
                    spkts.extend(spktsNew)
                    numNetStims += len(cellStims)

        spks2 = list(spkts)

    # time range
    if getattr(sim, 'cfg', None):
        timeRange = [0,sim.cfg.duration]
    else:
        timeRange = [0, max(spks1+spks2)]

    inputVec = h.Vector()
    outputVec = h.Vector()
    histo1 = np.histogram(spks1, bins = np.arange(timeRange[0], timeRange[1], binSize))
    histoCount1 = histo1[0] 
    histo2 = np.histogram(spks2, bins = np.arange(timeRange[0], timeRange[1], binSize))
    histoCount2 = histo2[0] 

    inputVec.from_python(histoCount1)
    outputVec.from_python(histoCount2)
    out = h.normte(inputVec, outputVec, numShuffle)
    TE, H, nTE, _, _ = out.to_python()
    return nTE


######################################################################################################################################################
## Calculate granger causality
######################################################################################################################################################
@exception
def granger(cells1 = [], cells2 = [], spks1 = None, spks2 = None, label1 = 'spkTrain1', label2 = 'spkTrain2', timeRange = None, binSize=5, plotFig = True, 
    saveData = None, saveFig = None, showFig = True):
    ''' 
    Calculate and optionally plot Granger Causality 
        - cells1 (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Subset of cells from which to obtain spike train 1 (default: [])
        - cells2 (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Subset of cells from which to obtain spike train 2 (default: [])
        - spks1 (list): Spike train 1; list of spike times; if omitted then obtains spikes from cells1 (default: None)
        - spks2 (list): Spike train 2; list of spike times; if omitted then obtains spikes from cells2 (default: None)
        - label1 (string): Label for spike train 1 to use in plot
        - label2 (string): Label for spike train 2 to use in plot
        - timeRange ([min, max]): Range of time to calculate nTE in ms (default: [0,cfg.duration])
        - binSize (int): Bin size used to convert spike times into histogram 
        - plotFig (True|False): Whether to plot a figure showing Granger Causality Fx2y and Fy2x
        - saveData (None|'fileName'): File name where to save the final data used to generate the figure (default: None)
        - saveFig (None|'fileName'): File name where to save the figure;
            if set to True uses filename from simConfig (default: None)(default: None)
        - showFig (True|False): Whether to show the figure or not;
            if set to True uses filename from simConfig (default: None)

        - Returns 
            F: list of freqs
            Fx2y: causality measure from x to y 
            Fy2x: causality from y to x 
            Fxy: instantaneous causality between x and y 
            fig: Figure handle 
    '''
    
    import sim
    import numpy as np
    from netpyne.support.bsmart import pwcausalr

    if not spks1:  # if doesnt contain a list of spk times, obtain from cells specified
        cells, cellGids, netStimPops = getCellsInclude(cells1)
        numNetStims = 0

        # Select cells to include
        if len(cellGids) > 0:
            try:
                spkts = [spkt for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids]
            except:
                spkts = []
        else: 
            spkts = []

        # Add NetStim spikes
        spkts = list(spkts)
        numNetStims = 0
        for netStimPop in netStimPops:
            if 'stims' in sim.allSimData:
                cellStims = [cellStim for cell,cellStim in sim.allSimData['stims'].iteritems() if netStimPop in cellStim]
                if len(cellStims) > 0:
                    spktsNew = [spkt for cellStim in cellStims for spkt in cellStim[netStimPop] ]
                    spkts.extend(spktsNew)
                    numNetStims += len(cellStims)

        spks1 = list(spkts)

    if not spks2:  # if doesnt contain a list of spk times, obtain from cells specified
        cells, cellGids, netStimPops = getCellsInclude(cells2)
        numNetStims = 0

        # Select cells to include
        if len(cellGids) > 0:
            try:
                spkts = [spkt for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids]
            except:
                spkts = []
        else: 
            spkts = []

        # Add NetStim spikes
        spkts = list(spkts)
        numNetStims = 0
        for netStimPop in netStimPops:
            if 'stims' in sim.allSimData:
                cellStims = [cellStim for cell,cellStim in sim.allSimData['stims'].iteritems() if netStimPop in cellStim]
                if len(cellStims) > 0:
                    spktsNew = [spkt for cellStim in cellStims for spkt in cellStim[netStimPop] ]
                    spkts.extend(spktsNew)
                    numNetStims += len(cellStims)

        spks2 = list(spkts)


    # time range
    if timeRange is None:
        if getattr(sim, 'cfg', None):
            timeRange = [0,sim.cfg.duration]
        else:
            timeRange = [0, max(spks1+spks2)]

    histo1 = np.histogram(spks1, bins = np.arange(timeRange[0], timeRange[1], binSize))
    histoCount1 = histo1[0] 

    histo2 = np.histogram(spks2, bins = np.arange(timeRange[0], timeRange[1], binSize))
    histoCount2 = histo2[0] 

    fs = 1000/binSize
    F,pp,cohe,Fx2y,Fy2x,Fxy = pwcausalr(np.array([histoCount1, histoCount2]), 1, len(histoCount1), 10, fs, fs/2)


    # plot granger
    fig = -1
    if plotFig:
        fig = plt.figure()
        plt.plot(F, Fy2x[0], label = label2 + ' -> ' + label1)
        plt.plot(F, Fx2y[0], 'r', label = label1 + ' -> ' + label2)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Granger Causality')
        plt.legend()
        
        # save figure data
        if saveData:
            figData = {'cells1': cells1, 'cells2': cells2, 'spks1': cells1, 'spks2': cells2, 'binSize': binSize, 'Fy2x': Fy2x[0], 'Fx2y': Fx2y[0], 
            'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}
        
            _saveFigData(figData, saveData, '2Dnet')
     
        # save figure
        if saveFig: 
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename+'_'+'2Dnet.png'
            plt.savefig(filename)

        # show fig 
        if showFig: _showFigure()

    return F, Fx2y[0],Fy2x[0], Fxy[0], fig



######################################################################################################################################################
## EPSPs amplitude
######################################################################################################################################################
@exception
def plotEPSPAmp(include=None, trace=None, start=0, interval=50, number=2, amp='absolute', polarity='exc', saveFig=False, showFig=True):

    import sim

    print('Plotting EPSP amplitudes...')

    if include is None: include = [] # If not defined, initialize as empty list

    cells, cellGids, _ = getCellsInclude(include)
    gidPops = {cell['gid']: cell['tags']['pop'] for cell in cells}

    if not trace: 
        print 'Error: Missing trace to to plot EPSP amplitudes'
        return
    step = sim.cfg.recordStep

    peaksAbs = np.zeros((number, len(cellGids)))
    peaksRel = np.zeros((number, len(cellGids)))
    for icell, gid in enumerate(cellGids):
        vsoma = sim.allSimData[trace]['cell_'+str(gid)]
        for ipeak in range(number):
            if polarity == 'exc':
                peakAbs = max(vsoma[int(start/step+(ipeak*interval/step)):int(start/step+(ipeak*interval/step)+(interval-1)/step)]) 
            elif polarity == 'inh':
                peakAbs = min(vsoma[int(start/step+(ipeak*interval/step)):int(start/step+(ipeak*interval/step)+(interval-1)/step)]) 
            peakRel = peakAbs - vsoma[int((start-1)/step)]
            peaksAbs[ipeak,icell] = peakAbs
            peaksRel[ipeak,icell] = peakRel

    if amp == 'absolute':
        peaks = peaksAbs
        ylabel = 'EPSP peak V (mV)'
    elif amp == 'relative':
        peaks = peaksRel
        ylabel = 'EPSP amplitude (mV)'
    elif amp == 'ratio':
        peaks = np.zeros((number, len(cellGids)))
        for icell in range(len(cellGids)):
            peaks[:, icell] = peaksRel[:, icell] / peaksRel[0, icell]
        ylabel = 'EPSP amplitude ratio'
        
    xlabel = 'EPSP number'

    # plot
    fig = plt.figure()
    plt.plot(peaks, marker='o')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    h = plt.axes()
    ylim=list(h.get_ylim())
    h.set_ylim(ylim[0], ylim[1]+(0.15*abs(ylim[1]-ylim[0])))
    h.set_xticks(range(number))
    h.set_xticklabels(range(1, number+1))
    plt.legend(gidPops.values())
    if amp == 'ratio':
        plt.plot((0, number-1), (1.0, 1.0), ':', color= 'gray')

    # save figure
    if saveFig: 
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'EPSPamp_'+amp+'.png'
        plt.savefig(filename)

    # show fig 
    if showFig: _showFigure()

    return peaks, fig

