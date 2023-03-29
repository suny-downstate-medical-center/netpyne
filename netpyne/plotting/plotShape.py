"""
Module for generating a shape plot (3D network layout)

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from builtins import open
from builtins import next
from builtins import range
from builtins import str

try:
    basestring
except NameError:
    basestring = str
from builtins import zip

from builtins import round
from future import standard_library

standard_library.install_aliases()
from netpyne import __gui__

if __gui__:
    import matplotlib.pyplot as plt
import numpy as np
from numbers import Number
from math import ceil
from ..analysis.utils import colorList, exception, _roundFigures, getCellsInclude, getCellsIncludeTags
from ..analysis.utils import _saveFigData, _showFigure
from .plotter import MetaFigure


@exception
def plotShape(
    axis=None,
    includePre=['all'],
    includePost=['all'],
    showSyns=False,
    showElectrodes=False,
    synStyle='.',
    synSize=3,
    dist=0.6,
    elev=90,
    azim=-90,
    cvar=None,
    cvals=None,
    clim=None,
    iv=False,
    ivprops=None,
    includeAxon=True,
    bkgColor=None,
    aspect='auto',
    axisLabels=False,
    kind='shape',
    returnPlotter=False,
    **kwargs
):
    """
    Function to plot morphology of network>
    """

    from .. import sim
    from neuron import h

    print('Plotting 3D cell shape ...')

    cellsPreGids = [c.gid for c in sim.getCellsList(includePre)] if includePre else []
    cellsPost = sim.getCellsList(includePost)

    if not hasattr(sim.net, 'compartCells'):
        sim.net.compartCells = [c for c in cellsPost if type(c) is sim.CompartCell]
    try:
        sim.net.defineCellShapes()  # in case some cells had stylized morphologies without 3d pts
    except:
        pass

    saveFig = False
    if 'saveFig' in kwargs:
        saveFig = kwargs['saveFig']

    fontSize = None
    if 'fontSize' in kwargs:
        fontSize = kwargs['fontSize']

    if not iv:  # plot using Python instead of interviews
        from mpl_toolkits.mplot3d import Axes3D
        from netpyne.support import (
            morphology as morph,
        )  # code adapted from https://github.com/ahwillia/PyNeuron-Toolbox

        # create secList from include
        secs = None

        # Set cvals and secs
        if not cvals and cvar:
            cvals = []
            secs = []
            # weighNorm
            if cvar == 'weightNorm':
                for cellPost in cellsPost:
                    cellSecs = (
                        list(cellPost.secs.values())
                        if includeAxon
                        else [s for s in list(cellPost.secs.values()) if 'axon' not in s['hObj'].hname()]
                    )
                    for sec in cellSecs:
                        if 'weightNorm' in sec:
                            secs.append(sec['hObj'])
                            cvals.extend(sec['weightNorm'])

                cvals = np.array(cvals)
                cvals = cvals / min(cvals)

            # numSyns
            elif cvar == 'numSyns':
                for cellPost in cellsPost:
                    cellSecs = (
                        cellPost.secs
                        if includeAxon
                        else {k: s for k, s in cellPost.secs.items() if 'axon' not in s['hObj'].hname()}
                    )
                    for secLabel, sec in cellSecs.items():
                        nseg = sec['hObj'].nseg
                        nsyns = [0] * nseg
                        secs.append(sec['hObj'])
                        conns = [
                            conn
                            for conn in cellPost.conns
                            if conn['sec'] == secLabel and conn['preGid'] in cellsPreGids
                        ]
                        for conn in conns:
                            nsyns[int(ceil(conn['loc'] * nseg)) - 1] += 1
                        cvals.extend(nsyns)

                cvals = np.array(cvals)

            # voltage
            elif cvar == 'voltage':
                for cellPost in cellsPost:
                    cellSecs = (
                        cellPost.secs
                        if includeAxon
                        else {k: s for k, s in cellPost.secs.items() if 'axon' not in s['hObj'].hname()}
                    )
                    for secLabel, sec in cellSecs.items():
                        for seg in sec['hObj']:
                            cvals.append(seg.v)

                cvals = np.array(cvals)

        if not isinstance(cellsPost[0].secs, dict):
            print('Error: Cell sections not available')
            return -1

        if not secs:
            secs = [s['hObj'] for cellPost in cellsPost for s in list(cellPost.secs.values())]
        if not includeAxon:
            secs = [sec for sec in secs if 'axon' not in sec.hname()]

        # Plot shapeplot
        cbLabels = {
            'numSyns': 'Number of synapses per segment',
            'weightNorm': 'Weight scaling',
            'voltage': 'Voltage (mV)',
        }
        # plt.rcParams.update({'font.size': fontSize})

        if axis is None:
            metaFig = MetaFigure(kind=kind, subplots=None, **kwargs)
            fig = metaFig.fig
            metaFig.ax.remove()
            shapeax = fig.add_subplot(111, projection='3d')
            metaFig.ax = shapeax
        else:
            shapeax = axis
            fig = axis.figure
            metafig = fig.metafig
            numRows = np.shape(metafig.ax)[0]
            numCols = np.shape(metafig.ax)[1]
            axisLoc = np.where(metafig.ax.ravel() == shapeax)[0][0] + 1
            plt.delaxes(shapeax)
            figIndex = int(str(numRows) + str(numCols) + str(axisLoc))
            shapeax = fig.add_subplot(figIndex, projection='3d')

        shapeax.elev = elev  # 90
        shapeax.azim = azim  # -90
        shapeax.dist = dist * shapeax.dist
        plt.axis(aspect)
        cmap = plt.cm.viridis  # plt.cm.jet  #plt.cm.rainbow #plt.cm.jet #YlOrBr_r
        morph.shapeplot(h, shapeax, sections=secs, cvals=cvals, cmap=cmap, clim=clim)

        # fix so that axes can be scaled
        ax = plt.gca()

        def set_axes_equal(ax):
            """Set 3D plot axes to equal scale.

            Make axes of 3D plot have equal scale so that spheres appear as
            spheres and cubes as cubes.  Required since `ax.axis('equal')`
            and `ax.set_aspect('equal')` don't work on 3D.
            """
            limits = np.array(
                [
                    ax.get_xlim3d(),
                    ax.get_ylim3d(),
                    ax.get_zlim3d(),
                ]
            )
            origin = np.mean(limits, axis=1)
            radius = 0.5 * np.max(np.abs(limits[:, 1] - limits[:, 0]))
            _set_axes_radius(ax, origin, radius)

        def _set_axes_radius(ax, origin, radius):
            x, y, z = origin
            ax.set_xlim3d([x - radius, x + radius])
            ax.set_ylim3d([y - radius, y + radius])
            ax.set_zlim3d([z - radius, z + radius])

        ax.set_box_aspect([1, 1, 1])  # IMPORTANT - this is the new, key line
        set_axes_equal(ax)

        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        if cvals is not None and len(cvals) > 0:
            vmin = np.min(cvals)
            vmax = np.max(cvals)

            if clim is not None:
                vmin = np.min(clim)
                vmax = np.max(clim)

            sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
            sm._A = []  # fake up the array of the scalar mappable
            cb = plt.colorbar(sm, fraction=0.15, shrink=0.5, pad=0.05, aspect=20)
            if cvar:
                cb.set_label(cbLabels[cvar], rotation=90, fontsize=fontSize)

            if saveFig == 'movie':
                cb.ax.set_title('Time = ' + str(round(h.t, 1)), fontsize=fontSize)

        if bkgColor:
            shapeax.w_xaxis.set_pane_color(bkgColor)
            shapeax.w_yaxis.set_pane_color(bkgColor)
            shapeax.w_zaxis.set_pane_color(bkgColor)
        # shapeax.grid(False)

        # Synapses
        if showSyns:
            synColor = 'red'
            for cellPost in cellsPost:
                for sec in list(cellPost.secs.values()):
                    for synMech in sec['synMechs']:
                        morph.mark_locations(
                            h, sec['hObj'], synMech['loc'], markspec=synStyle, color=synColor, markersize=synSize
                        )

        # Electrodes
        if showElectrodes:
            ax = plt.gca()
            colorOffset = 0
            if 'avg' in showElectrodes:
                showElectrodes.remove('avg')
                colorOffset = 1
            coords = sim.net.recXElectrode.pos.T[np.array(showElectrodes).astype(int), :]
            ax.scatter(
                coords[:, 0],
                coords[:, 1],
                coords[:, 2],
                s=150,
                c=colorList[colorOffset : len(coords) + colorOffset],
                marker='v',
                depthshade=False,
                edgecolors='k',
                linewidth=2,
            )
            for i in range(coords.shape[0]):
                ax.text(coords[i, 0], coords[i, 1], coords[i, 2], '  ' + str(showElectrodes[i]), fontweight='bold')
            cb.set_label('Segment total transfer resistance to electrodes (kiloohm)', rotation=90, fontsize=fontSize)

        if axisLabels:
            shapeax.set_xlabel('x (um)')
            shapeax.set_ylabel('y (um)')
            shapeax.set_zlabel('z (um)')
        else:
            shapeax.set_xticklabels([])
            shapeax.set_yticklabels([])
            shapeax.set_zticklabels([])

        if axis is None:
            metaFig.finishFig(**kwargs)
        else:
            if saveFig:
                if isinstance(saveFig, basestring):
                    if saveFig == 'movie':
                        filename = sim.cfg.filename + '_shape_movie_' + str(round(h.t, 1)) + '.png'
                    else:
                        filename = saveFig
                else:
                    filename = sim.cfg.filename + '_shape.png'
                plt.savefig(filename, dpi=dpi)

            # show fig
            # if showFig: _showFigure()

    else:  # Plot using Interviews
        # colors: 0 white, 1 black, 2 red, 3 blue, 4 green, 5 orange, 6 brown, 7 violet, 8 yellow, 9 gray
        from neuron import gui

        fig = h.Shape()
        secList = h.SectionList()
        if not ivprops:
            ivprops = {'colorSecs': 1, 'colorSyns': 2, 'style': 'O', 'siz': 5}

        for cell in [c for c in cellsPost]:
            for sec in list(cell.secs.values()):
                if 'axon' in sec['hObj'].hname() and not includeAxon:
                    continue
                sec['hObj'].push()
                secList.append()
                h.pop_section()
                if showSyns:
                    for synMech in sec['synMechs']:
                        if synMech['hObj']:
                            # find pre pop using conn[preGid]
                            # create dict with color for each pre pop; check if exists; increase color counter
                            # colorsPre[prePop] = colorCounter

                            # find synMech using conn['loc'], conn['sec'] and conn['synMech']
                            fig.point_mark(synMech['hObj'], ivprops['colorSyns'], ivprops['style'], ivprops['siz'])

        fig.observe(secList)
        fig.color_list(secList, ivprops['colorSecs'])
        fig.flush()
        fig.show(0)  # show real diam
        # save figure
        if saveFig:
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename + '_' + 'shape.ps'
            fig.printfile(filename)

    if not iv:
        if axis is None:
            if returnPlotter:
                return metaFig
            else:
                return fig, {}
        else:
            return fig, {}

    else:
        return fig, {}
