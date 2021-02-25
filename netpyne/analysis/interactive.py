"""
Module for production of interactive plots

"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from netpyne import __gui__

try:
    basestring
except NameError:
    basestring = str

if __gui__:
    import matplotlib.pyplot as plt
    from matplotlib import mlab
    from matplotlib_scalebar import scalebar
from numbers import Number
from .utils import colorList, exception, getSpktSpkid, _showFigure, _saveFigData, getCellsInclude, syncMeasure, _smooth1d, _guiTheme

import numpy as np
import pandas as pd

from bokeh.themes import built_in_themes
from bokeh.io import curdoc
from bokeh.palettes import Viridis256
from bokeh.models import HoverTool

bokeh_theme = curdoc().theme



# -------------------------------------------------------------------------------------------------------------------
## Plot interactive raster
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotRaster(include=['allCells'], timeRange=None, maxSpikes=1e8, orderBy='gid', orderInverse=False, popRates=False, spikeHist=False, spikeHistBin=5, syncLines=False, marker='circle', markerSize=3, popColors=None, saveData=None, saveFig=None, showFig=False, **kwargs):
    """
    Function for/to <short description of `netpyne.analysis.interactive.iplotRaster`>

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
        **Options:** ``<option>`` <description of option>

    maxSpikes : int
        Maximum number of spikes to be plotted.
        **Default:** ``1e8``
        **Options:** ``<option>`` <description of option>

    orderBy : str
        Unique numeric cell property by which to order the y-axis.
        **Default:** ``'gid'`` orders by cell ID
        **Options:**
        ``'y'`` orders by cell y-location,
        ``'ynorm'`` orders by cell normalized y-location

    orderInverse : bool
        Inverts the y-axis order if ``True``.
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    popRates : bool
        Include population firing rates on plot if ``True``.
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    spikeHist : bool
        Include spike histogram (spikes/bin) on plot if ``True``.
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    spikeHistBin : int
        Size of bin in ms to use for spike histogram.
        **Default:** ``5``
        **Options:** ``<option>`` <description of option>

    syncLines : bool
        Calculate synchrony measure and plot vertical lines for each spike to evidence synchrony if ``True``.
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    marker : str
        `Bokeh marker <https://docs.bokeh.org/en/latest/docs/gallery/markers.html>`_ for each spike.
        **Default:** ``'circle'``
        **Options:** ``<option>`` <description of option>

    markerSize : int
        Size of Bokeh marker for each spike.
        **Default:** ``3``
        **Options:** ``<option>`` <description of option>

    popColors : dict
        Dictionary with custom color (value) used for each population (key).
        **Default:** ``None`` uses standard colors
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
        ``'/path/filename.html'`` saves to a custom path and filename, only valid file extension is ``'.html'``

    showFig : bool
        Shows the figure if ``True``.
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    kwargs : <type>
        <Short description of kwargs>
        **Default:** *required*

    Returns
    -------


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

    theme = None
    if 'theme' in kwargs:
        if kwargs['theme'] != 'default':
            if kwargs['theme'] == 'gui':
                from bokeh.themes import Theme
                theme = Theme(json=_guiTheme)
            else:
                theme = kwargs['theme']
            curdoc().theme = theme

    TOOLS = 'hover,save,pan,box_zoom,reset,wheel_zoom',

    if not 'palette' in kwargs:
        colors = [RGB(*[round(f * 255) for f in color]) for color in colorList] # bokeh only handles integer rgb values from 0-255
    else:
        colors = kwargs['palette']

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
            sel, spkts, spkgids = getSpktSpkid(cellGids=[] if include == ['allCells'] else cellGids, timeRange=timeRange)
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
        active_drag = None,
        active_scroll = None,
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
    html = file_html(plot_layout, CDN, title="Raster Plot", theme=theme)

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
            filename = sim.cfg.filename + '_iraster_' + orderBy + '.html'
        file = open(filename, 'w')
        file.write(html)
        file.close()

    if showFig: show(plot_layout)

    return html, {'include': include, 'spkts': spkts, 'spkinds': sel['spkind'].tolist(), 'timeRange': timeRange}


# -------------------------------------------------------------------------------------------------------------------
## Plot interactive dipole
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotDipole(expData={'label': 'Experiment', 'x':[], 'y':[]}, dpl=None, t=None,  showFig=False, **kwargs):
    """
    Function for/to <short description of `netpyne.analysis.interactive.iplotDipole`>

    Parameters
    ----------
    expData : dict
        <Short description of expData>
        **Default:** ``{'label': 'Experiment', 'x': [], 'y': []}``
        **Options:** ``<option>`` <description of option>

    showFig : bool
        <Short description of showFig>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    kwargs : <type>
        <Short description of kwargs>
        **Default:** *required*

"""

    from .. import sim
    from bokeh.plotting import figure, show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import layout

    theme = None
    from bokeh.colors import RGB

    if 'theme' in kwargs:
        if kwargs['theme'] != 'default':
            if kwargs['theme'] == 'gui':
                from bokeh.themes import Theme
                theme = Theme(json=_guiTheme)
            else:
                theme = kwargs['theme']
            curdoc().theme = theme

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

    fig = figure(title="Dipole Plot", tools=TOOLS, toolbar_location='above', x_axis_label="Time (ms)", y_axis_label='Dipole (nAM x 3000)')

    if not 'palette' in kwargs:
        colors = [RGB(*[round(f * 255) for f in color]) for color in colorList] # bokeh only handles integer rgb values from 0-255
    else:
        colors = kwargs['palette']

    # renormalize the dipole and save
    def baseline_renormalize():

        dpl = {k: np.array(v) for k, v in sim.allSimData['dipole'].items()}
        t = sim.simData['t']

        # ad hoc postprocessing of dipole signal in orig HNN model L2 and L5
        if 'L2' in dpl and 'L5' in dpl:
            # N_pyr cells in grid. This is PER LAYER
            N_pyr = sim.cfg.hnn_params['N_pyr_x'] * sim.cfg.hnn_params['N_pyr_y']
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

            # piecewise normalization
            dpl['L5'][t <= 37.] -= dpl_offset['L5']
            dpl['L5'][(t > 37.) & (t < t1)] -= N_pyr * (m * t[(t > 37.) & (t < t1)] + b)
            dpl['L5'][t >= t1] -= N_pyr * (m1 * t[t >= t1] + b1)

        # recalculate the aggregate dipole based on the baseline normalized ones
        dpl['Aggregate'] = np.sum(list(dpl.values()), axis=0)

        return dpl

    # convolve with a hamming window
    def hammfilt(x, winsz):
        from pylab import convolve
        from numpy import hamming
        win = hamming(winsz)
        win /= sum(win)
        return convolve(x,win,'same')

    # baseline renormalize
    if dpl:
        dpl = {k: np.array(v) for k, v in dpl.items()}
    else:
        dpl = baseline_renormalize()

    if t is not None and len(t)>0:
        t=np.array(t)
    else:
        t=sim.simData['t']

        
    # convert units from fAm to nAm, rescale and smooth
    for key in dpl.keys():
        dpl[key] *= 1e-6 * sim.cfg.hnn_params['dipole_scalefctr']

        if sim.cfg.hnn_params['dipole_smooth_win'] > 0:
            dpl[key] = hammfilt(dpl[key], sim.cfg.hnn_params['dipole_smooth_win']/sim.cfg.dt)

        # Set index 0 to 0
        dpl[key][0] = 0.0

    # plot exp data
    #fig.line(expData['x'], expData['y'], color='black', legend=expData['label'])

    # plot recorded dipole data
    for i,(k,v) in enumerate(dpl.items()):
        fig.line(t, v, legend=k, color=colors[i], line_width=2.0)

    fig.legend.location = "top_right"
    fig.legend.click_policy = "hide"

    plot_layout = layout(fig, sizing_mode='stretch_both')
    html = file_html(plot_layout, CDN, title="Dipole Plot", theme=theme)

    if showFig:
        show(fig)

    return html, dpl


