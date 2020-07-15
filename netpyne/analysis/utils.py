"""
Helper functions to plot and analyse results
"""

from __future__ import print_function
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

# -------------------------------------------------------------------------------------------------------------------
# Define list of colors
# -------------------------------------------------------------------------------------------------------------------
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
    A decorator that wraps the passed in function and prints exception should one occur
    """
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            # print 
            err = "There was an exception in %s():"%(function.__name__)
            print(("  %s \n    %s \n    %s"%(err,e,sys.exc_info())))
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
        print(('Saving figure data as %s ... ' % (fileName)))
        with open(fileName, 'wb') as fileObj:
            pickle.dump(figData, fileObj)

    elif fileName.endswith('.json'):  # save to json
        print(('Saving figure data as %s ... ' % (fileName)))
        sim.saveJSON(fileName, figData)
    else: 
        print('File extension to save figure data not recognized')


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
    #print(len(s))
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
    """ Invert mapping of dictionary (i.e. map values to list of keys) """
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
    return spike ids and times; with allCells=True just need to identify slice of time so can omit cellGids
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
