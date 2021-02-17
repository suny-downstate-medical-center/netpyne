"""
Module for analysis of spiking-related results

"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()

from builtins import round
from builtins import open
from builtins import range

try:
    to_unicode = unicode
except NameError:
    to_unicode = str
try:
    basestring
except NameError:
    basestring = str

import pandas as pd
from numbers import Number
from .utils import exception, getCellsInclude, getSpktSpkid, saveData


#@exception
def prepareRaster(include=['allCells'], sim=None, timeRange=None, maxSpikes=1e8, orderBy='gid', popRates=True, saveData=False, fileName=None, fileDesc=None, fileType=None, **kwargs):
    """
    Function to prepare data for creating a raster plot

    """

    print('Preparing raster...')

    if not sim:
        from .. import sim

    # Select cells to include
    cells, cellGids, netStimLabels = getCellsInclude(include)

    df = pd.DataFrame.from_records(cells)
    df = pd.concat([df.drop('tags', axis=1), pd.DataFrame.from_records(df['tags'].tolist())], axis=1)

    keep = ['pop', 'gid', 'conns']

    # if orderBy property doesn't exist or is not numeric, use gid
    if isinstance(orderBy, basestring) and orderBy not in cells[0]['tags']:  
        orderBy = 'gid'
    elif orderBy == 'pop':
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

    # preserves original ordering:
    popLabels = [pop for pop in sim.net.allPops if pop in df['pop'].unique()] 
    
    if netStimLabels: 
        popLabels.append('NetStims')
    
    if len(cellGids) > 0:
        try:
            sel, spkts, spkgids = getSpktSpkid(cellGids=[] if include == ['allCells'] else cellGids, timeRange=timeRange) # using [] is faster for all cells
        except:
            import sys
            print((sys.exc_info()))
            spkgids, spkts = [], []
            sel = pd.DataFrame(columns=['spkt', 'spkid'])
        
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
    if (len(sel) > maxSpikes):
        print(('  Showing only the first %i out of %i spikes' % (maxSpikes, len(sel)))) # Limit num of spikes
        if numNetStims: # sort first if have netStims
            sel = sel.sort_values(by='spkt')
        sel = sel.iloc[:maxSpikes]
        timeRange[1] =  sel['spkt'].max()

    # Plot stats
    gidPops = df['pop'].tolist()
    popNumCells = [float(gidPops.count(pop)) for pop in popLabels] if numCellSpks else [0] * len(popLabels)
    totalSpikes = len(sel)
    totalConnections = sum([len(conns) for conns in df['conns']])
    numCells = len(cells)
    firingRate = float(totalSpikes)/(numCells+numNetStims)/(timeRange[1]-timeRange[0])*1e3 if totalSpikes>0 else 0
    connsPerCell = totalConnections/float(numCells) if numCells>0 else 0

    legendLabels = []
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

        legendLabels = [popLabel + ' (%.3g Hz)' % (avgRates[popLabel]) for popLabel in popLabels if popLabel in avgRates]

    axisArgs = {'xlabel': 'Time (ms)', 
                'ylabel': ylabelText, 
                'title': 'cells=%i   syns/cell=%0.1f   rate=%0.1f Hz' % (numCells, connsPerCell, firingRate)}

    figData = {'spkTimes': sel['spkt'].tolist(), 'spkInds': sel['spkind'].tolist(), 'cellGids': cellGids, 'numNetStims': numNetStims, 'include': include, 'timeRange': timeRange, 'maxSpikes': maxSpikes, 'orderBy': orderBy, 'popLabels': popLabels, 'gidPops': gidPops, 'axisArgs': axisArgs, 'legendLabels': legendLabels}

    if saveData:
        saveData(figData, fileName=fileName, fileDesc=fileDesc, fileType=fileType, sim=sim)
    
    return figData



#@exception
def prepareSpikeHist(include=['eachPop', 'allCells'], sim=None, timeRange=None, binSize=5, overlay=True, graphType='line', measure='rate', norm=False, smooth=None, filtFreq=None, filtOrder=3, axis=True, popColors=None, figSize=(10,8), dpi=100, saveData=None, saveFig=None, showFig=True, **kwargs):
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
    
    if not sim:
        from .. import sim
    
    from ..support.scalebar import add_scalebar

    print('Preparing spike histogram...')

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


    figData = {'histoData': histoData, 'histoT': histoT, 'include': include, 'timeRange': timeRange, 'binSize': binSize, 'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}










