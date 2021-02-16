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

from .utils import colorList, exception, getCellsInclude, getSpktSpkid
import pandas as pd


#@exception
def prepareRaster(popColors=None, include=['allCells'], sim=None, timeRange=None, maxSpikes=1e8, orderBy='gid', popRates=True, saveData=None, **kwargs):
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

    popLabels = [pop for pop in sim.net.allPops if pop in df['pop'].unique()] # preserves original ordering
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

    popLabelRates = [popLabel + ' (%.3g Hz)' % (avgRates[popLabel]) for popLabel in popLabels if popLabel in avgRates]

    # switch spkgidcolor to pop


    figData = {'spkTimes': sel['spkt'].tolist(), 'spkInds': sel['spkind'].tolist(), 'spkColors': sel['spkgidColor'].tolist(), 'cellGids': cellGids, 'numNetStims': numNetStims, 'include': include, 'timeRange': timeRange, 'maxSpikes': maxSpikes, 'orderBy': orderBy, 'popLabels': popLabels, 'popLabelRates': popLabelRates}
    

    # save figure data
    if saveData:
        # Need to replace _saveFigData
        _saveFigData(figData, saveData, 'raster')

    return figData