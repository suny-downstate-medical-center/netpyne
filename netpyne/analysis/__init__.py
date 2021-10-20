"""
Package for analysis

"""

# Import utils methods
from .tools import getInclude, plotData, saveData, loadData
from .utils import exception, _showFigure, _saveFigData, getCellsInclude, getCellsIncludeTags, _roundFigures, _smooth1d, syncMeasure, invertDictMapping, checkAvailablePlots

from netpyne.logger import logger
# Import connectivity-related functions
from .network import plotConn, _plotConnCalculateFromSim, _plotConnCalculateFromFile, plot2Dnet, plotShape, calculateDisynaptic, plot2Dfiring

# Import spike-related functions
from .spikes import prepareSpikeData, prepareRaster, prepareSpikeHist, popAvgRates
from ..plotting import plotRaster
from ..plotting import plotSpikeHist

# Import traces-related functions
#from .traces import prepareTraces
#from ..plotting import plotTraces
from .traces import plotTraces, plotEPSPAmp

# Import LFP-related functions
from .lfp import plotLFP

# Import information theory-related functions
from .info import nTE, granger

# Import RxD-related functions
from .rxd import plotRxDConcentration

# Import interactive functions functions
try:
    from .interactive import iplotDipole, iplotDipoleSpectrogram, iplotDipolePSD, iplotRaster, iplotSpikeHist, iplotRatePSD, iplotTraces, iplotLFP, iplotConn, iplotRxDConcentration, iplot2Dnet, iplotSpikeStats
except:
    logger.warning('Could not import interactive plotting functions; make sure the "bokeh" package is installed.')

# Import CSD-related functions
from .csd import getCSD, plotCSD