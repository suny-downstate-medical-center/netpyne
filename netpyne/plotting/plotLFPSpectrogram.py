# Generate plots of LFP (local field potentials) and related analyses

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import math
from ..analysis.utils import exception #, loadData
from ..analysis.tools import loadData
from .plotter import LinesPlotter
from .plotter import ImagePlotter
from .plotter import MetaFigure
import numpy as np


@exception
def plotLFPSpectrogram(
    SpectData=None,
    axis=None, 
    timeRange=None,
    electrodes=['avg', 'all'],
    pop=None,
    NFFT=256,
    noverlap=128, 
    nperseg=256,
    minFreq=1, 
    maxFreq=100, 
    stepFreq=1, 
    smooth=0,
    logy=False, 
    normSignal=False,
    normPSD=False, 
    filtFreq=False, 
    filtOrder=3, 
    detrend=False, 
    transformMethod='morlet',
    returnPlotter=False,
    **kwargs):
    """Function to produce a plot of LFP electrode spectrograms

    NetPyNE Options
    ---------------
    sim : NetPyNE sim object
        The *sim object* from which to get data.
        
        *Default:* ``None`` uses the current NetPyNE sim object

    Parameters
    ----------
    SpectData : dict, str
        The data necessary to plot the LFP spectrogram. 

        *Default:* ``None`` uses ``analysis.prepareSpectrogram`` to produce ``SpectData`` using the current NetPyNE sim object.
        
        If a *str* it must represent a file path to previously saved data.
        
    axis : matplotlib axis
        The axis to plot into, allowing overlaying of plots.
        
        *Default:* ``None`` produces a new figure and axis.

    timeRange : list
        Time range to include in the raster: ``[min, max]``.
        
        *Default:* ``None`` uses the entire simulation

    electrodes : list
        A *list* of the electrodes to plot from.
        
        *Default:* ``['avg', 'all']`` plots each electrode as well as their average

    pop : str
        A population name to calculate PSD from.
        
        *Default:* ``None`` uses all populations.

    NFFT : int (power of 2)
        Number of data points used in each block for the PSD and time-freq FFT.
        **Default:** ``256``

    noverlap : int (<nperseg)
        Number of points of overlap between segments for PSD and time-freq.
        **Default:** ``128``

    nperseg : int
        Length of each segment for time-freq.
        **Default:** ``256``

    minFreq : float
        Minimum frequency shown in plot for PSD and time-freq.
        **Default:** ``1``

    maxFreq : float
        Maximum frequency shown in plot for PSD and time-freq.
        **Default:** ``100``

    stepFreq : float
        Step frequency.
        **Default:** ``1``

    smooth : int
        Window size for smoothing LFP; no smoothing if ``0``
        **Default:** ``0``

    logy : bool
        Whether to use a log axis.

        *Default:* ``False`` 
    
    normSignal : bool
        Whether to normalize the LFP data.

        *Default:* ``False``

    normPSD : bool
        Whether to normalize the PSD data.

        *Default:* ``False``

    filtFreq : int or list
        Frequency for low-pass filter (int) or frequencies for bandpass filter in a list: [low, high]
        
        *Default:* ``None`` does not filter the data

    filtOrder : int
        Order of the filter defined by `filtFreq`.

        *Default:* ``3``    

    detrend : bool
        Whether to detrend the data.

        *Default:* ``False``

    transformMethod : str
        The transformation method to use, either 'morlet' or 'fft'.

        *Default:* ``'morlet'`` 

    returnPlotter : bool
        Whether to return the figure or the NetPyNE MetaFig object.
        
        *Default:* ``False`` returns the figure.


    Plot Options
    ------------
    showFig : bool
        Whether to show the figure.

        *Default:* ``False``

    saveFig : bool
        Whether to save the figure.

        *Default:* ``False``

    overwrite : bool
        whether to overwrite existing figure files.

        *Default:* ``True`` overwrites the figure file

        *Options:* ``False`` adds a number to the file name to prevent overwriting

    legendKwargs : dict
        a *dict* containing any or all legend kwargs.  These include ``'title'``, ``'loc'``, ``'fontsize'``, ``'bbox_to_anchor'``, ``'borderaxespad'``, and ``'handlelength'``.

    rcParams : dict
        a *dict* containing any or all matplotlib rcParams.  To see all options, execute ``import matplotlib; print(matplotlib.rcParams)`` in Python.  Any options in this *dict* will be used for this current figure and then returned to their prior settings.

    title : str
        the axis title
    
    xlabel : str
        label for x-axis
    
    ylabel : str
        label for y-axis

    
    Returns
    -------
    LFPSpectrogramPlot : *matplotlib figure*
        By default, returns the *figure*.  If ``returnPlotter`` is ``True``, instead returns the NetPyNE MetaFig.
        
    """

    
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
            pop=pop,
            NFFT=NFFT, 
            noverlap=noverlap, 
            nperseg=nperseg, 
            minFreq=minFreq, 
            maxFreq=maxFreq, 
            stepFreq=stepFreq, 
            smooth=smooth, 
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
        metaFig = MetaFigure(kind='LFPSpectrogram', subplots=len(names), rcParams=rcParams, **kwargs)

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
        title = 'Electrode ' + name
        if pop:
            title += ' - Population: ' + pop
        axisArgs['title'] = title
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
                plotaxis = metaFig.ax[index]
            else:
                plotaxis = metaFig.ax
        
        imagePlotter = ImagePlotter(data=imageData, kind='spect', axis=plotaxis, **axisArgs, **kwargs)
        spectPlot = imagePlotter.plot(**axisArgs, **kwargs)

    suptitle = {'t':'LFP Spectrogram'}

    if axis is None:
        metaFig.finishFig(suptitle=suptitle, **kwargs)
        return metaFig.fig
    else:
        return plt.gcf()


