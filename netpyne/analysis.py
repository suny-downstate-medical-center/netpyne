"""
analysis.py

Functions to plot and analyse results

Contributors: salvadordura@gmail.com
"""
import matplotlib
from matplotlib.pylab import arange, gca, scatter, figure, hold, subplot, axes, shape, imshow, colorbar, plot, xlabel, ylabel, title, xlim, ylim, clim, show, zeros, legend, savefig, psd, ion, subplots_adjust
from scipy import size, array, linspace, ceil

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
        if sim.cfg['plotRaster']: # Whether or not to plot
            if (sim.totalSpikes>sim.cfg['maxspikestoplot']): 
                print('  Too many spikes (%i vs. %i)' % (sim.totalSpikes, sim.cfg['maxspikestoplot'])) # Plot raster, but only if not too many spikes
            else: 
                print('Plotting raster...')
                sim.analysis.plotRaster() 
                showFig()
        if sim.cfg['plotCells']:
            print('Plotting recorded traces ...')
            sim.analysis.plotTraces() 
            showFig()
        if sim.cfg['plotConn']:
            print('Plotting connectivity matrix...')
            sim.analysis.plotConn()
            showFig()
        if sim.cfg['plotLFPSpectrum']:
            print('Plotting LFP power spectral density...')
            sim.analysis.plotLFPSpectrum()
            showFig()
        if sim.cfg['plot2Dnet']:
            print('Plotting 2D visualization of network...')
            sim.analysis.plot2Dnet()   
            showFig() 
        if sim.cfg['plotWeightChanges']:
            print('Plotting weight changes...')
            sim.analysis.plotWeightChanges()
            showFig()
        if sim.cfg['plot3dArch']:
            print('Plotting 3d architecture...')
            sim.analysis.plot3dArch()
            showFig()
        if sim.cfg['timing']:
            sim.timing('stop', 'plotTime')
            print('  Done; plotting time = %0.2f s' % sim.timingData['plotTime'])
            sim.timing('stop', 'totalTime')
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


## Raster plot 
def plotRaster (): 
    colorList = [[0.42,0.67,0.84], [0.90,0.76,0.00], [0.42,0.83,0.59], [0.90,0.32,0.00],
                [0.34,0.67,0.67], [0.90,0.59,0.00], [0.42,0.82,0.83], [1.00,0.85,0.00],
                [0.33,0.67,0.47], [1.00,0.38,0.60], [0.57,0.67,0.33], [0.5,0.2,0.0],
                [0.71,0.82,0.41], [0.0,0.2,0.5]] 
    popLabels = [pop.tags['popLabel'] for pop in sim.net.pops if pop.tags['cellModel'] not in ['NetStim']]
    popColors = {popLabel: colorList[ipop%len(colorList)] for ipop,popLabel in enumerate(popLabels)} # dict with color for each pop
    gidColors = {cell['gid']: popColors[cell['tags']['popLabel']] for cell in sim.net.allCells}  # dict with color for each gid
    spkids = sim.allSimData['spkid']
    ylabelText = 'Cell id'
    spkidColors = [gidColors[spkid] for spkid in spkids]
    try:
        if sim.cfg['orderRasterYnorm']:
            gids = [cell['gid'] for cell in sim.net.allCells]
            ynorms = [cell['tags']['ynorm'] for cell in sim.net.allCells]
            #ynorms.reverse()
            sortedGids = {gid:i for i,(y,gid) in enumerate(sorted(zip(ynorms,gids)))}
            spkids = [sortedGids[gid] for gid in spkids]
            ylabelText = 'Cell id (arranged by NCD)'
    except:
        pass     
    figure(figsize=(10,8)) # Open a new figure
    fontsiz = 12
    scatter(sim.allSimData['spkt'], spkids, 10, linewidths=2, marker='|', color = spkidColors) # Create raster  
    xlabel('Time (ms)', fontsize=fontsiz)
    ylabel(ylabelText, fontsize=fontsiz)
    if sim.cfg['plotSync']:
        for spkt in sim.allSimData['spkt']:
            plot((spkt, spkt), (0, sim.numCells), 'r-', linewidth=0.1)
        title('cells=%i syns/cell=%0.1f rate=%0.1f Hz sync=%0.2f' % (sim.numCells,sim.connsPerCell,sim.firingRate,syncMeasure()), fontsize=fontsiz)
    else:
        title('cells=%i syns/cell=%0.1f rate=%0.1f Hz' % (sim.numCells,sim.connsPerCell,sim.firingRate), fontsize=fontsiz)
    xlim(0,sim.cfg['duration'])
    ylim(0,sim.numCells)
    for popLabel in popLabels:
        plot(0,0,color=popColors[popLabel],label=popLabel)
    legend(fontsize=fontsiz, bbox_to_anchor=(1.02, 1), loc=2, borderaxespad=0.)
    maxLabelLen = max([len(l) for l in popLabels])
    subplots_adjust(right=(0.9-0.01*maxLabelLen))
    ax = gca()
    ax.invert_yaxis()

    #savefig('raster.png')

## Traces (v,i,g etc) plot
def plotTraces (): 
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
    #savefig('traces.png')


## Plot power spectra density
def plotLFPSpectrum ():
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
    #show()

# Plot 2D visualization of network cell positions and connections
def plot2Dnet():
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

## Plot weight changes
def plotWeightChanges():
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
        #show()


## plot 3d architecture:
def plot3dArch():
    # create plot
    figh = figure(figsize=(1.2*8,1.2*6))
    # figh.subplots_adjust(left=0.02) # Less space on left
    # figh.subplots_adjust(right=0.98) # Less space on right
    # figh.subplots_adjust(top=0.98) # Less space on bottom
    # figh.subplots_adjust(bottom=0.02) # Less space on bottom
    ax = figh.add_subplot(1,1,1, projection='3d')
    h = axes()

    #print len(sim.xlocs),len(sim.ylocs),len(sim.zlocs)
    xlocs =[1,2,3]
    ylocs=[3,2,1]
    zlocs=[0.1,0.5,1.2]
    ax.scatter(xlocs,ylocs, zlocs,  s=10, c=zlocs, edgecolors='none',cmap = 'jet_r' , linewidths=0.0, alpha=1, marker='o')
    azim = 40  
    elev = 60
    ax.view_init(elev, azim) 
    #xlim(min(sim.xlocs),max(sim.xlocs))
    #ylim(min(sim.ylocs),max(sim.ylocs))
    #ax.set_zlim(min(sim.zlocs),max(sim.zlocs))
    xlabel('lateral distance (mm)')
    ylabel('lateral distance (mm)')
    ylabel('cortical depth (mm)')


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
