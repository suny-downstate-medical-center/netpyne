"""
Module for utilities to help analyze and plot results

"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()

from builtins import round
from builtins import open
from builtins import range

try:
    to_unicode = unicode
except NameError:
    to_unicode = str
try:
    basestring
except NameError:
    basestring = str

import functools
import sys
import pandas as pd
import pickle, json
import os




def exception(function):
    """
    Wrapper function to catch exceptions in functions

    Parameters
    ----------
    function : function
        A Python function
        **Required**

    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            err = "There was an exception in %s():" % (function.__name__)
            print(("  %s \n    %s \n    %s" % (err, e, sys.exc_info())))
            return -1

    return wrapper



def getInclude(include='allCells', sim=None):
    """
    Function to return the cells indicated by the include list

    Parameters
    ----------
    include : str, int, list
        Cells and/or NetStims to return information for
        **Default:** 'allCells' includes all cells
        **Options:** 
        (1) 'all' includes all cells and all NetStims, 
        (2) 'allNetStims' includes all NetStims but no cells, 
        (3) a string which matches a pop name includes all cells in that pop,
        (4) a string which matches a NetStim name includes that NetStim, 
        (5) an int includes the cell with that global identifier (GID), 
        (6) a list of ints includes the cells with those GIDS,
        (7) a list with two items, the first of which is a string matching a pop name and the second of which is an int or a list of ints, includes the relative cell(s) from that population (e.g. ('popName', [0, 1]) includes the first two cells in popName, which are not likely to be the cells with GID 0 and 1)

    sim : NetPyNE sim object
        **Default:** ``None`` uses the current NetPyNE sim object

    Returns
    -------
    cells, cellGids, netStimLabels : tuple
        ``cells`` is a list of dicts containing cell information, ``cellGids`` is a list of ints of the global identifier (GID) for each cell, ``netStimLabels`` is a list of strings of the included stimulations

    """

    if not sim:
        from .. import sim

    allCells = sim.net.allCells
    allNetStimLabels = list(sim.net.params.stimSourceParams.keys())
    cellGids = []
    cells = []
    netStimLabels = []

    if type(include) == str:
        include = [include]
    
    for condition in include:

        if condition == 'all':  # all cells and all Netstims
            cellGids = [c['gid'] for c in allCells]
            cells = list(allCells)
            netStimLabels = list(allNetStimLabels)
            return cells, cellGids, netStimLabels

        elif condition == 'allCells':  # all cells but no NetStims
            cellGids = [c['gid'] for c in allCells]
            cells = list(allCells)

        elif condition == 'allNetStims':  # all Netstims but no cells
            netStimLabels = list(allNetStimLabels)

        elif isinstance(condition, int):  # cell gid
            cellGids.append(condition)

        elif isinstance(condition, basestring):  # entire pop or single NetStim
            if condition in allNetStimLabels:
                netStimLabels.append(condition)
            else:
                cellGids.extend([c['gid'] for c in allCells if c['tags']['pop'] == condition])

        elif (isinstance(condition, (list, tuple))  
        and len(condition) == 2
        and isinstance(condition[0], basestring)
        and isinstance(condition[1], (list, int))): # subset of a pop with relative indices
            
            cellsPop = [c['gid'] for c in allCells if c['tags']['pop'] == condition[0]]
            if isinstance(condition[1], list):
                cellGids.extend([gid for i, gid in enumerate(cellsPop) if i in condition[1]])
            elif isinstance(condition[1], int):
                cellGids.extend([gid for i, gid in enumerate(cellsPop) if i == condition[1]])

        elif isinstance(condition, (list,tuple)):  # subset
            for subcond in condition:
                if isinstance(subcond, int):  # cell gid
                    cellGids.append(subcond)

                elif isinstance(subcond, basestring):  # entire pop or single NetStim
                    if subcond in allNetStimLabels:
                        netStimLabels.append(subcond)
                    else:
                        cellGids.extend([c['gid'] for c in allCells if c['tags']['pop'] == subcond])

    cellGids = sim.unique(cellGids)
    cells = [cell for cell in allCells if cell['gid'] in cellGids]
    cells = sorted(cells, key=lambda k: k['gid'])

    return cells, cellGids, netStimLabels



def getSpktSpkid(cellGids=[], timeRange=None, sim=None):
    """
    Function to efficiently get a subset of spikes based on a timeRange and cellGids list

    Parameters
    ----------
    cellGids : list
        A list of cells to include by global identifier (GID)
        **Default:** ``[]``

    timeRange : [start, stop]
        A list of two floats specifying the time range of spikes to include
        **Default:** ``None`` includes the entire simulation time range

    sim : NetPyNE sim object
        **Default:** ``None`` uses the current NetPyNE sim object

    Returns
    -------
    (selection, spkt, spkid)
        A tuple consisting of the subset in a Pandas dataframe, a list of spike times, and a list of spike GIDs

    """

    if not sim:
        from .. import sim

    try: # Pandas 1.4.0
        from pandas._libs import lib as pandaslib
    except:
        try: # Pandas 0.24 and later
            from pandas import _lib as pandaslib
        except: # Pandas 0.23 and earlier
            from pandas import lib as pandaslib
            

    df = pd.DataFrame(pandaslib.to_object_array([sim.allSimData['spkt'], sim.allSimData['spkid']]).transpose(), columns=['spkt', 'spkid'])

    if timeRange:
        # binary search is faster than query
        min, max = [int(df['spkt'].searchsorted(timeRange[i])) for i in range(2)] 
    else:
        min, max = 0, len(df)
    
    if len(cellGids) == 0:
        sel = df[min:max]
    else:
        sel = df[min:max].query('spkid in @cellGids')

    spktList = sel['spkt'].tolist()
    spkidList = sel['spkid'].tolist()
    
    return sel, spktList, spkidList



