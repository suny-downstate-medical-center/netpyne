
"""
network.py 

Defines Network class which contains cell objects and network-realated methods

Contributors: salvadordura@gmail.com
"""

from matplotlib.pylab import array, sin, cos, tan, exp, sqrt, mean, inf, rand, dstack, unravel_index, argsort, zeros, ceil, copy
from random import seed, random, randint, sample, uniform, triangular, gauss, betavariate, expovariate, gammavariate
from time import time, sleep
from numbers import Number
from copy import copy
from specs import ODict
from neuron import h  # import NEURON
import sim


class Network (object):

    ###############################################################################
    # initialize variables
    ###############################################################################
    def __init__ (self, params = None):
        self.params = params

        # params that can be expressed using string-based functions in connections
        self.connStringFuncParams = ['weight', 'delay', 'synsPerConn', 'loc']  

        # params that can be expressed using string-based functions in stims
        self.stimStringFuncParams = ['delay', 'dur', 'amp', 'gain', 'rstim', 'tau1', 'tau2', 'i', 
        'onset', 'tau', 'gmax', 'e', 'i', 'interval', 'rate', 'number', 'start', 'noise']  

        self.pops = ODict()  # list to store populations ('Pop' objects)
        self.cells = [] # list to store cells ('Cell' objects)

        self.lid2gid = [] # Empty list for storing local index -> GID (index = local id; value = gid)
        self.gid2lid = {} # Empty dict for storing GID -> local index (key = gid; value = local id) -- ~x6 faster than .index() 
        self.lastGid = 0  # keep track of last cell gid 
        self.lastGapId = 0  # keep track of last gap junction gid 


    ###############################################################################
    # Set network params
    ###############################################################################
    def setParams (self, params):
        self.params = params

    ###############################################################################
    # Instantiate network populations (objects of class 'Pop')
    ###############################################################################
    def createPops (self):
        for popLabel, popParam in self.params.popParams.iteritems(): # for each set of population paramseters 
            self.pops[popLabel] = sim.Pop(popLabel, popParam)  # instantiate a new object of class Pop and add to list pop
        return self.pops


    ###############################################################################
    # Create Cells
    ###############################################################################
    def createCells (self):
        sim.pc.barrier()
        sim.timing('start', 'createTime')
        if sim.rank==0: 
            print("\nCreating network of %i cell populations on %i hosts..." % (len(self.pops), sim.nhosts)) 
        
        for ipop in self.pops.values(): # For each pop instantiate the network cells (objects of class 'Cell')
            newCells = ipop.createCells() # create cells for this pop using Pop method
            self.cells.extend(newCells)  # add to list of cells
            sim.pc.barrier()
            if sim.rank==0 and sim.cfg.verbose: print('Instantiated %d cells of population %s'%(len(newCells), ipop.tags['popLabel']))    
        print('  Number of cells on node %i: %i ' % (sim.rank,len(self.cells))) 
        sim.pc.barrier()
        sim.timing('stop', 'createTime')
        if sim.rank == 0 and sim.cfg.timing: print('  Done; cell creation time = %0.2f s.' % sim.timingData['createTime'])

        return self.cells
    
    ###############################################################################
    #  Add stims
    ###############################################################################
    def addStims (self):
        sim.timing('start', 'stimsTime')
        if self.params.stimSourceParams and self.params.stimTargetParams:
            if sim.rank==0: 
                print('Adding stims...')
                
            if sim.nhosts > 1: # Gather tags from all cells 
                allCellTags = sim._gatherAllCellTags()  
            else:
                allCellTags = {cell.gid: cell.tags for cell in self.cells}
            # allPopTags = {i: pop.tags for i,pop in enumerate(self.pops)}  # gather tags from pops so can connect NetStim pops

            sources = self.params.stimSourceParams

            for targetLabel, target in self.params.stimTargetParams.iteritems():  # for each target parameter set
                if 'sec' not in target: target['sec'] = None  # if section not specified, make None (will be assigned to first section in cell)
                if 'loc' not in target: target['loc'] = None  # if location not specified, make None 
                
                source = sources.get(target['source'])

                postCellsTags = allCellTags
                for condKey,condValue in target['conds'].iteritems():  # Find subset of cells that match postsyn criteria
                    if condKey in ['x','y','z','xnorm','ynorm','znorm']:
                        postCellsTags = {gid: tags for (gid,tags) in postCellsTags.iteritems() if condValue[0] <= tags[condKey] < condValue[1]}  # dict with post Cell objects}  # dict with pre cell tags
                    elif condKey == 'cellList':
                        pass
                    elif isinstance(condValue, list): 
                        postCellsTags = {gid: tags for (gid,tags) in postCellsTags.iteritems() if tags[condKey] in condValue}  # dict with post Cell objects
                    else:
                        postCellsTags = {gid: tags for (gid,tags) in postCellsTags.iteritems() if tags[condKey] == condValue}  # dict with post Cell objects
                
                # subset of cells from selected pops (by relative indices)                     
                if 'cellList' in target['conds']:
                    orderedPostGids = sorted(postCellsTags.keys())
                    gidList = [orderedPostGids[i] for i in target['conds']['cellList']]
                    postCellsTags = {gid: tags for (gid,tags) in postCellsTags.iteritems() if gid in gidList}

                # calculate params if string-based funcs
                strParams = self._stimStrToFunc(postCellsTags, source, target)

                # loop over postCells and add stim target
                for postCellGid in postCellsTags:  # for each postsyn cell
                    if postCellGid in self.lid2gid:  # check if postsyn is in this node's list of gids
                        postCell = self.cells[sim.net.gid2lid[postCellGid]]  # get Cell object 

                        # stim target params
                        params = {}
                        params['label'] = targetLabel
                        params['source'] = target['source']
                        params['sec'] = strParams['secList'][postCellGid] if 'secList' in strParams else target['sec']
                        params['loc'] = strParams['locList'][postCellGid] if 'locList' in strParams else target['loc']
                         
                        if source['type'] == 'NetStim': # for NetStims add weight+delay or default values
                            params['weight'] = strParams['weightList'][postCellGid] if 'weightList' in strParams else target.get('weight', 1.0)
                            params['delay'] = strParams['delayList'][postCellGid] if 'delayList' in strParams else target.get('delay', 1.0)
                            params['synsPerConn'] = strParams['synsPerConnList'][postCellGid] if 'synsPerConnList' in strParams else target.get('synsPerConn', 1)
                            params['synMech'] = target.get('synMech', None)
                        
                        for sourceParam in source: # copy source params
                            params[sourceParam] = strParams[sourceParam+'List'][postCellGid] if sourceParam+'List' in strParams else source.get(sourceParam)

                        postCell.addStim(params)  # call cell method to add connections

        print('  Number of stims on node %i: %i ' % (sim.rank, sum([len(cell.stims) for cell in self.cells])))
        sim.pc.barrier()
        sim.timing('stop', 'stimsTime')
        if sim.rank == 0 and sim.cfg.timing: print('  Done; cell stims creation time = %0.2f s.' % sim.timingData['stimsTime'])

        return [cell.stims for cell in self.cells]



    ###############################################################################
    # Convert stim param string to function
    ###############################################################################
    def _stimStrToFunc (self, postCellsTags, sourceParams, targetParams):
        # list of params that have a function passed in as a string
        #params = sourceParams+targetParams
        params = sourceParams.copy()
        params.update(targetParams)

        paramsStrFunc = [param for param in self.stimStringFuncParams+self.connStringFuncParams if param in params and isinstance(params[param], str)]  

        # dict to store correspondence between string and actual variable
        dictVars = {}   
        dictVars['post_x']      = lambda postConds: postConds['x'] 
        dictVars['post_y']      = lambda postConds: postConds['y'] 
        dictVars['post_z']      = lambda postConds: postConds['z'] 
        dictVars['post_xnorm']  = lambda postConds: postConds['xnorm'] 
        dictVars['post_ynorm']  = lambda postConds: postConds['ynorm'] 
        dictVars['post_znorm']  = lambda postConds: postConds['znorm'] 
         
        # add netParams variables
        for k,v in self.params.__dict__.iteritems():
            if isinstance(v, Number):
                dictVars[k] = v

        # for each parameter containing a function, calculate lambda function and arguments
        strParams = {}
        for paramStrFunc in paramsStrFunc:
            strFunc = params[paramStrFunc]  # string containing function
            strVars = [var for var in dictVars.keys() if var in strFunc and var+'norm' not in strFunc]  # get list of variables used (eg. post_ynorm or dist_xyz)
            lambdaStr = 'lambda ' + ','.join(strVars) +': ' + strFunc # convert to lambda function 
            lambdaFunc = eval(lambdaStr)

            # store lambda function and func vars in connParam (for weight, delay and synsPerConn since only calculated for certain conns)
            params[paramStrFunc+'Func'] = lambdaFunc
            params[paramStrFunc+'FuncVars'] = {strVar: dictVars[strVar] for strVar in strVars} 
 
            # initialize randomizer in case used in function
            seed(sim.id32('%d'%(sim.cfg.seeds['conn']+postCellsTags.keys()[0])))

            # replace lambda function (with args as dict of lambda funcs) with list of values
            strParams[paramStrFunc+'List'] = {postGid: params[paramStrFunc+'Func'](**{k:v if isinstance(v, Number) else v(postCellTags) for k,v in params[paramStrFunc+'FuncVars'].iteritems()})  
                    for postGid,postCellTags in postCellsTags.iteritems()}

        return strParams

    ###############################################################################
    # Calculate distance between 2 segments
    ###############################################################################
    def fromtodistance(self, origin_segment, to_segment):
        h.distance(0, origin_segment.x, sec=origin_segment.sec)
        return h.distance(to_segment.x, sec=to_segment.sec)


    ###############################################################################
    # Calculate 2d point from segment location
    ###############################################################################
    def _posFromLoc(self, sec, x):
        sec.push()
        s = x * sec.L
        numpts = int(h.n3d())
        b = -1
        for ii in range(numpts):
            if h.arc3d(ii) >= s:
                b = ii
                break
        if b == -1: print "an error occurred in pointFromLoc, SOMETHING IS NOT RIGHT"

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


    ###############################################################################
    # Calculate syn density for each segment from grid
    ###############################################################################
    def _interpolateSegmentSigma(self, cell, secList, gridX, gridY, gridSigma):
        segNumSyn = {}  #
        for secName in secList:
            sec = cell.secs[secName]
            segNumSyn[secName] = []
            for seg in sec['hSec']:
                x, y, z = self._posFromLoc(sec['hSec'], seg.x)
                if gridX and gridY: # 2D
                    distX = [abs(gx-x) for gx in gridX]
                    distY = [abs(gy-y) for gy in gridY]
                    ixs = array(distX).argsort()[:2]
                    jys = array(distY).argsort()[:2]
                    i1,i2,j1,j2 = min(ixs), max(ixs), min(jys), max(jys) 
                    x1,x2,y1,y2 = gridX[i1], gridX[i2], gridY[j1], gridY[j2]
                    sigma_x1_y1 = gridSigma[i1][j1]
                    sigma_x1_y2 = gridSigma[i1][j2]
                    sigma_x2_y1 = gridSigma[i2][j1]
                    sigma_x2_y2 = gridSigma[i2][j2]

                    if x1 == x2 or y1 == y2: 
                        print "ERROR in closest grid points: ", secName, x1, x2, y1, y2
                    else:
                       # bilinear interpolation, see http://en.wikipedia.org/wiki/Bilinear_interpolation
                       sigma = ((sigma_x1_y1*abs(x2-x)*abs(y2-y) + sigma_x2_y1*abs(x-x1)*abs(y2-y) + sigma_x1_y2*abs(x2-x)*abs(y-y1) + sigma_x2_y2*abs(x-x1)*abs(y-y1))/(abs(x2-x1)*abs(y2-y1)))
                       #sigma = ((sigma_x1_y1*abs(x2-x)*abs(y2-y) + sigma_x2_y1*abs(x-x1)*abs(y2-y) + sigma_x1_y2*abs(x2-x)*abs(y-y1) + sigma_x2_y2*abs(x-x1)*abs(y-y1))/((x2-x1)*(y2-y1)))

                elif gridY:  # 1d = radial
                    distY = [abs(gy-y) for gy in gridY]
                    jys = array(distY).argsort()[:2]
                    sigma = zeros((1,2))
                    j1,j2 = min(jys), max(jys)
                    y1, y2 = gridY[j1], gridY[j2]
                    sigma_y1 = gridSigma[j1]
                    sigma_y2 = gridSigma[j2]

                    if y1 == y2: 
                        print "ERROR in closest grid points: ", secName, y1, y2
                    else:
                       # linear interpolation, see http://en.wikipedia.org/wiki/Bilinear_interpolation
                       sigma = ((sigma_y1*abs(y2-y) + sigma_y2*abs(y-y1)) / abs(y2-y1))

                numSyn = sigma * sec['hSec'].L / sec['hSec'].nseg  # return num syns 
                segNumSyn[secName].append(numSyn)

        return segNumSyn


    ###############################################################################
    # Subcellular connectivity (distribution of synapses)
    ###############################################################################
    def subcellularConn(self, allCellTags, allPopTags):
        sim.timing('start', 'subConnectTime')
        print('  Distributing synapses based on subcellular connectivity rules...')

        for subConnParamTemp in self.params.subConnParams.values():  # for each conn rule or parameter set
            subConnParam = subConnParamTemp.copy()

            # find list of pre and post cell
            preCellsTags, postCellsTags = self._findPrePostCellsCondition(allCellTags, allPopTags, subConnParam['preConds'], subConnParam['postConds'])

            if preCellsTags and postCellsTags:
                # iterate over postsyn cells to redistribute synapses
                for postCellGid in postCellsTags:  # for each postsyn cell
                    if postCellGid in self.lid2gid:
                        postCell = self.cells[self.gid2lid[postCellGid]] 
                        allConns = [conn for conn in postCell.conns if conn['preGid'] in preCellsTags]
                        if 'NetStim' in [x['cellModel'] for x in preCellsTags.values()]: # temporary fix to include netstim conns 
                            allConns.extend([conn for conn in postCell.conns if conn['preGid'] == 'NetStim'])

                        # group synMechs so they are not distributed separately
                        if subConnParam.get('groupSynMechs', None):  
                            conns = []
                            connsGroup = {}
                            iConn = -1
                            for conn in allConns:
                                if not conn['synMech'].startswith('__grouped__'):
                                    conns.append(conn)
                                    iConn = iConn + 1
                                    if conn['synMech'] in subConnParam['groupSynMechs']:
                                        for synMech in [s for s in subConnParam['groupSynMechs'] if s != conn['synMech']]:
                                            connGroup = next(c for c in allConns if c['synMech'] == synMech and c['sec']==conn['sec'] and c['loc']==conn['loc'])
                                            connGroup['synMech'] = '__grouped__'+connGroup['synMech']
                                            connsGroup[iConn] = connGroup
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
                            somaX, somaY, _ = self._posFromLoc(postCell.secs['soma']['hSec'], 0.5) # get cell pos move method to Cell!
                            if subConnParam['density'].get('fixedSomaY', None):  # is fixed cell soma y, adjust y grid accordingly
                                fixedSomaY = subConnParam['density'].get('fixedSomaY')
                                gridY = [y+(somaY-fixedSomaY) for y in gridY] # adjust grid so cell soma is at fixedSomaY
                            if subConnParam['density']['type'] == '2Dmap': # 2D    
                                gridX = [x - somaX for x in subConnParam['density']['gridX']] # center x at cell soma
                                segNumSyn = self._interpolateSegmentSigma(postCell, secList, gridX, gridY, gridSigma) # move method to Cell!
                            elif subConnParam['density']['type'] == '1Dmap': # 1D
                                segNumSyn = self._interpolateSegmentSigma(postCell, secList, None, gridY, gridSigma) # move method to Cell!

                            totSyn = sum([sum(nsyn) for nsyn in segNumSyn.values()])  # summed density
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

                            totSynRescale = sum([sum(nsyn) for nsyn in segNumSyn.values()])

                            # if missing syns due to rescaling to 0, find top values which were rounded to 0 and make 1
                            if totSynRescale < len(conns):  
                                extraSyns = len(conns)-totSynRescale
                                diffList = sorted(diffList, key=lambda l:l[0], reverse=True)
                                for i in range(extraSyns):
                                    sec = diffList[i][1]
                                    seg = diffList[i][2]
                                    segNumSyn[sec][seg] += 1

                            # convert to list so can serialize and save
                            subConnParam['density']['gridY'] = list(subConnParam['density']['gridY'])
                            subConnParam['density']['gridValues'] = list(subConnParam['density']['gridValues']) 

                            newSecs, newLocs = [], []
                            for sec, nsyns in segNumSyn.iteritems():
                                for i, seg in enumerate(postCell.secs[sec]['hSec']):
                                    for isyn in range(nsyns[i]):
                                        newSecs.append(sec)
                                        newLocs.append(seg.x)


                        # Distance-based
                        elif subConnParam.get('density', None) == 'distance':
                            # find origin section 
                            if 'soma' in postCell.secs: 
                                secOrig = 'soma' 
                            elif any([secName.startswith('som') for secName in postCell.secs.keys()]):
                                secOrig = next(secName for secName in postCell.secs.keys() if secName.startswith('soma'))
                            else: 
                                secOrig = postCell.secs.keys()[0]

                            #print self.fromtodistance(postCell.secs[secOrig](0.5), postCell.secs['secs'][conn['sec']](conn['loc']))

                            # different case if has vs doesn't have 3d points
                            #  h.distance(sec=h.soma[0], seg=0)
                            # for sec in apical:
                            #    print h.secname()
                            #    for seg in sec:
                            #      print seg.x, h.distance(seg.x)


                        for i,(conn, newSec, newLoc) in enumerate(zip(conns, newSecs, newLocs)):
                            conn['sec'] = newSec
                            conn['loc'] = newLoc

                            # find grouped conns 
                            if subConnParam.get('groupSynMechs', None) and conn['synMech'] in subConnParam['groupSynMechs']:
                                connGroup = connsGroup[i]  # get grouped conn from previously stored dict 
                                connGroup['synMech'] = connGroup['synMech'].split('__grouped__')[1]  # remove '__grouped__' label

                                connGroup['sec'] = newSec
                                connGroup['loc'] = newLoc
                                    
            sim.pc.barrier()


    ###############################################################################
    # Connect Cells
    ###############################################################################
    def connectCells (self):
        # Instantiate network connections based on the connectivity rules defined in params
        sim.timing('start', 'connectTime')
        if sim.rank==0: 
            print('Making connections...')

        if sim.nhosts > 1: # Gather tags from all cells 
            allCellTags = sim._gatherAllCellTags()  
        else:
            allCellTags = {cell.gid: cell.tags for cell in self.cells}
        allPopTags = {-i: pop.tags for i,pop in enumerate(self.pops.values())}  # gather tags from pops so can connect NetStim pops

        if self.params.subConnParams:  # do not create NEURON objs until synapses are distributed based on subConnParams
            origCreateNEURONObj = bool(sim.cfg.createNEURONObj)
            origAddSynMechs = bool(sim.cfg.addSynMechs)
            sim.cfg.createNEURONObj = False
            sim.cfg.addSynMechs = False


        for connParamLabel,connParamTemp in self.params.connParams.iteritems():  # for each conn rule or parameter set
            connParam = connParamTemp.copy()
            connParam['label'] = connParamLabel

            # find pre and post cells that match conditions
            preCellsTags, postCellsTags = self._findPrePostCellsCondition(allCellTags, allPopTags, connParam['preConds'], connParam['postConds'])

            # call appropriate conn function
            if 'connFunc' not in connParam:  # if conn function not specified, select based on params
                if 'probability' in connParam: connParam['connFunc'] = 'probConn'  # probability based func
                elif 'convergence' in connParam: connParam['connFunc'] = 'convConn'  # convergence function
                elif 'divergence' in connParam: connParam['connFunc'] = 'divConn'  # divergence function
                elif 'connList' in connParam: connParam['connFunc'] = 'fromListConn'  # from list function
                else: connParam['connFunc'] = 'fullConn'  # convergence function

            connFunc = getattr(self, connParam['connFunc'])  # get function name from params
            if preCellsTags and postCellsTags:
                self._connStrToFunc(preCellsTags, postCellsTags, connParam)  # convert strings to functions (for the delay, and probability params)
                connFunc(preCellsTags, postCellsTags, connParam)  # call specific conn function

        # add gap junctions of presynaptic cells (need to do separately because could be in different ranks)
        for preGapParams in getattr(sim.net, 'preGapJunctions', []):
            if preGapParams['gid'] in self.lid2gid:  # only cells in this rank
                cell = self.cells[self.gid2lid[preGapParams['gid']]] 
                cell.addConn(preGapParams)

        # apply subcellular connectivity params (distribution of synaspes)
        if self.params.subConnParams:
            self.subcellularConn(allCellTags, allPopTags)
            sim.cfg.createNEURONObj = origCreateNEURONObj # set to original value
            sim.cfg.addSynMechs = origAddSynMechs # set to original value
            for cell in sim.net.cells:    
                # Add synMechs, stim and conn NEURON objects
                cell.addStimsNEURONObj()
                #cell.addSynMechsNEURONObj()
                cell.addConnsNEURONObj()


        print('  Number of connections on node %i: %i ' % (sim.rank, sum([len(cell.conns) for cell in self.cells])))
        sim.pc.barrier()
        sim.timing('stop', 'connectTime')
        if sim.rank == 0 and sim.cfg.timing: print('  Done; cell connection time = %0.2f s.' % sim.timingData['connectTime'])

        return [cell.conns for cell in self.cells]


    ###############################################################################
    # Find pre and post cells matching conditions
    ###############################################################################
    def _findCellsCondition(self, allCellTags, conds):
        cellsTags = dict(allCellTags)
        for condKey,condValue in conds.iteritems():  # Find subset of cells that match presyn criteria
            if condKey in ['x','y','z','xnorm','ynorm','znorm']:
                cellsTags = {gid: tags for (gid,tags) in cellsTags.iteritems() if condValue[0] <= tags[condKey] < condValue[1]}  # dict with pre cell tags
                prePops = {}
            else:
                if isinstance(condValue, list): 
                    cellsTags = {gid: tags for (gid,tags) in cellsTags.iteritems() if tags[condKey] in condValue}  # dict with pre cell tags
                    prePops = {i: tags for (i,tags) in prePops.iteritems() if (condKey in tags) and (tags[condKey] in condValue)}
                else:
                    cellsTags = {gid: tags for (gid,tags) in cellsTags.iteritems() if tags[condKey] == condValue}  # dict with pre cell tags
                    prePops = {i: tags for (i,tags) in prePops.iteritems() if (condKey in tags) and (tags[condKey] == condValue)}

        return cellsTags


    ###############################################################################
    # Find pre and post cells matching conditions
    ###############################################################################
    def _findPrePostCellsCondition(self, allCellTags, allPopTags, preConds, postConds):
        preCellsTags = dict(allCellTags)  # initialize with all presyn cells (make copy)
        prePops = allPopTags  # initialize with all presyn pops
        postCellsTags = None

        for condKey,condValue in preConds.iteritems():  # Find subset of cells that match presyn criteria
            if condKey in ['x','y','z','xnorm','ynorm','znorm']:
                preCellsTags = {gid: tags for (gid,tags) in preCellsTags.iteritems() if condValue[0] <= tags[condKey] < condValue[1]}  # dict with pre cell tags
                prePops = {}
            else:
                if isinstance(condValue, list): 
                    preCellsTags = {gid: tags for (gid,tags) in preCellsTags.iteritems() if tags[condKey] in condValue}  # dict with pre cell tags
                    prePops = {i: tags for (i,tags) in prePops.iteritems() if (condKey in tags) and (tags[condKey] in condValue)}
                else:
                    preCellsTags = {gid: tags for (gid,tags) in preCellsTags.iteritems() if tags[condKey] == condValue}  # dict with pre cell tags
                    prePops = {i: tags for (i,tags) in prePops.iteritems() if (condKey in tags) and (tags[condKey] == condValue)}
                

        if not preCellsTags: # if no presyn cells, check if netstim
            if any (prePopTags['cellModel'] == 'NetStim' for prePopTags in prePops.values()):
                for prePop in prePops.values():
                    if not 'start' in prePop: prePop['start'] = 1  # add default start time
                    if not 'number' in prePop: prePop['number'] = 1e9  # add default number 
                preCellsTags = prePops

        if preCellsTags:  # only check post if there are pre
            postCellsTags = allCellTags
            for condKey,condValue in postConds.iteritems():  # Find subset of cells that match postsyn criteria
                if condKey in ['x','y','z','xnorm','ynorm','znorm']:
                    postCellsTags = {gid: tags for (gid,tags) in postCellsTags.iteritems() if condValue[0] <= tags[condKey] < condValue[1]}  # dict with post Cell objects}  # dict with pre cell tags
                elif isinstance(condValue, list): 
                    postCellsTags = {gid: tags for (gid,tags) in postCellsTags.iteritems() if tags[condKey] in condValue}  # dict with post Cell objects
                else:
                    postCellsTags = {gid: tags for (gid,tags) in postCellsTags.iteritems() if tags[condKey] == condValue}  # dict with post Cell objects

        return preCellsTags, postCellsTags


    ###############################################################################
    # Convert connection param string to function
    ###############################################################################
    def _connStrToFunc (self, preCellsTags, postCellsTags, connParam):
        # list of params that have a function passed in as a string
        paramsStrFunc = [param for param in self.connStringFuncParams+['probability', 'convergence', 'divergence'] if param in connParam and isinstance(connParam[param], str)]  

        # dict to store correspondence between string and actual variable
        dictVars = {}  
        dictVars['pre_x']       = lambda preConds,postConds: preConds['x'] 
        dictVars['pre_y']       = lambda preConds,postConds: preConds['y'] 
        dictVars['pre_z']       = lambda preConds,postConds: preConds['z'] 
        dictVars['pre_xnorm']   = lambda preConds,postConds: preConds['xnorm'] 
        dictVars['pre_ynorm']   = lambda preConds,postConds: preConds['ynorm'] 
        dictVars['pre_znorm']   = lambda preConds,postConds: preConds['znorm'] 
        dictVars['post_x']      = lambda preConds,postConds: postConds['x'] 
        dictVars['post_y']      = lambda preConds,postConds: postConds['y'] 
        dictVars['post_z']      = lambda preConds,postConds: postConds['z'] 
        dictVars['post_xnorm']  = lambda preConds,postConds: postConds['xnorm'] 
        dictVars['post_ynorm']  = lambda preConds,postConds: postConds['ynorm'] 
        dictVars['post_znorm']  = lambda preConds,postConds: postConds['znorm'] 
        dictVars['dist_x']      = lambda preConds,postConds: abs(preConds['x'] - postConds['x'])
        dictVars['dist_y']      = lambda preConds,postConds: abs(preConds['y'] - postConds['y']) 
        dictVars['dist_z']      = lambda preConds,postConds: abs(preConds['z'] - postConds['z'])
        dictVars['dist_3D']    = lambda preConds,postConds: sqrt((preConds['x'] - postConds['x'])**2 +
                                (preConds['y'] - postConds['y'])**2 + 
                                (preConds['z'] - postConds['z'])**2)
        dictVars['dist_2D']     = lambda preConds,postConds: sqrt((preConds['x'] - postConds['x'])**2 +
                                (preConds['z'] - postConds['z'])**2)
        dictVars['dist_xnorm']  = lambda preConds,postConds: abs(preConds['xnorm'] - postConds['xnorm'])
        dictVars['dist_ynorm']  = lambda preConds,postConds: abs(preConds['ynorm'] - postConds['ynorm']) 
        dictVars['dist_znorm']  = lambda preConds,postConds: abs(preConds['znorm'] - postConds['znorm'])
        dictVars['dist_norm3D'] = lambda preConds,postConds: sqrt((preConds['xnorm'] - postConds['xnorm'])**2 +
                                sqrt(preConds['ynorm'] - postConds['ynorm']) + 
                                sqrt(preConds['znorm'] - postConds['znorm']))
        dictVars['dist_norm2D'] = lambda preConds,postConds: sqrt((preConds['xnorm'] - postConds['xnorm'])**2 +
                                sqrt(preConds['znorm'] - postConds['znorm']))
        
        # add netParams variables
        for k,v in self.params.__dict__.iteritems():
            if isinstance(v, Number):
                dictVars[k] = v

        # for each parameter containing a function, calculate lambda function and arguments
        for paramStrFunc in paramsStrFunc:
            strFunc = connParam[paramStrFunc]  # string containing function
            strVars = [var for var in dictVars.keys() if var in strFunc and var+'norm' not in strFunc]  # get list of variables used (eg. post_ynorm or dist_xyz)
            lambdaStr = 'lambda ' + ','.join(strVars) +': ' + strFunc # convert to lambda function 
            lambdaFunc = eval(lambdaStr)
       
            # initialize randomizer in case used in function
            seed(sim.id32('%d'%(sim.cfg.seeds['conn'])))

            if paramStrFunc in ['probability']:
                # replace function with dict of values derived from function (one per pre+post cell)
                connParam[paramStrFunc+'Func'] = {(preGid,postGid): lambdaFunc(
                    **{strVar: dictVars[strVar] if isinstance(dictVars[strVar], Number) else dictVars[strVar](preCellTags, postCellTags) for strVar in strVars})  
                    for preGid,preCellTags in preCellsTags.iteritems() for postGid,postCellTags in postCellsTags.iteritems()}

            elif paramStrFunc in ['convergence']:
                # replace function with dict of values derived from function (one per post cell)
                connParam[paramStrFunc+'Func'] = {postGid: lambdaFunc(
                    **{strVar: dictVars[strVar] if isinstance(dictVars[strVar], Number) else dictVars[strVar](None, postCellTags) for strVar in strVars}) 
                    for postGid,postCellTags in postCellsTags.iteritems()}

            elif paramStrFunc in ['divergence']:
                # replace function with dict of values derived from function (one per post cell)
                connParam[paramStrFunc+'Func'] = {preGid: lambdaFunc(
                    **{strVar: dictVars[strVar] if isinstance(dictVars[strVar], Number) else dictVars[strVar](preCellTags, None) for strVar in strVars}) 
                    for preGid, preCellTags in preCellsTags.iteritems()}

            else:
                # store lambda function and func vars in connParam (for weight, delay and synsPerConn since only calculated for certain conns)
                connParam[paramStrFunc+'Func'] = lambdaFunc
                connParam[paramStrFunc+'FuncVars'] = {strVar: dictVars[strVar] for strVar in strVars} 
 

    ###############################################################################
    ### Full connectivity
    ###############################################################################
    def fullConn (self, preCellsTags, postCellsTags, connParam):
        ''' Generates connections between all pre and post-syn cells '''
        if sim.cfg.verbose: print 'Generating set of all-to-all connections (rule: %s) ...' % (connParam['label'])

        # get list of params that have a lambda function
        paramsStrFunc = [param for param in [p+'Func' for p in self.connStringFuncParams] if param in connParam] 

        for paramStrFunc in paramsStrFunc:
            # replace lambda function (with args as dict of lambda funcs) with list of values
            seed(sim.id32('%d'%(sim.cfg.seeds['conn']+preCellsTags.keys()[0]+postCellsTags.keys()[0])))
            connParam[paramStrFunc[:-4]+'List'] = {(preGid,postGid): connParam[paramStrFunc](**{k:v if isinstance(v, Number) else v(preCellTags,postCellTags) for k,v in connParam[paramStrFunc+'Vars'].iteritems()})  
                for preGid,preCellTags in preCellsTags.iteritems() for postGid,postCellTags in postCellsTags.iteritems()}
        
        for postCellGid in postCellsTags:  # for each postsyn cell
            if postCellGid in self.lid2gid:  # check if postsyn is in this node's list of gids
                for preCellGid, preCellTags in preCellsTags.iteritems():  # for each presyn cell
                    if preCellTags['cellModel'] == 'NetStim':  # if NetStim
                        self._addNetStimParams(connParam, preCellTags) # cell method to add connection  
                        self._addCellConn(connParam, preCellGid, postCellGid) # add connection             
                    elif preCellGid != postCellGid: # if not self-connection
                        self._addCellConn(connParam, preCellGid, postCellGid) # add connection


    ###############################################################################
    ### Probabilistic connectivity 
    ###############################################################################
    def probConn (self, preCellsTags, postCellsTags, connParam):
        ''' Generates connections between all pre and post-syn cells based on probability values'''
        if sim.cfg.verbose: print 'Generating set of probabilistic connections (rule: %s) ...' % (connParam['label'])

        seed(sim.id32('%d'%(sim.cfg.seeds['conn']+preCellsTags.keys()[-1]+postCellsTags.keys()[-1])))  
        allRands = {(preGid,postGid): random() for preGid in preCellsTags for postGid in postCellsTags}  # Create an array of random numbers for checking each connection

        # get list of params that have a lambda function
        paramsStrFunc = [param for param in [p+'Func' for p in self.connStringFuncParams] if param in connParam] 

        for postCellGid,postCellTags in postCellsTags.iteritems():  # for each postsyn cell
            if postCellGid in self.lid2gid:  # check if postsyn is in this node
                for preCellGid, preCellTags in preCellsTags.iteritems():  # for each presyn cell
                    probability = connParam['probabilityFunc'][preCellGid,postCellGid] if 'probabilityFunc' in connParam else connParam['probability']
                    
                    for paramStrFunc in paramsStrFunc: # call lambda functions to get weight func args
                        connParam[paramStrFunc+'Args'] = {k:v if isinstance(v, Number) else v(preCellTags,postCellTags) for k,v in connParam[paramStrFunc+'Vars'].iteritems()}  
                  
                    if probability >= allRands[preCellGid,postCellGid]:      
                        seed(sim.id32('%d'%(sim.cfg.seeds['conn']+postCellGid+preCellGid)))  
                        if preCellTags['cellModel'] == 'NetStim':  # if NetStim
                            self._addNetStimParams(connParam, preCellTags) # cell method to add connection       
                            self._addCellConn(connParam, preCellGid, postCellGid) # add connection        
                        elif preCellGid != postCellGid: # if not self-connection
                           self._addCellConn(connParam, preCellGid, postCellGid) # add connection


    ###############################################################################
    ### Convergent connectivity 
    ###############################################################################
    def convConn (self, preCellsTags, postCellsTags, connParam):
        ''' Generates connections between all pre and post-syn cells based on probability values'''
        if sim.cfg.verbose: print 'Generating set of convergent connections (rule: %s) ...' % (connParam['label'])
               
        # get list of params that have a lambda function
        paramsStrFunc = [param for param in [p+'Func' for p in self.connStringFuncParams] if param in connParam] 

        for postCellGid,postCellTags in postCellsTags.iteritems():  # for each postsyn cell
            if postCellGid in self.lid2gid:  # check if postsyn is in this node
                convergence = connParam['convergenceFunc'][postCellGid] if 'convergenceFunc' in connParam else connParam['convergence']  # num of presyn conns / postsyn cell
                convergence = max(min(int(round(convergence)), len(preCellsTags)), 0)
                seed(sim.id32('%d'%(sim.cfg.seeds['conn']+postCellGid)))  
                preCellsSample = sample(preCellsTags.keys(), convergence)  # selected gids of presyn cells
                preCellsConv = {k:v for k,v in preCellsTags.iteritems() if k in preCellsSample}  # dict of selected presyn cells tags
                for preCellGid, preCellTags in preCellsConv.iteritems():  # for each presyn cell
             
                    for paramStrFunc in paramsStrFunc: # call lambda functions to get weight func args
                        connParam[paramStrFunc+'Args'] = {k:v if isinstance(v, Number) else v(preCellTags,postCellTags) for k,v in connParam[paramStrFunc+'Vars'].iteritems()}  
        
                    seed(sim.id32('%d'%(sim.cfg.seeds['conn']+postCellGid+preCellGid)))  
                    if preCellTags['cellModel'] == 'NetStim':  # if NetStim
                        print 'Error: Convergent connectivity for NetStims is not implemented'
                    if preCellGid != postCellGid: # if not self-connection   
                        self._addCellConn(connParam, preCellGid, postCellGid) # add connection


    ###############################################################################
    ### Divergent connectivity 
    ###############################################################################
    def divConn (self, preCellsTags, postCellsTags, connParam):
        ''' Generates connections between all pre and post-syn cells based on probability values'''
        if sim.cfg.verbose: print 'Generating set of divergent connections (rule: %s) ...' % (connParam['label'])
         
        # get list of params that have a lambda function
        paramsStrFunc = [param for param in [p+'Func' for p in self.connStringFuncParams] if param in connParam] 

        for preCellGid, preCellTags in preCellsTags.iteritems():  # for each presyn cell
            divergence = connParam['divergenceFunc'][preCellGid] if 'divergenceFunc' in connParam else connParam['divergence']  # num of presyn conns / postsyn cell
            divergence = max(min(int(round(divergence)), len(postCellsTags)), 0)
            seed(sim.id32('%d'%(sim.cfg.seeds['conn']+preCellGid)))  
            postCellsSample = sample(postCellsTags, divergence)  # selected gids of postsyn cells
            postCellsDiv = {postGid:postConds  for postGid,postConds in postCellsTags.iteritems() if postGid in postCellsSample and postGid in self.lid2gid}  # dict of selected postsyn cells tags
            for postCellGid, postCellTags in postCellsDiv.iteritems():  # for each postsyn cell
                
                for paramStrFunc in paramsStrFunc: # call lambda functions to get weight func args
                    connParam[paramStrFunc+'Args'] = {k:v if isinstance(v, Number) else v(preCellTags,postCellTags) for k,v in connParam[paramStrFunc+'Vars'].iteritems()}  
 
                seed(sim.id32('%d'%(sim.cfg.seeds['conn']+postCellGid+preCellGid)))  
                if preCellTags['cellModel'] == 'NetStim':  # if NetStim
                    print 'Error: Divergent connectivity for NetStims is not implemented'           
                if preCellGid != postCellGid: # if not self-connection
                    self._addCellConn(connParam, preCellGid, postCellGid) # add connection

                    
    ###############################################################################
    ### From list connectivity 
    ###############################################################################
    def fromListConn (self, preCellsTags, postCellsTags, connParam):
        ''' Generates connections between all pre and post-syn cells based list of relative cell ids'''
        if sim.cfg.verbose: print 'Generating set of connections from list (rule: %s) ...' % (connParam['label'])

        # list of params that can have a lambda function
        paramsStrFunc = [param for param in [p+'Func' for p in self.connStringFuncParams] if param in connParam] 
        for paramStrFunc in paramsStrFunc:
            # replace lambda function (with args as dict of lambda funcs) with list of values
            seed(sim.id32('%d'%(sim.cfg.seeds['conn']+preCellsTags.keys()[0]+postCellsTags.keys()[0])))
            connParam[paramStrFunc[:-4]+'List'] = {(preGid,postGid): connParam[paramStrFunc](**{k:v if isinstance(v, Number) else v(preCellTags,postCellTags) for k,v in connParam[paramStrFunc+'Vars'].iteritems()})  
                    for preGid,preCellTags in preCellsTags.iteritems() for postGid,postCellTags in postCellsTags.iteritems()}

        if isinstance(connParam['weight'], list): connParam['weightFromList'] = list(connParam['weight'])  # if weight is a list, copy to weightFromList
        if isinstance(connParam['delay'], list): connParam['delayFromList'] = list(connParam['delay'])  # if delay is a list, copy to delayFromList
        if isinstance(connParam['loc'], list): connParam['locFromList'] = list(connParam['loc'])  # if delay is a list, copy to locFromList
        
        orderedPreGids = sorted(preCellsTags.keys())
        orderedPostGids = sorted(postCellsTags.keys())

        for iconn, (relativePreId, relativePostId) in enumerate(connParam['connList']):  # for each postsyn cell
            preCellGid = orderedPreGids[relativePreId]
            preCellTags = preCellsTags[preCellGid]  # get pre cell based on relative id        
            postCellGid = orderedPostGids[relativePostId]
            if postCellGid in self.lid2gid:  # check if postsyn is in this node's list of gids
                
                if 'weightFromList' in connParam: connParam['weight'] = connParam['weightFromList'][iconn] 
                if 'delayFromList' in connParam: connParam['delay'] = connParam['delayFromList'][iconn]

                if preCellTags['cellModel'] == 'NetStim':  # if NetStim
                    print 'Error: fromList connectivity for NetStims is not implemented'           
                if preCellGid != postCellGid: # if not self-connection
                    self._addCellConn(connParam, preCellGid, postCellGid) # add connection


    ###############################################################################
    ### Set parameters and create NetStim and connection
    ###############################################################################
    def _addNetStimParams (self, connParam, preCellTags):

        netStimParams = {'source': preCellTags['popLabel'],
        'type': preCellTags['cellModel'],
        'rate': preCellTags['rate'],
        'noise': preCellTags['noise'],
        'number': preCellTags['number'],
        'start': preCellTags['start'],
        'seed': preCellTags['seed'] if 'seed' in preCellTags else sim.cfg.seeds['stim']}

        connParam['netStimParams'] = netStimParams


    ###############################################################################
    ### Set parameters and create connection
    ###############################################################################
    def _addCellConn (self, connParam, preCellGid, postCellGid):
        # set final param values
        paramStrFunc = self.connStringFuncParams
        finalParam = {}
        for param in paramStrFunc:
            if param+'List' in connParam:
                finalParam[param] = connParam[param+'List'][preCellGid,postCellGid]
            elif param+'Func' in connParam:
                finalParam[param] = connParam[param+'Func'](**connParam[param+'FuncArgs']) 
            else:
                finalParam[param] = connParam.get(param)

        # get Cell object 
        postCell = self.cells[self.gid2lid[postCellGid]] 

        # convert synMech param to list (if not already)
        if not isinstance(connParam.get('synMech'), list):
            connParam['synMech'] = [connParam.get('synMech')]

        # generate dict with final params for each synMech
        paramPerSynMech = ['weight', 'delay', 'loc']
        for i, synMech in enumerate(connParam.get('synMech')):

            for param in paramPerSynMech:
                finalParam[param+'SynMech'] = finalParam.get(param)
                if len(connParam['synMech']) > 1:
                    if isinstance (finalParam.get(param), list):  # get weight from list for each synMech
                        finalParam[param+'SynMech'] = finalParam[param][i]
                    elif 'synMech'+param+'Factor' in connParam: # adapt weight for each synMech
                        finalParam[param+'SynMech'] = finalParam[param] * connParam['synMech'+param+'Factor'][i]

            params = {'preGid': preCellGid, 
            'sec': connParam.get('sec'), 
            'loc': finalParam['locSynMech'], 
            'synMech': synMech, 
            'weight': finalParam['weightSynMech'],
            'delay': finalParam['delaySynMech'],
            'threshold': connParam.get('threshold'),
            'synsPerConn': finalParam['synsPerConn'],
            'shape': connParam.get('shape'),
            'plast': connParam.get('plast')}
            
            if sim.cfg.includeParamsLabel: params['label'] = connParam.get('label')
            if connParam.get('gapJunction', False): params['gapJunction'] = connParam.get('gapJunction')

            postCell.addConn(params=params, netStimParams=connParam.get('netStimParams'))


    ###############################################################################
    ### Modify cell params
    ###############################################################################
    def modifyCells (self, params, updateMasterAllCells=False):
        # Instantiate network connections based on the connectivity rules defined in params
        sim.timing('start', 'modifyCellsTime')
        if sim.rank==0: 
            print('Modfying cell parameters...')

        for cell in self.cells:
            cell.modify(params)

        if updateMasterAllCells:
            sim._gatherCells()  # update allCells

        sim.timing('stop', 'modifyCellsTime')
        if sim.rank == 0 and sim.cfg.timing: print('  Done; cells modification time = %0.2f s.' % sim.timingData['modifyCellsTime'])


    ###############################################################################
    ### Modify synMech params
    ###############################################################################
    def modifySynMechs (self, params, updateMasterAllCells=False):
        # Instantiate network connections based on the connectivity rules defined in params
        sim.timing('start', 'modifySynMechsTime')
        if sim.rank==0: 
            print('Modfying synaptic mech parameters...')

        for cell in self.cells:
            cell.modifySynMechs(params)

        if updateMasterAllCells:
             sim._gatherCells()  # update allCells

        sim.timing('stop', 'modifySynMechsTime')
        if sim.rank == 0 and sim.cfg.timing: print('  Done; syn mechs modification time = %0.2f s.' % sim.timingData['modifySynMechsTime'])



    ###############################################################################
    ### Modify conn params
    ###############################################################################
    def modifyConns (self, params, updateMasterAllCells=False):
        # Instantiate network connections based on the connectivity rules defined in params
        sim.timing('start', 'modifyConnsTime')
        if sim.rank==0: 
            print('Modfying connection parameters...')

        for cell in self.cells:
            cell.modifyConns(params)

        if updateMasterAllCells:
            sim._gatherCells()  # update allCells

        sim.timing('stop', 'modifyConnsTime')
        if sim.rank == 0 and sim.cfg.timing: print('  Done; connections modification time = %0.2f s.' % sim.timingData['modifyConnsTime'])


    ###############################################################################
    ### Modify stim source params
    ###############################################################################
    def modifyStims (self, params, updateMasterAllCells=False):
        # Instantiate network connections based on the connectivity rules defined in params
        sim.timing('start', 'modifyStimsTime')
        if sim.rank==0: 
            print('Modfying stimulation parameters...')

        for cell in self.cells:
            cell.modifyStims(params)

        if updateMasterAllCells:
            sim._gatherCells()  # update allCells

        sim.timing('stop', 'modifyStimsTime')
        if sim.rank == 0 and sim.cfg.timing: print('  Done; stims modification time = %0.2f s.' % sim.timingData['modifyStimsTime'])





