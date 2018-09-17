"""
analysis/__init__.py

Functions to plot and analyse results

Contributors: salvadordura@gmail.com
"""

import warnings
warnings.filterwarnings("ignore")

# -------------------------------------------------------------------------------------------------------------------
## Wrapper to run analysis functions in simConfig
# -------------------------------------------------------------------------------------------------------------------
from wrapper import plotData

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
from spikes import calculateRate, plotRates, plotSyncs, plotRaster, plotSpikeHist, plotSpikeStats, plotRatePSD, popAvgRates


# -------------------------------------------------------------------------------------------------------------------
# Import traces-related functions
# -------------------------------------------------------------------------------------------------------------------
from traces import plotTraces, plotEPSPAmp


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
