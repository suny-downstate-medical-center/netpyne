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



colorList = [[0.42, 0.67, 0.84], [0.90, 0.76, 0.00], [0.42, 0.83, 0.59], [0.90, 0.32, 0.00],
             [0.34, 0.67, 0.67], [0.90, 0.59, 0.00], [0.42, 0.82, 0.83], [1.00, 0.85, 0.00],
             [0.33, 0.67, 0.47], [1.00, 0.38, 0.60], [0.57, 0.67, 0.33], [0.50, 0.20, 0.00],
             [0.71, 0.82, 0.41], [0.00, 0.20, 0.50], [0.70, 0.32, 0.10]] * 3


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



def getCellsInclude(include='allCells', sim=None):
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
    
    return sel, sel['spkt'].tolist(), sel['spkid'].tolist()



def plotData(sim=None):
    """
    Wrapper to run plotting functions specified in somConfig
    
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
            func = getattr(sim.plotting, funcName)  # get pointer to function
            out = func(**kwargs)  # call function with user arguments

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