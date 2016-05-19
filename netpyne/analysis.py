"""
analysis.py

Functions to plot and analyse results

Contributors: salvadordura@gmail.com
"""

from pylab import arange, scatter, figure, hold, subplot, subplots, axes, shape, imshow, colorbar, plot, xlabel, ylabel, title, xlim, ylim, clim, show, zeros, legend, savefig, psd, ion, subplots_adjust
from scipy.io import loadmat
from scipy import loadtxt, size, array, linspace, ceil
from datetime import datetime
from time import time
from collections import OrderedDict
import csv
import pickle
from mpl_toolkits.mplot3d import Axes3D

import framework as f

###############################################################################
### Simulation-related graph plotting functions
###############################################################################

# sequence of generic plots (raster, connectivity,psd,...)
def plotData():
    ## Plotting
    if f.rank == 0:
        f.sim.timing('start', 'plotTime')
        if f.cfg['plotRaster']: # Whether or not to plot
            if (f.totalSpikes>f.cfg['maxspikestoplot']): 
                print('  Too many spikes (%i vs. %i)' % (f.totalSpikes, f.cfg['maxspikestoplot'])) # Plot raster, but only if not too many spikes
            else: 
                print('Plotting raster...')
                f.analysis.plotRaster() 
        if f.cfg['plotCells']:
            print('Plotting recorded traces ...')
            f.analysis.plotTraces() 
        if f.cfg['plotConn']:
            print('Plotting connectivity matrix...')
            f.analysis.plotConn()
        if f.cfg['plotLFPSpectrum']:
            print('Plotting LFP power spectral density')
            f.analysis.plotLFPSpectrum()
        if f.cfg['plot2Dnet']:
            print('Plotting 2D visualization of network...')
            f.analysis.plot2Dnet()  
        if f.cfg['plotWeightChanges']:
            print('Plotting weight changes...')
            f.analysis.plotWeightChanges()
        if f.cfg['plot3dArch']:
            print('Plotting 3d architecture...')
            f.analysis.plot3dArch()
        if f.cfg['timing']:
            f.sim.timing('stop', 'plotTime')
            print('  Done; plotting time = %0.2f s' % f.timing['plotTime'])
            f.sim.timing('stop', 'totalTime')
            print('\nTotal time = %0.2f s' % f.timing['totalTime'])
        show(block=False)

## Raster plot 
def plotRaster(): 
    colorList = [[0.42,0.67,0.84], [0.90,0.76,0.00], [0.42,0.83,0.59], [0.90,0.32,0.00],
                [0.34,0.67,0.67], [0.90,0.59,0.00], [0.42,0.82,0.83], [1.00,0.85,0.00],
                [0.33,0.67,0.47], [1.00,0.38,0.60], [0.57,0.67,0.33], [0.5,0.2,0.0],
                [0.71,0.82,0.41], [0.0,0.2,0.5]] 
    popLabels = [pop.tags['popLabel'] for pop in f.net.pops if pop.tags['cellModel'] not in ['NetStim']]
    popColors = {popLabel: colorList[ipop%len(colorList)] for ipop,popLabel in enumerate(popLabels)} # dict with color for each pop
    gidColors = {cell['gid']: popColors[cell['tags']['popLabel']] for cell in f.net.allCells}  # dict with color for each gid
    spkids = f.allSimData['spkid']
    ylabelText = 'Cell id'
    spkidColors = [gidColors[spkid] for spkid in spkids]
    try:
        if f.cfg['orderRasterYnorm']:
            gids = [cell['gid'] for cell in f.net.allCells]
            ynorms = [cell['tags']['ynorm'] for cell in f.net.allCells]
            sortInds = sorted(range(len(ynorms)), key=lambda k:ynorms[k])
            posdic = {gid: pos for gid,pos in zip(gids,sortInds)}
            spkids = [posdic[gid] for gid in spkids]  # spkids now contain indices ordered according to ynorm
            ylabelText = 'Cell id (arranged by NCD)'
    except:
        pass     
    figure(figsize=(10,8)) # Open a new figure
    fontsiz = 12
    scatter(f.allSimData['spkt'], spkids, 10, linewidths=1.5, marker='|', color = spkidColors) # Create raster  
    xlabel('Time (ms)', fontsize=fontsiz)
    ylabel(ylabelText, fontsize=fontsiz)
    title('cells=%i syns/cell=%0.1f rate=%0.1f Hz' % (f.numCells,f.connsPerCell,f.firingRate), fontsize=fontsiz)
    xlim(0,f.cfg['duration'])
    ylim(0,f.numCells)
    for popLabel in popLabels[::-1]:
        plot(0,0,color=popColors[popLabel],label=popLabel)
    legend(fontsize=fontsiz, bbox_to_anchor=(1.02, 1), loc=2, borderaxespad=0.)
    maxLabelLen = max([len(l) for l in popLabels])
    subplots_adjust(right=(0.9-0.01*maxLabelLen))
    #savefig('raster.png')

