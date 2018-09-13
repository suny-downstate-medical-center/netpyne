"""
analysis.py

Functions to plot and analyse results

Contributors: salvadordura@gmail.com
"""

from netpyne import __gui__

import warnings
warnings.filterwarnings("ignore")

# -------------------------------------------------------------------------------------------------------------------
## Wrapper to run analysis functions in simConfig
# -------------------------------------------------------------------------------------------------------------------
def plotData ():
    import sim

    ## Plotting
    if sim.rank == 0 and __gui__:
        sim.timing('start', 'plotTime')

        # Call analysis functions specified by user
        for funcName, kwargs in sim.cfg.analysis.iteritems():
            if kwargs == True: kwargs = {}
            elif kwargs == False: continue
            func = getattr(sim.analysis, funcName)  # get pointer to function
            out = func(**kwargs)  # call function with user arguments

        # Print timings
        if sim.cfg.timing:

            sim.timing('stop', 'plotTime')
            print('  Done; plotting time = %0.2f s' % sim.timingData['plotTime'])

            sim.timing('stop', 'totalTime')
            sumTime = sum([t for k,t in sim.timingData.iteritems() if k not in ['totalTime']])
            if sim.timingData['totalTime'] <= 1.2*sumTime:  # Print total time (only if makes sense)
                print('\nTotal time = %0.2f s' % sim.timingData['totalTime'])



# -------------------------------------------------------------------------------------------------------------------
# Import utils methods
# -------------------------------------------------------------------------------------------------------------------
from utils import exception, _showFigure, _saveFigData, getCellsInclude, getCellsIncludeTags, _roundFigures, \
     _smooth1d, syncMeasure, invertDictMapping


# -------------------------------------------------------------------------------------------------------------------
# Import connectivity-related functions
# -------------------------------------------------------------------------------------------------------------------
from network import plotConn, _plotConnCalculateFromSim, _plotConnCalculateFromFile, plot2Dnet, plotShape, calculateDisynaptic


# -------------------------------------------------------------------------------------------------------------------
# Import spike-related functions
# -------------------------------------------------------------------------------------------------------------------
from spikes import calculateRate, plotRates, plotSyncs, plotRaster, plotSpikeHist, plotSpikeStats, plotRatePSD


# -------------------------------------------------------------------------------------------------------------------
# Import traces-related functions
# -------------------------------------------------------------------------------------------------------------------
from traces import calculateRate, plotRates, plotSyncs, plotRaster, plotSpikeHist, plotSpikeStats, plotRatePSD


# -------------------------------------------------------------------------------------------------------------------
# Import cell shape-related functions
# -------------------------------------------------------------------------------------------------------------------
from shape import calculateRate, plotRates, plotSyncs, plotRaster, plotSpikeHist, plotSpikeStats, plotRatePSD


# -------------------------------------------------------------------------------------------------------------------
# Import cell shape-related functions
# -------------------------------------------------------------------------------------------------------------------
from shape import calculateRate, plotRates, plotSyncs, plotRaster, plotSpikeHist, plotSpikeStats, plotRatePSD


# -------------------------------------------------------------------------------------------------------------------
# Import LFP-related functions
# -------------------------------------------------------------------------------------------------------------------
from lfp import plotLFP


# -------------------------------------------------------------------------------------------------------------------
# Import information theory-related functions
# -------------------------------------------------------------------------------------------------------------------
from info import nTE, granger


# -------------------------------------------------------------------------------------------------------------------
# Import RxD-related functions
# -------------------------------------------------------------------------------------------------------------------
from rxd import plotRxDConcentration
