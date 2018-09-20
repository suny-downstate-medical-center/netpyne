
"""
network/conn.py 

Network class methods to create connections 

Contributors: salvadordura@gmail.com
"""

import numpy as np 
from numbers import Number
from matplotlib.pylab import array, sin, cos, tan, exp, sqrt, mean, inf, dstack, unravel_index, argsort, zeros, ceil, copy 


# -----------------------------------------------------------------------------
# Connect Cells
# -----------------------------------------------------------------------------
def connectCells (self):
    from .. import sim

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

    gapJunctions = False  # assume no gap junctions by default

    for connParamLabel,connParamTemp in self.params.connParams.items():  # for each conn rule or parameter set
        connParam = connParamTemp.copy()
        connParam['label'] = connParamLabel

        # find pre and post cells that match conditions
        preCellsTags, postCellsTags = self._findPrePostCellsCondition(allCellTags, connParam['preConds'], connParam['postConds'])

        # if conn function not specified, select based on params
        if 'connFunc' not in connParam:  
            if 'probability' in connParam: connParam['connFunc'] = 'probConn'  # probability based func
            elif 'convergence' in connParam: connParam['connFunc'] = 'convConn'  # convergence function
            elif 'divergence' in connParam: connParam['connFunc'] = 'divConn'  # divergence function
            elif 'connList' in connParam: connParam['connFunc'] = 'fromListConn'  # from list function
            else: connParam['connFunc'] = 'fullConn'  # convergence function
        connFunc = getattr(self, connParam['connFunc'])  # get function name from params

        # process string-based funcs and call conn function
        if preCellsTags and postCellsTags:
            # initialize randomizer in case used in string-based function (see issue #89 for more details)
            self.rand.Random123(sim.id32('conn_'+connParam['connFunc']), 
                                sim.id32('%d%d%d%d'%(len(preCellsTags), len(postCellsTags), sum(preCellsTags), sum(postCellsTags))), 
                                sim.cfg.seeds['conn'])
            self._connStrToFunc(preCellsTags, postCellsTags, connParam)  # convert strings to functions (for the delay, and probability params)
            connFunc(preCellsTags, postCellsTags, connParam)  # call specific conn function

        # check if gap junctions in any of the conn rules
        if not gapJunctions and 'gapJunction' in connParam: gapJunctions = True

        if sim.cfg.printSynsAfterRule:
            nodeSynapses = sum([len(cell.conns) for cell in sim.net.cells])
            print(('  Number of synaptic contacts on node %i after conn rule %s: %i ' % (sim.rank, connParamLabel, nodeSynapses)))


    # add presynaptoc gap junctions
    if gapJunctions:
        # distribute info on presyn gap junctions across nodes
        if not getattr(sim.net, 'preGapJunctions', False): 
            sim.net.preGapJunctions = []  # if doesn't exist, create list to store presynaptic cell gap junctions
        data = [sim.net.preGapJunctions]*sim.nhosts  # send cells data to other nodes
        data[sim.rank] = None
        gather = sim.pc.py_alltoall(data)  # collect cells data from other nodes (required to generate connections)
        sim.pc.barrier()
        for dataNode in gather:
            if dataNode: sim.net.preGapJunctions.extend(dataNode)

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
        cellsUpdate = [c for c in sim.net.cells if c.tags['cellModel'] not in ['NetStim', 'VecStim']]
        if sim.cfg.createNEURONObj:
            for cell in cellsUpdate:
                # Add synMechs, stim and conn NEURON objects
                cell.addStimsNEURONObj()
                #cell.addSynMechsNEURONObj()
                cell.addConnsNEURONObj()

    nodeSynapses = sum([len(cell.conns) for cell in sim.net.cells]) 
    if sim.cfg.createPyStruct:
        nodeConnections = sum([len(set([conn['preGid'] for conn in cell.conns])) for cell in sim.net.cells])   
    else:
        nodeConnections = nodeSynapses

    print(('  Number of connections on node %i: %i ' % (sim.rank, nodeConnections)))
    if nodeSynapses != nodeConnections:
        print(('  Number of synaptic contacts on node %i: %i ' % (sim.rank, nodeSynapses)))
    sim.pc.barrier()
    sim.timing('stop', 'connectTime')
    if sim.rank == 0 and sim.cfg.timing: print(('  Done; cell connection time = %0.2f s.' % sim.timingData['connectTime']))

    return [cell.conns for cell in self.cells]




