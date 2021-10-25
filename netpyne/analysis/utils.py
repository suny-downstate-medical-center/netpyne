"""
Module for utilities to help analyze and plot results

"""

from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from builtins import round
from builtins import open
from builtins import range

# required to make json saving work in Python 2/3
try:
    to_unicode = unicode
except NameError:
    to_unicode = str
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
import functools
import sys
from netpyne.logger import logger

# -------------------------------------------------------------------------------------------------------------------
# Define list of colors
# -------------------------------------------------------------------------------------------------------------------
try:
    from bokeh.themes import built_in_themes
except:
    pass

colorListType = 'alternate'  # 'graded'

if colorListType == 'alternate':
    colorList = [[0.42,0.67,0.84], [0.90,0.76,0.00], [0.42,0.83,0.59], [0.90,0.32,0.00],
            [0.34,0.67,0.67], [0.90,0.59,0.00], [0.42,0.82,0.83], [1.00,0.85,0.00],
            [0.33,0.67,0.47], [1.00,0.38,0.60], [0.57,0.67,0.33], [0.5,0.2,0.0],
            [0.71,0.82,0.41], [0.0,0.2,0.5], [0.70,0.32,0.10]]*3
elif colorListType == 'graded' and __gui__:
    import matplotlib
    cmap = matplotlib.cm.get_cmap('jet')
    colorList = [cmap(x) for x in np.linspace(0,1,12)]

# -------------------------------------------------------------------------------------------------------------------
## Exception decorator
# -------------------------------------------------------------------------------------------------------------------
def exception(function):
    """
    Function for/to <short description of `netpyne.analysis.utils.exception`>

    Parameters
    ----------
    function : <type>
        <Short description of function>
        **Default:** *required*

"""
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            err = "There was an exception in %s():"%(function.__name__)
            logger.warning("  %s \n    %s \n    %s"%(err,e,sys.exc_info()))
            return -1

    return wrapper


# -------------------------------------------------------------------------------------------------------------------
## Round to n sig figures
# -------------------------------------------------------------------------------------------------------------------
def _roundFigures(x, n):
    return round(x, -int(np.floor(np.log10(abs(x)))) + (n - 1))

# -------------------------------------------------------------------------------------------------------------------
## show figure
# -------------------------------------------------------------------------------------------------------------------
def _showFigure():
    try:
        plt.show(block=False)
    except:
        plt.show()


# -------------------------------------------------------------------------------------------------------------------
## Save figure data
# -------------------------------------------------------------------------------------------------------------------
def _saveFigData(figData, fileName=None, type=''):
    from .. import sim

    if not fileName or not isinstance(fileName, basestring):
        fileName = sim.cfg.filename+'_'+type+'.pkl'

    if fileName.endswith('.pkl'): # save to pickle
        import pickle
        logger.info('Saving figure data as %s ... ' % fileName)
        with open(fileName, 'wb') as fileObj:
            pickle.dump(figData, fileObj)
    elif fileName.endswith('.json'):  # save to json
        logger.info('Saving figure data as %s ... ' % fileName)
        sim.saveJSON(fileName, figData)
    else:
        logger.warning('File extension to save figure data not recognized')


# -------------------------------------------------------------------------------------------------------------------
## Smooth 1d signal
# -------------------------------------------------------------------------------------------------------------------
def _smooth1d(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also:

    np.hanning, np.hamming, np.bartlett, np.blackman, np.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")


    s=np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]

    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    return y[int((window_len/2-1)):int(-(window_len/2))]


