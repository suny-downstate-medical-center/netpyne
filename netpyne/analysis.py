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
from scipy import array, cumsum
from numbers import Number
import math

import warnings
warnings.filterwarnings("ignore")

colorList = [[0.42,0.67,0.84], [0.90,0.76,0.00], [0.42,0.83,0.59], [0.90,0.32,0.00],
            [0.34,0.67,0.67], [0.90,0.59,0.00], [0.42,0.82,0.83], [1.00,0.85,0.00],
            [0.33,0.67,0.47], [1.00,0.38,0.60], [0.57,0.67,0.33], [0.5,0.2,0.0],
            [0.71,0.82,0.41], [0.0,0.2,0.5], [0.70,0.32,0.10]]*3

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
        
        elif isinstance(condition, tuple):  # subset of a pop with relative indices
            cellsPop = [c['gid'] for c in allCells if c['tags']['pop']==condition[0]]
            if isinstance(condition[1], list):
                cellGids.extend([gid for i,gid in enumerate(cellsPop) if i in condition[1]])
            elif isinstance(condition[1], int):
                cellGids.extend([gid for i,gid in enumerate(cellsPop) if i==condition[1]])

    cellGids = list(set(cellGids))  # unique values
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
## Raster plot 
######################################################################################################################################################
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
        if orderBy not in cells[0]['tags']:  # if orderBy property doesn't exist or is not numeric, use gid
            orderBy = 'gid'
        elif not isinstance(cells[0]['tags'][orderBy], Number): 
            orderBy = 'gid'
        ylabelText = 'Cells (ordered by %s)'%(orderBy)   
    
        if orderBy == 'gid': 
            yorder = [cell[orderBy] for cell in cells]
        else:
            yorder = [cell['tags'][orderBy] for cell in cells]

        #if orderInverse: yorder.reverse()

        sortedGids = {gid:i for i,(y,gid) in enumerate(sorted(zip(yorder,cellGids)))}
        spkinds = [sortedGids[gid]  for gid in spkgids]

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
                    avgRates[pop] = len([spkid for spkid in spkinds[:numCellSpks-1] if sim.net.allCells[int(spkid)]['tags']['pop']==pop])/popNum/tsecs
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
        color = 'k'
        tx = 1.01
        margin = 1.0/numCells/2
        tys = [(float(popLen)/numCells)*(1-2*margin) for popLen in popNumCells]
        tysOffset = list(cumsum(tys))[:-1]
        tysOffset.insert(0, 0)
        labels = popLabelRates if popRates else popLabels
        for ipop,(ty, tyOffset, popLabel) in enumerate(zip(tys, tysOffset, popLabels)):
            label = popLabelRates[ipop] if popRates else popLabel
            if orderInverse:
                finalty = 1.0 - (tyOffset + ty/2.0 - 0.01)
            else:
                finalty = tyOffset + ty/2.0 - 0.01
            plt.text(tx, finalty, label, transform=ax.transAxes, fontsize=fontsiz, color=popColors[popLabel])
        maxLabelLen = max([len(l) for l in labels])
        plt.subplots_adjust(right=(1.0-0.011*maxLabelLen))

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
def plotSpikeHist (include = ['allCells', 'eachPop'], timeRange = None, binSize = 5, overlay=True, graphType='line', yaxis = 'rate', 
    popColors = [], dpi = 100, figSize = (10,8), saveData = None, saveFig = None, showFig = True): 
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
    if yaxis == 'rate': yaxisLabel = 'Avg cell firing rate (Hz)'
    elif yaxis == 'count': yaxisLabel = 'Spike count'
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

        histData.append(histoCount)

        if yaxis=='rate': histoCount = histoCount * (1000.0 / binSize) / (len(cellGids)+numNetStims) # convert to firing rate

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

    return fig