# -----------------------------------------------------------------------------
# Find pre and post cells matching conditions
# -----------------------------------------------------------------------------
def _findPrePostCellsCondition(self, allCellTags, preConds, postConds):

    #try:
    preCellsTags = dict(allCellTags)  # initialize with all presyn cells (make copy)
    postCellsTags = None

    for condKey,condValue in preConds.items():  # Find subset of cells that match presyn criteria
        if condKey in ['x','y','z','xnorm','ynorm','znorm']:
            preCellsTags = {gid: tags for (gid,tags) in preCellsTags.items() if condValue[0] <= tags.get(condKey, None) < condValue[1]}  # dict with pre cell tags
        else:
            if isinstance(condValue, list): 
                preCellsTags = {gid: tags for (gid,tags) in preCellsTags.items() if tags.get(condKey, None) in condValue}  # dict with pre cell tags
            else:
                preCellsTags = {gid: tags for (gid,tags) in preCellsTags.items() if tags.get(condKey, None) == condValue}  # dict with pre cell tags

    if preCellsTags:  # only check post if there are pre
        postCellsTags = allCellTags
        for condKey,condValue in postConds.items():  # Find subset of cells that match postsyn criteria
            if condKey in ['x','y','z','xnorm','ynorm','znorm']:
                postCellsTags = {gid: tags for (gid,tags) in postCellsTags.items() if condValue[0] <= tags.get(condKey, None) < condValue[1]}  # dict with post Cell objects}  # dict with pre cell tags
            elif isinstance(condValue, list): 
                postCellsTags = {gid: tags for (gid,tags) in postCellsTags.items() if tags.get(condKey, None) in condValue}  # dict with post Cell objects
            else:
                postCellsTags = {gid: tags for (gid,tags) in postCellsTags.items() if tags.get(condKey, None) == condValue}  # dict with post Cell objects
    #except:
    #   return None, None

    return preCellsTags, postCellsTags


