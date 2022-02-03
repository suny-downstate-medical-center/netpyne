# Generate plots of LFP (local field potentials) and related analyses

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from ..analysis.utils import exception #, loadData
from ..analysis.tools import loadData
from .plotter import LinesPlotter
from .plotter import ImagePlotter
from .plotter import MultiFigure
import numpy as np


#@exception
def plotLFPTimeSeries(
    LFPData=None, 
    axis=None, 
    sim=None,
    timeRange=None,
    electrodes=['avg', 'all'], 
    pop=None,
    separation=1.0, 
    logy=False, 
    normSignal=False, 
    filtFreq=False, 
    filtOrder=3, 
    detrend=False, 
    returnPlotter=False,
    colorList=None,
    orderInverse=True,
    legend=True,
    overlay=True,
    scalebar=True,
    **kwargs):
    

    # If there is no input data, get the data from the NetPyNE sim object
    if LFPData is None:
        if 'sim' not in kwargs:
            from .. import sim
        else:
            sim = kwargs['sim']

        LFPData = sim.analysis.prepareLFP(
            sim=sim,
            timeRange=timeRange,
            electrodes=electrodes, 
            LFPData=LFPData, 
            logy=logy, 
            normSignal=normSignal, 
            filtFreq=filtFreq, 
            filtOrder=filtOrder, 
            detrend=detrend, 
            **kwargs
            )

    print('Plotting LFP time series...')

    # If input is a dictionary, pull the data out of it
    if type(LFPData) == dict:
    
        t = LFPData['t']
        lfps = LFPData['electrodes']['lfps']
        names = LFPData['electrodes']['names']
        locs = LFPData['electrodes']['locs']
        colors = LFPData.get('colors')
        linewidths = LFPData.get('linewidths')
        alphas = LFPData.get('alphas')
        axisArgs = LFPData.get('axisArgs')

    # Set up colors, linewidths, and alphas for the plots
    if not colors:
        if not colorList:
            from .plotter import colorList
        colors = colorList[0:len(lfps)]

    if not linewidths:
        linewidths = [1.0 for lfp in lfps]

    if not alphas:
        alphas = [1.0 for lfp in lfps]

    # Create a dictionary to hold axis inputs
    if not axisArgs:
        axisArgs = {}
        axisArgs['title'] = 'LFP Time Series Plot'
        axisArgs['xlabel'] = 'Time (ms)'
        axisArgs['ylabel'] = 'LFP Signal (uV)'

    # Link colors to traces, make avg plot black, add separation to traces
    plotColors = []
    legendLabels = []
    colorIndex = 0
    offset = np.absolute(lfps).max() * separation

    for index, (name, lfp) in enumerate(zip(names, lfps)):
        legendLabels.append(name)
        lfps[index] = index * offset + lfp
        if orderInverse:
            lfps[index] = index * offset - lfp
            axisArgs['invert_yaxis'] = True
        else:
            lfps[index] = index * offset + lfp
        if name == 'avg':
            plotColors.append('black')
        else:
            plotColors.append(colors[colorIndex])
            colorIndex += 1

    # Create a dictionary with the inputs for a line plot
    linesData = {}
    linesData['x'] = t
    linesData['y'] = lfps
    linesData['colors'] = plotColors
    linesData['markers'] = None
    linesData['markersizes'] = None
    linesData['linewidths'] = linewidths
    linesData['alphas'] = alphas
    linesData['label'] = legendLabels

    # If a kwarg matches a lines input key, use the kwarg value instead of the default
    for kwarg in kwargs:
        if kwarg in linesData:
            linesData[kwarg] = kwargs[kwarg]

    # create Plotter object
    linesPlotter = LinesPlotter(data=linesData, kind='LFPTimeSeries', axis=axis, **axisArgs, **kwargs)
    multiFig = linesPlotter.multifig

    # remove the y-axis
    # linesPlotter.axis.get_yaxis().set_ticks([])
    # linesPlotter.axis.spines['top'].set_visible(False)
    # linesPlotter.axis.spines['right'].set_visible(False)
    # linesPlotter.axis.spines['left'].set_visible(False)

    # Set up the default legend settings
    legendKwargs = {}
    legendKwargs['title'] = 'Electrodes'
    #legendKwargs['bbox_to_anchor'] = (1.025, 1)
    legendKwargs['loc'] = 'upper right'
    #legendKwargs['borderaxespad'] = 0.0
    #legendKwargs['handlelength'] = 0.5
    legendKwargs['fontsize'] = 'small'
    legendKwargs['title_fontsize'] = 'small'

    # If 'legendKwargs' is found in kwargs, use those values instead of the defaults
    if 'legendKwargs' in kwargs:
        legendKwargs_input = kwargs['legendKwargs']
        kwargs.pop('legendKwargs')
        for key, value in legendKwargs_input:
            if key in legendKwargs:
                legendKwargs[key] = value
    
    # add the legend
    if legend:
        axisArgs['legend'] = legendKwargs

    # add the scalebar
    if scalebar:
        #axisArgs['scalebar'] = True
        args = {}
        args['hidey'] = True
        args['matchy'] = True 
        args['hidex'] = False 
        args['matchx'] = False 
        args['sizex'] = 0 
        args['sizey'] = 1.0 
        args['ymax'] = 0.25 * offset 
        #args['labely'] = 'test'
        args['unitsy'] = '$\mu$V' 
        args['scaley'] = 1000.0
        args['loc'] = 3
        args['pad'] = 0.5 
        args['borderpad'] = 0.5 
        args['sep'] = 3 
        args['prop'] = None 
        args['barcolor'] = "black" 
        args['barwidth'] = 2
        args['space'] = 0.25 * offset

        axisArgs['scalebar'] = args

    if overlay:
        for index, name in enumerate(names):
            linesPlotter.axis.text(t[0]-0.07*(t[-1]-t[0]), (index*offset), name, color=plotColors[index], ha='center', va='center', fontsize='large', fontweight='bold')
        linesPlotter.axis.spines['top'].set_visible(False)
        linesPlotter.axis.spines['right'].set_visible(False)
        linesPlotter.axis.spines['left'].set_visible(False)
        if len(names) > 1:
            linesPlotter.fig.text(0.05, 0.4, 'LFP electrode', color='k', ha='left', va='bottom', fontsize='large', rotation=90)

    # Generate the figure
    LFPTimeSeriesPlot = linesPlotter.plot(**axisArgs, **kwargs)

    if axis is None:
        multiFig.finishFig(**kwargs)

    # Default is to return the figure, but you can also return the plotter
    if returnPlotter:
        return linesPlotter
    else:
        return LFPTimeSeriesPlot




