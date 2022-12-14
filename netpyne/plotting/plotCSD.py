# PLOTTING CSD 

from ..analysis.utils import exception
import numpy as np
import scipy
import matplotlib
from matplotlib import pyplot as plt 


@exception
def plotCSD(
    CSDData=None,
    LFPData=None,
    pop=None,
    timeRange=None,
    dt=None,
    sampr=None,
    spacing_um=None,
    norm=True,
    fontSize=12,
    ymax=None,
    figSize=(8,8),
    overlay=None,
    hlines=False,
    layerBounds=None,
    stimTimes=None,
    saveFig=True, 
    dpi=200, 
    showFig=False,
    smooth=True,
    **kwargs): 
    """
    Function to plot CSD values extracted from simulated LFP data 
      
    Parameters
    ----------
    CSDData : list or array
        CSDData for plotting.
        **Default:** ``None`` 

    LFPData : list or numpy array 
        LFP data provided by user (mV).  Each element of the list/array must be a list/array containing LFP data for an electrode. 
        **Default:** ``None`` pulls the data from the current NetPyNE sim object.
    
    pop : str
        Plot CSD data from a specific cell population
        **Default:** ``None``plots overall CSD data

    timeRange : list
        Time range to plot [start, stop].
        **Default:** ``None`` plots entire time range

    dt : float
        Time between recording points (ms). 
        **Default:** ``None`` uses ``sim.cfg.recordStep`` from the current NetPyNE sim object.

    sampr : float
        Sampling rate for data recording (Hz).  
        **Default:** ``None`` uses ``1.0/sim.cfg.recordStep`` from the current NetPyNE sim object. 
      
    spacing_um : float
        Electrode contact spacing in units of microns.
        **Default:** ``None`` pulls the information from the current NetPyNE sim object.  If the data is empirical, defaults to ``100`` (microns).

    fontSize : int
        **Default:** 12 

    ymax : float
        The upper y-limit.
        **Default:** ``None`` 

    figSize: tuple 
        Size of CSD plot figure 
        **Default:** (8,8)

    overlay : str
        Option to include LFP data overlaid on CSD color map plot. 
        **Default:** ``None`` provides no overlay 
        OPTIONS are 'LFP' or 'CSD'

    hlines : bool
        Option to include horizontal lines on plot to indicate electrode positions. 
        **Default:** ``False`` 

    layerBounds : dict  #### <-- SHOULD FIX THIS SO L1 IS A LIST 
        Dictionary containing layer labels as keys, and layer boundaries as values, e.g. {'L1':100, 'L2': 160, 'L3': 950, 'L4': 1250, 'L5A': 1334, 'L5B': 1550, 'L6': 2000}
        **Default:** ``None``

    stimTimes : list OR float / int 
        Time(s) when stimulus is applied (ms)
        **Default:** ``None`` does not add anything to plot
        **Options:** Adds vertical dashed line(s) to the plot at stimulus onset(s) 

    saveFig : bool or str
        Whether and where to save the figure. 
        **Default:** ``True`` autosaves the figure.
        **Options:** ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.png'``, ``'.jpg'``, ``'.eps'``, and ``'.tiff'``.

    dpi : int
        Resolution for saving figures. 
        **Default:** 200 

    showFig : bool
        Whether to show the figure. 
        **Default:** ``True``

    smooth : bool 
        Whether or not to plot the smoothed interpoloation
        **Default:** ``True``

    """


    # If there is no input data, get the data from the NetPyNE sim object
    if CSDData is None:
        if 'sim' not in kwargs:
            from .. import sim
        else:
            sim = kwargs['sim']

        CSDData, LFPData, sampr, spacing_um, dt = sim.analysis.prepareCSD(
            sim=sim,
            pop=pop,
            dt=dt, 
            sampr=sampr,
            spacing_um=spacing_um,
            norm=True,
            getAllData=True,
            **kwargs)

    if timeRange is None:
        timeRange = [0,sim.cfg.duration] 
    else:
        LFPData = np.array(LFPData)[int(timeRange[0]/dt):int(timeRange[1]/dt),:]  # NOTE: THIS SHOULD ALREADY BE AN ARRAY
        CSDData = CSDData[:,int(timeRange[0]/dt):int(timeRange[1]/dt)]


    tt = np.arange(timeRange[0], timeRange[1], dt)


    #####################################################
    print('Plotting CSD... ')

    # PLOTTING 
    X = np.arange(timeRange[0], timeRange[1], dt)  # X == tt 
    Y = np.arange(CSDData.shape[0])

    # interpolation
    CSD_spline=scipy.interpolate.RectBivariateSpline(Y, X, CSDData)
    Y_plot = np.linspace(0,CSDData.shape[0],num=1000) 
    Z = CSD_spline(Y_plot, X)


    # plotting options
    plt.rcParams.update({'font.size': fontSize})
    xmin = int(X[0])
    xmax = int(X[-1]) + 1
    ymin = 0
    if ymax is None:
        ymax = sim.cfg.recordLFP[-1][1] + spacing_um 
    extent_xy = [xmin, xmax, ymax, ymin]

    # set up figure 
    fig = plt.figure(figsize=figSize) 

    # create plots w/ common axis labels and tick marks
    axs = []
    numplots = 1
    gs_outer = matplotlib.gridspec.GridSpec(1,1)


    for i in range(numplots):
        axs.append(plt.Subplot(fig,gs_outer[i*2:i*2+2]))
        fig.add_subplot(axs[i])
        axs[i].set_xlabel('Time (ms)',fontsize=fontSize)
        axs[i].tick_params(axis='y', which='major', labelsize=fontSize)
        axs[i].tick_params(axis='x', which='major', labelsize=fontSize)

    # plot interpolated CSD color map 
    if smooth:
       Z = scipy.ndimage.filters.gaussian_filter(Z, sigma = 5, mode='nearest')

    spline=axs[0].imshow(Z, extent=extent_xy, interpolation='none', aspect='auto', origin='upper', cmap='jet_r', alpha=0.9) 
    axs[0].set_ylabel('Contact depth (um)', fontsize=fontSize)


    # OVERLAY DATA ('LFP', 'CSD', or None) & Set title of plot 
    if pop is None:
        csdTitle = 'Current Source Density (CSD)'
    else:
        csdTitle = 'Current Source Density (CSD) for ' + str(pop) + ' Population'

    if overlay is None:
        print('No overlay')
        axs[0].set_title(csdTitle, fontsize=fontSize)

    elif overlay is 'CSD' or overlay is 'LFP':
        nrow = LFPData.shape[1]
        gs_inner = matplotlib.gridspec.GridSpecFromSubplotSpec(nrow, 1, subplot_spec=gs_outer[0:2], wspace=0.0, hspace=0.0)
        subaxs = []

        if overlay == 'CSD': 
            print('Overlaying with CSD time series data')
            axs[0].set_title(csdTitle, fontsize=fontSize)  
            legendLabel=True
            for chan in range(nrow):
                subaxs.append(plt.Subplot(fig, gs_inner[chan], frameon=False))
                fig.add_subplot(subaxs[chan])
                subaxs[chan].margins(0.0,0.01)
                subaxs[chan].get_xaxis().set_visible(False)
                subaxs[chan].get_yaxis().set_visible(False)
                subaxs[chan].plot(X, CSDData[chan,:], color='green', linewidth=0.3, label='CSD timeSeries')
                if legendLabel:
                    subaxs[chan].legend(loc='upper right', fontsize='small')
                    legendLabel=False

        elif overlay == 'LFP':
            print('Overlaying with LFP time series data')
            axs[0].set_title(csdTitle, fontsize=fontSize) 
            legendLabel=True
            for chan in range(nrow):
                subaxs.append(plt.Subplot(fig, gs_inner[chan], frameon=False))
                fig.add_subplot(subaxs[chan])
                subaxs[chan].margins(0.0,0.01)
                subaxs[chan].get_xaxis().set_visible(False)
                subaxs[chan].get_yaxis().set_visible(False)
                subaxs[chan].plot(X, LFPData[:,chan], color='gray', linewidth=0.3, label='LFP timeSeries')
                if legendLabel:
                    subaxs[chan].legend(loc='upper right', fontsize='small')
                    legendLabel=False

    else:
        print('Invalid option specified for overlay argument -- no data overlaid')
        axs[0].set_title('Current Source Density (CSD)', fontsize=fontSize)


    # add horizontal lines at electrode locations
    if hlines:
        for i in range(len(sim.cfg.recordLFP)):
            axs[0].hlines(sim.cfg.recordLFP[i][1], xmin, xmax, colors='pink', linewidth=1, linestyles='dashed')



    #if layerBounds:  
    if layerBounds is None:
        print('No layer boundaries given -- will not overlay layer boundaries on CSD plot')
    else:
        layerKeys = []
        for i in layerBounds.keys():
            axs[0].hlines(layerBounds[i][1], xmin, xmax, colors='black', linewidth=1, linestyles='dotted') 
            layerKeys.append(i) # makes a list with names of each layer, as specified in layerBounds dict argument 

        for n in range(len(layerKeys)): # label the horizontal layer lines with the proper layer label 
            if n == 0:
                axs[0].text(xmax+5, layerBounds[layerKeys[n]][1]/2, layerKeys[n], color='black', fontsize=fontSize)
            else:
                axs[0].text(xmax+5, (layerBounds[layerKeys[n]][1] + layerBounds[layerKeys[n-1]][1])/2, layerKeys[n], color='black', fontsize=fontSize, verticalalignment='center')


    # set vertical line(s) at stimulus onset(s)
    if type(stimTimes) is int or type(stimTimes) is float:
        axs[0].vlines(stimTimes, ymin, ymax, colors='red', linewidth=1, linestyles='dashed')
    elif type(stimTimes) is list:
        for stimTime in stimTimes:
            axs[0].vlines(stimTime, ymin, ymax, colors='red', linewidth=1, linestyles='dashed')



    # save figure 
    if saveFig:
        if isinstance(saveFig, str):
            filename = saveFig
        else:
            filename = str(sim.cfg.filename) + '_CSD.png'
        try:
            plt.savefig(filename, dpi=dpi)
        except:
            plt.savefig('CSD_fig.png', dpi=dpi)

    # display figure
    if showFig:
        plt.show()

