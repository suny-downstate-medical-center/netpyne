# Generate plots of LFP (local field potentials) and related analyses

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import math
from ..analysis.utils import exception #, loadData
from ..analysis.tools import loadData
from .plotter import LinesPlotter
from .plotter import ImagePlotter
from .plotter import MultiFigure
import numpy as np


#@exception
def plotLFPSpectrogram(
    SpectData=None,
    sim=None,
    axis=None, 
    timeRange=None,
    electrodes=['avg', 'all'],
    NFFT=256,
    noverlap=128, 
    nperseg=256,
    minFreq=1, 
    maxFreq=100, 
    stepFreq=1, 
    smooth=0,
    logx=False,
    logy=False, 
    normSignal=False,
    normPSD=False, 
    filtFreq=False, 
    filtOrder=3, 
    detrend=False, 
    transformMethod='morlet',
    returnPlotter=False,
    **kwargs):
    
    # If there is no input data, get the data from the NetPyNE sim object
    if SpectData is None:
        if 'sim' not in kwargs:
            from .. import sim
        else:
            sim = kwargs['sim']

        SpectData = sim.analysis.prepareSpectrogram(
            sim=sim,
            timeRange=timeRange,
            electrodes=electrodes, 
            NFFT=NFFT, 
            noverlap=noverlap, 
            nperseg=nperseg, 
            minFreq=minFreq, 
            maxFreq=maxFreq, 
            stepFreq=stepFreq, 
            smooth=smooth, 
            logx=logx, 
            logy=logy, 
            normSignal=normSignal, 
            normPSD=normPSD, 
            filtFreq=filtFreq, 
            filtOrder=filtOrder, 
            detrend=detrend, 
            transformMethod=transformMethod, 
            **kwargs)

    print('Plotting LFP spectrogram...')

    # If input is a dictionary, pull the data out of it
    if type(SpectData) == dict:
    
        names = SpectData['electrodes']['names']
        vmin = SpectData['electrodes']['spectrogram']['vmin']
        vmax = SpectData['electrodes']['spectrogram']['vmax']
        axisArgs = SpectData.get('axisArgs')

    if 'rcParams' in kwargs:
        rcParams = kwargs['rcParams']
    else:
        rcParams = None

    if axis is None:
        multiFig = MultiFigure(kind='spect', subplots=len(names), rcParams=rcParams, **kwargs)

    if 'morlet' in SpectData['electrodes']['spectrogram'].keys():
        spect = SpectData['electrodes']['spectrogram']['morlet']
        extent = SpectData['electrodes']['spectrogram']['extent']

    elif 'fft' in SpectData['electrodes']['spectrogram'].keys():
        spect = SpectData['electrodes']['spectrogram']['fft']
        xmesh = SpectData['electrodes']['spectrogram']['xmesh']
        ymesh = SpectData['electrodes']['spectrogram']['ymesh']
    
    for index, name in enumerate(names):

        # Create a dictionary with the inputs for an image plot
        imageData = {}
        imageData['X'] = np.array(spect)[index,:,:]
        imageData['vmin'] = vmin
        imageData['vmax'] = vmax
        imageData['extent'] = extent[index]
        imageData['origin'] = 'lower'
        imageData['interpolation'] = 'None'
        imageData['aspect'] = 'auto'
        imageData['cmap'] = plt.get_cmap('viridis')

        # Create a dictionary to hold axis inputs
        axisArgs = {}
        axisArgs['title'] = 'Electrode ' + name
        axisArgs['xlabel'] = 'Time (ms)'
        axisArgs['ylabel'] = 'Frequency (Hz)'

        # Create a dictionary to hold colorbar settings
        colorbarArgs = {}
        #colorbarArgs['mappable']     = None
        #colorbarArgs['cax']          = None
        #colorbarArgs['ax']           = None
        #colorbarArgs['use_gridspec'] = None
        #colorbarArgs['location']     = None
        #colorbarArgs['orientation']  = None
        #colorbarArgs['fraction']     = None
        #colorbarArgs['shrink']       = None
        #colorbarArgs['aspect']       = None
        #colorbarArgs['pad']          = None
        #colorbarArgs['anchor']       = None
        #colorbarArgs['panchor']      = None
        colorbarArgs['label']        = 'Power'

        axisArgs['colorbar'] = colorbarArgs



        plotaxis = axis
        if axis is None:
            if len(names) > 1:
                plotaxis = multiFig.ax[index]
            else:
                plotaxis = multiFig.ax
        
        imagePlotter = ImagePlotter(data=imageData, kind='spect', multifig=multiFig, axis=plotaxis, **axisArgs, **kwargs)
        spectPlot = imagePlotter.plot(**axisArgs, **kwargs)

        multiFig.plotters.append(imagePlotter)

    suptitle = {'t':'LFP Spectrogram'}

    if axis is None:
        multiFig.finishFig(suptitle=suptitle, **kwargs)
        return multiFig.fig
    else:
        return plt.gcf()


