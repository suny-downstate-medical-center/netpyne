"""
Package for analysis

"""

# Import utils methods
from .tools import getInclude, plotData, saveData, loadData
from .utils import exception, _showFigure, _saveFigData, getCellsInclude, getCellsIncludeTags, _roundFigures, _smooth1d, syncMeasure, invertDictMapping, checkAvailablePlots

# Import connectivity-related functions
from .network import plotConn, _plotConnCalculateFromSim, _plotConnCalculateFromFile, plot2Dnet, calculateDisynaptic, plot2Dfiring
from ..plotting import plotShape

# Import spike-related functions
from .spikes import prepareSpikeData, prepareRaster, prepareSpikeHist, popAvgRates

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
from .csd import getCSD, plotCSD


# Legacy code so that new plots produce same output as originals
def plotLFP(
    timeRange=None, 
    electrodes=['avg', 'all'], 
    plots=['timeSeries', 'PSD', 'spectrogram', 'locations'], 
    inputLFP=None, 
    NFFT=256, 
    noverlap=128, 
    nperseg=256, 
    minFreq=1, 
    maxFreq=100, 
    stepFreq=1, 
    smooth=0, 
    separation=1.0, 
    includeAxon=True, 
    logx=False, 
    logy=False, 
    normSignal=False, 
    normPSD=False, 
    normSpec=False, 
    filtFreq=False, 
    filtOrder=3, 
    detrend=False, 
    transformMethod='morlet', 
    maxPlots=8, 
    overlay=False, 
    colors=None, 
    figSize=(8, 8), 
    fontSize=14, 
    lineWidth=1.5, 
    dpi=200, 
    saveData=None, 
    saveFig=None, 
    showFig=True,):

    from ..plotting import plotLFPTimeSeries, plotLFPPSD, plotLFPSpectrogram, plotLFPLocations

    if 'timeSeries' in plots:
        plotLFPTimeSeries(
            timeRange=timeRange,
            electrodes=electrodes,
            separation=separation,
            logy=logy,
            normSignal=normSignal, 
            filtFreq=filtFreq, 
            filtOrder=filtOrder, 
            detrend=detrend, 
            colorList=colors,
            figSize=figSize,
            legend=False,
            overlay=True,
            dpi=dpi,
            saveFig=saveFig,
            showFig=showFig,
            )

    
    if 'PSD' in plots:
        plotLFPPSD()
    
    if 'spectrogram' in plots:
        plotLFPSpectrogram()
    
    if 'locations' in plots:
        plotLFPLocations()


def plotSpikeHist(**kwargs):
    pass

def plotRaster(**kwargs):
    pass


