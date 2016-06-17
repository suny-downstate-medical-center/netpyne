"""
analysis.py

Functions to plot and analyse results

Contributors: salvadordura@gmail.com
"""
import matplotlib
from matplotlib.pylab import floor, ceil, yticks, arange, gca, scatter, figure, hold, subplot, axes, shape, imshow, colorbar, plot, xlabel, ylabel, title, xlim, ylim, clim, show, zeros, legend, savefig, psd, ion, subplots_adjust
from scipy import size, array, linspace, ceil
from numbers import Number

import sim

###############################################################################
### Simulation-related graph plotting functions
###############################################################################

def showFig():
    try:
        show(block=False)
    except:
        show()

# sequence of generic plots (raster, connectivity,psd,...)
def plotData ():
    ## Plotting
    if sim.rank == 0:
        sim.timing('start', 'plotTime')

        # Call analysis functions specified by user
        for funcName, args in sim.cfg['analysis']:
            func = getattr(sim.analysis, funcName)  # get pointer to function
            func(args)  # call function with user arguments

        # Print timings
        if sim.cfg['timing']:
            
            sim.timing('stop', 'plotTime')
            print('  Done; plotting time = %0.2f s' % sim.timingData['plotTime'])
            
            sim.timing('stop', 'totalTime')
            sumTime = sum([t for k,t in sim.timingData.iteritems() if k not in ['totalTime']])
            if sim.timingData['totalTime'] <= 1.2*sumTime:  # Print total time (only if makes sense)         
                print('\nTotal time = %0.2f s' % sim.timingData['totalTime'])


## Sync measure
def syncMeasure ():
    t0=-1 
    width=1 
    cnt=0
    for spkt in sim.allSimData['spkt']:
        if (spkt>=t0+width): 
            t0=spkt 
            cnt+=1
    return 1-cnt/(sim.cfg['duration']/width)

def getCellsInclude(include):
    allCells = sim.net.allCells
    allNetStimPops = [p.tags['popLabel'] for p in sim.net.pops if p.tags['cellModel']=='NetStim']
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
            cellGids.extend([gid for i,gid in enumerate(cellsPop) if i in condition[1]])

    cellGids = list(set(cellGids))  # unique values
    cells = [cell for cell in allCells if cell['gid'] in cellGids]

    return cells, cellGids, netStimPops



