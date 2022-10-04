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


@exception
def prepareCSD(
    LFP_input_data=None, 
    LFP_input_file=None, 
    sampr=None, 
    dt=None, 
    spacing_um=None, 
    minf=0.05, 
    maxf=300, 
    norm=True, 
    vaknin=True, 
    save_to_sim=True, 
    getAllData=False,
    **kwargs): 
    ## Output data that can be used for plotting (plotting/plotCSD.py)
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

    print('Preparing CSD data')


    ### DEFAULT -- CONDITION 1 : LFP DATA COMES FROM SIMULATION ###

    # Get LFP data from simulation
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
            sampr = 1.0/(dt/1000.0) # sim.cfg.recordStep --> == dt

        # Spacing between electrodes (in microns)
        if spacing_um is None:
            spacing_um = sim.cfg.recordLFP[1][1] - sim.cfg.recordLFP[0][1]

        ## This retrieves: 
        #   lfp_data (as an array)
        #   dt --> recording time step (in ms)
        #   sampr --> sampling rate of data recording (in Hz)
        #   spacing_um --> spacing btwn electrodes (in um)



    ### CONDITION 2 : LFP DATA FROM SIM .JSON FILE ###     # Note: need to expand capability to include a list of multiple files 
  
    # load sim data from JSON file
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

        ## This retrieves: 
        #   lfp_data (as a list)
        #   dt --> recording time step (in ms)
        #   sampr --> sampling rate of data recording (in Hz)
        #   spacing_um --> spacing btwn electrodes (in um)



    ### CONDITION 3 : ARBITRARY LFP DATA ###    # NOTE: for condition 3 --> need to also retrieve the dt, sampr, and spacing_um !!

    # get lfp_data and cast as numpy array
    elif len(LFP_input_data) > 0 and LFP_input_file is None:
        lfp_data = np.array(LFP_input_data)


    ####################################

    # Convert spacing from microns to mm 
    spacing_mm = spacing_um/1000

    # Bandpass filter the LFP data with getbandpass() fx defined above
    datband = getbandpass(lfp_data,sampr,minf,maxf) 

    # Take CSD along smaller dimension
    if datband.shape[0] > datband.shape[1]:
        ax = 1
    else:
        ax = 0
    print('ax = ' + str(ax))

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


# returns CSD in units of mV/mm**2 (assuming lfps are in mV)
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

    ### DEFAULT -- CONDITION 1 : LFP DATA COMES FROM SIMULATION ###

    # Get LFP data from simulation
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
            sampr = 1.0/(dt/1000.0) # sim.cfg.recordStep --> == dt

        # Spacing between electrodes (in microns)
        if spacing_um is None:
            spacing_um = sim.cfg.recordLFP[1][1] - sim.cfg.recordLFP[0][1]

        ## This retrieves: 
        #   lfp_data (as an array)
        #   dt --> recording time step (in ms)
        #   sampr --> sampling rate of data recording (in Hz)
        #   spacing_um --> spacing btwn electrodes (in um)



    ### CONDITION 2 : LFP DATA FROM SIM .JSON FILE ###     # Note: need to expand capability to include a list of multiple files 
  
    # load sim data from JSON file
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

        ## This retrieves: 
        #   lfp_data (as a list)
        #   dt --> recording time step (in ms)
        #   sampr --> sampling rate of data recording (in Hz)
        #   spacing_um --> spacing btwn electrodes (in um)



    ### CONDITION 3 : ARBITRARY LFP DATA ###    # NOTE: for condition 3 --> need to also retrieve the dt, sampr, and spacing_um !!

    # get lfp_data and cast as numpy array
    elif len(LFP_input_data) > 0 and LFP_input_file is None:
        lfp_data = np.array(LFP_input_data)


    ####################################

    # Convert spacing from microns to mm 
    spacing_mm = spacing_um/1000

    # Bandpass filter the LFP data with getbandpass() fx defined above
    datband = getbandpass(lfp_data,sampr,minf,maxf) 

    # Take CSD along smaller dimension
    if datband.shape[0] > datband.shape[1]:
        ax = 1
    else:
        ax = 0
    print('ax = ' + str(ax))

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