# -----------------------------------------------------------------------------
# Convert connection param string to function
# -----------------------------------------------------------------------------
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
    dictVars['dist_3D']    = lambda preConds,postConds: np.sqrt((preConds['x'] - postConds['x'])**2 +
                            (preConds['y'] - postConds['y'])**2 + 
                            (preConds['z'] - postConds['z'])**2)
    dictVars['dist_3D_border'] = lambda preConds,postConds: np.sqrt((abs(preConds['x'] - postConds['x']) - postConds['borderCorrect'][0])**2 +
                            (abs(preConds['y'] - postConds['y']) - postConds['borderCorrect'][1])**2 + 
                            (abs(preConds['z'] - postConds['z']) - postConds['borderCorrect'][2])**2)
    dictVars['dist_2D']     = lambda preConds,postConds: np.sqrt((preConds['x'] - postConds['x'])**2 +
                            (preConds['z'] - postConds['z'])**2)
    dictVars['dist_xnorm']  = lambda preConds,postConds: abs(preConds['xnorm'] - postConds['xnorm'])
    dictVars['dist_ynorm']  = lambda preConds,postConds: abs(preConds['ynorm'] - postConds['ynorm']) 
    dictVars['dist_znorm']  = lambda preConds,postConds: abs(preConds['znorm'] - postConds['znorm'])
    dictVars['dist_norm3D'] = lambda preConds,postConds: np.sqrt((preConds['xnorm'] - postConds['xnorm'])**2 +
                            np.sqrt(preConds['ynorm'] - postConds['ynorm']) + 
                            np.sqrt(preConds['znorm'] - postConds['znorm']))
    dictVars['dist_norm2D'] = lambda preConds,postConds: np.sqrt((preConds['xnorm'] - postConds['xnorm'])**2 +
                            np.sqrt(preConds['znorm'] - postConds['znorm']))
    dictVars['rand'] = lambda unused1,unused2: self.rand
    
    # add netParams variables
    for k,v in self.params.__dict__.items():
        if isinstance(v, Number):
            dictVars[k] = v

    # for each parameter containing a function, calculate lambda function and arguments
    for paramStrFunc in paramsStrFunc:
        strFunc = connParam[paramStrFunc]  # string containing function
        for randmeth in self.stringFuncRandMethods: strFunc = strFunc.replace(randmeth, 'rand.'+randmeth) # append rand. to h.Random() methods
        strVars = [var for var in list(dictVars.keys()) if var in strFunc and var+'norm' not in strFunc]  # get list of variables used (eg. post_ynorm or dist_xyz)
        lambdaStr = 'lambda ' + ','.join(strVars) +': ' + strFunc # convert to lambda function 
        lambdaFunc = eval(lambdaStr)
   
        if paramStrFunc in ['probability']:
            # replace function with dict of values derived from function (one per pre+post cell)
            connParam[paramStrFunc+'Func'] = {(preGid,postGid): lambdaFunc(
                **{strVar: dictVars[strVar] if isinstance(dictVars[strVar], Number) else dictVars[strVar](preCellTags, postCellTags) for strVar in strVars})  
                for preGid,preCellTags in preCellsTags.items() for postGid,postCellTags in postCellsTags.items()}

        elif paramStrFunc in ['convergence']:
            # replace function with dict of values derived from function (one per post cell)
            connParam[paramStrFunc+'Func'] = {postGid: lambdaFunc(
                **{strVar: dictVars[strVar] if isinstance(dictVars[strVar], Number) else dictVars[strVar](None, postCellTags) for strVar in strVars}) 
                for postGid,postCellTags in postCellsTags.items()}

        elif paramStrFunc in ['divergence']:
            # replace function with dict of values derived from function (one per post cell)
            connParam[paramStrFunc+'Func'] = {preGid: lambdaFunc(
                **{strVar: dictVars[strVar] if isinstance(dictVars[strVar], Number) else dictVars[strVar](preCellTags, None) for strVar in strVars}) 
                for preGid, preCellTags in preCellsTags.items()}

        else:
            # store lambda function and func vars in connParam (for weight, delay and synsPerConn since only calculated for certain conns)
            connParam[paramStrFunc+'Func'] = lambdaFunc
            connParam[paramStrFunc+'FuncVars'] = {strVar: dictVars[strVar] for strVar in strVars} 


# -----------------------------------------------------------------------------
# Disynaptic bias for probability
# -----------------------------------------------------------------------------
def _disynapticBiasProb(self, origProbability, bias, prePreGids, postPreGids, disynCounter, maxImbalance=10):
    probability = float(origProbability)
    factor = bias/origProbability
    #bias = min(bias, origProbability)  # don't modify more than orig, so can compensate
    if not set(prePreGids).isdisjoint(postPreGids) and disynCounter < maxImbalance:
        probability = min(origProbability + bias, 1.0)
        disynCounter += factor #1
    elif disynCounter > -maxImbalance:
        probability = max(origProbability - (min(origProbability + bias, 1.0) - origProbability), 0.0)
        disynCounter -= 1
    #print disynCounter, origProbability, probability
    return probability, disynCounter


# -----------------------------------------------------------------------------
# Disynaptic bias for probability (version 2)
# bis = min fraction of conns that will be disynaptic
# -----------------------------------------------------------------------------
def _disynapticBiasProb2(self, probMatrix, allRands, bias, prePreGids, postPreGids):
    connGids = []
    # calculate which conns are disyn vs 
    disynMatrix = {(preGid, postGid): not set(prePreGids[preGid]).isdisjoint(postPreGids[postGid]) 
            for preGid, postGid in list(probMatrix.keys())}

    # calculate which conns are going to be created
    connCreate = {(preGid, postGid): probMatrix[(preGid, postGid)] >= allRands[(preGid, postGid)]
            for preGid, postGid in list(probMatrix.keys())}
    numConns = len([c for c in list(connCreate.values()) if c])

    # change % bias of conns from non-disyn to disyn (start with low, high probs respectively)
    disynConn, nonDisynConn, disynNotConn = [], [], []
    for (pre,post), disyn in disynMatrix.items():
        if disyn and connCreate[(pre,post)]:
            disynConn.append((pre,post))
        elif not disyn and connCreate[(pre,post)]:
            nonDisynConn.append((pre,post))
        elif disyn and not connCreate[(pre,post)]:
            disynNotConn.append((pre,post))
    disynNumNew = int(float(bias) * numConns)
    disynAdd = disynNumNew - len(disynConn)

    if disynAdd > 0:
        # sort by low/high probs 
        nonDisynConn = sorted(nonDisynConn, key=lambda k: probMatrix[k])
        disynNotConn = sorted(disynNotConn, key=lambda k: probMatrix[k], reverse=True)

        # replaced nonDisynConn with disynNotConn
        for i in range(min(disynAdd, nonDisynConn, disynNotConn)):
            connCreate[nonDisynConn[i]] = False
            connCreate[disynNotConn[i]] = True

    connGids = [(pre,post) for (pre,post), c in connCreate.items() if c]
    return connGids
    

