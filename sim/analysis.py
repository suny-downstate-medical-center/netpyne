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
        if p.sim['plotraster']: # Whether or not to plot
            if (s.totalspikes>p.sim['maxspikestoplot']): 
                print('  Too many spikes (%i vs. %i)' % (s.totalspikes, s.maxspikestoplot)) # Plot raster, but only if not too many spikes
            else: 
                print('Plotting raster...')
                s.analysis.plotraster()#allspiketimes, allspikecells, EorI, ncells, connspercell, backgroundweight, firingrate, duration)
        if p.sim['plotconn']:
            print('Plotting connectivity matrix...')
            s.analysis.plotconn()
        if p.sim['plotpsd']:
            print('Plotting power spectral density')
            s.analysis.plotpsd()
        if p.sim['plotweightchanges']:
            print('Plotting weight changes...')
            s.analysis.plotweightchanges()
        if p.sim['plot3darch']:
            print('Plotting 3d architecture...')
            s.analysis.plot3darch()

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
def plotraster(): # allspiketimes, allspikecells, EorI, ncells, connspercell, backgroundweight, firingrate, duration): # Define a function for plotting a raster
    plotstart = time() # See how long it takes to plot
    #EorIcolors = array([(1,0.4,0) , (0,0.2,0.8)]) # Define excitatory and inhibitory colors -- orange and turquoise
    #cellcolors = EorIcolors[array(s.EorI)[array(s.allspikecells,dtype=int)]] # Set each cell to be either orange or turquoise
    figure() # Open a new figure
    scatter(s.allsimdata['spkt'],s.allsimdata['spkid'],10,linewidths=0.5,marker='|') # Create raster  
    xlabel('Time (ms)')
    ylabel('Cell ID')
    title('cells=%i syns/cell=%0.1f noise=%0.1f rate=%0.1f Hz' % (s.ncells,s.connspercell,p.net['backgroundWeight'][0],s.firingrate),fontsize=12)
    xlim(0,p.sim['duration'])
    ylim(0,s.ncells)
    plottime = time()-plotstart # See how long it took
    print('  Done; time = %0.1f s' % plottime)
    #show()

## Plot power spectra density
def plotpsd():
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
def plotconn():
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
def plotweightchanges():
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


## plot motor subpopulations connectivity changes
def plotmotorpopchanges():
    showInh = True
    if s.usestdp:
        Ewpre =  []
        Ewpost = []
        EwpreSum = []
        EwpostSum = []
        if showInh: 
            Iwpre =  []
            Iwpost = []
            IwpreSum = []
            IwpostSum = [] 
        for imus in range(len(s.motorCmdCellRange)):
            Ewpre.append([x[0][-1] for (icon,x) in enumerate(s.allweightchanges) if s.allstdpconndata[icon][1] in s.motorCmdCellRange[imus]])
            Ewpost.append([x[-1][-1] for (icon,x) in enumerate(s.allweightchanges) if s.allstdpconndata[icon][1] in s.motorCmdCellRange[imus]])
            EwpreSum.append(sum(Ewpre[imus]))
            EwpostSum.append(sum(Ewpost[imus]))
       

            if showInh:
                motorInhCellRange = s.motorCmdCellRange[imus] - s.popGidStart[s.EDSC] + s.popGidStart[s.IDSC]
                Iwpre.append([x[0][-1] for (icon,x) in enumerate(s.allweightchanges) if s.allstdpconndata[icon][1] in motorInhCellRange])
                Iwpost.append([x[-1][-1] for (icon,x) in enumerate(s.allweightchanges) if s.allstdpconndata[icon][1] in motorInhCellRange])
                IwpreSum.append(sum(Iwpre[imus]))
                IwpostSum.append(sum(Iwpost[imus]))

        print '\ninitial E weights: ',EwpreSum
        print 'final E weigths: ',EwpostSum
        print 'absolute E difference: ',array(EwpostSum) - array(EwpreSum)
        print 'relative E difference: ',(array(EwpostSum) - array(EwpreSum)) / array(EwpreSum)

        if showInh:
            print '\ninitial I weights: ',IwpreSum
            print 'final I weigths: ',IwpostSum
            print 'absolute I difference: ',array(IwpostSum) - array(IwpreSum)
            print 'relative I difference: ',(array(IwpostSum) - array(IwpreSum)) / array(IwpreSum)
            

        # plot
        figh = figure(figsize=(1.2*8,1.2*6))
        ax1 = figh.add_subplot(2,1,1)
        ind = arange(len(EwpreSum))  # the x locations for the groups
        width = 0.35       # the width of the bars
        ax1.bar(ind, EwpreSum, width, color='b')
        ax1.bar(ind+width, EwpostSum, width, color='r')
        ax1.set_xticks(ind+width)
        ax1.set_xticklabels( ('shext','shflex','elext','elflex') )
        #legend(['pre','post'])
        ax1.grid()

        ax2 = figh.add_subplot(2,1,2)
        width = 0.70       # the width of the bars
        bar(ind,(array(EwpostSum) - array(EwpreSum)) / array(EwpreSum), width, color='b')
        ax2.set_xticks(ind+width/2)
        ax2.set_xticklabels( ('shext','shflex','elext','elflex') )
        ax2.grid()

        if showInh:
            figh = figure(figsize=(1.2*8,1.2*6))
            ax1 = figh.add_subplot(2,1,1)
            ind = arange(len(IwpreSum))  # the x locations for the groups
            width = 0.35       # the width of the bars
            ax1.bar(ind, IwpreSum, width, color='b')
            ax1.bar(ind+width, IwpostSum, width, color='r')
            ax1.set_xticks(ind+width)
            ax1.set_xticklabels( ('shext','shflex','elext','elflex') )
            legend(['pre','post'])
            ax1.grid()

            ax2 = figh.add_subplot(2,1,2)
            width = 0.70       # the width of the bars
            bar(ind,(array(IwpostSum) - array(IwpreSum)) / array(IwpreSum), width, color='b')
            ax2.set_xticks(ind+width/2)
            ax2.set_xticklabels( ('shext','shflex','elext','elflex') )
            ax2.grid()
        

## plot 3d architecture:
def plot3darch():
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
