"""
Module with functions to extract and plot CSD info from LFP data

"""

# from __future__ import print_function
# from __future__ import division
# from __future__ import unicode_literals
# from __future__ import absolute_import

# from future import standard_library
# standard_library.install_aliases()

# try:
#     basestring
# except NameError:
#     basestring = str

import numpy as np
from numbers import Number
# import scipy

# import matplotlib 
# from matplotlib import pyplot as plt 
# from matplotlib import ticker as ticker
# import json
# import sys
# import os
# from collections import OrderedDict  
# import warnings 
# from scipy.fftpack import hilbert
# from scipy.signal import cheb2ord, cheby2, convolve, get_window, iirfilter, remez, decimate
from .filter import lowpass,bandpass
from .utils import exception, _saveFigData 



def getbandpass(
    lfps, 
    sampr, 
    minf=0.05, 
    maxf=300):
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



@exception
def prepareCSD(
    sim=None,
    timeRange=None,
    electrodes=['avg', 'all'],
    pop=None,
    dt=None, 
    sampr=None,
    spacing_um=None,
    minf=0.05, 
    maxf=300, 
    vaknin=True,
    norm=False,
    **kwargs):


    """
    Function to prepare data for plotting of current source density (CSD) data

    Parameters
    ----------
    sim : NetPyNE object
        **Default:** ``None``

    timeRange: list 
        List of length two, with timeRange[0] as beginning of desired timeRange, and timeRange[1] as the end
        **Default:** ``None`` retrieves timeRange = [0, sim.cfg.duration]

    electrodes : list of electrodes to look at CSD data 
        **Default:** ['avg', 'all']

    pop : str
        Retrieves CSD data from a specific cell population
        **Default:** ``None`` retrieves overall CSD data 

    dt : float or int
        Time between recording points (ms). 
        **Default:** ``None`` uses ``sim.cfg.recordStep`` from the current NetPyNE sim object.

    sampr : float or int
        Sampling rate for data recording (Hz). 
        **Default:** ``None`` uses ``1.0/sim.cfg.recordStep`` from the current NetPyNE sim object. 

    spacing_um : float or int
        Electrode contact spacing in units of microns.
        **Default:** ``None`` pulls the information from the current NetPyNE sim object.  If the data is empirical, defaults to ``100`` (microns).

    minf : float or int
        Minimum frequency for bandpassing the LFP data. 
        **Default:** ``0.05``

    maxf : float or int
        Maximum frequency for bandpassing the LFP data. 
        **Default:** ``300``

    vaknin : bool 
        Allows CSD to be performed on all N contacts instead of N-2 contacts
        **Default:** ``True``

    norm : bool 
        Subtracts the mean from the CSD data
        **Default:** ``False`` --> ``True``

    """

    print('Preparing CSD data... ')

    if not sim:
        try:
            from .. import sim
        except:
            raise Exception('Cannot access sim')


    # ## Get LFP data from sim and instantiate as a numpy array 
    # simDataCategories = sim.allSimData.keys()
    
    # if pop is None:
    #     if 'LFP' in simDataCategories:
    #         LFPData = np.array(sim.allSimData['LFP'])
    #     else:
    #         raise Exception('NO LFP DATA!! Need to re-run simulation with cfg.recordLFP enabled')
    # else:
    #     if 'LFPPops' in simDataCategories:
    #         simLFPPops = sim.allSimData['LFPPops'].keys()
    #         if pop in simLFPPops:
    #             LFPData = sim.allSimData['LFPPops'][pop]
    #         else:
    #             raise Exception('No LFP data for ' + str(pop) + ' cell pop; CANNOT GENERATE CSD DATA OR PLOT')
    #     else:
    #         raise Exception('No pop-specific LFP data recorded! CANNOT GENERATE POP-SPECIFIC CSD DATA OR PLOT')


    # Retrieve LFP data from sim
    if pop and pop in sim.allSimData['LFPPops']:
        lfpData = np.array(sim.allSimData['LFPPops'][pop])    
    else:
        lfpData = np.array(sim.allSimData['LFP'])


    # time step used in simulation recording (in ms)
    if dt is None:
        dt = sim.cfg.recordStep

    # Calculate the sampling rate of data recording during the simulation 
    if sampr is None:
        # divide by 1000.0 to turn denominator from units of ms to s
        sampr = 1.0/(dt/1000.0) # dt == sim.cfg.recordStep, unless specified otherwise by user 


    # Bandpass filter the LFP data with getbandpass() fx defined above
    datband = getbandpass(lfpData,sampr,minf,maxf) 

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


    # Spacing between electrodes (in microns)
    if spacing_um is None:
        spacing_um = sim.cfg.recordLFP[1][1] - sim.cfg.recordLFP[0][1]
    
    # Convert spacing from microns to mm 
    spacing_mm = spacing_um/1000



    # now each column (or row) is an electrode -- take CSD along electrodes
    CSDData = -np.diff(datband, n=2, axis=ax)/spacing_mm**2  


    # Splice CSD data by timeRange, if relevant 
    if timeRange is None:
        timeRange = [0, sim.cfg.duration]
    else:
        # lfpData = lfpData[int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep),:]
        CSDData = CSDData[:,int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep)]


    # create the output data dictionary
    data = {}
    data['electrodes'] = {}
    data['electrodes']['names'] = []
    data['electrodes']['locs'] = []
    data['electrodes']['csds'] = []

    # create an array of the time steps and store in output data 
    t = np.arange(timeRange[0], timeRange[1], sim.cfg.recordStep)
    data['t'] = t


    # electrode preparation (add average if needed)
    if 'all' in electrodes:
        electrodes.remove('all')
        electrodes.extend(list(range(int(sim.net.recXElectrode.nsites))))

    for i, elec in enumerate(electrodes):
        if elec == 'avg':
            csdSignal = np.mean(CSDData, axis=0)
            loc = None
        elif isinstance(elec, Number) and elec <= sim.net.recXElectrode.nsites:
            csdSignal = CSDData[elec,:] 
            loc = sim.cfg.recordLFP[elec]


        data['electrodes']['names'].append(str(elec))
        data['electrodes']['locs'].append(loc)
        data['electrodes']['csds'].append(csdSignal) ## <-- this can be turned into an array with np.array(data['electrodes']['csds'] -- NOTE: first row will be average -- data['electrodes']['csds'][0])

    ## testing line 
    data['CSDData'] = CSDData
    ### NOTE: 
    ### csd = np.array(data['electrodes']['csds'])
    ### csd = np.array(csd)
    ### csd[1:, :] == CSDData['CSDData']   ---> True, True, True... True 

    return data 