# -----------------------------------------------------------------------------
# Full connectivity
# -----------------------------------------------------------------------------
def fullConn (self, preCellsTags, postCellsTags, connParam):
    from .. import sim

    ''' Generates connections between all pre and post-syn cells '''
    if sim.cfg.verbose: print('Generating set of all-to-all connections (rule: %s) ...' % (connParam['label']))

    # get list of params that have a lambda function
    paramsStrFunc = [param for param in [p+'Func' for p in self.connStringFuncParams] if param in connParam] 

    for paramStrFunc in paramsStrFunc:
        # replace lambda function (with args as dict of lambda funcs) with list of values
        connParam[paramStrFunc[:-4]+'List'] = {(preGid,postGid): connParam[paramStrFunc](**{k:v if isinstance(v, Number) else v(preCellTags,postCellTags) for k,v in connParam[paramStrFunc+'Vars'].items()})  
            for preGid,preCellTags in preCellsTags.items() for postGid,postCellTags in postCellsTags.items()}
    
    for postCellGid in postCellsTags:  # for each postsyn cell
        if postCellGid in self.lid2gid:  # check if postsyn is in this node's list of gids
            for preCellGid, preCellTags in preCellsTags.items():  # for each presyn cell
                self._addCellConn(connParam, preCellGid, postCellGid) # add connection


# -----------------------------------------------------------------------------
# Generate random values for all pre and post cells (to use in prob conn)
# -----------------------------------------------------------------------------
def generateRandsPrePost(self, pre, post):
    from .. import sim
    
    if hasattr(sim.cfg, 'useOldProbConn') and sim.cfg.useOldProbConn:
        if sim.cfg.verbose:
            print(' Creating probabilistic connections using deprecated method (only useful to replicate results from versions < 0.8.0).')
    else:
        pre = sorted(pre)     
        post = sorted(post)

    # Create an array of random numbers for checking each connection 
    allRands = {(preGid, postGid): self.rand.uniform(0,1) for preGid in pre for postGid in post}

    return allRands