# -------------------------------------------------------------------------------------------------------------------
## Plot interactive dipole Spectrogram
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotDipoleSpectrogram(expData={'label': 'Experiment', 'x':[], 'y':[]}, dpl=None, minFreq = 1, maxFreq = 80, stepFreq = 1, norm = True, showFig=False, **kwargs):
    """
    Function for/to <short description of `netpyne.analysis.interactive.iplotDipoleSpectrogram`>

    Parameters
    ----------
    expData : dict
        <Short description of expData>
        **Default:** ``{'label': 'Experiment', 'x': [], 'y': []}``
        **Options:** ``<option>`` <description of option>

    minFreq : int
        <Short description of minFreq>
        **Default:** ``1``
        **Options:** ``<option>`` <description of option>

    maxFreq : int
        <Short description of maxFreq>
        **Default:** ``80``
        **Options:** ``<option>`` <description of option>

    stepFreq : int
        <Short description of stepFreq>
        **Default:** ``1``
        **Options:** ``<option>`` <description of option>

    norm : bool
        <Short description of norm>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    showFig : bool
        <Short description of showFig>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    kwargs : <type>
        <Short description of kwargs>
        **Default:** *required*

"""
    from .. import sim
    from bokeh.plotting import figure, show
    from bokeh.models import BasicTicker, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import layout

    if 'theme' in kwargs:
        if kwargs['theme'] != 'default':
            if kwargs['theme'] == 'gui':
                from bokeh.themes import Theme
                theme = Theme(json=_guiTheme)
            else:
                theme = kwargs['theme']
            curdoc().theme = theme

    # renormalize the dipole and save
    def baseline_renormalize():
        # N_pyr cells in grid. This is PER LAYER
        N_pyr = sim.cfg.hnn_params['N_pyr_x'] * sim.cfg.hnn_params['N_pyr_y']
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

    if not dpl:
        # baseline renormalize
        dpl = baseline_renormalize()

        # convert units from fAm to nAm, rescale and smooth
        for key in dpl.keys():
            dpl[key] *= 1e-6 * sim.cfg.hnn_params['dipole_scalefctr']

            if sim.cfg.hnn_params['dipole_smooth_win'] > 0:
                dpl[key] = hammfilt(dpl[key], sim.cfg.hnn_params['dipole_smooth_win']/sim.cfg.dt)

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
def iplotDipolePSD(expData={'label': 'Experiment', 'x':[], 'y':[]}, minFreq = 1, maxFreq = 80, stepFreq = 1, norm = True, showFig=False, **kwargs):
    """
    Function for/to <short description of `netpyne.analysis.interactive.iplotDipolePSD`>

    Parameters
    ----------
    expData : dict
        <Short description of expData>
        **Default:** ``{'label': 'Experiment', 'x': [], 'y': []}``
        **Options:** ``<option>`` <description of option>

    minFreq : int
        <Short description of minFreq>
        **Default:** ``1``
        **Options:** ``<option>`` <description of option>

    maxFreq : int
        <Short description of maxFreq>
        **Default:** ``80``
        **Options:** ``<option>`` <description of option>

    stepFreq : int
        <Short description of stepFreq>
        **Default:** ``1``
        **Options:** ``<option>`` <description of option>

    norm : bool
        <Short description of norm>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    showFig : bool
        <Short description of showFig>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    kwargs : <type>
        <Short description of kwargs>
        **Default:** *required*

"""

    from .. import sim
    from bokeh.plotting import figure, show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import layout

    if 'theme' in kwargs:
        if kwargs['theme'] != 'default':
            if kwargs['theme'] == 'gui':
                from bokeh.themes import Theme
                theme = Theme(json=_guiTheme)
            else:
                theme = kwargs['theme']
            curdoc().theme = theme

    # renormalize the dipole and save
    def baseline_renormalize():
        # N_pyr cells in grid. This is PER LAYER
        N_pyr = sim.cfg.hnn_params['N_pyr_x'] * sim.cfg.hnn_params['N_pyr_y']
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
        dpl[key] *= 1e-6 * sim.cfg.hnn_params['dipole_scalefctr']

        if sim.cfg.hnn_params['dipole_smooth_win'] > 0:
            dpl[key] = hammfilt(dpl[key], sim.cfg.hnn_params['dipole_smooth_win']/sim.cfg.dt)

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
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotSpikeHist(include = ['allCells', 'eachPop'], legendLabels = [], timeRange = None, binSize = 5, overlay=True, yaxis = 'rate', popColors=[], norm=False, smooth=None, filtFreq=False, filtOrder=3, saveData = None, saveFig = None, showFig = False, **kwargs):
    """
    Function for/to <short description of `netpyne.analysis.interactive.iplotSpikeHist`>

    Parameters
    ----------
    include : list
        <Short description of include>
        **Default:** ``['allCells', 'eachPop']``
        **Options:** ``<option>`` <description of option>

    legendLabels : list
        <Short description of legendLabels>
        **Default:** ``[]``
        **Options:** ``<option>`` <description of option>

    timeRange : <``None``?>
        <Short description of timeRange>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    binSize : int
        <Short description of binSize>
        **Default:** ``5``
        **Options:** ``<option>`` <description of option>

    overlay : bool
        <Short description of overlay>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    yaxis : str
        <Short description of yaxis>
        **Default:** ``'rate'``
        **Options:** ``<option>`` <description of option>

    popColors : list
        <Short description of popColors>
        **Default:** ``[]``
        **Options:** ``<option>`` <description of option>

    norm : bool
        <Short description of norm>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    smooth : <``None``?>
        <Short description of smooth>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    filtFreq : bool
        <Short description of filtFreq>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    filtOrder : int
        <Short description of filtOrder>
        **Default:** ``3``
        **Options:** ``<option>`` <description of option>

    saveData : <``None``?>
        <Short description of saveData>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    saveFig : <``None``?>
        <Short description of saveFig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    showFig : bool
        <Short description of showFig>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    kwargs : <type>
        <Short description of kwargs>
        **Default:** *required*

"""

    from .. import sim
    from bokeh.plotting import figure, show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import gridplot
    from bokeh.models import Legend
    from bokeh.colors import RGB

    print('Plotting interactive spike histogram...')

    theme = None
    if 'theme' in kwargs:
        if kwargs['theme'] != 'default':
            if kwargs['theme'] == 'gui':
                from bokeh.themes import Theme
                theme = Theme(json=_guiTheme)
            else:
                theme = kwargs['theme']
            curdoc().theme = theme

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

    if not 'palette' in kwargs:
        colors = [RGB(*[round(f * 255) for f in color]) for color in colorList] # bokeh only handles integer rgb values from 0-255
    else:
        colors = kwargs['palette']

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
        figs.append(figure(title="Spike Histogram", tools=TOOLS, x_axis_label="Time (ms)", y_axis_label=yaxisLabel, toolbar_location='above'))
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
    html = file_html(plot_layout, CDN, title="Spike Histogram", theme=theme)

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
def iplotRatePSD(include=['allCells', 'eachPop'], timeRange=None, binSize=5, maxFreq=100, NFFT=256, noverlap=128, smooth=0, overlay=True, ylim=None, popColors={}, saveData=None, saveFig=None, showFig=False, **kwargs):
    """
    Function for/to <short description of `netpyne.analysis.interactive.iplotRatePSD`>

    Parameters
    ----------
    include : list
        <Short description of include>
        **Default:** ``['allCells', 'eachPop']``
        **Options:** ``<option>`` <description of option>

    timeRange : <``None``?>
        <Short description of timeRange>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    binSize : int
        <Short description of binSize>
        **Default:** ``5``
        **Options:** ``<option>`` <description of option>

    maxFreq : int
        <Short description of maxFreq>
        **Default:** ``100``
        **Options:** ``<option>`` <description of option>

    NFFT : int
        <Short description of NFFT>
        **Default:** ``256``
        **Options:** ``<option>`` <description of option>

    noverlap : int
        <Short description of noverlap>
        **Default:** ``128``
        **Options:** ``<option>`` <description of option>

    smooth : int
        <Short description of smooth>
        **Default:** ``0``
        **Options:** ``<option>`` <description of option>

    overlay : bool
        <Short description of overlay>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    ylim : <``None``?>
        <Short description of ylim>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    popColors : dict
        <Short description of popColors>
        **Default:** ``{}``
        **Options:** ``<option>`` <description of option>

    saveData : <``None``?>
        <Short description of saveData>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    saveFig : <``None``?>
        <Short description of saveFig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    showFig : bool
        <Short description of showFig>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    kwargs : <type>
        <Short description of kwargs>
        **Default:** *required*

"""

    from .. import sim
    from bokeh.plotting import figure, show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import layout
    from bokeh.colors import RGB
    from bokeh.models import Legend

    print('Plotting interactive firing rate power spectral density (PSD) ...')

    theme = None
    if 'theme' in kwargs:
        if kwargs['theme'] != 'default':
            if kwargs['theme'] == 'gui':
                from bokeh.themes import Theme
                theme = Theme(json=_guiTheme)
            else:
                theme = kwargs['theme']
            curdoc().theme = theme

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

    if not 'palette' in kwargs:
        colors = [RGB(*[round(f * 255) for f in color]) for color in colorList] # bokeh only handles integer rgb values from 0-255
    else:
        colors = kwargs['palette']

    popColorDict = popColors.copy()
    if popColorDict:
        for pop, color in popColorDict.items():
            popColorDict[pop] = RGB(*[round(f * 255) for f in color])

    # Replace 'eachPop' with list of pops
    if 'eachPop' in include:
        include.remove('eachPop')
        for pop in sim.net.allPops: include.append(pop)

    # time range
    if timeRange is None:
        timeRange = [0, sim.cfg.duration]

    histData = []

    allPower, allSignal, allFreqs = [], [], []
    legendItems = []

    figs = []
    if overlay:
        figs.append(figure(title="PSD Rate Plot", tools=TOOLS, x_axis_label="Frequency (Hz)", y_axis_label="Power Spectral Density (db/Hz)", toolbar_location='above'))
        fig = figs[0]
        legendItems = []

    # Plot separate line for each entry in include
    for iplot, subset in enumerate(include):
        if not overlay:
            figs.append(figure(title=str(subset), tools=TOOLS, x_axis_label="Frequency (HZ)", y_axis_label="Power Spectral Density (db/Hz)"))
            fig = figs[iplot]

        cells, cellGids, netStimLabels = getCellsInclude([subset])

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

    plot_layout = layout(figs, sizing_mode='stretch_both')

    html = file_html(plot_layout, CDN, title="PSD Rate Plot", theme=theme)

    if showFig: show(plot_layout)

    if saveFig:
        if isinstance(saveFig, str):
            filename = saveFig
        else:
            filename = sim.cfg.filename + '_ipsd.html'
        file = open(filename, 'w')
        file.write(html)
        file.close()

    return html