######################################################################################################################################################
## Plot spike histogram
######################################################################################################################################################
def plotSpikeStats (include = ['allCells', 'eachPop'], timeRange = None, graphType='boxplot', stats = ['rate', 'isicv'], 
                 popColors = [], figSize = (6,8), saveData = None, saveFig = None, showFig = True): 
    ''' 
    Plot spike histogram
        - include (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): List of data series to include. 
            Note: one line per item, not grouped (default: ['allCells', 'eachPop'])
        - timeRange ([start:stop]): Time range of spikes shown; if None shows all (default: None)
        - graphType ('boxplot'): Type of graph to use (default: 'boxplot')
        - stats (['rate', |'isicv'| 'sync'| 'pairsync']): Measure to plot stats on (default: ['rate', 'isicv'])
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

    print('Plotting spike stats...')

    # Set plot style
    colors = []
    params = {
        'axes.labelsize': 14,
        'text.fontsize': 14,
        'legend.fontsize': 14,
        'xtick.labelsize': 14,
        'ytick.labelsize': 14,
        'text.usetex': False,
        }
    plt.rcParams.update(params)

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
        fontsiz = 16

        statData = []

        # Calculate data for each entry in include
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


            # rate stats
            if stat == 'rate':
                toRate = 1e3/(timeRange[1]-timeRange[0])
                rates = [spkinds.count(gid)*toRate for gid in set(spkinds)] 
                statData.insert(0, rates)
                xlabel = 'Rate'

            # Inter-spike interval (ISI) coefficient of variation (CV) stats
            elif stat == 'isicv':
                xlabel = 'Irregularity (ISI CV)'
                spkmat = [[spkt for spkind,spkt in zip(spkinds,spkts) if spkind==gid] for gid in set(spkinds)]
                isimat = [[t - s for s, t in zip(spks, spks[1:])] for spks in spkmat]
                isicv = [np.std(x) / np.mean(x) for x in isimat if len(x)>0]
                statData.insert(0, isicv) 

            # synchrony
            elif stat in ['sync', 'pairsync']:
                try: 
                    import pyspike  
                except:
                    print "Error: plotSpikeStats() requires the PySpike python package to calculate synchrony (try: pip install pyspike)"
                    return 0

                
                spkmat = [pyspike.SpikeTrain([spkt for spkind,spkt in zip(spkinds,spkts) if spkind==gid], timeRange) for gid in set(spkinds)]
                if stat == 'sync':
                    xlabel = 'Synchrony'# (SPIKE-Sync measure)' # see http://www.scholarpedia.org/article/Measures_of_spike_train_synchrony
                    syncMat = [pyspike.spike_sync(spkmat)]
                    #graphType = 'bar'
                elif stat == 'pairsync':
                    xlabel = 'Pairwise synchrony'# (SPIKE-Sync measure)' # see http://www.scholarpedia.org/article/Measures_of_spike_train_synchrony
                    syncMat = np.mean(pyspike.spike_sync_matrix(spkmat), 0)
                    

                statData.insert(0, syncMat)

            colors.insert(0, popColors[subset] if subset in popColors else colorList[iplot%len(colorList)])

        # plotting
        if include[0] == 'allCells': 
            colors.insert(len(include), (0.5,0.5,0.5))  # if allCells is at top make its color=black
            del colors[0]

        if graphType == 'boxplot':
            meanpointprops = dict(marker=(5,1,0), markeredgecolor='black', markerfacecolor='white')
            bp=plt.boxplot(statData, labels=include[::-1], notch=False, sym='k+', meanprops=meanpointprops, 
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
                #for f in bp['fliers']:
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
        
        # elif graphType == 'bar':
        #     print range(1, len(statData)+1), statData
        #     plt.bar(range(1, len(statData)+1), statData, tick_label=include[::-1], orientation='horizontal', colors=colors)

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
                filename = saveFig
            else:
                filename = sim.cfg.filename+'_'+'spikeStat_'+stat+'.png'
            plt.savefig(filename)

        # show fig 
        if showFig: _showFigure()

    return fig



######################################################################################################################################################
## Plot spike histogram
######################################################################################################################################################
def plotRatePSD (include = ['allCells', 'eachPop'], timeRange = None, binSize = 5, Fs = 200, smooth = 0, overlay=True, 
    popColors = None, figSize = (10,8), saveData = None, saveFig = None, showFig = True): 
    ''' 
    Plot firing rate power spectral density (PSD)
        - include (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): List of data series to include. 
            Note: one line per item, not grouped (default: ['allCells', 'eachPop'])
        - timeRange ([start:stop]): Time range of spikes shown; if None shows all (default: None)
        - binSize (int): Size in ms of spike bins (default: 5)
        - Fs (float): PSD sampling frequency used to calculate the Fourier frequencies (default: 200)
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

        color = popColors[subset] if subset in popColors else colorList[iplot%len(colorList)] 

        if not overlay: 
            plt.subplot(len(include),1,iplot+1)  # if subplot, create new subplot
            title (str(subset), fontsize=fontsiz)
            color = 'blue'
        
        power = mlab.psd(histoCount, Fs=Fs, NFFT=256, detrend=mlab.detrend_none, window=mlab.window_hanning, 
            noverlap=0, pad_to=None, sides='default', scale_by_freq=None)

        if smooth:
            signal = _smooth1d(10*np.log10(power[0]), smooth)
        else:
            signal = 10*np.log10(power[0])
        freqs = power[1]


        plt.plot(freqs, signal, linewidth=1.5, color=color)

        plt.xlabel('Frequency (Hz)', fontsize=fontsiz)
        plt.ylabel('Power Spectral Density (dB/Hz)', fontsize=fontsiz) # add yaxis in opposite side
        plt.xlim([0, (Fs/2)-1])

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

    return fig, power



