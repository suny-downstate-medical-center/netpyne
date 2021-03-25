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
import numpy as np
from numbers import Number
from .utils import exception, getInclude, getSpktSpkid
from .utils import saveData as saveFigData
from ..support.scalebar import add_scalebar


#@exception
def prepareSpikeData(include=['allCells'], sim=None, timeRange=None, maxSpikes=1e8, orderBy='gid', popRates=True, saveData=False, fileName=None, fileDesc=None, fileType=None, fileDir=None, **kwargs):
    """
    Function to prepare data for creating a raster plot, a spike histogram plot, ...

    """

    print('Preparing spike data...')

    if not sim:
        from .. import sim

    # Select cells to include
    cells, cellGids, netStimLabels = getInclude(include)

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
        print(netStimLabel)
        stims = sim.allSimData['stims'].items()
        print(stims)
        netStimSpks = [spk for cell, stims in sim.allSimData['stims'].items() for stimLabel, stimSpks in stims.items() for spk in stimSpks if stimLabel == netStimLabel]
        print(netStimSpks)
        if len(netStimSpks) > 0:
            # lastInd = max(spkinds) if len(spkinds)>0 else 0
            lastInd = sel['spkind'].max() if len(sel['spkind']) > 0 else 0
            spktsNew = netStimSpks
            spkindsNew = [lastInd+1+i for i in range(len(netStimSpks))]
            ns = pd.DataFrame(list(zip(spktsNew, spkindsNew)), columns=['spkt', 'spkind'])
            ns['spkgidColor'] = popColors['netStims']
            sel = pd.concat([sel, ns])
            numNetStims += 1
        
    if len(cellGids) > 0 and numNetStims:
        ylabelText = ylabelText + ' and NetStims (at the end)'
    elif numNetStims:
        ylabelText = ylabelText + 'NetStims'

    if numCellSpks + numNetStims == 0:
        print('No spikes available to plot raster')
        return None

    # Time Range
    if timeRange == [0, sim.cfg.duration]:
        pass
    elif timeRange is None:
        timeRange = [0, sim.cfg.duration]
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
    conns = df['conns'].tolist()
    popNumCells = [float(gidPops.count(pop)) for pop in popLabels] if numCellSpks else [0] * len(popLabels)
    totalSpikes = len(sel)
    cellNumConns = [len(conn) for conn in conns]
    popNumConns = [sum([cellNumConn for cellIndex, cellNumConn in enumerate(cellNumConns) if gidPops[cellIndex] == pop]) for pop in popLabels]
    totalConnections = sum([len(conns) for conns in df['conns']])
    numCells = len(cells)
    firingRate = float(totalSpikes)/(numCells+numNetStims)/(timeRange[1]-timeRange[0])*1e3 if totalSpikes>0 else 0
    connsPerCell = totalConnections/float(numCells) if numCells>0 else 0
    popConnsPerCell = [popNumConns[popIndex]/popNumCells[popIndex] for popIndex, pop in enumerate(popLabels)]

    title = 'Raster plot of spiking'
    legendLabels = []
    
    if popRates:
        avgRates = {}
        tsecs = (timeRange[1]-timeRange[0])/1e3
        for i, (pop, popNum) in enumerate(zip(popLabels, popNumCells)):
            if numCells > 0 and pop != 'NetStims':
                if numCellSpks == 0:
                    avgRates[pop] = 0
                else:
                    avgRates[pop] = len([spkid for spkid in sel['spkind'].iloc[:numCellSpks-1] if df['pop'].iloc[int(spkid)]==pop])/popNum/tsecs
        if numNetStims:
            popNumCells[-1] = numNetStims
            avgRates['NetStims'] = len([spkid for spkid in sel['spkind'].iloc[numCellSpks:]])/numNetStims/tsecs

        if popRates == 'minimal':
            legendLabels = [popLabel + ' (%.3g Hz)' % (avgRates[popLabel]) for popIndex, popLabel in enumerate(popLabels) if popLabel in avgRates]
            title = 'cells: %i   syn/cell: %0.1f   rate: %0.1f Hz' % (numCells, connsPerCell, firingRate)
        else:
            legendLabels = [popLabel + '\n  cells: %i\n  syn/cell: %0.1f\n  rate: %.3g Hz' % (popNumCells[popIndex], popConnsPerCell[popIndex], avgRates[popLabel]) for popIndex, popLabel in enumerate(popLabels) if popLabel in avgRates]
            title = 'cells: %i   syn/cell: %0.1f   rate: %0.1f Hz' % (numCells, connsPerCell, firingRate)

        if 'title' in kwargs:
            title = kwargs['title']

    axisArgs = {'xlabel': 'Time (ms)', 
                'ylabel': ylabelText, 
                'title': title}
    
    spikeData = {'spkTimes': sel['spkt'].tolist(), 'spkInds': sel['spkind'].tolist(), 'popNumCells': popNumCells, 'popLabels': popLabels, 'numNetStims': numNetStims, 'include': include, 'timeRange': timeRange, 'maxSpikes': maxSpikes, 'orderBy': orderBy, 'axisArgs': axisArgs, 'legendLabels': legendLabels}

    if saveData:
        saveFigData(spikeData, fileName=fileName, fileDesc='spike_data', fileType=fileType, fileDir=fileDir, sim=sim)
    
    return spikeData



