"""
analysis.py

Functions to plot and analyse results

Contributors: salvadordura@gmail.com
"""

from matplotlib.pylab import nanmax, nanmin, errstate, bar, histogram, floor, ceil, yticks, arange, gca, scatter, figure, hold, subplot, axes, shape, imshow, \
    colorbar, plot, xlabel, ylabel, title, xlim, ylim, clim, show, zeros, legend, savefig, psd, ion, subplots_adjust, subplots, tight_layout
from matplotlib import gridspec
from scipy import size, array, linspace, ceil
from numbers import Number
import math

import sim

import warnings
warnings.filterwarnings("ignore")

######################################################################################################################################################
## Wrapper to run analysis functions in simConfig
######################################################################################################################################################
def plotData ():
    ## Plotting
    if sim.rank == 0:
        sim.timing('start', 'plotTime')

        # Call analysis functions specified by user
        for funcName, kwargs in sim.cfg.analysis.iteritems():
            if kwargs == True: kwargs = {}
            elif kwargs == False: continue
            func = getattr(sim.analysis, funcName)  # get pointer to function
            func(**kwargs)  # call function with user arguments

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
        show(block=False)
    except:
        show()


######################################################################################################################################################
## Save figure data
######################################################################################################################################################
def _saveFigData(figData, fileName, type=''):
    if not isinstance(fileName, str):
        fileName = sim.cfg.filename+'_'+type+'.pkl'

    fileName = fileName.split('.')
    ext = fileName[1] if len(fileName) > 1 else 'pkl'

    if ext == 'pkl': # save to pickle
        import pickle
        print('Saving figure data as %s ... ' % (fileName[0]+'.pkl'))
        with open(fileName[0]+'.pkl', 'wb') as fileObj:
            pickle.dump(figData, fileObj)

    elif ext == 'json':  # save to json
        import json
        print('Saving figure data as %s ... ' % (fileName[0]+'.json '))
        with open(fileName[0]+'.json', 'w') as fileObj:
            json.dump(figData, fileObj)
    else: 
        print 'File extension to save figure data not recognized: %s'%(ext)


######################################################################################################################################################
## Synchrony measure
######################################################################################################################################################
def syncMeasure ():
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
    allCells = sim.net.allCells
    allNetStimPops = [popLabel for popLabel,pop in sim.net.allPops.iteritems() if pop['tags']['cellModel']=='NetStim']
    cellGids = []
    cells = []
    netStimPops = []
    for condition in include:
        if condition == 'all':  # all cells + Netstims 
            cellGids = [c['gid'] for c in allCells]
            cells = list(allCells)
            netStimPops = list(allNetStimPops)
            return cells, cellGids, netStimPops

        elif condition == 'allCells':  # all cells 
            cellGids = [c['gid'] for c in allCells]
            cells = list(allCells)

        elif condition == 'allNetStims':  # all cells + Netstims 
            netStimPops = list(allNetStimPops)

        elif isinstance(condition, int):  # cell gid 
            cellGids.append(condition)
        
        elif isinstance(condition, str):  # entire pop
            if condition in allNetStimPops:
                netStimPops.append(condition)
            else:
                cellGids.extend([c['gid'] for c in allCells if c['tags']['popLabel']==condition])
        
        elif isinstance(condition, tuple):  # subset of a pop with relative indices
            cellsPop = [c['gid'] for c in allCells if c['tags']['popLabel']==condition[0]]
            if isinstance(condition[1], list):
                cellGids.extend([gid for i,gid in enumerate(cellsPop) if i in condition[1]])
            elif isinstance(condition[1], int):
                cellGids.extend([gid for i,gid in enumerate(cellsPop) if i==condition[1]])

    cellGids = list(set(cellGids))  # unique values
    cells = [cell for cell in allCells if cell['gid'] in cellGids]
    cells = sorted(cells, key=lambda k: k['gid'])

    return cells, cellGids, netStimPops