## Traces (v,i,g etc) plot
def plotTraces(): 
    tracesList = f.cfg['recordTraces'].keys()
    tracesList.sort()
    gidList = [trace for trace in f.cfg['plotCells'] if isinstance(trace, int)]
    popList = [trace for trace in f.cfg['plotCells'] if isinstance(trace, str)]
    if 'all' in popList:
        gidList = [cell.gid for cell in f.net.allCell]
        popList = []
    duration = f.cfg['duration']
    recordStep = f.cfg['recordStep']

    for gid in gidList:
        figure() # Open a new figure
        fontsiz = 12
        for itrace, trace in enumerate(tracesList):
            try:
                data = f.allSimData[trace]['cell_'+str(gid)]
                t = arange(0, duration+recordStep, recordStep)
                subplot(len(tracesList),1,itrace+1)
                plot(t, data, linewidth=1.5)
                xlabel('Time (ms)', fontsize=fontsiz)
                ylabel(trace, fontsize=fontsiz)
                xlim(0,f.cfg['duration'])
            except:
                pass
        if tracesList: subplot(len(tracesList),1,1)
        title('Cell %d'%(int(gid)))

    for popLabel in popList:
        fontsiz = 12
        for pop in f.net.pops:
            if pop.tags['popLabel'] == popLabel and pop.cellGids:
                figure() # Open a new figure
                gid = pop.cellGids[0] 
                for itrace, trace in enumerate(tracesList):
                    try:
                        data = f.allSimData[trace]['cell_'+str(gid)]
#                        print(data)
#                        print len(data)
#                        wait = input('Current data printed')
                        t = arange(0, len(data)*recordStep, recordStep)
                        subplot(len(tracesList),1,itrace+1)
                        plot(t, data, linewidth=1.5)
                        xlabel('Time (ms)', fontsize=fontsiz)
                        ylabel(trace, fontsize=fontsiz)
                        xlim(0,f.cfg['duration'])
                    except:
                        pass
        subplot(len(tracesList),1,1)
        title('Pop %s, Cell %d'%(popLabel, int(gid)))
    #savefig('traces.png')


## Plot power spectra density
def plotLFPSpectrum():
#    colorspsd=array([[0.42,0.67,0.84],[0.42,0.83,0.59],[0.90,0.76,0.00],[0.90,0.32,0.00],[0.34,0.67,0.67],[0.42,0.82,0.83],[0.90,0.59,0.00],[0.33,0.67,0.47],[1.00,0.85,0.00],[0.71,0.82,0.41],[0.57,0.67,0.33],[1.00,0.38,0.60],[0.5,0.2,0.0],[0.0,0.2,0.5]]) 
    
    import math
    import numpy as np
    #Electrode positions
    electrode_x = [50]*3
    electrode_y = [50]*3
    electrode_z = [30, 60, 90] 
    num_e = len(electrode_x)
    dur = int(f.testTime)
    
    
    #Weighted sum of synapse currents
    SynCurrents = {'NMDA': {},
                   'AMPA': {},
                   'GABA': {}}
    for cell in f.net.cells:
        if cell.conns:
            syn_type = cell.conns[0]['synMech']
            if 'cell_'+str(cell.gid) in f.allSimData['I']:            
