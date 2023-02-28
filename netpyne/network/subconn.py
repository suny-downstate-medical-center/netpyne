"""
Module for distributing synapses at the subcellular level in networks

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from builtins import zip
from builtins import range

from builtins import round
from builtins import next
from builtins import str
from future import standard_library

standard_library.install_aliases()
import numpy as np
from neuron import h

# -----------------------------------------------------------------------------
# Calculate distance between 2 segments
# -----------------------------------------------------------------------------
def pathDistance(from_segment, to_segment):
    """
    Compute the path distance between two points on a neuron based on h.distance()

    Parameters
    ----------

    from_segment : <type>
        <Short description of origin_segment>
        **Default:** *required*

    to_segment : <type>
        <Short description of to_segment>
        **Default:** *required*
    """

    return h.distance(from_segment, to_segment)


# -----------------------------------------------------------------------------
# Calculate position from segment location
# -----------------------------------------------------------------------------
def posFromLoc(sec, x):
    """
    Compute absolute 3D position of given section at location x

    Parameters
    ----------

    sec : dict
        <Short description of origin_segment>
        **Default:** *required*

    x : float
        <Short description of to_segment>
        **Default:** *required*
    """

    secObj = sec['hObj']
    secObj.push()
    s = x * secObj.L
    numpts = int(h.n3d())
    b = -1
    for ii in range(numpts):
        if h.arc3d(ii) >= s:
            b = ii
            break
    if b == -1:
        print("an error occurred in pointFromLoc, SOMETHING IS NOT RIGHT")

    if h.arc3d(b) == s:  # shortcut
        x, y, z = h.x3d(b), h.y3d(b), h.z3d(b)
    else:  # need to interpolate
        a = b - 1
        t = (s - h.arc3d(a)) / (h.arc3d(b) - h.arc3d(a))
        x = h.x3d(a) + t * (h.x3d(b) - h.x3d(a))
        y = h.y3d(a) + t * (h.y3d(b) - h.y3d(a))
        z = h.z3d(a) + t * (h.z3d(b) - h.z3d(a))

    h.pop_section()
    return x, y, z


# -----------------------------------------------------------------------------
# Calculate syn density for each segment from grid
# -----------------------------------------------------------------------------
def _interpolateSegmentSigma(self, cell, secList, gridX, gridY, gridSigma):
    segNumSyn = {}  #
    for secName in secList:
        sec = cell.secs[secName]
        segNumSyn[secName] = []
        for seg in sec['hObj']:
            x, y, z = posFromLoc(sec, seg.x)
            if gridX and gridY:  # 2D
                distX = [abs(gx - x) for gx in gridX]
                distY = [abs(gy - y) for gy in gridY]
                ixs = np.array(distX).argsort()[:2]
                jys = np.array(distY).argsort()[:2]
                i1, i2, j1, j2 = min(ixs), max(ixs), min(jys), max(jys)
                x1, x2, y1, y2 = gridX[i1], gridX[i2], gridY[j1], gridY[j2]
                sigma_x1_y1 = gridSigma[i1][j1]
                sigma_x1_y2 = gridSigma[i1][j2]
                sigma_x2_y1 = gridSigma[i2][j1]
                sigma_x2_y2 = gridSigma[i2][j2]

                if x1 == x2 or y1 == y2:
                    print("ERROR in closest grid points: ", secName, x1, x2, y1, y2)
                else:
                    # bilinear interpolation, see http://en.wikipedia.org/wiki/Bilinear_interpolation (fixed bug from Ben Suter's code)
                    sigma = (
                        sigma_x1_y1 * (x2 - x) * (y2 - y)
                        + sigma_x2_y1 * (x - x1) * (y2 - y)
                        + sigma_x1_y2 * (x2 - x) * (y - y1)
                        + sigma_x2_y2 * (x - x1) * (y - y1)
                    ) / ((x2 - x1) * (y2 - y1))

            elif gridY:  # 1d = radial
                distY = [abs(gy - y) for gy in gridY]
                jys = np.array(distY).argsort()[:2]
                sigma = np.zeros((1, 2))
                j1, j2 = min(jys), max(jys)
                y1, y2 = gridY[j1], gridY[j2]
                sigma_y1 = gridSigma[j1]
                sigma_y2 = gridSigma[j2]

                if y1 == y2:
                    print("ERROR in closest grid points: ", secName, y1, y2)
                else:
                    # linear interpolation, see http://en.wikipedia.org/wiki/Bilinear_interpolation
                    sigma = (sigma_y1 * (y2 - y) + sigma_y2 * (y - y1)) / (y2 - y1)

            numSyn = sigma * sec['hObj'].L / sec['hObj'].nseg  # return num syns
            segNumSyn[secName].append(numSyn)

    return segNumSyn


# -----------------------------------------------------------------------------
# Subcellular connectivity (distribution of synapses)
# -----------------------------------------------------------------------------
def subcellularConn(self, allCellTags, allPopTags):
    """
    Function for/to <short description of `netpyne.network.subconn.subcellularConn`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*

    allCellTags : <type>
        <Short description of allCellTags>
        **Default:** *required*

    allPopTags : <type>
        <Short description of allPopTags>
        **Default:** *required*


    """

    from .. import sim

    sim.timing('start', 'subConnectTime')
    print('  Distributing synapses based on subcellular connectivity rules...')

    for subConnParamTemp in list(self.params.subConnParams.values()):  # for each conn rule or parameter set
        subConnParam = subConnParamTemp.copy()

        # find list of pre and post cell
        preCellsTags, postCellsTags = self._findPrePostCellsCondition(
            allCellTags, subConnParam['preConds'], subConnParam['postConds']
        )

        if preCellsTags and postCellsTags:
            # iterate over postsyn cells to redistribute synapses
            for postCellGid in postCellsTags:  # for each postsyn cell
                if postCellGid in self.gid2lid:
                    postCell = self.cells[self.gid2lid[postCellGid]]
                    allConns = [conn for conn in postCell.conns if conn['preGid'] in preCellsTags]
                    if 'NetStim' in [
                        x['cellModel'] for x in list(preCellsTags.values()) if 'cellModel' in x.keys()
                    ]:  # temporary fix to include netstim conns
                        allConns.extend([conn for conn in postCell.conns if conn['preGid'] == 'NetStim'])

                    # group synMechs so they are not distributed separately
                    if 'groupSynMechs' in subConnParam and len(subConnParam['groupSynMechs']) > 1:
                        conns = []
                        connsGroup = {}
                        # iConn = -1
                        for conn in allConns:
                            if not conn['synMech'].startswith('__grouped__'):
                                conns.append(conn)
                                # iConn = iConn + 1
                                connGroupLabel = '%d_%s_%.4f' % (conn['preGid'], conn['sec'], conn['loc'])
                                if conn['synMech'] in subConnParam['groupSynMechs']:
                                    for synMech in [s for s in subConnParam['groupSynMechs'] if s != conn['synMech']]:
                                        connGroup = next(
                                            (
                                                c
                                                for c in allConns
                                                if c['synMech'] == synMech
                                                and c['sec'] == conn['sec']
                                                and c['loc'] == conn['loc']
                                            ),
                                            None,
                                        )
                                        try:
                                            connGroup['synMech'] = '__grouped__' + connGroup['synMech']
                                            connsGroup[connGroupLabel] = connGroup
                                        except:
                                            print('  Warning: Grouped synMechs %s not found' % (str(connGroup)))
                    else:
                        conns = allConns

                    # sort conns so reproducible across different number of cores
                    # use sec+preGid to avoid artificial distribution based on preGid (e.g. low gids = close to soma)
                    conns = sorted(conns, key=lambda v: v['sec'] + str(v['loc']) + str(v['preGid']))

                    # set sections to be used
                    secList = postCell._setConnSections(subConnParam)

                    # Uniform distribution
                    if subConnParam.get('density', None) == 'uniform':
                        # calculate new syn positions
                        newSecs, newLocs = postCell._distributeSynsUniformly(secList=secList, numSyns=len(conns))

                    # 2D map and 1D map (radial)
                    elif isinstance(subConnParam.get('density', None), dict) and subConnParam['density']['type'] in [
                        '2Dmap',
                        '1Dmap',
                    ]:

                        gridY = subConnParam['density']['gridY']
                        gridSigma = subConnParam['density']['gridValues']
                        somaX, somaY, _ = posFromLoc(postCell.secs['soma'], 0.5)  # get cell pos move method to Cell!
                        if 'fixedSomaY' in subConnParam['density']:  # is fixed cell soma y, adjust y grid accordingly
                            fixedSomaY = subConnParam['density'].get('fixedSomaY')
                            gridY = [
                                y + (somaY - fixedSomaY) for y in gridY
                            ]  # adjust grid so cell soma is at fixedSomaY

                        if subConnParam['density']['type'] == '2Dmap':  # 2D
                            gridX = [x - somaX for x in subConnParam['density']['gridX']]  # center x at cell soma
                            segNumSyn = self._interpolateSegmentSigma(
                                postCell, secList, gridX, gridY, gridSigma
                            )  # move method to Cell!
                        elif subConnParam['density']['type'] == '1Dmap':  # 1D
                            segNumSyn = self._interpolateSegmentSigma(
                                postCell, secList, None, gridY, gridSigma
                            )  # move method to Cell!

                        totSyn = sum([sum(nsyn) for nsyn in list(segNumSyn.values())])  # summed density
                        scaleNumSyn = float(len(conns)) / float(totSyn) if totSyn > 0 else 0.0
                        diffList = []
                        for sec in segNumSyn:
                            for seg, x in enumerate(segNumSyn[sec]):
                                orig = float(x * scaleNumSyn)
                                scaled = int(round(x * scaleNumSyn))
                                segNumSyn[sec][seg] = scaled
                                diff = orig - scaled
                                if diff > 0:
                                    diffList.append([diff, sec, seg])

                        totSynRescale = sum([sum(nsyn) for nsyn in list(segNumSyn.values())])

                        # if missing syns due to rescaling to 0, find top values which were rounded to 0 and make 1
                        if totSynRescale < len(conns):
                            extraSyns = len(conns) - totSynRescale
                            diffList = sorted(diffList, key=lambda l: l[0], reverse=True)
                            for i in range(min(extraSyns, len(diffList))):
                                sec = diffList[i][1]
                                seg = diffList[i][2]
                                segNumSyn[sec][seg] += 1

                        # convert to list so can serialize and save
                        subConnParam['density']['gridY'] = list(subConnParam['density']['gridY'])
                        subConnParam['density']['gridValues'] = list(subConnParam['density']['gridValues'])

                        newSecs, newLocs = [], []
                        for sec, nsyns in segNumSyn.items():
                            for i, seg in enumerate(postCell.secs[sec]['hObj']):
                                for isyn in range(nsyns[i]):
                                    newSecs.append(sec)
                                    newLocs.append(seg.x)

                    # Distance-based
                    elif (
                        isinstance(subConnParam.get('density', None), dict)
                        and subConnParam['density']['type'] == 'distance'
                    ):
                        # find origin section
                        # giving argument
                        if 'ref_sec' in subConnParam['density']:
                            if subConnParam['density']['ref_sec'] in list(postCell.secs.keys()):
                                secOrigName = subConnParam['density']['ref_sec']
                            else:
                                print(
                                    '  Warning: Redistributing synapses based on inexistent information for neuron %d - section %s not found'
                                    % (postCell.gid, subConnParam['density']['ref_sec'])
                                )
                        # default
                        if not secOrigName:
                            secOrigName = postCell.originSecName()

                        # find origin segment
                        segOrig = 0.5  # default
                        if 'ref_seg' in subConnParam['density']:
                            segOrig = subConnParam['density']['ref_seg']
                        secOrig = postCell.secs[secOrigName]
                        segOrigObj = secOrig['hObj'](segOrig)

                        # target
                        target_distance = 0.0
                        if 'target_distance' in subConnParam['density']:
                            target_distance = subConnParam['density']['target_distance']

                        newSec, newLoc = secOrigName, segOrig
                        min_dist = target_distance
                        if 'coord' in subConnParam['density'] and subConnParam['density']['coord'] == 'cartesian':
                            # calculate euclidean distance from reference
                            x0, y0, z0 = posFromLoc(secOrig, segOrigObj.x)
                            for secName in secList:
                                sec = postCell.secs[secName]
                                for seg in sec['hObj']:
                                    x, y, z = posFromLoc(sec, seg.x)
                                    dist = np.sqrt((x - x0) ** 2 + (y - y0) ** 2 + (z - z0) ** 2)
                                    if abs(dist - target_distance) <= min_dist:
                                        min_dist = abs(dist - target_distance)
                                        newSec, newLoc = secName, seg.x

                        else:
                            # (default) calculate distance based on the topology
                            for secName in secList:
                                sec = postCell.secs[secName]
                                for seg in sec['hObj']:
                                    dist = pathDistance(segOrigObj, seg)
                                    if abs(dist - target_distance) <= min_dist:
                                        min_dist = abs(dist - target_distance)
                                        newSec, newLoc = secName, seg.x

                        newSecs = [newSec] * len(conns)
                        newLocs = [newLoc] * len(conns)

                    for i, (conn, newSec, newLoc) in enumerate(zip(conns, newSecs, newLocs)):

                        # get conn group label before updating params
                        connGroupLabel = '%d_%s_%.4f' % (conn['preGid'], conn['sec'], conn['loc'])

                        # update weight if weightNorm present
                        newWeightNorm = None
                        if 'weightNorm' in postCell.secs[conn['sec']] and isinstance(
                            postCell.secs[conn['sec']]['weightNorm'], list
                        ):
                            oldNseg = postCell.secs[conn['sec']]['geom']['nseg']
                            oldWeightNorm = postCell.secs[conn['sec']]['weightNorm'][
                                int(round(conn['loc'] * oldNseg)) - 1
                            ]
                            newNseg = postCell.secs[newSec]['geom']['nseg']
                            newWeightNorm = (
                                postCell.secs[newSec]['weightNorm'][int(round(newLoc * newNseg)) - 1]
                                if 'weightNorm' in postCell.secs[newSec]
                                else 1.0
                            )
                            conn['weight'] = conn['weight'] / oldWeightNorm * newWeightNorm

                        # avoid locs at 0.0 or 1.0 - triggers hoc error if syn needs an ion (eg. ca_ion)
                        if newLoc == 0.0:
                            newLoc = 0.00001
                        elif newLoc == 1.0:
                            newLoc = 0.99999

                        # updade sec and loc
                        conn['sec'] = newSec
                        conn['loc'] = newLoc

                        # find grouped conns
                        if (
                            subConnParam.get('groupSynMechs', None)
                            and len(subConnParam['groupSynMechs']) > 1
                            and conn['synMech'] in subConnParam['groupSynMechs']
                        ):

                            connGroup = connsGroup[connGroupLabel]  # get grouped conn from previously stored dict
                            connGroup['synMech'] = connGroup['synMech'].split('__grouped__')[
                                1
                            ]  # remove '__grouped__' label

                            connGroup['sec'] = newSec
                            connGroup['loc'] = newLoc
                            if newWeightNorm:
                                connGroup['weight'] = connGroup['weight'] / oldWeightNorm * newWeightNorm

        sim.pc.barrier()