# -------------------------------------------------------------------------------------------------------------------
## Get subset of cells and netstims indicated by include list
# -------------------------------------------------------------------------------------------------------------------
def getCellsInclude(include, sim = None):
    """
    Function for/to <short description of `netpyne.analysis.utils.getCellsInclude`>

    Parameters
    ----------
    include : <type>
        <Short description of include>
        **Default:** *required*

    sim : <``None``?>
        <Short description of sim>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>


    """



    if not sim:
        from .. import sim

    allCells = sim.net.allCells
    allNetStimLabels = list(sim.net.params.stimSourceParams.keys())
    cellGids = []
    cells = []
    netStimLabels = []
    for condition in include:
        if condition == 'all':  # all cells + Netstims
            cellGids = [c['gid'] for c in allCells]
            cells = list(allCells)
            netStimLabels = list(allNetStimLabels)
            return cells, cellGids, netStimLabels

        elif condition == 'allCells':  # all cells
            cellGids = [c['gid'] for c in allCells]
            cells = list(allCells)

        elif condition == 'allNetStims':  # all cells + Netstims
            netStimLabels = list(allNetStimLabels)

        elif isinstance(condition, int):  # cell gid
            cellGids.append(condition)

        elif isinstance(condition, basestring):  # entire pop
            if condition in allNetStimLabels:
                netStimLabels.append(condition)
            else:
                cellGids.extend([c['gid'] for c in allCells if c['tags']['pop']==condition])

        # subset of a pop with relative indices
        # when load from json gets converted to list (added as exception)
        elif (isinstance(condition, (list,tuple))
        and len(condition)==2
        and isinstance(condition[0], basestring)
        and isinstance(condition[1], (list,int))):
            cellsPop = [c['gid'] for c in allCells if c['tags']['pop']==condition[0]]
            if isinstance(condition[1], list):
                cellGids.extend([gid for i,gid in enumerate(cellsPop) if i in condition[1]])
            elif isinstance(condition[1], int):
                cellGids.extend([gid for i,gid in enumerate(cellsPop) if i==condition[1]])

        elif isinstance(condition, (list,tuple)):  # subset
            for subcond in condition:
                if isinstance(subcond, int):  # cell gid
                    cellGids.append(subcond)

                elif isinstance(subcond, basestring):  # entire pop
                    if subcond in allNetStimLabels:
                        netStimLabels.append(subcond)
                    else:
                        cellGids.extend([c['gid'] for c in allCells if c['tags']['pop']==subcond])

    cellGids = sim.unique(cellGids)  # unique values
    cells = [cell for cell in allCells if cell['gid'] in cellGids]
    cells = sorted(cells, key=lambda k: k['gid'])

    return cells, cellGids, netStimLabels


# -------------------------------------------------------------------------------------------------------------------
## Get subset of cells and netstims indicated by include list
# -------------------------------------------------------------------------------------------------------------------
def getCellsIncludeTags(include, tags, tagsFormat=None):
    """
    Function for/to <short description of `netpyne.analysis.utils.getCellsIncludeTags`>

    Parameters
    ----------
    include : <type>
        <Short description of include>
        **Default:** *required*

    tags : <type>
        <Short description of tags>
        **Default:** *required*

    tagsFormat : <``None``?>
        <Short description of tagsFormat>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>


    """


    allCells = tags.copy()
    cellGids = []

    # using list with indices
    if tagsFormat or 'format' in allCells:
        if not tagsFormat: tagsFormat = allCells.pop('format')
        popIndex = tagsFormat.index('pop')

        for condition in include:
            if condition in  ['all', 'allCells']:  # all cells
                cellGids = list(allCells.keys())
                return cellGids

            elif isinstance(condition, int):  # cell gid
                cellGids.append(condition)

            elif isinstance(condition, basestring):  # entire pop
                cellGids.extend([gid for gid,c in allCells.items() if c[popIndex]==condition])

            elif isinstance(condition, tuple):  # subset of a pop with relative indices
                cellsPop = [gid for gid,c in allCells.items() if c[popIndex]==condition[0]]
                if isinstance(condition[1], list):
                    cellGids.extend([gid for i,gid in enumerate(cellsPop) if i in condition[1]])
                elif isinstance(condition[1], int):
                    cellGids.extend([gid for i,gid in enumerate(cellsPop) if i==condition[1]])

    # using dict with keys
    else:

        for condition in include:
            if condition in  ['all', 'allCells']:  # all cells
                cellGids = list(allCells.keys())
                return cellGids

            elif isinstance(condition, int):  # cell gid
                cellGids.append(condition)

            elif isinstance(condition, basestring):  # entire pop
                cellGids.extend([gid for gid,c in allCells.items() if c['pop']==condition])

            elif isinstance(condition, tuple):  # subset of a pop with relative indices
                cellsPop = [gid for gid,c in allCells.items() if c['pop']==condition[0]]
                if isinstance(condition[1], list):
                    cellGids.extend([gid for i,gid in enumerate(cellsPop) if i in condition[1]])
                elif isinstance(condition[1], int):
                    cellGids.extend([gid for i,gid in enumerate(cellsPop) if i==condition[1]])

    cellGids = [int(x) for x in set(cellGids)]  # unique values

    return cellGids


