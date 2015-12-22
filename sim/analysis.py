"""
analysis.py

Functions to plot and analyse results

Contributors: salvadordura@gmail.com
"""

from pylab import mean, arange, bar, vstack,scatter, figure, hold, isscalar, gca, unique, subplot, axes, shape, imshow, colorbar, plot, xlabel, ylabel, title, xlim, ylim, clim, show, zeros, legend, savefig, cm, specgram, get_cmap, psd
from scipy.io import loadmat
from scipy import loadtxt, size, array, linspace, ceil
from datetime import datetime
from time import time
from collections import OrderedDict
import csv
import pickle
from mpl_toolkits.mplot3d import Axes3D

import shared as s

###############################################################################
### Simulation-related graph plotting functions
###############################################################################

# sequence of generic plots (raster, connectivity,psd,...)
def plotData():
    ## Plotting
    if s.rank == 0:
        if s.cfg['plotRaster']: # Whether or not to plot
            if (s.totalSpikes>s.cfg['maxspikestoplot']): 
                print('  Too many spikes (%i vs. %i)' % (s.totalSpikes, s.cfg['maxspikestoplot'])) # Plot raster, but only if not too many spikes
            else: 
                print('Plotting raster...')
                s.analysis.plotRaster()#allspiketimes, allspikecells, EorI, ncells, connspercell, backgroundweight, firingrate, duration)
        if s.cfg['plotConn']:
            print('Plotting connectivity matrix...')
            s.analysis.plotConn()
        if s.cfg['plotPsd']:
            print('Plotting power spectral density')
            s.analysis.plotPsd()
        if s.cfg['plotWeightChanges']:
            print('Plotting weight changes...')
            s.analysis.plotWeightChanges()
        if s.cfg['plot3darch']:
            print('Plotting 3d architecture...')
            s.analysis.plot3dArch()

        show(block=False)


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

## Raster plot 
def plotRaster(): 
    plotstart = time() # See how long it takes to plot
    colorList = [[0.42,0.67,0.84],[0.42,0.83,0.59],[0.90,0.76,0.00],[0.90,0.32,0.00],[0.34,0.67,0.67],[0.42,0.82,0.83],[0.90,0.59,0.00],[0.33,0.67,0.47],[1.00,0.85,0.00],[0.71,0.82,0.41],[0.57,0.67,0.33],[1.00,0.38,0.60],[0.5,0.2,0.0],[0.0,0.2,0.5]] 
    popLabels = [pop.tags['popLabel'] for pop in s.net.pops if pop.tags['cellModel'] not in ['NetStim']]
    popColors = {popLabel: colorList[ipop%len(colorList)] for ipop,popLabel in enumerate(popLabels)} # dict with color for each pop
    gidColors = {cell['gid']: popColors[cell['tags']['popLabel']] for cell in s.net.allCells}  # dict with color for each gid
    spkidColors = [gidColors[spkid] for spkid in s.allSimData['spkid']]

    print popColors

    figure() # Open a new figure
    fontsiz = 12
    scatter(s.allSimData['spkt'],s.allSimData['spkid'], 10, linewidths=1, marker='|', color = spkidColors) # Create raster  
    xlabel('Time (ms)', fontsize=fontsiz)
    ylabel('Cell ID', fontsize=fontsiz)
    title('cells=%i syns/cell=%0.1f rate=%0.1f Hz' % (s.numCells,s.connsPerCell,s.firingRate), fontsize=fontsiz)
    xlim(0,s.cfg['duration'])
    ylim(0,s.numCells)
    for popLabel in popLabels:
        plot(0,0,color=popColors[popLabel],label=popLabel)
    legend(fontsize=fontsiz)
    plottime = time()-plotstart # See how long it took
    print('  Done; plotting time = %0.1f s' % plottime)

def plotRasterYfrac(): # allspiketimes, allspikecells, EorI, ncells, connspercell, backgroundweight, firingrate, duration): # Define a function for plotting a raster
    plotstart = time() # See how long it takes to plot
    
    # reorder cells as func of yfrac
    yfracs = [cell['tags']['yfrac'] for cell in s.net.allCells]
    gids = [cell['gid'] for cell in s.net.allCells]
    sortInds = sorted(range(len(yfracs)), key=lambda k:yfracs[k])
    posdic={gid: pos for gid,pos in zip(gids,sortInds)}

    # plot cells types with different colors
    from  collections import OrderedDict
    colors = OrderedDict()
    dark=0.9
    colors['IT'] = [1,1,1]#[0.90*dark,0.76*dark,0.00]
    colors['PT'] = [0.90*dark,0.32*dark,0.00]
    colors['CT'] = [1,1,1]#[0.90*dark,0.59*dark,0.00]
    colors['SOM'] = [1,1,1]#[0.42*dark,0.83*dark,0.59*dark]
    colors['PV'] = [1,1,1]#[0.42*dark,0.67*dark,0.84*dark]

    cellcolors = [colors[cell['tags']['cellType']] for cell in s.net.allCells]
    colordic = {gid: color for gid,color in zip(gids,cellcolors)}

    fontsi=16;
    figure() # Open a new figure
    scatter(s.allSimData['spkt'],[posdic[gid] for gid in s.allSimData['spkid']],10,linewidths=1.5,marker='|',color=[colordic[gid] for gid in s.allSimData['spkid']]) # Create raster  
    xlabel('Time (ms)', fontsize=fontsi )
    ylabel('Cell id (arranged by NCD)', fontsize=fontsi)
    title('cells=%i, synapses=%i, rate=%0.1f Hz' % (s.numCells,s.totalConnections,s.firingRate),fontsize=fontsi)
    xlim(0,s.cfg['duration'])
    ylim(0,s.numCells)
    for k,v in colors.iteritems():
        plot(0,0,color=v,label=k)
    legend(fontsize=fontsi)
    plottime = time()-plotstart # See how long it took
    print('  Done; plotting time = %0.1f s' % plottime)


