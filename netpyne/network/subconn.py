
"""
network/subconn.py 

Methods to distribute synapses at the subcellular level (e.g. dendritic) in the network

Contributors: salvadordura@gmail.com
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
def fromtodistance(self, origin_segment, to_segment):
    h.distance(0, origin_segment.x, sec=origin_segment.sec)
    return h.distance(to_segment.x, sec=to_segment.sec)


# -----------------------------------------------------------------------------
# Calculate 2d point from segment location
# -----------------------------------------------------------------------------
def _posFromLoc(self, sec, x):
    sec.push()
    s = x * sec.L
    numpts = int(h.n3d())
    b = -1
    for ii in range(numpts):
        if h.arc3d(ii) >= s:
            b = ii
            break
    if b == -1: print("an error occurred in pointFromLoc, SOMETHING IS NOT RIGHT")

    if h.arc3d(b) == s:  # shortcut
        x, y, z = h.x3d(b), h.y3d(b), h.z3d(b)
    else:               # need to interpolate
        a = b-1
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
            x, y, z = self._posFromLoc(sec['hObj'], seg.x)
            if gridX and gridY: # 2D
                distX = [abs(gx-x) for gx in gridX]
                distY = [abs(gy-y) for gy in gridY]
                ixs = np.array(distX).argsort()[:2]
                jys = np.array(distY).argsort()[:2]
                i1,i2,j1,j2 = min(ixs), max(ixs), min(jys), max(jys) 
                x1,x2,y1,y2 = gridX[i1], gridX[i2], gridY[j1], gridY[j2]
                sigma_x1_y1 = gridSigma[i1][j1]
                sigma_x1_y2 = gridSigma[i1][j2]
                sigma_x2_y1 = gridSigma[i2][j1]
                sigma_x2_y2 = gridSigma[i2][j2]

                if x1 == x2 or y1 == y2: 
                    print("ERROR in closest grid points: ", secName, x1, x2, y1, y2)
                else:
                   # bilinear interpolation, see http://en.wikipedia.org/wiki/Bilinear_interpolation (fixed bug from Ben Suter's code)
                   sigma = ((sigma_x1_y1*abs(x2-x)*abs(y2-y) + sigma_x2_y1*abs(x-x1)*abs(y2-y) + sigma_x1_y2*abs(x2-x)*abs(y-y1) + sigma_x2_y2*abs(x-x1)*abs(y-y1))/(abs(x2-x1)*abs(y2-y1)))
                   #sigma = ((sigma_x1_y1*abs(x2-x)*abs(y2-y) + sigma_x2_y1*abs(x-x1)*abs(y2-y) + sigma_x1_y2*abs(x2-x)*abs(y-y1) + sigma_x2_y2*abs(x-x1)*abs(y-y1))/((x2-x1)*(y2-y1)))

            elif gridY:  # 1d = radial
                distY = [abs(gy-y) for gy in gridY]
                jys = np.array(distY).argsort()[:2]
                sigma = np.zeros((1,2))
                j1,j2 = min(jys), max(jys)
                y1, y2 = gridY[j1], gridY[j2]
                sigma_y1 = gridSigma[j1]
                sigma_y2 = gridSigma[j2]

                if y1 == y2: 
                    print("ERROR in closest grid points: ", secName, y1, y2)
                else:
                   # linear interpolation, see http://en.wikipedia.org/wiki/Bilinear_interpolation
                   sigma = ((sigma_y1*abs(y2-y) + sigma_y2*abs(y-y1)) / abs(y2-y1))

            numSyn = sigma * sec['hObj'].L / sec['hObj'].nseg  # return num syns 
            segNumSyn[secName].append(numSyn)

    return segNumSyn


# -----------------------------------------------------------------------------
# Subcellular connectivity (distribution of synapses)
# -----------------------------------------------------------------------------
def subcellularConn(self, allCellTags, allPopTags):
    from .. import sim

    sim.timing('start', 'subConnectTime')
    print('  Distributing synapses based on subcellular connectivity rules...')

    for subConnParamTemp in list(self.params.subConnParams.values()):  # for each conn rule or parameter set
        subConnParam = subConnParamTemp.copy()

        # find list of pre and post cell
        preCellsTags, postCellsTags = self._findPrePostCellsCondition(allCellTags, subConnParam['preConds'], subConnParam['postConds'])

        if preCellsTags and postCellsTags:
            # iterate over postsyn cells to redistribute synapses
            for postCellGid in postCellsTags:  # for each postsyn cell
                if postCellGid in self.gid2lid:
                    postCell = self.cells[self.gid2lid[postCellGid]] 
                    allConns = [conn for conn in postCell.conns if conn['preGid'] in preCellsTags]
                    if 'NetStim' in [x['cellModel'] for x in list(preCellsTags.values())]: # temporary fix to include netstim conns 
                        allConns.extend([conn for conn in postCell.conns if conn['preGid'] == 'NetStim'])

                    # group synMechs so they are not distributed separately
                    if 'groupSynMechs' in subConnParam:  
                        conns = []
                        connsGroup = {}
                        iConn = -1
                        for conn in allConns:
                            if not conn['synMech'].startswith('__grouped__'):
                                conns.append(conn)
                                iConn = iConn + 1
                                if conn['synMech'] in subConnParam['groupSynMechs']:
                                    for synMech in [s for s in subConnParam['groupSynMechs'] if s != conn['synMech']]:
                                        connGroup = next((c for c in allConns if c['synMech'] == synMech and c['sec']==conn['sec'] and c['loc']==conn['loc']), None)
                                        try:
                                            connGroup['synMech'] = '__grouped__'+connGroup['synMech']
                                            connsGroup[iConn] = connGroup
                                        except:
                                            print('  Warning: Grouped synMechs %s not found' % (str(connGroup)))
                    else:
                        conns = allConns

                    # set sections to be used
                    secList = postCell._setConnSections(subConnParam)
                    
                    # Uniform distribution
                    if subConnParam.get('density', None) == 'uniform':
                        # calculate new syn positions
                        newSecs, newLocs = postCell._distributeSynsUniformly(secList=secList, numSyns=len(conns))

                    # 2D map and 1D map (radial)
                    elif isinstance(subConnParam.get('density', None), dict) and subConnParam['density']['type'] in ['2Dmap', '1Dmap']:

                        gridY = subConnParam['density']['gridY']
                        gridSigma = subConnParam['density']['gridValues']
                        somaX, somaY, _ = self._posFromLoc(postCell.secs['soma']['hObj'], 0.5) # get cell pos move method to Cell!
                        if 'fixedSomaY' in subConnParam['density']:  # is fixed cell soma y, adjust y grid accordingly
                            fixedSomaY = subConnParam['density'].get('fixedSomaY')
                            gridY = [y+(somaY-fixedSomaY) for y in gridY] # adjust grid so cell soma is at fixedSomaY
                            
                        if subConnParam['density']['type'] == '2Dmap': # 2D    
                            gridX = [x - somaX for x in subConnParam['density']['gridX']] # center x at cell soma
                            segNumSyn = self._interpolateSegmentSigma(postCell, secList, gridX, gridY, gridSigma) # move method to Cell!
                        elif subConnParam['density']['type'] == '1Dmap': # 1D
                            segNumSyn = self._interpolateSegmentSigma(postCell, secList, None, gridY, gridSigma) # move method to Cell!

                        totSyn = sum([sum(nsyn) for nsyn in list(segNumSyn.values())])  # summed density
                        scaleNumSyn = float(len(conns))/float(totSyn) if totSyn>0 else 0.0  
                        diffList = []
                        for sec in segNumSyn: 
                            for seg,x in enumerate(segNumSyn[sec]):
                                orig = float(x*scaleNumSyn)
                                scaled = int(round(x * scaleNumSyn))
                                segNumSyn[sec][seg] = scaled
                                diff = orig - scaled
                                if diff > 0:
                                    diffList.append([diff,sec,seg])

                        totSynRescale = sum([sum(nsyn) for nsyn in list(segNumSyn.values())])

                        # if missing syns due to rescaling to 0, find top values which were rounded to 0 and make 1
                        if totSynRescale < len(conns):  
                            extraSyns = len(conns)-totSynRescale
                            diffList = sorted(diffList, key=lambda l:l[0], reverse=True)
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
                    elif subConnParam.get('density', None) == 'distance':
                        # find origin section 
                        if 'soma' in postCell.secs: 
                            secOrig = 'soma' 
                        elif any([secName.startswith('som') for secName in list(postCell.secs.keys())]):
                            secOrig = next(secName for secName in list(postCell.secs.keys()) if secName.startswith('soma'))
                        else: 
                            secOrig = list(postCell.secs.keys())[0]

                        #print self.fromtodistance(postCell.secs[secOrig](0.5), postCell.secs['secs'][conn['sec']](conn['loc']))

                        # different case if has vs doesn't have 3d points
                        #  h.distance(sec=h.soma[0], seg=0)
                        # for sec in apical:
                        #    print h.secname()
                        #    for seg in sec:
                        #      print seg.x, h.distance(seg.x)


                    # sort conns so reproducible across different number of cores 
                    # use sec+preGid to avoid artificial distribution based on preGid (low gids = close to soma)
                    conns = sorted(conns, key = lambda v: v['sec']+str(v['preGid']))

                    # assign conns to new syn locations
                    for i,(conn, newSec, newLoc) in enumerate(zip(conns, newSecs, newLocs)):

                        # update weight if weightNorm present
                        if 'weightNorm' in postCell.secs[conn['sec']] and isinstance(postCell.secs[conn['sec']]['weightNorm'], list): 
                            oldNseg = postCell.secs[conn['sec']]['geom']['nseg']
                            oldWeightNorm = postCell.secs[conn['sec']]['weightNorm'][int(round(conn['loc']*oldNseg))-1]
                            newNseg = postCell.secs[newSec]['geom']['nseg']
                            newWeightNorm = postCell.secs[newSec]['weightNorm'][int(round(newLoc*newNseg))-1] if 'weightNorm' in postCell.secs[newSec] else 1.0
                            conn['weight'] = conn['weight'] / oldWeightNorm * newWeightNorm

                        # avoid locs at 0.0 or 1.0 - triggers hoc error if syn needs an ion (eg. ca_ion)
                        if newLoc == 0.0: newLoc = 0.00001 
                        elif newLoc == 1.0: newLoc = 0.99999  
                        
                        # updade sec and loc
                        conn['sec'] = newSec
                        conn['loc'] = newLoc

                        # find grouped conns 
                        if subConnParam.get('groupSynMechs', None) and conn['synMech'] in subConnParam['groupSynMechs']:
                            connGroup = connsGroup[i]  # get grouped conn from previously stored dict 
                            connGroup['synMech'] = connGroup['synMech'].split('__grouped__')[1]  # remove '__grouped__' label

                            connGroup['sec'] = newSec
                            connGroup['loc'] = newLoc
                            if newWeightNorm: connGroup['weight'] = connGroup['weight'] / oldWeightNorm * newWeightNorm

                                
        sim.pc.barrier()



