"""
Package for analysis

"""

import netpyne

# Import utils methods
from .tools import getInclude, plotData, saveData, loadData
from .utils import exception, _showFigure, _saveFigData, getCellsInclude, getCellsIncludeTags, _roundFigures, _smooth1d, syncMeasure, invertDictMapping, checkAvailablePlots

# Import connectivity-related functions
from .network import plotConn, _plotConnCalculateFromSim, _plotConnCalculateFromFile, plot2Dnet, calculateDisynaptic, plot2Dfiring
from ..plotting import plotShape

# Import spike-related functions
from .spikes import prepareSpikeData, prepareRaster, prepareSpikeHist, popAvgRates
from .spikes_legacy import calculateRate, plotRates, plotSyncs, plotSpikeStats, plotRatePSD, plotRateSpectrogram, popAvgRates, plotfI, calculatefI

# Import traces-related functions
#from .traces import prepareTraces
#from ..plotting import plotTraces
from .traces import plotTraces, plotEPSPAmp

# Import LFP-related functions
from .lfp import prepareLFP
from .lfp import preparePSD
from .lfp import prepareSpectrogram

# Import information theory-related functions
from .info import nTE, granger

# Import RxD-related functions
from .rxd import plotRxDConcentration

# Import interactive functions functions
try:
    from .interactive import iplotDipole, iplotDipoleSpectrogram, iplotDipolePSD, iplotRaster, iplotSpikeHist, iplotRatePSD, iplotTraces, iplotLFP, iplotConn, iplotRxDConcentration, iplot2Dnet, iplotSpikeStats
except:
    print('Warning: could not import interactive plotting functions; make sure the "bokeh" package is installed.')

# Import CSD-related functions
from .csd import prepareCSD
# Import CSD-related functions -- LEGACY VERSION !!
### from .csd import getCSD, plotCSD

# Import dipole-related functions
from .dipole import plotDipole, plotEEG

# Import mapped functions (for legacy purposes)
from .mapping import plotLFP, plotSpikeHist, plotRaster

