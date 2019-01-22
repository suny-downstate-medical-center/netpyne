
"""
inputs.py 

Methods to create patterned spike inputs

Contributors: salvadordura@gmail.com
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from numbers import Number
try:
    basestring
except NameError:
    basestring = str

import numpy as np

def createRhythmicPattern(params, rand):
    ''' creates the ongoing external inputs (rhythmic)
    input params:
    - start: time of first spike. if -1, uniform distribution between startMin and startMax (ms)
    - startMin: minimum values of uniform distribution for start time (ms)
    - startMax: maximum values of uniform distribution for start time (ms)
    - startStd: standard deviation of normal distrinution for start time (ms); mean is set by start param. Only used if > 0.0      
    - freq: oscillatory frequency of rhythmic pattern (Hz)
    - freqStd: standard deviation of oscillatory frequency (Hz)
    - distribution: distribution type fo oscillatory frequencies; either 'normal' or 'uniform'
    - eventsPerCycle: spikes/burst per cycle; should be either 1 or 2
    - repeats: number of times to repeat input pattern (equivalent to number of inputs) 
    - stop: maximum time for last spike of pattern (ms)
    '''
    # start is always defined
    start = params['start']
    # If start is -1, randomize start time of inputs
    if start == -1:
        startMin = getattr(params, 'startMin', 25.)
        startMax = getattr(params, 'startMax', 125.)
        start = rand.uniform(startMin, startMax)
    elif getattr(params, 'startStd', -1) > 0.0: # randomize start time based on startStd
        start = rand.normal(start, params['startStd']) # start time uses different prng
    freq = getattr(params, 'freq', 0)
    freqStd = getattr(params, 'freqStd', 0)
    eventsPerCycle = getattr(params, 'eventsPerCycle', 2) 
    distribution = getattr(params, 'distribution', 'normal')
    if eventsPerCycle > 2 or eventsPerCycle <= 0:
        print("eventsPerCycle should be either 1 or 2, trying 2")
        eventsPerCycle = 2
    # If frequency is 0, create empty vector if input times
    if not freq:
        t_input = []
    elif distribution == 'normal':
        # array of mean stimulus times, starts at start
        isi_array = np.arange(start, params['stop'], 1000. / freq)
        # array of single stimulus times -- no doublets
        if freqStd:
            #t_array = [rand.normal(x, freqStd) for np.repeat(isi_array, params['repeats'])]  # not efficient!
            isi_array_repeat = np.repeat(isi_array, params['repeats'])
            stdvec = h.Vector(int(len(isi_array_repeat)))
            rand.normal(0, freqStd)
            stdvec.setrand(rand)
            t_array = np.array([mean+std for (mean,std) in zip(list(stdvec), isi_array_repeat)])
        else:
            t_array = isi_array
        if eventsPerCycle == 2: # spikes/burst in GUI
            # Two arrays store doublet times
            t_array_low = t_array - 5
            t_array_high = t_array + 5
            # Array with ALL stimulus times for input
            # np.append concatenates two np arrays
            t_input = np.append(t_array_low, t_array_high)
        elif eventsPerCycle == 1:
            t_input = t_array
        # brute force remove zero times. Might result in fewer vals than desired
        t_input = t_input[t_input > 0]
        t_input.sort()
    # Uniform Distribution
    elif distribution == 'uniform':
        n_inputs = params['repeats'] * freq * (params['tstop'] - start) / 1000.
        t_array = rand.uniform(start, params['tstop'], n_inputs)
        if eventsPerCycle == 2:
            # Two arrays store doublet times
            t_input_low = t_array - 5
            t_input_high = t_array + 5
            # Array with ALL stimulus times for input
            # np.append concatenates two np arrays
            t_input = np.append(t_input_low, t_input_high)
        elif eventsPerCycle == 1:
            t_input = t_array
        # brute force remove non-zero times. Might result in fewer vals than desired
        t_input = t_input[t_input > 0]
        t_input.sort()
    else:
        print("Indicated distribution not recognized. Not making any alpha feeds.")
        t_input = []
    return t_input

def createPoissonPattern(params):
    pass

def createGaussPattern(params):
    pass

