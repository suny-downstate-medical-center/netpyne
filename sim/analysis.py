"""
analysis.py

Functions to plot and analyse results

Version: 2014July9
"""
from pylab import scatter, figure, hold, subplot, axes, shape, imshow, colorbar, plot, xlabel, ylabel, title, xlim, ylim, clim, show, zeros, legend, savefig, cm, specgram, get_cmap
from scipy.io import loadmat
from scipy import loadtxt, size, array, linspace, ceil
from datetime import datetime
from time import time
import shared as s

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

def plotraster(): # allspiketimes, allspikecells, EorI, ncells, connspercell, backgroundweight, firingrate, duration): # Define a function for plotting a raster
    plotstart = time() # See how long it takes to plot
    EorIcolors = array([(1,0.4,0) , (0,0.2,0.8)]) # Define excitatory and inhibitory colors -- orange and turquoise
    cellcolors = EorIcolors[array(s.EorI)[array(s.allspikecells,dtype=int)]] # Set each cell to be either orange or turquoise
    figure() # Open a new figure
    scatter(s.allspiketimes,s.allspikecells,10,cellcolors,linewidths=0.5,marker='|') # Create raster  
    xlabel('Time (ms)')
    ylabel('Cell ID')
    title('cells=%i syns/cell=%0.1f noise=%0.1f rate=%0.1f Hz' % (s.ncells,s.connspercell,s.backgroundweight[0],s.firingrate),fontsize=12)
    xlim(0,s.duration)
    ylim(0,s.ncells)
    plottime = time()-plotstart # See how long it took
    print('  Done; time = %0.1f s' % plottime)
    #show()


## For diagnostic purposes -- plot connectivity. Based on conndiagram.py.
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
	wcs = [x[-1][-1] for x in s.weightchanges]
	pre,post,recep = zip(*[(x[0],x[1],x[2]) for x in s.allstdpconndata])
	ncells = int(max(max(pre),max(post))+1)
	wcmat = zeros([ncells, ncells])
	for iwc,ipre,ipost,irecep in zip(wcs,pre,post,recep):
		wcmat[ipre,ipost] = iwc *(-1 if irecep>=2 else 1)

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