# -------------------------------------------------------------------------------------------------------------------
## Synchrony measure
# -------------------------------------------------------------------------------------------------------------------
def syncMeasure():
    """
    Function for/to <short description of `netpyne.analysis.utils.syncMeasure`>


    """


    from .. import sim

    t0=-1
    width=1
    cnt=0
    for spkt in sim.allSimData['spkt']:
        if (spkt>=t0+width):
            t0=spkt
            cnt+=1
    return 1-cnt/(sim.cfg.duration/width)


# -------------------------------------------------------------------------------------------------------------------
## Invert mapping of dict
# -------------------------------------------------------------------------------------------------------------------
def invertDictMapping(d):
    """
    Function for/to <short description of `netpyne.analysis.utils.invertDictMapping`>

    Parameters
    ----------
    d : <type>
        <Short description of d>
        **Default:** *required*

"""
    inv_map = {}
    for k, v in d.items():
        inv_map[v] = inv_map.get(v, [])
        inv_map[v].append(k)
    return inv_map


# -------------------------------------------------------------------------------------------------------------------
## Get subset of spkt, spkid based on a timeRange and cellGids list; ~10x speedup over list iterate
# -------------------------------------------------------------------------------------------------------------------
def getSpktSpkid(cellGids=[], timeRange=None, sim = None):
    """
    Function for/to <short description of `netpyne.analysis.utils.getSpktSpkid`>

    Parameters
    ----------
    cellGids : list
        <Short description of cellGids>
        **Default:** ``[]``
        **Options:** ``<option>`` <description of option>

    timeRange : <``None``?>
        <Short description of timeRange>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    sim : <``None``?>
        <Short description of sim>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

"""

    if not sim:
        from .. import sim

    import pandas as pd

    try: # Pandas 0.24 and later
        from pandas import _lib as pandaslib
    except: # Pandas 0.23 and earlier
        from pandas import lib as pandaslib
    df = pd.DataFrame(pandaslib.to_object_array([sim.allSimData['spkt'], sim.allSimData['spkid']]).transpose(), columns=['spkt', 'spkid'])
    #df = pd.DataFrame(pd.lib.to_object_array([sim.allSimData['spkt'], sim.allSimData['spkid']]).transpose(), columns=['spkt', 'spkid'])

    if timeRange:
        min, max = [int(df['spkt'].searchsorted(timeRange[i])) for i in range(2)] # binary search faster than query
    else: # timeRange None or empty list means all times
        min, max = 0, len(df)
    if len(cellGids)==0:
        sel = df[min:max]
    else:
        sel = df[min:max].query('spkid in @cellGids')
    return sel, sel['spkt'].tolist(), sel['spkid'].tolist() # will want to return sel as well for further sorting