@exception
def prepareCSDPSD(
    CSDData=None, 
    sim=None,
    timeRange=None,
    electrodes=['avg', 'all'], 
    pop=None,
    minFreq=1, 
    maxFreq=100, 
    stepFreq=1, 
    normSignal=False, 
    normPSD=False, 
    transformMethod='morlet', 
    **kwargs
    ):

    """
    Function to prepare data for plotting of power spectral density (PSD) of current source density (CSD)
    """


    ## OLD ARGS --> 
    #   NFFT=256, 
    #   noverlap=128, 
    #   nperseg=256, 
    #   smooth=0,
    #   logy=False, 
    ##  --> These were args in preparePSD for LFP but I bet these won't be relevant --> 
    #   filtFreq=False, 
    #   filtOrder=3, 
    #   detrend=False, 



    if not sim:
        from .. import sim


    data = prepareCSD(
        sim=sim,
        electrodes=electrodes,
        timeRange=timeRange,
        pop=pop,
        **kwargs)

    # prepareCSD args covered under kwargs --> 
        # dt=dt, 
        # sampr=sampr,
        # spacing_um=spacing_um,
        # minf=minf,
        # maxf=maxf,
        # vaknin=vaknin,
        # norm=norm,

    print('Preparing PSD CSD data...')


    names = data['electrodes']['names']
    csds = data['electrodes']['csds']       # KEEP IN MIND THAT THE FIRST [0] IS AVERAGE ELECTRODE!!! 

    allFreqs = []
    allSignal = []
    allNames = []


    # Used in both transforms
    fs = int(1000.0/sim.cfg.recordStep)


    for index, csd in enumerate(csds):

        # Morlet wavelet transform method
        if transformMethod == 'morlet':
            
            from ..support.morlet import MorletSpec, index2ms
            morletSpec = MorletSpec(csd, fs, freqmin=minFreq, freqmax=maxFreq, freqstep=stepFreq)
            freqs = morletSpec.f
            spec = morletSpec.TFR
            signal = np.mean(spec, 1)
            ylabel = 'Power'


        allFreqs.append(freqs)
        allSignal.append(signal)
        allNames.append(names[index])

    if normPSD:
        vmax = np.max(allSignal)
        for index, signal in enumerate(allSignal):
            allSignal[index] = allSignal[index]/vmax


    psdFreqs = []
    psdSignal = []

    for index, name in enumerate(names):
        freqs = allFreqs[index]
        signal = allSignal[index]
        
        psdFreqs.append(freqs[freqs<maxFreq])
        psdSignal.append(signal[freqs<maxFreq])

    data = {}
    data['psdFreqs'] = psdFreqs
    data['psdSignal'] = psdSignal
    data['psdNames'] = names

    return data


### FUTURE WORK --> DEFINE FUNCTION prepareSpectrogram() ### 
# @exception
# def prepareSpectrogram(
#     sim=None,
#     timeRange=None,
#     electrodes=['avg', 'all'], 
#     pop=None,
#     CSDData=None, 
#     minFreq=1, 
#     maxFreq=100, 
#     stepFreq=1, 
#     normSignal=False, 
#     normPSD=False, 
#     normSpec=False, 
#     transformMethod='morlet', 
#     **kwargs):

#     """
#     Function to prepare data for plotting of the spectrogram
#     """














