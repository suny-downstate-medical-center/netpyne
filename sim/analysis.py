"""
analysis.py

Functions to plot and analyse results

Version: 2014July9
"""
from pylab import mean, arange, bar, vstack,scatter, figure, hold, isscalar, gca, unique, subplot, axes, shape, imshow, colorbar, plot, xlabel, ylabel, title, xlim, ylim, clim, show, zeros, legend, savefig, cm, specgram, get_cmap
from scipy.io import loadmat
from scipy import loadtxt, size, array, linspace, ceil
from datetime import datetime
from time import time
import csv
import pickle
import shared as s
from mpl_toolkits.mplot3d import Axes3D

###############################################################################
### Simulation-related graph plotting functions
###############################################################################

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


###############################################################################
### Evolutionary-algorithm analysis/plotting functions
###############################################################################

#%% plot filled error bars
def errorfill(x, y, yerr, lw=1, elinewidth=1, color=None, alpha_fill=0.2, ax=None):
    ax = ax if ax is not None else gca()
    if color is None:
        color = ax._get_lines.color_cycle.next()
    if isscalar(yerr) or len(yerr) == len(y):
        ymin = y - yerr
        ymax = y + yerr
    elif len(yerr) == 2:
        ymin, ymax = yerr
    ax.plot(x, y, color=color, lw=lw)
    ax.fill_between(x, ymax, ymin, color=color, lw= elinewidth, alpha=alpha_fill)

#%% function to obtain unique list of lists
def uniqueList(seq): 
    seen = {}
    result = []
    indices = []
    for index,item in enumerate(seq):
        marker = tuple(item)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
        indices.append(index)
    return result,indices
                
#%% function to read data               
def loadData(folder, islands, dataFrom):
    #%% Load data from files
    if islands > 1:
        ind_gens_isl=[] # individuals data for islands
        ind_cands_isl=[]
        ind_fits_isl=[]
        ind_cs_isl=[]
            
        stat_gens_isl=[] # statistics.csv for islands
        stat_worstfits_isl=[]
        stat_bestfits_isl=[]
        stat_avgfits_isl=[]
        stat_stdfits_isl=[]
        
        fits_sort_isl=[] #sorted data
        gens_sort_isl=[] 
        cands_sort_isl=[]
        params_sort_isl=[]
    
    for island in range(islands):
        ind_gens=[] # individuals data
        ind_cands=[]
        ind_fits=[]
        ind_cs=[]
        
        eval_gens=[] # error files for each evaluation
        eval_cands=[]
        eval_fits=[]
        eval_params=[]
        
        stat_gens=[] # statistics.csv 
        stat_worstfits=[]
        stat_bestfits=[]
        stat_avgfits=[]
        stat_stdfits=[]
        
        if islands > 0:
            folderFinal = folder+"_island_"+str(island)
        else: 
            folderFinal = folder
            
        with open('../data/%s/individuals.csv'% (folderFinal)) as f: # read individuals.csv
            reader=csv.reader(f)
            for row in reader:
                ind_gens.append(int(row[0]))
                ind_cands.append(int(row[1]))
                ind_fits.append(float(row[2]))
                cs = [float(row[i].replace("[","").replace("]","")) for i in range(3,len(row))]
                ind_cs.append(cs)
        
        with open('../data/%s/statistics.csv'% (folderFinal)) as f: # read statistics.csv
            reader=csv.reader(f)
            for row in reader:
                stat_gens.append(float(row[0]))
                stat_worstfits.append(float(row[2]))
                stat_bestfits.append(float(row[3]))
                stat_avgfits.append(float(row[4]))
                stat_stdfits.append(float(row[6]))
        
        # unique generation number (sometimes repeated due to rerunning in hpc)
        stat_gens, stat_gens_indices = unique(stat_gens,1) # unique individuals
        stat_worstfits, stat_bestfits, stat_avgfits, stat_stdfits = zip(*[[stat_worstfits[i], stat_bestfits[i], stat_avgfits[i], stat_stdfits[i]] for i in stat_gens_indices])
        
        if dataFrom == 'fitness':       
            for igen in range(max(ind_gens)): # read error files from evaluations
                for ican in range(max(ind_cands)):
                    try:
                        f=open('../data/%s/gen_%d_cand_%d_error'%(folderFinal, igen,ican)); 
                        eval_fits.append(pickle.load(f))
                        f=open('../data/%s/gen_%d_cand_%d_params'%(folderFinal, igen,ican)); 
                        eval_params.append(pickle.load(f))
                        eval_gens.append(igen)
                        eval_cands.append(ican)
                    except:
                             pass
                        #eval_fits.append(0.15)
                        #eval_params.append([])
        
        # find x corresponding to smallest error from function evaluations  
        if dataFrom == 'fitness':
            #fits_sort, fits_sort_indices, fits_sort_origind = unique(eval_fits, True, True)
            fits_sort_indices = sorted(range(len(eval_fits)), key=lambda k: eval_fits[k])
            fits_sort = [eval_fits[i] for i in fits_sort_indices]
            gens_sort = [eval_gens[i] for i in fits_sort_indices]
            cands_sort = [eval_cands[i] for i in fits_sort_indices]
            params_sort = [eval_params[i] for i in fits_sort_indices]
        # find x corresponding to smallest error from individuals file
        elif dataFrom == 'individuals':
            params_unique, unique_indices = uniqueList(ind_cs) # unique individuals
            fits_unique = [ind_fits[i] for i in unique_indices]
            gens_unique = [ind_gens[i] for i in unique_indices]
            cands_unique = [ind_cands[i] for i in unique_indices]
            
            sort_indices = sorted(range(len(fits_unique)), key=lambda k: fits_unique[k]) # sort fits
            fits_sort = [fits_unique[i] for i in sort_indices]
            gens_sort = [gens_unique[i] for i in sort_indices]
            cands_sort = [cands_unique[i] for i in sort_indices]
            params_sort = [params_unique[i] for i in sort_indices]
        
        # if multiple islands, save data for each
        if islands > 1:
            ind_gens_isl.append(ind_gens) # individuals data for islands
            ind_cands_isl.append(ind_cands)
            ind_fits_isl.append(ind_fits)
            ind_cs_isl.append(ind_cs)
                
            stat_gens_isl.append(stat_gens) # statistics.csv for islands
            stat_worstfits_isl.append(stat_worstfits)
            stat_bestfits_isl.append(stat_bestfits)
            stat_avgfits_isl.append(stat_avgfits)
            stat_stdfits_isl.append(stat_stdfits)
            
            fits_sort_isl.append(fits_sort) #sorted data
            gens_sort_isl.append(gens_sort) 
            cands_sort_isl.append(cands_sort)
            params_sort_isl.append(params_sort)
            
    if islands > 1:
        return ind_gens_isl, ind_cands_isl, ind_fits_isl, ind_cs_isl, stat_gens_isl, \
            stat_worstfits_isl, stat_bestfits_isl, stat_avgfits_isl, stat_stdfits_isl, \
            fits_sort_isl, gens_sort_isl, cands_sort_isl, params_sort_isl