# -----------------------------------------------------------------------------
# Probabilistic connectivity 
# -----------------------------------------------------------------------------
def probConn (self, preCellsTags, postCellsTags, connParam):
    from .. import sim

    ''' Generates connections between all pre and post-syn cells based on probability values'''
    if sim.cfg.verbose: print('Generating set of probabilistic connections (rule: %s) ...' % (connParam['label']))

    allRands = self.generateRandsPrePost(preCellsTags.keys(), postCellsTags.keys())

    # get list of params that have a lambda function
    paramsStrFunc = [param for param in [p+'Func' for p in self.connStringFuncParams] if param in connParam] 

    # probabilistic connections with disynapticBias  
    if isinstance(connParam.get('disynapticBias', None), Number):  
        allPreGids = sim._gatherAllCellConnPreGids()
        prePreGids = {gid: allPreGids[gid] for gid in preCellsTags}
        postPreGids = {gid: allPreGids[gid] for gid in postCellsTags}
        
        probMatrix = {(preCellGid,postCellGid): connParam['probabilityFunc'][preCellGid,postCellGid] if 'probabilityFunc' in connParam else connParam['probability']
                                            for postCellGid,postCellTags in postCellsTags.items() # for each postsyn cell
                                            for preCellGid, preCellTags in preCellsTags.items()  # for each presyn cell
                                            if postCellGid in self.lid2gid}  # check if postsyn is in this node
        
        connGids = self._disynapticBiasProb2(probMatrix, allRands, connParam['disynapticBias'], prePreGids, postPreGids)
        for preCellGid, postCellGid in connGids:
            for paramStrFunc in paramsStrFunc: # call lambda functions to get weight func args
                connParam[paramStrFunc+'Args'] = {k:v if isinstance(v, Number) else v(preCellsTags[preCellGid],postCellsTags[postCellGid]) for k,v in connParam[paramStrFunc+'Vars'].items()}  
            self._addCellConn(connParam, preCellGid, postCellGid) # add connection

    # standard probabilistic conenctions   
    else:
        # calculate the conn preGids of the each pre and post cell
        for postCellGid,postCellTags in postCellsTags.items():  # for each postsyn cell
            if postCellGid in self.lid2gid:  # check if postsyn is in this node
                for preCellGid, preCellTags in preCellsTags.items():  # for each presyn cell
                    probability = connParam['probabilityFunc'][preCellGid,postCellGid] if 'probabilityFunc' in connParam else connParam['probability']
                    if probability >= allRands[preCellGid,postCellGid]: 
                        for paramStrFunc in paramsStrFunc: # call lambda functions to get weight func args
                            connParam[paramStrFunc+'Args'] = {k:v if isinstance(v, Number) else v(preCellTags,postCellTags) for k,v in connParam[paramStrFunc+'Vars'].items()}  
                        self._addCellConn(connParam, preCellGid, postCellGid) # add connection


# -----------------------------------------------------------------------------
# Generate random unique integers 
# -----------------------------------------------------------------------------
def randUniqueInt(self, r, N, vmin, vmax):

    r.discunif(vmin,vmax)
    out = []
    while len(out)<N:
        x=int(r.repick())
        if x not in out: out.append(x)
    return out


# -----------------------------------------------------------------------------
# Convergent connectivity 
# -----------------------------------------------------------------------------
def convConn (self, preCellsTags, postCellsTags, connParam):
    from .. import sim

    ''' Generates connections between all pre and post-syn cells based on probability values'''
    if sim.cfg.verbose: print('Generating set of convergent connections (rule: %s) ...' % (connParam['label']))
           
    # get list of params that have a lambda function
    paramsStrFunc = [param for param in [p+'Func' for p in self.connStringFuncParams] if param in connParam] 

    for postCellGid,postCellTags in postCellsTags.items():  # for each postsyn cell
        if postCellGid in self.lid2gid:  # check if postsyn is in this node
            convergence = connParam['convergenceFunc'][postCellGid] if 'convergenceFunc' in connParam else connParam['convergence']  # num of presyn conns / postsyn cell
            convergence = max(min(int(round(convergence)), len(preCellsTags)-1), 0)
            self.rand.Random123(sim.id32('%d%d'%(len(preCellsTags), sum(preCellsTags))), postCellGid, sim.cfg.seeds['conn'])  # init randomizer
            randSample = self.randUniqueInt(self.rand, convergence+1, 0, len(preCellsTags)-1) 
            preCellsSample = [list(preCellsTags.keys())[i] for i in randSample][0:convergence]  # selected gids of presyn cells
            preCellsSample[:] = [randSample[convergence] if x==postCellGid else x for x in preCellsSample] # remove post gid  
            preCellsConv = {k:v for k,v in preCellsTags.items() if k in preCellsSample}  # dict of selected presyn cells tags
            for preCellGid, preCellTags in preCellsConv.items():  # for each presyn cell
         
                for paramStrFunc in paramsStrFunc: # call lambda functions to get weight func args
                    connParam[paramStrFunc+'Args'] = {k:v if isinstance(v, Number) else v(preCellTags,postCellTags) for k,v in connParam[paramStrFunc+'Vars'].items()}  
                if preCellGid != postCellGid: # if not self-connection   
                    self._addCellConn(connParam, preCellGid, postCellGid) # add connection


