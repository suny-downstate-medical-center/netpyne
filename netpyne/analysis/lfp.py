"""
Module for analyzing LFP-related results

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from builtins import range
from builtins import round
from builtins import str
try:
    basestring
except NameError:
    basestring = str

from future import standard_library
standard_library.install_aliases()
from netpyne import __gui__

if __gui__:
    import matplotlib.pyplot as plt
    from matplotlib import mlab
import numpy as np
from numbers import Number
from .utils import colorList, exception, _saveFigData, _showFigure, _smooth1d
from ..support.scalebar import add_scalebar


#@exception
def prepareLFP(
    sim=None,
    timeRange=None,
    electrodes=['avg', 'all'],
    pop=None,
    LFPData=None, 
    logx=False, 
    logy=False, 
    normSignal=False, 
    filtFreq=False, 
    filtOrder=3, 
    detrend=False,
    **kwargs):

    """
    Function to prepare data for plotting of local field potentials (LFP)
    """

    print('Preparing LFP data...')

    if not sim:
        from .. import sim

    # create the output data dictionary
    data = {}
    data['electrodes'] = {}
    data['electrodes']['names'] = []
    data['electrodes']['locs'] = []
    data['electrodes']['lfps'] = []

    # set time range
    if timeRange is None:
        timeRange = [0, sim.cfg.duration]

    # create an array of the time steps
    t = np.arange(timeRange[0], timeRange[1], sim.cfg.recordStep)
    data['t'] = t

    # accept input lfp data
    if LFPData is not None:
        # loading LFPData is not yet functional
        lfp = LFPData[int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep),:]
    else:
        if pop and pop in sim.allSimData['LFPPops']:
            lfp = np.array(sim.allSimData['LFPPops'][pop])[int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep),:]     
        else:
            lfp = np.array(sim.allSimData['LFP'])[int(timeRange[0]/sim.cfg.recordStep):int(timeRange[1]/sim.cfg.recordStep),:]

    # filter the signals
    if filtFreq:
        from scipy import signal
        fs = 1000.0/sim.cfg.recordStep
        nyquist = fs/2.0
        if isinstance(filtFreq, list): # bandpass
            Wn = [filtFreq[0]/nyquist, filtFreq[1]/nyquist]
            b, a = signal.butter(filtOrder, Wn, btype='bandpass')
        elif isinstance(filtFreq, Number): # lowpass
            Wn = filtFreq/nyquist
            b, a = signal.butter(filtOrder, Wn)
        for i in range(lfp.shape[1]):
            lfp[:,i] = signal.filtfilt(b, a, lfp[:,i])

    # detrend the signals
    if detrend:
        from scipy import signal
        for i in range(lfp.shape[1]):
            lfp[:,i] = signal.detrend(lfp[:,i])

    # normalize the signals
    if normSignal:
        for i in range(lfp.shape[1]):
            offset = min(lfp[:,i])
            if offset <= 0:
                lfp[:,i] += abs(offset)
            lfp[:,i] /= max(lfp[:,i])

    # electrode preparation
    if 'all' in electrodes:
        electrodes.remove('all')
        electrodes.extend(list(range(int(sim.net.recXElectrode.nsites))))
    
    # if 'avg' in electrodes:
    #     electrodes.remove('avg')
    #     data['electrodes']['names'].append('avg')
    #     data['electrodes']['locs'].append(None)
    #     data['electrodes']['lfps'].append(np.mean(lfp, axis=1))

    for i, elec in enumerate(electrodes):
        
        if isinstance(elec, Number) and (LFPData is not None or elec <= sim.net.recXElectrode.nsites):
            lfpSignal = lfp[:, elec]
            loc = sim.cfg.recordLFP[elec]
        elif elec == 'avg':
            lfpSignal = np.mean(lfp, axis=1)
            loc = None
        elif isinstance(elec, list) and (LFPData is not None or all([x <= sim.net.recXElectrode.nsites for x in elec])):
                lfpSignal = np.mean(lfp[:, elec], axis=1)
                loc = None

        if len(t) < len(lfpSignal):
            lfpSignal = lfpSignal[:len(t)]

        data['electrodes']['names'].append(str(elec))
        data['electrodes']['locs'].append(loc)
        data['electrodes']['lfps'].append(lfpSignal)

    #data['electrodes']['lfps'] = np.transpose(np.array(data['electrodes']['lfps']))

    return data


#@exception
def preparePSD(
    LFPData=None, 
    sim=None,
    timeRange=None,
    electrodes=['avg', 'all'], 
    pop=None,
    NFFT=256, 
    noverlap=128, 
    nperseg=256, 
    minFreq=1, 
    maxFreq=100, 
    stepFreq=1, 
    smooth=0,
    logx=False, 
    logy=False, 
    normSignal=False, 
    normPSD=False, 
    filtFreq=False, 
    filtOrder=3, 
    detrend=False, 
    transformMethod='morlet', 
    **kwargs):
    """
    Function to prepare data for plotting of power spectral density (PSD)
    """

    if not sim:
        from .. import sim

    data = prepareLFP(
        sim=sim,
        timeRange=timeRange,
        electrodes=electrodes,
        pop=pop,
        LFPData=LFPData, 
        logy=logy, 
        normSignal=normSignal, 
        filtFreq=filtFreq, 
        filtOrder=filtOrder, 
        detrend=detrend,
        **kwargs)

    print('Preparing PSD data...')

    names = data['electrodes']['names']
    lfps = data['electrodes']['lfps']

    allFreqs = []
    allSignal = []
    allNames = []

    # Used in both transforms
    fs = int(1000.0/sim.cfg.recordStep)
    
    for index, lfp in enumerate(lfps):

        # Morlet wavelet transform method
        if transformMethod == 'morlet':
            
            from ..support.morlet import MorletSpec, index2ms
            morletSpec = MorletSpec(lfp, fs, freqmin=minFreq, freqmax=maxFreq, freqstep=stepFreq)
            freqs = morletSpec.f
            spec = morletSpec.TFR
            signal = np.mean(spec, 1)
            ylabel = 'Power'

        # FFT transform method
        elif transformMethod == 'fft':
            
            power = mlab.psd(lfp, Fs=fs, NFFT=NFFT, detrend=mlab.detrend_none, window=mlab.window_hanning, noverlap=noverlap, pad_to=None, sides='default', scale_by_freq=None)

            if smooth:
                signal = _smooth1d(10 * np.log10(power[0]), smooth)
            else:
                signal = 10 * np.log10(power[0])
            freqs = power[1]
            ylabel = 'Power (dB/Hz)'

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



#@exception
def prepareSpectrogram(
    sim=None,
    timeRange=None,
    electrodes=['avg', 'all'], 
    LFPData=None, 
    NFFT=256, 
    noverlap=128, 
    nperseg=256, 
    minFreq=1, 
    maxFreq=100, 
    stepFreq=1, 
    smooth=0, 
    includeAxon=True, 
    logx=False, 
    logy=False, 
    normSignal=False, 
    normPSD=False, 
    normSpec=False, 
    filtFreq=False, 
    filtOrder=3, 
    detrend=False, 
    transformMethod='morlet', 
    **kwargs):
    """
    Function to prepare data for plotting of the spectrogram
    """

    data = prepareLFP(
    sim=sim,
    timeRange=timeRange,
    electrodes=electrodes, 
    LFPData=LFPData, 
    NFFT=NFFT, 
    noverlap=noverlap, 
    nperseg=nperseg, 
    minFreq=minFreq, 
    maxFreq=maxFreq, 
    stepFreq=stepFreq, 
    smooth=smooth, 
    includeAxon=includeAxon, 
    logy=logy, 
    normSignal=normSignal, 
    normPSD=normPSD, 
    normSpec=normSpec, 
    filtFreq=filtFreq, 
    filtOrder=filtOrder, 
    detrend=detrend, 
    transformMethod=transformMethod, 
    **kwargs)

    print('Preparing spectrogram data...')

    if not sim:
        from .. import sim

    if not timeRange:
        timeRange = [0, sim.cfg.duration]

    lfps = np.array(data['electrodes']['lfps'])
    names = data['electrodes']['names']
    electrodes = data['electrodes']

    spect_data = {}
    spect_data['vmin'] = None
    spect_data['vmax'] = None

    # Morlet wavelet transform method
    if transformMethod == 'morlet':
        
        from ..support.morlet import MorletSpec, index2ms

        fs = int(1000.0/sim.cfg.recordStep)

        spec = []
        spect_data['morlet'] = []
        spect_data['extent'] = []

        freqList = None
        if logy:
            freqList = np.logspace(np.log10(minFreq), np.log10(maxFreq), int((maxFreq-minFreq)/stepFreq))

        for i, elec in enumerate(names):
            lfp_elec = lfps[i, :]
            t_spec = np.linspace(0, index2ms(len(lfp_elec), fs), len(lfp_elec))
            spec.append(MorletSpec(lfp_elec, fs, freqmin=minFreq, freqmax=maxFreq, freqstep=stepFreq, lfreq=freqList))

        vmin = np.array([s.TFR for s in spec]).min()
        vmax = np.array([s.TFR for s in spec]).max()

        if normSpec:
            vmin = 0
            vmax = 1

        spect_data['vmin'] = vmin
        spect_data['vmax'] = vmax

        for i, elec in enumerate(names):
            T = timeRange
            F = spec[i].f
            if normSpec:
                S = spec[i].TFR / vmax
            else:
                S = spec[i].TFR
            spect_data['morlet'].append(S)
            spect_data['extent'].append([np.amin(T), np.amax(T), np.amin(F), np.amax(F)])
            
    # FFT transform method
    elif transformMethod == 'fft':

        from scipy import signal as spsig
        
        spect_data['fft'] = []

        for i, elec in enumerate(names):
            lfp_elec = lfps[:, i]
            fs = int(1000.0/sim.cfg.recordStep)
            f, t_spec, x_spec = spsig.spectrogram(lfp_elec, fs=fs, window='hanning', detrend=mlab.detrend_none, nperseg=nperseg, noverlap=noverlap, nfft=NFFT,  mode='psd')
            x_mesh, y_mesh = np.meshgrid(t_spec*1000.0, f[f<maxFreq])
            spect_data['fft'].append(10*np.log10(x_spec[f<maxFreq]))

        vmin = np.array(spect_data['fft']).min()
        vmax = np.array(spect_data['fft']).max()
        
        spect_data['vmin'] = vmin
        spect_data['vmax'] = vmax

        spect_data['xmesh'] = x_mesh
        spect_data['ymesh'] = y_mesh

        #for i, elec in enumerate(electrodes):
        #    plt.pcolormesh(x_mesh, y_mesh, spec[i], cmap=cm.viridis, vmin=vmin, vmax=vmax)
            
    data['electrodes']['spectrogram'] = spect_data

    return data
    