######################################################################################################################################################
## Plot recorded cell traces (V, i, g, etc.)
######################################################################################################################################################
def plotTraces (include = None, timeRange = None, overlay = False, oneFigPer = 'cell', rerun = False, colors = None, ylim = None,
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

    if include is None: include = [] # If not defined, initialize as empty list
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
            fontsiz = 12
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
                        data = np.transpose(array(data))
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
def plotShape (includePost = ['all'], includePre = ['all'], showSyns = False, synStyle = '.', synSiz=3, dist=0.6, cvar=None, cvals=None, iv=False, ivprops=None,
    includeAxon=True, figSize = (10,8), saveData = None, saveFig = None, showFig = True): 
    ''' 
    Plot 3D cell shape using NEURON Interview PlotShape
        - includePre: (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): List of presynaptic cells to consider 
        when plotting connections (default: ['all'])
        - includePost: (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): List of cells to show shape of (default: ['all'])
        - synStyle: Style of marker to show synapses (default: '.') 
        - dist: 3D distance (like zoom) (default: 0.6)
        - synSize: Size of marker to show synapses (default: 3)
        - cvar: ('numSyns'|'weightNorm') Variable to represent in shape plot (default: None)
        - cvals: List of values to represent in shape plot; must be same as num segments (default: None)
        - iv: Use NEURON Interviews (instead of matplotlib) to show shape plot (default: None)
        - ivprops: Dict of properties to plot using Interviews (default: None)
        - includeAxon: Include axon in shape plot (default: True)
        - showSyns (True|False): Show synaptic connections in 3D 
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

    if not iv: # plot using Python instead of interviews
        from mpl_toolkits.mplot3d import Axes3D
        from netpyne.support import morphology as morph # code adapted from https://github.com/ahwillia/PyNeuron-Toolbox
        
        # create secList from include
        cellsPreGids = [c.gid for c in sim.getCellsList(includePre)] if includePre else []
        cellsPost = sim.getCellsList(includePost)
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
        # if not includeAxon:         
        #     secs = [sec for sec in secs if 'axon' not in sec.hname()]

        # Plot shapeplot
        cbLabels = {'numSyns': 'number of synapses', 'weightNorm': 'weight scaling'}
        fig=plt.figure(figsize=(10,10))
        shapeax = plt.subplot(111, projection='3d')
        shapeax.elev=90 # 90 
        shapeax.azim=-90 # -90
        shapeax.dist=dist*shapeax.dist
        plt.axis('equal')
        cmap=plt.cm.jet #YlOrBr_r
        morph.shapeplot(h,shapeax, sections=secs, cvals=cvals, cmap=cmap)
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        if not cvals==None and len(cvals)>0: 
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=np.min(cvals), vmax=np.max(cvals)))
            sm._A = []  # fake up the array of the scalar mappable
            cb = plt.colorbar(sm, fraction=0.15, shrink=0.5, pad=0.01, aspect=20)    
            if cvar: cb.set_label(cbLabels[cvar], rotation=90)

        if showSyns:
            synColor='red'
            for cellPost in cellsPost:
                for sec in cellPost.secs.values():
                    for synMech in sec['synMechs']:
                        morph.mark_locations(h, sec['hSec'], synMech['loc'], markspec=synStyle, color=synColor, markersize=synSiz)
                  
        #plt.title(str(includePre)+' -> '+str(includePost) + ' ' + str(cvar))
        shapeax.set_xticklabels([])

        # save figure
        if saveFig: 
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename+'_shape.png'
            plt.savefig(filename)

        # show fig 
        if showFig: _showFigure()

    else:  # Plot using Interviews
        # colors: 0 white, 1 black, 2 red, 3 blue, 4 green, 5 orange, 6 brown, 7 violet, 8 yellow, 9 gray
        fig = h.Shape()
        secList = h.SectionList()
        if not ivprops:
            ivprops = {'colorSecs': 1, 'colorSyns':2 ,'style': 'o', 'siz':2}
        
        for cell in [c for c in sim.net.cells if c.gid in includePost or c.tags['pop'] in includePost]:
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
## Plot LFP (time-resolved or power spectra)
######################################################################################################################################################
def plotLFP ():
    import sim

    print('Plotting LFP power spectral density...')

    colorspsd=array([[0.42,0.67,0.84],[0.42,0.83,0.59],[0.90,0.76,0.00],[0.90,0.32,0.00],[0.34,0.67,0.67],[0.42,0.82,0.83],[0.90,0.59,0.00],[0.33,0.67,0.47],[1.00,0.85,0.00],[0.71,0.82,0.41],[0.57,0.67,0.33],[1.00,0.38,0.60],[0.5,0.2,0.0],[0.0,0.2,0.5]]) 

    lfpv=[[] for c in range(len(sim.lfppops))]    
    # Get last modified .mat file if no input and plot
    for c in range(len(sim.lfppops)):
        lfpv[c] = sim.lfps[:,c]    
    lfptot = sum(lfpv)
        
    # plot pops separately
    plotPops = 0
    if plotPops:    
        plt.figure() # Open a new figure
        for p in range(len(sim.lfppops)):
            psd(lfpv[p],Fs=200, linewidth= 2,color=colorspsd[p])
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('Power')
            h=plt.axes()
            h.set_yticklabels([])
        plt.legend(['L2/3','L5A', 'L5B', 'L6'])

    # plot overall psd
    plt.figure() # Open a new figure
    psd(lfptot,Fs=200, linewidth= 2)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power')
    h=plt.axes()
    h.set_yticklabels([])

    plt.show()

def _roundFigures(x, n):
    """Returns x rounded to n significant figures."""
    return round(x, int(n - math.ceil(math.np.log10(abs(x)))))


######################################################################################################################################################
## Support function for plotConn() - calculate conn using data from sim object
######################################################################################################################################################

def __plotConnCalculateFromSim__(includePre, includePost, feature, orderBy, groupBy, groupByInterval, synOrConn, synMech):

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
                        if conn[preGidIndex] in cellIndsPre:
                            connMatrix[cellIndsPre[conn[preGidIndex]], cellIndsPost[cell['gid']]] += conn[feature]
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
        if not isinstance(groupByInterval, Number):
            print 'groupByInterval not specified'
            return
  
        # group cells by 'groupBy' feature (eg. 'y') in intervals of 'groupByInterval')
        cellValuesPre = [cell['tags'][groupBy] for cell in cellsPre]
        minValuePre = _roundFigures(groupByInterval * np.floor(min(cellValuesPre) / groupByInterval), 3)
        maxValuePre  = _roundFigures(groupByInterval * np.ceil(max(cellValuesPre) / groupByInterval), 3)        
        groupsPre = np.arange(minValuePre, maxValuePre, groupByInterval)
        groupsPre = [_roundFigures(x,3) for x in groupsPre]

        if includePre == includePost:
            groupsPost = groupsPre       
        else:
            cellValuesPost = [cell['tags'][groupBy] for cell in cellsPost]
            minValuePost = _roundFigures(groupByInterval * np.floor(min(cellValuesPost) / groupByInterval), 3)
            maxValuePost  = _roundFigures(groupByInterval * np.ceil(max(cellValuesPost) / groupByInterval), 3)        
            groupsPre = np.arange(minValuePost, maxValuePost, groupByInterval)
            groupsPre = [_roundFigures(x,3) for x in groupsPost]


        if len(groupsPre) < 2 or len(groupsPost) < 2: 
            print 'groupBy %s with groupByInterval %s results in <2 groups'%(str(groupBy), str(groupByInterval))
            return
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
            numCellsGroupPre[groupPre] = len([cell for cell in cellsPre if groupPre <= cell['tags'][groupBy] < (groupPre+groupByInterval)])
        
        if includePre == includePost:
            numCellsGroupPost = numCellsGroupPre  
        else:
            numCellsGroupPost = {}
            for groupPost in groupsPost:
                numCellsGroupPost[groupPost] = len([cell for cell in cellsPost if groupPost <= cell['tags'][groupBy] < (groupPost+groupByInterval)])


        maxConnMatrix = np.zeros((len(groupsPre), len(groupsPost)))
        if feature == 'convergence': maxPostConnMatrix = np.zeros((len(groupsPre), len(groupsPost)))
        if feature == 'divergence': maxPreConnMatrix = np.zeros((len(groupsPre), len(groupsPost)))
        for preGroup in groupsPre:
            for postGroup in groupsPost: 
                if numCellsGroupPre[preGroup] == -1: numCellsGroupPre[preGroup] = numCellsGroupPost[postGroup]
                maxConnMatrix[groupIndsPre[preGroup], groupIndsPost[postGroup]] = numCellsGroupPre[preGroup]*numCellsGroupPost[postGroup]
                if feature == 'convergence': maxPostConnMatrix[groupIndsPre[prePop], groupIndsPost[postGroup]] = numCellsPopPost[postGroup]
                if feature == 'divergence': maxPreConnMatrix[groupIndsPre[preGroup], groupIndsPost[postGroup]] = numCellsPopPre[preGroup]
        
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
                    preCell = next((c for c in cellsPre if cell['gid']==conn[preGidIndex]), None)
                    if preCell:
                        preGroup = _roundFigures(groupByInterval * np.floor(preCell['tags'][groupBy] / groupByInterval), 3)
                    else:
                        None

                postGroup = _roundFigures(groupByInterval * np.floor(cell['tags'][groupBy] / groupByInterval), 3)

                #print groupInds
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

def __plotConnCalculateFromFile__(includePre, includePost, feature, orderBy, groupBy, groupByInterval, synOrConn, synMech, connsFile, tagsFile):
    
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
def plotConn (includePre = ['all'], includePost = ['all'], feature = 'strength', orderBy = 'gid', figSize = (10,10), groupBy = 'pop', groupByInterval = None, 
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
        connMatrix, pre, post = __plotConnCalculateFromFile__(includePre, includePost, feature, orderBy, groupBy, groupByInterval, synOrConn, synMech, connsFile, tagsFile)
    else:
        connMatrix, pre, post = __plotConnCalculateFromSim__(includePre, includePost, feature, orderBy, groupBy, groupByInterval, synOrConn, synMech)


    if connMatrix == None:
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
                plt.plot(array([0,len(popsPre)])-0.5,array([ipop,ipop])-0.5,'-',c=(0.7,0.7,0.7))
            for ipop, pop in enumerate(popsPost):
                plt.plot(array([ipop,ipop])-0.5,array([0,len(popsPost)])-0.5,'-',c=(0.7,0.7,0.7))

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
                plt.plot(array([0,len(groupsPre)])-0.5,array([igroup,igroup])-0.5,'-',c=(0.7,0.7,0.7))
            for igroup, group in enumerate(groupsPost):
                plt.plot(array([igroup,igroup])-0.5,array([0,len(groupsPost)])-0.5,'-',c=(0.7,0.7,0.7))

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

