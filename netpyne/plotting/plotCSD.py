# PLOTTING CSD 

from ..analysis.utils import exception
import numpy as np
import scipy
import matplotlib
from matplotlib import pyplot as plt 




### copied from netpyne/netpyne/analysis/csd_legacy.py
@exception
def plotCSD(
    CSDData=None,
    LFPData=None,
    pop=None,   ### kwargs...? 
    timeRange=None,
    dt=None,
    sampr=None,
    spacing_um=None,
    fontSize=12,
    ymax=None,
    figSize=(8,8),
    overlay=None,
    hlines=False,
    layerLines=False,
    layerBounds=None,
    stimTimes=None,
    saveFig=True, 
    dpi=200, 
    showFig=True,
    smooth=True, #### SMOOTH ISN'T IN USE RIGHT NOW 
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




    stim_start_time : float 
        Time when stimulus is applied (ms). 
        **Default:** ``None`` does not add anything to plot. 
        **Options:** a float adds a vertical dashed line to the plot at stimulus onset. 

    ymax : float
        The upper y-limit.
        **Default:** ``None`` 

    overlay : str
        Option to include LFP data overlaid on CSD color map plot. 
        **Default:** ``None`` provides no overlay 
        OPTIONS are 'LFP' or 'CSD'

    hlines : bool
        Option to include horizontal lines on plot to indicate electrode positions. 
        **Default:** ``False`` 

    layerLines : bool 
        Whether to plot horizontal lines over CSD plot at layer boundaries. 
        **Default:** ``False`` 

    layerBounds : dict
        Dictionary containing layer labels as keys, and layer boundaries as values, e.g. {'L1':100, 'L2': 160, 'L3': 950, 'L4': 1250, 'L5A': 1334, 'L5B': 1550, 'L6': 2000}
        **Default:** ``None``

    saveFig : bool or str
        Whether and where to save the figure. 
        **Default:** ``True`` autosaves the figure.
        **Options:** ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.png'``, ``'.jpg'``, ``'.eps'``, and ``'.tiff'``.

    showFig : bool
        Whether to show the figure. 
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
            timeRange=timeRange,   ### timeRange here or...? 
            dt=dt, 
            sampr=sampr,
            spacing_um=spacing_um,
            getAllData=True,
            **kwargs)

    print('CSDData extracted!')
    # print('CSDData shape: ' + str(CSDData.shape))
    # print('LFPData shape: ' + str(LFPData.shape))
    

    if timeRange is None:
        timeRange = [0,sim.cfg.duration] 
    else:
        LFPData = np.array(LFPData)[int(timeRange[0]/dt):int(timeRange[1]/dt),:]
        CSDData = CSDData[:,int(timeRange[0]/dt):int(timeRange[1]/dt)]

    tt = np.arange(timeRange[0], timeRange[1], dt)


    #####################################################
    print('Plotting CSD... ')

    # PLOTTING 
    X = np.arange(timeRange[0], timeRange[1], dt)  # same as tt above 
    Y = np.arange(CSDData.shape[0])

    # interpolation
    CSD_spline=scipy.interpolate.RectBivariateSpline(Y, X, CSDData)
    Y_plot = np.linspace(0,CSDData.shape[0],num=1000) 
    Z = CSD_spline(Y_plot, X)


    # plotting options
    plt.rcParams.update({'font.size': fontSize})
    xmin = int(X[0])
    xmax = int(X[-1]) + 1  #int(sim.allSimData['t'][-1])
    ymin = 0
    if ymax is None:
        ymax = sim.cfg.recordLFP[-1][1] + spacing_um 
    extent_xy = [xmin, xmax, ymax, ymin]

    # set up figure 
    fig = plt.figure(figsize=figSize) 

    # create plots w/ common axis labels and tick marks
    axs = []
    numplots = 1
    gs_outer = matplotlib.gridspec.GridSpec(1,1)                #(2, 2, wspace=0.4, hspace=0.2, height_ratios=[20, 1])


    for i in range(numplots):
        axs.append(plt.Subplot(fig,gs_outer[i*2:i*2+2]))
        fig.add_subplot(axs[i])
        axs[i].set_xlabel('Time (ms)',fontsize=fontSize)
        axs[i].tick_params(axis='y', which='major', labelsize=fontSize)
        axs[i].tick_params(axis='x', which='major', labelsize=fontSize)

    ## plot interpolated CSD color map 
    #if smooth:
    #    Z = scipy.ndimage.filters.gaussian_filter(Z, sigma = 5, mode='nearest')#smooth, mode='nearest')

    spline=axs[0].imshow(Z, extent=extent_xy, interpolation='none', aspect='auto', origin='upper', cmap='jet_r', alpha=0.9) 
    axs[0].set_ylabel('Contact depth (um)', fontsize=fontSize)


    # OVERLAY DATA ('LFP', 'CSD', or None) & Set title of plot 
    if overlay is None:
        print('No overlay')
        axs[0].set_title('Current Source Density (CSD)', fontsize=fontSize)

    elif overlay is 'CSD' or overlay is 'LFP':
        nrow = LFPData.shape[1]
        gs_inner = matplotlib.gridspec.GridSpecFromSubplotSpec(nrow, 1, subplot_spec=gs_outer[0:2], wspace=0.0, hspace=0.0)
        subaxs = []

        if overlay == 'CSD':
            axs[0].set_title('CSD with time series overlay', fontsize=fontSize) 
            for chan in range(nrow):
                subaxs.append(plt.Subplot(fig, gs_inner[chan], frameon=False))
                fig.add_subplot(subaxs[chan])
                subaxs[chan].margins(0.0,0.01)
                subaxs[chan].get_xaxis().set_visible(False)
                subaxs[chan].get_yaxis().set_visible(False)
                subaxs[chan].plot(X, CSDData[chan,:], color='green', linewidth=0.3) # 'blue'

        elif overlay == 'LFP':
            axs[0].set_title('CSD with LFP overlay', fontsize=fontSize) 
            for chan in range(nrow):
                subaxs.append(plt.Subplot(fig, gs_inner[chan], frameon=False))
                fig.add_subplot(subaxs[chan])
                subaxs[chan].margins(0.0,0.01)
                subaxs[chan].get_xaxis().set_visible(False)
                subaxs[chan].get_yaxis().set_visible(False)
                subaxs[chan].plot(X, LFPData[:,chan], color='gray', linewidth=0.3)

    else:
        print('Invalid option specified for overlay argument -- no data overlaid')
        axs[0].set_title('Current Source Density (CSD)', fontsize=fontSize)


    # add horizontal lines at electrode locations
    if hlines:
        for i in range(len(sim.cfg.recordLFP)):
            axs[0].hlines(sim.cfg.recordLFP[i][1], xmin, xmax, colors='pink', linewidth=1, linestyles='dashed')



    if layerLines:  
        if layerBounds is None:
            print('No layer boundaries given -- will not overlay layer boundaries on CSD plot')
        else:
            layerKeys = []
            for i in layerBounds.keys():
                axs[0].hlines(layerBounds[i], xmin, xmax, colors='black', linewidth=1, linestyles='dotted') 
                layerKeys.append(i) # makes a list with names of each layer, as specified in layerBounds dict argument 

            for n in range(len(layerKeys)): # label the horizontal layer lines with the proper layer label 
                if n == 0:
                    axs[0].text(xmax+5, layerBounds[layerKeys[n]]/2, layerKeys[n], color='black', fontsize=fontSize)
                else:
                    axs[0].text(xmax+5, (layerBounds[layerKeys[n]] + layerBounds[layerKeys[n-1]])/2, layerKeys[n], color='black', fontsize=fontSize, verticalalignment='center')


    # set vertical line(s) at stimulus onset(s)
    if type(stimTimes) is int or type(stimTimes) is float:
        axs[0].vlines(stimTimes, ymin, ymax, colors='red', linewidth=1, linestyles='dashed')
    elif type(stimTimes) is list:
        for stimTime in stimTimes:
            axs[0].vlines(stimTime, ymin, ymax, colors='red', linewidth=1, linestyles='dashed')



    # save figure  ### NOTE: Make this more elaborate? 
    if saveFig:
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename + '_CSD.png'
        try:
            plt.savefig(filename, dpi=dpi)
        except:
            plt.savefig('CSD_fig.png', dpi=dpi)

    # display figure
    if showFig:
        plt.show()