######################################################################################################################################################
## Raster plot 
######################################################################################################################################################
def plotRaster (include = ['allCells'], timeRange = None, maxSpikes = 1e8, orderBy = 'gid', orderInverse = False, spikeHist = None, 
        spikeHistBin = 5, syncLines = False, figSize = (10,8), saveData = None, saveFig = None, showFig = True): 
    ''' 
    Raster plot of network cells 
        - include (['all',|'allCells',|'allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Cells to include (default: 'allCells')
        - timeRange ([start:stop]): Time range of spikes shown; if None shows all (default: None)
        - maxSpikes (int): maximum number of spikes that will be plotted  (default: 1e8)
        - orderBy ('gid'|'y'|'ynorm'|...): Unique numeric cell property to order y-axis by, e.g. 'gid', 'ynorm', 'y' (default: 'gid')
        - orderInverse (True|False): Invert the y-axis order (default: False)
        - spikeHist (None|'overlay'|'subplot'): overlay line over raster showing spike histogram (spikes/bin) (default: False)
        - spikeHistBin (int): Size of bin in ms to use for histogram (default: 5)
        - syncLines (True|False): calculate synchorny measure and plot vertical lines for each spike to evidence synchrony (default: False)
        - figSize ((width, height)): Size of figure (default: (10,8))
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure; 
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure (default: None)
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)

        - Returns figure handle
    '''

    print('Plotting raster...')

    colorList = [[0.42,0.67,0.84], [0.90,0.76,0.00], [0.42,0.83,0.59], [0.90,0.32,0.00],
                [0.34,0.67,0.67], [0.90,0.59,0.00], [0.42,0.82,0.83], [1.00,0.85,0.00],
                [0.33,0.67,0.47], [1.00,0.38,0.60], [0.57,0.67,0.33], [0.5,0.2,0.0],
                [0.71,0.82,0.41], [0.0,0.2,0.5]] 

    # Select cells to include
    cells, cellGids, netStimPops = getCellsInclude(include)
    selectedPops = [cell['tags']['popLabel'] for cell in cells]+netStimPops
    popLabels = [pop for pop in sim.net.allPops if pop in selectedPops] # preserves original ordering
    popColors = {popLabel: colorList[ipop%len(colorList)] for ipop,popLabel in enumerate(popLabels)} # dict with color for each pop
    if len(cellGids) > 0:
        gidColors = {cell['gid']: popColors[cell['tags']['popLabel']] for cell in cells}  # dict with color for each gid
        try:
            spkgids,spkts = zip(*[(spkgid,spkt) for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids])
        except:
            print 'No spikes available to plot raster'
            return None
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

        if orderInverse: yorder.reverse()

        sortedGids = {gid:i for i,(y,gid) in enumerate(sorted(zip(yorder,cellGids)))}
        spkinds = [sortedGids[gid]  for gid in spkgids]

    else:
        spkts = []
        spkinds = []
        spkgidColors = []
        ylabelText = ''

    # Add NetStim spikes
    spkts,spkgidColors = list(spkts), list(spkgidColors)
    numNetStims = 0
    for netStimPop in netStimPops:
        cellStims = [cellStim for cell,cellStim in sim.allSimData['stims'].iteritems() if netStimPop in cellStim]
        if len(cellStims) > 0:
            lastInd = max(spkinds) if len(spkinds)>0 else 0
            spktsNew = [spkt for cellStim in cellStims for spkt in cellStim[netStimPop] ]
            spkindsNew = [lastInd+1+i for i,cellStim in enumerate(cellStims) for spkt in cellStim[netStimPop]]
            spkts.extend(spktsNew)
            spkinds.extend(spkindsNew)
            for i in range(len(spktsNew)): 
                spkgidColors.append(popColors[netStimPop])
            numNetStims += len(cellStims)
    if len(cellGids)>0 and numNetStims: 
        ylabelText = ylabelText + ' and NetStims (at the end)'
    elif numNetStims:
        ylabelText = ylabelText + 'NetStims'

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
        histo = histogram(spkts, bins = arange(timeRange[0], timeRange[1], spikeHistBin))
        histoT = histo[1][:-1]+spikeHistBin/2
        histoCount = histo[0]

    # Plot spikes
    fig,ax1 = subplots(figsize=figSize)
    fontsiz = 12
    
    if spikeHist == 'subplot':
        gs = gridspec.GridSpec(2, 1,height_ratios=[2,1])
        ax1=subplot(gs[0])
    ax1.scatter(spkts, spkinds, 10, linewidths=2, marker='|', color = spkgidColors) # Create raster  
    
    # Plot stats
    totalSpikes = len(spkts)   
    totalConnections = sum([len(cell['conns']) for cell in cells])   
    numCells = len(cells)
    firingRate = float(totalSpikes)/numCells/(timeRange[1]-timeRange[0])*1e3 if totalSpikes>0 else 0# Calculate firing rate 
    connsPerCell = totalConnections/float(numCells) if numCells>0 else 0 # Calculate the number of connections per cell
    
    # Plot synchrony lines 
    if syncLines: 
        for spkt in spkts:
            ax1.plot((spkt, spkt), (0, len(cells)+numNetStims), 'r-', linewidth=0.1)
        title('cells=%i syns/cell=%0.1f rate=%0.1f Hz sync=%0.2f' % (numCells,connsPerCell,firingRate,syncMeasure()), fontsize=fontsiz)
    else:
        title('cells=%i syns/cell=%0.1f rate=%0.1f Hz' % (numCells,connsPerCell,firingRate), fontsize=fontsiz)

    # Plot spike hist
    if spikeHist == 'overlay':
        ax2 = ax1.twinx()
        ax2.plot (histoT, histoCount, linewidth=0.5)
        ax2.set_ylabel('Spike count', fontsize=fontsiz) # add yaxis label in opposite side
    elif spikeHist == 'subplot':
        ax2=subplot(gs[1])
        plot (histoT, histoCount, linewidth=1.0)
        ax2.set_xlabel('Time (ms)', fontsize=fontsiz)
        ax2.set_ylabel('Spike count', fontsize=fontsiz)

    # Axis
    ax1.set_xlabel('Time (ms)', fontsize=fontsiz)
    ax1.set_ylabel(ylabelText, fontsize=fontsiz)
    ax1.set_xlim(timeRange)
    ax1.set_ylim(-1, len(cells)+numNetStims+1)    

    # Add legend
    for popLabel in popLabels:
        plot(0,0,color=popColors[popLabel],label=popLabel)
    legend(fontsize=fontsiz, bbox_to_anchor=(1.04, 1), loc=2, borderaxespad=0.)
    maxLabelLen = max([len(l) for l in popLabels])
    subplots_adjust(right=(0.9-0.012*maxLabelLen))

    # save figure data
    if saveData:
        figData = {'spkTimes': spkts, 'spkInds': spkinds, 'spkColors': spkgidColors, 'cellGids': cellGids, 'sortedGids': sortedGids, 'numNetStims': numNetStims, 
        'include': include, 'timeRange': timeRange, 'maxSpikes': maxSpikes, 'orderBy': orderBy, 'orderInverse': orderInverse, 'spikeHist': spikeHist,
        'syncLines': syncLines}

        _saveFigData(figData, saveData, 'raster')
 
    # save figure
    if saveFig: 
        if isinstance(saveFig, str):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'raster.png'
        savefig(filename)

    # show fig 
    if showFig: _showFigure()

    return fig


