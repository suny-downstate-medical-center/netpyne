"""
analysis/csd.py

current source density approximation using second spatial derivative of local field potential

 Written by Sam Neymotin (NKI)
 Vaknin function written by Max Sherman (Brown University)
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

def Vaknin(x):
    """
    Vaknin correction for CSD analysis (Max Sherman [Brown U] implementation)
    Allows CSD to be performed on all N contacts instead of N-2 contacts
    See Vaknin et al (1989) for more details
    """
    # Preallocate array with 2 more rows than input array
    x_new = np.zeros((x.shape[0]+2, x.shape[1]))
    # print x_new.shape
    # Duplicate first and last row of x into first and last row of x_new
    x_new[0, :] = x[0, :]
    x_new[-1, :] = x[-1, :]
    # Duplicate all of x into middle rows of x_neww
    x_new[1:-1, :] = x
    return x_new

def removemean(x, ax=1):
    # remove the mean from each dimension of x
    mean = np.mean(x, axis=ax, keepdims=True)
    x -= mean

def getCSD(lfps,sampr,minf=0.05,maxf=300,norm=True,vaknin=False,spacing=1.0):
    """
    get current source density approximation using set of local field potentials with equidistant spacing
    first performs a lowpass filter
    lfps is a list or numpy array of LFPs arranged spatially by column
    spacing is in microns
    """
    datband = getbandpass(lfps,sampr,minf,maxf)
    if datband.shape[0] > datband.shape[1]: # take CSD along smaller dimension
        ax = 1
    else:
        ax = 0
    # can change default to run Vaknin on bandpass filtered LFPs before calculating CSD, that
    # way would have same number of channels in CSD and LFP (but not critical, and would take more RAM);
    if vaknin: datband = Vaknin(datband)
    if norm: removemean(datband,ax=ax)
    # NB: when drawing CSD make sure that negative values (depolarizing intracellular current) drawn in red,
    # and positive values (hyperpolarizing intracellular current) drawn in blue
    CSD = -numpy.diff(datband,n=2,axis=ax) / spacing**2 # now each column (or row) is an electrode -- CSD along electrodes
    return CSD
