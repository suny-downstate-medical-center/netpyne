"""
Module for anaysis and plotting of spiking-related results

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from builtins import dict
from builtins import round
from builtins import str
try:
    basestring
except NameError:
    basestring = str
from builtins import range
from builtins import zip

from future import standard_library
standard_library.install_aliases()
from netpyne import __gui__

if __gui__:
    import matplotlib.pyplot as plt
    from matplotlib import gridspec
    from matplotlib import mlab
import numpy as np
from numbers import Number
import pandas as pd
import scipy
from ..specs import Dict
from .utils import colorList, exception, getCellsInclude, getSpktSpkid, _showFigure, _saveFigData, syncMeasure, _smooth1d


# -------------------------------------------------------------------------------------------------------------------
## Calculate avg and peak rate of different subsets of cells for specific time period
# -------------------------------------------------------------------------------------------------------------------
@exception
def calculateRate (include = ['allCells', 'eachPop'], peakBin = 5, timeRange = None): 
    """
    Function for/to <short description of `netpyne.analysis.spikes.calculateRate`>

    Parameters
    ----------
    include : list
        <Short description of include>
        **Default:** ``['allCells', 'eachPop']``
        **Options:** ``<option>`` <description of option>
 
    peakBin : int
        <Short description of peakBin>
        **Default:** ``5``
        **Options:** ``<option>`` <description of option>
 
    timeRange : <``None``?>
        <Short description of timeRange>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
"""

    from .. import sim

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
                spkinds,spkts = list(zip(*[(spkgid,spkt) for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids]))
            except:
                spkinds,spkts = [],[]
        else: 
            spkinds,spkts = [],[]

        # Add NetStim spikes
        spkts, spkinds = list(spkts), list(spkinds)
        numNetStims = 0
        if 'stims' in sim.allSimData:
            for netStimLabel in netStimLabels:
                netStimSpks = [spk for cell,stims in sim.allSimData['stims'].items() \
                for stimLabel,stimSpks in stims.items() for spk in stimSpks if stimLabel == netStimLabel]
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


# -------------------------------------------------------------------------------------------------------------------
## Plot avg and peak rates at different time periods 
# -------------------------------------------------------------------------------------------------------------------
@exception
def plotRates (include =['allCells', 'eachPop'], peakBin = 5, timeRanges = None, timeRangeLabels = None, colors = None, figSize = ((5,5)), saveData = None, ylim = None, saveFig = None, showFig = True):
    """
    Function for/to <short description of `netpyne.analysis.spikes.plotRates`>

    Parameters
    ----------
    include : list
        <Short description of include>
        **Default:** ``['allCells', 'eachPop']``
        **Options:** ``<option>`` <description of option>
 
    peakBin : int
        <Short description of peakBin>
        **Default:** ``5``
        **Options:** ``<option>`` <description of option>
 
    timeRanges : <``None``?>
        <Short description of timeRanges>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    timeRangeLabels : <``None``?>
        <Short description of timeRangeLabels>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    colors : <``None``?>
        <Short description of colors>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    figSize : tuple
        <Short description of figSize>
        **Default:** ``(5, 5)``
        **Options:** ``<option>`` <description of option>
 
    saveData : <``None``?>
        <Short description of saveData>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    ylim : <``None``?>
        <Short description of ylim>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    saveFig : <``None``?>
        <Short description of saveFig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    showFig : bool
        <Short description of showFig>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>
 
"""

    from .. import sim

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
        ax1.set_xticks(list(range(len(timeRangeLabels))))
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
        ax2.set_xticks(list(range(len(timeRangeLabels))))
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


# -------------------------------------------------------------------------------------------------------------------
## Plot sync at different time periods 
# -------------------------------------------------------------------------------------------------------------------
@exception
def plotSyncs(include=['allCells', 'eachPop'], timeRanges=None, timeRangeLabels=None, colors=None, figSize=((5,5)), saveData=None, saveFig = None, showFig=True):
    """
    Function for/to <short description of `netpyne.analysis.spikes.plotSyncs`>

    Parameters
    ----------
    include : list
        <Short description of include>
        **Default:** ``['allCells', 'eachPop']``
        **Options:** ``<option>`` <description of option>
 
    timeRanges : <``None``?>
        <Short description of timeRanges>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    timeRangeLabels : <``None``?>
        <Short description of timeRangeLabels>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    colors : <``None``?>
        <Short description of colors>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    figSize : tuple
        <Short description of figSize>
        **Default:** ``(5, 5)``
        **Options:** ``<option>`` <description of option>
 
    saveData : <``None``?>
        <Short description of saveData>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    saveFig : <``None``?>
        <Short description of saveFig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    showFig : bool
        <Short description of showFig>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>
 
