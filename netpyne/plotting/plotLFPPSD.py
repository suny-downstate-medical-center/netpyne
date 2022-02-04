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
def plotLFPPSD(
    PSDData=None,
    sim=None,
    axis=None, 
    timeRange=None,
    electrodes=['avg', 'all'],
    pop=None, 
    separation=1.0,
    roundOffset=True,
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
    colorList=None,
    orderInverse=True,
    legend=True,
    **kwargs):
    

    # If there is no input data, get the data from the NetPyNE sim object
    if PSDData is None:
        if 'sim' not in kwargs:
            from .. import sim
        else:
            sim = kwargs['sim']

        PSDData = sim.analysis.preparePSD(
            PSDData=PSDData, 
            sim=sim,
            timeRange=timeRange,
            electrodes=electrodes,
            pop=pop,
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
            **kwargs
            )

    print('Plotting LFP power spectral density (PSD)...')

    # If input is a dictionary, pull the data out of it
    if type(PSDData) == dict:
    
        freqs = PSDData['psdFreqs']
        freq = freqs[0]
        psds = PSDData['psdSignal']
        names = PSDData['psdNames']
        colors = PSDData.get('colors')
        linewidths = PSDData.get('linewidths')
        alphas = PSDData.get('alphas')
        axisArgs = PSDData.get('axisArgs')

    # Set up colors, linewidths, and alphas for the plots
    if not colors:
        if not colorList:
            from .plotter import colorList
        colors = colorList[0:len(psds)]

    if not linewidths:
        linewidths = [1.0 for name in names]

    if not alphas:
        alphas = [1.0 for name in names]
    
    # Create a dictionary to hold axis inputs
    if not axisArgs:
        axisArgs = {}
        axisArgs['title'] = 'LFP Power Spectral Density'
        axisArgs['xlabel'] = 'Frequency (Hz)'
        axisArgs['ylabel'] = 'Power (arbitrary units)'


    axisArgs['grid'] = {'which': 'both'}

    # Link colors to traces, make avg plot black, add separation to traces
    plotColors = []
    legendLabels = []
    colorIndex = 0
    offset = np.absolute(psds).max() * separation

    if roundOffset:
        sigfigs = 1
        if type(roundOffset) == int:
            sigfigs = roundOffset
        offset = round(offset, sigfigs - int(math.floor(math.log10(abs(offset)))) - 1)
    
    for index, (name, psd) in enumerate(zip(names, psds)):
        legendLabels.append(name)
        if orderInverse:
            psds[index] = index * offset - psd
            axisArgs['invert_yaxis'] = True
        else:
            psds[index] = index * offset + psd
        if name == 'avg':
            plotColors.append('black')
        else:
            plotColors.append(colors[colorIndex])
            colorIndex += 1

    # Create a dictionary with the inputs for a line plot
    linesData = {}
    linesData['x'] = freq
    linesData['y'] = psds
    linesData['colors'] = plotColors
    linesData['markers'] = None
    linesData['markersizes'] = None
    linesData['linewidths'] = None
    linesData['alphas'] = None
    linesData['label'] = legendLabels

    # If a kwarg matches a lines input key, use the kwarg value instead of the default
    for kwarg in kwargs:
        if kwarg in linesData:
            linesData[kwarg] = kwargs[kwarg]

    # create Plotter object
    linesPlotter = LinesPlotter(data=linesData, kind='PSD', axis=axis, **axisArgs, **kwargs)
    multiFig = linesPlotter.multifig

    # remove the y-axis tick labels
    linesPlotter.axis.get_yaxis().set_ticklabels([])

    # Set up the default legend settings
    legendKwargs = {}
    legendKwargs['title'] = 'Electrodes'
    #legendKwargs['bbox_to_anchor'] = (1.025, 1)
    legendKwargs['loc'] = 'upper right'
    #legendKwargs['borderaxespad'] = 0.0
    #legendKwargs['handlelength'] = 0.5
    legendKwargs['fontsize'] = 'small'
    legendKwargs['title_fontsize'] = 'small'
    
    # add the legend
    if legend:
        axisArgs['legend'] = legendKwargs

    # Generate the figure
    PSDPlot = linesPlotter.plot(**axisArgs, **kwargs)

    if axis is None:
        multiFig.finishFig(**kwargs)

    # Default is to return the figure, but you can also return the plotter
    if returnPlotter:
        return linesPlotter
    else:
        return PSDPlot


