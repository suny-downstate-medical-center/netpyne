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
from numbers import Number
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
from .filter import lowpass, bandpass
from .utils import exception, _saveFigData


def getBandpass(
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

def vakninCorrection(x):
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

def removeMean(x, ax=1):
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
    saveData=True,
    getAllData=True,
    **kwargs
):
 

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

    saveData : bool
        Saves CSD data to sim object
        **Default:** ``True``

    getAllData : bool
        Returns CSDData as well as LFPData, sampr, spacing_um, and dt
        **Default:** ``True``
    """

    print('Preparing CSD data... ')

    if not sim:
        try:
            from .. import sim
        except:
            raise Exception('Cannot access sim')


    ## Get LFP data from sim and instantiate as a numpy array 
    simDataCategories = sim.allSimData.keys()
    
    if pop is None:
        if 'LFP' in simDataCategories:
            LFPData = np.array(sim.allSimData['LFP'])
        else:
            raise Exception('NO LFP DATA!! Need to re-run simulation with cfg.recordLFP enabled')
    else:
        if 'LFPPops' in simDataCategories:
            simLFPPops = sim.allSimData['LFPPops'].keys()
            if pop in simLFPPops:
                LFPData = sim.allSimData['LFPPops'][pop]
            else:
                raise Exception('No LFP data for ' + str(pop) + ' cell pop; CANNOT GENERATE CSD DATA OR PLOT')
        else:
            raise Exception('No pop-specific LFP data recorded! CANNOT GENERATE POP-SPECIFIC CSD DATA OR PLOT')

    # time step used in simulation recording (in ms)
    if dt is None:
        dt = sim.cfg.recordStep

    # slice data by timeRange, if relevant 
    if timeRange is None:
        timeRange = [0, sim.cfg.duration]
    else:
        LFPData = LFPData[int(timeRange[0] / sim.cfg.recordStep) : int(timeRange[1] / sim.cfg.recordStep), :]

    # Sampling rate of data recording during the simulation
    if sampr is None:
        # divide by 1000.0 to turn denominator from units of ms to s
        sampr = 1.0 / (dt / 1000.0)  # dt == sim.cfg.recordStep, unless specified otherwise by user


    # Spacing between electrodes (in microns)
    if spacing_um is None:
        # if not specified, use average spacing along y coord (depth)
        yCoords = np.array(sim.cfg.recordLFP)[:,1]
        spacing_um = (yCoords.max() - yCoords.min()) / (len(yCoords) - 1)

    # Convert spacing from microns to mm
    spacing_mm = spacing_um / 1000

    # print('dt, sampr, spacing_um, spacing_mm values determined')

    # Bandpass filter the LFP data with getBandpass() fx defined above
    datband = getBandpass(LFPData, sampr, minf, maxf)
    # now each row is an electrode - `datband` shape is (N_electrodes, N_timesteps)

    # Vaknin correction
    if vaknin:
        datband = vakninCorrection(datband)

    # norm data
    if norm:
        removeMean(datband, ax=0)

    # take CSD along electrodes dimension
    CSDData = -np.diff(datband, n=2, axis=0) / spacing_mm**2

    ##### SAVE DATA #######
    # Add CSDData to sim.allSimData for later access
    if saveData:
        if pop is None:
            sim.allSimData['CSD'] = CSDData
        else:
            sim.allSimData['CSDPops'] = {}
            sim.allSimData['CSDPops'][pop] = CSDData

    # return CSD_data or all data
    if getAllData:
        return CSDData, LFPData, sampr, spacing_um, dt
    else:
        from .lfp import prepareDataPerElectrode
        CSDData = CSDData.T # to match the shape expected by prepareDataPerElectrode
        return prepareDataPerElectrode(CSDData, electrodes, timeRange, sim)
