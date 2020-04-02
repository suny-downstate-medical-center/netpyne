"""
analysis/interactive.py

Functions to plot and analyze RxD-related results

Contributors: salvadordura@gmail.com, joe.w.graham@gmail.com
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from netpyne import __gui__

if __gui__:
    import matplotlib.pyplot as plt
    from matplotlib import mlab
    from matplotlib_scalebar import scalebar
from numbers import Number
from .utils import colorList, exception, getSpktSpkid, _showFigure, _saveFigData, getCellsInclude, syncMeasure, _smooth1d

import numpy as np
import pandas as pd

# -------------------------------------------------------------------------------------------------------------------
## Plot interactive raster
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotRaster(include=['allCells'], timeRange=None, maxSpikes=1e8, orderBy='gid', orderInverse=False, popRates=False, spikeHist=False, spikeHistBin=5, syncLines=False, marker='circle', markerSize=3, popColors=None, saveData=None, saveFig=None, showFig=False):
    """Creates an interactive html raster plot of network cells using Bokeh.

    Parameters
    ----------
    include : list
        Cells to include in the plot.
        **Default:** 
        ``['allCells']`` plots all cells
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

    maxSpikes : int
        Maximum number of spikes to be plotted.
        **Default:** ``1e8``

    orderBy : str
        Unique numeric cell property by which to order the y-axis.
        **Default:** ``'gid'`` orders by cell ID
        **Options:**
        ``'y'`` orders by cell y-location,
        ``'ynorm'`` orders by cell normalized y-location

    orderInverse : bool
        Inverts the y-axis order if ``True``.
        **Default:** ``False`` 
    
    popRates : bool
        Include population firing rates on plot if ``True``.
        **Default:** ``False``
    
    spikeHist : bool
        Include spike histogram (spikes/bin) on plot if ``True``. 
        **Default:** ``False``
    
    spikeHistBin : int
        Size of bin in ms to use for spike histogram. 
        **Default:** ``5`` 
    
    syncLines : bool
        Calculate synchrony measure and plot vertical lines for each spike to evidence synchrony if ``True``.
        **Default:** ``False``
    
    marker : str
        `Bokeh marker <https://docs.bokeh.org/en/latest/docs/gallery/markers.html>`_ for each spike.
        **Default:** ``'circle'``
    
    markerSize : int
        Size of Bokeh marker for each spike.
        **Default:** ``3`` 
    
    popColors : dict
        Dictionary with custom color (value) used for each population (key).
        **Default:** ``None`` uses standard colors
    
    saveData : bool or str
        Whether and where to save the data used to generate the plot. 
        **Default:** ``False`` 
        **Options:** ``True`` autosaves the data,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.pkl'`` and ``'.json'``
    
    saveFig : bool or str
        Whether and where to save the figure.
        **Default:** ``False``
        **Options:** ``True`` autosaves the figure,
        ``'/path/filename.html'`` saves to a custom path and filename, only valid file extension is ``'.html'``
    
    showFig : bool
        Shows the figure if ``True``.
        **Default:** ``True``

    Returns
    -------
    (str, dict)
        A tuple consisting of a string containing the html for the figure and a dictionary containing the plot data.

    See Also
    --------
    plotRaster :
    iplotSpikeHist : 
    plotSpikeHist :

    Examples
    --------
    >>> import netpyne, netpyne.examples.example
    >>> out = netpyne.analysis.iplotRaster()
    """    

    from .. import sim
    from bokeh.plotting import figure, show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import layout
    from bokeh.models import Legend
    from bokeh.colors import RGB
    from bokeh.models.annotations import Title

    print('Plotting interactive raster ...')

    TOOLS = 'hover,save,pan,box_zoom,reset,wheel_zoom',

    colors = [RGB(*[round(f * 255) for f in color]) for color in colorList] # bokeh only handles integer rgb values from 0-255

    popColorDict = None
    if popColors is not None:
        popColorDict = popColors.copy()
        for pop, color in popColorDict.items():
            popColorDict[pop] = RGB(*[round(f * 255) for f in color])

    cells, cellGids, netStimLabels = getCellsInclude(include)

    df = pd.DataFrame.from_records(cells)
    df = pd.concat([df.drop('tags', axis=1), pd.DataFrame.from_records(df['tags'].tolist())], axis=1)

    keep = ['pop', 'gid', 'conns']

    if isinstance(orderBy, str) and orderBy not in cells[0]['tags']:  # if orderBy property doesn't exist or is not numeric, use gid
        orderBy = 'gid'
    elif isinstance(orderBy, str) and not isinstance(cells[0]['tags'][orderBy], Number):
        orderBy = 'gid'

    if isinstance(orderBy, list):
        keep = keep + list(set(orderBy) - set(keep))
    elif orderBy not in keep:
        keep.append(orderBy)

    df = df[keep]

    popLabels = [pop for pop in sim.net.allPops if pop in df['pop'].unique()] #preserves original ordering
    if netStimLabels: popLabels.append('NetStims')
    popColorsTmp = {popLabel: colors[ipop%len(colors)] for ipop,popLabel in enumerate(popLabels)} # dict with color for each pop
    if popColorDict: popColorsTmp.update(popColorDict)
    popColorDict = popColorsTmp
    if len(cellGids) > 0:
        gidColors = {cell['gid']: popColorDict[cell['tags']['pop']] for cell in cells}  # dict with color for each gid
        try:
            sel, spkts, spkgids = getSpktSpkid(cellGids=cellGids, timeRange=timeRange, allCells=(include == ['allCells']))
        except:
            import sys
            print((sys.exc_info()))
            spkgids, spkts = [], []
            sel = pd.DataFrame(columns=['spkt', 'spkid'])
        sel['spkgidColor'] = sel['spkid'].map(gidColors)
        sel['pop'] = sel['spkid'].map(df.set_index('gid')['pop'])
        df['gidColor'] = df['pop'].map(popColorDict)
        df.set_index('gid', inplace=True)

    # Order by
    if len(df) > 0:
        ylabelText = 'Cells (ordered by %s)'%(orderBy)
        df = df.sort_values(by=orderBy)
        sel['spkind'] = sel['spkid'].apply(df.index.get_loc)
    else:
        sel = pd.DataFrame(columns=['spkt', 'spkid', 'spkind'])
        ylabelText = ''

    # Add NetStim spikes
    numCellSpks = len(sel)
    numNetStims = 0
    for netStimLabel in netStimLabels:
        netStimSpks = [spk for cell,stims in sim.allSimData['stims'].items() \
                       for stimLabel,stimSpks in stims.items() for spk in stimSpks if stimLabel == netStimLabel]
        if len(netStimSpks) > 0:
            # lastInd = max(spkinds) if len(spkinds)>0 else 0
            lastInd = sel['spkind'].max() if len(sel['spkind']) > 0 else 0
            spktsNew = netStimSpks
            spkindsNew = [lastInd+1+i for i in range(len(netStimSpks))]
            ns = pd.DataFrame(list(zip(spktsNew, spkindsNew)), columns=['spkt', 'spkind'])
            ns['spkgidColor'] = popColorDict['netStims']
            sel = pd.concat([sel, ns])
            numNetStims += 1
        else:
            pass
            #print netStimLabel+' produced no spikes'
    if len(cellGids)>0 and numNetStims:
        ylabelText = ylabelText + ' and NetStims (at the end)'
    elif numNetStims:
        ylabelText = ylabelText + 'NetStims'

    if numCellSpks+numNetStims == 0:
        print('No spikes available to plot raster')
        return None

    # Time Range
    if timeRange == [0, sim.cfg.duration]:
        pass
    elif timeRange is None:
        timeRange = [0, sim.cfg.duration]
    else:
        sel = sel.query('spkt >= @timeRange[0] and spkt <= @timeRange[1]')

    # Limit to max spikes
    if (len(sel)>maxSpikes):
        print(('  Showing only the first %i out of %i spikes' % (maxSpikes, len(sel)))) # Limit num of spikes
        if numNetStims: # sort first if have netStims
            sel = sel.sort_values(by='spkt')
        sel = sel.iloc[:maxSpikes]
        timeRange[1] =  sel['spkt'].max()

    # Plot stats
    gidPops = df['pop'].tolist()
    popNumCells = [float(gidPops.count(pop)) for pop in popLabels] if numCellSpks else [0] * len(popLabels)
    totalSpikes = len(sel)
    totalConnections = sum([len(conns) for conns in df['conns']])
    numCells = len(cells)
    firingRate = float(totalSpikes)/(numCells+numNetStims)/(timeRange[1]-timeRange[0])*1e3 if totalSpikes>0 else 0 # Calculate firing rate
    connsPerCell = totalConnections/float(numCells) if numCells>0 else 0 # Calculate the number of connections per cell

    if popRates:
        avgRates = {}
        tsecs = (timeRange[1]-timeRange[0])/1e3
        for i, (pop, popNum) in enumerate(zip(popLabels, popNumCells)):
            if numCells > 0 and pop != 'NetStims':
                if numCellSpks == 0:
                    avgRates[pop] = 0
                else:
                    avgRates[pop] = len([spkid for spkid in sel['spkind'].iloc[:numCellSpks-1] if df['pop'].iloc[int(spkid)]==pop])/popNum/tsecs
        if numNetStims:
            popNumCells[-1] = numNetStims
            avgRates['NetStims'] = len([spkid for spkid in sel['spkind'].iloc[numCellSpks:]])/numNetStims/tsecs

    if orderInverse:
        y_range=(sel['spkind'].max(), sel['spkind'].min())
    else:
        y_range=(sel['spkind'].min(), sel['spkind'].max())

    fig = figure(
        title="Raster Plot", 
        tools=TOOLS, 
        active_drag = 'pan', 
        active_scroll = 'wheel_zoom',
        tooltips=[('Cell GID', '@y'), ('Spike time', '@x')],
        x_axis_label="Time (ms)", 
        y_axis_label=ylabelText,
        x_range=(timeRange[0], timeRange[1]), 
        y_range=y_range, 
        toolbar_location='above')

    t = Title()
    if syncLines:
        for spkt in sel['spkt'].tolist():
            fig.line((spkt, spkt), (0, len(cells)+numNetStims), color='red', line_width=2)
        print(syncMeasure())
        t.text = 'cells=%i  syns/cell=%0.1f  rate=%0.1f Hz  sync=%0.2f' % (numCells,connsPerCell,firingRate,syncMeasure())
    else:
        t.text = 'cells=%i  syns/cell=%0.1f  rate=%0.1f Hz' % (numCells,connsPerCell,firingRate)
    fig.title = t

    if spikeHist:
        histo = np.histogram(sel['spkt'].tolist(), bins = np.arange(timeRange[0], timeRange[1], spikeHistBin))
        histoT = histo[1][:-1]+spikeHistBin/2
        histoCount = histo[0]

    legendItems = []
    grouped = sel.groupby('pop')
    for name, group in grouped:
        if popRates:
            label = name + ' (%.3g Hz)'%(avgRates[name])
        else:
            label = name

        fig.scatter(group['spkt'], group['spkind'], color=group['spkgidColor'], marker=marker, size=markerSize, legend_label=label)
        #legendItems.append((label, [s]))

    if spikeHist:
        from bokeh.models import LinearAxis, Range1d
        fig.extra_y_ranges={'spikeHist': Range1d(start=min(histoCount), end=max(histoCount))}
        fig.add_layout(LinearAxis(y_range_name='spikeHist', axis_label='Spike count'), 'right')
        fig.line (histoT, histoCount, line_width=2, y_range_name='spikeHist')

    legend = Legend(items=legendItems, location=(10,0))
    legend.click_policy='hide'
    fig.add_layout(legend, 'right')

    plot_layout = layout([fig], sizing_mode='stretch_both')
    html = file_html(plot_layout, CDN, title="Raster Plot")

    # save figure data
    if saveData:
        figData = {'spkTimes': sel['spkt'].tolist(), 'spkInds': sel['spkind'].tolist(), 'spkColors': sel['spkgidColor'].tolist(), 'cellGids': cellGids, 'sortedGids': df.index.tolist(), 'numNetStims': numNetStims,
                   'include': include, 'timeRange': timeRange, 'maxSpikes': maxSpikes, 'orderBy': orderBy, 'orderInverse': orderInverse, 'spikeHist': spikeHist,
                   'syncLines': syncLines}
        _saveFigData(figData, saveData, 'raster')

    # save figure
    if saveFig:
        if isinstance(saveFig, str):
            filename = saveFig
        else:
            filename = sim.cfg.filename + '_iplot_raster.html'
        file = open(filename, 'w')
        file.write(html)
        file.close()

    if showFig: show(plot_layout)

    return html, {'include': include, 'spkts': spkts, 'spkinds': sel['spkind'].tolist(), 'timeRange': timeRange}


# -------------------------------------------------------------------------------------------------------------------
## Plot interactive dipole
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotDipole(expData={'label': 'Experiment', 'x':[], 'y':[]}, showFig=False):
    '''
    expData: experimental data; a dict with ['x'] and ['y'] 1-d vectors (either lists or np.arrays) of same length
    showFig: show output figure in web browser (default: None)
    '''
    from .. import sim
    from bokeh.plotting import figure, show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import layout

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

    fig = figure(title="Dipole Plot", tools=TOOLS, toolbar_location='above', x_axis_label="Time (ms)", y_axis_label='Dipole (nAM x 3000)')


    # renormalize the dipole and save
    def baseline_renormalize():
        # N_pyr cells in grid. This is PER LAYER
        N_pyr = sim.cfg.N_pyr_x * sim.cfg.N_pyr_y
        # dipole offset calculation: increasing number of pyr cells (L2 and L5, simultaneously)
        # with no inputs resulted in an aggregate dipole over the interval [50., 1000.] ms that
        # eventually plateaus at -48 fAm. The range over this interval is something like 3 fAm
        # so the resultant correction is here, per dipole
        # dpl_offset = N_pyr * 50.207
        dpl_offset = {
            # these values will be subtracted
            'L2': N_pyr * 0.0443,
            'L5': N_pyr * -49.0502
            # 'L5': N_pyr * -48.3642,
            # will be calculated next, this is a placeholder
            # 'agg': None,
        }

        # L2 dipole offset can be roughly baseline shifted over the entire range of t
        dpl = {'L2': np.array(sim.simData['dipole']['L2']),
               'L5': np.array(sim.simData['dipole']['L5'])}
        dpl['L2'] -= dpl_offset['L2']

        # L5 dipole offset should be different for interval [50., 500.] and then it can be offset
        # slope (m) and intercept (b) params for L5 dipole offset
        # uncorrected for N_cells
        # these values were fit over the range [37., 750.)
        m = 3.4770508e-3
        b = -51.231085
        # these values were fit over the range [750., 5000]
        t1 = 750.
        m1 = 1.01e-4
        b1 = -48.412078

        t = sim.simData['t']

        # piecewise normalization
        dpl['L5'][t <= 37.] -= dpl_offset['L5']
        dpl['L5'][(t > 37.) & (t < t1)] -= N_pyr * (m * t[(t > 37.) & (t < t1)] + b)
        dpl['L5'][t >= t1] -= N_pyr * (m1 * t[t >= t1] + b1)
        # recalculate the aggregate dipole based on the baseline normalized ones
        dpl['agg'] = dpl['L2'] + dpl['L5']

        return dpl

    # convolve with a hamming window
    def hammfilt(x, winsz):
        from pylab import convolve
        from numpy import hamming
        win = hamming(winsz)
        win /= sum(win)
        return convolve(x,win,'same')

    # baseline renormalize
    dpl = baseline_renormalize()

    # convert units from fAm to nAm, rescale and smooth
    for key in dpl.keys():
        dpl[key] *= 1e-6 * sim.cfg.dipole_scalefctr
        
        if sim.cfg.dipole_smooth_win > 0:
            dpl[key] = hammfilt(dpl[key], sim.cfg.dipole_smooth_win/sim.cfg.dt)

        # Set index 0 to 0
        dpl[key][0] = 0.0

    # plot exp data
    fig.line(expData['x'], expData['y'], color='black', legend=expData['label'])

    # plot recorded dipole data
    fig.line(sim.simData['t'], dpl['L2'], color='green', legend="L2Pyr", line_width=2.0)
    fig.line(sim.simData['t'], dpl['L5'], color='red', legend="L5Pyr", line_width=2.0)
    fig.line(sim.simData['t'], dpl['L2']+dpl['L5'], color='blue', legend="Aggregate", line_width=2.0)

    fig.legend.location = "top_right"
    fig.legend.click_policy = "hide"

    plot_layout = layout(fig, sizing_mode='stretch_both')
    html = file_html(plot_layout, CDN, title="Dipole Plot")

    if showFig:
        show(fig)

    return html


# -------------------------------------------------------------------------------------------------------------------
## Plot interactive dipole Spectrogram
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotDipoleSpectrogram(expData={'label': 'Experiment', 'x':[], 'y':[]}, minFreq = 1, maxFreq = 80, stepFreq = 1, norm = True, showFig=False):
    '''
    expData: experimental data; a dict with ['x'] and ['y'] 1-d vectors (either lists or np.arrays) of same length
    showFig: show output figure in web browser (default: None)
    '''
    from .. import sim
    from bokeh.plotting import figure, show
    from bokeh.models import BasicTicker, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import layout


    # renormalize the dipole and save
    def baseline_renormalize():
        # N_pyr cells in grid. This is PER LAYER
        N_pyr = sim.cfg.N_pyr_x * sim.cfg.N_pyr_y
        # dipole offset calculation: increasing number of pyr cells (L2 and L5, simultaneously)
        # with no inputs resulted in an aggregate dipole over the interval [50., 1000.] ms that
        # eventually plateaus at -48 fAm. The range over this interval is something like 3 fAm
        # so the resultant correction is here, per dipole
        # dpl_offset = N_pyr * 50.207
        dpl_offset = {
            # these values will be subtracted
            'L2': N_pyr * 0.0443,
            'L5': N_pyr * -49.0502
            # 'L5': N_pyr * -48.3642,
            # will be calculated next, this is a placeholder
            # 'agg': None,
        }

        # L2 dipole offset can be roughly baseline shifted over the entire range of t
        dpl = {'L2': np.array(sim.simData['dipole']['L2']),
               'L5': np.array(sim.simData['dipole']['L5'])}
        dpl['L2'] -= dpl_offset['L2']

        # L5 dipole offset should be different for interval [50., 500.] and then it can be offset
        # slope (m) and intercept (b) params for L5 dipole offset
        # uncorrected for N_cells
        # these values were fit over the range [37., 750.)
        m = 3.4770508e-3
        b = -51.231085
        # these values were fit over the range [750., 5000]
        t1 = 750.
        m1 = 1.01e-4
        b1 = -48.412078

        t = sim.simData['t']

        # piecewise normalization
        dpl['L5'][t <= 37.] -= dpl_offset['L5']
        dpl['L5'][(t > 37.) & (t < t1)] -= N_pyr * (m * t[(t > 37.) & (t < t1)] + b)
        dpl['L5'][t >= t1] -= N_pyr * (m1 * t[t >= t1] + b1)
        # recalculate the aggregate dipole based on the baseline normalized ones
        dpl['agg'] = dpl['L2'] + dpl['L5']

        return dpl

    # convolve with a hamming window
    def hammfilt(x, winsz):
        from pylab import convolve
        from numpy import hamming
        win = hamming(winsz)
        win /= sum(win)
        return convolve(x,win,'same')

    # baseline renormalize
    dpl = baseline_renormalize()

    # convert units from fAm to nAm, rescale and smooth
    for key in dpl.keys():
        dpl[key] *= 1e-6 * sim.cfg.dipole_scalefctr
        
        if sim.cfg.dipole_smooth_win > 0:
            dpl[key] = hammfilt(dpl[key], sim.cfg.dipole_smooth_win/sim.cfg.dt)

        # Set index 0 to 0
        dpl[key][0] = 0.0


    # plot recorded dipole data
    #fig.line(sim.simData['t'], dpl['L2']+dpl['L5'], color='blue', legend="Aggregate", line_width=2.0)

    # plot Morlet spectrogram
    from ..support.morlet import MorletSpec, index2ms

    spec = []
    dplsum = dpl['L2'] + dpl['L5']

    fs = int(1000.0 / sim.cfg.recordStep)
    t_spec = np.linspace(0, index2ms(len(dplsum), fs), len(dplsum))
    spec = MorletSpec(dplsum, fs, freqmin=minFreq, freqmax=maxFreq, freqstep=stepFreq)
        
    f = np.array(range(minFreq, maxFreq+1, stepFreq))  # only used as output for user

    vmin = np.array(spec.TFR).min()
    vmax = np.array(spec.TFR).max()

    
    T = [0, sim.cfg.duration]
    F = spec.f
    if norm:
        spec.TFR = spec.TFR / vmax
        S = spec.TFR
        vc = [0, 1]
    else:
        S = spec.TFR
        vc = [vmin, vmax]


    # old code
    fig = plt.imshow(S, extent=(np.amin(T), np.amax(T), np.amin(F), np.amax(F)), origin='lower', interpolation='None', aspect='auto', vmin=vc[0], vmax=vc[1],
    cmap=plt.get_cmap('jet'))  # viridis
    plt.colorbar(label='Power')
    plt.gca().invert_yaxis()
    plt.ylabel('Hz')
    plt.tight_layout()
    if showFig:
        plt.show()            


    # TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

    # fig = figure(title="Dipole Spectrogram Plot", tools=TOOLS, toolbar_location='above',
    # plot_width=S.shape[1], plot_height=S.shape[0], x_axis_label="Time (ms)", y_axis_label='Frequency (Hz)')

    # fig.image(image=[S], x=[0], y=[0], dw=[S.shape[1]], dh=[S.shape[0]], palette='Spectral11')
    
    # steps = list(range(0, S.shape[1], int(1./fs*1e6)))
    # fig.xaxis.ticker = steps
    # fig.xaxis.major_label_overrides = {t*40000/1e6: str(t) for t in T}

    # fig.legend.location = "top_right"
    # fig.legend.click_policy = "hide"

    # plot_layout = layout(fig, sizing_mode='stretch_both')
    # html = file_html(plot_layout, CDN, title="Dipole Spectrogram Plot")


    # if showFig:
    #     show(fig)

    return fig #html


# -------------------------------------------------------------------------------------------------------------------
## Plot interactive dipole Spectrogram
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotDipolePSD(expData={'label': 'Experiment', 'x':[], 'y':[]}, minFreq = 1, maxFreq = 80, stepFreq = 1, norm = True, showFig=False):
    '''
    expData: experimental data; a dict with ['x'] and ['y'] 1-d vectors (either lists or np.arrays) of same length
    showFig: show output figure in web browser (default: None)
    '''
    from .. import sim
    from bokeh.plotting import figure, show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import layout


    # renormalize the dipole and save
    def baseline_renormalize():
        # N_pyr cells in grid. This is PER LAYER
        N_pyr = sim.cfg.N_pyr_x * sim.cfg.N_pyr_y
        # dipole offset calculation: increasing number of pyr cells (L2 and L5, simultaneously)
        # with no inputs resulted in an aggregate dipole over the interval [50., 1000.] ms that
        # eventually plateaus at -48 fAm. The range over this interval is something like 3 fAm
        # so the resultant correction is here, per dipole
        # dpl_offset = N_pyr * 50.207
        dpl_offset = {
            # these values will be subtracted
            'L2': N_pyr * 0.0443,
            'L5': N_pyr * -49.0502
            # 'L5': N_pyr * -48.3642,
            # will be calculated next, this is a placeholder
            # 'agg': None,
        }

        # L2 dipole offset can be roughly baseline shifted over the entire range of t
        dpl = {'L2': np.array(sim.simData['dipole']['L2']),
               'L5': np.array(sim.simData['dipole']['L5'])}
        dpl['L2'] -= dpl_offset['L2']

        # L5 dipole offset should be different for interval [50., 500.] and then it can be offset
        # slope (m) and intercept (b) params for L5 dipole offset
        # uncorrected for N_cells
        # these values were fit over the range [37., 750.)
        m = 3.4770508e-3
        b = -51.231085
        # these values were fit over the range [750., 5000]
        t1 = 750.
        m1 = 1.01e-4
        b1 = -48.412078

        t = sim.simData['t']

        # piecewise normalization
        dpl['L5'][t <= 37.] -= dpl_offset['L5']
        dpl['L5'][(t > 37.) & (t < t1)] -= N_pyr * (m * t[(t > 37.) & (t < t1)] + b)
        dpl['L5'][t >= t1] -= N_pyr * (m1 * t[t >= t1] + b1)
        # recalculate the aggregate dipole based on the baseline normalized ones
        dpl['agg'] = dpl['L2'] + dpl['L5']

        return dpl

    # convolve with a hamming window
    def hammfilt(x, winsz):
        from pylab import convolve
        from numpy import hamming
        win = hamming(winsz)
        win /= sum(win)
        return convolve(x,win,'same')

    # baseline renormalize
    dpl = baseline_renormalize()

    # convert units from fAm to nAm, rescale and smooth
    for key in dpl.keys():
        dpl[key] *= 1e-6 * sim.cfg.dipole_scalefctr
        
        if sim.cfg.dipole_smooth_win > 0:
            dpl[key] = hammfilt(dpl[key], sim.cfg.dipole_smooth_win/sim.cfg.dt)

        # Set index 0 to 0
        dpl[key][0] = 0.0


    # plot recorded dipole data
    #fig.line(sim.simData['t'], dpl['L2']+dpl['L5'], color='blue', legend="Aggregate", line_width=2.0)

    # plot Morlet spectrogram
    from ..support.morlet import MorletSpec, index2ms

    spec = []
    dplsum = dpl['L2'] + dpl['L5']

    fs = int(1000.0 / sim.cfg.recordStep)
    t_spec = np.linspace(0, index2ms(len(dplsum), fs), len(dplsum))
    spec = MorletSpec(dplsum, fs, freqmin=minFreq, freqmax=maxFreq, freqstep=stepFreq)
        
    f = np.array(range(minFreq, maxFreq+1, stepFreq))  # only used as output for user

    vmin = np.array(spec.TFR).min()
    vmax = np.array(spec.TFR).max()
    
    T = [0, sim.cfg.duration]
    F = spec.f
    S = spec.TFR
    vc = [vmin, vmax]

    Fs = int(1000.0/sim.cfg.recordStep)

    signal = np.mean(S, 1)

    # plot
    TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

    fig = figure(title="Dipole PSD Plot", tools=TOOLS, toolbar_location='above', x_axis_label="Frequency (Hz)", y_axis_label='Power')

    fig.line(F, signal, color='black', line_width=2.0)
    
    fig.legend.location = "top_right"
    fig.legend.click_policy = "hide"

    plot_layout = layout(fig, sizing_mode='stretch_both')
    html = file_html(plot_layout, CDN, title="Dipole PSD Plot")

    if showFig:
        show(fig)

    return html


# -------------------------------------------------------------------------------------------------------------------
## Plot interactive Spike Histogram
## ISSUES: Y scale, add colors to be effective
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotSpikeHist(include = ['allCells', 'eachPop'], legendLabels = [], timeRange = None, binSize = 5, overlay=True, yaxis = 'rate',
    popColors=[], norm=False, smooth=None, filtFreq=False, filtOrder=3, saveData = None, saveFig = None, showFig = False):
    '''
    Plot spike histogram
        - include (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): List of data series to include.
            Note: one line per item, not grouped (default: ['allCells', 'eachPop'])
        - timeRange ([start:stop]): Time range of spikes shown; if None shows all (default: None)
        - binSize (int): Size in ms of each bin (default: 5)
        - overlay (True|False): Whether to overlay the data lines or plot in separate subplots (default: True)
        - yaxis ('rate'|'count'): Units of y axis (firing rate in Hz, or spike count) (default: 'rate')
        - popColors (dict): Dictionary with color (value) used for each population (key) (default: None)
        - figSize ((width, height)): Size of figure (default: (10,8))
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure;
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure;
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)
        - Returns figure handle
    '''
        
    from .. import sim
    from bokeh.plotting import figure, show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import gridplot
    from bokeh.models import Legend
    from bokeh.colors import RGB
    
    print('Plotting interactive spike histogram...')

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

    colors = [RGB(*[round(f * 255) for f in color]) for color in colorList] # bokeh only handles integer rgb values from 0-255
            
    popColorDict=popColors.copy()
    if popColorDict:
        for pop, color in popColorDict.items():
            if not isinstance(color, RGB):
                popColorDict[pop] = RGB(*[round(f * 255) for f in color])
    
    if timeRange is None:
        timeRange = [0, sim.cfg.duration]

    if 'eachPop' in include:
        include.remove('eachPop')
        for pop in sim.net.allPops: include.append(pop)
        
    if yaxis == 'rate':
        if norm:
            yaxisLabel = 'Normalized firing rate'
        else:
            yaxisLabel = 'Avg cell firing rate (Hz)'
    elif yaxis == 'count':
        if norm:
            yaxisLabel = 'Normalized spike count'
        else:
            yaxisLabel = 'Spike count'
            
    figs=[]
    if overlay:
        figs.append(figure(title="Spike Historgram", tools=TOOLS, x_axis_label="Time (ms)", y_axis_label=yaxisLabel, toolbar_location='above'))
        fig = figs[0]
        legendItems = []  
      
    for iplot, subset in enumerate(include):
        if not overlay:
            figs.append(figure(title=str(subset), tools=TOOLS, x_axis_label="Time (ms)", y_axis_label=yaxisLabel))
            fig = figs[iplot]
                    
        if isinstance(subset, list):
            cells, cellGids, netStimLabels = getCellsInclude(subset)
        else:
            cells, cellGids, netStimLabels = getCellsInclude([subset])        
        numNetStims = 0

        # Select cells to include
        if len(cellGids) > 0:
            try:
                spkinds,spkts = list(zip(*[(spkgid,spkt) for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids]))
            except:
                spkinds,spkts = [],[]
        else:
            spkinds,spkts = [],[]

        spkts, spkinds = list(spkts), list(spkinds)
        numNetStims = 0
        if 'stims' in sim.allSimData:
            for netStimLabel in netStimLabels:
                netStimSpks = [spk for cell,stims in sim.allSimData['stims'].items() \
                               for stimLabel,stimSpks in stims.items() for spk in stimSpks if stimLabel == netStimLabel]
                if len(netStimSpks) > 0:
                    lastInd = max(spkinds) if len(spkinds)>0 else 0
                    spktsNew = netStimSpks
                    spkindsNew = [lastInd+1+i for i in range(len(netStimSpks))]
                    spkts.extend(spktsNew)
                    spkinds.extend(spkindsNew)
                    numNetStims += 1
        
        histo = np.histogram(spkts, bins = np.arange(timeRange[0], timeRange[1], binSize))
        histoT = histo[1][:-1]+binSize/2
        histoCount = histo[0]

        if yaxis=='rate':
            histoCount = histoCount * (1000.0 / binSize) / (len(cellGids)+numNetStims) # convert to firing rate
                    
        if filtFreq:
            from scipy import signal
            fs = 1000.0/binSize
            nyquist = fs/2.0
            if isinstance(filtFreq, list): # bandpass
                Wn = [filtFreq[0]/nyquist, filtFreq[1]/nyquist]
                b, a = signal.butter(filtOrder, Wn, btype='bandpass')
            elif isinstance(filtFreq, Number): # lowpass
                Wn = filtFreq/nyquist
                b, a = signal.butter(filtOrder, Wn)
            histoCount = signal.filtfilt(b, a, histoCount)

        if norm:
            histoCount /= max(histoCount)
            
        if smooth:
            histoCount = _smooth1d(histoCount, smooth)[:len(histoT)]
        
        if isinstance(subset, list): 
            color = colors[iplot%len(colors)]
        else:   
            color = popColorDict[subset] if subset in popColorDict else colors[iplot%len(colors)]
        
        label = legendLabels[iplot] if legendLabels else str(subset)
            
        s = fig.line(histoT, histoCount, line_width=2.0, name=str(subset), color=color)

        if overlay:
           legendItems.append((str(label), [s]))
    
    if overlay:
        legend = Legend(items=legendItems, location=(10,0))
        fig.add_layout(legend)
        fig.legend.click_policy='hide'
        fig.legend.location='top_right'

    print(figs)
    plot_layout = gridplot(figs, ncols=1, merge_tools=False, sizing_mode='stretch_both')
    html = file_html(plot_layout, CDN, title="Spike Historgram")

    if showFig: show(plot_layout)

    if saveFig:
        if isinstance(saveFig, str):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'ispikeHist.html'
        file = open(filename, 'w')
        file.write(html)
        file.close()

    return html

# -------------------------------------------------------------------------------------------------------------------
## Plot interactive Rate PSD
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotRatePSD(include = ['allCells', 'eachPop'], timeRange = None, binSize = 5, maxFreq = 100, NFFT = 256, noverlap = 128, smooth = 0, overlay=True, ylim = None,
                 popColors = {}, figSize=(1000, 400), saveData = None, saveFig = None, showFig = False):
    ''' 
    Plot firing rate power spectral density (PSD)
        - include (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): List of data series to include. 
            Note: one line per item, not grouped (default: ['allCells', 'eachPop'])
        - timeRange ([start:stop]): Time range of spikes shown; if None shows all (default: None)
        - binSize (int): Size in ms of spike bins (default: 5)
        - maxFreq (float): Maximum frequency to show in plot (default: 100)
        - NFFT (float): The number of data points used in each block for the FFT (power of 2) (default: 256)
        - smooth (int): Window size for smoothing; no smoothing if 0 (default: 0)
        - overlay (True|False): Whether to overlay the data lines or plot in separate subplots (default: True)
        - graphType ('line'|'bar'): Type of graph to use (line graph or bar plot) (default: 'line')
        - yaxis ('rate'|'count'): Units of y axis (firing rate in Hz, or spike count) (default: 'rate')
        - popColors (dict): Dictionary with color (value) used for each population (key) (default: None)
        - figSize ((width, height)): Size of figure (default: (10,8))
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure;
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure;
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)

        - Returns figure handle
    '''
    
    from .. import sim
    from bokeh.plotting import figure, show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import layout
    from bokeh.colors import RGB
    from bokeh.models import Legend
    
    print('Plotting interactive firing rate power spectral density (PSD) ...')

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

    colors = [RGB(*[round(f * 255) for f in color]) for color in colorList] # bokeh only handles integer rgb values from 0-255

    popColorDict=popColors.copy()
    if popColorDict:
        for pop, color in popColorDict.items():
            popColorDict[pop] = RGB(*[round(f * 255) for f in color])

    # Replace 'eachPop' with list of pops
    if 'eachPop' in include:
        include.remove('eachPop')
        for pop in sim.net.allPops: include.append(pop)

    # time range
    if timeRange is None:
        timeRange = [0,sim.cfg.duration]

    histData = []

    allPower, allSignal, allFreqs = [], [], []
    legendItems = []
    
    
    figs=[]
    if overlay:
        figs.append(figure(title="PSD Rate Plot", tools=TOOLS, x_axis_label="Frequncy (Hz)", y_axis_label="Power Spectral Density (db/Hz)", toolbar_location='above'))
        fig = figs[0]
        legendItems = []  

    # Plot separate line for each entry in include
    for iplot, subset in enumerate(include):
        if not overlay:
            figs.append(figure(title=str(subset), tools=TOOLS, x_axis_label="Frequency (HZ)", y_axis_label="Power Spectral Density (db/Hz)"))
            fig = figs[iplot]
            
        cells, cellGids, netStimLabels = getCellsInclude([subset])
        numNetStims = 0

        # Select cells to include
        if len(cellGids) > 0:
            try:
                spkinds,spkts = list(zip(*[(spkgid,spkt) for spkgid,spkt in zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids]))
            except:
                spkinds,spkts = [],[]
        else:
            spkinds,spkts = [],[]


        # Add NetStim spikes
        spkts, spkinds = list(spkts), list(spkinds)
        numNetStims = 0
        if 'stims' in sim.allSimData:
            for netStimLabel in netStimLabels:
                netStimSpks = [spk for cell,stims in sim.allSimData['stims'].items() \
                               for stimLabel,stimSpks in stims.items() for spk in stimSpks if stimLabel == netStimLabel]
                if len(netStimSpks) > 0:
                    lastInd = max(spkinds) if len(spkinds)>0 else 0
                    spktsNew = netStimSpks
                    spkindsNew = [lastInd+1+i for i in range(len(netStimSpks))]
                    spkts.extend(spktsNew)
                    spkinds.extend(spkindsNew)
                    numNetStims += 1

        histo = np.histogram(spkts, bins = np.arange(timeRange[0], timeRange[1], binSize))
        histoT = histo[1][:-1]+binSize/2
        histoCount = histo[0]
        histoCount = histoCount * (1000.0 / binSize) / (len(cellGids)+numNetStims) # convert to rates

        histData.append(histoCount)

        Fs = 1000.0 / binSize
        power = mlab.psd(histoCount, Fs=Fs, NFFT=NFFT, detrend=mlab.detrend_none, window=mlab.window_hanning,
                         noverlap=noverlap, pad_to=None, sides='default', scale_by_freq=None)

        if smooth:
            signal = _smooth1d(10*np.log10(power[0]), smooth)
        else:
            signal = 10*np.log10(power[0])

        freqs = power[1]

        color = popColorDict[subset] if subset in popColorDict else colors[iplot%len(colors)]
        
        allFreqs.append(freqs)
        allPower.append(power)
        allSignal.append(signal)
        s = fig.line(freqs[freqs<maxFreq], signal[freqs<maxFreq], line_width = 2.0, color=color)
        if overlay: legendItems.append((subset, [s]))

    if overlay: 
        legend = Legend(items=legendItems)
        legend.click_policy = 'hide'
        fig.add_layout(legend)

    plot_layout = layout(figs, ncols=1, plot_width=figSize[0], figHeight=figSize[1], sizing_mode='stretch_both')
    html = file_html(plot_layout, CDN, title="PSD Rate Plot")

    if showFig: show(plot_layout)

    if saveFig:
        if isinstance(saveFig, str):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'ipsd.html'
        file = open(filename, 'w')
        file.write(html)
        file.close()

    return html

# -------------------------------------------------------------------------------------------------------------------
## Plot interactive Traces
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotTraces(include=None, timeRange=None, overlay=False, oneFigPer='cell', rerun=False, colors=None, ylim=None, axis='on', fontSize=12, figSize=(10,8), saveData=None, saveFig=None, showFig=True, ylabel=None, linkAxes=False):
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
    from bokeh.plotting import figure, show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import layout, column
    from bokeh.models import HoverTool
    from bokeh.models import Legend
    from bokeh.colors import RGB
    
    print('Plotting interactive recorded cell traces per', oneFigPer)

    TOOLS = 'save,pan,box_zoom,reset,wheel_zoom'
    colors = [RGB(*[round(f * 255) for f in color]) for color in colorList] # bokeh only handles integer rgb values from 0-255

    if include is None:  # if none, record from whatever was recorded
        if 'plotTraces' in sim.cfg.analysis and 'include' in sim.cfg.analysis['plotTraces']:
            include = sim.cfg.analysis['plotTraces']['include'] + sim.cfg.recordCells
        else:
            include = sim.cfg.recordCells

    if timeRange is None:
        timeRange = [0,sim.cfg.duration]

    tracesList = list(sim.cfg.recordTraces.keys())
    tracesList.sort()
    cells, cellGids, _ = getCellsInclude(include)
    gidPops = {cell['gid']: cell['tags']['pop'] for cell in cells}

    recordStep = sim.cfg.recordStep

    figs = {}
    tracesData = []

    if ylabel is None:
        y_axis_label = None
    else:
        y_axis_label = ylabel

    if oneFigPer == 'cell':
        
        for gid in cellGids:

            if overlay:
                figs['_gid_' + str(gid)] = figure(title = "Cell {}, Pop {}".format(gid, gidPops[gid]), 
                                                  tools = TOOLS, 
                                                  active_drag = 'pan', 
                                                  active_scroll = 'wheel_zoom',
                                                  x_axis_label="Time (ms)",
                                                  y_axis_label=y_axis_label
                                                  )
                fig = figs['_gid_' + str(gid)]

            else:
                figs['_gid_' + str(gid)] = []

            for itrace, trace in enumerate(tracesList):
                if 'cell_{}'.format(gid) in sim.allSimData[trace]:
                    fullTrace = sim.allSimData[trace]['cell_{}'.format(gid)]
                    if isinstance(fullTrace, dict):
                        data = [fullTrace[key][int(timeRange[0]/recordStep):int(timeRange[1]/recordStep)] for key in list(fullTrace.keys())]
                        lenData = len(data[0])
                        data = np.transpose(np.array(data))
                    else:
                        data = fullTrace[int(timeRange[0]/recordStep):int(timeRange[1]/recordStep)]
                        lenData = len(data)
                    t = np.arange(timeRange[0], timeRange[1]+recordStep, recordStep)
                    tracesData.append({'t': t, 'cell_'+str(gid)+'_'+trace: data})
                    
                    if overlay:
                        fig.line(t[:lenData], data, line_width=2, line_color=colors[itrace], legend_label=trace)
                        hover = HoverTool(tooltips=[('Time', '@x'), ('Value', '@y')], mode='vline')
                        fig.add_tools(hover)
                        fig.legend.click_policy="hide"
                    else:
                        subfig = figure(title = "Cell {}, Pop {}".format(gid, gidPops[gid]), 
                                        tools = TOOLS, 
                                        active_drag = 'pan', 
                                        active_scroll = 'wheel_zoom',
                                        x_axis_label="Time (ms)",
                                        y_axis_label=y_axis_label
                                        )
                        subfig.line(t[:lenData], data, line_width=2, line_color=colors[itrace], legend_label=trace)
                        if linkAxes:
                            if itrace > 0:
                                subfig.x_range = figs['_gid_' + str(gid)][0].x_range
                                subfig.y_range = figs['_gid_' + str(gid)][0].y_range
                        hover = HoverTool(tooltips=[('Time', '@x'), ('Value', '@y')], mode='vline')
                        subfig.add_tools(hover)
                        subfig.legend.click_policy="hide"
                        figs['_gid_' + str(gid)].append(subfig)

    elif oneFigPer == 'trace':

        for itrace, trace in enumerate(tracesList):
            
            if overlay:
                figs['_trace_' + str(trace)] = figure(title = str(trace), 
                                                  tools = TOOLS, 
                                                  active_drag = 'pan', 
                                                  active_scroll = 'wheel_zoom',
                                                  x_axis_label="Time (ms)",
                                                  y_axis_label=y_axis_label
                                                  )
                fig = figs['_trace_' + str(trace)]

            else:
                figs['_trace_' + str(trace)] = []

            for igid, gid in enumerate(cellGids):
                if 'cell_'+str(gid) in sim.allSimData[trace]:
                    fullTrace = sim.allSimData[trace]['cell_'+str(gid)]
                    if isinstance(fullTrace, dict):
                        data = [fullTrace[key][int(timeRange[0]/recordStep):int(timeRange[1]/recordStep)] for key in list(fullTrace.keys())]
                        lenData = len(data[0])
                        data = np.transpose(np.array(data))
                    else:
                        data = np.array(fullTrace[int(timeRange[0]/recordStep):int(timeRange[1]/recordStep)])
                        lenData = len(data)
                    t = np.arange(timeRange[0], timeRange[1]+recordStep, recordStep)
                    tracesData.append({'t': t, 'cell_'+str(gid)+'_'+trace: data})
                                        
                    if overlay:
                        fig.line(t[:lenData], data, line_width=2, line_color=colors[igid], legend_label='Cell %d, Pop %s '%(int(gid), gidPops[gid]))
                        hover = HoverTool(tooltips=[('Time', '@x'), ('Value', '@y')], mode='vline')
                        fig.add_tools(hover)
                        fig.legend.click_policy="hide"
                    else:
                        subfig = figure(title = str(trace), 
                                        tools = TOOLS, 
                                        active_drag = 'pan', 
                                        active_scroll = 'wheel_zoom',
                                        x_axis_label="Time (ms)",
                                        y_axis_label=y_axis_label
                                        )

                        if isinstance(data, list):
                            for tl,dl in zip(t,data):
                                subfig.line(tl[:len(dl)], dl, line_width=1.5, line_color=colors[igid], legend_label='Cell %d, Pop %s '%(int(gid), gidPops[gid]))
                        else:
                            subfig.line(t[:len(data)], data, line_width=1.5, line_color=colors[igid], legend_label='Cell %d, Pop %s '%(int(gid), gidPops[gid]))

                        if linkAxes:
                            if igid > 0:
                                subfig.x_range = figs['_trace_' + str(trace)][0].x_range
                                subfig.y_range = figs['_trace_' + str(trace)][0].y_range
                        hover = HoverTool(tooltips=[('Time', '@x'), ('Value', '@y')], mode='vline')
                        subfig.add_tools(hover)
                        subfig.legend.click_policy="hide"
                        figs['_trace_' + str(trace)].append(subfig)
                    
                    
    for figLabel, figObj in figs.items():

        if overlay:
            plot_layout = layout(figObj, sizing_mode='stretch_both')
            html = file_html(plot_layout, CDN, title=figLabel)
            overlay_text = '_overlay'
        else:
            plot_layout = column(*figObj, sizing_mode='stretch_both')
            html = file_html(plot_layout, CDN, title=figLabel)
            overlay_text = ''

        if showFig: show(plot_layout)

        if saveFig:
            if isinstance(saveFig, str):
                filename = saveFig
            else:
                filename = sim.cfg.filename + '_iplot_traces' + figLabel + overlay_text + '.html'
            file = open(filename, 'w')
            file.write(html)
            file.close()

    return html


# -------------------------------------------------------------------------------------------------------------------
## Plot interactive LFP
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotLFP(electrodes = ['avg', 'all'], plots = ['timeSeries', 'PSD', 'spectrogram', 'locations'], timeRange = None, NFFT = 256, noverlap = 128,
             nperseg = 256, maxFreq = 100, smooth = 0, separation = 1.0, includeAxon=True, logx=False, logy=False, norm=False, dpi = 200, overlay=False, filtFreq = False, filtOrder=3, detrend=False, colors = None, saveData = None, saveFig = None, showFig = False):
    from .. import sim
    from bokeh.plotting import figure, show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import layout, column, row
    from bokeh.colors import RGB

    print('Plotting interactive LFP ...')

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

    if timeRange is None:
        timeRange = [0,sim.cfg.duration]

    lfp = np.array(sim.allSimData['LFP'])[int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep),:]

    if not colors:
        colors = [RGB(*[round(f * 255) for f in color]) for color in colorList] # bokeh only handles integer rgb values from 0-255

    # electrode selection
    if 'all' in electrodes:
        electrodes.remove('all')
        electrodes.extend(list(range(int(sim.net.recXElectrode.nsites))))

    figs = {}
    data = {'lfp': lfp}

    # time series plot
    # TODO add scalebar
    if 'timeSeries' in plots:
        figs['timeSeries'] = figure(title="LFP Time Series Plot", tools=TOOLS, x_axis_label="Time (ms)", y_axis_label="LFP electrode")
        figs['timeSeries'].yaxis.major_tick_line_color = None
        figs['timeSeries'].yaxis.minor_tick_line_color = None
        figs['timeSeries'].yaxis.major_label_text_font_size = '0pt'
        figs['timeSeries'].yaxis.axis_line_color = None
        figs['timeSeries'].ygrid.visible = False

        ydisp = np.absolute(lfp).max() * separation
        offset = 1.0*ydisp
        t = np.arange(timeRange[0], timeRange[1], sim.cfg.recordStep)

        for i,elec in enumerate(electrodes[::-1]):
            if elec == 'avg':
                dplSum = np.mean(lfp, axis=1)
                color = 'black'
                lw=1.0
                # figs['timeSeries'].line(t, -lfpPlot+(i*ydisp), line_color=color)
            elif isinstance(elec, Number) and elec <= sim.net.recXElectrode.nsites:
                pass
                lfpPlot = lfp[:, elec]
                color = colors[i%len(colors)]
                lw=1.0

            legend=str(elec)
            # if len(electrodes) > 1:
            #     legend=str(elec)
            # else:
            #     legend=None

            figs['timeSeries'].line(t, lfpPlot+(i*ydisp), color=color, name=str(elec), legend=legend)

        data['lfpPlot'] = lfpPlot
        data['ydisp'] =  ydisp
        data['t'] = t

        figs['timeSeries'].legend.location = "top_right"
        figs['timeSeries'].legend.click_policy = "hide"

        plot_layout = layout(figs['timeSeries'], sizing_mode='stretch_both')
        html = file_html(plot_layout, CDN, title="Time Series LFP Plot")

        if saveFig:
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename+'_'+'lfp_timeseries.png'
            file = open(filename, 'w')
            file.write(html)
            file.close()

    # PSD ----------------------------------
    # TODO fix final layout of plots
    if 'PSD' in plots:

        figs['psd'] = []
        allFreqs = []
        allSignal = []
        data['allFreqs'] = allFreqs
        data['allSignal'] = allSignal

        for i,elec in enumerate(electrodes):
            p = figure(title="Electrode {}".format(str(elec)), tools=TOOLS, x_axis_label="Frequency (Hz)", y_axis_label="db/Hz")

            if elec == 'avg':
                lfpPlot = np.mean(lfp, axis=1)
                color = 'black'
                lw=1.5
            elif isinstance(elec, Number) and elec <= sim.net.recXElectrode.nsites:
                lfpPlot = lfp[:, elec]
                color = colors[i%len(colors)]
                lw=1.5

            Fs = int(1000.0/sim.cfg.recordStep)
            power = mlab.psd(lfpPlot, Fs=Fs, NFFT=NFFT, detrend=mlab.detrend_none, window=mlab.window_hanning,
                             noverlap=noverlap, pad_to=None, sides='default', scale_by_freq=None)

            if smooth:
                signal = _smooth1d(10*np.log10(power[0]), smooth)
            else:
                signal = 10*np.log10(power[0])
            freqs = power[1]

            allFreqs.append(freqs)
            allSignal.append(signal)

            p.line(freqs[freqs<maxFreq], signal[freqs<maxFreq], color=color)
            figs['psd'].append(p)

        # format plot

        plot_layout = column(figs['psd'] )
        html = file_html(plot_layout, CDN, title="LFP Power Spectral Density")

        show(plot_layout)


        if saveFig:
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename+'_'+'lfp_psd.png'
            file = open(filename, 'w')
            file.write(html)
            file.close()


    # Spectrogram ------------------------------
    # TODO impprove the color mapper to be more detailed
    if 'spectrogram' in plots:
        import matplotlib.cm as cm
        from bokeh.transform import linear_cmap
        from bokeh.models import ColorBar
        from scipy import signal as spsig

        # numCols = np.round(len(electrodes) / maxPlots) + 1
        figs['spectro'] = []
        #t = np.arange(timeRange[0], timeRange[1], sim.cfg.recordStep)

        logx_spec = []

        for i,elec in enumerate(electrodes):
            if elec == 'avg':
                lfpPlot = np.mean(lfp, axis=1)
            elif isinstance(elec, Number) and elec <= sim.net.recXElectrode.nsites:
                lfpPlot = lfp[:, elec]
            # creates spectrogram over a range of data
            # from: http://joelyancey.com/lfp-python-practice/
            fs = int(1000.0/sim.cfg.recordStep)
            f, t_spec, x_spec = spsig.spectrogram(lfpPlot, fs=fs, window='hanning',
                                                  detrend=mlab.detrend_none, nperseg=nperseg, noverlap=noverlap, nfft=NFFT,  mode='psd')
            x_mesh, y_mesh = np.meshgrid(t_spec*1000.0, f[f<maxFreq])
            logx_spec.append(10*np.log10(x_spec[f<maxFreq]))

        vmin = np.array(logx_spec).min()
        vmax = np.array(logx_spec).max()

        for i,elec in enumerate(electrodes):
            p = figure(title="Electrode {}".format(str(elec)), tools=TOOLS, x_range=(0, timeRange[1]), y_range=(0, maxFreq),
                       x_axis_label = "Time (ms)", y_axis_label = "Frequency(Hz)")
            mapper = linear_cmap (field_name='dB/Hz', palette='Spectral11', low=vmin, high=vmax)
            color_bar = ColorBar(color_mapper=mapper['transform'], width=8, location=(0,0), label_standoff=7, major_tick_line_color=None)
            p.image(image=[x_mesh, y_mesh, logx_spec[i]], x=0, y=0, color_mapper=mapper['transform'], dw=timeRange[1], dh=100)
            p.add_layout(color_bar, 'right')
            figs['spectro'].append(p)


        plot_layout = column(figs['spectro'] )
        html = file_html(plot_layout, CDN, title="LFP Power Spectral Density")

        show(plot_layout)

        if saveFig:
            if isinstance(saveFig, str):
                filename = saveFig
            else:
                filename = sim.cfg.filename+'_'+'lfp_spectrogram.png'
            file = open(filename, 'w')
            file.write(html)
            file.close()

    return html


# -------------------------------------------------------------------------------------------------------------------
## Plot interactive connectivity
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotConn(includePre=['all'], includePost=['all'], feature='strength', orderBy='gid', figSize=(10,10), groupBy='pop', groupByIntervalPre=None, groupByIntervalPost=None, removeWeightNorm=False, graphType='matrix', synOrConn='syn', synMech=None, connsFile=None, tagsFile=None, clim=None, fontSize=12, saveData=None, saveFig=None, showFig=False): 
    ''' 
    Plot network connectivity
        - includePre (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Cells to show (default: ['all'])
        - includePost (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Cells to show (default: ['all'])
        - feature ('weight'|'delay'|'numConns'|'probability'|'strength'|'convergence'|'divergence'): Feature to show in connectivity matrix; 
            the only features applicable to groupBy='cell' are 'weight', 'delay' and 'numConns';  'strength' = weight * probability (default: 'strength')
        - groupBy ('pop'|'cell'|'y'|: Show matrix for individual cells, populations, or by other numeric tag such as 'y' (default: 'pop')
        - groupByInterval (int or float): Interval of groupBy feature to group cells by in conn matrix, e.g. 100 to group by cortical depth in steps of 100 um   (default: None)
        - orderBy ('gid'|'y'|'ynorm'|...): Unique numeric cell property to order x and y axes by, e.g. 'gid', 'ynorm', 'y' (requires groupBy='cells') (default: 'gid')
        - graphType ('matrix','bar','pie'): Type of graph to represent data (default: 'matrix')
        - synOrConn ('syn'|'conn'): Use synapses or connections; note 1 connection can have multiple synapses (default: 'syn')
        - figSize ((width, height)): Size of figure (default: (10,10))
        - synMech (['AMPA', 'GABAA',...]): Show results only for these syn mechs (default: None)
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure; 
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure; 
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)

        - Returns figure handles
    '''
    
    from netpyne import sim
    from netpyne.analysis import network
    from bokeh.plotting import figure, show
    from bokeh.transform import linear_cmap
    from bokeh.palettes import Viridis256
    from bokeh.palettes import viridis 
    from bokeh.models import ColorBar
    from bokeh.embed import file_html
    from bokeh.resources import CDN
    from bokeh.layouts import layout
    from bokeh.colors import RGB

    print('Plotting interactive connectivity matrix...')

    if connsFile and tagsFile:
        connMatrix, pre, post = network._plotConnCalculateFromFile(includePre, includePost, feature, orderBy, groupBy, groupByIntervalPre, groupByIntervalPost, synOrConn, synMech, connsFile, tagsFile, removeWeightNorm)
    else:
        connMatrix, pre, post = network._plotConnCalculateFromSim(includePre, includePost, feature, orderBy, groupBy, groupByIntervalPre, groupByIntervalPost, synOrConn, synMech, removeWeightNorm)


    if connMatrix is None:
        print("  Error calculating connMatrix in iplotConn()")
        return None

    # TODO: set plot font size in Bokeh

    # for groupBy = 'cell' (needed to properly format data for Bokeh)
    if groupBy == 'cell':
        pre = [str(cell['gid']) for cell in pre]
        post = [str(cell['gid']) for cell in post]

    # matrix plot
    if graphType == 'matrix':
        
        pandas_data = pd.DataFrame(data=connMatrix, index=pre, columns=post)
        pandas_data.index.name = 'pre'
        pandas_data.columns.name = 'post'
        bokeh_data = pandas_data.reset_index().melt(id_vars=['pre'], value_name=feature)

        # the colormapper doesn't work if both high and low values are the same
        low = np.nanmin(connMatrix)
        high = np.nanmax(connMatrix)
        if low == high:
            low = low - 0.1 * low
            high = high + 0.1 * high

        conn_colormapper = linear_cmap(
        field_name=feature,
        palette=Viridis256,
        low=low,
        high=high,
        nan_color='white'
        )

        conn_colorbar = ColorBar(color_mapper=conn_colormapper['transform'])
        conn_colorbar.location = (0, 0)
        conn_colorbar.title = feature

        fig = figure(
            x_range=pandas_data.columns.values,
            y_range=np.flip(pandas_data.index.values),
            tools = 'hover,save,pan,box_zoom,reset,wheel_zoom',
            active_drag = 'pan',
            active_scroll = 'wheel_zoom',
            tooltips=[('Pre', '@pre'), ('Post', '@post'), (feature, '@' + feature)],
            title='Connection ' + feature + ' matrix',
            toolbar_location='below',
            x_axis_location='above'
            )

        fig.xaxis.axis_label = pandas_data.columns.name
        fig.yaxis.axis_label = pandas_data.index.name
        fig.yaxis.major_label_orientation = 'horizontal'
        fig.xaxis.major_label_orientation = 'vertical'

        fig.rect(
            source=bokeh_data, 
            x='post', 
            y='pre', 
            width=1, 
            height=1, 
            color=conn_colormapper
            )

        fig.add_layout(conn_colorbar, 'right')
        
        # TODO: add grid lines?
            
    # stacked bar graph
    elif graphType == 'bar':
        if groupBy == 'pop':
            
            popsPre, popsPost = pre, post
            colors = [RGB(*[round(f * 255) for f in color]) for color in colorList] # bokeh only handles integer rgb values from 0-255
            bar_colors = colors[0:len(popsPre)]

            data = {'post' : popsPost}
            for popIndex, pop in enumerate(popsPre):
                data[pop] = connMatrix[popIndex, :]

            fig = figure(
                x_range=popsPost, 
                title='Connection ' + feature + ' stacked bar graph',
                toolbar_location=None, 
                tools='hover,save,pan,box_zoom,reset,wheel_zoom', 
                active_drag='pan', 
                active_scroll = 'wheel_zoom', 
                tooltips=[('Pre', '$name'), ('Post', '@post'), (feature, '@$name')],
                )

            fig.vbar_stack(
                popsPre, 
                x='post', 
                width=0.9, 
                color=bar_colors, 
                source=data,
                legend_label=popsPre,
                )

            fig.xgrid.grid_line_color = None
            fig.legend.title = 'Pre'
            fig.xaxis.axis_label = 'Post'
            fig.yaxis.axis_label = feature

        elif groupBy == 'cell':
            print('  Error: plotConn graphType="bar" with groupBy="cell" not yet implemented')
            return None

    elif graphType == 'pie':
        print('  Error: plotConn graphType="pie" not yet implemented')
        return None

    plot_layout = layout([fig], sizing_mode='stretch_both')
    html = file_html(plot_layout, CDN, title='Connection ' + feature + ' matrix')

    #save figure data
    if saveData:
        figData = {'connMatrix': connMatrix, 'feature': feature, 'groupBy': groupBy,
         'includePre': includePre, 'includePost': includePost, 'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}
    
        _saveFigData(figData, saveData, 'conn')
 
    # save figure
    if saveFig: 
        if isinstance(saveFig, str):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_iplot_conn_'+groupBy+'_'+feature+'_'+graphType+'.html'
        file = open(filename, 'w')
        file.write(html)
        file.close()

    # show fig 
    if showFig: show(fig)

    return html