######################################################################################################################################################
## Plot spike histogram
######################################################################################################################################################
def plotSpikeHist (include = ['allCells', 'eachPop'], timeRange = None, binSize = 5, overlay=True, graphType='line', yaxis = 'rate', 
    figSize = (10,8), saveData = None, saveFig = None, showFig = True): 
    ''' 
    Plot spike histogram
        - include (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): List of data series to include. 
            Note: one line per item, not grouped (default: ['allCells', 'eachPop'])
        - timeRange ([start:stop]): Time range of spikes shown; if None shows all (default: None)
        - binSize (int): Size in ms of each bin (default: 5)
        - overlay (True|False): Whether to overlay the data lines or plot in separate subplots (default: True)
        - graphType ('line'|'bar'): Type of graph to use (line graph or bar plot) (default: 'line')
        - yaxis ('rate'|'count'): Units of y axis (firing rate in Hz, or spike count) (default: 'rate')
        - figSize ((width, height)): Size of figure (default: (10,8))
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure;
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure;
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)

        - Returns figure handle
    '''

    print('Plotting spike histogram...')

    colorList = [[0.42,0.67,0.84], [0.90,0.76,0.00], [0.42,0.83,0.59], [0.90,0.32,0.00],
                [0.34,0.67,0.67], [0.90,0.59,0.00], [0.42,0.82,0.83], [1.00,0.85,0.00],
                [0.33,0.67,0.47], [1.00,0.38,0.60], [0.57,0.67,0.33], [0.5,0.2,0.0],
                [0.71,0.82,0.41], [0.0,0.2,0.5]] 

    
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
    fig,ax1 = subplots(figsize=figSize)
    fontsiz = 12
    
    # Plot separate line for each entry in include
    for iplot,subset in enumerate(include):
        cells, cellGids, netStimPops = getCellsInclude([subset])
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
        for netStimPop in netStimPops:
            cellStims = [cellStim for cell,cellStim in sim.allSimData['stims'].iteritems() if netStimPop in cellStim]
            if len(cellStims) > 0:
                lastInd = max(spkinds) if len(spkinds)>0 else 0
                spktsNew = [spkt for cellStim in cellStims for spkt in cellStim[netStimPop] ]
                spkindsNew = [lastInd+1+i for i,cellStim in enumerate(cellStims) for spkt in cellStim[netStimPop]]
                spkts.extend(spktsNew)
                spkinds.extend(spkindsNew)
                numNetStims += len(cellStims)

        histo = histogram(spkts, bins = arange(timeRange[0], timeRange[1], binSize))
        histoT = histo[1][:-1]+binSize/2
        histoCount = histo[0] 

        histData.append(histoCount)

        if yaxis=='rate': histoCount = histoCount * (1000.0 / binSize) / (len(cellGids)+numNetStims) # convert to firing rate

        color = colorList[iplot%len(colorList)]

        if not overlay: 
            subplot(len(include),1,iplot+1)  # if subplot, create new subplot
            title (str(subset))
            color = 'blue'
   
        if graphType == 'line':
            plot (histoT, histoCount, linewidth=1.0, color = color)
        elif graphType == 'bar':
            bar(histoT, histoCount, width = binSize, color = color)

        xlabel('Time (ms)', fontsize=fontsiz)
        ylabel(yaxisLabel, fontsize=fontsiz) # add yaxis in opposite side
        ax1.set_xlim(timeRange)

    try:
        tight_layout()
    except:
        pass

    # Add legend
    if overlay:
        for i,subset in enumerate(include):
            plot(0,0,color=colorList[i%len(colorList)],label=str(subset))
        legend(fontsize=fontsiz, bbox_to_anchor=(1.04, 1), loc=2, borderaxespad=0.)
        maxLabelLen = min(10,max([len(str(l)) for l in include]))
        subplots_adjust(right=(0.9-0.012*maxLabelLen))


    # save figure data
    if saveData:
        figData = {'histData': histData, 'histT': histoT, 'include': include, 'timeRange': timeRange, 'binSize': binSize,
         'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}
    
        _saveFigData(figData, saveData, 'spikeHist')
 
    # save figure
    if saveFig: 
        if isinstance(saveFig, str):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'spikeHist.png'
        savefig(filename)

    # show fig 
    if showFig: _showFigure()

    return fig

        

######################################################################################################################################################
## Plot recorded cell traces (V, i, g, etc.)
######################################################################################################################################################
def plotTraces (include = None, timeRange = None, overlay = False, oneFigPer = 'cell', rerun = False,
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
        - figSize ((width, height)): Size of figure (default: (10,8))
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure; 
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure;
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)

        - Returns figure handles
    '''

    print('Plotting recorded cell traces ...')

    if include is None: include = [] # If not defined, initialize as empty list

    # rerun simulation so new include cells get recorded from
    if rerun: 
        cellsRecord = [cell.gid for cell in sim.getCellsList(include)]
        for cellRecord in cellsRecord:
            if cellRecord not in sim.cfg.recordCells:
                sim.cfg.recordCells.append(cellRecord)
        sim.setupRecording()
        sim.simulate()


    colorList = [[0.42,0.67,0.84], [0.90,0.76,0.00], [0.42,0.83,0.59], [0.90,0.32,0.00],
                [0.34,0.67,0.67], [0.90,0.59,0.00], [0.42,0.82,0.83], [1.00,0.85,0.00],
                [0.33,0.67,0.47], [1.00,0.38,0.60], [0.57,0.67,0.33], [0.5,0.2,0.0],
                [0.71,0.82,0.41], [0.0,0.2,0.5]] 

    tracesList = sim.cfg.recordTraces.keys()
    tracesList.sort()
    cells, cellGids, _ = getCellsInclude(include)
    gidPops = {cell['gid']: cell['tags']['popLabel'] for cell in cells}

    # time range
    if timeRange is None:
        timeRange = [0,sim.cfg.duration]

    recordStep = sim.cfg.recordStep

    figs = []
    tracesData = []
    # Plot one fig per cell
    if oneFigPer == 'cell':
        for gid in cellGids:
            figs.append(figure()) # Open a new figure
            fontsiz = 12
            for itrace, trace in enumerate(tracesList):
                if 'cell_'+str(gid) in sim.allSimData[trace]:
                    data = sim.allSimData[trace]['cell_'+str(gid)][int(timeRange[0]/recordStep):int(timeRange[1]/recordStep)]
                    t = arange(timeRange[0], timeRange[1]+recordStep, recordStep)
                    tracesData.append({'t': t, 'cell_'+str(gid)+'_'+trace: data})
                    color = colorList[itrace]
                    if not overlay:
                        subplot(len(tracesList),1,itrace+1)
                        color = 'blue'
                    plot(t[:len(data)], data, linewidth=1.5, color=color, label=trace)
                    xlabel('Time (ms)', fontsize=fontsiz)
                    ylabel(trace, fontsize=fontsiz)
                    xlim(timeRange)
                    if itrace==0: title('Cell %d, Pop %s '%(int(gid), gidPops[gid]))
                    if overlay: 
                        maxLabelLen = 10
                        subplots_adjust(right=(0.9-0.012*maxLabelLen))
                        legend(fontsize=fontsiz, bbox_to_anchor=(1.04, 1), loc=2, borderaxespad=0.)


    # Plot one fig per cell
    elif oneFigPer == 'trace':
        for itrace, trace in enumerate(tracesList):
            figs.append(figure()) # Open a new figure
            fontsiz = 12
            for igid, gid in enumerate(cellGids):
                if 'cell_'+str(gid) in sim.allSimData[trace]:
                    data = sim.allSimData[trace]['cell_'+str(gid)][int(timeRange[0]/recordStep):int(timeRange[1]/recordStep)]
                    t = arange(timeRange[0], timeRange[1]+recordStep, recordStep)
                    tracesData.append({'t': t, 'cell_'+str(gid)+'_'+trace: data})
                    color = colorList[igid]
                    if not overlay:
                        subplot(len(cellGids),1,igid+1)
                        color = 'blue'
                        ylabel(trace, fontsize=fontsiz)
                    plot(t[:len(data)], data, linewidth=1.5, color=color, label='Cell %d, Pop %s '%(int(gid), gidPops[gid]))
                    xlabel('Time (ms)', fontsize=fontsiz)
                    xlim(timeRange)
                    title('Cell %d, Pop %s '%(int(gid), gidPops[gid]))
            if overlay:
                maxLabelLen = 10
                subplots_adjust(right=(0.9-0.012*maxLabelLen)) 
                legend(fontsize=fontsiz, bbox_to_anchor=(1.04, 1), loc=2, borderaxespad=0.)

    try:
        tight_layout()
    except:
        pass

    #save figure data
    if saveData:
        figData = {'tracesData': tracesData, 'include': include, 'timeRange': timeRange, 'oneFigPer': oneFigPer,
         'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}
    
        _saveFigData(figData, saveData, 'traces')
 
    # save figure
    if saveFig: 
        if isinstance(saveFig, str):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'traces.png'
        savefig(filename)

    # show fig 
    if showFig: _showFigure()

    return figs



######################################################################################################################################################
## Plot LFP (time-resolved or power spectra)
######################################################################################################################################################
def plotLFP ():
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
        figure() # Open a new figure
        for p in range(len(sim.lfppops)):
            psd(lfpv[p],Fs=200, linewidth= 2,color=colorspsd[p])
            xlabel('Frequency (Hz)')
            ylabel('Power')
            h=axes()
            h.set_yticklabels([])
        legend(['L2/3','L5A', 'L5B', 'L6'])

    # plot overall psd
    figure() # Open a new figure
    psd(lfptot,Fs=200, linewidth= 2)
    xlabel('Frequency (Hz)')
    ylabel('Power')
    h=axes()
    h.set_yticklabels([])

    show()

def _roundFigures(x, n):
    """Returns x rounded to n significant figures."""
    return round(x, int(n - math.ceil(math.log10(abs(x)))))

######################################################################################################################################################
## Plot connectivity
######################################################################################################################################################
def plotConn (include = ['all'], feature = 'strength', orderBy = 'gid', figSize = (10,10), groupBy = 'pop', groupByInterval = None, saveData = None, saveFig = None, showFig = True): 
    ''' 
    Plot network connectivity
        - include (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Cells to show (default: ['all'])
        - feature ('weight'|'delay'|'numConns'|'probability'|'strength'|'convergence'|'divergence'): Feature to show in connectivity matrix; 
            the only features applicable to groupBy='cell' are 'weight', 'delay' and 'numConns';  'strength' = weight * probability (default: 'strength')
        - groupBy ('pop'|'cell'|'y'|: Show matrix for individual cells, populations, or by other numeric tag such as 'y' (default: 'pop')
        - groupByInterval (int or float): Interval of groupBy feature to group cells by in conn matrix, e.g. 100 to group by cortical depth in steps of 100 um   (default: None)
        - orderBy ('gid'|'y'|'ynorm'|...): Unique numeric cell property to order x and y axes by, e.g. 'gid', 'ynorm', 'y' (requires groupBy='cells') (default: 'gid')
        - figSize ((width, height)): Size of figure (default: (10,10))
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure; 
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure; 
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)

        - Returns figure handles
    '''

    print('Plotting connectivity matrix...')
    
    cells, cellGids, netStimPops = getCellsInclude(include)    

    # Create plot
    fig = figure(figsize=figSize)
    fig.subplots_adjust(right=0.98) # Less space on right
    fig.subplots_adjust(top=0.96) # Less space on top
    fig.subplots_adjust(bottom=0.02) # Less space on bottom

    h = axes()

    # Calculate matrix if grouped by cell
    if groupBy == 'cell': 
        if feature in ['weight', 'delay', 'numConns']: 
            connMatrix = zeros((len(cellGids), len(cellGids)))
            countMatrix = zeros((len(cellGids), len(cellGids)))
        else: 
            print 'Conn matrix with groupBy="cell" only supports features= "weight", "delay" or "numConns"'
            return fig
        cellInds = {cell['gid']: ind for ind,cell in enumerate(cells)}

        # Order by
        if len(cells) > 0:
            if orderBy not in cells[0]['tags']:  # if orderBy property doesn't exist or is not numeric, use gid
                orderBy = 'gid'
            elif not isinstance(cells[0]['tags'][orderBy], Number): 
                orderBy = 'gid' 
        
            if orderBy == 'gid': 
                yorder = [cell[orderBy] for cell in cells]
            else:
                yorder = [cell['tags'][orderBy] for cell in cells]
            
            sortedGids = {gid:i for i,(y,gid) in enumerate(sorted(zip(yorder,cellGids)))}
            cellInds = sortedGids

        # Calculate conn matrix
        for cell in cells:  # for each postsyn cell
            for conn in cell['conns']:
                if conn['preGid'] != 'NetStim' and conn['preGid'] in cellInds:
                    if feature in ['weight', 'delay']: 
                        if conn['preGid'] in cellInds:
                            connMatrix[cellInds[conn['preGid']], cellInds[cell['gid']]] += conn[feature]
                    countMatrix[cellInds[conn['preGid']], cellInds[cell['gid']]] += 1

        if feature in ['weight', 'delay']: connMatrix = connMatrix / countMatrix 
        elif feature in ['numConns']: connMatrix = countMatrix 

    # Calculate matrix if grouped by pop
    elif groupBy == 'pop': 
        
        # get list of pops
        popsTemp = list(set([cell['tags']['popLabel'] for cell in cells]))
        pops = [pop for pop in sim.net.allPops if pop in popsTemp]+netStimPops
        popInds = {pop: ind for ind,pop in enumerate(pops)}
        
        # initialize matrices
        if feature in ['weight', 'strength']: 
            weightMatrix = zeros((len(pops), len(pops)))
        elif feature == 'delay': 
            delayMatrix = zeros((len(pops), len(pops)))
        countMatrix = zeros((len(pops), len(pops)))
        
        # calculate max num conns per pre and post pair of pops
        numCellsPop = {}
        for pop in pops:
            if pop in netStimPops:
                numCellsPop[pop] = -1
            else:
                numCellsPop[pop] = len([cell for cell in cells if cell['tags']['popLabel']==pop])

        maxConnMatrix = zeros((len(pops), len(pops)))
        if feature == 'convergence': maxPostConnMatrix = zeros((len(pops), len(pops)))
        if feature == 'divergence': maxPreConnMatrix = zeros((len(pops), len(pops)))
        for prePop in pops:
            for postPop in pops: 
                if numCellsPop[prePop] == -1: numCellsPop[prePop] = numCellsPop[postPop]
                maxConnMatrix[popInds[prePop], popInds[postPop]] = numCellsPop[prePop]*numCellsPop[postPop]
                if feature == 'convergence': maxPostConnMatrix[popInds[prePop], popInds[postPop]] = numCellsPop[postPop]
                if feature == 'divergence': maxPreConnMatrix[popInds[prePop], popInds[postPop]] = numCellsPop[prePop]
        
        # Calculate conn matrix
        for cell in cells:  # for each postsyn cell
            for conn in cell['conns']:
                if conn['preGid'] == 'NetStim':
                    prePopLabel = conn['preLabel']
                else:
                    preCell = next((cell for cell in cells if cell['gid']==conn['preGid']), None)
                    prePopLabel = preCell['tags']['popLabel'] if preCell else None
                
                if prePopLabel in popInds:
                    if feature in ['weight', 'strength']: 
                        weightMatrix[popInds[prePopLabel], popInds[cell['tags']['popLabel']]] += conn['weight']
                    elif feature == 'delay': 
                        delayMatrix[popInds[prePopLabel], popInds[cell['tags']['popLabel']]] += conn['delay'] 
                    countMatrix[popInds[prePopLabel], popInds[cell['tags']['popLabel']]] += 1    
    
    # Calculate matrix if grouped by numeric tag (eg. 'y')
    elif groupBy in sim.net.allCells[0]['tags'] and isinstance(sim.net.allCells[0]['tags'][groupBy], Number):
        if not isinstance(groupByInterval, Number):
            print 'groupByInterval not specified'
            return
  
        # group cells by 'groupBy' feature (eg. 'y') in intervals of 'groupByInterval')
        cellValues = [cell['tags'][groupBy] for cell in cells]
        minValue = _roundFigures(groupByInterval * floor(min(cellValues) / groupByInterval), 3)
        maxValue  = _roundFigures(groupByInterval * ceil(max(cellValues) / groupByInterval), 3)
        
        groups = arange(minValue, maxValue, groupByInterval)
        groups = [_roundFigures(x,3) for x in groups]
        print groups

        if len(groups) < 2: 
            print 'groupBy %s with groupByInterval %s results in <2 groups'%(str(groupBy), str(groupByInterval))
            return
        groupInds = {group: ind for ind,group in enumerate(groups)}
        
        # initialize matrices
        if feature in ['weight', 'strength']: 
            weightMatrix = zeros((len(groups), len(groups)))
        elif feature == 'delay': 
            delayMatrix = zeros((len(groups), len(groups)))
        countMatrix = zeros((len(groups), len(groups)))

        # calculate max num conns per pre and post pair of pops
        numCellsGroup = {}
        for group in groups:
            numCellsGroup[group] = len([cell for cell in cells if group <= cell['tags'][groupBy] < (group+groupByInterval)])

        maxConnMatrix = zeros((len(groups), len(groups)))
        if feature == 'convergence': maxPostConnMatrix = zeros((len(groups), len(groups)))
        if feature == 'divergence': maxPreConnMatrix = zeros((len(groups), len(groups)))
        for preGroup in groups:
            for postGroup in groups: 
                if numCellsGroup[preGroup] == -1: numCellsGroup[preGroup] = numCellsGroup[postGroup]
                maxConnMatrix[groupInds[preGroup], groupInds[postGroup]] = numCellsGroup[preGroup]*numCellsGroup[postGroup]
                if feature == 'convergence': maxPostConnMatrix[groupInds[prePop], groupInds[postGroup]] = numCellsPop[postGroup]
                if feature == 'divergence': maxPreConnMatrix[groupInds[preGroup], groupInds[postGroup]] = numCellsPop[preGroup]
        
        # Calculate conn matrix
        for cell in cells:  # for each postsyn cell
            for conn in cell['conns']:
                if conn['preGid'] == 'NetStim':
                    prePopLabel = -1  # maybe add in future
                else:
                    preCell = next((cell for cell in cells if cell['gid']==conn['preGid']), None)
                    if preCell:
                        preGroup = _roundFigures(groupByInterval * floor(preCell['tags'][groupBy] / groupByInterval), 3)
                    else:
                        None

                postGroup = _roundFigures(groupByInterval * floor(cell['tags'][groupBy] / groupByInterval), 3)

                #print groupInds
                if preGroup in groupInds:
                    if feature in ['weight', 'strength']: 
                        weightMatrix[groupInds[preGroup], groupInds[postGroup]] += conn['weight']
                    elif feature == 'delay': 
                        delayMatrix[groupInds[preGroup], groupInds[postGroup]] += conn['delay'] 
                    countMatrix[groupInds[preGroup], groupInds[postGroup]] += 1    

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

    imshow(connMatrix, interpolation='nearest', cmap='jet', vmin=nanmin(connMatrix), vmax=nanmax(connMatrix))  #_bicolormap(gap=0)


    # Plot grid lines
    hold(True)
    if groupBy == 'cell':
        # Make pretty
        step = int(len(cells)/10.0)
        base = 100 if step>100 else 10
        step = int(base * floor(float(step)/base))
        h.set_xticks(arange(0,len(cells),step))
        h.set_yticks(arange(0,len(cells),step))
        h.set_xticklabels(arange(0,len(cells),step))
        h.set_yticklabels(arange(0,len(cells),step))
        h.xaxis.set_ticks_position('top')
        xlim(-0.5,len(cells)-0.5)
        ylim(len(cells)-0.5,-0.5)
        clim(nanmin(connMatrix),nanmax(connMatrix))

    elif groupBy == 'pop':
        for ipop, pop in enumerate(pops):
            plot(array([0,len(pops)])-0.5,array([ipop,ipop])-0.5,'-',c=(0.7,0.7,0.7))
            plot(array([ipop,ipop])-0.5,array([0,len(pops)])-0.5,'-',c=(0.7,0.7,0.7))

        # Make pretty
        h.set_xticks(range(len(pops)))
        h.set_yticks(range(len(pops)))
        h.set_xticklabels(pops)
        h.set_yticklabels(pops)
        h.xaxis.set_ticks_position('top')
        xlim(-0.5,len(pops)-0.5)
        ylim(len(pops)-0.5,-0.5)
        clim(nanmin(connMatrix),nanmax(connMatrix))

    else:
        for igroup, group in enumerate(groups):
            plot(array([0,len(groups)])-0.5,array([igroup,igroup])-0.5,'-',c=(0.7,0.7,0.7))
            plot(array([igroup,igroup])-0.5,array([0,len(groups)])-0.5,'-',c=(0.7,0.7,0.7))

        # Make pretty
        h.set_xticks([i-0.5 for i in range(len(groups))])
        h.set_yticks([i-0.5 for i in range(len(groups))])
        h.set_xticklabels([int(x) if x>1 else x for x in groups])
        h.set_yticklabels([int(x) if x>1 else x for x in groups])
        h.xaxis.set_ticks_position('top')
        xlim(-0.5,len(groups)-0.5)
        ylim(len(groups)-0.5,-0.5)
        clim(nanmin(connMatrix),nanmax(connMatrix))

    colorbar(label=feature, shrink=0.8) #.set_label(label='Fitness',size=20,weight='bold')
    xlabel('post')
    h.xaxis.set_label_coords(0.5, 1.06)
    ylabel('pre')
    title ('Connection '+feature+' matrix', y=1.08)

    #save figure data
    if saveData:
        figData = {'connMatrix': connMatrix, 'feature': feature, 'groupBy': groupBy,
         'include': include, 'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}
    
        _saveFigData(figData, saveData, 'conn')
 
    # save figure
    if saveFig: 
        if isinstance(saveFig, str):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'conn.png'
        savefig(filename)

    # show fig 
    if showFig: _showFigure()

    return fig


######################################################################################################################################################
## Plot 2D representation of network cell positions and connections
######################################################################################################################################################
def plot2Dnet (include = ['allCells'], figSize = (12,12), showConns = True, saveData = None, saveFig = None, showFig = True): 
    ''' 
    Plot 2D representation of network cell positions and connections
        - include (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Cells to show (default: ['all'])
        - showConns (True|False): Whether to show connections or not (default: True)
        - figSize ((width, height)): Size of figure (default: (12,12))
        - saveData (None|'fileName'): File name where to save the final data used to generate the figure (default: None)
        - saveFig (None|'fileName'): File name where to save the figure;
            if set to True uses filename from simConfig (default: None)(default: None)
        - showFig (True|False): Whether to show the figure or not;
            if set to True uses filename from simConfig (default: None)

        - Returns figure handles
    '''

    print('Plotting 2D representation of network cell locations and connections...')

    fig = figure(figsize=figSize)
    colorList = [[0.42,0.67,0.84], [0.90,0.76,0.00], [0.42,0.83,0.59], [0.90,0.32,0.00],
                [0.34,0.67,0.67], [0.90,0.59,0.00], [0.42,0.82,0.83], [1.00,0.85,0.00],
                [0.33,0.67,0.47], [1.00,0.38,0.60], [0.57,0.67,0.33], [0.5,0.2,0.0],
                [0.71,0.82,0.41], [0.0,0.2,0.5]] 

    cells, cellGids, _ = getCellsInclude(include)           
    selectedPops = [cell['tags']['popLabel'] for cell in cells]
    popLabels = [pop for pop in sim.net.allPops if pop in selectedPops] # preserves original ordering
    popColors = {popLabel: colorList[ipop%len(colorList)] for ipop,popLabel in enumerate(popLabels)} # dict with color for each pop
    cellColors = [popColors[cell['tags']['popLabel']] for cell in cells]
    posX = [cell['tags']['x'] for cell in cells]  # get all x positions
    posY = [cell['tags']['y'] for cell in cells]  # get all y positions
    scatter(posX, posY, s=60, color = cellColors) # plot cell soma positions
    if showConns:
        for postCell in cells:
            for con in postCell['conns']:  # plot connections between cells
                if not isinstance(con['preGid'], str) and con['preGid'] in cellGids:
                    posXpre,posYpre = next(((cell['tags']['x'],cell['tags']['y']) for cell in cells if cell['gid']==con['preGid']), None)  
                    posXpost,posYpost = postCell['tags']['x'], postCell['tags']['y'] 
                    color='red'
                    if con['synMech'] in ['inh', 'GABA', 'GABAA', 'GABAB']:
                        color = 'blue'
                    width = 0.1 #50*con['weight']
                    plot([posXpre, posXpost], [posYpre, posYpost], color=color, linewidth=width) # plot line from pre to post
    xlabel('x (um)')
    ylabel('y (um)') 
    xlim([min(posX)-0.05*max(posX),1.05*max(posX)]) 
    ylim([min(posY)-0.05*max(posY),1.05*max(posY)])
    fontsiz = 12

    for popLabel in popLabels:
        plot(0,0,color=popColors[popLabel],label=popLabel)
    legend(fontsize=fontsiz, bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
    ax = gca()
    ax.invert_yaxis()

    # save figure data
    if saveData:
        figData = {'posX': posX, 'posY': posY, 'posX': cellColors, 'posXpre': posXpre, 'posXpost': posXpost, 'posYpre': posYpre, 'posYpost': posYpost,
         'include': include, 'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}
    
        _saveFigData(figData, saveData, '2Dnet')
 
    # save figure
    if saveFig: 
        if isinstance(saveFig, str):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'2Dnet.png'
        savefig(filename)

    # show fig 
    if showFig: _showFigure()

    return fig


######################################################################################################################################################
## Plot weight changes
######################################################################################################################################################
def plotWeightChanges():
    print('Plotting weight changes...')

    if sim.usestdp:
        # create plot
        figh = figure(figsize=(1.2*8,1.2*6))
        figh.subplots_adjust(left=0.02) # Less space on left
        figh.subplots_adjust(right=0.98) # Less space on right
        figh.subplots_adjust(top=0.96) # Less space on bottom
        figh.subplots_adjust(bottom=0.02) # Less space on bottom
        figh.subplots_adjust(wspace=0) # More space between
        figh.subplots_adjust(hspace=0) # More space between
        h = axes()

        # create data matrix
        wcs = [x[-1][-1] for x in sim.allweightchanges] # absolute final weight
        wcs = [x[-1][-1]-x[0][-1] for x in sim.allweightchanges] # absolute weight change
        pre,post,recep = zip(*[(x[0],x[1],x[2]) for x in sim.allstdpconndata])
        ncells = int(max(max(pre),max(post))+1)
        wcmat = zeros([ncells, ncells])

        for iwc,ipre,ipost,irecep in zip(wcs,pre,post,recep):
            wcmat[int(ipre),int(ipost)] = iwc *(-1 if irecep>=2 else 1)

        # plot
        imshow(wcmat,interpolation='nearest',cmap=_bicolormap(gap=0,mingreen=0.2,redbluemix=0.1,epsilon=0.01))
        xlabel('post-synaptic cell id')
        ylabel('pre-synaptic cell id')
        h.set_xticks(sim.popGidStart)
        h.set_yticks(sim.popGidStart)
        h.set_xticklabels(sim.popnames)
        h.set_yticklabels(sim.popnames)
        h.xaxif.set_ticks_position('top')
        xlim(-0.5,ncells-0.5)
        ylim(ncells-0.5,-0.5)
        clim(-abs(wcmat).max(),abs(wcmat).max())
        colorbar()
        showFigure()



######################################################################################################################################################
## Create colormap
######################################################################################################################################################
def _bicolormap(gap=0.1,mingreen=0.2,redbluemix=0.5,epsilon=0.01):
   from matplotlib.colors import LinearSegmentedColormap as makecolormap
   
   mng=mingreen; # Minimum amount of green to add into the colors
   mix=redbluemix; # How much red to mix with the blue an vice versa
   eps=epsilon; # How much of the center of the colormap to make gray
   omg=1-gap # omg = one minus gap
   
   cdict = {'red': ((0.00000, 0.0, 0.0),
                    (0.5-eps, mix, omg),
                    (0.50000, omg, omg),
                    (0.5+eps, omg, 1.0),
                    (1.00000, 1.0, 1.0)),

         'green':  ((0.00000, mng, mng),
                    (0.5-eps, omg, omg),
                    (0.50000, omg, omg),
                    (0.5+eps, omg, omg),
                    (1.00000, mng, mng)),

         'blue':   ((0.00000, 1.0, 1.0),
                    (0.5-eps, 1.0, omg),
                    (0.50000, omg, omg),
                    (0.5+eps, omg, mix),
                    (1.00000, 0.0, 0.0))}
   cmap = makecolormap('bicolormap',cdict,256)

   return cmap
