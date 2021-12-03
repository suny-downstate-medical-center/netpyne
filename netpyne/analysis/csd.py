"""
Module with functions to extract and plot CSD info from LFP data

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()

try:
    basestring
except NameError:
    basestring = str

import numpy as np
import scipy

import matplotlib 
from matplotlib import pyplot as plt 
from matplotlib import ticker as ticker
import json
import sys
import os
from collections import OrderedDict  
import warnings 
from scipy.fftpack import hilbert
from scipy.signal import cheb2ord, cheby2, convolve, get_window, iirfilter, remez, decimate
from .filter import lowpass,bandpass
from .utils import exception, _saveFigData 


def getbandpass(lfps, sampr, minf=0.05, maxf=300):
    """
    Function to bandpass filter data

    Parameters
    ----------
    lfps : list or array 
        LFP signal data arranged spatially in a column.
        **Default:** *required*

    sampr : float
        The data sampling rate.
        **Default:** *required*

    minf : float
        The high-pass filter frequency (Hz).
        **Default:** ``0.05``

    maxf : float
        The low-pass filter frequency (Hz).
        **Default:** ``300``


    Returns
    -------
    data : array
        The bandpass-filtered data.

    """

    datband = []
    for i in range(len(lfps[0])):datband.append(bandpass(lfps[:,i], minf, maxf, df=sampr, zerophase=True))

    datband = np.array(datband)

    return datband


def Vaknin(x):
    """ 
    Function to perform the Vaknin correction for CSD analysis

    Allows CSD to be performed on all N contacts instead of N-2 contacts (see Vaknin et al (1988) for more details).

    Parameters
    ----------
    x : array 
        Data to be corrected.
        **Default:** *required*


    Returns
    -------
    data : array
        The corrected data.

    """

    # Preallocate array with 2 more rows than input array
    x_new = np.zeros((x.shape[0]+2, x.shape[1]))

    # Duplicate first and last row of x into first and last row of x_new
    x_new[0, :] = x[0, :]
    x_new[-1, :] = x[-1, :]

    # Duplicate all of x into middle rows of x_neww
    x_new[1:-1, :] = x

    return x_new


def removemean(x, ax=1):
    """
    Function to subtract the mean from an array or list

    Parameters
    ----------
    x : array 
        Data to be processed.
        **Default:** *required*

    ax : int
        The axis to remove the mean across.
        **Default:** ``1``


    Returns
    -------
    data : array
        The processed data.

    """
  
    mean = np.mean(x, axis=ax, keepdims=True)
    x -= mean



def getCSD(LFP_input_data=None, LFP_input_file=None, sampr=None, dt=None, spacing_um=None, minf=0.05, maxf=300, norm=True, vaknin=True, save_to_sim=True, getAllData=False): 
    """
    Function to extract CSD values from simulated LFP data 

    Parameters
    ----------
    LFP_input_data : list or numpy array 
        LFP data provided by user (mV).  Each element of the list/array must be a list/array containing LFP data for an electrode. 
        **Default:** ``None`` pulls the data from the current NetPyNE sim object.

    LFP_input_file : str    
        Location of a JSON data file with LFP data.
        **Default:** ``None`` 

    sampr : float
        Sampling rate for data recording (Hz).  
        **Default:** ``None`` uses ``1.0/sim.cfg.recordStep`` from the current NetPyNE sim object. 

    dt : float
        Time between recording points (ms). 
        **Default:** ``None`` uses ``sim.cfg.recordStep`` from the current NetPyNE sim object.

    spacing_um : float
        Electrode contact spacing in units of microns.
        **Default:** ``None`` pulls the information from the current NetPyNE sim object.  If the data is empirical, defaults to ``100`` (microns).

    minf : float
        Minimum frequency for bandpass filter (Hz).
        **Default:** ``0.05`` 

    maxf : float
        Maximum frequency cutoff for bandpass filter (Hz).
        **Default:** ``300``

    norm : bool
        Whether to subtract the mean from the signal or not. 
        **Default:** ``True`` subtracts the mean.

    vaknin : bool
        Whether or not to to perform the Vaknin correction for CSD analysis. 
        **Default** ``True`` performs the correction.

    save_to_sim : bool
        Whether to attempt to store CSD values in sim.allSimData, if this exists.
        **Default** ``True`` attempts to store the data.

    getAllData : bool
        True will have this function return dt, tt, timeRange, sampr, spacing_um, lfp_data, and CSD_data. 
        **Default** ``False`` returns only CSD_data.

    """

    # DEFAULT -- CONDITION 1 : LFP DATA COMES FROM SIMULATION 

    # if no inputs are given, get LFP data from simulation
    if LFP_input_data is None and LFP_input_file is None:
        
        try:
            from .. import sim 
        except:
            raise Exception('No LFP input data, input file, or existing simulation. Cannot calculate CSD.')
        
        # time step used in simulation recording (in ms)
        if dt is None:
            dt = sim.cfg.recordStep  
        
        # Get LFP data from sim and instantiate as a numpy array 
        sim_data_categories = sim.allSimData.keys()
        
        if 'LFP' in sim_data_categories:
            lfp_data = np.array(sim.allSimData['LFP'])
        else:
            raise Exception('NO LFP DATA!! Need to re-run simulation with cfg.recordLFP enabled.')

        # Sampling rate of data recording during the simulation 
        if sampr is None:
            # divide by 1000.0 to turn denominator from units of ms to s
            sampr = 1.0/(sim.cfg.recordStep/1000.0) 

        # Spacing between electrodes --> convert from micron to mm 
        if spacing_um is None:
            spacing_um = sim.cfg.recordLFP[1][1] - sim.cfg.recordLFP[0][1]


    # CONDITION 2 : ARBITRARY LFP DATA 
    # Note: need to expand capability to include a list of multiple files 
  
    # load sim data from a JSON file
    elif LFP_input_data is None and '.json' in LFP_input_file:
    
        data = {}
        with open(LFP_input_file) as file:
            data['json_input_data'] = json.load(file)

        ## FOR MULTIPLE FILES
        #for x in LFP_input_file:
            #with open(x) as file:
                #data[x] = json.load(file)

        # extract LFP data (only works in the 1 input file scenario; expand capability for multiple files) 
        for key in data.keys:
            lfp_data_list = data[key]['simData']['LFP']              
        
        # cast LFP data as Numpy array 
        lfp_data = np.array(lfp_data_list)

        # get CSD data and relevant plotting params 
        csd_data = {}
        for i in data.keys():
            csd_data[i] = {}

            if sampr is None:
                csd_data[i]['sampr'] = 1.0/((data[i]['simConfig']['recordStep'])/1000.0) 
                sampr = csd_data[i]['sampr']
            else:
                csd_data[i]['sampr'] = sampr

            if spacing_um is None:
                csd_data[i]['spacing_um'] = data[i]['simConfig']['recordLFP'][1][1] - data[i]['simConfig']['recordLFP'][0][1]
                spacing_um = csd_data[i]['spacing_um']
            else:
                csd_data[i]['spacing_um'] = spacing_um

            if dt is None:
                csd_data[i]['dt'] = data[i]['simConfig']['recordStep']
                dt = csd_data[i]['dt']
            else:
                csd_data[i]['dt'] = dt



    # FOR LIST OF LFP DATA WITHOUT ANY .JSON INPUT FILE

    # get lfp_data and cast as numpy array
    elif len(LFP_input_data) > 0 and LFP_input_file is None:     
        lfp_data = np.array(LFP_input_data)  

    # Convert spacing from microns to mm 
    spacing_mm = spacing_um/1000

    # Bandpass filter the LFP data with getbandpass() fx defined above
    datband = getbandpass(lfp_data,sampr,minf,maxf) 

    # Take CSD along smaller dimension
    if datband.shape[0] > datband.shape[1]:
        ax = 1
    else:
        ax = 0

    # Vaknin correction
    if vaknin: 
        datband = Vaknin(datband)

    # norm data
    if norm: 
        removemean(datband,ax=ax)

    # now each column (or row) is an electrode -- take CSD along electrodes
    CSD_data = -np.diff(datband, n=2, axis=ax)/spacing_mm**2  
  

    
    # noBandpass trial 
    datband_noBandpass = lfp_data.T
  
    if datband_noBandpass.shape[0] > datband_noBandpass.shape[1]:
        ax = 1
    else:
        ax = 0
  
    if vaknin:
        datband_noBandpass = Vaknin(datband_noBandpass)
  
    if norm:
        removemean(datband_noBandpass, ax=ax)
  
    CSD_data_noBandpass = -np.diff(datband_noBandpass,n=2,axis=ax)/spacing_mm**2 


    # Add CSD and other param values to sim.allSimData for later access
    if save_to_sim is True: 
        try:
            from .. import sim 
            sim.allSimData['CSD'] = {}
            sim.allSimData['CSD']['sampr'] = sampr
            sim.allSimData['CSD']['spacing_um'] = spacing_um 
            sim.allSimData['CSD']['CSD_data'] = CSD_data
            sim.allSimData['CSD']['CSD_data_noBandpass'] = CSD_data_noBandpass 
        except:
            print('NOTE: No sim.allSimData construct available to store CSD data.')

    # return CSD_data or all data
    if getAllData is True:
        return lfp_data, CSD_data, sampr, spacing_um, dt
    if getAllData is False:
        return CSD_data       



# PLOTTING CSD 

#@exception
def plotCSD(CSD_data=None, LFP_input_data=None, overlay=None, timeRange=None, sampr=None, stim_start_time=None, spacing_um=None, ymax=None, dt=None, hlines=False, layer_lines=False, layer_bounds=None, smooth=None, vaknin=False, fontSize=12, figSize=(10,10),dpi=200, saveFig=True, showFig=True): 
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
        Option to include other data overlaid on CSD color map plot. 
        **Default:** ``None``
        **Options:** ``'CSD_raw'``, ``'CSD_bandpassed'``, ``'LFP'``

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

    layer_lines : bool 
        Whether to plot horizontal lines over CSD plot at layer boundaries. 
        **Default:** ``False`` 

    layer_bounds : dict
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
        lfp_data, CSD_data, sampr, spacing_um, dt = getCSD(sampr=sampr, spacing_um=spacing_um, vaknin=vaknin, dt=dt, getAllData=True)

        sim_data_categories = sim.allSimData.keys()
        
        if 'CSD' in sim_data_categories:

            if timeRange is None:
                timeRange = [0,sim.cfg.duration] 

            dt = sim.cfg.recordStep
            tt = np.arange(timeRange[0],timeRange[1],dt)

            spacing_um = sim.allSimData['CSD']['spacing_um']
            spacing_mm = spacing_um/1000 

            ymax = sim.cfg.recordLFP[-1][1] + spacing_um

            # get LFP data
            LFP_data = np.array(sim.allSimData['LFP'])[int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep),:]

            # get CSD data
            CSD_data = sim.allSimData['CSD']['CSD_data'][:,int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep)]  

            # noBandpass trial
            CSD_data_noBandpass = sim.allSimData['CSD']['CSD_data_noBandpass'][:,int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep)]
      
        else:
            raise Exception('No CSD data in sim.')


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
        CSD_data = np.array(CSD_data)[:, int(timeRange[0]/dt):int(timeRange[1]/dt)]
        

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
    gs_outer = matplotlib.gridspec.GridSpec(2, 2, figure=fig, wspace=0.4, hspace=0.2, height_ratios=[20, 1])

    for i in range(numplots):
        axs.append(plt.Subplot(fig,gs_outer[i*2:i*2+2]))
        fig.add_subplot(axs[i])
        axs[i].set_xlabel('Time (ms)',fontsize=fontSize)
        axs[i].tick_params(axis='y', which='major', labelsize=fontSize)
        axs[i].tick_params(axis='x', which='major', labelsize=fontSize)

    # plot interpolated CSD color map 
    if smooth:
        Z = scipy.ndimage.filters.gaussian_filter(Z, smooth, mode='nearest')

    spline=axs[0].imshow(Z, extent=extent_xy, interpolation='none', aspect='auto', origin='upper', cmap='jet_r', alpha=0.9) 
    axs[0].set_ylabel('Contact depth (um)', fontsize=fontSize)

    # set Title of plot & overlay data (CSD_raw, CSD_bandpassed, or LFP)  
    if overlay is 'CSD_raw' or overlay is 'CSD_bandpassed' or overlay is 'LFP':
        nrow = LFP_data.shape[1]
        gs_inner = matplotlib.gridspec.GridSpecFromSubplotSpec(nrow, 1, subplot_spec=gs_outer[0:2], wspace=0.0, hspace=0.0)
        subaxs = []

        # go down grid and add data from each channel
        if overlay == 'CSD_raw':
            axs[0].set_title('CSD with raw CSD time series overlay', fontsize=fontSize)
            for chan in range(nrow):
                subaxs.append(plt.Subplot(fig, gs_inner[chan], frameon=False))
                fig.add_subplot(subaxs[chan])
                subaxs[chan].margins(0.0,0.01)
                subaxs[chan].get_xaxis().set_visible(False)
                subaxs[chan].get_yaxis().set_visible(False)
                subaxs[chan].plot(X, CSD_data_noBandpass[chan,:], color='red', linewidth=0.4)
    
        elif overlay == 'CSD_bandpassed':
            axs[0].set_title('CSD with Bandpassed CSD time series overlay', fontsize=fontSize) 
            for chan in range(nrow):
                subaxs.append(plt.Subplot(fig, gs_inner[chan], frameon=False))
                fig.add_subplot(subaxs[chan])
                subaxs[chan].margins(0.0,0.01)
                subaxs[chan].get_xaxis().set_visible(False)
                subaxs[chan].get_yaxis().set_visible(False)
                subaxs[chan].plot(X, CSD_data[chan,:], color='blue', linewidth=0.3)

        elif overlay == 'LFP':
            axs[0].set_title('CSD with LFP overlay', fontsize=14) 
            for chan in range(nrow):
                subaxs.append(plt.Subplot(fig, gs_inner[chan], frameon=False))
                fig.add_subplot(subaxs[chan])
                subaxs[chan].margins(0.0,0.01)
                subaxs[chan].get_xaxis().set_visible(False)
                subaxs[chan].get_yaxis().set_visible(False)
                subaxs[chan].plot(X, LFP_data[:,chan], color='gray', linewidth=0.3)

    else:
        print('No data being overlaid')
        axs[0].set_title('Current Source Density (CSD)', fontsize=fontSize)



    # add horizontal lines at electrode locations
    if hlines:
        for i in range(len(sim.cfg.recordLFP)):
            axs[0].hlines(sim.cfg.recordLFP[i][1], xmin, xmax, colors='black', linestyles='dashed')

    if layer_lines: 
        if layer_bounds is None:
            print('No layer boundaries given')
        else:
            layerKeys = []
        for i in layer_bounds.keys():
            axs[0].hlines(layer_bounds[i], xmin, xmax, colors='black', linewidth=1, linestyles='dotted') 
        layerKeys.append(i)

        for n in range(len(layerKeys)):
            if n == 0:
                axs[0].text(xmax+5, layer_bounds[layerKeys[n]]/2, layerKeys[n], color='black', fontsize=fontSize)
            else:
                axs[0].text(xmax+5, (layer_bounds[layerKeys[n]] + layer_bounds[layerKeys[n-1]])/2, layerKeys[n], color='black', fontsize=fontSize)

    # set vertical line at stimulus onset
    if type(stim_start_time) is int or type(stim_start_time) is float:
        axs[0].vlines(stim_start_time, ymin, ymax, colors='red', linewidth=1, linestyles='dashed')

    ax = plt.gca()
    ax.grid(False)

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
    if showFig is True:
        plt.show()