# -------------------------------------------------------------------------------------------------------------------
## Plot interactive Traces
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotTraces(include=None, timeRange=None, overlay=False, oneFigPer='cell', rerun=False, colors=None, ylim=None, axis='on', fontSize=12, figSize=(10,8), saveData=None, saveFig=None, showFig=True, ylabel=None, linkAxes=False, **kwargs):
    """
    Function for/to <short description of `netpyne.analysis.interactive.iplotTraces`>

    Parameters
    ----------
    include : <``None``?>
        <Short description of include>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    timeRange : <``None``?>
        <Short description of timeRange>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    overlay : bool
        <Short description of overlay>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    oneFigPer : str
        <Short description of oneFigPer>
        **Default:** ``'cell'``
        **Options:** ``<option>`` <description of option>

    rerun : bool
        <Short description of rerun>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    colors : <``None``?>
        <Short description of colors>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    ylim : <``None``?>
        <Short description of ylim>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    axis : str
        <Short description of axis>
        **Default:** ``'on'``
        **Options:** ``<option>`` <description of option>

    fontSize : int
        <Short description of fontSize>
        **Default:** ``12``
        **Options:** ``<option>`` <description of option>

    figSize : tuple
        <Short description of figSize>
        **Default:** ``(10, 8)``
        **Options:** ``<option>`` <description of option>

    saveData : <``None``?>
        <Short description of saveData>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    saveFig : <``None``?>
        <Short description of saveFig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    showFig : bool
        <Short description of showFig>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    ylabel : <``None``?>
        <Short description of ylabel>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    linkAxes : bool
        <Short description of linkAxes>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    kwargs : <type>
        <Short description of kwargs>
        **Default:** *required*

"""

    from .. import sim
    from bokeh.plotting import figure, show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import layout, column
    from bokeh.models import HoverTool
    from bokeh.models import Legend
    from bokeh.colors import RGB

    print('Plotting interactive recorded cell traces per', oneFigPer)

    theme = None
    if 'theme' in kwargs:
        if kwargs['theme'] != 'default':
            if kwargs['theme'] == 'gui':
                from bokeh.themes import Theme
                theme = Theme(json=_guiTheme)
            else:
                theme = kwargs['theme']
            curdoc().theme = theme

    TOOLS = 'save,pan,box_zoom,reset,wheel_zoom'

    if not 'palette' in kwargs:
        colors = [RGB(*[round(f * 255) for f in color]) for color in colorList] # bokeh only handles integer rgb values from 0-255
    else:
        colors = kwargs['palette']

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
                                                  active_drag = None,
                                                  active_scroll = None,
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
                                        active_drag = None,
                                        active_scroll = None,
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
                                                  active_drag = None,
                                                  active_scroll = None,
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
                                        active_drag = None,
                                        active_scroll = None,
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
            html = file_html(plot_layout, CDN, title=figLabel, theme=theme)
            overlay_text = '_overlay'
        else:
            plot_layout = column(*figObj, sizing_mode='stretch_both')
            html = file_html(plot_layout, CDN, title=figLabel, theme=theme)
            overlay_text = ''

        if showFig: show(plot_layout)

        if saveFig:
            if isinstance(saveFig, str):
                filename = saveFig
            else:
                filename = sim.cfg.filename + '_itraces' + figLabel + overlay_text + '.html'
            file = open(filename, 'w')
            file.write(html)
            file.close()

    return html


