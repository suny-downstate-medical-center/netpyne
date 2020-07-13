"""
Functions to plot and extract CSD info from LFP data
Contributors: Erica Y Griffith, Sam Neymotin, Salvador Dura-Bernal
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

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
def getCSD (LFP_exists=False,LFP_input_data=None,LFP_input_file=None,sampr=None,dt=None,timeRange=None,spacing_um=None,minf=0.05,maxf=300,norm=True,vaknin=False,save_to_sim=True,getAllData=True):
  """ Extracts CSD values from simulated LFP data 

      Parameters
      ----------
      LFP_exists : bool
        "True" means that the user will input the lfp data as either a .json file from a netpyne simulation (into LFP_input_file), 
        or as a list / np array of LFP values (mV) (into LFP_input_data)
        **Default:**
        ``False``

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

      timeRange : list [start, stop]  
        Time range to calculate CSD (ms). 
        ** MUST BE PROVIDED BY USER IF LFP_exists IS TRUE ** 
        **Default:** 
        ``None`` uses entire time range if data is from sim

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
        ``False``

      save_to_sim : bool
        True will have getCSD attempt to store CSD values in sim.allSimData, if this exists.
        **Default**
        ``True``

      getAllData : bool
        True will have this function returns dt, tt, timeRange, sampr, spacing_um, lfp_data, and CSD_data.
        False will return only CSD_data. 
        **Default**
        ``True``
  """

  ############### DEFAULT -- CONDITION 1 : LFP DATA COMES FROM SIMULATION ###############

  if LFP_exists is False:   ### GET LFP DATA FROM SIMULATION
    from .. import sim 

    ## SET DEFAULT ARGUMENT / PARAMETER VALUES 
    if timeRange is None:                 # Specify the time range of relevant LFP data 
      timeRange = [0,sim.cfg.duration]    # This makes the timeRange equal to the entire sim duration
    
    if dt is None:
      dt = sim.cfg.recordStep                         # units: ms 
    tt = np.arange(timeRange[0], timeRange[1],dt)   # make array of time points 

    if sampr is None:
      sampr = 1./sim.cfg.recordStep          # Sampling rate of data recording during the simulation 


    # Spacing between electrodes --> convert from micron to mm 
    if spacing_um is None:
      print('NOTE: using sim.cfg.recordLFP to determine spacing_um !!')
      spacing_um = sim.cfg.recordLFP[1][1] - sim.cfg.recordLFP[0][1]


    ## Check if LFP was recorded during the simulation 
    sim_data_categories = sim.allSimData.keys()

    if 'LFP' in sim_data_categories:
      lfp_data = np.array(sim.allSimData['LFP'])[int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep),:] # from lfp.py, line 200; array splicing

    elif 'LFP' not in sim_data:
      print('!! WARNING: NO LFP DATA !! Need to re-run simulation with cfg.recordLFP enabled')




  ############### CONDITION 2 : ARBITRARY LFP DATA ############################

  elif LFP_exists is True:   ### GET LFP DATA AND CONFIRM EXISTENCE OF OTHER NECESSARY PARAMS FROM USER
    if LFP_input_data is None and LFP_input_file is None:
      print('MUST PROVIDE LFP DATA')
      if timeRange is None:
        print('MUST PROVIDE TIME RANGE in ms')
      if sampr is None:
        print('MUST PROVIDE SAMPLING RATE in Hz')
      if dt is None:
        print('MUST PROVIDE dt in ms')
      if spacing_um is None:
        print('MUST PROVIDE SPACING BETWEEN ELECTRODES in MICRONS')

    ## EXPAND CAPABILITY TO INCLUDE LIST OF MULTIPLE FILES 
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
      #full_lfp_data = {}
      for key in data.keys:
        full_lfp_data = data[key]['simData']['LFP']  # only works in the 1 input file scenario; expand capability for multiple files             

      ## GET CSD DATA AND RELEVANT PLOTTING PARAMS 
      csd_data = {}
      for i in data.keys():
        csd_data[i] = {}        # e.g. csd['json_input_data'] = {}

        if timeRange is None:
          csd_data[i]['timeRange'] = [0, data[i]['simConfig']['duration']]
          timeRange = csd_data[i]['timeRange']        # only works in the 1 input file scenario; expand capability for multiple files 
        else:
          csd_data[i]['timeRange'] = timeRange

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



      ## GET LFP DATA OVER THE SPECIFIED TIME RANGE
      lfp_data = np.array(full_lfp_data)[int(timeRange[0]/dt):int(timeRange[1]/dt),:]

      ## MAKE ARRAY OF TIME POINTS ## USEFUL FOR GETALLDATA CONDITION
      tt = np.arange(timeRange[0],timeRange[1],dt)


    ## FOR LIST OF LFP DATA WITHOUT ANY .JSON INPUT FILE 
    elif LFP_input_file is None and len(LFP_input_data) > 0: 
      ## GET LFP DATA OVER THE SPECIFIED TIME RANGE
      lfp_data = np.array(LFP_input_data)[int(timeRange[0]/dt):int(timeRange[1]/dt),:]  # get lfp_data in timeRange specified 

      ## MAKE ARRAY OF TIME POINTS
      tt = np.arange(timeRange[0],timeRange[1],dt)


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



  ################## SAVING DATA ##########################
  # Add CSD and other param values to sim.allSimData for access outside of this function or script 
  if save_to_sim is True:   ## FROM SIM 
    try:
      from .. import sim 
      sim.allSimData['CSD']['timeRange'] = timeRange       # ['CSD']['sim']
      sim.allSimData['CSD']['sampr'] = sampr
      sim.allSimData['CSD']['spacing_um'] = spacing_um 
      sim.allSimData['CSD']['CSD_data'] = CSD_data
    except:
      print('NOTE: No sim.allSimData construct available to store CSD data')



  # RETURN CSD AND OTHER RELEVANT PARAM VALUES, IF DESIRED 
  if getAllData is True:
    return lfp_data, CSD_data, timeRange, sampr, spacing_um, dt, tt
  if getAllData is False:
    return CSD_data       # returns CSD in units of mV/mm**2 (assuming lfps are in mV)








################################
######### PLOTTING CSD #########
################################
def plotCSD(CSD_exists=False,CSD_data=None,LFP_input_data=None,LFP_overlay=True,timeRange=None,sampr=None,stim_start_time=None,aspacing_um=None,ymax=None,dt=None,hlines=False,layer_lines=False,saveFig=True,showFig=True): # saveData=None
  """ Plots CSD values extracted from simulated LFP data 
      
      Parameters
      ----------
      CSD_exists : bool
        Indicates if you are inputting arbitrary CSD data 
        ``True`` indicates that CSD data will be passed in as arbitrary input via CSD_data
        ``False`` assumes that CSD data must be derived using getCSD()
        **Default:**
        ``False`` 

      CSD_data : list or np array
        Enter list or numpy array of CSD data
        **Default:**
        ``None`` 

      LFP_input_data : list or np array
        pre-existing LFP data for overlay
        **Default:**
        ``None``

      LFP_overlay : bool
        Option to include LFP data overlaid on CSD plot 
        **Default:** ``True`` 


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
  
  ############### DEFAULT -- CONDITION 1 : GET CSD DATA USING getCSD() ###############
  if CSD_exists is False:
    # Get CSD data
    try:
      [LFP_input_data, CSD_data, timeRange, sampr, spacing_um, dt, tt] = getCSD(timeRange,sampr,spacing_um,dt)
    except: 
      ('getCSD() error: unable to acquire CSD data.')

  ############### CONDITION 2 : ARBITRARY CSD DATA ###############
  elif CSD_exists is True and len(CSD_data) > 0:     # arbitrary CSD data exists, and has been given.
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


    # Need to have CSD_data, timeRange, dt, spacing_um, ymax, and tt 

  ############## CONDITION 2 : DATA COMES FROM SIMULATION ###############
  elif CSD_exists is True and CSD_data is None:   # CSD data exists, but is not provided; try retrieving from (ongoing) simulation. 
    print('sim data used for plotting')
    
    try: 
      from .. import sim
    except:
      print('RUN SIMULATION TO ACQUIRE DATA')
    else:
      CSD_data = sim.allSimData['CSD']['CSD_data']   ## RETRIEVE CSD DATA (in mV/mm*2)
      
      if timeRange is None:  ## RETRIEVE TIME RANGE (in ms), IF UNSPECIFIED IN ARGS
        timeRange = sim.allSimData['CSD']['timeRange']
      
      dt = sim.cfg.recordStep                                       # dt --> recording time step (ms)
      tt = np.arange(timeRange[0],timeRange[1],dt)                  # tt --> time points 
      
      spacing_um = sim.allSimData['CSD']['spacing_um']   ## RETRIEVE SPACING BETWEEN ELECTRODE CONTACTS (in microns)
      spacing_mm = spacing_um/1000    # convert from microns to mm 

      ymax = sim.cfg.recordLFP[-1][1] + spacing_um

      # Need to have CSD_data, timeRange, dt, tt, spacing_um, and ymax 



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
  extent_xy = [xmin, xmax, ymax, ymin]


  # (ii) Set up figure 
  fig = plt.figure() #plt.figure(figsize=(10, 8)) #<-- quite large; for multiple subplots 

  # (iii) Create plots w/ common axis labels and tick marks
  axs = []
  if LFP_overlay is True:
    numplots=1
  else:
    numplots=2   # SWITCHED, used to be above numplots = 2, and here numplots = 1

  gs_outer = matplotlib.gridspec.GridSpec(2, 2, figure=fig, wspace=0.4, hspace=0.2, height_ratios = [20, 1]) # GridSpec(2, 4, figure = ...)
  for i in range(numplots):
    axs.append(plt.Subplot(fig,gs_outer[i*2:i*2+2]))
    fig.add_subplot(axs[i])
    axs[i].set_xlabel('Time (ms)',fontsize=12)
    axs[i].tick_params(axis='y', which='major', labelsize=8)

  # (iv) Set up title and y axis label and axis limits for CSD plot
  spline=axs[0].imshow(Z, extent=extent_xy, interpolation='none', aspect='auto', origin='upper', cmap='jet_r') # cmap = 'jet_r'
  axs[0].set_ylabel('Contact depth (um)', fontsize = 12)
  axs[0].set_title('CSD with LFP overlay',fontsize=14) #axs[0].set_title('RectBivariateSpline',fontsize=12)
  xmin = axs[0].get_xlim()[0]
  xmax = axs[0].get_xlim()[1]
  #ymin = axs[0].get_ylim()[0]
  #ymax = axs[0].get_ylim()[1]


  # grid for LFP plots
  if LFP_overlay is True:
    LFP_data = np.array(LFP_input_data)[int(timeRange[0]/dt):int(timeRange[1]/dt),:] #np.array(sim.allSimData['LFP'])[int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep),:]
    nrow = LFP_data.shape[1] # LFP_data.shape[0] gives you number of recorded time points.... 
    gs_inner = matplotlib.gridspec.GridSpecFromSubplotSpec(nrow, 1, subplot_spec=gs_outer[0:2], wspace=0.0, hspace=0.0)  # subplot_spec=gs_outer[2:4]
    clr = 'gray' 
    lw=0.3
    subaxs = []

    # go down grid and add LFP from each channel
    for chan in range(nrow):
      subaxs.append(plt.Subplot(fig,gs_inner[chan],frameon=False))
      fig.add_subplot(subaxs[chan])
      subaxs[chan].margins(0.0,0.01)
      subaxs[chan].get_xaxis().set_visible(False)
      subaxs[chan].get_yaxis().set_visible(False)
      subaxs[chan].plot(X,LFP_data[:,chan],color=clr,linewidth=lw)



  ## ADD HORIZONTAL LINES AT LOCATIONS OF EACH ELECTRODE
  if hlines is True:
    for i in range(len(sim.cfg.recordLFP)):
      axs[0].hlines(sim.cfg.recordLFP[i][1], xmin, xmax, colors='black', linestyles='dashed')


  ## ADD HORIZONTAL LINES AT CORTICAL LAYER BOUNDARIES
  A1_layer_bounds = {'I': 100, 'II': 160, 'III': 950, 'IV': 1250, 'VA': 1334, 'VB': 1550, 'VI': 2000} # "lower" bound for each layer
  if layer_lines is True: 
    for i in A1_layer_bounds.keys():
      axs[0].hlines(A1_layer_bounds[i], xmin, xmax, colors='black', linewidth=1,linestyles='dotted') 

    ## add labels for each layer -- would have to be adjusted by hand if changing layer bounds
    fig.text(0.922,0.855,'I',color='black')
    fig.text(0.92,0.825,'II',color='black')
    fig.text(0.92,0.68,'III',color='black')
    fig.text(0.92,0.5,'IV',color='black')
    fig.text(0.92,0.44,'VA',color='black')
    fig.text(0.92,0.39,'VB',color='black')
    fig.text(0.92,0.29,'VI',color='black')


  ## SET VERTICAL LINE AT STIMULUS ONSET
  if type(stim_start_time) is int or type(stim_start_time) is float:
    axs[0].vlines(stim_start_time,ymin,ymax,colors='red',linewidth=1,linestyles='dashed')



  # SAVE FIGURE
  if saveFig is True:
    plt.savefig('csd_fig.svg')
    plt.savefig('csd_fig.pdf')
  
  # DISPLAY FINAL FIGURE
  if showFig is True:
    plt.show()
    #plt.close()