### copied from netpyne/netpyne/analysis/csd_legacy.py
@exception
def plotCSD_LEGACY(CSD_data=None, LFP_input_data=None, overlay=None, timeRange=None, sampr=None, stim_start_time=None, spacing_um=None, ymax=None, dt=None, hlines=False, layerLines=False, layerBounds=None, smooth=True, fontSize=12, figSize=(8,8),dpi=200, saveFig=True, showFig=True): 
    """
    Function to plot CSD values extracted from simulated LFP data 
      
    Parameters
    ----------
    CSD_data : list or array
        CSD_data for plotting.
        **Default:** ``None`` 

    LFP_input_data : list or numpy array 
        LFP data provided by user (mV).  Each element of the list/array must be a list/array containing LFP data for an electrode. 
        **Default:** ``None`` pulls the data from the current NetPyNE sim object.


    overlay : str
        Option to include LFP data overlaid on CSD color map plot. 
        **Default:** ``None`` provides no overlay 
        OPTIONS are 'LFP' or 'CSD'

    timeRange : list
        Time range to plot [start, stop].
        **Default:** ``None`` plots entire time range

    sampr : float
        Sampling rate for data recording (Hz).  
        **Default:** ``None`` uses ``1.0/sim.cfg.recordStep`` from the current NetPyNE sim object. 
      
    stim_start_time : float 
        Time when stimulus is applied (ms). 
        **Default:** ``None`` does not add anything to plot. 
        **Options:** a float adds a vertical dashed line to the plot at stimulus onset. 

    spacing_um : float
        Electrode contact spacing in units of microns.
        **Default:** ``None`` pulls the information from the current NetPyNE sim object.  If the data is empirical, defaults to ``100`` (microns).

    ymax : float
        The upper y-limit.
        **Default:** ``None`` 

    dt : float
        Time between recording points (ms). 
        **Default:** ``None`` uses ``sim.cfg.recordStep`` from the current NetPyNE sim object.

    hlines : bool
        Option to include horizontal lines on plot to indicate electrode positions. 
        **Default:** ``False`` 

    layerLines : bool 
        Whether to plot horizontal lines over CSD plot at layer boundaries. 
        **Default:** ``False`` 

    layerBounds : dict
        Dictionary containing layer labels as keys, and layer boundaries as values, e.g. {'L1':100, 'L2': 160, 'L3': 950, 'L4': 1250, 'L5A': 1334, 'L5B': 1550, 'L6': 2000}
        **Default:** ``None``

    saveFig : bool or str
        Whether and where to save the figure. 
        **Default:** ``True`` autosaves the figure.
        **Options:** ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.png'``, ``'.jpg'``, ``'.eps'``, and ``'.tiff'``.

    showFig : bool
        Whether to show the figure. 
        **Default:** ``True``

    """

    print('Plotting CSD... ')
  
    # DEFAULT -- CONDITION 1 : GET CSD DATA FROM SIM
    if CSD_data is None:
    
        from .. import sim
        LFP_data, CSD_data, sampr, spacing_um, dt = getCSD(getAllData=True) #getCSD(sampr=sampr, spacing_um=spacing_um, dt=dt, getAllData=True)

        if timeRange is None:
            timeRange = [0,sim.cfg.duration] 

        tt = np.arange(timeRange[0], timeRange[1], dt)

        ymax = sim.cfg.recordLFP[-1][1] + spacing_um 

        LFP_data = np.array(LFP_data)[int(timeRange[0]/dt):int(timeRange[1]/dt),:]
        CSD_data = CSD_data[:,int(timeRange[0]/dt):int(timeRange[1]/dt)]

        CSD_data_noBandpass = sim.allSimData['CSD']['CSD_data_noBandpass'][:,int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep)]
        #CSD_data_noBandpass = CSD_data_noBandpass[:,int(timeRange[0]/dt):int(timeRange[1]/dt)]


        ### The problem with this setup is that it defaults to whatever was saved in .pkl !!
        # sim_data_categories = sim.allSimData.keys()
        
        # if 'CSD' in sim_data_categories:  

        #     if timeRange is None:
        #         timeRange = [0,sim.cfg.duration] 

        #     dt = sim.cfg.recordStep
        #     tt = np.arange(timeRange[0],timeRange[1],dt)

        #     spacing_um = sim.allSimData['CSD']['spacing_um']
        #     #spacing_mm = spacing_um/1000 

        #     ymax = sim.cfg.recordLFP[-1][1] + spacing_um

        #     # get LFP data
        #     LFP_data = np.array(sim.allSimData['LFP'])[int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep),:]

        #     # get CSD data
        #     CSD_data = sim.allSimData['CSD']['CSD_data'][:,int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep)]  

        #     # noBandpass trial
        #     CSD_data_noBandpass = sim.allSimData['CSD']['CSD_data_noBandpass'][:,int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep)]
      
        # else:
        #     raise Exception('No CSD data in sim.')


    # CONDITION 2 : ARBITRARY CSD DATA 
    elif CSD_data is not None:
        if timeRange is None:
            print('MUST PROVIDE TIME RANGE in ms')
        else:
            print('timeRange = ' + str(timeRange))

        if dt is None:
            print('MUST PROVIDE dt in ms')
        else:
            print('dt = ' + str(dt)) # batch0['simConfig']['recordStep']

        if spacing_um is None:
            print('MUST PROVIDE SPACING BETWEEN ELECTRODES in MICRONS')
        else:
            print('spacing_um = ' + str(spacing_um))

        if ymax is None:
            print('MUST PROVIDE YMAX (MAX DEPTH) in MICRONS')
        else:
            print('ymax = ' + str(ymax))

        tt = np.arange(timeRange[0], timeRange[1], dt)
        LFP_data = np.array(LFP_input_data)[int(timeRange[0]/dt):int(timeRange[1]/dt),:]


    # PLOTTING 
    X = np.arange(timeRange[0], timeRange[1], dt)
    Y = np.arange(CSD_data.shape[0])

    # interpolation
    CSD_spline=scipy.interpolate.RectBivariateSpline(Y, X, CSD_data)
    Y_plot = np.linspace(0,CSD_data.shape[0],num=1000) 
    Z = CSD_spline(Y_plot, X)

    # plotting options
    plt.rcParams.update({'font.size': fontSize})
    xmin = int(X[0])
    xmax = int(X[-1]) + 1  #int(sim.allSimData['t'][-1])
    ymin = 0
    extent_xy = [xmin, xmax, ymax, ymin]

    # set up figure 
    fig = plt.figure(figsize=figSize) 

    # create plots w/ common axis labels and tick marks
    axs = []
    numplots = 1
    gs_outer = matplotlib.gridspec.GridSpec(1,1)#(2, 2, figure=fig)#, wspace=0.4, hspace=0.2, height_ratios=[20, 1])

    for i in range(numplots):
        axs.append(plt.Subplot(fig,gs_outer[i*2:i*2+2]))
        fig.add_subplot(axs[i])
        axs[i].set_xlabel('Time (ms)',fontsize=fontSize)
        axs[i].tick_params(axis='y', which='major', labelsize=fontSize)
        axs[i].tick_params(axis='x', which='major', labelsize=fontSize)

    ## plot interpolated CSD color map 
    #if smooth:
    #    Z = scipy.ndimage.filters.gaussian_filter(Z, sigma = 5, mode='nearest')#smooth, mode='nearest')

    spline=axs[0].imshow(Z, extent=extent_xy, interpolation='none', aspect='auto', origin='upper', cmap='jet_r', alpha=0.9) 
    axs[0].set_ylabel('Contact depth (um)', fontsize=fontSize)


    # OVERLAY DATA ('LFP', 'CSD', or None) & Set title of plot 
    if overlay is None:
        print('No data being overlaid')
        axs[0].set_title('Current Source Density (CSD)', fontsize=fontSize)

    elif overlay is 'CSD' or overlay is 'LFP':
        nrow = LFP_data.shape[1]
        gs_inner = matplotlib.gridspec.GridSpecFromSubplotSpec(nrow, 1, subplot_spec=gs_outer[0:2], wspace=0.0, hspace=0.0)
        subaxs = []

        if overlay == 'CSD':
            axs[0].set_title('CSD with time series overlay', fontsize=fontSize) 
            for chan in range(nrow):
                subaxs.append(plt.Subplot(fig, gs_inner[chan], frameon=False))
                fig.add_subplot(subaxs[chan])
                subaxs[chan].margins(0.0,0.01)
                subaxs[chan].get_xaxis().set_visible(False)
                subaxs[chan].get_yaxis().set_visible(False)
                subaxs[chan].plot(X, CSD_data[chan,:], color='green', linewidth=0.3) # 'blue'

        elif overlay == 'LFP':
            axs[0].set_title('CSD with LFP overlay', fontsize=fontSize) 
            for chan in range(nrow):
                subaxs.append(plt.Subplot(fig, gs_inner[chan], frameon=False))
                fig.add_subplot(subaxs[chan])
                subaxs[chan].margins(0.0,0.01)
                subaxs[chan].get_xaxis().set_visible(False)
                subaxs[chan].get_yaxis().set_visible(False)
                subaxs[chan].plot(X, LFP_data[:,chan], color='gray', linewidth=0.3)

    else:
        print('Invalid option specified for overlay argument -- no data overlaid')
        axs[0].set_title('Current Source Density (CSD)', fontsize=fontSize)



    # add horizontal lines at electrode locations
    if hlines:
        for i in range(len(sim.cfg.recordLFP)):
            axs[0].hlines(sim.cfg.recordLFP[i][1], xmin, xmax, colors='pink', linewidth=1, linestyles='dashed')

    if layerLines:  
        if layerBounds is None:
            print('No layer boundaries given -- will not overlay layer boundaries on CSD plot')
        else:
            layerKeys = []
            for i in layerBounds.keys():
                axs[0].hlines(layerBounds[i], xmin, xmax, colors='black', linewidth=1, linestyles='dotted') 
                layerKeys.append(i) # makes a list with names of each layer, as specified in layerBounds dict argument 

            for n in range(len(layerKeys)): # label the horizontal layer lines with the proper layer label 
                if n == 0:
                    axs[0].text(xmax+5, layerBounds[layerKeys[n]]/2, layerKeys[n], color='black', fontsize=fontSize)
                else:
                    axs[0].text(xmax+5, (layerBounds[layerKeys[n]] + layerBounds[layerKeys[n-1]])/2, layerKeys[n], color='black', fontsize=fontSize, verticalalignment='center')

    # set vertical line at stimulus onset
    if type(stim_start_time) is int or type(stim_start_time) is float:
        axs[0].vlines(stim_start_time, ymin, ymax, colors='red', linewidth=1, linestyles='dashed')


    # save figure
    if saveFig:
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename + '_CSD.png'
        try:
            plt.savefig(filename, dpi=dpi)
        except:
            plt.savefig('CSD_fig.png', dpi=dpi)

    # display figure
    if showFig:
        plt.show()