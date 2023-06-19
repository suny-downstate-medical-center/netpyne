"""
Module with support for Morlet wavelets

Time-frequency representation using Morlet wavelets

 Original version written by Shane Lee (Brown University)
 Modified by Sam Neymotin (NKI; added phase calculations, saving/passing in Morlet, specifying different
 frequency steps and frequencies used for calculations (e.g. logarithmic frequency instead of linear)
 don't detrend the signal > 1 time; don't waste RAM by copying/storing time-series in MorletSpec class;
 subtract mean from time series within the wavelet class)
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import numpy as np
import scipy.signal as sps
import matplotlib.pyplot as plt


def index2ms(idx, sampr):
    return 1e3 * idx / sampr  # index to millisecond; sampr=sampling rate in Hz


def ms2index(ms, sampr):
    return int(sampr * ms / 1e3)  # millisecond to index; sampr=sampling rate in Hz


# calculate the Morlet wavelet for central frequency f
def Morlet(sampr, freq, width=7.0):
    """Morlet's wavelet for frequency f and time t
    Wavelet normalized so total energy is 1
    freq: specific frequency (Hz)
    width: number of cycles for the Morlet wavelet
    output returned: final units are 1/s
    """
    dt = 1.0 / sampr
    sf = freq / width  # sf in Hz
    st = 1.0 / (2.0 * np.pi * sf)  # st in s
    t = np.arange(-3.5 * st, 3.5 * st, dt)
    A = 1.0 / (st * np.sqrt(2.0 * np.pi))  # A in 1 / s
    # units: 1/s * (exp (s**2 / s**2)) * exp( 1/ s * s)
    return A * np.exp(-(t**2.0) / (2.0 * st**2.0)) * np.exp(1.0j * 2.0 * np.pi * freq * t)


# Return an array containing the energy as function of time for freq f
def MorletVec(sig, sampr, freq, width, m=None, getphase=False):
    """Final units of y: signal units squared. For instance, a signal of Am would have Am^2
    The energy is calculated using Morlet's wavelets; also returns phase when getphase==True
    sig: input signal
    sampr: sampling rate (Hz)
    freq: frequency
    m: Morlet wavelet
    width: number of cycles of Morlet wavelet
    """
    # calculate the morlet wavelet for this frequency
    # units of m are 1/s
    if m is None:
        m = Morlet(sampr, freq, width)
    # convolve wavelet with signal
    y = sps.fftconvolve(sig, m)
    if getphase:
        phs = np.angle(y)  # get phase too?
    # take the power ...
    y = (2.0 * abs(y) / sampr) ** 2.0
    i_lower = int(np.ceil(len(m) / 2.0))
    i_upper = int(len(y) - np.floor(len(m) / 2.0) + 1)
    if getphase:
        return y[i_lower:i_upper], phs[i_lower:i_upper]
    else:
        return y[i_lower:i_upper]


# MorletSpec class based on a time series vec tsvec
class MorletSpec:
    def __init__(self, tsvec, sampr, freqmin=1.0, freqmax=250.0, freqstep=1.0, width=7.0, getphase=False, lfreq=None):
        # Get Morlet Spectrogram from time-series (tsvec); lfreq is optional list of frequencies over which to calculate
        self.freqmin = freqmin  # minimum frequency of analysis
        self.freqmax = freqmax  # maximum frequency of analysis
        self.freqstep = freqstep  # frequency step for analysis
        if lfreq is not None:  # user-specified frequencies
            self.f = [freq for freq in lfreq]
            self.freqmin = min(self.f)
            self.freqmax = max(self.f)
        else:
            self.f = np.arange(
                self.freqmin, self.freqmax + 1, self.freqstep
            )  # Array of frequencies over which to calculate
        self.width = width  # Number of cycles in wavelet (>5 advisable)
        self.sampr = sampr  # sampling rate
        self.transform(tsvec, getphase)  # perform wavelet transform

    def plot_to_ax(self, ax_spec, dt):
        # plots spec to axis
        pc = ax_spec.imshow(self.TFR, aspect='auto', origin='upper', cmap=plt.get_cmap('jet'))
        return pc

    def transform(self, tsvec, getphase=False):
        # convert timeseries (tsvec) to wavelet spectrogram, optionally save wavelet phase
        sig = sps.detrend(tsvec - np.mean(tsvec))  # subtract mean and (linear) detrend the input time series
        self.t = np.linspace(0, 1e3 * len(sig) / self.sampr, len(sig))  # this is in ms
        self.TFR = np.zeros(
            (len(self.f), len(sig))
        )  # time frequency representation (spectrogram, organized by frequency)
        self.PHS = None  # wavelet phase time-series (organized by frequency)
        if getphase:
            self.PHS = np.zeros((len(self.f), len(sig)))
            for j, freq in enumerate(self.f):
                self.TFR[j, :], self.PHS[j, :] = MorletVec(sig, self.sampr, freq, self.width, getphase=True)
        else:
            for j, freq in enumerate(self.f):
                self.TFR[j, :] = MorletVec(sig, self.sampr, freq, self.width, getphase=False)