def prepareRaster(include=['allCells'], sim=None, timeRange=None, maxSpikes=1e8, orderBy='gid', popRates=True, saveData=False, fileName=None, fileDesc=None, fileType=None, fileDir=None, **kwargs):
    """
    Function to prepare data for creating a raster plot

    """

    figData = prepareSpikeData(include=include, sim=sim, timeRange=timeRange, maxSpikes=maxSpikes, orderBy=orderBy, popRates=popRates, saveData=saveData, fileName=fileName, fileDesc=fileDesc, fileType=fileType, fileDir=fileDir, **kwargs)

    # figData = {'spkTimes': sel['spkt'].tolist(), 'spkInds': sel['spkind'].tolist(), 'popNumCells': popNumCells, 'popLabels': popLabels, 'numNetStims': numNetStims, 'include': include, 'timeRange': timeRange, 'maxSpikes': maxSpikes, 'orderBy': orderBy, 'axisArgs': axisArgs, 'legendLabels': legendLabels}

    return figData







def prepareSpikeHist(
    include=['eachPop', 'allCells'], 
    sim=None, 
    timeRange=None,
    maxSpikes=1e8,
    popRates=True,
    saveData=False,
    fileName=None, 
    fileDesc=None, 
    fileType=None, 
    fileDir=None,

    binSize=5, 
    overlay=True, 
    graphType='line', 
    measure='rate', 
    norm=False, 
    smooth=None, 
    filtFreq=None, 
    filtOrder=3, 
     
    **kwargs):
    """
    Function to prepare data for creating a spike histogram plot

    """

    figData = prepareSpikeData(include=include, sim=sim, timeRange=timeRange, maxSpikes=maxSpikes, orderBy='gid', popRates=popRates, saveData=saveData, fileName=fileName, fileDesc=fileDesc, fileType=fileType, fileDir=fileDir, **kwargs)

    # figData = {'spkTimes': sel['spkt'].tolist(), 'spkInds': sel['spkind'].tolist(), 'popNumCells': popNumCells, 'popLabels': popLabels, 'numNetStims': numNetStims, 'include': include, 'timeRange': timeRange, 'maxSpikes': maxSpikes, 'orderBy': orderBy, 'axisArgs': axisArgs, 'legendLabels': legendLabels}

    # axisArgs = {'xlabel': 'Time (ms)', 
    #             'ylabel': ylabelText, 
    #             'title': title}

    #figData['axisArgs']['title'] = 'Spike histogram plot'
    figData['axisArgs']['ylabel'] = 'Number of spikes'

    return figData









#@exception
def prepareSpikeHist_OLD(
    include=['eachPop', 'allCells'], 
    sim=None, 
    timeRange=None,
    maxSpikes=1e8,
    saveData=False,
    fileName=None, 
    fileDesc=None, 
    fileType=None, 
    fileDir=None,

    binSize=5, 
    overlay=True, 
    graphType='line', 
    measure='rate', 
    norm=False, 
    smooth=None, 
    filtFreq=None, 
    filtOrder=3, 
     
    **kwargs):
    """
    Function to prepare data for creating a spike histogram plot

    """
    
    if not sim:
        from .. import sim
    
    


    # Replace 'eachPop' with list of pops
    if 'eachPop' in include:
        include.remove('eachPop')
        for pop in sim.net.allPops: 
            include.append(pop)

    # Measure
    if measure == 'rate':
        if norm:
            ylabelText = 'Normalized firing rate'
        else:
            ylabelText = 'Avg cell firing rate (Hz)'
    elif measure == 'count':
        if norm:
            ylabelText = 'Normalized spike count'
        else:
            ylabelText = 'Spike count'
    else:
        print('Invalid measure: %s', (measure))
        return

    # time range
    if timeRange is None:
        timeRange = [0, sim.cfg.duration]

    histoData = []

    # Plot separate line for each entry in include
    for iplot, subset in enumerate(include):
        if isinstance(subset, list):
            cells, cellGids, netStimLabels = getInclude(subset)
        else:
            cells, cellGids, netStimLabels = getInclude([subset])
        numNetStims = 0

        # Select cells to include
        if len(cellGids) > 0:
            try:
                spkinds, spkts = list(zip(*[(spkgid, spkt) for spkgid, spkt in zip(sim.allSimData['spkid'], sim.allSimData['spkt']) if spkgid in cellGids]))
            except:
                spkinds, spkts = [], []
        else:
            spkinds, spkts = [], []

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

        histo = np.histogram(spkts, bins=np.arange(timeRange[0], timeRange[1], binSize))
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

    legendLabels = []
    title = 'Histogram Plot of Spiking'
    if 'title' in kwargs:
            title = kwargs['title']

    figData = {'histoData': histoData, 'histoT': histoT, 'include': include, 'timeRange': timeRange, 'binSize': binSize}

    axisArgs = {'xlabel': 'Time (ms)', 
                'ylabel': ylabelText, 
                'title': title}

    if saveData:
        saveFigData(figData, fileName=fileName, fileDesc='hist_data', fileType=fileType, fileDir=fileDir, sim=sim)
    
    return figData










