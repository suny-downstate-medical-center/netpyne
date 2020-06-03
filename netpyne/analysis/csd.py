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

## LOCAL APPLICATION IMPORTS 
from .filter import lowpass,bandpass
from .utils import exception, _saveFigData, _showFigure



############################################
######## FUNCTIONS USED IN getCSD() ########
############################################

# Bandpass filter  
def getbandpass (lfps,sampr,minf=0.05,maxf=300):   # lfps should be a list or numpy array of LFPs arranged spatially in a column
  datband = []
  for i in range(len(lfps[0])): datband.append(bandpass(lfps[:,i],minf,maxf,df=sampr,zerophase=True))
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



################################################
######### GET CSD VALUES FROM LFP DATA #########
################################################
#@exception
def getCSD (sampr=None,timeRange=None,spacing_um=100.0,minf=0.05,maxf=300,norm=True,vaknin=False):
  """ Extracts CSD values from simulated LFP data 

      Parameters
      ----------
      sampr : float
        Sampling rate for data recording.
        **Default:** 
        ``None`` uses cfg.recordStep


      timeRange : list [start, stop]
        Time range to plot.
        **Default:** 
        ``None`` plots entire time range

      spacing_um : float
        Electrode's contact spacing in units of microns <-- VERTICALLY, I ASSUME?
        **Default:** ``100.0``

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
  """

  from .. import sim 

  ## SET DEFAULT ARGUMENT / PARAMETER VALUES 
  if timeRange is None:                 # Specify the time range of relevant LFP data 
    timeRange = [0,sim.cfg.duration]    # This makes the timeRange equal to the entire sim duration
  
  if sampr is None:
    sampr = 1./sim.cfg.recordStep          # Sampling rate of data recording during the simulation 
  
  spacing_mm = spacing_um/1000          # Spacing between electrodes --> convert from micron to mm 


  ## Check if LFP was recorded during the simulation 
  sim_data_categories = sim.allSimData.keys()
  
  if 'LFP' in sim_data_categories:
    # Get LFP data
    lfp_data = np.array(sim.allSimData['LFP'])[int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep),:] # from lfp.py, line 200; array splicing
    
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
    
    # Add CSD values to sim.allSimData for access outside of this function or script 
    sim.allSimData['CSD'] = CSD_data
  
  elif 'LFP' not in sim_data:
    print('!! WARNING: NO LFP DATA !! Need to re-run simulation with cfg.recordLFP enabled')
    CSD_data = []

  # returns CSD in units of mV/mm**2 (assuming lfps are in mV)
  return CSD_data



################################
######### PLOTTING CSD #########
################################