"""

    from .. import sim

    if not colors: colors = colorList

    syncs = []
    if not timeRangeLabels:
        timeRangeLabels = ['%f-%f ms'%(t[0], t[1]) for t in timeRanges] #['period '+i for i in range(len(timeRanges))]

    for i, timeRange in enumerate(timeRanges):
        print(timeRange)
        _, sync = sim.analysis.plotSpikeStats (include = include, timeRange = timeRange, stats = ['sync'], saveFig = False, showFig =False)
        print(sync)
        sync = [s[0] for s in sync]
        syncs.append(sync)

    fig1,ax1 = plt.subplots(figsize=figSize)

    # avg
    fontsiz=14
    ax1.set_color_cycle(colors)
    ax1.plot(syncs, marker='o')
    ax1.set_xlabel('Time period', fontsize=fontsiz)
    ax1.set_ylabel('Spiking synchrony', fontsize=fontsiz)
    ax1.set_xticks(list(range(len(timeRangeLabels))))
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


# -------------------------------------------------------------------------------------------------------------------
## Raster plot
# -------------------------------------------------------------------------------------------------------------------
@exception
def plotRaster(include=['allCells'], timeRange=None, maxSpikes=1e8, orderBy='gid', orderInverse=False, labels='legend', popRates=False, spikeHist=None, spikeHistBin=5, syncLines=False, lw=2, marker='|', markerSize=5, popColors=None, figSize=(10, 8), fontSize=12, dpi=100, saveData=None, saveFig=None, showFig=True):
    """
    Function for/to <short description of `netpyne.analysis.spikes.plotRaster`>

    Parameters
    ----------
    include : list
        Cells to include in the plot.
        **Default:** 
        ``['allCells']`` plots all cells
        **Options:** 
        ``['all']`` plots all cells and stimulations, 
        ``['allNetStims']`` plots just stimulations, 
        ``['popName1']`` plots a single population, 
        ``['popName1', 'popName2']`` plots multiple populations, 
        ``[120]`` plots a single cell, 
        ``[120, 130]`` plots multiple cells, 
        ``[('popName1', 56)]`` plots a cell from a specific population, 
        ``[('popName1', [0, 1]), ('popName2', [4, 5, 6])]``, plots cells from multiple populations

    timeRange : list [start, stop]
        Time range to plot.
        **Default:** 
        ``None`` plots entire time range
        **Options:** ``<option>`` <description of option>
 
    maxSpikes : int
        Maximum number of spikes to be plotted.
        **Default:** ``1e8``
        **Options:** ``<option>`` <description of option>
 
    orderBy : str
        Unique numeric cell property by which to order the y-axis.
        **Default:** ``'gid'`` orders by cell ID
        **Options:**
        ``'y'`` orders by cell y-location,
        ``'ynorm'`` orders by cell normalized y-location

    orderInverse : bool
        Inverts the y-axis order if ``True``.
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
 
    labels : str
        Show population labels in a legend or as an overlay on one side of raster.
        **Default:** ``'legend'``
        **Options:** ``'overlay'``

    popRates : bool
        Include population firing rates on plot if ``True``.
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
 
    spikeHist : str
        Include spike histogram (spikes/bin) on plot. 
        **Default:** ``None``
        **Options:** 
        ``'overlay'`` overlays the histogram directly on the raster plot
        ``'subplot'`` shows the histogram as a subplot to the raster plot

    spikeHistBin : int
        Size of bin in ms to use for spike histogram. 
        **Default:** ``5``
        **Options:** ``<option>`` <description of option>
 
    syncLines : bool
        Calculate synchrony measure and plot vertical lines for each spike to evidence synchrony if ``True``.
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
 
    lw : int
        Line width for each spike.
        **Default:** ``2``
        **Options:** ``<option>`` <description of option>
 
    marker : str
        Marker for each spike.
        **Default:** ``'|'``
        **Options:** ``<option>`` <description of option>
 
    markerSize : int
        Size of marker for each spike.
        **Default:** ``5``
        **Options:** ``<option>`` <description of option>
 
    popColors : dict
        Dictionary with custom color (value) used for each population (key).
        **Default:** ``None`` uses standard colors
        **Options:** ``<option>`` <description of option>
 
    figSize : list [width, height]
        Size of figure in inches.
        **Default:** ``(10, 8)``
        **Options:** ``<option>`` <description of option>
 
    fontSize : int
        Font size on figure.
        **Default:** ``12``
        **Options:** ``<option>`` <description of option>
 
    dpi : int
        Resolution of figure in dots per inch.
        **Default:** ``100``
        **Options:** ``<option>`` <description of option>
 
    saveData : bool or str
        Whether and where to save the data used to generate the plot. 
        **Default:** ``False`` 
        **Options:** ``True`` autosaves the data,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.pkl'`` and ``'.json'``

    saveFig : bool or str
        Whether and where to save the figure.
        **Default:** ``False``
        **Options:** ``True`` autosaves the figure,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.png'``, ``'.jpg'``, ``'.eps'``, and ``'.tiff'``

    showFig : bool
        Shows the figure if ``True``.
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>
 
    Returns
    -------


