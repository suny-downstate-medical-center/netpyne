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
@exception
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
    sampr = sim.cfg.recordStep          # Sampling rate of data recording during the simulation 
  
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

### getAvgERP <-- function from analysis-scripts-master used in plotCSD()
# get the average ERP (dat should be either LFP or CSD; type --> numpy array)
# def getAvgERP (dat, sampr, trigtimes, swindowms, ewindowms):
#   nrow = dat.shape[0]
#   tt = np.linspace(swindowms, ewindowms,ms2index(ewindowms - swindowms,sampr))
#   swindowidx = ms2index(swindowms,sampr) # could be negative
#   ewindowidx = ms2index(ewindowms,sampr)
#   avgERP = np.zeros((nrow,len(tt)))
#   for chan in range(nrow): # go through channels
#     for trigidx in trigtimes: # go through stimuli
#       sidx = max(0,trigidx+swindowidx)
#       eidx = min(dat.shape[1],trigidx+ewindowidx)
#       avgERP[chan,:] += dat[chan, sidx:eidx]
#     avgERP[chan,:] /= float(len(trigtimes))
#   return tt,avgERP



def plotCSD(timeRange=None, sampr=None, saveData=None, saveFig=None, showFig=True):
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
    CSD_data = sim.allSimData['CSD']
    CSD_data = np.array(CSD_data)       ## Needs to be in numpy array format for getAvgERP fx 
  elif 'CSD' not in sim_data:
    print('NEED TO GET CSD VALUES FROM LFP DATA -- run sim.analysis.getCSD()')
    sim.analysis.getCSD()   # WHAT ABOUT ARGS? ANY NEEDED? 
    CSD_data = sim.allSimData['CSD']
    CSD_data = np.array(CSD_data)


  ##### (3) GET AVERAGE ERP FOR CSD DATA #####

  # (i) Get sampling rate 
  if sampr is None:
    sampr = sim.cfg.recordStep  # First need sampling rate (ms)
  
  # # (ii) Set epoch params
  # swindowms = 0
  # ewindowms = 50      # WHY THESE VALUES? NEED TO BE CHANGED? 
  # windoms = ewindowms - swindowms

  # (iii) Get tts (removeBadEpochs <-- )
  # FILL THIS IN!!! 

  # (iv) Get averages 
  # ttavg,avgCSD = getAvgERP(CSD_data, sampr, tts, swindowms, ewindowms) ## NEED TO ATTEND TO tts




  ##### (4) INTERPOLATION #####
  X = sim.allSimData['t']
  Y = range(CSD_data.shape[0])
  CSD_spline=scipy.interpolate.RectBivariateSpline(Y, X, CSD_data)
  Y_plot = np.linspace(0,CSD_data.shape[0],num=1000) # SURE ABOUT SHAPE? NUM? 
  Z = CSD_spline(Y_plot, X)



  ##### (5) SET UP PLOTTING #####

  # (i) Set up axes 
  xmin = 0 
  xmax = int(sim.allSimData['t'][-1])     # why this index? and also, need to resolve ttavg <--
  ymin = 1    # where does this come from? 
  ymax = 24   # where does this come from?
  extent_xy = [xmin, xmax, ymax, ymin]

  # (ii) Make the outer grid
  fig = plt.figure(figsize=(10, 8))
  numplots=1
  gs_outer = matplotlib.gridspec.GridSpec(2, 4, figure=fig, wspace=0.4, hspace=0.2, height_ratios = [20, 1])

  # (iii) Title
  fig.suptitle('CSD in A1')            #("Averaged Laminar CSD (n=%d) in A1 after 40 dB stimuli"%len(tts))

  # (iii) Create subplots w/ common axis labels and tick marks
  axs = []
  for i in range(numplots):
    axs.append(plt.Subplot(fig,gs_outer[i*2:i*2+2]))
    fig.add_subplot(axs[i])
    axs[i].set_yticks(np.arange(1, 24, step=1))
    axs[i].set_ylabel('Contact', fontsize=12)
    axs[i].set_xlabel('Time (ms)',fontsize=12)
    axs[i].set_xticks(np.arange(0, 60, step=10))

  # (iv)
  spline=axs[0].imshow(Z, extent=extent_xy, interpolation='none', aspect='auto', origin='upper', cmap='jet_r')
  axs[0].set_title('RectBivariateSpline',fontsize=12)

  height = axs[0].get_ylim()[0]
  perlayer_height = int(height/avgCSD.shape[0])
  xmin = axs[0].get_xlim()[0]
  xmax = axs[0].get_xlim()[1]
  for i,val in enumerate(values):
    if start_or_end[i] == "start":
      axs[0].hlines(values[i]+0.02, xmin, xmax, colors='black', linestyles='dashed')
      axs[0].text(2, values[i]+0.7, sink_or_source[i], fontsize=10)
    else:
      axs[0].hlines(values[i]+1.02, xmin, xmax, colors='black', linestyles='dashed')


  # COLORBAR
  ## FILL THIS IN

  # DISPLAY FINAL FIGURE
  plt.show()




  ## CODE FROM GRAPH.PY, FROM SAM, lines 76-99:
  # plot 3: CSD w/ same smoothing as Sherman et al. 2016
