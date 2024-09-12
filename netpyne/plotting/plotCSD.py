# PLOTTING CSD

from netpyne import __gui__
if __gui__:
    import matplotlib
    from matplotlib import pyplot as plt

from ..analysis.utils import exception, _showFigure
import numpy as np
import scipy

def getPaddedCSD (CSDData, pad):
  # pad the first/last row of CSDData by replication (to avoid edge artifacts when drawing colors plots)
  npcsd = []
  for i in range(pad): npcsd.append(CSDData[0,:])
  for i in range(CSDData.shape[0]): npcsd.append(CSDData[i,:])
  for i in range(pad): npcsd.append(CSDData[-1,:])
  npcsd=np.array(npcsd)
  return npcsd

@exception
def plotCSD(
    CSDData=None,
    LFPData=None,
    pop=None,
    timeRange=None,
    dt=None,
    sampr=None,
    spacing_um=None,
    fontSize=12,
    ymax=None,
    figSize=(8, 8),
    overlay=None,
    hlines=False,
    layerBounds=None,
    stimTimes=None,
    saveFig=True,
    dpi=200,
    showFig=False,
    smooth=True,
    colorbar=True,
    pad=1,
    **kwargs
):
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

    colorbar : bool
        Whether or not to plot the colorbar
        **Default:** ``True``

    pad : int
        Amount to pad CSDData on top/bottom for more accurate interpolation at edges
        **Default:** ``1``

    """

    # If there is no input data, get the data from the NetPyNE sim object
    if CSDData is None:
        if 'sim' not in kwargs:
            from .. import sim
        else:
            sim = kwargs['sim']

        CSDData, LFPData, sampr, spacing_um, dt = sim.analysis.prepareCSD(
            sim=sim,
            timeRange=timeRange,
            pop=pop,
            dt=dt,
            sampr=sampr,
            spacing_um=spacing_um,
            getAllData=True,
            **kwargs)
    else:
        pass # TODO: ensure time slicing works properly in case CSDData is passed as an argument

    npcsd = CSDData
    if pad > 0: npcsd = getPaddedCSD(CSDData, pad) # apply padding (replicate first,last rows)

    if timeRange is None:
        timeRange = [0, sim.cfg.duration]

    #####################################################
    print('Plotting CSD... ')

    # PLOTTING
    X = np.arange(timeRange[0], timeRange[1], dt)  # X == tt
    Y = np.arange(npcsd.shape[0])

    # interpolation
    fctr = int(1000 / CSDData.shape[0])
    CSD_spline = scipy.interpolate.RectBivariateSpline(Y, X, npcsd)
    Y_plot = np.linspace(-pad, npcsd.shape[0] + pad, num=int(1000*npcsd.shape[0]/CSDData.shape[0]))    
    Z = CSD_spline(Y_plot, X)[pad*fctr:pad*fctr+1000,:]

    # plotting options
    plt.rcParams.update({'font.size': fontSize})
    xmin = int(X[0])
    xmax = int(X[-1]) + 1
    ymin = 0
    if ymax is None:
        ymax = sim.cfg.recordLFP[-1][1] + spacing_um + pad
    extent_xy = [xmin, xmax, ymax, ymin]

    # set up figure
    fig = plt.figure(figsize=figSize)

    # create plots w/ common axis labels and tick marks
    axs = []
    if colorbar:
        numplots = 2
        gs_outer = matplotlib.gridspec.GridSpec(2, 1, height_ratios=[20,3])
    else:
        numplots = 1
        gs_outer = matplotlib.gridspec.GridSpec(1, 1)


    for i in range(numplots):
        if colorbar:
            axs.append(plt.Subplot(fig, gs_outer[i, 0:2]))#i * 2 : i * 2 + 2]))
            fig.add_subplot(axs[i])
        else:
            axs.append(plt.Subplot(fig, gs_outer[i * 2 : i * 2 + 2]))
            fig.add_subplot(axs[i])
            axs[i].set_xlabel('Time (ms)', fontsize=fontSize)
            axs[i].tick_params(axis='y', which='major', labelsize=fontSize)
            axs[i].tick_params(axis='x', which='major', labelsize=fontSize)


    # plot interpolated CSD color map
    if smooth:
        Z = scipy.ndimage.filters.gaussian_filter(Z, sigma=smooth, mode='nearest')

    spline = axs[0].imshow(
        Z, extent=extent_xy, interpolation='none', aspect='auto', origin='upper', cmap='jet_r', alpha=0.9
    )
    axs[0].set_ylabel('Contact depth (um)', fontsize=fontSize)


    # OVERLAY DATA ('LFP', 'CSD', or None) & Set title of plot
    if pop is None:
        csdTitle = 'Current Source Density (CSD)'
    else:
        csdTitle = 'Current Source Density (CSD) for ' + str(pop) + ' Population'

    if overlay is None:
        print('No overlay')
        axs[0].set_title(csdTitle, fontsize=fontSize)

    elif overlay == 'CSD' or overlay == 'LFP':
        nrow = LFPData.shape[1]
        if colorbar:
            gs_inner = matplotlib.gridspec.GridSpecFromSubplotSpec(
                nrow, 1, subplot_spec=gs_outer[0, 0:2], wspace=0.0, hspace=0.0
            )
            subaxs = []
        else:
            gs_inner = matplotlib.gridspec.GridSpecFromSubplotSpec(
                nrow, 1, subplot_spec=gs_outer[0:2], wspace=0.0, hspace=0.0
            )
            subaxs = []

        if overlay == 'CSD':
            print('Overlaying with CSD time series data')
            axs[0].set_title(csdTitle, fontsize=fontSize)
            legendLabel = True
            for chan in range(nrow):
                subaxs.append(plt.Subplot(fig, gs_inner[chan], frameon=False))
                fig.add_subplot(subaxs[chan])
                subaxs[chan].margins(0.0, 0.01)
                subaxs[chan].get_xaxis().set_visible(False)
                subaxs[chan].get_yaxis().set_visible(False)
                subaxs[chan].plot(X, npcsd[pad+chan, :], color='green', linewidth=0.3, label='CSD time series')
                if legendLabel:
                    subaxs[chan].legend(loc='upper right', fontsize=fontSize)
                    legendLabel = False

        elif overlay == 'LFP':
            print('Overlaying with LFP time series data')
            axs[0].set_title(csdTitle, fontsize=fontSize)
            legendLabel = True
            for chan in range(nrow):
                subaxs.append(plt.Subplot(fig, gs_inner[chan], frameon=False))
                fig.add_subplot(subaxs[chan])
                subaxs[chan].margins(0.0, 0.01)
                subaxs[chan].get_xaxis().set_visible(False)
                subaxs[chan].get_yaxis().set_visible(False)
                subaxs[chan].plot(X, LFPData[:, chan], color='gray', linewidth=0.3, label='LFP time series')
                if legendLabel:
                    subaxs[chan].legend(loc='upper right', fontsize=fontSize)
                    legendLabel = False

    else:
        print(f'Invalid option specified for overlay argument ({overlay}) -- no data overlaid')
        axs[0].set_title('Current Source Density (CSD)', fontsize=fontSize)

    # add horizontal lines at electrode locations
    if hlines:
        for i in range(len(sim.cfg.recordLFP)):
            axs[0].hlines(sim.cfg.recordLFP[i][1], xmin, xmax, colors='pink', linewidth=1, linestyles='dashed')


    ## colorbar at the bottom using unsmoothed data for values
    if colorbar:
        ax_bottom = plt.subplot(gs_outer[1,0:1])   # gs_outer[1,0:1]
        ax_bottom.axis('off')
        cbar_min = round(np.min(Z)) 
        cbar_max = round(np.max(Z)) 
        cbar_ticks = np.linspace(cbar_min, cbar_max, 3, endpoint=True)
        cbar = plt.colorbar(spline, ax=ax_bottom, ticks=cbar_ticks, orientation='horizontal', shrink=1.0)
        cbar.set_label(label=r'CSD (mV/mm$^2$)', fontsize=fontSize) # ,use_gridspec=True,
        cbar.ax.tick_params(labelsize=fontSize)

    # if layerBounds:
    if layerBounds is None:
        print('No layer boundaries given -- will not overlay layer boundaries on CSD plot')
    else:
        layerKeys = []
        for i in layerBounds.keys():
            axs[0].hlines(layerBounds[i][1], xmin, xmax, colors='black', linewidth=1, linestyles='dotted')
            layerKeys.append(i)  # makes a list with names of each layer, as specified in layerBounds dict argument

        for n in range(len(layerKeys)):  # label the horizontal layer lines with the proper layer label
            if n == 0:
                axs[0].text(xmax + 5, layerBounds[layerKeys[n]][1] / 2, layerKeys[n], color='black', fontsize=fontSize)
            else:
                axs[0].text(
                    xmax + 5,
                    (layerBounds[layerKeys[n]][1] + layerBounds[layerKeys[n - 1]][1]) / 2,
                    layerKeys[n],
                    color='black',
                    fontsize=fontSize,
                    verticalalignment='center',
                )



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
        _showFigure()
        #plt.show()

    return fig, axs
