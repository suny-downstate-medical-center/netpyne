"""
Module for analyzing and plotting LFP-related results

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import os
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


def plotDipole(showCell=None, showPop=None, timeRange=None, dpi=300, figSize=(6, 6), showFig=True, saveFig=True):
    from .. import sim

    try:
        if showCell:
            p = sim.allSimData['dipoleCells'][showCell]
        elif showPop:
            p = sim.allSimData['dipolePops'][showPop]
        else:
            p = sim.allSimData['dipoleSum']
        
        # if list (as a result of side-effect of some of save-load operations), make sure to convert to np.array
        if isinstance(p, list):
            p = np.array(p)

        p = p / 1000.0  # convert from nA to uA
    except:
        print('Unable to collect dipole information...')

    if timeRange is None:
        timeRange = [0, sim.cfg.duration]

    timeSteps = [int(timeRange[0] / sim.cfg.recordStep), int(timeRange[1] / sim.cfg.recordStep)]

    # current dipole moment
    plt.figure(figsize=figSize)
    plt.plot(np.arange(timeRange[0], timeRange[1], sim.cfg.recordStep), np.array(p)[timeSteps[0] : timeSteps[1]])
    # plt.legend([r'$P_x$ (mA um)', r'$P_y$ (mA um)', r'$P_z$ (mA um)'])
    plt.legend([r'$P_x$', r'$P_y$', r'$P_z$'])
    plt.ylabel(r'$\mathbf{P}(t)$ ($\mu$A $\mu$m)')
    plt.xlabel('$t$ (ms)')
    ax = plt.gca()
    ax.grid(False)

    # save figure
    if saveFig:
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename + '_dipole.png'
        try:
            plt.savefig(filename, dpi=dpi)
        except:
            plt.savefig('dipole_fig.png', dpi=dpi)

    # display figure
    if showFig is True:
        plt.show()


def plotEEG(
    showCell=None,
    showPop=None,
    timeRange=None,
    dipole_location='parietal_lobe',
    dpi=300,
    figSize=(19, 10),
    showFig=True,
    saveFig=True,
):
    from .. import sim

    from lfpykit.eegmegcalc import NYHeadModel

    nyhead = NYHeadModel(nyhead_file=os.getenv('NP_LFPYKIT_HEAD_FILE', None))

    # dipole_location = 'parietal_lobe'  # predefined location from NYHead class
    nyhead.set_dipole_pos(dipole_location)
    M = nyhead.get_transformation_matrix()

    if showCell:
        p = sim.allSimData['dipoleCells'][showCell]
    elif showPop:
        p = sim.allSimData['dipolePops'][showPop]
    else:
        p = sim.allSimData['dipoleSum']

    if timeRange is None:
        timeRange = [0, sim.cfg.duration]

    timeSteps = [int(timeRange[0] / sim.cfg.recordStep), int(timeRange[1] / sim.cfg.recordStep)]

    p = np.array(p).T

    p = p[:, timeSteps[0] : timeSteps[1]]

    # We rotate current dipole moment to be oriented along the normal vector of cortex
    p = nyhead.rotate_dipole_to_surface_normal(p)
    eeg = M @ p * 1e9  # [mV] -> [pV] unit conversion

    # plot EEG daa
    x_lim = [-100, 100]
    y_lim = [-130, 100]
    z_lim = [-160, 120]

    t = np.arange(timeRange[0], timeRange[1], sim.cfg.recordStep)

    plt.close("all")
    fig = plt.figure(figsize=[19, 10])
    fig.subplots_adjust(top=0.96, bottom=0.05, hspace=0.17, wspace=0.3, left=0.1, right=0.99)
    ax1 = fig.add_subplot(245, aspect=1, xlabel="x (mm)", ylabel='y (mm)', xlim=x_lim, ylim=y_lim)
    ax2 = fig.add_subplot(246, aspect=1, xlabel="x (mm)", ylabel='z (mm)', xlim=x_lim, ylim=z_lim)
    ax3 = fig.add_subplot(247, aspect=1, xlabel="y (mm)", ylabel='z (mm)', xlim=y_lim, ylim=z_lim)
    ax_eeg = fig.add_subplot(244, xlabel="Time (ms)", ylabel='pV', title='EEG at all electrodes')

    ax_cdm = fig.add_subplot(248, xlabel="Time (ms)", ylabel='nA$\cdot \mu$m', title='Current dipole moment')
    dist, closest_elec_idx = nyhead.find_closest_electrode()
    print("Closest electrode to dipole: {:1.2f} mm".format(dist))

    max_elec_idx = np.argmax(np.std(eeg, axis=1))
    time_idx = np.argmax(np.abs(eeg[max_elec_idx]))
    max_eeg = np.max(np.abs(eeg[:, time_idx]))
    max_eeg_idx = np.argmax(np.abs(eeg[:, time_idx]))

    max_eeg_pos = nyhead.elecs[:3, max_eeg_idx]
    fig.text(0.01, 0.25, "Cortex", va='center', rotation=90, fontsize=22)
    fig.text(
        0.03,
        0.25,
        "Dipole pos: {:1.1f}, {:1.1f}, {:1.1f}\nDipole moment: {:1.2f} {:1.2f} {:1.2f}".format(
            nyhead.dipole_pos[0],
            nyhead.dipole_pos[1],
            nyhead.dipole_pos[2],
            p[0, time_idx],
            p[1, time_idx],
            p[2, time_idx],
        ),
        va='center',
        rotation=90,
        fontsize=14,
    )

    fig.text(0.01, 0.75, "EEG", va='center', rotation=90, fontsize=22)
    fig.text(
        0.03,
        0.75,
        "Max: {:1.2f} pV at idx {}\n({:1.1f}, {:1.1f} {:1.1f})".format(
            max_eeg, max_eeg_idx, max_eeg_pos[0], max_eeg_pos[1], max_eeg_pos[2]
        ),
        va='center',
        rotation=90,
        fontsize=14,
    )

    ax7 = fig.add_subplot(241, aspect=1, xlabel="x (mm)", ylabel='y (mm)', xlim=x_lim, ylim=y_lim)
    ax8 = fig.add_subplot(242, aspect=1, xlabel="x (mm)", ylabel='z (mm)', xlim=x_lim, ylim=z_lim)
    ax9 = fig.add_subplot(243, aspect=1, xlabel="y (mm)", ylabel='z (mm)', xlim=y_lim, ylim=z_lim)

    ax_cdm.plot(t, p[2, :], 'k')
    [ax_eeg.plot(t, eeg[idx, :], c='gray') for idx in range(eeg.shape[0])]
    ax_eeg.plot(t, eeg[closest_elec_idx, :], c='green', lw=2)

    vmax = np.max(np.abs(eeg[:, time_idx]))
    v_range = vmax
    cmap = lambda v: plt.cm.bwr((v + vmax) / (2 * vmax))

    threshold = 2

    xz_plane_idxs = np.where(np.abs(nyhead.cortex[1, :] - nyhead.dipole_pos[1]) < threshold)[0]
    xy_plane_idxs = np.where(np.abs(nyhead.cortex[2, :] - nyhead.dipole_pos[2]) < threshold)[0]
    yz_plane_idxs = np.where(np.abs(nyhead.cortex[0, :] - nyhead.dipole_pos[0]) < threshold)[0]

    ax1.scatter(nyhead.cortex[0, xy_plane_idxs], nyhead.cortex[1, xy_plane_idxs], s=5)
    ax2.scatter(nyhead.cortex[0, xz_plane_idxs], nyhead.cortex[2, xz_plane_idxs], s=5)
    ax3.scatter(nyhead.cortex[1, yz_plane_idxs], nyhead.cortex[2, yz_plane_idxs], s=5)

    for idx in range(eeg.shape[0]):
        c = cmap(eeg[idx, time_idx])
        ax7.plot(nyhead.elecs[0, idx], nyhead.elecs[1, idx], 'o', ms=10, c=c, zorder=nyhead.elecs[2, idx])
        ax8.plot(nyhead.elecs[0, idx], nyhead.elecs[2, idx], 'o', ms=10, c=c, zorder=nyhead.elecs[1, idx])
        ax9.plot(nyhead.elecs[1, idx], nyhead.elecs[2, idx], 'o', ms=10, c=c, zorder=-nyhead.elecs[0, idx])

    img = ax3.imshow([[], []], origin="lower", vmin=-vmax, vmax=vmax, cmap=plt.cm.bwr)
    plt.colorbar(img, ax=ax9, shrink=0.5)

    ax1.plot(nyhead.dipole_pos[0], nyhead.dipole_pos[1], '*', ms=12, color='orange', zorder=1000)
    ax2.plot(nyhead.dipole_pos[0], nyhead.dipole_pos[2], '*', ms=12, color='orange', zorder=1000)
    ax3.plot(nyhead.dipole_pos[1], nyhead.dipole_pos[2], '*', ms=12, color='orange', zorder=1000)

    ax7.plot(nyhead.dipole_pos[0], nyhead.dipole_pos[1], '*', ms=15, color='orange', zorder=1000)
    ax8.plot(nyhead.dipole_pos[0], nyhead.dipole_pos[2], '*', ms=15, color='orange', zorder=1000)
    ax9.plot(nyhead.dipole_pos[1], nyhead.dipole_pos[2], '*', ms=15, color='orange', zorder=1000)

    # save figure
    if saveFig:
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename + '_EEG.png'
        try:
            plt.savefig(filename, dpi=dpi)
        except:
            plt.savefig('EEG_fig.png', dpi=dpi)

    # display figure
    if showFig is True:
        plt.show()

    # import IPython as ipy; ipy.embed()