## Plot power spectra density
def plotPsd():
    colorspsd=array([[0.42,0.67,0.84],[0.42,0.83,0.59],[0.90,0.76,0.00],[0.90,0.32,0.00],[0.34,0.67,0.67],[0.42,0.82,0.83],[0.90,0.59,0.00],[0.33,0.67,0.47],[1.00,0.85,0.00],[0.71,0.82,0.41],[0.57,0.67,0.33],[1.00,0.38,0.60],[0.5,0.2,0.0],[0.0,0.2,0.5]]) 

    lfpv=[[] for c in range(len(s.lfppops))]    
    # Get last modified .mat file if no input and plot
    for c in range(len(s.lfppops)):
        lfpv[c] = s.lfps[:,c]    
    lfptot = sum(lfpv)
        
    # plot pops separately
    plotPops = 0
    if plotPops:    
        figure() # Open a new figure
        for p in range(len(s.lfppops)):
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
    totalconns = zeros(shape(s.connprobs))
    for c1 in range(size(s.connprobs,0)):
        for c2 in range(size(s.connprobs,1)):
            for w in range(s.nreceptors):
                totalconns[c1,c2] += s.connprobs[c1,c2]*s.connweights[c1,c2,w]*(-1 if w>=2 else 1)
    imshow(totalconns,interpolation='nearest',cmap=bicolormap(gap=0))

    # Plot grid lines
    hold(True)
    for pop in range(s.npops):
        plot(array([0,s.npops])-0.5,array([pop,pop])-0.5,'-',c=(0.7,0.7,0.7))
        plot(array([pop,pop])-0.5,array([0,s.npops])-0.5,'-',c=(0.7,0.7,0.7))

    # Make pretty
    h.set_xticks(range(s.npops))
    h.set_yticks(range(s.npops))
    h.set_xticklabels(s.popnames)
    h.set_yticklabels(s.popnames)
    h.xaxis.set_ticks_position('top')
    xlim(-0.5,s.npops-0.5)
    ylim(s.npops-0.5,-0.5)
    clim(-abs(totalconns).max(),abs(totalconns).max())
    colorbar()
    #show()


## Plot weight changes
def plotWeightChanges():
    if s.usestdp:
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
        wcs = [x[-1][-1] for x in s.allweightchanges] # absolute final weight
        wcs = [x[-1][-1]-x[0][-1] for x in s.allweightchanges] # absolute weight change
        pre,post,recep = zip(*[(x[0],x[1],x[2]) for x in s.allstdpconndata])
        ncells = int(max(max(pre),max(post))+1)
        wcmat = zeros([ncells, ncells])

        for iwc,ipre,ipost,irecep in zip(wcs,pre,post,recep):
            wcmat[int(ipre),int(ipost)] = iwc *(-1 if irecep>=2 else 1)

        # plot
        imshow(wcmat,interpolation='nearest',cmap=bicolormap(gap=0,mingreen=0.2,redbluemix=0.1,epsilon=0.01))
        xlabel('post-synaptic cell id')
        ylabel('pre-synaptic cell id')
        h.set_xticks(s.popGidStart)
        h.set_yticks(s.popGidStart)
        h.set_xticklabels(s.popnames)
        h.set_yticklabels(s.popnames)
        h.xaxis.set_ticks_position('top')
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

    #print len(s.xlocs),len(s.ylocs),len(s.zlocs)
    xlocs =[1,2,3]
    ylocs=[3,2,1]
    zlocs=[0.1,0.5,1.2]
    ax.scatter(xlocs,ylocs, zlocs,  s=10, c=zlocs, edgecolors='none',cmap = 'jet_r' , linewidths=0.0, alpha=1, marker='o')
    azim = 40  
    elev = 60
    ax.view_init(elev, azim) 
    #xlim(min(s.xlocs),max(s.xlocs))
    #ylim(min(s.ylocs),max(s.ylocs))
    #ax.set_zlim(min(s.zlocs),max(s.zlocs))
    xlabel('lateral distance (mm)')
    ylabel('lateral distance (mm)')
    ylabel('cortical depth (mm)')