"""

    from .. import sim

    print('Plotting raster...')

    # Select cells to include
    cells, cellGids, netStimLabels = getCellsInclude(include)

    df = pd.DataFrame.from_records(cells)
    df = pd.concat([df.drop('tags', axis=1), pd.DataFrame.from_records(df['tags'].tolist())], axis=1)

    keep = ['pop', 'gid', 'conns']

    if isinstance(orderBy, basestring) and orderBy not in cells[0]['tags']:  # if orderBy property doesn't exist or is not numeric, use gid
        orderBy = 'gid'
    elif orderBy is 'pop':
        df['popInd'] = df['pop'].astype('category')
        df['popInd'].cat.set_categories(sim.net.pops.keys(), inplace=True)
        orderBy='popInd'
    elif isinstance(orderBy, basestring) and not isinstance(cells[0]['tags'][orderBy], Number):
        orderBy = 'gid'
        
    if isinstance(orderBy, list):
        if 'pop' in orderBy:
            df['popInd'] = df['pop'].astype('category')
            df['popInd'].cat.set_categories(sim.net.pops.keys(), inplace=True)
            orderBy[orderBy.index('pop')] = 'popInd'
        keep = keep + list(set(orderBy) - set(keep))
    elif orderBy not in keep:
        keep.append(orderBy)

    df = df[keep]

    popLabels = [pop for pop in sim.net.allPops if pop in df['pop'].unique()] #preserves original ordering
    if netStimLabels: popLabels.append('NetStims')
    popColorsTmp = {popLabel: colorList[ipop%len(colorList)] for ipop,popLabel in enumerate(popLabels)} # dict with color for each pop
    if popColors: popColorsTmp.update(popColors)
    popColors = popColorsTmp
    if len(cellGids) > 0:
        gidColors = {cell['gid']: popColors[cell['tags']['pop']] for cell in cells}  # dict with color for each gid
        try:
            sel, spkts, spkgids = getSpktSpkid(cellGids=[] if include == ['allCells'] else cellGids, timeRange=timeRange) # using [] is faster for all cells
        except:
            import sys
            print((sys.exc_info()))
            spkgids, spkts = [], []
            sel = pd.DataFrame(columns=['spkt', 'spkid'])
        sel['spkgidColor'] = sel['spkid'].map(gidColors)
        df['gidColor'] = df['pop'].map(popColors)
        df.set_index('gid', inplace=True)


    # Order by
    if len(df) > 0:
        ylabelText = 'Cells (ordered by %s)'%(orderBy)
        df = df.sort_values(by=orderBy)
        sel['spkind'] = sel['spkid'].apply(df.index.get_loc)

    else:
        sel = pd.DataFrame(columns=['spkt', 'spkid', 'spkind'])
        ylabelText = ''

    # Add NetStim spikes
    numCellSpks = len(sel)
    numNetStims = 0
    for netStimLabel in netStimLabels:
        netStimSpks = [spk for cell,stims in sim.allSimData['stims'].items() \
            for stimLabel,stimSpks in stims.items() for spk in stimSpks if stimLabel == netStimLabel]
        if len(netStimSpks) > 0:
            # lastInd = max(spkinds) if len(spkinds)>0 else 0
            lastInd = sel['spkind'].max() if len(sel['spkind']) > 0 else 0
            spktsNew = netStimSpks
            spkindsNew = [lastInd+1+i for i in range(len(netStimSpks))]
            ns = pd.DataFrame(list(zip(spktsNew, spkindsNew)), columns=['spkt', 'spkind'])
            ns['spkgidColor'] = popColors['netStims']
            sel = pd.concat([sel, ns])
            numNetStims += 1
        else:
            pass
            #print netStimLabel+' produced no spikes'
    if len(cellGids)>0 and numNetStims:
        ylabelText = ylabelText + ' and NetStims (at the end)'
    elif numNetStims:
        ylabelText = ylabelText + 'NetStims'

    if numCellSpks+numNetStims == 0:
        print('No spikes available to plot raster')
        return None

    # Time Range
    if timeRange == [0,sim.cfg.duration]:
        pass
    elif timeRange is None:
        timeRange = [0,sim.cfg.duration]
    else:
        sel = sel.query('spkt >= @timeRange[0] and spkt <= @timeRange[1]')


    # Limit to maxSpikes
    if (len(sel)>maxSpikes):
        print(('  Showing only the first %i out of %i spikes' % (maxSpikes, len(sel)))) # Limit num of spikes
        if numNetStims: # sort first if have netStims
            sel = sel.sort_values(by='spkt')
        sel = sel.iloc[:maxSpikes]
        timeRange[1] =  sel['spkt'].max()

    # Calculate spike histogram
    if spikeHist:
        histo = np.histogram(sel['spkt'].tolist(), bins = np.arange(timeRange[0], timeRange[1], spikeHistBin))
        histoT = histo[1][:-1]+spikeHistBin/2
        histoCount = histo[0]

    # Plot spikes
    # set font size
    plt.rcParams.update({'font.size': fontSize})

    fig,ax1 = plt.subplots(figsize=figSize)
    fontsiz = fontSize
 
    if spikeHist == 'subplot':
        gs = gridspec.GridSpec(2, 1,height_ratios=[2,1])
        ax1=plt.subplot(gs[0])
    sel['spkt'] = sel['spkt'].apply(pd.to_numeric)
    sel.plot.scatter(ax=ax1, x='spkt', y='spkind', lw=lw, s=markerSize, marker=marker, c=sel['spkgidColor'].tolist()) # Create raster
    ax1.set_xlim(timeRange)

    # Plot stats
    gidPops = df['pop'].tolist()
    popNumCells = [float(gidPops.count(pop)) for pop in popLabels] if numCellSpks else [0] * len(popLabels)
    totalSpikes = len(sel)
    totalConnections = sum([len(conns) for conns in df['conns']])
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
                    avgRates[pop] = len([spkid for spkid in sel['spkind'].iloc[:numCellSpks-1] if df['pop'].iloc[int(spkid)]==pop])/popNum/tsecs
        if numNetStims:
            popNumCells[-1] = numNetStims
            avgRates['NetStims'] = len([spkid for spkid in sel['spkind'].iloc[numCellSpks:]])/numNetStims/tsecs

    # Plot synchrony lines
    if syncLines:
        for spkt in sel['spkt'].tolist():
            ax1.plot((spkt, spkt), (0, len(cells)+numNetStims), 'r-', linewidth=0.1)
        plt.title('cells=%i   syns/cell=%0.1f   rate=%0.1f Hz   sync=%0.2f' % (numCells,connsPerCell,firingRate,syncMeasure()), fontsize=fontsiz)
    else:
        plt.title('cells=%i   syns/cell=%0.1f   rate=%0.1f Hz' % (numCells,connsPerCell,firingRate), fontsize=fontsiz)
    # Axis
    ax1.set_xlabel('Time (ms)', fontsize=fontsiz)
    ax1.set_ylabel(ylabelText, fontsize=fontsiz)
    ax1.set_xlim(timeRange)
    ax1.set_ylim(-1, len(cells)+numNetStims+1)

    # Add legend
    if popRates:
        popLabelRates = [popLabel + ' (%.3g Hz)' % (avgRates[popLabel]) for popLabel in popLabels if popLabel in avgRates]

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
        figData = {'spkTimes': sel['spkt'].tolist(), 'spkInds': sel['spkind'].tolist(), 'spkColors': sel['spkgidColor'].tolist(), 'cellGids': cellGids, 'sortedGids': df.index.tolist(), 'numNetStims': numNetStims, 'include': include, 'timeRange': timeRange, 'maxSpikes': maxSpikes, 'orderBy': orderBy, 'orderInverse': orderInverse, 'spikeHist': spikeHist, 'syncLines': syncLines}
        _saveFigData(figData, saveData, 'raster')

    # save figure
    if saveFig:
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename + '_raster_' + orderBy + '.png'
        plt.savefig(filename, dpi=dpi)

    # show fig
    if showFig: _showFigure()

    return fig, {'include': include, 'spkts': spkts, 'spkinds': sel['spkind'].tolist(), 'timeRange': timeRange}


# -------------------------------------------------------------------------------------------------------------------
## Plot spike histogram
# -------------------------------------------------------------------------------------------------------------------
@exception
def plotSpikeHist(include=['eachPop', 'allCells'], timeRange=None, binSize=5, overlay=True, graphType='line', measure='rate', norm=False, smooth=None, filtFreq=None, filtOrder=3, axis=True, popColors=None, figSize=(10,8), dpi=100, saveData=None, saveFig=None, showFig=True, **kwargs):
    """
    Function for/to <short description of `netpyne.analysis.spikes.plotSpikeHist`>

    Parameters
    ----------
    include : list
        Populations and cells to include in the plot.
        **Default:** 
        ``['eachPop', 'allCells']`` plots histogram for each population and overall average
        **Options:** 
        ``['all']`` plots all cells and stimulations, 
        ``['allNetStims']`` plots just stimulations, 
        ``['popName1']`` plots a single population, 
        ``['popName1', 'popName2']`` plots multiple populations, 
        ``[120]`` plots a single cell, 
        ``[120, 130]`` plots multiple cells, 
        ``[('popName1', 56)]`` plots a cell from a specific population, 
        ``[('popName1', [0, 1]), ('popName2', [4, 5, 6])]``, plots cells from multiple populations

    timeRange : list [start, stop]
        Time range to plot.
        **Default:** 
        ``None`` plots entire time range
        **Options:** ``<option>`` <description of option>
 
    binSize : int
        Size of bin in ms to use for spike histogram. 
        **Default:** ``5``
        **Options:** ``<option>`` <description of option>
 
    overlay : bool
        Plots each group on a separate axis if ``False``.
        **Default:** ``True`` plots each group on one axis
        **Options:** ``<option>`` <description of option>
 
    graphType : str
        Show histograms as line graphs or bar plots.
        **Default:** ``'line'``
        **Options:** ``'bar'``

    measure : str
        Whether to plot spike freguency (rate) or spike count.
        **Default:** ``'rate'``
        **Options:** ``'count'``

    norm : bool
        Whether to normalize the data or not.
        **Default:** ``False`` does not normalize the data
        **Options:** ``<option>`` <description of option>
 
    smooth : int
        Window width for smoothing.
        **Default:** ``None`` does not smooth the data
        **Options:** ``<option>`` <description of option>
 
    filtFreq : int or list
        Frequency for low-pass filter (int) or frequencies for bandpass filter in a list: [low, high]
        **Default:** ``None`` does not filter the data
        **Options:** ``<option>`` <description of option>
 
    filtOrder : int
        Order of the filter defined by `filtFreq`.
        **Default:** ``3``
        **Options:** ``<option>`` <description of option>
 
    axis : bool
        Whether to include a labeled axis on the figure.
        **Default:** ``True`` includes a labeled axis
        **Options:** ``False`` includes a scale bar

    popColors : dict
        Dictionary with custom color (value) used for each population (key).
        **Default:** ``None`` uses standard colors
        **Options:** ``<option>`` <description of option>
 
    figSize : list [width, height]
        Size of figure in inches.
        **Default:** ``(10, 8)``
        **Options:** ``<option>`` <description of option>
 
    dpi : int
        Resolution of figure in dots per inch.
        **Default:** ``100``
        **Options:** ``<option>`` <description of option>
 
    saveData : bool or str
        Whether and where to save the data used to generate the plot. 
        **Default:** ``False`` 
        **Options:** ``True`` autosaves the data,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.pkl'`` and ``'.json'``

    saveFig : bool or str
        Whether and where to save the figure.
        **Default:** ``False``
        **Options:** ``True`` autosaves the figure,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.png'``, ``'.jpg'``, ``'.eps'``, and ``'.tiff'``

    showFig : bool
        Shows the figure if ``True``.
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>
 
    kwargs : <type>
        <Short description of kwargs>
        **Default:** *required*

    Returns
    -------


