"""
analysis.py

Functions to plot and analyse results

Version: 2014July9
"""
from pylab import scatter, figure, hold, subplot, axes, shape, imshow, colorbar, plot, xlabel, ylabel, title, xlim, ylim, clim, show, zeros, legend, savefig, cm, specgram, get_cmap
from scipy.io import loadmat
from scipy import loadtxt, size, array, linspace, ceil
from bicolormap import bicolormap
from datetime import datetime
from time import time

def plotraster(allspiketimes, allspikecells, EorI, ncells, connspercell, backgroundweight, firingrate, duration): # Define a function for plotting a raster
    plotstart = time() # See how long it takes to plot
    EorIcolors = array([(1,0.4,0) , (0,0.2,0.8)]) # Define excitatory and inhibitory colors -- orange and turquoise
    cellcolors = EorIcolors[array(EorI)[array(allspikecells,dtype=int)]] # Set each cell to be either orange or turquoise
    figure() # Open a new figure
    scatter(allspiketimes,allspikecells,10,cellcolors,linewidths=0.5,marker='|') # Create raster  
    xlabel('Time (ms)')
    ylabel('Cell ID')
    title('cells=%i syns/cell=%0.1f noise=%0.1f rate=%0.1f Hz' % (ncells,connspercell,backgroundweight[0],firingrate),fontsize=12)
    xlim(0,duration)
    ylim(0,ncells)
    plottime = time()-plotstart # See how long it took
    print('  Done; time = %0.1f s' % plottime)
    #show()


## For diagnostic purposes -- plot connectivity. Based on conndiagram.py.
def plotconn(p):
    # Create plot
    figh = figure(figsize=(8,6))
    figh.subplots_adjust(left=0.02) # Less space on left
    figh.subplots_adjust(right=0.98) # Less space on right
    figh.subplots_adjust(top=0.96) # Less space on bottom
    figh.subplots_adjust(bottom=0.02) # Less space on bottom
    figh.subplots_adjust(wspace=0) # More space between
    figh.subplots_adjust(hspace=0) # More space between
    h = axes()
    connprobs = p.setconnprobs()
    connweights = p.setconnweights()
    npops = p.npops
    popnames = p.popnames
    totalconns = zeros(shape(connprobs))
    for c1 in range(size(connprobs,0)):
        for c2 in range(size(connprobs,1)):
            for w in range(p.nreceptors):
                totalconns[c1,c2] += connprobs[c1,c2]*connweights[c1,c2,w]*(-1 if w>=2 else 1)
    imshow(totalconns,interpolation='nearest',cmap=bicolormap(gap=0))

    # Plot grid lines
    hold(True)
    for pop in range(npops):
        plot(array([0,npops])-0.5,array([pop,pop])-0.5,'-',c=(0.7,0.7,0.7))
        plot(array([pop,pop])-0.5,array([0,npops])-0.5,'-',c=(0.7,0.7,0.7))

    # Make pretty
    h.set_xticks(range(npops))
    h.set_yticks(range(npops))
    h.set_xticklabels(popnames)
    h.set_yticklabels(popnames)
    h.xaxis.set_ticks_position('top')
    xlim(-0.5,npops-0.5)
    ylim(npops-0.5,-0.5)
    clim(-abs(totalconns).max(),abs(totalconns).max())
    colorbar()
    #show()

## Plot weight changes
def plotweightchanges(p, allconnections, stdpdata, weightchanges):
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
	wcs = [x[-1][-1] for x in weightchanges]
	pre,post,recep = zip(*[(x[0],x[1],x[2]) for x in stdpdata])
	ncells = int(max(max(pre),max(post))+1)
	wcmat = zeros([ncells, ncells])
	for iwc,ipre,ipost,irecep in zip(wcs,pre,post,recep):
		wcmat[ipre,ipost] = iwc *(-1 if irecep>=2 else 1)

	# plot
	imshow(wcmat,interpolation='nearest',cmap=bicolormap(gap=0,mingreen=0.2,redbluemix=0.1,epsilon=0.01))
	xlabel('post-synaptic cell id')
	ylabel('pre-synaptic cell id')
	h.set_xticks(p.popGidStart)
	h.set_yticks(p.popGidStart)
	h.set_xticklabels(p.popnames)
	h.set_yticklabels(p.popnames)
	h.xaxis.set_ticks_position('top')
	xlim(-0.5,ncells-0.5)
	ylim(ncells-0.5,-0.5)
	clim(-abs(wcmat).max(),abs(wcmat).max())
	colorbar()
	#show()
