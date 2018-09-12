"""
analysis.py

Functions to plot and analyse results

Contributors: salvadordura@gmail.com
"""

from netpyne import __gui__
if __gui__:
    import matplotlib.pyplot as plt
import numpy as np
import functools

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
            print("%s \n %s"%(err,e))
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
    import sim

    if not fileName or not isinstance(fileName, basestring):
        fileName = sim.cfg.filename+'_'+type+'.pkl'

    if fileName.endswith('.pkl'): # save to pickle
        import pickle
        print('Saving figure data as %s ... ' % (fileName))
        with open(fileName, 'wb') as fileObj:
            pickle.dump(figData, fileObj)

    elif fileName.endswith('.json'):  # save to json
        import json
        print('Saving figure data as %s ... ' % (fileName))
        with open(fileName, 'w') as fileObj:
            json.dump(figData, fileObj)
    else: 
        print 'File extension to save figure data not recognized'


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
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    return y[(window_len/2-1):-(window_len/2)]


# -------------------------------------------------------------------------------------------------------------------
## Get subset of cells and netstims indicated by include list
# -------------------------------------------------------------------------------------------------------------------
def getCellsInclude(include):
    import sim

    allCells = sim.net.allCells
    allNetStimLabels = sim.net.params.stimSourceParams.keys()
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
                cellGids = allCells.keys()
                return cellGids

            elif isinstance(condition, int):  # cell gid 
                cellGids.append(condition)
            
            elif isinstance(condition, basestring):  # entire pop
                cellGids.extend([gid for gid,c in allCells.iteritems() if c[popIndex]==condition])
            
            elif isinstance(condition, tuple):  # subset of a pop with relative indices
                cellsPop = [gid for gid,c in allCells.iteritems() if c[popIndex]==condition[0]]
                if isinstance(condition[1], list):
                    cellGids.extend([gid for i,gid in enumerate(cellsPop) if i in condition[1]])
                elif isinstance(condition[1], int):
                    cellGids.extend([gid for i,gid in enumerate(cellsPop) if i==condition[1]])

    # using dict with keys
    else:
    
        for condition in include:
            if condition in  ['all', 'allCells']:  # all cells 
                cellGids = allCells.keys()
                return cellGids

            elif isinstance(condition, int):  # cell gid 
                cellGids.append(condition)
            
            elif isinstance(condition, basestring):  # entire pop
                cellGids.extend([gid for gid,c in allCells.iteritems() if c['pop']==condition])
            
            elif isinstance(condition, tuple):  # subset of a pop with relative indices
                cellsPop = [gid for gid,c in allCells.iteritems() if c['pop']==condition[0]]
                if isinstance(condition[1], list):
                    cellGids.extend([gid for i,gid in enumerate(cellsPop) if i in condition[1]])
                elif isinstance(condition[1], int):
                    cellGids.extend([gid for i,gid in enumerate(cellsPop) if i==condition[1]])

    cellGids = [int(x) for x in set(cellGids)]  # unique values

    return cellGids


# -------------------------------------------------------------------------------------------------------------------
## Synchrony measure
# -------------------------------------------------------------------------------------------------------------------
def syncMeasure ():
    import sim

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
    for k, v in d.iteritems():
        inv_map[v] = inv_map.get(v, [])
        inv_map[v].append(k)
    return inv_map