# X = ttavg
# Y = range(avgCSD.shape[0])
# CSD_spline=scipy.interpolate.RectBivariateSpline(Y, X, avgCSD)
# Y_plot = np.linspace(0,avgCSD.shape[0],num=1000)
# Z = CSD_spline(Y_plot, X)
# #Z = np.clip(Z, -Z.max(), Z.max())
# ​
# spline=axs[0].imshow(Z, extent=extent_xy, interpolation='none', aspect='auto', origin='upper', cmap='jet_r')
# axs[0].set_title('RectBivariateSpline',fontsize=12)
# ​
# height = axs[0].get_ylim()[0]
# perlayer_height = int(height/avgCSD.shape[0])
# xmin = axs[0].get_xlim()[0]
# xmax = axs[0].get_xlim()[1]
# for i,val in enumerate(values):
#     if start_or_end[i] == "start":
#       axs[0].hlines(values[i]+0.02, xmin, xmax,
#                 colors='black', linestyles='dashed')
#       axs[0].text(2, values[i]+0.7, sink_or_source[i], fontsize=10)
#     else:
#       axs[0].hlines(values[i]+1.02, xmin, xmax,
#                 colors='black', linestyles='dashed')


# NOTE ON COLORS: 
# # when drawing CSD make sure that negative values (depolarizing intracellular current) drawn in red,
# # and positive values (hyperpolarizing intracellular current) drawn in blue




##################################################
################ UNUSED FUNCTIONS ################
##################################################

## These are from Sam Neymotin; https://github.com/NathanKlineInstitute/OEvent/blob/master/csd.py


### LOWPASS FILTER ###

# # lowpass filter the items in lfps. lfps is a list or numpy array of LFPs arranged spatially by column
# def getlowpass (lfps,sampr,maxf):
#   datlow = []
#   for i in range(len(lfps[0])): datlow.append(lowpass(lfps[:,i],maxf,df=sampr,zerophase=True))
#   datlow = np.array(datlow)
#   return datlow


### BIPOLAR WAVEFORMS ###

# # get bipolar waveforms - first do a lowpass filter. lfps is a list or numpy array of LFPs arranged spatially by column
# # spacing_um is electrode's contact spacing in units of micron
# # returns bipolar signal in units of mV/mm (assuming lfps are in mV)
# def getBipolar (lfps,sampr,spacing_um=100.0,minf=0.05,maxf=300,norm=True,vaknin=False):
#   datband = getbandpass(lfps,sampr,minf,maxf)
#   if datband.shape[0] > datband.shape[1]: # take CSD along smaller dimension
#     ax = 1
#   else:
#     ax = 0
#   if vaknin: datband = Vaknin(datband)    
#   if norm: removemean(datband,ax=ax)    
#   # can change to run Vaknin on bandpass filtered LFPs before calculating bipolar waveforms, that
#   # way would have same number of channels in bipolar and LFP (but not critical, and would take more RAM);
#   # also might want to subtract mean of each channel before calculating the diff ?
#   spacing_mm = spacing_um/1000 # spacing in mm
#   bipolar = -np.diff(datband,n=1,axis=ax)/spacing_mm # now each column (or row) is an electrode -- bipolar along electrodes
#   return bipolar


### MULTI-UNIT ACTIVITY ###

# # get MUA - first do a bandpass filter then rectify. 
# #  lfps is a list or numpy array of LFPs arranged spatially by column
# def getMUA (lfps,sampr,minf=300,maxf=5000):
#   datband = getbandpass(lfps,sampr,minf,maxf)
#   return np.abs(datband)