"""

    from .. import sim
    from ..support.scalebar import add_scalebar

    print('Plotting spike histogram...')

    # Replace 'eachPop' with list of pops
    if 'eachPop' in include:
        include.remove('eachPop')
        for pop in sim.net.allPops: include.append(pop)

    # Measure
    if measure == 'rate':
        if norm:
            yaxisLabel = 'Normalized firing rate'
        else:
            yaxisLabel = 'Avg cell firing rate (Hz)'
    elif measure == 'count':
        if norm:
            yaxisLabel = 'Normalized spike count'
        else:
            yaxisLabel = 'Spike count'
    else:
        print('Invalid measure: %s', (measure))
        return

    # time range
    if timeRange is None:
        timeRange = [0, sim.cfg.duration]

    histoData = []

    # create fig
    fig, ax1 = plt.subplots(figsize=figSize)
    fontsiz = 12

    # Plot separate line for each entry in include
    for iplot,subset in enumerate(include):
        if isinstance(subset, list):
            cells, cellGids, netStimLabels = getCellsInclude(subset)
        else:
            cells, cellGids, netStimLabels = getCellsInclude([subset])
        numNetStims = 0

        # Select cells to include
        if len(cellGids) > 0:
            try:
                spkinds,spkts = list(zip(*[(spkgid,spkt) for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids]))
            except:
                spkinds,spkts = [],[]
        else:
            spkinds,spkts = [],[]

        # Add NetStim spikes
        spkts, spkinds = list(spkts), list(spkinds)
        numNetStims = 0
        if 'stims' in sim.allSimData:
            for netStimLabel in netStimLabels:
                netStimSpks = [spk for cell,stims in sim.allSimData['stims'].items() \
                for stimLabel,stimSpks in stims.items() for spk in stimSpks if stimLabel == netStimLabel]
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

        if measure == 'rate':
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

        histoData.append(histoCount)

        if not isinstance(subset, list): 
            color = colorList[iplot%len(colorList)]
        else:   
            color = popColors[subset] if subset in popColors else colorList[iplot%len(colorList)]

        if not overlay:
            plt.subplot(len(include), 1, iplot+1)  # if subplot, create new subplot
            plt.title(str(subset), fontsize=fontsiz)
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
            if not isinstance(subset, list):
                color = colorList[i%len(colorList)]
            else:
                color = popColors[subset] if subset in popColors else colorList[i%len(colorList)]
            plt.plot(0,0,color=color,label=str(subset))
        plt.legend(fontsize=fontsiz, bbox_to_anchor=(1.04, 1), loc=2, borderaxespad=0.)
        maxLabelLen = min(10,max([len(str(l)) for l in include]))
        plt.subplots_adjust(right=(0.9-0.012*maxLabelLen))

    # Set axis or scaleber
    if not axis:
        ax = plt.gca()
        scalebarLoc = kwargs.get('scalebarLoc', 7)
        round_to_n = lambda x, n, m: int(np.round(round(x, -int(np.floor(np.log10(abs(x)))) + (n - 1)) / m)) * m
        sizex = round_to_n((timeRange[1]-timeRange[0])/10.0, 1, 50)
        add_scalebar(ax, hidex=False, hidey=True, matchx=False, matchy=True, sizex=sizex, sizey=None, unitsx='ms', unitsy='Hz', scalex=1, scaley=1, loc=scalebarLoc, pad=2, borderpad=0.5, sep=4, prop=None, barcolor="black", barwidth=3)
        plt.axis(axis)

    # save figure data
    if saveData:
        figData = {'histoData': histoData, 'histoT': histoT, 'include': include, 'timeRange': timeRange, 'binSize': binSize, 'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}

        _saveFigData(figData, saveData, 'spikeHist')

    # save figure
    if saveFig:
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_plot_spikeHist.png'
        plt.savefig(filename, dpi=dpi)

    # show fig
    if showFig: _showFigure()

    return fig, {'include': include, 'histoData': histoData, 'histoT': histoT, 'timeRange': timeRange}


# -------------------------------------------------------------------------------------------------------------------
## Plot spike statistics
# -------------------------------------------------------------------------------------------------------------------
@exception
def plotSpikeStats(include=['eachPop', 'allCells'], statDataIn={}, timeRange=None, graphType='boxplot', stats=['rate', 'isicv'], bins=50, histlogy=False, histlogx=False, histmin=0.0, density=False, includeRate0=False, legendLabels=None, normfit=False, histShading=True, xlim=None, popColors={}, figSize=(6,8), fontSize=12, dpi=100, saveData=None, saveFig=None, showFig=True, **kwargs): 
    """
    Function for/to <short description of `netpyne.analysis.spikes.plotSpikeStats`>

    Parameters
    ----------
    include : list
        Populations and cells to include in the plot.
        **Default:** 
        ``['eachPop', 'allCells']`` plots histogram for each population and overall average
        **Options:** 
        ``['all']`` plots all cells and stimulations, 
        ``['allNetStims']`` plots just stimulations, 
        ``['popName1']`` plots a single population, 
        ``['popName1', 'popName2']`` plots multiple populations, 
        ``[120]`` plots a single cell, 
        ``[120, 130]`` plots multiple cells, 
        ``[('popName1', 56)]`` plots a cell from a specific population, 
        ``[('popName1', [0, 1]), ('popName2', [4, 5, 6])]``, plots cells from multiple populations

    statDataIn : dict
        A pre-computed dictionary of stats data to import.
        **Default:** ``{}``
        **Options:** ``<option>`` <description of option>
 
    timeRange : list [start, stop]
        Time range to plot.
        **Default:** 
        ``None`` plots entire time range
        **Options:** ``<option>`` <description of option>
 
    graphType : str
        Whether to plot stats using boxplots or histograms.
        **Default:** ``'boxplot'``
        **Options:** ``'histogram'``

    stats : list
        Statistics to plot.  
        **Default:** ``['rate', 'isicv']``
        **Options:** ``['rate', 'isicv', 'sync', 'pairsync']``

    bins : int or list
        Number of bins (if int) or edges (if list) for histogram 
        **Default:** ``50``
        **Options:** ``<option>`` <description of option>
 
    histlogy : bool
        <Short description of histlogy>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
 
    histlogx : bool
        Whether to make the x axis logarithmic
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
 
    histmin : float
        The minimumum value to include in analyses.
        **Default:** ``0.0``
        **Options:** ``<option>`` <description of option>
 
    density : bool
        If ``True``, weights values by density
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
 
    includeRate0 : bool
        Needs documentation.
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
 
    legendLabels : list?
        Needs documentation.
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    normfit : bool
        Needs documentation.
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
 
    histShading : bool
        Needs documentation.
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>
 
    xlim : list [min, max]
        Sets the x limits of the plot.
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    popColors : dict
        Dictionary with custom color (value) used for each population (key).
        **Default:** ``{}`` uses standard colors
        **Options:** ``<option>`` <description of option>
 
    figSize : list [width, height]
        Size of figure in inches.
        **Default:** ``(10, 8)``
        **Options:** ``<option>`` <description of option>
 
    fontSize : int
        Font size on figure.
        **Default:** ``12``
        **Options:** ``<option>`` <description of option>
 
    dpi : int
        Resolution of figure in dots per inch.
        **Default:** ``100``
        **Options:** ``<option>`` <description of option>
 
    saveData : bool or str
        Whether and where to save the data used to generate the plot. 
        **Default:** ``False`` 
        **Options:** ``True`` autosaves the data,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.pkl'`` and ``'.json'``

    saveFig : bool or str
        Whether and where to save the figure.
        **Default:** ``False``
        **Options:** ``True`` autosaves the figure,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.png'``, ``'.jpg'``, ``'.eps'``, and ``'.tiff'``

    showFig : bool
        Shows the figure if ``True``.
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>
 
    kwargs : <type>
        <Short description of kwargs>
        **Default:** *required*

    Returns
    -------