def plotData(sim=None):
    """
    Wrapper to run plotting functions specified in simConfig
    
    Parameters
    ----------
    sim : NetPyNE sim object
        **Default:** ``None`` uses the current NetPyNE sim object

    """

    if not sim:
        from .. import sim

    from netpyne import __gui__

    # Only plot from the main node in parallel simulations
    if sim.rank == 0 and __gui__:
        sim.timing('start', 'plotTime')

        # Call analysis functions specified by user
        for funcName, kwargs in sim.cfg.analysis.items():
            if kwargs == True: kwargs = {}
            elif kwargs == False: continue
            func = None
            try:
                func = getattr(sim.plotting, funcName)
                out = func(**kwargs)  # call function with user arguments
            except:
                try:
                    func = getattr(sim.analysis, funcName)
                    out = func(**kwargs)  # call function with user arguments
                except Exception as e:
                    print('Unable to run', funcName, 'from sim.plotting and sim.analysis. Reason:', e)
                

        # Print timings
        if sim.cfg.timing:

            sim.timing('stop', 'plotTime')
            print(('  Done; plotting time = %0.2f s' % sim.timingData['plotTime']))

            sim.timing('stop', 'totalTime')
            sumTime = sum([t for k,t in sim.timingData.items() if k not in ['totalTime']])
            if sim.timingData['totalTime'] <= 1.2*sumTime:  # Print total time (only if makes sense)
                print(('\nTotal time = %0.2f s' % sim.timingData['totalTime']))

        try:
            print('\nEnd time: ', datetime.now())
        except:
            pass


def saveData(data, fileName=None, fileDesc=None, fileType=None, fileDir=None, sim=None, **kwargs):
    """
    Function to save data to a file
    
    Parameters
    ----------
    data : data object
        **Required**

    fileName : str
        **Default:** ``None`` uses sim.cfg.fileName

    fileDesc : str
        **Default:** ``None``
        If fileDesc is a string, it will be added to the file name after an underscore

    fileType : str
        **Default:** ``None`` saves the data as a Python Pickle file
        **Options:** ``'json'`` saves the data in a .json file

    fileDir : str
        **Default:** ``None`` saves to the current directory

    sim : NetPyNE sim object
        **Default:** ``None`` uses the current NetPyNE sim object

    Returns
    -------
    fileName : str
        The complete name, with extension and path, of the file saved

    """

    if not sim:
        from .. import sim

    if not fileType or fileType in ['pkl', 'pickle', '.pkl']:
        fileExt = '.pkl'
    elif fileType in ['json', '.json']:
        fileExt = '.json'
    else:
        raise Exception('fileType not recognized in saveData')

    if fileDesc is None:
        fileDesc = '_data'
    else:
        fileDesc = '_' + str(fileDesc)

    if not fileName or not isinstance(fileName, basestring):
        fileName = sim.cfg.filename + fileDesc + fileExt
    else:
        if fileName.endswith(fileExt):
            fileName = fileName.split(fileExt)[0] + fileDesc + fileExt
        else:
            fileName = fileName + fileDesc + fileExt

    if fileDir is not None:
        fileName = os.path.join(fileDir, fileName)

    if fileName.endswith('.pkl'):
        print(('Saving data as %s ... ' % (fileName)))
        with open(fileName, 'wb') as fileObj:
            pickle.dump(data, fileObj)

    elif fileName.endswith('.json'):
        print(('Saving data as %s ... ' % (fileName)))
        sim.saveJSON(fileName, data)
    else:
        print('File extension to save data not recognized')

    return fileName


def loadData(fileName, fileDir=None, sim=None):
    """
    Function to load data from a file (JSON or Python Pickle)
    
    Parameters
    ----------
    fileName : str
        **Required**

    fileDir : str
        The directory to load the data file from
        **Default:** ``None`` loads from the current directory

    sim : NetPyNE sim object
        **Default:** ``None`` uses the current NetPyNE sim object

    Returns
    -------
    data : dict
        The data from the file

    """
    
    if fileDir is not None:
        fileName = os.path.join(fileName, fileDir)

    if fileName.endswith('.pkl'):
        with open(fileName, 'rb') as input_file:
            data = pickle.load(input_file)

    elif fileName.endswith('.json'):
        with open(fileName) as input_file:
            data = json.load(input_file)
    
    else:
        raise Exception('loadData can only load JSON (.json) or Python Pickle (.pkl) files')

    return data

  
def checkAvailablePlots(requireCfg=False):
    """
    Function to check which plots are available for the GUI 

    Parameters
    ----------
    requireCfg : bool
        Whether a plot configuration in sim.cfg.analysis is required to return True for each plot
        **Default:** False

    Returns
    ----------
    output : dict
        Keys indicate the name of the analysis function and values whether they are available or not (Boolean)

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