# -----------------------------------------------------------------------------
# Divergent connectivity 
# -----------------------------------------------------------------------------
def divConn (self, preCellsTags, postCellsTags, connParam):
    from .. import sim

    ''' Generates connections between all pre and post-syn cells based on probability values'''
    if sim.cfg.verbose: print('Generating set of divergent connections (rule: %s) ...' % (connParam['label']))
     
    # get list of params that have a lambda function
    paramsStrFunc = [param for param in [p+'Func' for p in self.connStringFuncParams] if param in connParam] 

    # PERFORMANCE: copy the vars into args immediately and work out which keys are associated with lambda functions only once per method
    funcKeys = {}
    for paramStrFunc in paramsStrFunc:
        connParam[paramStrFunc + 'Args'] = connParam[paramStrFunc + 'Vars'].copy()
        funcKeys[paramStrFunc] = [key for key in connParam[paramStrFunc + 'Vars'] if callable(connParam[paramStrFunc + 'Vars'][key])]

    # PERFORMANCE: converted to list only once 
    postCellsTagsKeys = list(postCellsTags.keys())    

    for preCellGid, preCellTags in preCellsTags.items():  # for each presyn cell
        divergence = connParam['divergenceFunc'][preCellGid] if 'divergenceFunc' in connParam else connParam['divergence']  # num of presyn conns / postsyn cell
        divergence = max(min(int(round(divergence)), len(postCellsTags)-1), 0)
        self.rand.Random123(sim.id32('%d%d'%(len(postCellsTags), sum(postCellsTags))), preCellGid, sim.cfg.seeds['conn'])  # init randomizer
        randSample = self.randUniqueInt(self.rand, divergence+1, 0, len(postCellsTags)-1)
        

        # PERFORMANCE: postCellsSample = [list(postCellsTags.keys())[i] for i in randSample[0:divergence]]  # selected gids of postsyn cells
        # PERFORMANCE: postCellsSample[:] = [randSample[divergence] if x==preCellGid else x for x in postCellsSample] # remove post gid  
        # note: randSample[divergence] is an extra value used only if one of the random postGids coincided with the preGid 
        postCellsSample = {(randSample[divergence] if postCellsTagsKeys[i]==preCellGid else postCellsTagsKeys[i]): 0
                               for i in randSample[0:divergence]}  # dict of selected gids of postsyn cells with removed post (pre?) gid

        # PERFORMANCE: postCellsDiv = {postGid:postConds  for postGid,postConds in postCellsTags.items() if postGid in postCellsSample and postGid in self.lid2gid}  # dict of selected postsyn cells tags
        # PERFORMANCE: for postCellGid, postCellTags in postCellsDiv.items():  # for each postsyn cell
        for postCellGid, postCellTags in postCellsTags.items():
            if postCellGid not in postCellsSample or postCellGid not in self.lid2gid:
                continue
            
            for paramStrFunc in paramsStrFunc: # call lambda functions to get weight func args
                # PERFORMANCE: connParam[paramStrFunc+'Args'] = {k:v if isinstance(v, Number) else v(preCellTags,postCellTags) for k,v in connParam[paramStrFunc+'Vars'].items()}  
        
                # PERFORMANCE: update the relevant FuncArgs dict where lambda functions are known to exist in the corresponding FuncVars dict
                for funcKey in funcKeys[paramStrFunc]:
                    connParam[paramStrFunc + 'Args'][funcKey] = connParam[paramStrFunc+'Vars'][funcKey](preCellTags,postCellTags)

            if preCellGid != postCellGid: # if not self-connection
                self._addCellConn(connParam, preCellGid, postCellGid) # add connection


            # postCellsSample = [postCellsTags.keys()[i] for i in randSample[0:divergence]]  # selected gids of postsyn cells
            # postCellsSample[:] = [randSample[divergence] if x == preCellGid else x for x in postCellsSample]  # remove post gid
            postCellsSample = {(randSample[divergence] if postCellsTagsKeys[i]==preCellGid else postCellsTagsKeys[i]):0
                               for i in randSample[0:divergence]}  # dict of selected gids of postsyn cells with removed post (pre?) gid
                