## Raster plot 
def plotRaster (include = ['allCells'], timeRange = None, maxSpikes = 1e8, orderBy = 'gid', orderInverse = False, spikeHist = None, syncLines = False, saveData = None, saveFig = None): 
    ''' 
    Raster plot of network cells
        - include (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Subset of cells to include (default: 'all')
        - timeRange ([start:stop]): Time range of spikes shown; if None shows all (default: None)
        - maxSpikes (int): maximum number of spikes that will be plotted  (default: 1e8)
        - orderBy ('gid'|'y'|'ynorm'|...): Unique numeric cell property to order y-axis by, e.g. 'gid', 'ynorm', 'y' (default: 'gid')
        - orderInverse (True|False): Invert the y-axis order (default: False)
        - spikeHist (None|'overlay'|'subplot'): overlay line over raster showing spike histogram (spikes/bin) (default: False)
        - syncLines (True|False): calculate synchorny measure and plot vertical lines for each spike to evidence synchrony (default: False)
        - saveData (None|'fileName'): File name where to save the final data used to generate the figure
        - saveFig (None|'fileName'): File name where to save the figure
    '''

    print('Plotting raster...')

    colorList = [[0.42,0.67,0.84], [0.90,0.76,0.00], [0.42,0.83,0.59], [0.90,0.32,0.00],
                [0.34,0.67,0.67], [0.90,0.59,0.00], [0.42,0.82,0.83], [1.00,0.85,0.00],
                [0.33,0.67,0.47], [1.00,0.38,0.60], [0.57,0.67,0.33], [0.5,0.2,0.0],
                [0.71,0.82,0.41], [0.0,0.2,0.5]] 

    # Select cells to include
    cells, cellGids, netStimPops = getCellsInclude(include)
    popLabels = list(set(([cell['tags']['popLabel'] for cell in cells])))+netStimPops
    popColors = {popLabel: colorList[ipop%len(colorList)] for ipop,popLabel in enumerate(popLabels)} # dict with color for each pop
    if len(cellGids) > 0:
        gidColors = {cell['gid']: popColors[cell['tags']['popLabel']] for cell in cells}  # dict with color for each gid
        spkgids,spkts = zip(*[(spkgid,spkt) for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids])
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
    if timeRange == [0,sim.cfg['duration']]:
        pass
    elif timeRange is None:
        timeRange = [0,sim.cfg['duration']]
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


    # plotting
    figure(figsize=(10,8)) # Open a new figure
    fontsiz = 12
    scatter(spkts, spkinds, 10, linewidths=2, marker='|', color = spkgidColors) # Create raster  
    xlabel('Time (ms)', fontsize=fontsiz)
    ylabel(ylabelText, fontsize=fontsiz)
    if syncLines: # plot synchrony lines 
        for spkt in spkts:
            plot((spkt, spkt), (0, sim.numCells), 'r-', linewidth=0.1)
        title('cells=%i syns/cell=%0.1f rate=%0.1f Hz sync=%0.2f' % (sim.numCells,sim.connsPerCell,sim.firingRate,syncMeasure()), fontsize=fontsiz)
    else:
        title('cells=%i syns/cell=%0.1f rate=%0.1f Hz' % (sim.numCells,sim.connsPerCell,sim.firingRate), fontsize=fontsiz)
    xlim(timeRange)
    ylim(-1, len(cells)+numNetStims+1)
    
    # code to make y-axis show actual values instead of ids (difficult to make work in a generic way for all cases)
    '''maxY = max(y2ind.values())
    minY = min(y2ind.values())
    # if  maxy >= 20: base = 5
    # elif maxy >= 10: base = 2
    # elif maxy > 1: base = 1
    # elif maxy >= 0.1: base = 0.1
    # else: base = 0.001
    base=10
    upperY = base * ceil(float(maxY)/base)
    lowerY = base * floor(float(minY)/base)
    yAddUpper = int(upperY - maxY)
    yAddLower = int (minY-lowerY)
    for i in range(yAddUpper): y2ind.update({yAddUpper: len(y2ind)+1})
    for i in range(yAddLower): y2ind.update({yAddLower: min(y2ind.values())-1})
    ystep = base #int(len(y2ind)/base)
    #ystep = base * round(float(ystep)/base)
    yticks(y2ind.values()[::ystep], y2ind.keys()[::ystep])'''

    for popLabel in popLabels:
        plot(0,0,color=popColors[popLabel],label=popLabel)
    legend(fontsize=fontsiz, bbox_to_anchor=(1.02, 1), loc=2, borderaxespad=0.)
    maxLabelLen = max([len(l) for l in popLabels])
    subplots_adjust(right=(0.9-0.01*maxLabelLen))
    ax = gca()
    ax.invert_yaxis()

    showFig()


## Traces (v,i,g etc) plot
def plotTraces (): 
    print('Plotting recorded cell traces ...')

    tracesList = sim.cfg['recordTraces'].keys()
    tracesList.sort()
    gidList = [trace for trace in sim.cfg['plotCells'] if isinstance(trace, int)]
    popList = [trace for trace in sim.cfg['plotCells'] if isinstance(trace, str)]
    if 'all' in popList:
        gidList = [cell['gid'] for cell in sim.net.allCells]
        popList = []
    duration = sim.cfg['duration']
    recordStep = sim.cfg['recordStep']

    for gid in gidList:
        figure() # Open a new figure
        fontsiz = 12
        for itrace, trace in enumerate(tracesList):
            try:
                data = sim.allSimData[trace]['cell_'+str(gid)]
                t = arange(0, duration+recordStep, recordStep)
                subplot(len(tracesList),1,itrace+1)
                plot(t[:len(data)], data, linewidth=1.5)
                xlabel('Time (ms)', fontsize=fontsiz)
                ylabel(trace, fontsize=fontsiz)
                xlim(0,sim.cfg['duration'])
            except:
                pass
        if tracesList: subplot(len(tracesList),1,1)
        title('Cell %d'%(int(gid)))

    for popLabel in popList:
        fontsiz = 12
        for pop in sim.net.pops:
            if pop.tags['popLabel'] == popLabel and pop.cellGids:
                figure() # Open a new figure
                gid = pop.cellGids[0] 
                for itrace, trace in enumerate(tracesList):
                    try:
                        data = sim.allSimData[trace]['cell_'+str(gid)]
                        t = arange(0, len(data)*recordStep, recordStep)
                        subplot(len(tracesList),1,itrace+1)
                        plot(t, data, linewidth=1.5)
                        xlabel('Time (ms)', fontsize=fontsiz)
                        ylabel(trace, fontsize=fontsiz)
                        xlim(0,sim.cfg['duration'])
                    except:
                        pass
        subplot(len(tracesList),1,1)
        title('Pop %s, Cell %d'%(popLabel, int(gid)))
    showFig()