"""

    from .. import sim
    print('Plotting spike stats...')

    # Set plot style
    colors = []
    params = {
        'axes.labelsize': fontSize,
        'font.size': fontSize,
        'legend.fontsize': fontSize,
        'xtick.labelsize': fontSize,
        'ytick.labelsize': fontSize,
        'text.usetex': False,
        }
    plt.rcParams.update(params)

    xlabels = {'rate': 'Rate (Hz)', 'isicv': 'Irregularity (ISI CV)', 'sync':  'Synchrony', 'pairsync': 'Pairwise synchrony'}

    # Replace 'eachPop' with list of pops
    if 'eachPop' in include: 
        include.remove('eachPop')
        for pop in sim.net.allPops: include.append(pop)

    # time range
    if timeRange is None:
        timeRange = [0, sim.cfg.duration]

    for stat in stats:
        # create fig
        fig, ax1 = plt.subplots(figsize=figSize)
        fontsiz = fontSize
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
                        spkinds,spkts = list(zip(*[(spkgid,spkt) for spkgid,spkt in 
                            zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids]))
                    except:
                        spkinds,spkts = [],[]
                else: 
                    spkinds,spkts = [],[]

                # Add NetStim spikes
                spkts, spkinds = list(spkts), list(spkinds)
                numNetStims = 0
                if 'stims' in sim.allSimData:
                    for netStimLabel in netStimLabels:
                        netStimSpks = [spk for cell,stims in sim.allSimData['stims'].items() \
                        for stimLabel,stimSpks in stims.items() 
                            for spk in stimSpks if stimLabel == netStimLabel]
                        if len(netStimSpks) > 0:
                            lastInd = max(spkinds) if len(spkinds)>0 else 0
                            spktsNew = netStimSpks 
                            spkindsNew = [lastInd+1+i for i in range(len(netStimSpks))]
                            spkts.extend(spktsNew)
                            spkinds.extend(spkindsNew)
                            numNetStims += 1
                try:
                    spkts,spkinds = list(zip(*[(spkt, spkind) for spkt, spkind in zip(spkts, spkinds) 
                        if timeRange[0] <= spkt <= timeRange[1]]))
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
                    statData.append(rates)


                # Inter-spike interval (ISI) coefficient of variation (CV) stats
                elif stat == 'isicv':
                    import numpy as np
                    spkmat = [[spkt for spkind,spkt in zip(spkinds,spkts) if spkind==gid] 
                        for gid in set(spkinds)]
                    isimat = [[t - s for s, t in zip(spks, spks[1:])] for spks in spkmat if len(spks)>10]
                    isicv = [np.std(x) / np.mean(x) if len(x)>0 else 0 for x in isimat] # if len(x)>0] 
                    statData.append(isicv) 


                # synchrony
                elif stat in ['sync', 'pairsync']:
                    try: 
                        import pyspike  
                    except:
                        print("Error: plotSpikeStats() requires the PySpike python package \
                            to calculate synchrony (try: pip install pyspike)")
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
                        

                    statData.append(syncMat)

            colors.append(popColors[subset] if subset in popColors else colorList[iplot%len(colorList)])  # colors in inverse order

        # if 'allCells' included make it black
        if include[0] == 'allCells':
            #if graphType == 'boxplot':
            del colors[0]
            colors.insert(0, (0.5,0.5,0.5))  # 
            #colors.insert(len(include), (0.5,0.5,0.5))  # 
            

        # boxplot
        if graphType == 'boxplot':
            meanpointprops = dict(marker=(5,1,0), markeredgecolor='black', markerfacecolor='white')
            labels = legendLabels if legendLabels else include
            bp=plt.boxplot(statData[::-1], labels=labels[::-1], notch=False, sym='k+', meanprops=meanpointprops,  
                        whis=1.5, widths=0.6, vert=False, showmeans=True, patch_artist=True) #labels[::-1]
            plt.xlabel(xlabel, fontsize=fontsiz)
            plt.ylabel('Population', fontsize=fontsiz) 

            icolor=0
            borderColor = 'k'
            for i in range(0, len(bp['boxes'])):
                icolor = i
                bp['boxes'][i].set_facecolor(colors[::-1][icolor])
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
                        print('    Pop %s rate: mean=%f, std=%f, lognorm mu=%f, lognorm sigma=%f, R=%.2f (p-value=%.2f)' % (popLabel, M, s, mu, sigma, R, p))
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

            # if xlim: ax.set_xlim(xlim)

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

        try:
            plt.tight_layout()
        except:
            pass

        # save figure data
        if saveData:
            figData = {'include': include, 'statData': statData, 'timeRange': timeRange, 'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}

            _saveFigData(figData, saveData, 'spikeStats_' + stat)

        # save figure
        if saveFig: 
            if isinstance(saveFig, basestring):
                filename = saveFig + '_spikeStat_' + graphType + '_' + stat + '.png'
            else:
                filename = sim.cfg.filename + '_spikeStat_' + graphType + '_' + stat + '.png'
            plt.savefig(filename, dpi=dpi)

        # show fig 
        if showFig: _showFigure()

    return fig, {'include': include, 'statData': statData, 'gidsData':gidsData, 'ynormsData':ynormsData}


# -------------------------------------------------------------------------------------------------------------------
## Plot spiking power spectral density
# -------------------------------------------------------------------------------------------------------------------
@exception
def plotRatePSD(include=['eachPop', 'allCells'], timeRange=None, binSize=5, minFreq=1, maxFreq=100, transformMethod='morlet', stepFreq=1, NFFT=256, noverlap=128, smooth=0, norm=False, overlay=True, popColors=None, ylim=None, figSize=(10,8), fontSize=12, lineWidth=1.5, saveData=None, saveFig=None, showFig=True): 
    """
    Function for/to <short description of `netpyne.analysis.spikes.plotRatePSD`>

    Parameters
    ----------
    include : list
        Populations and cells to include in the plot.
        **Default:** 
        ``['eachPop', 'allCells']`` plots histogram for each population and overall average
        **Options:** 
        ``['all']`` plots all cells and stimulations, 
        ``['allNetStims']`` plots just stimulations, 
        ``['popName1']`` plots a single population, 
        ``['popName1', 'popName2']`` plots multiple populations, 
        ``[120]`` plots a single cell, 
        ``[120, 130]`` plots multiple cells, 
        ``[('popName1', 56)]`` plots a cell from a specific population, 
        ``[('popName1', [0, 1]), ('popName2', [4, 5, 6])]``, plots cells from multiple populations

    timeRange : list [start, stop]
        Time range to plot.
        **Default:** 
        ``None`` plots entire time range
        **Options:** ``<option>`` <description of option>
 
    binSize : int
        Size in ms of spike bins.
        **Default:** ``5``
        **Options:** ``<option>`` <description of option>
 
    minFreq : float
        Minimum frequency to show in plot.
        **Default:** ``1``
        **Options:** ``<option>`` <description of option>
 
    maxFreq : float
        Maximum frequency to show in plot.
        **Default:** ``100``
        **Options:** ``<option>`` <description of option>
 
    transformMethod : str
        Sets the transform method.
        **Default:** ``'morlet'`` 
        **Options:** ``'fft'``

    stepFreq : float
        Step frequency for Morlet transform.
        **Default:** ``1``
        **Options:** ``<option>`` <description of option>
 
    NFFT : int
        The number of data points used in each block for the FFT (power of 2)
        **Default:** ``256``
        **Options:** ``<option>`` <description of option>
 
    noverlap : int
        Sets noverlap in FFT transform.
        **Default:** ``128``
        **Options:** ``<option>`` <description of option>
 
    smooth : int
        Window size for smoothing; no smoothing if ``0``.
        **Default:** ``0``
        **Options:** ``<option>`` <description of option>
 
    norm : bool
        Normalize power.
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
 
    overlay : bool
        Whether to overlay plots or use subplots.
        **Default:** ``True`` overlays plots.
        **Options:** ``<option>`` <description of option>
 
    popColors : dict
        Dictionary with custom color (value) used for each population (key).
        **Default:** ``None`` uses standard colors
        **Options:** ``<option>`` <description of option>
 
    ylim : list [min, max]
        Sets the y limits of the plot.
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    figSize : list [width, height]
        Size of figure in inches.
        **Default:** ``(10, 8)``
        **Options:** ``<option>`` <description of option>
 
    fontSize : int
        Font size on figure.
        **Default:** ``12``
        **Options:** ``<option>`` <description of option>
 
    lineWidth : float
        Line width in the plot.
        **Default:** ``1.5``
        **Options:** ``<option>`` <description of option>
 
    saveData : bool or str
        Whether and where to save the data used to generate the plot. 
        **Default:** ``False`` 
        **Options:** ``True`` autosaves the data,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.pkl'`` and ``'.json'``

    saveFig : bool or str
        Whether and where to save the figure.
        **Default:** ``False``
        **Options:** ``True`` autosaves the figure,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.png'``, ``'.jpg'``, ``'.eps'``, and ``'.tiff'``

    showFig : bool
        Shows the figure if ``True``.
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>
 
    Returns
    -------