# -----------------------------------------------------------------------------
# From list connectivity 
# -----------------------------------------------------------------------------
def fromListConn (self, preCellsTags, postCellsTags, connParam):
    from .. import sim

    ''' Generates connections between all pre and post-syn cells based list of relative cell ids'''
    if sim.cfg.verbose: print('Generating set of connections from list (rule: %s) ...' % (connParam['label']))

    # list of params that can have a lambda function
    paramsStrFunc = [param for param in [p+'Func' for p in self.connStringFuncParams] if param in connParam] 
    for paramStrFunc in paramsStrFunc:
        # replace lambda function (with args as dict of lambda funcs) with list of values
        connParam[paramStrFunc[:-4]+'List'] = {(preGid,postGid): connParam[paramStrFunc](**{k:v if isinstance(v, Number) else v(preCellTags,postCellTags) for k,v in connParam[paramStrFunc+'Vars'].items()})  
                for preGid,preCellTags in preCellsTags.items() for postGid,postCellTags in postCellsTags.items()}

    if 'weight' in connParam and isinstance(connParam['weight'], list): 
        connParam['weightFromList'] = list(connParam['weight'])  # if weight is a list, copy to weightFromList
    if 'delay' in connParam and isinstance(connParam['delay'], list): 
        connParam['delayFromList'] = list(connParam['delay'])  # if delay is a list, copy to delayFromList
    if 'loc' in connParam and isinstance(connParam['loc'], list): 
        connParam['locFromList'] = list(connParam['loc'])  # if delay is a list, copy to locFromList
    
    orderedPreGids = sorted(preCellsTags.keys())
    orderedPostGids = sorted(postCellsTags.keys())

    for iconn, (relativePreId, relativePostId) in enumerate(connParam['connList']):  # for each postsyn cell
        preCellGid = orderedPreGids[relativePreId]     
        postCellGid = orderedPostGids[relativePostId]
        if postCellGid in self.lid2gid:  # check if postsyn is in this node's list of gids
            
            if 'weightFromList' in connParam: connParam['weight'] = connParam['weightFromList'][iconn] 
            if 'delayFromList' in connParam: connParam['delay'] = connParam['delayFromList'][iconn]
            if 'locFromList' in connParam: connParam['loc'] = connParam['locFromList'][iconn]
    
            if preCellGid != postCellGid: # if not self-connection
                self._addCellConn(connParam, preCellGid, postCellGid) # add connection


# -----------------------------------------------------------------------------
# Set parameters and create connection
# -----------------------------------------------------------------------------
def _addCellConn (self, connParam, preCellGid, postCellGid):
    from .. import sim

    # set final param values
    paramStrFunc = self.connStringFuncParams
    finalParam = {}

    # initialize randomizer for string-based funcs that use rand (except for conv conn which already init)
    # PERFORMANCE:
    # args = [x for param in paramStrFunc if param+'FuncArgs' in connParam for x in connParam[param+'FuncArgs'] ]
    # if 'rand' in args and connParam['connFunc'] not in ['convConn']:
    #     self.rand.Random123(preCellGid, postCellGid, sim.cfg.seeds['conn']) 

    randSeeded = False
    for param in paramStrFunc:
        if param+'List' in connParam:
            finalParam[param] = connParam[param+'List'][preCellGid,postCellGid]
        elif param+'Func' in connParam:
            if not randSeeded and connParam['connFunc'] not in ['convConn'] and 'rand' in connParam[param+'FuncArgs']:
                self.rand.Random123(preCellGid, postCellGid, sim.cfg.seeds['conn'])
                randSeeded = True
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
                elif 'synMech'+param.title()+'Factor' in connParam: # adapt weight for each synMech
                    finalParam[param+'SynMech'] = finalParam[param] * connParam['synMech'+param.title()+'Factor'][i]

        params = {'preGid': preCellGid, 
        'sec': connParam.get('sec'), 
        'loc': finalParam['locSynMech'], 
        'synMech': synMech, 
        'weight': finalParam['weightSynMech'],
        'delay': finalParam['delaySynMech'],
        'synsPerConn': finalParam['synsPerConn']}

        # if 'threshold' in connParam: params['threshold'] = connParam.get('threshold')  # deprecated, use threshold in preSyn cell sec
        if 'shape' in connParam: params['shape'] = connParam.get('shape')    
        if 'plast' in connParam: params['plast'] = connParam.get('plast')    
        if 'gapJunction' in connParam: params['gapJunction'] = connParam.get('gapJunction')

        if sim.cfg.includeParamsLabel: params['label'] = connParam.get('label')
        
        postCell.addConn(params=params)