# -------------------------------------------------------------------------------------------------------------------
## Plot interactive LFP
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotLFP(electrodes=['avg', 'all'], plots=['timeSeries', 'PSD', 'spectrogram'], timeRange=None, NFFT=256, noverlap=128, nperseg=256, minFreq=1, maxFreq=100, stepFreq=1, smooth=0, separation=1.0, includeAxon=True, logx=False, logy=False, normSignal=False, normPSD=False, normSpec=False, overlay=False, filtFreq=False, filtOrder=3, detrend=False, transformMethod='morlet', colors=None, saveData=None, saveFig=None, showFig=False, **kwargs):
    """
    Function for/to <short description of `netpyne.analysis.interactive.iplotLFP`>

    Parameters
    ----------
    electrodes : list
        <Short description of electrodes>
        **Default:** ``['avg', 'all']``
        **Options:** ``<option>`` <description of option>

    plots : list
        <Short description of plots>
        **Default:** ``['timeSeries', 'PSD', 'spectrogram']``
        **Options:** ``<option>`` <description of option>

    timeRange : <``None``?>
        <Short description of timeRange>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    NFFT : int
        <Short description of NFFT>
        **Default:** ``256``
        **Options:** ``<option>`` <description of option>

    noverlap : int
        <Short description of noverlap>
        **Default:** ``128``
        **Options:** ``<option>`` <description of option>

    nperseg : int
        <Short description of nperseg>
        **Default:** ``256``
        **Options:** ``<option>`` <description of option>

    minFreq : int
        <Short description of minFreq>
        **Default:** ``1``
        **Options:** ``<option>`` <description of option>

    maxFreq : int
        <Short description of maxFreq>
        **Default:** ``100``
        **Options:** ``<option>`` <description of option>

    stepFreq : int
        <Short description of stepFreq>
        **Default:** ``1``
        **Options:** ``<option>`` <description of option>

    smooth : int
        <Short description of smooth>
        **Default:** ``0``
        **Options:** ``<option>`` <description of option>

    separation : float
        <Short description of separation>
        **Default:** ``1.0``
        **Options:** ``<option>`` <description of option>

    includeAxon : bool
        <Short description of includeAxon>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    logx : bool
        <Short description of logx>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    logy : bool
        <Short description of logy>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    normSignal : bool
        <Short description of normSignal>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    normPSD : bool
        <Short description of normPSD>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    normSpec : bool
        <Short description of normSpec>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    overlay : bool
        <Short description of overlay>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    filtFreq : bool
        <Short description of filtFreq>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    filtOrder : int
        <Short description of filtOrder>
        **Default:** ``3``
        **Options:** ``<option>`` <description of option>

    detrend : bool
        <Short description of detrend>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    transformMethod : str
        <Short description of transformMethod>
        **Default:** ``'morlet'``
        **Options:** ``<option>`` <description of option>

    colors : <``None``?>
        <Short description of colors>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    saveData : <``None``?>
        <Short description of saveData>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    saveFig : <``None``?>
        <Short description of saveFig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    showFig : bool
        <Short description of showFig>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    kwargs : <type>
        <Short description of kwargs>
        **Default:** *required*


    """



    from .. import sim
    from bokeh.plotting import figure, show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import layout, column, row
    from bokeh.colors import RGB

    print('Plotting interactive LFP ...')

    html = None
    theme = None
    if 'theme' in kwargs:
        if kwargs['theme'] != 'default':
            if kwargs['theme'] == 'gui':
                from bokeh.themes import Theme
                theme = Theme(json=_guiTheme)
            else:
                theme = kwargs['theme']
            curdoc().theme = theme

    if not 'palette' in kwargs:
        colors = [RGB(*[round(f * 255) for f in color]) for color in colorList]
    else:
        colors = kwargs['palette']

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

    if timeRange is None:
        timeRange = [0,sim.cfg.duration]

    lfp = np.array(sim.allSimData['LFP'])[int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep),:]

    # electrode selection
    if 'all' in electrodes:
        electrodes.remove('all')
        electrodes.extend(list(range(int(sim.net.recXElectrode.nsites))))

    figs = {}
    data = {'lfp': lfp}

    # time series plot
    # TODO add scalebar
    if 'timeSeries' in plots:
        figs['timeSeries'] = figure(
            title="LFP Time Series Plot",
            tools=TOOLS,
            active_drag = None,
            active_scroll = None,
            x_axis_label="Time (ms)",
            y_axis_label="LFP electrode",
            toolbar_location="above")
        figs['timeSeries'].yaxis.major_tick_line_color = None
        figs['timeSeries'].yaxis.minor_tick_line_color = None
        figs['timeSeries'].yaxis.major_label_text_font_size = '0pt'
        figs['timeSeries'].yaxis.axis_line_color = None
        figs['timeSeries'].ygrid.visible = False

        hover = HoverTool(tooltips=[('Time', '@x'), ('Value', '@y')], mode='vline')
        figs['timeSeries'].add_tools(hover)
        figs['timeSeries'].legend.click_policy="hide"

        ydisp = np.absolute(lfp).max() * separation
        offset = 1.0*ydisp
        t = np.arange(timeRange[0], timeRange[1], sim.cfg.recordStep)

        avg_color = 'black'
        if 'theme' in kwargs:
            if kwargs['theme'] == 'gui' or 'dark' in kwargs['theme']:
                avg_color = 'white'

        for i,elec in enumerate(electrodes[::-1]):
            if elec == 'avg':
                dplSum = np.mean(lfp, axis=1)
                color = avg_color
            elif isinstance(elec, Number) and elec <= sim.net.recXElectrode.nsites:
                pass
                lfpPlot = lfp[:, elec]
                color = colors[i%len(colors)]

            legend=str(elec)
            figs['timeSeries'].line(t, lfpPlot+(i*ydisp), color=color, name=str(elec), legend=legend)

        data['lfpPlot'] = lfpPlot
        data['ydisp'] =  ydisp
        data['t'] = t

        figs['timeSeries'].legend.location = "top_right"
        figs['timeSeries'].legend.click_policy = "hide"

        plot_layout = layout(figs['timeSeries'], sizing_mode='stretch_both')
        html = file_html(plot_layout, CDN, title="Time Series LFP Plot", theme=theme)

        if showFig: show(plot_layout)

        if saveFig:
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename + '_iLFP_timeseries.html'
            file = open(filename, 'w')
            file.write(html)
            file.close()

    # PSD ----------------------------------
    if 'PSD' in plots:

        figs['psd'] = []
        allFreqs = []
        allSignal = []
        data['allFreqs'] = allFreqs
        data['allSignal'] = allSignal

        avg_color = 'black'
        if 'theme' in kwargs:
            if kwargs['theme'] == 'gui' or 'dark' in kwargs['theme']:
                avg_color = 'white'

        for i,elec in enumerate(electrodes):
            p = figure(title="Electrode {}".format(str(elec)),
                tools=TOOLS,
                active_drag = None,
                active_scroll = None,
                x_axis_label="Frequency (Hz)",
                y_axis_label="db/Hz",
                toolbar_location="above")

            hover = HoverTool(tooltips=[('Frequency', '@x'), ('Power', '@y')], mode='vline')
            p.add_tools(hover)
            p.legend.click_policy="hide"

            if elec == 'avg':
                lfpPlot = np.mean(lfp, axis=1)
                color = avg_color
            elif isinstance(elec, Number) and elec <= sim.net.recXElectrode.nsites:
                lfpPlot = lfp[:, elec]
                color = colors[i%len(colors)]

            # Morlet wavelet transform method
            if transformMethod == 'morlet':
                from ..support.morlet import MorletSpec, index2ms

                Fs = int(1000.0/sim.cfg.recordStep)
                morletSpec = MorletSpec(lfpPlot, Fs, freqmin=minFreq, freqmax=maxFreq, freqstep=stepFreq)
                freqs = F = morletSpec.f
                spec = morletSpec.TFR
                signal = np.mean(spec, 1)
                ylabel = 'Power'

            # FFT transform method
            elif transformMethod == 'fft':

                Fs = int(1000.0/sim.cfg.recordStep)
                power = mlab.psd(lfpPlot, Fs=Fs, NFFT=NFFT, detrend=mlab.detrend_none, window=mlab.window_hanning, noverlap=noverlap, pad_to=None, sides='default', scale_by_freq=None)

                if smooth:
                    signal = _smooth1d(10*np.log10(power[0]), smooth)
                else:
                    signal = 10*np.log10(power[0])
                freqs = power[1]
                ylabel = 'Power (dB/Hz)'

            allFreqs.append(freqs)
            allSignal.append(signal)

            p.line(freqs[freqs<maxFreq], signal[freqs<maxFreq], color=color, line_width=3)
            figs['psd'].append(p)

        plot_layout = column(figs['psd'], sizing_mode='stretch_both')
        html = file_html(plot_layout, CDN, title="LFP Power Spectral Density", theme=theme)

        if showFig: show(plot_layout)

        if saveFig:
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename+'_iLFP_psd.html'
            file = open(filename, 'w')
            file.write(html)
            file.close()

    # Spectrogram ------------------------------
    if 'spectrogram' in plots:
        import matplotlib.cm as cm
        from bokeh.transform import linear_cmap
        from bokeh.models import ColorBar
        from scipy import signal as spsig

        figs['spectro'] = []
        logx_spec = []

        # Morlet wavelet transform method
        if transformMethod == 'morlet':
            from ..support.morlet import MorletSpec, index2ms

            spec = []

            for i,elec in enumerate(electrodes):
                if elec == 'avg':
                    lfpPlot = np.mean(lfp, axis=1)
                elif isinstance(elec, Number) and elec <= sim.net.recXElectrode.nsites:
                    lfpPlot = lfp[:, elec]
                fs = int(1000.0/sim.cfg.recordStep)
                t_spec = np.linspace(0, index2ms(len(lfpPlot), fs), len(lfpPlot))
                spec.append(MorletSpec(lfpPlot, fs, freqmin=minFreq, freqmax=maxFreq, freqstep=stepFreq))

            f = np.array(range(minFreq, maxFreq+1, stepFreq))
            x_mesh, y_mesh = np.meshgrid(t_spec*1000.0, f[f<maxFreq])
            vmin = np.array([s.TFR for s in spec]).min()
            vmax = np.array([s.TFR for s in spec]).max()

            for i,elec in enumerate(electrodes):

                T = timeRange
                F = spec[i].f
                if normSpec:
                    spec[i].TFR = spec[i].TFR / vmax
                    S = spec[i].TFR
                    vc = [0, 1]
                else:
                    S = spec[i].TFR
                    vc = [vmin, vmax]

                p = figure(
                    title="Electrode {}".format(str(elec)),
                    tools=TOOLS,
                    active_drag = None,
                    active_scroll = None,
                    x_range=(0, timeRange[1]),
                    y_range=(0, maxFreq),
                    x_axis_label = "Time (ms)",
                    y_axis_label = "Frequency(Hz)",
                    toolbar_location="above",
                    #tooltips = [("Time", "$x"), ("Frequency", "$y"), ("Power", "@image")],
                    )

                mapper = linear_cmap(field_name='dB/Hz', palette=Viridis256, low=vmin, high=vmax)
                color_bar = ColorBar(color_mapper=mapper['transform'], location=(0,0), label_standoff=15, title='Power')

                p.image(image=[x_mesh, y_mesh, S], x=0, y=0, color_mapper=mapper['transform'], dw=timeRange[1], dh=100)
                p.add_layout(color_bar, 'right')
                figs['spectro'].append(p)

        # FFT transform method
        elif transformMethod == 'fft':

            for i,elec in enumerate(electrodes):
                if elec == 'avg':
                    lfpPlot = np.mean(lfp, axis=1)
                elif isinstance(elec, Number) and elec <= sim.net.recXElectrode.nsites:
                    lfpPlot = lfp[:, elec]
                # creates spectrogram over a range of data
                # from: http://joelyancey.com/lfp-python-practice/
                fs = int(1000.0/sim.cfg.recordStep)
                f, t_spec, x_spec = spsig.spectrogram(lfpPlot, fs=fs, window='hanning', detrend=mlab.detrend_none, nperseg=nperseg, noverlap=noverlap, nfft=NFFT,  mode='psd')
                x_mesh, y_mesh = np.meshgrid(t_spec*1000.0, f[f<maxFreq])
                logx_spec.append(10*np.log10(x_spec[f<maxFreq]))

            vmin = np.array(logx_spec).min()
            vmax = np.array(logx_spec).max()

            for i,elec in enumerate(electrodes):
                p = figure(
                    title="Electrode {}".format(str(elec)),
                    tools=TOOLS,
                    active_drag = None,
                    active_scroll = None,
                    x_range=(0, timeRange[1]),
                    y_range=(0, maxFreq),
                    x_axis_label = "Time (ms)",
                    y_axis_label = "Frequency(Hz)")
                mapper = linear_cmap(field_name='dB/Hz', palette=Viridis256, low=vmin, high=vmax)
                color_bar = ColorBar(color_mapper=mapper['transform'], width=8, location=(0,0), label_standoff=7, major_tick_line_color=None)
                p.image(image=[x_mesh, y_mesh, logx_spec[i]], x=0, y=0, color_mapper=mapper['transform'], dw=timeRange[1], dh=100)
                p.add_layout(color_bar, 'right')
                figs['spectro'].append(p)

        plot_layout = column(figs['spectro'], sizing_mode='stretch_both')
        html = file_html(plot_layout, CDN, title="LFP Power Spectral Density", theme=theme)

        if showFig: show(plot_layout)

        if saveFig:
            if isinstance(saveFig, str):
                filename = saveFig
            else:
                filename = sim.cfg.filename + '_iLFP_timefreq.html'
            file = open(filename, 'w')
            file.write(html)
            file.close()

    return html

