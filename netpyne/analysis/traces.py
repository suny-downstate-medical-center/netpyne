"""
Module for analysis and plotting of traces-related results

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from builtins import range
from builtins import str
try:
    basestring
except NameError:
    basestring = str
from future import standard_library
standard_library.install_aliases()
from netpyne import __gui__

if __gui__:
    import matplotlib.pyplot as plt
import numpy as np
from .utils import colorList, _showFigure, _saveFigData, exception, getCellsInclude


# -------------------------------------------------------------------------------------------------------------------
## Plot recorded cell traces (V, i, g, etc.)
# -------------------------------------------------------------------------------------------------------------------
@exception
def plotTraces(include=None, timeRange=None, oneFigPer='cell', rerun=False, title=None, overlay=False, colors=None, ylim=None, axis=True, scaleBarLoc=1, figSize = (10,8), fontSize=12, saveData=None, saveFig=None, showFig=True):
    """
    Function for/to <short description of `netpyne.analysis.traces.plotTraces`>

    Parameters
    ----------
    include : list
        Populations and cells to include in the plot.
        **Default:** 
        ``['eachPop', 'allCells']`` plots histogram for each population and overall average
        **Options:** 
        ``['all']`` plots all cells and stimulations, 
        ``['allNetStims']`` plots just stimulations, 
        ``['popName1']`` plots a single population, 
        ``['popName1', 'popName2']`` plots multiple populations, 
        ``[120]`` plots a single cell, 
        ``[120, 130]`` plots multiple cells, 
        ``[('popName1', 56)]`` plots a cell from a specific population, 
        ``[('popName1', [0, 1]), ('popName2', [4, 5, 6])]``, plots cells from multiple populations

    timeRange : list [start, stop]
        Time range to plot.
        **Default:** 
        ``None`` plots entire time range
        **Options:** ``<option>`` <description of option>
 
    oneFigPer : str
        Whether to plot one figure per cell (showing multiple traces) or per trace (showing multiple cells).
        **Default:** ``'cell'`` 
        **Options:** ``'trace'``

    rerun : bool
        Rerun simulation so a new set of cells gets recorded.
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
 
    title : str
        Set the whole figure title, works only with ``oneFigPer='cell'``.
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    overlay : bool
        Whether to overlay plots or use subplots.
        **Default:** ``True`` overlays plots.
        **Options:** ``<option>`` <description of option>
 
    colors : list
        List of normalized RGB colors to use for traces.
        **Default:** ``None`` uses standard colors
        **Options:** ``<option>`` <description of option>
 
    ylim : list [min, max]
        Sets the y limits of the plot.
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    axis : bool
        Whether to show axis or not; if not, then a scalebar is included.
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>
 
    scaleBarLoc : int
        Sets the location of the scale bar (added when axis=False).
        **Default:** ``1``
        **Options:** 
        ``1``  upper right, ``2`` upper left, ``3`` lower left, ``4`` lower right, ``5`` right, ``6`` center left, ``7`` center right, ``8`` lower center, ``9`` upper center, ``10`` center

    figSize : list [width, height]
        Size of figure in inches.
        **Default:** ``(10, 8)``
        **Options:** ``<option>`` <description of option>
 
    fontSize : int
        Font size on figure.
        **Default:** ``12``
        **Options:** ``<option>`` <description of option>
 
    saveData : bool or str
        Whether and where to save the data used to generate the plot. 
        **Default:** ``False`` 
        **Options:** ``True`` autosaves the data,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.pkl'`` and ``'.json'``

    saveFig : bool or str
        Whether and where to save the figure.
        **Default:** ``False``
        **Options:** ``True`` autosaves the figure,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.png'``, ``'.jpg'``, ``'.eps'``, and ``'.tiff'``

    showFig : bool
        Shows the figure if ``True``.
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>
 
    Returns
    -------