def checkAvailablePlots(requireCfg=False):
    """
    Function to check which plots are available for the GUI 

    Returns
    ----------
        requireCfg : <Bool>
        <Whether a plot configuration in sim.cfg.analysis is required to return True for each plot>
        **Default:** False

    Returns
    ----------
    dict
        <Keys indicate the name of the analysis function and values whether they are available or not (Boolean)>

"""
    from .. import sim

    avail = {'plotConn': False,
             'plot2Dnet':  False,
             'plotTraces': False,
             'plotRaster': False,
             'plotSpikeHist': False,
             'plotSpikeStats': False,
             'plotLFP': False,
             'granger': False,
             'plotRxDConcentration': False}

    # plot conn
    if hasattr(sim, 'net') and hasattr(sim.net, 'allCells') and len(sim.net.allCells) > 0:
        avail['plotConn'] = True
        avail['plot2Dnet'] = True

    # plot traces
    traces = list(sim.cfg.recordTraces.keys())
    if len(traces)>0 and hasattr(sim, 'allSimData'):
        for trace in traces:
            if trace in sim.allSimData and len(sim.allSimData.get(trace)):
                avail['plotTraces'] = True
                break
    
    # raster, spike hist, spike stats, rate psd and granger 
    if hasattr(sim, 'allSimData') and 'spkid' in sim.allSimData and 'spkt' in sim.allSimData \
        and len(sim.allSimData['spkid']) > 0 and len(sim.allSimData['spkt']) > 0:

        avail['plotRaster'] = True
        avail['plotSpikeHist'] = True
        avail['plotSpikeStats'] = True
        avail['plotRatePSD'] = True
        avail['granger'] = True


    # plot lfp 
    if hasattr(sim, 'allSimData') and 'LFP' in sim.allSimData and len(sim.allSimData['LFP']) > 0:

        avail['plotLFP'] = True

    # rxd concentation 
    if hasattr(sim, 'net') and hasattr(sim.net, 'rxd') and 'species' in sim.net.rxd and 'regions' in sim.net.rxd \
        and len(sim.net.rxd['species']) > 0 and len(sim.net.rxd['regions']) > 0: 

        avail['plotRxDConcentration'] = True

    # require config of plots in sim.cfg.analysis
    if requireCfg:
        for k in avail:
            if k not in sim.cfg.analysis:
                avail[k] = False

    return avail



# -------------------------------------------------------------------------------------------------------------------
## Default NetPyNE Bokeh theme -- based on dark_minimal
# -------------------------------------------------------------------------------------------------------------------

# Note: The Bokeh plotting APIs defaults override some theme properties. Namely: fill_alpha,
# fill_color, line_alpha, line_color, text_alpha and text_color. Those properties should
# therefore be set explicitly when using the plotting API.

_guiTheme = {
    "attrs": {
        "Figure" : {
            "background_fill_color": "#434343", #"#20262B",
            "border_fill_color": "#434343", #"#15191C",
            "outline_line_color": "#E0E0E0",
            "outline_line_alpha": 0.25
        },

        "Grid": {
            "grid_line_color": "#E0E0E0",
            "grid_line_alpha": 0.25
        },

        "Axis": {
            "major_tick_line_alpha": 0,
            "major_tick_line_color": "#E0E0E0",

            "minor_tick_line_alpha": 0,
            "minor_tick_line_color": "#E0E0E0",

            "axis_line_alpha": 0,
            "axis_line_color": "#E0E0E0",

            "major_label_text_color": "#E0E0E0",
            "major_label_text_font": "Helvetica",
            "major_label_text_font_size": "1.025em",

            "axis_label_standoff": 10,
            "axis_label_text_color": "#E0E0E0",
            "axis_label_text_font": "Helvetica",
            "axis_label_text_font_size": "1.25em",
            "axis_label_text_font_style": "normal"
        },

        "Legend": {
            "spacing": 8,
            "glyph_width": 15,

            "label_standoff": 8,
            "label_text_color": "#E0E0E0",
            "label_text_font": "Helvetica",
            "label_text_font_size": "1.025em",

            "border_line_alpha": 0,
            "background_fill_alpha": 0.5, #0.25,
            "background_fill_color": "#434343", #"#20262B"
        },

        "ColorBar": {
            "title_text_color": "#E0E0E0",
            "title_text_font": "Helvetica",
            "title_text_font_size": "1.025em",
            "title_text_font_style": "normal",

            "major_label_text_color": "#E0E0E0",
            "major_label_text_font": "Helvetica",
            "major_label_text_font_size": "1.025em",

            "background_fill_color": "#434343", #"#15191C",
            "major_tick_line_alpha": 0,
            "bar_line_alpha": 0
        },

        "Title": {
            "text_color": "#E0E0E0",
            "text_font": "Helvetica",
            "text_font_size": "1.15em"
        }
    }
}