# -------------------------------------------------------------------------------------------------------------------
## Plot interactive connectivity
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotConn(includePre=['all'], includePost=['all'], feature='strength', orderBy='gid', figSize=(10,10), groupBy='pop', groupByIntervalPre=None, groupByIntervalPost=None, removeWeightNorm=False, graphType='matrix', synOrConn='syn', synMech=None, connsFile=None, tagsFile=None, clim=None, fontSize=12, saveData=None, saveFig=None, showFig=False, **kwargs):
    """
    Function for/to <short description of `netpyne.analysis.interactive.iplotConn`>

    Parameters
    ----------
    includePre : list
        <Short description of includePre>
        **Default:** ``['all']``
        **Options:** ``<option>`` <description of option>

    includePost : list
        <Short description of includePost>
        **Default:** ``['all']``
        **Options:** ``<option>`` <description of option>

    feature : str
        <Short description of feature>
        **Default:** ``'strength'``
        **Options:** ``<option>`` <description of option>

    orderBy : str
        <Short description of orderBy>
        **Default:** ``'gid'``
        **Options:** ``<option>`` <description of option>

    figSize : tuple
        <Short description of figSize>
        **Default:** ``(10, 10)``
        **Options:** ``<option>`` <description of option>

    groupBy : str
        <Short description of groupBy>
        **Default:** ``'pop'``
        **Options:** ``<option>`` <description of option>

    groupByIntervalPre : <``None``?>
        <Short description of groupByIntervalPre>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    groupByIntervalPost : <``None``?>
        <Short description of groupByIntervalPost>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    removeWeightNorm : bool
        <Short description of removeWeightNorm>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    graphType : str
        <Short description of graphType>
        **Default:** ``'matrix'``
        **Options:** ``<option>`` <description of option>

    synOrConn : str
        <Short description of synOrConn>
        **Default:** ``'syn'``
        **Options:** ``<option>`` <description of option>

    synMech : <``None``?>
        <Short description of synMech>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    connsFile : <``None``?>
        <Short description of connsFile>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    tagsFile : <``None``?>
        <Short description of tagsFile>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    clim : <``None``?>
        <Short description of clim>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    fontSize : int
        <Short description of fontSize>
        **Default:** ``12``
        **Options:** ``<option>`` <description of option>

    saveData : <``None``?>
        <Short description of saveData>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    saveFig : <``None``?>
        <Short description of saveFig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    showFig : bool
        <Short description of showFig>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    kwargs : <type>
        <Short description of kwargs>
        **Default:** *required*

"""

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

    theme = None
    if 'theme' in kwargs:
        if kwargs['theme'] != 'default':
            if kwargs['theme'] == 'gui':
                from bokeh.themes import Theme
                theme = Theme(json=_guiTheme)
            else:
                theme = kwargs['theme']
            curdoc().theme = theme

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
            active_drag = None,
            active_scroll = None,
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
            #colors = [RGB(*[round(f * 255) for f in color]) for color in colorList] # bokeh only handles integer rgb values from 0-255
            colors = colorList
            bar_colors = colors[0:len(popsPre)]

            data = {'post' : popsPost}
            for popIndex, pop in enumerate(popsPre):
                data[pop] = connMatrix[popIndex, :]

            fig = figure(
                x_range=popsPost,
                title='Connection ' + feature + ' stacked bar graph',
                toolbar_location=None,
                tools='hover,save,pan,box_zoom,reset,wheel_zoom',
                active_drag= None,
                active_scroll = None,
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
    html = file_html(plot_layout, CDN, title='Connection ' + feature + ' matrix', theme=theme)

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
            filename = sim.cfg.filename+'_iconn_' + groupBy + '_' + feature + '_' + graphType + '_' + orderBy + '.html'
        file = open(filename, 'w')
        file.write(html)
        file.close()

    # show fig
    if showFig: show(fig)

    return html


# -------------------------------------------------------------------------------------------------------------------
## Plot 2D representation of network cell positions and connections
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplot2Dnet(include=['allCells'], view='xy', showConns=True, popColors=None, tagsFile=None, figSize=(12,12), fontSize=12, saveData=None, saveFig=None, showFig=True, **kwargs):
    """
    Function for/to <short description of `netpyne.analysis.interactive.iplot2Dnet`>

    Parameters
    ----------
    include : list
        List of presynaptic cells to include.
        **Default:** ``['allCells']``
        **Options:**
        ``['all']`` plots all cells and stimulations,
        ``['allNetStims']`` plots just stimulations,
        ``['popName1']`` plots a single population,
        ``['popName1', 'popName2']`` plots multiple populations,
        ``[120]`` plots a single cell,
        ``[120, 130]`` plots multiple cells,
        ``[('popName1', 56)]`` plots a cell from a specific population,
        ``[('popName1', [0, 1]), ('popName2', [4, 5, 6])]``, plots cells from multiple populations

    view : str
        Perspective of view.
        **Default:** ``'xy'`` front view,
        **Options:** ``'xz'`` top-down view

    showConns : bool
        Whether to show connections or not.
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    popColors : dict
        Dictionary with custom color (value) used for each population (key).
        **Default:** ``None`` uses standard colors
        **Options:** ``<option>`` <description of option>

    tagsFile : str
        Path to a saved tags file to use in connectivity plot.
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    figSize : list [width, height]
        Size of figure in inches.
        **Default:** ``(12, 12)``
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

    kwargs : <type>
        <Short description of kwargs>
        **Default:** *required*

    Returns
    -------


"""

    from .. import sim
    from bokeh.plotting import figure, show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import layout
    from bokeh.models import Legend
    from bokeh.colors import RGB
    from bokeh.models.annotations import Title

    print('Plotting interactive 2D representation of network cell locations and connections...')

    theme = None
    if 'theme' in kwargs:
        if kwargs['theme'] != 'default':
            if kwargs['theme'] == 'gui':
                from bokeh.themes import Theme
                theme = Theme(json=_guiTheme)
            else:
                theme = kwargs['theme']
            curdoc().theme = theme

    TOOLS = 'hover,save,pan,box_zoom,reset,wheel_zoom',

    if not 'palette' in kwargs:
        colors = [RGB(*[round(f * 255) for f in color]) for color in colorList] # bokeh only handles integer rgb values from 0-255
    else:
        colors = kwargs['palette']

    # front view
    if view == 'xy':
        ycoord = 'y'
    elif view == 'xz':
        ycoord = 'z'

    if tagsFile:
        print('Loading tags file...')
        import json
        with open(tagsFile, 'r') as fileObj: tagsTmp = json.load(fileObj)['tags']
        tagsFormat = tagsTmp.pop('format', [])
        tags = {int(k): v for k,v in tagsTmp.items()} # find method to load json with int keys?
        del tagsTmp

        # set indices of fields to read compact format (no keys)
        missing = []
        popIndex = tagsFormat.index('pop') if 'pop' in tagsFormat else missing.append('pop')
        xIndex = tagsFormat.index('x') if 'x' in tagsFormat else missing.append('x')
        yIndex = tagsFormat.index('y') if 'y' in tagsFormat else missing.append('y')
        zIndex = tagsFormat.index('z') if 'z' in tagsFormat else missing.append('z')
        if len(missing) > 0:
            print("Missing:")
            print(missing)
            return None, None, None

        # find pre and post cells
        if tags:
            cellGids = getCellsIncludeTags(include, tags, tagsFormat)
            popLabels = list(set([tags[gid][popIndex] for gid in cellGids]))

            # pop and cell colors
            popColorsTmp = {popLabel: colorList[ipop%len(colorList)] for ipop,popLabel in enumerate(popLabels)} # dict with color for each pop
            if popColors: popColorsTmp.update(popColors)
            popColors = popColorsTmp
            cellColors = [popColors[tags[gid][popIndex]] for gid in cellGids]

            # cell locations
            posX = [tags[gid][xIndex] for gid in cellGids]  # get all x positions
            if ycoord == 'y':
                posY = [tags[gid][yIndex] for gid in cellGids]  # get all y positions
            elif ycoord == 'z':
                posY = [tags[gid][zIndex] for gid in cellGids]  # get all y positions
        else:
            print('Error loading tags from file')
            return None

    else:
        cells, cellGids, _ = getCellsInclude(include)
        selectedPops = [cell['tags']['pop'] for cell in cells]
        popLabels = [pop for pop in sim.net.allPops if pop in selectedPops] # preserves original ordering

        # pop and cell colors
        popColorsTmp = {popLabel: colorList[ipop%len(colorList)] for ipop,popLabel in enumerate(popLabels)} # dict with color for each pop
        if popColors: popColorsTmp.update(popColors)
        popColors = popColorsTmp
        cellColors = ['#%02x%02x%02x' % tuple([int(col * 255) for col in popColors[cell['tags']['pop']]]) for cell in cells]


        # cell locations
        posX = [cell['tags']['x'] for cell in cells]  # get all x positions
        posY = [cell['tags'][ycoord] for cell in cells]  # get all y positions


    fig = figure(
        title="2D Network representation",
        tools=TOOLS,
        active_drag = None,
        active_scroll = None,
        tooltips=[('y location', '@y'), ('x location', '@x')],
        x_axis_label="x (um)",
        y_axis_label='y (um)',
        #x_range=[min(posX)-0.05*max(posX),1.05*max(posX)],
        #y_range=[1.05*max(posY), min(posY)-0.05*max(posY)],
        toolbar_location='above',
        match_aspect = True,
        #aspect_scale = 0.001,
        )

    if 'radius' in kwargs:
        radius = kwargs['radius']
    else:
        radius = 1.0

    fig.scatter(posX, posY, radius=radius, fill_color=cellColors, line_color=None)  # plot cell soma positions


    posXpre, posYpre = [], []
    posXpost, posYpost = [], []
    if showConns and not tagsFile:
        for postCell in cells:
            for con in postCell['conns']:  # plot connections between cells
                if not isinstance(con['preGid'], basestring) and con['preGid'] in cellGids:
                    posXpre,posYpre = next(((cell['tags']['x'],cell['tags'][ycoord]) for cell in cells if cell['gid']==con['preGid']), None)
                    posXpost, posYpost = postCell['tags']['x'], postCell['tags'][ycoord]
                    if kwargs.get('theme', '') == 'gui':
                        color = 'yellow'
                    else:
                        color='red'
                    if con['synMech'] in ['inh', 'GABA', 'GABAA', 'GABAB']:
                        if kwargs.get('theme', '') == 'gui':
                            color = 'lightcyan'
                        else:
                            color = 'blue'
                    width = 0.1 #50*con['weight']
                    fig.line([posXpre, posXpost], [posYpre, posYpost], color=color, line_width=width) # plot line from pre to post

    fontsiz = fontSize

    for popLabel in popLabels:
        #fig.line(0,0,color=tuple([int(x*255) for x in popColors[popLabel]]), legend_label=popLabel)
        fig.circle(0,0,color=tuple([int(x*255) for x in popColors[popLabel]]), legend_label=popLabel, line_width=0, radius=0)

    legend = Legend(location=(10,0))
    legend.click_policy='hide'
    fig.add_layout(legend, 'right')

    plot_layout = layout([fig], sizing_mode='stretch_both')
    html = file_html(plot_layout, CDN, title="2D Net Plot", theme=theme)

    # save figure data
    if saveData:
        figData = {'posX': posX, 'posY': posY, 'posX': cellColors, 'posXpre': posXpre, 'posXpost': posXpost, 'posYpre': posYpre, 'posYpost': posYpost,
         'include': include, 'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}

        _saveFigData(figData, saveData, '2Dnet')

    # save figure
    if saveFig:
        if isinstance(saveFig, str):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_i2Dnet_.html'
        file = open(filename, 'w')
        file.write(html)
        file.close()

    # show fig
    if showFig: show(fig)

    return html, {'include': include, 'posX': posX, 'posY': posY, 'posXpre': posXpre, 'posXpost': posXpost, 'posYpre': posYpre, 'posYpost': posYpost}



# -------------------------------------------------------------------------------------------------------------------
## Plot interactive RxD concentration
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotRxDConcentration(speciesLabel, regionLabel, plane='xy', saveFig=None, showFig=True, **kwargs):
    """
    Function for/to <short description of `netpyne.analysis.interactive.iplotRxDConcentration`>

    Parameters
    ----------
    speciesLabel : <type>
        <Short description of speciesLabel>
        **Default:** *required*

    regionLabel : <type>
        <Short description of regionLabel>
        **Default:** *required*

    plane : str
        <Short description of plane>
        **Default:** ``'xy'``
        **Options:** ``<option>`` <description of option>

    saveFig : <``None``?>
        <Short description of saveFig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    showFig : bool
        <Short description of showFig>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    kwargs : <type>
        <Short description of kwargs>
        **Default:** *required*


    """



    from .. import sim
    from bokeh.plotting import figure, show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import layout, column, row
    from bokeh.colors import RGB
    from bokeh.transform import linear_cmap
    from bokeh.models import ColorBar

    print('Plotting interactive RxD concentration ...')
    theme = None
    if 'theme' in kwargs:
        if kwargs['theme'] != 'default':
            if kwargs['theme'] == 'gui':
                from bokeh.themes import Theme
                theme = Theme(json=_guiTheme)
            else:
                theme = kwargs['theme']
            curdoc().theme = theme

    if not 'palette' in kwargs:
        from bokeh.palettes import Viridis256
        colors = Viridis256
        #colors = [RGB(*[round(f * 255) for f in color]) for color in colorList]
    else:
        colors = kwargs['palette']

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

    species = sim.net.rxd['species'][speciesLabel]['hObj']
    region = sim.net.rxd['regions'][regionLabel]['hObj']
    plane2mean = {'xz': 1, 'xy': 2}

    data = species[region].states3d[:].mean(plane2mean[plane]).T
    data = np.flipud(data) # This does not flip the axis values, should improve

    extent = []
    extent.append(sim.net.rxd['regions'][regionLabel][plane[0] + 'lo'])
    extent.append(sim.net.rxd['regions'][regionLabel][plane[0] + 'hi'])
    extent.append(sim.net.rxd['regions'][regionLabel][plane[1] + 'lo'])
    extent.append(sim.net.rxd['regions'][regionLabel][plane[1] + 'hi'])

    dw = extent[1] - extent[0]
    dh = extent[3] - extent[2]

    low = np.nanmin(data)
    high = np.nanmax(data)
    if low == high:
        low = low - 0.1 * low
        high = high + 0.1 * high

    conc_colormapper = linear_cmap(
        field_name = '[' + species.name + '] (mM)',
        palette = colors,
        low = low,
        high = high,
        nan_color = 'white',
        )

    conc_colorbar = ColorBar(
        color_mapper = conc_colormapper['transform'],
        label_standoff = 12,
        title_standoff = 12,
        )
    conc_colorbar.title = '[' + species.name + '] (mM)'

    fig = figure(
        title = 'RxD: ' + species.name + ' concentration',
        toolbar_location = 'above',
        tools = 'hover,save,pan,box_zoom,reset,wheel_zoom',
        active_drag = None,
        active_scroll = None,
        tooltips = [("x", "$x"), ("y", "$y"), ("value", "@image")],
        match_aspect = True,
        x_axis_label = plane[0] + " location (um)",
        y_axis_label = plane[1] + " location (um)",
        )

    fig.image(image=[data], x=extent[0], y=extent[2], dw=dw, dh=dh, color_mapper=conc_colormapper['transform'], level="image")
    fig.add_layout(conc_colorbar, 'right')

    plot_layout = layout([fig], sizing_mode='scale_height')
    html = file_html(plot_layout, CDN, title="RxD Concentration", theme=theme)

    if showFig:
        show(plot_layout)

    if saveFig:
        if isinstance(saveFig, str):
            filename = saveFig
        else:
            filename = sim.cfg.filename + '_RxD_concentration.html'
        outfile = open(filename, 'w')
        outfile.write(html)
        outfile.close()

    return html, data



# -------------------------------------------------------------------------------------------------------------------
## Plot interactive spike statistics
# -------------------------------------------------------------------------------------------------------------------
@exception
def iplotSpikeStats(include=['eachPop', 'allCells'], statDataIn={}, timeRange=None, graphType='boxplot', stats=['rate', 'isicv'], bins=50, histlogy=False, histlogx=False, histmin=0.0, density=False, includeRate0=False, legendLabels=None, normfit=False, histShading=True, xlim=None, popColors={}, saveData=None, saveFig=None, showFig=True, **kwargs):
    """
    Function for/to <short description of `netpyne.analysis.interactive.iplotSpikeStats`>

    Parameters
    ----------
    include : list
        <Short description of include>
        **Default:** ``['eachPop', 'allCells']``
        **Options:** ``<option>`` <description of option>

    statDataIn : dict
        <Short description of statDataIn>
        **Default:** ``{}``
        **Options:** ``<option>`` <description of option>

    timeRange : <``None``?>
        <Short description of timeRange>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    graphType : str
        <Short description of graphType>
        **Default:** ``'boxplot'``
        **Options:** ``<option>`` <description of option>

    stats : list
        <Short description of stats>
        **Default:** ``['rate', 'isicv']``
        **Options:** ``<option>`` <description of option>

    bins : int
        <Short description of bins>
        **Default:** ``50``
        **Options:** ``<option>`` <description of option>

    histlogy : bool
        <Short description of histlogy>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    histlogx : bool
        <Short description of histlogx>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    histmin : float
        <Short description of histmin>
        **Default:** ``0.0``
        **Options:** ``<option>`` <description of option>

    density : bool
        <Short description of density>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    includeRate0 : bool
        <Short description of includeRate0>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    legendLabels : <``None``?>
        <Short description of legendLabels>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    normfit : bool
        <Short description of normfit>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    histShading : bool
        <Short description of histShading>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    xlim : <``None``?>
        <Short description of xlim>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    popColors : dict
        <Short description of popColors>
        **Default:** ``{}``
        **Options:** ``<option>`` <description of option>

    saveData : <``None``?>
        <Short description of saveData>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    saveFig : <``None``?>
        <Short description of saveFig>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    showFig : bool
        <Short description of showFig>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    kwargs : <type>
        <Short description of kwargs>
        **Default:** *required*


    """



    from .. import sim
    from bokeh.plotting import figure, show
    from bokeh.resources import CDN
    from bokeh.embed import file_html
    from bokeh.layouts import layout, column, row
    from bokeh.colors import RGB
    from bokeh.transform import linear_cmap
    from bokeh.transform import factor_cmap
    from bokeh.models import ColorBar
    from bokeh.palettes import Spectral6
    from bokeh.models.mappers import CategoricalColorMapper

    print('Plotting interactive spike statistics ...')

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"

    xlabels = {'rate': 'Rate (Hz)', 'isicv': 'Irregularity (ISI CV)', 'sync':  'Synchrony', 'pairsync': 'Pairwise synchrony'}

    # Replace 'eachPop' with list of pops
    if 'eachPop' in include:
        include.remove('eachPop')
        for pop in sim.net.allPops: include.append(pop)

    # time range
    if timeRange is None:
        timeRange = [0, sim.cfg.duration]

    theme = None
    for stat in stats:

        if 'theme' in kwargs:
            if kwargs['theme'] != 'default':
                if kwargs['theme'] == 'gui':
                    from bokeh.themes import Theme
                    theme = Theme(json=_guiTheme)
                else:
                    theme = kwargs['theme']
                curdoc().theme = theme
            else:
                curdoc().theme = bokeh_theme
        else:
            curdoc().theme = bokeh_theme

        if not 'palette' in kwargs:
            colors = [RGB(*[round(f * 255) for f in color]) for color in colorList]
        else:
            colors = kwargs['palette']

        xlabel = xlabels[stat]
        statData = []
        gidsData = []
        ynormsData = []

        # Calculate data for each entry in include
        for iplot,subset in enumerate(include):

            if stat in statDataIn:
                statData = statDataIn[stat]['statData']
                gidsData = statDataIn[stat].get('gidsData', [])
                ynormsData = statDataIn[stat].get('ynormsData', [])

            else:
                cells, cellGids, netStimLabels = getCellsInclude([subset])
                numNetStims = 0

                # Select cells to include
                if len(cellGids) > 0:
                    try:
                        spkinds,spkts = list(zip(*[(spkgid,spkt) for spkgid,spkt in
                            zip(sim.allSimData['spkid'],sim.allSimData['spkt']) if spkgid in cellGids]))
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
                        for stimLabel,stimSpks in stims.items()
                            for spk in stimSpks if stimLabel == netStimLabel]
                        if len(netStimSpks) > 0:
                            lastInd = max(spkinds) if len(spkinds)>0 else 0
                            spktsNew = netStimSpks
                            spkindsNew = [lastInd+1+i for i in range(len(netStimSpks))]
                            spkts.extend(spktsNew)
                            spkinds.extend(spkindsNew)
                            numNetStims += 1
                try:
                    spkts,spkinds = list(zip(*[(spkt, spkind) for spkt, spkind in zip(spkts, spkinds)
                        if timeRange[0] <= spkt <= timeRange[1]]))
                except:
                    pass

                # rate stats
                if stat == 'rate':
                    toRate = 1e3/(timeRange[1]-timeRange[0])
                    if includeRate0:
                        rates = [spkinds.count(gid)*toRate for gid in cellGids] \
                            if len(spkinds)>0 else [0]*len(cellGids) #cellGids] #set(spkinds)]
                    else:
                        rates = [spkinds.count(gid)*toRate for gid in set(spkinds)] \
                            if len(spkinds)>0 else [0] #cellGids] #set(spkinds)]
                    statData.append(rates)

                # Inter-spike interval (ISI) coefficient of variation (CV) stats
                elif stat == 'isicv':
                    import numpy as np
                    spkmat = [[spkt for spkind,spkt in zip(spkinds,spkts) if spkind==gid]
                        for gid in set(spkinds)]
                    isimat = [[t - s for s, t in zip(spks, spks[1:])] for spks in spkmat if len(spks)>10]
                    isicv = [np.std(x) / np.mean(x) if len(x)>0 else 0 for x in isimat] # if len(x)>0]
                    statData.append(isicv)

                # synchrony
                elif stat in ['sync', 'pairsync']:
                    try:
                        import pyspike
                    except:
                        print("Error: plotSpikeStats() requires the PySpike python package \
                            to calculate synchrony (try: pip install pyspike)")
                        return 0

                    spkmat = [pyspike.SpikeTrain([spkt for spkind,spkt in zip(spkinds,spkts)
                        if spkind==gid], timeRange) for gid in set(spkinds)]
                    if stat == 'sync':
                        # (SPIKE-Sync measure)' # see http://www.scholarpedia.org/article/Measures_of_spike_train_synchrony
                        syncMat = [pyspike.spike_sync(spkmat)]
                        #graphType = 'bar'
                    elif stat == 'pairsync':
                        # (SPIKE-Sync measure)' # see http://www.scholarpedia.org/article/Measures_of_spike_train_synchrony
                        syncMat = np.mean(pyspike.spike_sync_matrix(spkmat), 0)

                    statData.append(syncMat)

        # boxplot
        if graphType == 'boxplot':

            line_width = 2
            line_color = 'black'
            if 'theme' in kwargs:
                if kwargs['theme'] is not None:
                    if kwargs['theme'] == 'gui' or 'dark' in kwargs['theme'] or kwargs['theme'] == 'contrast':
                        line_color = 'lightgray'

            labels = legendLabels if legendLabels else include
            data_lists = statData[::-1]
            data_lists.reverse()
            box_colors = colors[0:len(labels)]

            if include[0] == 'allCells':
                del box_colors[-1]
                box_colors.insert(0, ('darkslategray'))

            data = {}
            for label, data_list in zip(labels, data_lists):
                data[label] = data_list

            fig = figure(
                title = 'Spike statistics: ' + xlabels[stat],
                toolbar_location = 'above',
                tools = 'hover,save,pan,box_zoom,reset,wheel_zoom',
                active_drag = None,
                active_scroll = None,
                tooltips = [(stat, "$y")],
                x_axis_label = 'Population',
                y_axis_label = xlabel,
                x_range = labels
            )

            fig.xgrid.visible = False

            df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in data.items() ]))

            q1 = df.quantile(q=0.25)
            q2 = df.quantile(q=0.5)
            q3 = df.quantile(q=0.75)
            iqr = q3 - q1
            upper = q3 + 1.5 * iqr
            lower = q1 - 1.5 * iqr
            qmin = df.quantile(q=0.00)
            qmax = df.quantile(q=1.00)
            qmean = df.mean()

            out_highs = df[df > upper]
            out_lows  = df[df < lower]

            # outliers
            for index, label in enumerate(labels):
                out_x = []
                out_y = []
                out_high = out_highs[label].dropna()
                if not out_high.empty:
                    upper[label] = df[df < upper][label].max()
                    for val in out_high:
                        out_x.append(label)
                        out_y.append(val)
                else:
                    upper[label] = qmax[label]
                out_low = out_lows[label].dropna()
                if not out_low.empty:
                    lower[label] = df[df > lower][label].min()
                    for val in out_low:
                        out_x.append(label)
                        out_y.append(val)
                else:
                    lower[label] = qmin[label]
                if out_x:
                    fig.circle_x(out_x, out_y, size=10, fill_color=box_colors[index], fill_alpha=0.8, line_color=line_color)

            # stems
            fig.segment(labels, upper, labels, q3, line_color=line_color, line_width=line_width)
            fig.segment(labels, lower, labels, q1, line_color=line_color, line_width=line_width)

            # boxes
            fig.vbar(labels, 0.7, q2, q3, line_color=line_color, line_width=line_width, fill_color=box_colors)
            fig.vbar(labels, 0.7, q1, q2, line_color=line_color, line_width=line_width, fill_color=box_colors)

            # whiskers (almost-0 height rects simpler than segments)
            fig.rect(labels, lower, 20, 1, width_units='screen', height_units='screen', line_color=line_color, line_width=line_width)
            fig.rect(labels, upper, 20, 1, width_units='screen', height_units='screen', line_color=line_color, line_width=line_width)

            # means
            fig.circle_cross(labels, qmean, size=10, fill_color='white', fill_alpha=0.5, line_color='black')



        else:
            raise Exception('Only boxplot is currently supported in iplotSpikeStats.')

        plot_layout = layout([fig], sizing_mode='stretch_both')
        html = file_html(plot_layout, CDN, title="Spike Statistics", theme=theme)

        if showFig:
            show(plot_layout)

        if saveFig:
            if isinstance(saveFig, str):
                filename = saveFig
            else:
                filename = sim.cfg.filename + '_spike_' + stat + '.html'
            outfile = open(filename, 'w')
            outfile.write(html)
            outfile.close()

    return html