def plotCSD(timeRange=None,saveData=None, saveFig=None, showFig=True):
  """ Plots CSD values extracted from simulated LFP data 
      
      Parameters
      ----------
      timeRange : list [start, stop]
        Time range to plot.
        **Default:** 
        ``None`` plots entire time range

      saveData : bool or str
        Whether and where to save the data used to generate the plot. 
        **Default:** ``False`` 
        **Options:** ``True`` autosaves the data
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.pkl'`` and ``'.json'``
     
     saveFig : bool or str
        Whether and where to save the figure.
        **Default:** ``False``
        **Options:** ``True`` autosaves the figure,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.png'``, ``'.jpg'``, ``'.eps'``, and ``'.tiff'``
    
      showFig : bool
        Shows the figure if ``True``.
        **Default:** ``True``

  """
  from .. import sim

  print('Plotting CSD... ')
  
  ##### (1) CHECK IF CSD VALUES HAVE ALREADY BEEN EXTRACTED FROM LFP #####
  sim_data = sim.allSimData.keys()


  ##### (2) STORE CSD DATA #####
  if 'CSD' in sim_data:
    CSD_data = sim.allSimData['CSD']     ## Should already be numpy array from getCSD()
    #CSD_data = np.array(CSD_data)       ## Needs to be in numpy array format for getAvgERP fx 
  elif 'CSD' not in sim_data:
    print('NEED TO GET CSD VALUES FROM LFP DATA -- run sim.analysis.getCSD()')
    sim.analysis.getCSD()   # WHAT ABOUT ARGS? ANY NEEDED? 
    CSD_data = sim.allSimData['CSD']
    #CSD_data = np.array(CSD_data)



  ##### (3) INTERPOLATION #####
  ## SET UP TIME POINTS FOR X AXIS 
  if timeRange is None:
    #timeRange = [0,sim.cfg.duration] 
    timeRange = sim.cfg.analysis['getCSD']['timeRange']
  X = np.arange(timeRange[0], timeRange[1], sim.cfg.recordStep)

  Y = np.arange(CSD_data.shape[0])
  CSD_spline=scipy.interpolate.RectBivariateSpline(Y, X, CSD_data)
  Y_plot = np.linspace(0,CSD_data.shape[0],num=1000) # SURE ABOUT SHAPE? NUM? 
  Z = CSD_spline(Y_plot, X)



  ##### (4) SET UP PLOTTING #####

  # (i) Set up axes 
  xmin = 0 
  xmax = int(X[-1]) + 1  #int(sim.allSimData['t'][-1])     # why this index? and also, need to resolve ttavg <--
  ymin = 1    # where does this come from? 
  ymax = int(Y[-1]) + 1   # where does this come from?
  extent_xy = [xmin, xmax, ymax, ymin]

  # (ii) Set up figure 
  fig = plt.figure() #plt.figure(figsize=(10, 8)) #<-- quite large; for multiple subplots 

  # (iii) Title
  fig.suptitle('Current Source Density')            #("Averaged Laminar CSD (n=%d) in A1 after 40 dB stimuli"%len(tts))

  # (iii) Create plots w/ common axis labels and tick marks
  axs = []
  numplots=1
  gs_outer = matplotlib.gridspec.GridSpec(2, 4, figure=fig, wspace=0.4, hspace=0.2, height_ratios = [20, 1])
  for i in range(numplots):
    axs.append(plt.Subplot(fig,gs_outer[i*2:i*2+2]))
    fig.add_subplot(axs[i])
    #axs[i].set_yticks(np.arange(1, 24, step=1)) # np.arange(1, 24, step=1))
    axs[i].set_ylabel('Contact', fontsize=12)
    axs[i].set_xlabel('Time (ms)',fontsize=12)
    #axs[i].set_xticks(np.arange(0, 60, step=10)) # np.arange(0, 60, step=10))

  # (iv)
  spline=axs[0].imshow(Z, extent=extent_xy, interpolation='none', aspect='auto', origin='upper', cmap='jet_r')
  axs[0].set_title('RectBivariateSpline',fontsize=12)

  height = axs[0].get_ylim()[0]
  perlayer_height = int(height/CSD_data.shape[0])
  xmin = axs[0].get_xlim()[0]
  xmax = axs[0].get_xlim()[1]




   # DISPLAY FINAL FIGURE
  plt.show()


  # values = [1, 4, 5, 9, 10, 11, 12, 13, 14, 16] ### WHAT IS THIS ABOUT? 
  # for i,val in enumerate(values):
  #   if start_or_end[i] == "start":
  #     axs[0].hlines(values[i]+0.02, xmin, xmax, colors='black', linestyles='dashed')
  #     axs[0].text(2, values[i]+0.7, sink_or_source[i], fontsize=10)
  #   else:
  #     axs[0].hlines(values[i]+1.02, xmin, xmax, colors='black', linestyles='dashed')


  # COLORBAR
  ## FILL THIS IN

 


# NOTE ON COLORS: 
# # when drawing CSD make sure that negative values (depolarizing intracellular current) drawn in red,
# # and positive values (hyperpolarizing intracellular current) drawn in blue



