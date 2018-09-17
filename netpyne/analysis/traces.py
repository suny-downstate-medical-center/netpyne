"""
analysis/spikes.py

Functions to plot and analyze traces-related results

Contributors: salvadordura@gmail.com
"""

from netpyne import __gui__

if __gui__:
    import matplotlib.pyplot as plt
import numpy as np
from .utils import colorList, _showFigure, exception, getCellsInclude


# -------------------------------------------------------------------------------------------------------------------
## Plot recorded cell traces (V, i, g, etc.)
# -------------------------------------------------------------------------------------------------------------------
@exception
def plotTraces (include = None, timeRange = None, overlay = False, oneFigPer = 'cell', rerun = False, colors = None, ylim = None, axis='on',
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
        - colors (list): List of normalized RGB colors to use for traces
        - ylim (list): Y-axis limits
        - axis ('on'|'off'): Whether to show axis or not; if not, then a scalebar is included (default: 'on')
        - figSize ((width, height)): Size of figure (default: (10,8))
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure; 
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure;
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)

        - Returns figure handles
    '''
    from .. import sim

    print('Plotting recorded cell traces ...')

    if include is None:  # if none, record from whatever was recorded
        if 'plotTraces' in sim.cfg.analysis and 'include' in sim.cfg.analysis['plotTraces']:
            include = sim.cfg.analysis['plotTraces']['include'] + sim.cfg.recordCells
        else:
            include = sim.cfg.recordCells
            
    global colorList
    if isinstance(colors, list): 
        colorList2 = colors
    else:
        colorList2 = colorList

    # rerun simulation so new include cells get recorded from
    if rerun: 
        cellsRecord = [cell.gid for cell in sim.getCellsList(include)]
        for cellRecord in cellsRecord:
            if cellRecord not in sim.cfg.recordCells:
                sim.cfg.recordCells.append(cellRecord)
        sim.setupRecording()
        sim.simulate()

    tracesList = sim.cfg.recordTraces.keys()
    tracesList.sort()
    cells, cellGids, _ = getCellsInclude(include)
    gidPops = {cell['gid']: cell['tags']['pop'] for cell in cells}

    # time range
    if timeRange is None:
        timeRange = [0,sim.cfg.duration]

    recordStep = sim.cfg.recordStep

    figs = {}
    tracesData = []

    # Plot one fig per trace for given cell list
    def plotFigPerTrace(subGids):
        for itrace, trace in enumerate(tracesList):
            figs['_trace_'+str(trace)] = plt.figure(figsize=figSize) # Open a new figure
            fontsiz = 2
            for igid, gid in enumerate(subGids):
                if 'cell_'+str(gid) in sim.allSimData[trace]:
                    data = sim.allSimData[trace]['cell_'+str(gid)][int(timeRange[0]/recordStep):int(timeRange[1]/recordStep)]
                    t = np.arange(timeRange[0], timeRange[1]+recordStep, recordStep)
                    tracesData.append({'t': t, 'cell_'+str(gid)+'_'+trace: data})
                    color = colorList2[igid%len(colorList2)]
                    if not overlay:
                        plt.subplot(len(subGids),1,igid+1)
                        plt.ylabel(trace, fontsize=fontsiz)
                    plt.plot(t[:len(data)], data, linewidth=1.5, color=color, label='Cell %d, Pop %s '%(int(gid), gidPops[gid]))
                    plt.xlabel('Time (ms)', fontsize=fontsiz)
                    plt.xlim(timeRange)
                    if ylim: plt.ylim(ylim)
                    plt.title('Cell %d, Pop %s '%(int(gid), gidPops[gid]))
                    
            if axis == 'off':  # if no axis, add scalebar
                ax = plt.gca()
                sizex =  (timeRange[1]-timeRange[0])/20.0
                # yl = plt.ylim()
                # plt.ylim(yl[0]-0.2*(yl[1]-yl[0]), yl[1])
                add_scalebar(ax, hidex=False, hidey=True, matchx=False, matchy=True, sizex=sizex, sizey=None, 
                    unitsx='ms', unitsy='mV', scalex=1, scaley=1, loc=1, pad=-1, borderpad=0.5, sep=4, prop=None, barcolor="black", barwidth=3)   
                plt.axis(axis) 

            if overlay:
                #maxLabelLen = 10
                #plt.subplots_adjust(right=(0.9-0.012*maxLabelLen)) 
                #plt.legend(fontsize=fontsiz, bbox_to_anchor=(1.04, 1), loc=2, borderaxespad=0.)
                plt.legend()

    # Plot one fig per cell
    if oneFigPer == 'cell':
        for gid in cellGids:
            figs['_gid_'+str(gid)] = plt.figure(figsize=figSize) # Open a new figure
            fontsiz = 12
            for itrace, trace in enumerate(tracesList):
                if 'cell_'+str(gid) in sim.allSimData[trace]:
                    fullTrace = sim.allSimData[trace]['cell_'+str(gid)]
                    if isinstance(fullTrace, dict):
                        data = [fullTrace[key][int(timeRange[0]/recordStep):int(timeRange[1]/recordStep)] for key in fullTrace.keys()]
                        lenData = len(data[0])
                        data = np.transpose(np.array(data))
                    else:
                        data = fullTrace[int(timeRange[0]/recordStep):int(timeRange[1]/recordStep)]
                        lenData = len(data)
                    t = np.arange(timeRange[0], timeRange[1]+recordStep, recordStep)
                    tracesData.append({'t': t, 'cell_'+str(gid)+'_'+trace: data})
                    color = colorList2[itrace%len(colorList2)]
                    if not overlay:
                        plt.subplot(len(tracesList),1,itrace+1)
                        color = 'blue'
                    plt.plot(t[:lenData], data, linewidth=1.5, color=color, label=trace)
                    plt.xlabel('Time (ms)', fontsize=fontsiz)
                    plt.ylabel(trace, fontsize=fontsiz)
                    plt.xlim(timeRange)
                    if ylim: plt.ylim(ylim)
                    if itrace==0: plt.title('Cell %d, Pop %s '%(int(gid), gidPops[gid]))
                    
            if overlay: 
                #maxLabelLen = 10
                #plt.subplots_adjust(right=(0.9-0.012*maxLabelLen))
                plt.legend()#fontsize=fontsiz, bbox_to_anchor=(1.04, 1), loc=2, borderaxespad=0.)

            if axis == 'off':  # if no axis, add scalebar
                ax = plt.gca()
                sizex = timeRange[1]-timeRange[0]/20
                yl = plt.ylim()
                plt.ylim(yl[0]-0.2*(yl[1]-yl[0]), yl[1])  # leave space for scalebar?
                add_scalebar(ax, hidex=False, hidey=True, matchx=False, matchy=True,  sizex=sizex, sizey=None, 
                    unitsx='ms', unitsy='mV', scalex=1, scaley=1, loc=4, pad=10, borderpad=0.5, sep=3, prop=None, barcolor="black", barwidth=2)   
                plt.axis(axis)                 
            
    # Plot one fig per trace
    elif oneFigPer == 'trace':
        plotFigPerTrace(cellGids)

    # Plot one fig per trace for each population
    elif oneFigPer == 'popTrace':
        allPopGids = invertDictMapping(gidPops)
        for popLabel, popGids in allPopGids.iteritems():
            plotFigPerTrace(popGids)


    try:
        plt.tight_layout()
    except:
        pass

    #save figure data
    if saveData:
        figData = {'tracesData': tracesData, 'include': include, 'timeRange': timeRange, 'oneFigPer': oneFigPer,
         'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}
    
        _saveFigData(figData, saveData, 'traces')
 
    # save figure
    if saveFig: 
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'traces.png'
        if len(figs) > 1:
            for figLabel, figObj in figs.iteritems():
                plt.figure(figObj.number)
                plt.savefig(filename[:-4]+figLabel+filename[-4:])
        else:
            plt.savefig(filename)

    # show fig 
    if showFig: _showFigure()

    return figs, {'tracesData': tracesData, 'include': include}

# -------------------------------------------------------------------------------------------------------------------
## EPSPs amplitude
# -------------------------------------------------------------------------------------------------------------------
@exception
def plotEPSPAmp(include=None, trace=None, start=0, interval=50, number=2, amp='absolute', polarity='exc', saveFig=False, showFig=True):

    from .. import sim

    print('Plotting EPSP amplitudes...')

    if include is None: include = [] # If not defined, initialize as empty list

    cells, cellGids, _ = getCellsInclude(include)
    gidPops = {cell['gid']: cell['tags']['pop'] for cell in cells}

    if not trace: 
        print 'Error: Missing trace to to plot EPSP amplitudes'
        return
    step = sim.cfg.recordStep

    peaksAbs = np.zeros((number, len(cellGids)))
    peaksRel = np.zeros((number, len(cellGids)))
    for icell, gid in enumerate(cellGids):
        vsoma = sim.allSimData[trace]['cell_'+str(gid)]
        for ipeak in range(number):
            if polarity == 'exc':
                peakAbs = max(vsoma[int(start/step+(ipeak*interval/step)):int(start/step+(ipeak*interval/step)+(interval-1)/step)]) 
            elif polarity == 'inh':
                peakAbs = min(vsoma[int(start/step+(ipeak*interval/step)):int(start/step+(ipeak*interval/step)+(interval-1)/step)]) 
            peakRel = peakAbs - vsoma[int((start-1)/step)]
            peaksAbs[ipeak,icell] = peakAbs
            peaksRel[ipeak,icell] = peakRel

    if amp == 'absolute':
        peaks = peaksAbs
        ylabel = 'EPSP peak V (mV)'
    elif amp == 'relative':
        peaks = peaksRel
        ylabel = 'EPSP amplitude (mV)'
    elif amp == 'ratio':
        peaks = np.zeros((number, len(cellGids)))
        for icell in range(len(cellGids)):
            peaks[:, icell] = peaksRel[:, icell] / peaksRel[0, icell]
        ylabel = 'EPSP amplitude ratio'
        
    xlabel = 'EPSP number'

    # plot
    fig = plt.figure()
    plt.plot(peaks, marker='o')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    h = plt.axes()
    ylim=list(h.get_ylim())
    h.set_ylim(ylim[0], ylim[1]+(0.15*abs(ylim[1]-ylim[0])))
    h.set_xticks(range(number))
    h.set_xticklabels(range(1, number+1))
    plt.legend(gidPops.values())
    if amp == 'ratio':
        plt.plot((0, number-1), (1.0, 1.0), ':', color= 'gray')

    # save figure
    if saveFig: 
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'EPSPamp_'+amp+'.png'
        plt.savefig(filename)

    # show fig 
    if showFig: _showFigure()

    return fig, {'peaks': peaks}

