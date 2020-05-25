"""
Functions to plot and extract CSD info from LFP data
Contributors: Erica Y Griffith, Sam Neymotin, Salvador Dura-Bernal
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import
### THIS SET OF IMPORTS FROM FUTURE IS IN lfp.py, traces.py, and spikes.py

# THIRD PARTY IMPORTS
import numpy as np
from future import standard_library
standard_library.install_aliases()

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
    if datband.shape[0] > datband.shape[1]: # take CSD along smaller dimension
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

def plotCSD():
  print('Plotting CSD... ') # NO PLOT YET 
  sim_data = sim.allSimData.keys()

  if 'CSD' in sim_data:
    print('CSD values have already been extracted from LFP by getCSD()')
  else:
    sim.analysis.getCSD() # WHAT ABOUT ARGS? 

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