"""

    from .. import sim

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
    fontsiz = fontSize

    # set font size
    plt.rcParams.update({'font.size': fontSize})
        
    allSignal, allFreqs = [], []

    # Plot separate line for each entry in include
    for iplot,subset in enumerate(include):
        cells, cellGids, netStimLabels = getCellsInclude([subset])   
        numNetStims = 0

        # Select cells to include
        if len(cellGids) > 0:
            try:
                spkinds,spkts = list(zip(*[(spkgid,spkt) for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids]))
            except:
                spkinds,spkts = [],[]
        else: 
            spkinds,spkts = [],[]


        # Add NetStim spikes
        spkts, spkinds = list(spkts), list(spkinds)
        numNetStims = 0
        if 'stims' in sim.allSimData:
            for netStimLabel in netStimLabels:
                netStimSpks = [spk for cell,stims in sim.allSimData['stims'].items() \
                    for stimLabel,stimSpks in stims.items() for spk in stimSpks if stimLabel == netStimLabel]
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

        # Morlet wavelet transform method
        if transformMethod == 'morlet':
            from ..support.morlet import MorletSpec, index2ms

            Fs = 1000.0 / binSize

            morletSpec = MorletSpec(histoCount, Fs, freqmin=minFreq, freqmax=maxFreq, freqstep=stepFreq)
            freqs = morletSpec.f
            spec = morletSpec.TFR
            signal = np.mean(spec, 1)
            ylabel = 'Power'

        # FFT transform method
        elif transformMethod == 'fft':

            Fs = 1000.0/binSize # ACTUALLY DEPENDS ON BIN WINDOW!!! RATE NOT SPIKE!
            power = mlab.psd(histoCount, Fs=Fs, NFFT=NFFT, detrend=mlab.detrend_none, window=mlab.window_hanning, 
                noverlap=noverlap, pad_to=None, sides='default', scale_by_freq=None)

            allSignal = poerwe[0]
            freqs = power[1]

            if smooth:
                signal = _smooth1d(10*np.log10(allSignal), smooth)
            else:
                signal = 10*np.log10(allSignal)

            ylabel = 'Power (dB/Hz)'

        allFreqs.append(freqs)
        allSignal.append(signal)

    if norm:
        vmax = np.max(allSignal)
        for i, s in enumerate(allSignal):
            allSignal[i] = allSignal[i]/vmax

    for iplot,(subset,freqs, signal) in enumerate(zip(include,allFreqs, allSignal)):
        color = popColors[subset] if isinstance(subset, (str, tuple)) and subset in popColors else colorList[iplot % len(colorList)]

        if not overlay: 
            plt.subplot(len(include),1,iplot+1)  # if subplot, create new subplot
            plt.title(str(subset), fontsize=fontsiz)
            color = 'blue'

        plt.plot(freqs[freqs<maxFreq], signal[freqs<maxFreq], linewidth=lineWidth, color=color)

        plt.xlabel('Frequency (Hz)', fontsize=fontsiz)
        plt.ylabel(ylabel, fontsize=fontsiz) # add yaxis in opposite side
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
            plt.plot(0,0,color=color,label=str(subset), linewidth=lineWidth)
        plt.legend(fontsize=fontsiz, loc=1)#, bbox_to_anchor=(1.04, 1), loc=2, borderaxespad=0.)
        maxLabelLen = min(10,max([len(str(l)) for l in include]))
        #plt.subplots_adjust(right=(0.9-0.012*maxLabelLen))


    # save figure data
    if saveData:
        figData = {'histData': histData, 'histT': histoT, 'include': include, 'timeRange': timeRange, 'binSize': binSize,
         'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}
    
        _saveFigData(figData, saveData, 'spikePSD')
 
    # save figure
    if saveFig: 
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename + '_plot_spikePSD.png'
        plt.savefig(filename)

    # show fig 
    if showFig: _showFigure()

    return fig, {'allSignal': allSignal, 'allFreqs':allFreqs}


# -------------------------------------------------------------------------------------------------------------------
## Plot spiking spectrogram
# -------------------------------------------------------------------------------------------------------------------
@exception
def plotRateSpectrogram(include=['allCells', 'eachPop'], timeRange=None, binSize=5, minFreq=1, maxFreq=100, stepFreq=1, NFFT=256, noverlap=128, smooth=0, overlay=True, ylim = None, transformMethod = 'morlet', norm=False, popColors = {}, lineWidth = 1.5, fontSize=12, figSize=(10,8), saveData=None, saveFig=None, showFig=True): 
    """
    Function for/to <short description of `netpyne.analysis.spikes.plotRateSpectrogram`>

    Parameters
    ----------
    include : list
        <Short description of include>
        **Default:** ``['allCells', 'eachPop']``
        **Options:** ``<option>`` <description of option>
 
    timeRange : <``None``?>
        <Short description of timeRange>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    binSize : int
        <Short description of binSize>
        **Default:** ``5``
        **Options:** ``<option>`` <description of option>
 
    minFreq : int
        <Short description of minFreq>
        **Default:** ``1``
        **Options:** ``<option>`` <description of option>
 
    maxFreq : int
        <Short description of maxFreq>
        **Default:** ``100``
        **Options:** ``<option>`` <description of option>
 
    stepFreq : int
        <Short description of stepFreq>
        **Default:** ``1``
        **Options:** ``<option>`` <description of option>
 
    NFFT : int
        <Short description of NFFT>
        **Default:** ``256``
        **Options:** ``<option>`` <description of option>
 
    noverlap : int
        <Short description of noverlap>
        **Default:** ``128``
        **Options:** ``<option>`` <description of option>
 
    smooth : int
        <Short description of smooth>
        **Default:** ``0``
        **Options:** ``<option>`` <description of option>
 
    overlay : bool
        <Short description of overlay>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>
 
    ylim : <``None``?>
        <Short description of ylim>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    transformMethod : str
        <Short description of transformMethod>
        **Default:** ``'morlet'``
        **Options:** ``<option>`` <description of option>
 
    norm : bool
        <Short description of norm>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
 
    popColors : dict
        <Short description of popColors>
        **Default:** ``{}``
        **Options:** ``<option>`` <description of option>
 
    lineWidth : float
        <Short description of lineWidth>
        **Default:** ``1.5``
        **Options:** ``<option>`` <description of option>
 
    fontSize : int
        <Short description of fontSize>
        **Default:** ``12``
        **Options:** ``<option>`` <description of option>
 
    figSize : tuple
        <Short description of figSize>
        **Default:** ``(10, 8)``
        **Options:** ``<option>`` <description of option>
 
    saveData : <``None``?>
        <Short description of saveData>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    saveFig : <``None``?>
        <Short description of saveFig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    showFig : bool
        <Short description of showFig>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>
 