## Plot power spectra density
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


## Plot connectivityFor diagnostic purposes . Based on conndiagram.py.
def plotConn():
    print('Plotting connectivity matrix...')
    # Create plot
    figh = figure(figsize=(8,6))
    figh.subplots_adjust(left=0.02) # Less space on left
    figh.subplots_adjust(right=0.98) # Less space on right
    figh.subplots_adjust(top=0.96) # Less space on bottom
    figh.subplots_adjust(bottom=0.02) # Less space on bottom
    figh.subplots_adjust(wspace=0) # More space between
    figh.subplots_adjust(hspace=0) # More space between
    h = axes()
    totalconns = zeros(shape(sim.connprobs))
    for c1 in range(size(sim.connprobs,0)):
        for c2 in range(size(sim.connprobs,1)):
            for w in range(sim.nreceptors):
                totalconns[c1,c2] += sim.connprobs[c1,c2]*sim.connweights[c1,c2,w]*(-1 if w>=2 else 1)
    imshow(totalconns,interpolation='nearest',cmap=bicolormap(gap=0))

    # Plot grid lines
    hold(True)
    for pop in range(sim.npops):
        plot(array([0,sim.npops])-0.5,array([pop,pop])-0.5,'-',c=(0.7,0.7,0.7))
        plot(array([pop,pop])-0.5,array([0,sim.npops])-0.5,'-',c=(0.7,0.7,0.7))

    # Make pretty
    h.set_xticks(range(sim.npops))
    h.set_yticks(range(sim.npops))
    h.set_xticklabels(sim.popnames)
    h.set_yticklabels(sim.popnames)
    h.xaxis.set_ticks_position('top')
    xlim(-0.5,sim.npops-0.5)
    ylim(sim.npops-0.5,-0.5)
    clim(-abs(totalconns).max(),abs(totalconns).max())
    colorbar()

    showFig()

# Plot 2D visualization of network cell positions and connections
def plot2Dnet():
    print('Plotting 2D representation of network cell locations and connections...')

    allCells = sim.net.allCells
    figure(figsize=(12,12))
    colorList = [[0.42,0.67,0.84], [0.90,0.76,0.00], [0.42,0.83,0.59], [0.90,0.32,0.00],
                [0.34,0.67,0.67], [0.90,0.59,0.00], [0.42,0.82,0.83], [1.00,0.85,0.00],
                [0.33,0.67,0.47], [1.00,0.38,0.60], [0.57,0.67,0.33], [0.5,0.2,0.0],
                [0.71,0.82,0.41], [0.0,0.2,0.5]] 
    popLabels = [pop.tags['popLabel'] for pop in sim.net.pops if pop.tags['cellModel'] not in ['NetStim']]
    popColors = {popLabel: colorList[ipop%len(colorList)] for ipop,popLabel in enumerate(popLabels)} # dict with color for each pop
    cellColors = [popColors[cell.tags['popLabel']] for cell in sim.net.cells]
    posX = [cell['tags']['x'] for cell in allCells]  # get all x positions
    posY = [cell['tags']['y'] for cell in allCells]  # get all y positions
    scatter(posX, posY, s=60, color = cellColors) # plot cell soma positions
    for postCell in allCells:
        for con in postCell['conns']:  # plot connections between cells
            if not isinstance(con['preGid'], str):
                posXpre,posYpre = next(((cell['tags']['x'],cell['tags']['y']) for cell in allCells if cell['gid']==con['preGid']), None)  
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
    legend(fontsize=fontsiz, bbox_to_anchor=(1.02, 1), loc=2, borderaxespad=0.)
    ax = gca()
    ax.invert_yaxis()

    showFig()

## Plot weight changes
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
        imshow(wcmat,interpolation='nearest',cmap=bicolormap(gap=0,mingreen=0.2,redbluemix=0.1,epsilon=0.01))
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
        showFig()



## Create colormap
def bicolormap(gap=0.1,mingreen=0.2,redbluemix=0.5,epsilon=0.01):
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