#@exception
def plotPSD(
    PSDData=None,
    sim=None,
    axis=None, 
    timeRange=None,
    electrodes=['avg', 'all'],
    pop=None, 
    separation=1.0,
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

    # Link colors to traces, make avg plot black, add separation to traces
    plotColors = []
    legendLabels = []
    colorIndex = 0
    offset = np.absolute(psds).max() * separation
    
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

    # remove the y-axis
    linesPlotter.axis.get_yaxis().set_ticks([])

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



#@exception
def plotSpectrogram(
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

        plotaxis = axis
        if axis is None:
            if len(names) > 1:
                plotaxis = multiFig.ax[index]
            else:
                plotaxis = multiFig.ax
        
        imagePlotter = ImagePlotter(data=imageData, kind='spect', multifig=multiFig, axis=plotaxis, **axisArgs, **kwargs)
        spectPlot = imagePlotter.plot(**axisArgs, **kwargs)

        multiFig.plotters.append(imagePlotter)

    if axis is None:
        multiFig.finishFig(**kwargs)
        return multiFig.fig
    else:
        return plt.gcf()





#@exception
def plotLFPLocations(
    sim=None,
    axis=None, 
    electrodes=['all'],
    includeAxon=True,
    returnPlotter=False,
    **kwargs):

    print('Plotting LFP electrode locations...')

    if 'sim' not in kwargs:
        from .. import sim
    else:
        sim = kwargs['sim']

    if 'rcParams' in kwargs:
        rcParams = kwargs['rcParams']
    else:
        rcParams = None

    # electrode selection
    if 'all' in electrodes:
        electrodes.remove('all')
        electrodes.extend(list(range(int(sim.net.recXElectrode.nsites))))

    cvals = [] # used to store total transfer resistance

    for cell in sim.net.compartCells:
        trSegs = list(np.sum(sim.net.recXElectrode.getTransferResistance(cell.gid)*1e3, axis=0)) # convert from Mohm to kilohm
        if not includeAxon:
            i = 0
            for secName, sec in cell.secs.items():
                nseg = sec['hObj'].nseg #.geom.nseg
                if 'axon' in secName:
                    for j in range(i,i+nseg): del trSegs[j]
                i+=nseg
        cvals.extend(trSegs)

    includePost = [c.gid for c in sim.net.compartCells]
    
    fig = sim.plotting.plotShape(includePost=includePost, showElectrodes=electrodes, cvals=cvals, includeAxon=includeAxon, **kwargs)[0]

    return fig