"""

    from .. import sim

    print('Plotting firing rate spectrogram ...')
    
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
    fontsiz = fontSize

    # set font size
    plt.rcParams.update({'font.size': fontSize})
        
    allSignal, allFreqs = [], []

    # Plot separate line for each entry in include
    for iplot,subset in enumerate(include):
        cells, cellGids, netStimLabels = getCellsInclude([subset])   
        numNetStims = 0

        # Select cells to include
        if len(cellGids) > 0:
            try:
                spkinds,spkts = list(zip(*[(spkgid,spkt) for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids]))
            except:
                spkinds,spkts = [],[]
        else: 
            spkinds,spkts = [],[]


        # Add NetStim spikes
        spkts, spkinds = list(spkts), list(spkinds)
        numNetStims = 0
        if 'stims' in sim.allSimData:
            for netStimLabel in netStimLabels:
                netStimSpks = [spk for cell,stims in sim.allSimData['stims'].items() \
                    for stimLabel,stimSpks in stims.items() for spk in stimSpks if stimLabel == netStimLabel]
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

        # Morlet wavelet transform method
        if transformMethod == 'morlet':
            from ..support.morlet import MorletSpec, index2ms

            Fs = 1000.0 / binSize

            morletSpec = MorletSpec(histoCount, Fs, freqmin=minFreq, freqmax=maxFreq, freqstep=stepFreq)
            freqs = morletSpec.f
            spec = morletSpec.TFR
            ylabel = 'Power'
            allSignal.append(spec)
            allFreqs.append(freqs)

    # plotting
    T = timeRange
    for iplot,(subset, freqs, signal) in enumerate(zip(include, allFreqs, allSignal)):

        plt.subplot(len(include),1,iplot+1)  # if subplot, create new subplot
        plt.title(str(subset), fontsize=fontsiz)

        plt.imshow(signal, extent=(np.amin(T), np.amax(T), np.amin(freqs), np.amax(freqs)), origin='lower', interpolation='None', aspect='auto',cmap=plt.get_cmap('viridis'))
        plt.colorbar(label='Power')
        plt.ylabel('Time (ms)')
        plt.ylabel('Hz')
        plt.tight_layout()                

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
            filename = sim.cfg.filename+'_'+'spikeSpectrogram.png'
        plt.savefig(filename)

    # show fig 
    if showFig: _showFigure()

    return fig, {'allSignal': allSignal, 'allFreqs':allFreqs}


#------------------------------------------------------------------------------
# Calculate and print avg pop rates
#------------------------------------------------------------------------------
@exception
def popAvgRates(tranges = None, show = True):
    """
    Function for/to <short description of `netpyne.analysis.spikes.popAvgRates`>

    Parameters
    ----------
    tranges : <``None``?>
        <Short description of tranges>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    show : bool
        <Short description of show>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>
 

    """


    from .. import sim

    avgRates = Dict()

    if not hasattr(sim, 'allSimData') or 'spkt' not in sim.allSimData:
        print('Error: sim.allSimData not available; please call sim.gatherData()')
        return None

    spktsAll = sim.allSimData['spkt']
    spkidsAll = sim.allSimData['spkid']
    
    spkidsList, spktsList = [], []

    if not isinstance(tranges, list):  # True or None
        tranges = [[0, sim.cfg.duration]]

    if isinstance(tranges, list):
    
        # convert single time interval to list
        if not isinstance(tranges[0], (list, tuple)):
            tranges = [tranges]

        # calculate for multiple time intervals
        if isinstance(tranges[0], (list,tuple)):
            for trange in tranges:
                try:
                    spkids, spkts = list(zip(*[(spkid, spkt) for spkid, spkt in zip(spkidsAll, spktsAll) if trange[0] <= spkt <= trange[1]]))
                except:
                    spkids, spkts = [], []
                spkidsList.append(spkids)
                spktsList.append(spkts)

    else:
        return avgRates

    for pop in sim.net.allPops:

        if len(tranges) > 1:
            print('   %s ' % (pop))
            avgRates[pop] = {}
            
        for spkids, spkts, trange in zip(spkidsList, spktsList, tranges):
            numCells = float(len(sim.net.allPops[pop]['cellGids']))
            if numCells > 0:
                
                # single time intervals
                if len(tranges) == 1:
                    tsecs = float((trange[1]-trange[0]))/1000.0
                    avgRates[pop] = len([spkid for spkid in spkids if sim.net.allCells[int(spkid)]['tags']['pop']==pop])/numCells/tsecs
                    print('   %s : %.3f Hz'%(pop, avgRates[pop]))
                
                # multiple time intervals
                else:
                    tsecs = float((trange[1]-trange[0]))/1000.0
                    avgRates[pop]['%d_%d'%(trange[0], trange[1])] = len([spkid for spkid in spkids if sim.net.allCells[int(spkid)]['tags']['pop']==pop])/numCells/tsecs
                    print('        (%d - %d ms): %.3f Hz'%(trange[0], trange[1], avgRates[pop]['%d_%d'%(trange[0], trange[1])]))

    return avgRates


#------------------------------------------------------------------------------
# Calculate f-I curve and analyze features
#------------------------------------------------------------------------------
@exception
def calculatefI():

    from .. import sim
    
    #print('calculating fI')

    times = sim.cfg.analysis['plotfI'].get('times', [0, sim.cfg.duration])
    dur = sim.cfg.analysis['plotfI'].get('dur', sim.cfg.duration)
    onset = sim.cfg.analysis['plotfI'].get('calculateOnset', False)
    durSteady = sim.cfg.analysis['plotfI'].get('durSteady', None)

    sim.allSimData['fI'] = [len([spkt for spkt in sim.allSimData['spkt']
                    if t <= spkt < t + dur]) / (dur / 1000.0) for t in times]  

    if onset: # rate based on inter-spike interval of 1st 2 spikes 
        sim.allSimData['fI_onset'] = []
        for t in times:
            allSpks = [spkt for spkt in sim.allSimData['spkt'] if t <= spkt < t + dur]
            if len(allSpks) >= 2:
                sim.allSimData['fI_onset'].append(1000.0 / (allSpks[1] - allSpks[0]))
            else:
                sim.allSimData['fI_onset'].append(0.0)
    
    if durSteady: # rate based on the last 'dur' ms
        sim.allSimData['fI_steady'] = [len([spkt for spkt in sim.allSimData['spkt']
                    if t + dur - durSteady <= spkt < t + dur]) / (durSteady / 1000.0) for t in times] 

    # calculate features of fI curve
    calculateFeatures = sim.cfg.analysis['plotfI']['calculateFeatures']
    threshold = sim.net.params.defaultThreshold
    v = sim.allSimData['V_soma']['cell_0']
    dt = sim.cfg.recordStep

    # calculate latency to 1st spike peak
    if 'latencyPeak1' in calculateFeatures:
        # find peaks
        sim.allSimData['fI_latencyPeak1'] = []
        for time in times:
            v1 = v[time:time + dur]
            vpeak = np.max(v1)
            if vpeak > threshold:
                tpeak = np.argmax(v1)
                sim.allSimData['fI_latencyPeak1'].append(abs(tpeak - time)*dt)
            else:
                sim.allSimData['fI_latencyPeak1'].append(-1.)

    # calculate interspike  to 1st spike peak
    if 'ISIPeak1' in calculateFeatures:
        
        pass

    # calculate interspike  to 1st spike peak
    if 'ampSpike1' in calculateFeatures: 
        pass

    # calculate interspike  to 1st spike peak
    if 'ampSpike2' in calculateFeatures: 
        pass

#------------------------------------------------------------------------------
# Calculate and plot f-I curve
#------------------------------------------------------------------------------
@exception
def plotfI(amps, times, dur, targetRates=[], calculateOnset=False, targetRatesOnset=[], durSteady=None, targetRatesSteady=[], saveFig=None, showFig=True):
    """
    Function to plot frequency-current (fI) relationship

    Parameters
    ----------
    amps : <type>
        <Short description of amps>
        **Default:** *required*

    times : <type>
        <Short description of times>
        **Default:** *required*

    dur : <type>
        <Short description of dur>
        **Default:** *required*

    targetRates : list
        <Short description of targetRates>
        **Default:** ``[]``
        **Options:** ``<option>`` <description of option>
 
    calculateOnset : bool
        <Short description of calculateOnset>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
 
    targetRatesOnset : list
        <Short description of targetRatesOnset>
        **Default:** ``[]``
        **Options:** ``<option>`` <description of option>
 
    durSteady : <``None``?>
        <Short description of durSteady>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    targetRatesSteady : list
        <Short description of targetRatesSteady>
        **Default:** ``[]``
        **Options:** ``<option>`` <description of option>
 
    saveFig : <``None``?>
        <Short description of saveFig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    showFig : bool
        <Short description of showFig>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    Returns
    -------
    (fig, dict)
        A tuple consisting of the Matplotlib figure handle and a dictionary containing the plot data

    See Also
    --------
    calculatefI :
 

    """

    from .. import sim 

    outData = {}
    
    fig = plt.figure(figsize=(10, 6))
        
    if not 'fI_steady' in sim.allSimData:
        fI = sim.allSimData['fI']
        plt.plot(amps, fI, label='Model', linewidth=2, marker='o')
        if targetRates:
            plt.plot(amps, targetRates, label = 'Experiment', linestyle = 'dotted', marker='o')
        plt.xlabel('Current amplitude (nA)')
        plt.ylabel('Rate (Hz)')
        plt.legend()
        outData['fI'] = fI

    if 'fI_onset' in sim.allSimData:
        fI_onset = sim.allSimData['fI_onset']
        plt.plot(amps, fI_onset, label='Model (onset)', linewidth=2, marker='o')
        if targetRatesOnset:
            plt.plot(amps, targetRatesOnset, label = 'Experiment (onset)', linestyle = 'dotted', marker='o')
        plt.xlabel('Current amplitude (nA)')
        plt.ylabel('Rate (Hz)')
        plt.legend()
        outData['fI_onset'] = fI_onset

    if 'fI_steady' in sim.allSimData:
        fI_steady = sim.allSimData['fI_steady']
        plt.plot(amps, fI_steady, label='Model (steady)', linewidth=2, marker='o')
        if targetRatesSteady:
            plt.plot(amps, targetRatesSteady, label = 'Experiment (steady)', linestyle = 'dotted', marker='o')
        plt.xlabel('Current amplitude (nA)')
        plt.ylabel('Rate (Hz)')
        plt.legend()
        outData['fI_steady'] = fI_steady

    # save figure
    if saveFig: 
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'fI.png'
        plt.savefig(filename)

    # show fig 
    if showFig: _showFigure()

    return fig, outData