"""
    
    from .. import sim
    from ..support.scalebar import add_scalebar

    print('Plotting recorded cell traces ...', oneFigPer)

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

    tracesList = list(sim.cfg.recordTraces.keys())
    tracesList.sort()
    cells, cellGids, _ = getCellsInclude(include)
    gidPops = {cell['gid']: cell['tags']['pop'] for cell in cells}

    # time range
    if timeRange is None:
        timeRange = [0,sim.cfg.duration]

    recordStep = sim.cfg.recordStep

    figs = {}
    tracesData = []

    # set font size
    plt.rcParams.update({'font.size': fontSize})
    fontsiz = fontSize

    # add scale bar
    def addScaleBar(timeRange=timeRange, loc=scaleBarLoc):
        ax = plt.gca()
        sizex =  (timeRange[1]-timeRange[0])/20.0
        #yl = plt.ylim()
        #plt.ylim(yl[0]-0.2*(yl[1]-yl[0]), yl[1])
        add_scalebar(ax, hidex=False, hidey=True, matchx=False, matchy=True, sizex=sizex, sizey=None, unitsx='ms', unitsy='mV', scalex=1, scaley=1, loc=loc, pad=-1, borderpad=0.5, sep=4, prop=None, barcolor="black", barwidth=3)
        plt.axis(axis)

    # Plot one fig per trace for given cell list
    def plotFigPerTrace(subGids):
        fontsiz = 12
        for itrace, trace in enumerate(tracesList):
            figs['_trace_'+str(trace)] = plt.figure(figsize=figSize) # Open a new figure
            for igid, gid in enumerate(subGids):
                # print('recordStep',recordStep)
                if 'cell_'+str(gid) in sim.allSimData[trace]:
                    fullTrace = sim.allSimData[trace]['cell_'+str(gid)]
                    if isinstance(fullTrace, dict):
                        if recordStep == 'adaptive':
                            t = []
                            t_indexes = []
                            data = []
                            lenData = []
                            for key in list(fullTrace.keys()):
                                t.append(np.array(sim.allSimData[trace]['cell_time_'+str(gid)][key]))
                                t_indexes.append(t[-1].__ge__(timeRange[0]).__and__(t[-1].__le__(timeRange[1])))
                                data.append(np.array(fullTrace[key])[t_indexes[-1]])
                                lenData = len(data[-1])
                                t[-1] = t[-1][t_indexes[-1]]
                        else:
                            data = [fullTrace[key][int(timeRange[0]/recordStep):int(timeRange[1]/recordStep)] for key in list(fullTrace.keys())]
                            lenData = len(data[0])
                            data = np.transpose(np.array(data))
                            t = np.arange(timeRange[0], timeRange[1]+recordStep, recordStep)
                    else:
                        if recordStep == 'adaptive':
                            t = np.array(sim.allSimData[trace]['cell_time_'+str(gid)])
                            t_indexes = t.__ge__(timeRange[0]).__and__(t.__le__(timeRange[1]))
                            data = np.array(sim.allSimData[trace]['cell_'+str(gid)])[t_indexes]
                            lenData = len(data)
                            t = t[t_indexes]
                        else:
                            data = np.array(fullTrace[int(timeRange[0]/recordStep):int(timeRange[1]/recordStep)])
                            lenData = len(data)
                            t = np.arange(timeRange[0], timeRange[1]+recordStep, recordStep)
                    tracesData.append({'t': t, 'cell_'+str(gid)+'_'+trace: data})
                    color = colorList2[igid%len(colorList2)]
                    if not overlay:
                        plt.subplot(len(subGids),1,igid+1)
                        plt.ylabel(trace, fontsize=fontsiz)
                    if recordStep == 'adaptive':
                        if isinstance(data, list):
                            for tl,dl in zip(t,data):
                                plt.plot(tl[:len(dl)], dl, linewidth=1.5,
                                         color=color, label='Cell %d, Pop %s '%(int(gid), gidPops[gid]))
                        else:
                            plt.plot(t, data, linewidth=1.5,
                                     color=color, label='Cell %d, Pop %s '%(int(gid), gidPops[gid]))
                            # plt.plot(t, data, linewidth=1.5, color=color, label=trace)
                    else:
                        if isinstance(data, list):
                            for tl,dl in zip(t,data):
                                plt.plot(tl[:len(dl)], dl, linewidth=1.5,
                                         color=color, label='Cell %d, Pop %s '%(int(gid), gidPops[gid]))
                        else:
                            plt.plot(t[:len(data)], data, linewidth=1.5,
                                     color=color, label='Cell %d, Pop %s '%(int(gid), gidPops[gid]))
                    plt.xlabel('Time (ms)', fontsize=fontsiz)
                    plt.xlim(timeRange)
                    if ylim: plt.ylim(ylim)
                    plt.title('%s '%(trace))
                    
                    if not overlay:
                        if not axis or axis=='off':  # if no axis, add scalebar
                            addScaleBar()

            if overlay: 
                if not axis or axis=='off':  # if no axis, add scalebar
                    addScaleBar()
                if len(subGids) < 20:
                    #maxLabelLen = 10
                    #plt.subplots_adjust(right=(0.9-0.012*maxLabelLen)) 
                    #plt.legend(fontsize=fontsiz, bbox_to_anchor=(1.04, 1), loc=2, borderaxespad=0.)
                    plt.legend()  # PUT BACK!!!!!!



    # Plot one fig per cell
    if oneFigPer == 'cell':
        for cell, gid in zip(cells,cellGids):
            figs['_gid_'+str(gid)] = plt.figure(figsize=figSize) # Open a new figure
            for itrace, trace in enumerate(tracesList):
                if 'cell_'+str(gid) in sim.allSimData[trace]:
                    fullTrace = sim.allSimData[trace]['cell_'+str(gid)]
                    if isinstance(fullTrace, dict):
                        if recordStep == 'adaptive':
                            t = []
                            t_indexes = []
                            data = []
                            lenData = []
                            for key in list(fullTrace.keys()):
                                t.append(np.array(sim.allSimData[trace]['cell_time_'+str(gid)][key]))
                                t_indexes.append(t[-1].__ge__(timeRange[0]).__and__(t[-1].__le__(timeRange[1])))
                                data.append(np.array(fullTrace[key])[t_indexes[-1]])
                                lenData = len(data[-1])
                                t[-1] = t[-1][t_indexes[-1]]
                        else:
                                data = [fullTrace[key][int(timeRange[0]/recordStep):int(timeRange[1]/recordStep)] for key in list(fullTrace.keys())]
                                lenData = len(data[0])
                                data = np.transpose(np.array(data))
                                t = np.arange(timeRange[0], timeRange[1]+recordStep, recordStep)
                    else:
                        if recordStep == 'adaptive':
                            t = np.array(sim.allSimData[trace]['cell_time_'+str(gid)])
                            t_indexes = t.__ge__(timeRange[0]).__and__(t.__le__(timeRange[1]))
                            data = np.array(sim.allSimData[trace]['cell_'+str(gid)])[t_indexes]
                            lenData = len(data)
                            t = t[t_indexes]
                        else:
                            data = np.array(fullTrace[int(timeRange[0]/recordStep):int(timeRange[1]/recordStep)])
                            lenData = len(data)
                            t = np.arange(timeRange[0], timeRange[1]+recordStep, recordStep)
                    tracesData.append({'t': t, 'cell_'+str(gid)+'_'+trace: data})
                    color = colorList2[itrace%len(colorList2)]
                    if not overlay:
                        plt.subplot(len(tracesList),1,itrace+1)
                        color = 'blue'
                    if recordStep == 'adaptive':
                        if isinstance(data, list) and isinstance(data[0], (list, np.array)):
                            for tl,dl in zip(t,data):
                                plt.plot(tl, dl, linewidth=1.5, color=color, label=trace)
                        else:
                            plt.plot(t, data, linewidth=1.5, color=color, label=trace)
                    else:
                        plt.plot(t[:lenData], data, linewidth=1.5, color=color, label=trace)
                    plt.xlabel('Time (ms)', fontsize=fontsiz)
                    plt.ylabel(trace, fontsize=fontsiz)
                    plt.xlim(timeRange)
                    if ylim:
                        if ylim[itrace]:
                            plt.ylim(ylim[itrace])
                    if itrace==0: plt.title('Cell %d, Pop %s '%(int(gid), gidPops[gid]))
                    if not overlay:
                        if not axis or axis=='off':  # if no axis, add scalebar
                            addScaleBar()       
                    
            if overlay: 
                if not axis or axis=='off':  # if no axis, add scalebar
                    addScaleBar() 
                #maxLabelLen = 10
                #plt.subplots_adjust(right=(0.9-0.012*maxLabelLen))
                plt.legend() #fontsize=fontsiz, bbox_to_anchor=(1.04, 1), loc=2, borderaxespad=0.)

            if title:
                figs['_gid_'+str(gid)].suptitle(cell['tags'][title])
                
    # Plot one fig per trace
    elif oneFigPer == 'trace':
        plotFigPerTrace(cellGids)

    # Plot one fig per trace for each population
    elif oneFigPer == 'popTrace':
        allPopGids = invertDictMapping(gidPops)
        for popLabel, popGids in allPopGids.items():
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
            filename = sim.cfg.filename + '_traces.png'
        if len(figs) > 1:
            for figLabel, figObj in figs.items():
                plt.figure(figObj.number)
                plt.savefig(filename[:-4] + '_' + figLabel + '_' + filename[-4:])
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
    """
    Function for/to <short description of `netpyne.analysis.traces.plotEPSPAmp`>

    Parameters
    ----------
    include : <``None``?>
        <Short description of include>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    trace : <``None``?>
        <Short description of trace>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>
 
    start : int
        <Short description of start>
        **Default:** ``0``
        **Options:** ``<option>`` <description of option>
 
    interval : int
        <Short description of interval>
        **Default:** ``50``
        **Options:** ``<option>`` <description of option>
 
    number : int
        <Short description of number>
        **Default:** ``2``
        **Options:** ``<option>`` <description of option>
 
    amp : str
        <Short description of amp>
        **Default:** ``'absolute'``
        **Options:** ``<option>`` <description of option>
 
    polarity : str
        <Short description of polarity>
        **Default:** ``'exc'``
        **Options:** ``<option>`` <description of option>
 
    saveFig : bool
        <Short description of saveFig>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
 
    showFig : bool
        <Short description of showFig>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>
 

    """



    from .. import sim

    print('Plotting EPSP amplitudes...')

    if include is None: include = [] # If not defined, initialize as empty list

    cells, cellGids, _ = getCellsInclude(include)
    gidPops = {cell['gid']: cell['tags']['pop'] for cell in cells}

    if not trace: 
        print('Error: Missing trace to to plot EPSP amplitudes')
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
    h.set_xticks(list(range(number)))
    h.set_xticklabels(list(range(1, number+1)))
    plt.legend(list(gidPops.values()))
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