#                SynCurrents[syn_type][cell.gid] = f.allSimData['I']['cell_'+str(cell.gid)]
                SynCurrents[syn_type][cell.gid] = {}                
                r = [0]*num_e
                for t in range(0,num_e):
                    r[t] = ((electrode_x[t]-cell.tags.get('x'))**2 + (electrode_y[t]-cell.tags.get('y'))**2 + (electrode_z[t]-cell.tags.get('z'))**2)**1/2
                    SynCurrents[syn_type][cell.gid][str(t)] = np.array(f.allSimData['I']['cell_'+str(cell.gid)])*math.exp(-(1./100)*r[t])
            
            if 'cell_'+str(cell.gid) in f.allSimData['NMDA_i']:
                SynCurrents['NMDA'][cell.gid] = {}
                r = [0]*num_e
                for t in range(0,num_e):
                    r[t] = ((electrode_x[t]-cell.tags.get('x'))**2 + (electrode_y[t]-cell.tags.get('y'))**2 + (electrode_z[t]-cell.tags.get('z'))**2)**1/2
                    SynCurrents['NMDA'][cell.gid][str(t)] = np.array(f.allSimData['NMDA_i']['cell_'+str(cell.gid)])*math.exp(-(1./100)*r[t])
                    
            if 'cell_'+str(cell.gid) in f.allSimData['GABA_i']:
                SynCurrents['GABA'][cell.gid] = {}
                r = [0]*num_e
                for t in range(0,num_e):
                    r[t] = ((electrode_x[t]-cell.tags.get('x'))**2 + (electrode_y[t]-cell.tags.get('y'))**2 + (electrode_z[t]-cell.tags.get('z'))**2)**1/2
                    SynCurrents['GABA'][cell.gid][str(t)] = np.array(f.allSimData['GABA_i']['cell_'+str(cell.gid)])*math.exp(-(1./100)*r[t])
                    
        elif cell.stims:
#            print cell.stims[0]
            syn_type = cell.stims[0]['synMech']
            if 'cell_'+str(cell.gid) in f.allSimData['I']: 
                SynCurrents[syn_type][cell.gid] = {}                
                r = [0]*3
                for t in range(0,num_e):
                    r[t] = ((electrode_x[t]-cell.tags.get('x'))**2 + (electrode_y[t]-cell.tags.get('y'))**2 + (electrode_z[t]-cell.tags.get('z'))**2)**1/2
                    SynCurrents[syn_type][cell.gid][str(t)] = np.array(f.allSimData['I']['cell_'+str(cell.gid)])*math.exp(-(1./100)*r[t])
                    
            if 'cell_'+str(cell.gid) in f.allSimData['NMDA_i']:
                SynCurrents['NMDA'][cell.gid] = {}
                r = [0]*num_e
                for t in range(0,num_e):
                    r[t] = ((electrode_x[t]-cell.tags.get('x'))**2 + (electrode_y[t]-cell.tags.get('y'))**2 + (electrode_z[t]-cell.tags.get('z'))**2)**1/2
                    SynCurrents['NMDA'][cell.gid][str(t)] = np.array(f.allSimData['NMDA_i']['cell_'+str(cell.gid)])*math.exp(-(1./100)*r[t])
                    
            if 'cell_'+str(cell.gid) in f.allSimData['GABA_i']:
                SynCurrents['GABA'][cell.gid] = {}
                r = [0]*num_e
                for t in range(0,num_e):
                    r[t] = ((electrode_x[t]-cell.tags.get('x'))**2 + (electrode_y[t]-cell.tags.get('y'))**2 + (electrode_z[t]-cell.tags.get('z'))**2)**1/2
                    SynCurrents['GABA'][cell.gid][str(t)] = np.array(f.allSimData['GABA_i']['cell_'+str(cell.gid)])*math.exp(-(1./100)*r[t])
            

    
    N_const = 1
    A_const = 1
    G_const = 1.65    
    
    AMPA_currents=[[0]*dur,[0]*dur,[0]*dur]
    for key,val in SynCurrents['AMPA'].iteritems():
        for el,meas in val.iteritems():        
            iterator = 0        
            for n in meas:        
                AMPA_currents[int(el)][iterator] = AMPA_currents[int(el)][iterator] + n
                iterator += 1
    
    NMDA_currents=[[0]*dur,[0]*dur,[0]*dur]
    for key,val in SynCurrents['NMDA'].iteritems():
        for el,meas in val.iteritems():        
            iterator = 0        
            for n in meas:        
                NMDA_currents[int(el)][iterator] = NMDA_currents[int(el)][iterator] + n
                iterator += 1
        
    GABA_currents=[[0]*dur,[0]*dur,[0]*dur]
    for key,val in SynCurrents['NMDA'].iteritems():
        for el,meas in val.iteritems():        
            iterator = 0        
            for n in meas:        
                GABA_currents[int(el)][iterator] = GABA_currents[int(el)][iterator] + n
                iterator += 1
    
    N_delay = 0
    A_delay = 6
    G_delay = 0
    
    for el in range(num_e):
        AMPA_currents[el]=[0]*A_delay + AMPA_currents[el]
        NMDA_currents[el]=[0]*N_delay + NMDA_currents[el]
        GABA_currents[el]=[0]*G_delay + GABA_currents[el]
    

    
    empty = np.array([0.]*dur)    
    f.Sum_Currents = np.array([empty]*num_e)
    for el in range(num_e):        
        for t in range(0,dur):
             f.Sum_Currents[el][t] = A_const*AMPA_currents[el][t] + N_const*NMDA_currents[el][t] - G_const*GABA_currents[el][t]

    
#   Normalise Weighted Sum
    for el in range(num_e):     
        for iters in range(len(f.Sum_Currents[el])):
            f.Sum_Currents[el][iters] = f.Sum_Currents[el][iters] - (1./1000)*sum(f.Sum_Currents[el])
    
#    Plot the LFP signal from all electrodes
    g, axarr = subplots(num_e, sharex=True)
    xlabel('Time (ms)')
    ylabel('LFP')
    for el in range(num_e):
        x = np.array(range(dur))
        axarr[el].plot(x, f.Sum_Currents[el], color='b')
#        axarr[el].ylabel('Electrode '+str(el+1))
    
    
    
#    Sum_Currents
#    print Sum_Currents
#    print NMDA_currents
#    wait = input('sldkjf')

        
#    for pop in f.net.pops:
#        for gid in pop.cellGids:
#            data = f.allSimData['I']['cell_'+str(gid)]
#            data_one = {cell.gid: cell.tags for cell in f.net.cells}
            
    
    
