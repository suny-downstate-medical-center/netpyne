"""
Functions to plot and extract CSD info from LFP data
Contributors: Erica Y Griffith, Sam Neymotin, Salvador Dura-Bernal
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

try:
    basestring
except NameError:
    basestring = str

# THIRD PARTY IMPORTS
import numpy as np
import scipy                                  # for plotCSD()
from future import standard_library
standard_library.install_aliases()
import matplotlib 
from matplotlib import pyplot as plt 
from matplotlib import ticker as ticker
import json
## imports for rdmat ## 
import sys
import os
from collections import OrderedDict  
## imports for downsample ## 
import warnings 
from scipy.fftpack import hilbert
from scipy.signal import (cheb2ord, cheby2, convolve, get_window, iirfilter,
                          remez, decimate)

## LOCAL APPLICATION IMPORTS 
from .filter import lowpass,bandpass
#from .utils import exception, _saveFigData, _showFigure
from .utils import exception, _saveFigData 


############################################
######## FUNCTIONS USED IN getCSD() ########
############################################

# Bandpass filter  
def getbandpass (lfps,sampr,minf=0.05,maxf=300):   # lfps should be a list or numpy array of LFPs arranged spatially in a column
  datband = []
  for i in range(len(lfps[0])): datband.append(bandpass(lfps[:,i],minf,maxf,df=sampr,zerophase=True))
  #lfps_transpose = np.transpose(lfps)
  #for i in range(len(lfps_transpose[0])): datband.append(bandpass(lfps_transpose[:,i],minf,maxf,df=sampr,zerophase=True))
  datband = np.array(datband)
  return datband


# Vaknin correction for CSD analysis (MS implementation)
def Vaknin (x): ## Allows CSD to be performed on all N contacts instead of N-2 contacts (See Vaknin et al (1988) for more details)
  # Preallocate array with 2 more rows than input array
  x_new = np.zeros((x.shape[0]+2, x.shape[1]))
  # print(x_new.shape)
  # Duplicate first and last row of x into first and last row of x_new
  x_new[0, :] = x[0, :]
  x_new[-1, :] = x[-1, :]
  # Duplicate all of x into middle rows of x_neww
  x_new[1:-1, :] = x
  return x_new


# REMOVE MEAN 
def removemean (x, ax=1):
  mean = np.mean(x, axis=ax, keepdims=True)
  x -= mean
  #print(np.mean(x, axis=ax, keepdims=True))


###### FUNCTIONS SPECIFIC TO NHP DATA ######
############## REMOVED ###################


##################################################################


################################################
######### GET CSD VALUES FROM LFP DATA #########
################################################
def getCSD (LFP_input_data=None,LFP_input_file=None,sampr=None,dt=None,spacing_um=None,minf=0.05,maxf=300,norm=True,vaknin=True,save_to_sim=True,getAllData=False): # timeRange=None,
  """ Extracts CSD values from simulated LFP data 

      Parameters
      ----------
      LFP_input_data : list or numpy array 
        LFP data provided by user   (mV).
        ** CAN BE PROVIDED BY USER IF "LFP_exists" IS TRUE ** 
        Format: list, where each element is a list containing LFP data for each electrode. 
        **Default:**
        ``None`` 

      LFP_input_file : .json file entered as str    # (NOTE: make this compatible with list of .json files) 
        .json file from prior netpyne simulation
        **Default:**
        ``None`` 

      sampr : float
        Sampling rate for data recording (Hz).
        ** MUST BE PROVIDED BY USER IF LFP_exists IS TRUE ** 
        **Default:** 
        ``None`` uses 1./sim.cfg.recordStep if data is from sim 

      dt : float
        Time between recording points (ms). 
        **Default:**
          sim.config.recordStep if data is from sim

      spacing_um : float
        Electrode's contact spacing in units of microns 
        ** MUST BE PROVIDED BY USER IF LFP_exists IS TRUE (else default value of 100 microns is used) ** 
        **Default:** ``None``

      minf : float
        Minimum frequency for bandpass filter (Hz).
        **Default:** ``0.05`` 

      maxf : float
        Maximum frequency cutoff for bandpass filter (Hz).
        **Default:** ``300``

      norm : bool
        Needs documentation. <---- ?? 
        **Default:**
        ``True``

      vaknin : bool
        Needs documentation. <---- ?? 
        **Default**
        ``True``

      save_to_sim : bool
        True will have getCSD attempt to store CSD values in sim.allSimData, if this exists.
        **Default**
        ``True``

      getAllData : bool
        True will have this function returns dt, tt, timeRange, sampr, spacing_um, lfp_data, and CSD_data.
        False will return only CSD_data. 
        **Default**
        ``False``
  """

  ############### DEFAULT -- CONDITION 1 : LFP DATA COMES FROM SIMULATION ###############

  if LFP_input_data is None and LFP_input_file is None:   ### GET LFP DATA FROM SIMULATION
    try:
      from .. import sim 
    except:
      print('No LFP input data, input file, or existing simulation. Cannot calculate CSD.')
    else:
      ## Check if LFP was recorded during the simulation 
      print('getCSD() is using LFP data from existing simulation.')


    # ## These lines technically assume that from .. import sim worked -- slight reorganization needed 
    # if timeRange is None:
    #   try:
    #     timeRange = sim.cfg.analysis['plotLFP']['timeRange']
    #     # This sets the timeRange equal to the timeRange used in plotLFP
    #   except:
    #     print('No timeRange specified in plotLFP -- using entire sim duration as timeRange.')
    #     timeRange = [0,sim.cfg.duration]
    #     print('timeRange = ' + str(timeRange))
    #   else:
    #     print('timeRange specified in plotLFP.')
    #     print('timeRange = ' + str(timeRange))
    # else:
    #   print('Using timeRange from getCSD() arguments.')
    #   print('timeRange = ' + str(timeRange)) # This is to verify that the timeRange being used is the timeRange specified in the arguments


    # time step used in simulation recording 
    if dt is None:
      dt = sim.cfg.recordStep                         # units: ms 
    print('dt = ' + str(dt))

    # tt = np.arange(timeRange[0], timeRange[1],dt)   # make array of time points 
    # print('tt.size = ' + str(tt.size))


    sim_data_categories = sim.allSimData.keys()
    
    # Get LFP data from sim and instantiate as a numpy array 
    if 'LFP' in sim_data_categories:
      lfp_data = np.array(sim.allSimData['LFP'])
      print('lfp_data shape = ' + str(lfp_data.shape))
    elif 'LFP' not in sim_data_categories:
      print('!! WARNING: NO LFP DATA !! Need to re-run simulation with cfg.recordLFP enabled')


    # Sampling rate of data recording during the simulation 
    if sampr is None:
      sampr = 1./sim.cfg.recordStep


    # Spacing between electrodes --> convert from micron to mm 
    if spacing_um is None:
      print('NOTE: using sim.cfg.recordLFP to determine spacing_um !!')
      spacing_um = sim.cfg.recordLFP[1][1] - sim.cfg.recordLFP[0][1]




  ############### CONDITION 2 : ARBITRARY LFP DATA ############################
  ## NOTE: EXPAND CAPABILITY TO INCLUDE LIST OF MULTIPLE FILES 
  
  ## LOAD SIM DATA FROM JSON FILE
  elif LFP_input_data is None and '.json' in LFP_input_file:
    data = {}
    with open(LFP_input_file) as file:
      data['json_input_data'] = json.load(file)

    ## FOR MULTIPLE FILES
    #for x in LFP_input_file:
      #with open(x) as file:
        #data[x] = json.load(file)


    ## EXTRACT LFP DATA 
    for key in data.keys:
      lfp_data_list = data[key]['simData']['LFP']  # only works in the 1 input file scenario; expand capability for multiple files             
    
    ## CAST LFP DATA AS NUMPY ARRAY 
    lfp_data = np.array(lfp_data_list)

    ## GET CSD DATA AND RELEVANT PLOTTING PARAMS 
    csd_data = {}
    for i in data.keys():
      csd_data[i] = {}        # e.g. csd['json_input_data'] = {}

      # if timeRange is None:
      #   try:
      #     csd_data[i]['timeRange'] = sim.cfg.analysis['plotLFP']['timeRange'] # USE LFP TIMERANGE BY DEFAULT
      #   except:
      #     csd_data[i]['timeRange'] = [0, data[i]['simConfig']['duration']] # USE WHOLE SIM DURATION IF NOT ACCESSIBLE
      #     print('timeRange not specified in plotLFP - using whole sim duration for timeRange')
      #   timeRange = csd_data[i]['timeRange']        # only works in the 1 input file scenario; expand capability for multiple files 
      # else:
      #   csd_data[i]['timeRange'] = timeRange

      if sampr is None:
        csd_data[i]['sampr'] = 1./data[i]['simConfig']['recordStep']
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


    # ## MAKE ARRAY OF TIME POINTS ## USEFUL FOR GETALLDATA CONDITION
    # tt = np.arange(timeRange[0],timeRange[1],dt)


  ## FOR LIST OF LFP DATA WITHOUT ANY .JSON INPUT FILE 
  elif len(LFP_input_data) > 0 and LFP_input_file is None:     # elif LFP_input_file is None and ...
    ## GET LFP DATA OVER THE SPECIFIED TIME RANGE
    lfp_data = np.array(LFP_input_data)  # get lfp_data and cast as numpy array

    # ## MAKE ARRAY OF TIME POINTS
    # tt = np.arange(timeRange[0],timeRange[1],dt)


  ##############################################################################
   # Now lfp_data exists for either existing (e.g. empirical) or simulated data 
  ##############################################################################

  # Convert spacing from microns to mm 
  spacing_mm = spacing_um/1000

  # Bandpass filter the LFP data with getbandpass() fx defined above
  datband = getbandpass(lfp_data,sampr,minf,maxf) 

  # Take CSD along smaller dimension
  if datband.shape[0] > datband.shape[1]:
    ax = 1
  else:
    ax = 0

  # VAKNIN CORRECTION
  if vaknin: 
    datband = Vaknin(datband)

  # NORM <-- ASKING SAM MORE ABOUT THIS
  if norm: 
    removemean(datband,ax=ax)

  # now each column (or row) is an electrode -- take CSD along electrodes
  CSD_data = -np.diff(datband,n=2,axis=ax)/spacing_mm**2  ## CSD_data should be in mV/mm**2, assuming that LFP data is in mV. 
  

  ########################################
  ########## noBandpass trial ############
  ########################################
  datband_noBandpass = lfp_data.T
  
  if datband_noBandpass.shape[0] > datband_noBandpass.shape[1]:
    ax = 1
  else:
    ax = 0
  
  if vaknin:
   datband_noBandpass = Vaknin(datband_noBandpass)
  
  if norm:
    removemean(datband_noBandpass,ax=ax)
  
  CSD_data_noBandpass = -np.diff(datband_noBandpass,n=2,axis=ax)/spacing_mm**2 # noBandpass trial 
  ##########################################



  ################## SAVING DATA ##########################
  # Add CSD and other param values to sim.allSimData for access outside of this function or script 
  if save_to_sim is True:   ## FROM SIM 
    try:
      from .. import sim 
      sim.allSimData['CSD'] = {}
      #sim.allSimData['CSD']['timeRange'] = timeRange 
      sim.allSimData['CSD']['sampr'] = sampr
      sim.allSimData['CSD']['spacing_um'] = spacing_um 
      sim.allSimData['CSD']['CSD_data'] = CSD_data
      sim.allSimData['CSD']['CSD_data_noBandpass'] = CSD_data_noBandpass # noBandpass trial 
    except:
      print('NOTE: No sim.allSimData construct available to store CSD data')



  # RETURN CSD AND OTHER RELEVANT PARAM VALUES, IF DESIRED 
  if getAllData is True:
    return lfp_data, CSD_data, sampr, spacing_um, dt
  if getAllData is False:
    return CSD_data       # returns CSD in units of mV/mm**2 (assuming lfps are in mV)








################################
######### PLOTTING CSD #########
################################
@exception
def plotCSD(CSD_data=None,LFP_input_data=None,overlay=None,timeRange=None,sampr=None,stim_start_time=None,spacing_um=None,ymax=None,dt=None,hlines=False,layer_lines=False,layer_bounds=None,saveFig=True,showFig=True): # saveData=None
  """ Plots CSD values extracted from simulated LFP data 
      
      Parameters
      ----------
      CSD_data : list or np array
        Enter list or numpy array of CSD data
        **Default:**
        ``None`` 

      LFP_input_data : list or np array
        pre-existing LFP data for overlay
        **Default:**
        ``None``

      LFP_overlay : str
        Option to include other data overlaid on CSD color map plot 
        Options: 'CSD_raw', 'CSD_bandpassed', 'LFP'
        **Default:** ``None`` 


      timeRange : list [start, stop]
        Time range to plot.
        **Default:** 
        ``None`` plots entire time range

      sampr : int or float
        sampling rate (Hz.)
        Needed for getCSD()
        **Default:**
        ``None`` 
      
      stim_start_time : int or float 
        Time when stimulus is applied (ms). 
        **Default:**
        ``None`` does not add anything to plot. 
        Value adds a vertical dashed line to the plot, at time of stimulus onset. 

      spacing_um : float
        Electrode's contact spacing in units of microns 
        ** MUST BE PROVIDED BY USER IF LFP DATA IS EMPIRICAL ** 
        **Default:** 
        If data is from simulation: spacing_um is extracted from sim.cfg.recordLFP
        IF data is empirical: spacing_um defaults to 100 microns unless otherwise specified

      ymax : float
        if CSD_exists = True; can manually enter this (microns)
        **Default:**
        ``None`` 

      dt : float
        simConfig.recordStep

      hlines : bool
        Option to include horizontal lines on plot to indicate height of electrode(s). 
        **Default:**
        ``False`` 

      layer_lines : bool 
        Indicates whether or not to plot horizontal lines over CSD plot at layer boundaries 
        **Default:**
        ``False`` 

      layer_bounds : dict
        Dictionary containing layer labels as keys, and layer boundaries as values. 
        e.g. {'L1':100, 'L2': 160, 'L3': 950, 'L4': 1250, 'L5A': 1334, 'L5B': 1550, 'L6': 2000}
        **Default:**
        ``None``

     saveFig : bool or str
        Whether and where to save the figure.
        **Default:** ``True``
        **Options:** ``True`` autosaves the figure,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.png'``, ``'.jpg'``, ``'.eps'``, and ``'.tiff'``
    
      showFig : bool
        Shows the figure if ``True``.
        **Default:** ``True``

      ### saveData : bool or str
        Whether and where to save the data used to generate the plot. 
        **Default:** ``False`` 
        **Options:** ``True`` autosaves the data
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.pkl'`` and ``'.json'``
     

  """

  print('Plotting CSD... ')
  
  ############### DEFAULT -- CONDITION 1 : GET CSD DATA FROM SIM ###############
  if CSD_data is None:
    
    #print('sim data used for plotting')
    getCSD(sampr=sampr,spacing_um=spacing_um,dt=dt,getAllData=True)

    from .. import sim      ## put this in try except block? 

    sim_data_categories = sim.allSimData.keys()
    if 'CSD' in sim_data_categories:

      if timeRange is None:  ## RETRIEVE TIME RANGE (in ms), IF UNSPECIFIED IN ARGS
        #timeRange = sim.allSimData['CSD']['timeRange']
        timeRange = [0,sim.cfg.duration] # sim.cfg.duration is a float # timeRange should be the entire sim duration 

      dt = sim.cfg.recordStep                                       # dt --> recording time step (ms)
      
      tt = np.arange(timeRange[0],timeRange[1],dt)                  # tt --> time points 

      spacing_um = sim.allSimData['CSD']['spacing_um']   ## RETRIEVE SPACING BETWEEN ELECTRODE CONTACTS (in microns)
      spacing_mm = spacing_um/1000    # convert from microns to mm 

      ymax = sim.cfg.recordLFP[-1][1] + spacing_um

      # GET LFP DATA 
      ## This will be the LFP data sliced by relevant timeRange -- default is whole sim, unless specified in plotCSD() args
      LFP_data = np.array(sim.allSimData['LFP'])[int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep),:]

      # GET CSD DATA  --> ## RETRIEVE CSD DATA (in mV/mm*2)
      print("Using CSD sim data from sim.allSimData['CSD']")
      CSD_data = sim.allSimData['CSD']['CSD_data'][:,int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep)]
      #CSD_data = sim.allSimData['CSD']['CSD_data']   
      ####### noBandpass trial ######
      CSD_data_noBandpass = sim.allSimData['CSD']['CSD_data_noBandpass'][:,int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep)]
      ###############################


    elif 'CSD' not in sim_data_categories:
      print('No CSD data to use in sim -- getCSD() did not work') #running getCSD to acquire CSD data')

  ############### CONDITION 2 : ARBITRARY CSD DATA ###############
  elif CSD_data is not None:     # arbitrary CSD data exists, and has been given.
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

    # NEED tt and LFP_data
    tt = np.arange(timeRange[0], timeRange[1], dt)
    LFP_data = np.array(LFP_input_data)[int(timeRange[0]/dt):int(timeRange[1]/dt),:]
    # Need to have CSD_data, timeRange, dt, spacing_um, ymax, and tt 



  ############### PLOTTING ######################
  ## INTERPOLATION ## 
  X = np.arange(timeRange[0], timeRange[1], dt)  # dt == sim.cfg.recordStep if data is from simulation 
  Y = np.arange(CSD_data.shape[0])
  CSD_spline=scipy.interpolate.RectBivariateSpline(Y, X, CSD_data)
  Y_plot = np.linspace(0,CSD_data.shape[0],num=1000) 
  Z = CSD_spline(Y_plot, X)



  # (i) Set up axes 
  xmin = int(X[0])
  xmax = int(X[-1]) + 1  #int(sim.allSimData['t'][-1])
  ymin = 0
  ## DEALT WITH ymax IN ALL CONDITIONS ABOVE #  ymax = sim.cfg.recordLFP[-1][1] + spacing_um #(sim.cfg.recordLFP[-1][1])/1000 + spacing_mm #depth 
  #ymax = 24  
  extent_xy = [xmin, xmax, ymax, ymin]


  # (ii) Set up figure 
  fig = plt.figure() 

  # (iii) Create plots w/ common axis labels and tick marks
  axs = []

  numplots = 1

  gs_outer = matplotlib.gridspec.GridSpec(2, 2, figure=fig, wspace=0.4, hspace=0.2, height_ratios = [20, 1]) # GridSpec(2, 4, figure = ...)
  for i in range(numplots):
    axs.append(plt.Subplot(fig,gs_outer[i*2:i*2+2]))
    fig.add_subplot(axs[i])
    axs[i].set_xlabel('Time (ms)',fontsize=12)
    axs[i].tick_params(axis='y', which='major', labelsize=8)

  # (iv) PLOT INTERPOLATED CSD COLOR MAP
  spline=axs[0].imshow(Z, extent=extent_xy, interpolation='none', aspect='auto', origin='upper', cmap='jet_r', alpha=0.9) # alpha controls transparency -- set to 0 for transparent, 1 for opaque
  axs[0].set_ylabel('Contact depth (um)', fontsize = 12)

  # (v) Set Title of plot & overlay data if specified (CSD_raw, CSD_bandpassed, or LFP)  
  if overlay is 'CSD_raw' or 'CSD_bandpassed' or 'LFP':
    nrow = LFP_data.shape[1]  # could this also be CSD_data.shape[0] -- TEST THIS 
    gs_inner = matplotlib.gridspec.GridSpecFromSubplotSpec(nrow, 1, subplot_spec=gs_outer[0:2], wspace=0.0, hspace=0.0)  # subplot_spec=gs_outer[2:4]
    subaxs = []

    # go down grid and add data from each channel
    if overlay == 'CSD_raw':
      axs[0].set_title('CSD with raw CSD time series overlay',fontsize=14)
      for chan in range(nrow):
        subaxs.append(plt.Subplot(fig,gs_inner[chan],frameon=False))
        fig.add_subplot(subaxs[chan])
        subaxs[chan].margins(0.0,0.01)
        subaxs[chan].get_xaxis().set_visible(False)
        subaxs[chan].get_yaxis().set_visible(False)
        subaxs[chan].plot(X,CSD_data_noBandpass[chan,:],color='red',linewidth=0.4)
    
    elif overlay == 'CSD_bandpassed':
      axs[0].set_title('CSD with Bandpassed CSD time series overlay',fontsize=12) 
      for chan in range(nrow):
        subaxs.append(plt.Subplot(fig,gs_inner[chan],frameon=False))
        fig.add_subplot(subaxs[chan])
        subaxs[chan].margins(0.0,0.01)
        subaxs[chan].get_xaxis().set_visible(False)
        subaxs[chan].get_yaxis().set_visible(False)
        subaxs[chan].plot(X,CSD_data[chan,:],color='blue',linewidth=0.3)

    elif overlay == 'LFP':
      axs[0].set_title('CSD with LFP overlay',fontsize=14) 
      for chan in range(nrow):
        subaxs.append(plt.Subplot(fig,gs_inner[chan],frameon=False))
        fig.add_subplot(subaxs[chan])
        subaxs[chan].margins(0.0,0.01)
        subaxs[chan].get_xaxis().set_visible(False)
        subaxs[chan].get_yaxis().set_visible(False)
        subaxs[chan].plot(X,LFP_data[:,chan],color='gray',linewidth=0.3)

  else:
    axs[0].set_title('Current Source Density (CSD)',fontsize=14)


  # if overlay == 'CSD_raw':
  #   axs[0].set_title('CSD with raw CSD time series overlay',fontsize=14) ### noBandpass trial 
  #   subaxs[chan].plot(X,CSD_data_noBandpass[chan,:],color='red',linewidth=0.4)

  # elif overlay == 'LFP': 
  #   axs[0].set_title('CSD with LFP overlay',fontsize=14) 
  #   subaxs[chan].plot(X,LFP_data[:,chan],color='gray',linewidth=0.3)

  # elif overlay == 'CSD_bandpassed':
  #   axs[0].set_title('CSD with Bandpassed CSD time series overlay',fontsize=12) 
  #   subaxs[chan].plot(X,CSD_data[chan,:],color='blue',linewidth=0.3)
  
  # else:
  #   axs[0].set_title('Current Source Density (CSD)',fontsize=14)
  


  # # grid for LFP plots
  # if LFP_overlay:
  #   ## DOES THIS LINE BELOW ALSO DO THE CSD COLOR MAP PLOT? 
  #   axs[0].imshow(Z, extent=extent_xy, interpolation='none', aspect='auto', origin='upper', cmap='jet_r', alpha=0.8)
  #   # DEFINED ABOVE # LFP_data = np.array(LFP_input_data)#[int(timeRange[0]/dt):int(timeRange[1]/dt),:] #np.array(sim.allSimData['LFP'])[int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep),:]
  #   nrow = LFP_data.shape[1] # LFP_data.shape[0] gives you number of recorded time points.... 
  #   gs_inner = matplotlib.gridspec.GridSpecFromSubplotSpec(nrow, 1, subplot_spec=gs_outer[0:2], wspace=0.0, hspace=0.0)  # subplot_spec=gs_outer[2:4]
  #   clr = 'gray' 
  #   lw=0.3
  #   subaxs = []

    # go down grid and add LFP from each channel
    # for chan in range(nrow):
    #   subaxs.append(plt.Subplot(fig,gs_inner[chan],frameon=False))
    #   fig.add_subplot(subaxs[chan])
    #   subaxs[chan].margins(0.0,0.01)
    #   subaxs[chan].get_xaxis().set_visible(False)
    #   subaxs[chan].get_yaxis().set_visible(False)
      #subaxs[chan].plot(X,LFP_data[:,chan],color='black',linewidth=lw) ## LFP OVERLAY 

      ## CSD TIME COURSE DATA (BANDPASSED): 
      #subaxs[chan].plot(X,CSD_data[chan,:],color='blue',linewidth=0.3)
      ## noBandpass trial 
      #subaxs[chan].plot(X,CSD_data_noBandpass[chan,:],color='red',linewidth=0.4)


  ## ADD HORIZONTAL LINES AT LOCATIONS OF EACH ELECTRODE
  if hlines:
    for i in range(len(sim.cfg.recordLFP)):
      axs[0].hlines(sim.cfg.recordLFP[i][1], xmin, xmax, colors='black', linestyles='dashed')


  ## ADD HORIZONTAL LINES AT CORTICAL LAYER BOUNDARIES
  #layer_bounds = {'L1': 100, 'L2': 160, 'L3': 950, 'L4': 1250, 'L5A': 1334, 'L5B': 1550, 'L6': 2000} # "lower" bound for each layer

  if layer_lines: 
    if layer_bounds is None:
      print('No layer boundaries given')
    else:
      layerKeys = []  # list that will contain layer names (e.g. 'L1')
      for i in layer_bounds.keys():
        axs[0].hlines(layer_bounds[i], xmin, xmax, colors='black', linewidth=1, linestyles='dotted') # draw horizontal lines at lower boundary of each layer
        layerKeys.append(i)   # make a list of the layer names 
      for n in range(len(layerKeys)): # place layer name labels (e.g. 'L1', 'L2') onto plot 
        if n == 0:
          axs[0].text(xmax+5, layer_bounds[layerKeys[n]]/2, layerKeys[n],color='black',fontsize=8)
        else:
          axs[0].text(xmax+5, (layer_bounds[layerKeys[n]] + layer_bounds[layerKeys[n-1]])/2,layerKeys[n],color='black',fontsize=8)



  ## SET VERTICAL LINE AT STIMULUS ONSET
  if type(stim_start_time) is int or type(stim_start_time) is float:
    axs[0].vlines(stim_start_time,ymin,ymax,colors='red',linewidth=1,linestyles='dashed')


  # SAVE FIGURE
  if saveFig:
    if isinstance(saveFig, basestring):
      filename = saveFig
    else:
      filename = sim.cfg.filename + '_CSD.png'
    try:
      plt.savefig(filename)   #dpi
    except:
      plt.savefig('CSD_fig.png')

  # DISPLAY FINAL FIGURE
  if showFig is True:
    plt.show()
    #plt.close()