_guiBlack = {
    "attrs": {
        "Figure" : {
            "background_fill_color": "#000000", 
            "border_fill_color": "#434343", 
            "outline_line_color": "#E0E0E0",
            "outline_line_alpha": 0.25
        },

        "Grid": {
            "grid_line_color": "#E0E0E0",
            "grid_line_alpha": 0.25
        },

        "Axis": {
            "major_tick_line_alpha": 0,
            "major_tick_line_color": "#E0E0E0",

            "minor_tick_line_alpha": 0,
            "minor_tick_line_color": "#E0E0E0",

            "axis_line_alpha": 0,
            "axis_line_color": "#E0E0E0",

            "major_label_text_color": "#E0E0E0",
            "major_label_text_font": "Helvetica",
            "major_label_text_font_size": "1.025em",

            "axis_label_standoff": 10,
            "axis_label_text_color": "#E0E0E0",
            "axis_label_text_font": "Helvetica",
            "axis_label_text_font_size": "1.25em",
            "axis_label_text_font_style": "normal"
        },

        "Legend": {
            "spacing": 8,
            "glyph_width": 15,

            "label_standoff": 8,
            "label_text_color": "#E0E0E0",
            "label_text_font": "Helvetica",
            "label_text_font_size": "1.025em",

            "border_line_alpha": 0,
            "background_fill_alpha": 0.5, #0.25,
            "background_fill_color": "#434343", #"#20262B"
        },

        "ColorBar": {
            "title_text_color": "#E0E0E0",
            "title_text_font": "Helvetica",
            "title_text_font_size": "1.025em",
            "title_text_font_style": "normal",

            "major_label_text_color": "#E0E0E0",
            "major_label_text_font": "Helvetica",
            "major_label_text_font_size": "1.025em",

            "background_fill_color": "#434343", #"#15191C",
            "major_tick_line_alpha": 0,
            "bar_line_alpha": 0
        },

        "Title": {
            "text_color": "#E0E0E0",
            "text_font": "Helvetica",
            "text_font_size": "1.15em"
        }
    }
}


_guiWhite = {
    "attrs": {
        "Figure" : {
            "background_fill_color": "#ffffff", #"#20262B",
            "border_fill_color": "#434343", #"#15191C",
            "outline_line_color": "#E0E0E0",
            "outline_line_alpha": 0.25
        },

        "Grid": {
            "grid_line_color": "#E0E0E0",
            "grid_line_alpha": 0.25
        },

        "Axis": {
            "major_tick_line_alpha": 0,
            "major_tick_line_color": "#E0E0E0",

            "minor_tick_line_alpha": 0,
            "minor_tick_line_color": "#E0E0E0",

            "axis_line_alpha": 0,
            "axis_line_color": "#E0E0E0",

            "major_label_text_color": "#E0E0E0",
            "major_label_text_font": "Helvetica",
            "major_label_text_font_size": "1.025em",

            "axis_label_standoff": 10,
            "axis_label_text_color": "#E0E0E0",
            "axis_label_text_font": "Helvetica",
            "axis_label_text_font_size": "1.25em",
            "axis_label_text_font_style": "normal"
        },

        "Legend": {
            "spacing": 8,
            "glyph_width": 15,

            "label_standoff": 8,
            "label_text_color": "#E0E0E0",
            "label_text_font": "Helvetica",
            "label_text_font_size": "1.025em",

            "border_line_alpha": 0,
            "background_fill_alpha": 0.5, #0.25,
            "background_fill_color": "#434343", #"#20262B"
        },

        "ColorBar": {
            "title_text_color": "#E0E0E0",
            "title_text_font": "Helvetica",
            "title_text_font_size": "1.025em",
            "title_text_font_style": "normal",

            "major_label_text_color": "#E0E0E0",
            "major_label_text_font": "Helvetica",
            "major_label_text_font_size": "1.025em",

            "background_fill_color": "#434343", #"#15191C",
            "major_tick_line_alpha": 0,
            "bar_line_alpha": 0
        },

        "Title": {
            "text_color": "#E0E0E0",
            "text_font": "Helvetica",
            "text_font_size": "1.15em"
        }
    }
}