#    lfpv=[[] for c in range(len(f.lfppops))]    
#    # Get last modified .mat file if no input and plot
#    for c in range(len(f.lfppops)):
#        lfpv[c] = f.lfps[:,c]    
#    lfptot = sum(lfpv)
#        
#    # plot pops separately
#    plotPops = 0
#    if plotPops:    
#        figure() # Open a new figure
#        for p in range(len(f.lfppops)):
#            psd(lfpv[p],Fs=200, linewidth= 2,color=colorspsd[p])
#            xlabel('Frequency (Hz)')
#            ylabel('Power')
#            h=axes()
#            h.set_yticklabels([])
#        legend(['L2/3','L5A', 'L5B', 'L6'])
#
#    # plot overall psd
#    figure() # Open a new figure
#    psd(lfptot,Fs=200, linewidth= 2)
#    xlabel('Frequency (Hz)')
#    ylabel('Power')
#    h=axes()
#    h.set_yticklabels([])
#
#    show()


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
    totalconns = zeros(shape(f.connprobs))
    for c1 in range(size(f.connprobs,0)):
        for c2 in range(size(f.connprobs,1)):
            for w in range(f.nreceptors):
                totalconns[c1,c2] += f.connprobs[c1,c2]*f.connweights[c1,c2,w]*(-1 if w>=2 else 1)
    imshow(totalconns,interpolation='nearest',cmap=bicolormap(gap=0))

    # Plot grid lines
    hold(True)
    for pop in range(f.npops):
        plot(array([0,f.npops])-0.5,array([pop,pop])-0.5,'-',c=(0.7,0.7,0.7))
        plot(array([pop,pop])-0.5,array([0,f.npops])-0.5,'-',c=(0.7,0.7,0.7))

    # Make pretty
    h.set_xticks(range(f.npops))
    h.set_yticks(range(f.npops))
    h.set_xticklabels(f.popnames)
    h.set_yticklabels(f.popnames)
    h.xaxis.set_ticks_position('top')
    xlim(-0.5,f.npops-0.5)
    ylim(f.npops-0.5,-0.5)
    clim(-abs(totalconns).max(),abs(totalconns).max())
    colorbar()
    #show()


# Plot 2D visualization of network cell positions and connections
def plot2Dnet():
    allCells = f.net.allCells
    figure(figsize=(12,12))
    colorList = [[0.42,0.67,0.84], [0.90,0.76,0.00], [0.42,0.83,0.59], [0.90,0.32,0.00],
                [0.34,0.67,0.67], [0.90,0.59,0.00], [0.42,0.82,0.83], [1.00,0.85,0.00],
                [0.33,0.67,0.47], [1.00,0.38,0.60], [0.57,0.67,0.33], [0.5,0.2,0.0],
                [0.71,0.82,0.41], [0.0,0.2,0.5]] 
    popLabels = [pop.tags['popLabel'] for pop in f.net.pops if pop.tags['cellModel'] not in ['NetStim']]
    popColors = {popLabel: colorList[ipop%len(colorList)] for ipop,popLabel in enumerate(popLabels)} # dict with color for each pop
    cellColors = [popColors[cell.tags['popLabel']] for cell in f.net.cells]
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


## Plot weight changes
def plotWeightChanges():
    if f.usestdp:
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
        wcs = [x[-1][-1] for x in f.allweightchanges] # absolute final weight
        wcs = [x[-1][-1]-x[0][-1] for x in f.allweightchanges] # absolute weight change
        pre,post,recep = zip(*[(x[0],x[1],x[2]) for x in f.allstdpconndata])
        ncells = int(max(max(pre),max(post))+1)
        wcmat = zeros([ncells, ncells])

        for iwc,ipre,ipost,irecep in zip(wcs,pre,post,recep):
            wcmat[int(ipre),int(ipost)] = iwc *(-1 if irecep>=2 else 1)

        # plot
        imshow(wcmat,interpolation='nearest',cmap=bicolormap(gap=0,mingreen=0.2,redbluemix=0.1,epsilon=0.01))
        xlabel('post-synaptic cell id')
        ylabel('pre-synaptic cell id')
        h.set_xticks(f.popGidStart)
        h.set_yticks(f.popGidStart)
        h.set_xticklabels(f.popnames)
        h.set_yticklabels(f.popnames)
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

    #print len(f.xlocs),len(f.ylocs),len(f.zlocs)
    xlocs =[1,2,3]
    ylocs=[3,2,1]
    zlocs=[0.1,0.5,1.2]
    ax.scatter(xlocs,ylocs, zlocs,  s=10, c=zlocs, edgecolors='none',cmap = 'jet_r' , linewidths=0.0, alpha=1, marker='o')
    azim = 40  
    elev = 60
    ax.view_init(elev, azim) 
    #xlim(min(f.xlocs),max(f.xlocs))
    #ylim(min(f.ylocs),max(f.ylocs))
    #ax.set_zlim(min(f.zlocs),max(f.zlocs))
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
