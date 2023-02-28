"""
Module for creating network connections

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from builtins import dict
from builtins import range

from builtins import round

try:
    basestring
except NameError:
    basestring = str
from future import standard_library

standard_library.install_aliases()
import numpy as np
from array import array as arrayFast
from numbers import Number


# -----------------------------------------------------------------------------
# Connect Cells
# -----------------------------------------------------------------------------
def connectCells(self):
    """
    Function for/to <short description of `netpyne.network.conn.connectCells`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*


    """

    from .. import sim

    # Instantiate network connections based on the connectivity rules defined in params
    sim.timing('start', 'connectTime')
    if sim.rank == 0:
        print('Making connections...')

    if sim.nhosts > 1:  # Gather tags from all cells
        allCellTags = sim._gatherAllCellTags()
    else:
        allCellTags = {cell.gid: cell.tags for cell in self.cells}
    allPopTags = {
        -i: pop.tags for i, pop in enumerate(self.pops.values())
    }  # gather tags from pops so can connect NetStim pops

    if self.params.subConnParams:  # do not create NEURON objs until synapses are distributed based on subConnParams
        origCreateNEURONObj = bool(sim.cfg.createNEURONObj)
        origAddSynMechs = bool(sim.cfg.addSynMechs)
        sim.cfg.createNEURONObj = False
        sim.cfg.addSynMechs = False

    hasPointerConns = self.params.synMechParams.hasPointerConns()

    for connParamLabel, connParamTemp in self.params.connParams.items():  # for each conn rule or parameter set
        connParam = connParamTemp.copy()
        connParam['label'] = connParamLabel

        # find pre and post cells that match conditions
        preCellsTags, postCellsTags = self._findPrePostCellsCondition(
            allCellTags, connParam['preConds'], connParam['postConds']
        )

        # if conn function not specified, select based on params
        if 'connFunc' not in connParam:
            if 'probability' in connParam:
                connParam['connFunc'] = 'probConn'  # probability based func
            elif 'convergence' in connParam:
                connParam['connFunc'] = 'convConn'  # convergence function
            elif 'divergence' in connParam:
                connParam['connFunc'] = 'divConn'  # divergence function
            elif 'connList' in connParam:
                connParam['connFunc'] = 'fromListConn'  # from list function
            else:
                connParam['connFunc'] = 'fullConn'  # convergence function
        connFunc = getattr(self, connParam['connFunc'])  # get function name from params

        # process string-based funcs and call conn function
        if preCellsTags and postCellsTags:
            # initialize randomizer in case used in string-based function (see issue #89 for more details)
            self.rand.Random123(
                sim.hashStr('conn_' + connParam['connFunc']),
                sim.hashList(sorted(preCellsTags) + sorted(postCellsTags)),
                sim.cfg.seeds['conn'],
            )
            self._connStrToFunc(
                preCellsTags, postCellsTags, connParam
            )  # convert strings to functions (for the delay, and probability params)
            connFunc(preCellsTags, postCellsTags, connParam)  # call specific conn function

        # check if gap junctions in any of the conn rules (deprecated)
        if 'gapJunction' in connParam:
            hasPointerConns = True

        if sim.cfg.printSynsAfterRule:
            nodeSynapses = sum([len(cell.conns) for cell in sim.net.cells])
            print(
                (
                    '  Number of synaptic contacts on node %i after conn rule %s: %i '
                    % (sim.rank, connParamLabel, nodeSynapses)
                )
            )

    # add pointer conns targeting presynaptic cells
    if hasPointerConns:
        # distribute info across nodes
        if not getattr(sim.net, 'preCellPointerConns', False):
            sim.net.preCellPointerConns = []
        data = [sim.net.preCellPointerConns] * sim.nhosts  # send cells data to other nodes
        data[sim.rank] = None
        gather = sim.pc.py_alltoall(data)  # collect cells data from other nodes (required to generate connections)
        sim.pc.barrier()
        for dataNode in gather:
            if dataNode:
                sim.net.preCellPointerConns.extend(dataNode)

        # add connections (need to do separately because could be in different ranks)
        for preGapParams in getattr(sim.net, 'preCellPointerConns', []):
            if preGapParams['gid'] in self.gid2lid:  # only cells in this rank
                cell = self.cells[self.gid2lid[preGapParams['gid']]]
                cell.addConn(preGapParams)

    # apply subcellular connectivity params (distribution of synaspes)
    if self.params.subConnParams:
        self.subcellularConn(allCellTags, allPopTags)
        sim.cfg.createNEURONObj = origCreateNEURONObj  # set to original value
        sim.cfg.addSynMechs = origAddSynMechs  # set to original value
        cellsUpdate = [c for c in sim.net.cells if c.tags.get('cellModel', None) not in ['NetStim', 'VecStim']]
        if sim.cfg.createNEURONObj:
            for cell in cellsUpdate:
                # Add synMechs, stim and conn NEURON objects
                cell.addStimsNEURONObj()
                # cell.addSynMechsNEURONObj()
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
    if sim.rank == 0 and sim.cfg.timing:
        print(('  Done; cell connection time = %0.2f s.' % sim.timingData['connectTime']))

    return [cell.conns for cell in self.cells]


# -----------------------------------------------------------------------------
# Find pre and post cells matching conditions
# -----------------------------------------------------------------------------
def _findPrePostCellsCondition(self, allCellTags, preConds, postConds):

    # try:
    preCellsTags = dict(allCellTags)  # initialize with all presyn cells (make copy)
    postCellsTags = None

    for condKey, condValue in preConds.items():  # Find subset of cells that match presyn criteria
        if condKey in ['x', 'y', 'z', 'xnorm', 'ynorm', 'znorm']:
            preCellsTags = {
                gid: tags
                for (gid, tags) in preCellsTags.items()
                if condValue[0] <= tags.get(condKey, None) < condValue[1]
            }  # dict with pre cell tags
        else:
            if isinstance(condValue, list):
                preCellsTags = {
                    gid: tags for (gid, tags) in preCellsTags.items() if tags.get(condKey, None) in condValue
                }  # dict with pre cell tags
            else:
                preCellsTags = {
                    gid: tags for (gid, tags) in preCellsTags.items() if tags.get(condKey, None) == condValue
                }  # dict with pre cell tags

    if preCellsTags:  # only check post if there are pre
        postCellsTags = allCellTags
        for condKey, condValue in postConds.items():  # Find subset of cells that match postsyn criteria
            if condKey in ['x', 'y', 'z', 'xnorm', 'ynorm', 'znorm']:
                postCellsTags = {
                    gid: tags
                    for (gid, tags) in postCellsTags.items()
                    if condValue[0] <= tags.get(condKey, None) < condValue[1]
                }  # dict with post Cell objects}  # dict with pre cell tags
            elif isinstance(condValue, list):
                postCellsTags = {
                    gid: tags for (gid, tags) in postCellsTags.items() if tags.get(condKey, None) in condValue
                }  # dict with post Cell objects
            else:
                postCellsTags = {
                    gid: tags for (gid, tags) in postCellsTags.items() if tags.get(condKey, None) == condValue
                }  # dict with post Cell objects
    # except:
    #   return None, None

    return preCellsTags, postCellsTags


# -----------------------------------------------------------------------------
# Convert connection param string to function
# -----------------------------------------------------------------------------
def _connStrToFunc(self, preCellsTags, postCellsTags, connParam):
    # list of params that have a function passed in as a string
    paramsStrFunc = [
        param
        for param in self.connStringFuncParams + ['probability', 'convergence', 'divergence']
        if param in connParam and isinstance(connParam[param], basestring)
    ]

    # dict to store correspondence between string and actual variable
    dictVars = {}
    dictVars['pre_x'] = lambda preConds, postConds: preConds['x']
    dictVars['pre_y'] = lambda preConds, postConds: preConds['y']
    dictVars['pre_z'] = lambda preConds, postConds: preConds['z']
    dictVars['pre_xnorm'] = lambda preConds, postConds: preConds['xnorm']
    dictVars['pre_ynorm'] = lambda preConds, postConds: preConds['ynorm']
    dictVars['pre_znorm'] = lambda preConds, postConds: preConds['znorm']
    dictVars['post_x'] = lambda preConds, postConds: postConds['x']
    dictVars['post_y'] = lambda preConds, postConds: postConds['y']
    dictVars['post_z'] = lambda preConds, postConds: postConds['z']
    dictVars['post_xnorm'] = lambda preConds, postConds: postConds['xnorm']
    dictVars['post_ynorm'] = lambda preConds, postConds: postConds['ynorm']
    dictVars['post_znorm'] = lambda preConds, postConds: postConds['znorm']
    dictVars['dist_x'] = lambda preConds, postConds: abs(preConds['x'] - postConds['x'])
    dictVars['dist_y'] = lambda preConds, postConds: abs(preConds['y'] - postConds['y'])
    dictVars['dist_z'] = lambda preConds, postConds: abs(preConds['z'] - postConds['z'])
    dictVars['dist_3D'] = lambda preConds, postConds: np.sqrt(
        (preConds['x'] - postConds['x']) ** 2
        + (preConds['y'] - postConds['y']) ** 2
        + (preConds['z'] - postConds['z']) ** 2
    )
    dictVars['dist_3D_border'] = lambda preConds, postConds: np.sqrt(
        (abs(preConds['x'] - postConds['x']) - postConds['borderCorrect'][0]) ** 2
        + (abs(preConds['y'] - postConds['y']) - postConds['borderCorrect'][1]) ** 2
        + (abs(preConds['z'] - postConds['z']) - postConds['borderCorrect'][2]) ** 2
    )
    dictVars['dist_2D'] = lambda preConds, postConds: np.sqrt(
        (preConds['x'] - postConds['x']) ** 2 + (preConds['z'] - postConds['z']) ** 2
    )
    dictVars['dist_xnorm'] = lambda preConds, postConds: abs(preConds['xnorm'] - postConds['xnorm'])
    dictVars['dist_ynorm'] = lambda preConds, postConds: abs(preConds['ynorm'] - postConds['ynorm'])
    dictVars['dist_znorm'] = lambda preConds, postConds: abs(preConds['znorm'] - postConds['znorm'])
    dictVars['dist_norm3D'] = lambda preConds, postConds: np.sqrt(
        (preConds['xnorm'] - postConds['xnorm']) ** 2
        + np.sqrt(preConds['ynorm'] - postConds['ynorm'])
        + np.sqrt(preConds['znorm'] - postConds['znorm'])
    )
    dictVars['dist_norm2D'] = lambda preConds, postConds: np.sqrt(
        (preConds['xnorm'] - postConds['xnorm']) ** 2 + np.sqrt(preConds['znorm'] - postConds['znorm'])
    )
    dictVars['rand'] = lambda unused1, unused2: self.rand

    # add netParams variables
    for k, v in self.params.__dict__.items():
        if isinstance(v, Number):
            dictVars[k] = v

    # for each parameter containing a function, calculate lambda function and arguments
    from netpyne.specs.utils import generateStringFunction

    for paramStrFunc in paramsStrFunc:
        strFunc = connParam[paramStrFunc]  # string containing function
        lambdaFunc, strVars = generateStringFunction(strFunc, list(dictVars.keys()))

        if paramStrFunc in ['probability']:
            # replace function with dict of values derived from function (one per pre+post cell)
            connParam[paramStrFunc + 'Func'] = {
                (preGid, postGid): lambdaFunc(
                    **{
                        strVar: dictVars[strVar]
                        if isinstance(dictVars[strVar], Number)
                        else dictVars[strVar](preCellTags, postCellTags)
                        for strVar in strVars
                    }
                )
                for preGid, preCellTags in preCellsTags.items()
                for postGid, postCellTags in postCellsTags.items()
            }

        elif paramStrFunc in ['convergence']:
            # replace function with dict of values derived from function (one per post cell)
            connParam[paramStrFunc + 'Func'] = {
                postGid: lambdaFunc(
                    **{
                        strVar: dictVars[strVar]
                        if isinstance(dictVars[strVar], Number)
                        else dictVars[strVar](None, postCellTags)
                        for strVar in strVars
                    }
                )
                for postGid, postCellTags in postCellsTags.items()
            }

        elif paramStrFunc in ['divergence']:
            # replace function with dict of values derived from function (one per post cell)
            connParam[paramStrFunc + 'Func'] = {
                preGid: lambdaFunc(
                    **{
                        strVar: dictVars[strVar]
                        if isinstance(dictVars[strVar], Number)
                        else dictVars[strVar](preCellTags, None)
                        for strVar in strVars
                    }
                )
                for preGid, preCellTags in preCellsTags.items()
            }

        else:
            # store lambda function and func vars in connParam (for weight, delay and synsPerConn since only calculated for certain conns)
            connParam[paramStrFunc + 'Func'] = lambdaFunc
            connParam[paramStrFunc + 'FuncVars'] = {strVar: dictVars[strVar] for strVar in strVars}


# -----------------------------------------------------------------------------
# Disynaptic bias for probability
# -----------------------------------------------------------------------------
def _disynapticBiasProb(self, origProbability, bias, prePreGids, postPreGids, disynCounter, maxImbalance=10):
    probability = float(origProbability)
    factor = bias / origProbability
    # bias = min(bias, origProbability)  # don't modify more than orig, so can compensate
    if not set(prePreGids).isdisjoint(postPreGids) and disynCounter < maxImbalance:
        probability = min(origProbability + bias, 1.0)
        disynCounter += factor  # 1
    elif disynCounter > -maxImbalance:
        probability = max(origProbability - (min(origProbability + bias, 1.0) - origProbability), 0.0)
        disynCounter -= 1
    # print disynCounter, origProbability, probability
    return probability, disynCounter


# -----------------------------------------------------------------------------
# Disynaptic bias for probability (version 2)
# bis = min fraction of conns that will be disynaptic
# -----------------------------------------------------------------------------
def _disynapticBiasProb2(self, probMatrix, allRands, bias, prePreGids, postPreGids):
    connGids = []
    # calculate which conns are disyn vs
    disynMatrix = {
        (preGid, postGid): not set(prePreGids[preGid]).isdisjoint(postPreGids[postGid])
        for preGid, postGid in list(probMatrix.keys())
    }

    # calculate which conns are going to be created
    connCreate = {
        (preGid, postGid): probMatrix[(preGid, postGid)] >= allRands[(preGid, postGid)]
        for preGid, postGid in list(probMatrix.keys())
    }
    numConns = len([c for c in list(connCreate.values()) if c])

    # change % bias of conns from non-disyn to disyn (start with low, high probs respectively)
    disynConn, nonDisynConn, disynNotConn = [], [], []
    for (pre, post), disyn in disynMatrix.items():
        if disyn and connCreate[(pre, post)]:
            disynConn.append((pre, post))
        elif not disyn and connCreate[(pre, post)]:
            nonDisynConn.append((pre, post))
        elif disyn and not connCreate[(pre, post)]:
            disynNotConn.append((pre, post))
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

    connGids = [(pre, post) for (pre, post), c in connCreate.items() if c]
    return connGids


# -----------------------------------------------------------------------------
# Full connectivity
# -----------------------------------------------------------------------------
def fullConn(self, preCellsTags, postCellsTags, connParam):
    """
    Function for/to <short description of `netpyne.network.conn.fullConn`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*

    preCellsTags : <type>
        <Short description of preCellsTags>
        **Default:** *required*

    postCellsTags : <type>
        <Short description of postCellsTags>
        **Default:** *required*

    connParam : <type>
        <Short description of connParam>
        **Default:** *required*
    """

    from .. import sim

    if sim.cfg.verbose:
        print('Generating set of all-to-all connections (rule: %s) ...' % (connParam['label']))

    # get list of params that have a lambda function
    paramsStrFunc = [param for param in [p + 'Func' for p in self.connStringFuncParams] if param in connParam]

    for paramStrFunc in paramsStrFunc:
        # replace lambda function (with args as dict of lambda funcs) with list of values
        connParam[paramStrFunc[:-4] + 'List'] = {
            (preGid, postGid): connParam[paramStrFunc](
                **{
                    k: v if isinstance(v, Number) else v(preCellTags, postCellTags)
                    for k, v in connParam[paramStrFunc + 'Vars'].items()
                }
            )
            for preGid, preCellTags in preCellsTags.items()
            for postGid, postCellTags in postCellsTags.items()
        }

    for postCellGid in postCellsTags:  # for each postsyn cell
        if postCellGid in self.gid2lid:  # check if postsyn is in this node's list of gids
            for preCellGid, preCellTags in preCellsTags.items():  # for each presyn cell
                self._addCellConn(connParam, preCellGid, postCellGid, preCellsTags)  # add connection


# -----------------------------------------------------------------------------
# Generate random values for all pre and post cells (to use in prob conn)
# -----------------------------------------------------------------------------
def generateRandsPrePost(self, pre, post):
    """
    Function for/to <short description of `netpyne.network.conn.generateRandsPrePost`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*

    pre : <type>
        <Short description of pre>
        **Default:** *required*

    post : <type>
        <Short description of post>
        **Default:** *required*


    """

    from .. import sim

    sortedPre = sorted(pre)
    sortedPost = sorted(post)
    # initialize randomizer using unique hash of pre and post gids and global conn seed
    self.rand.Random123(sim.hashList(sortedPre), sim.hashList(sortedPost), sim.cfg.seeds['conn'])  #

    # obtain rand value for pre,post pairs
    lenPre = len(pre)
    lenPost = len(post)
    vec = sim.h.Vector(lenPre * lenPost)  # create Vector
    self.rand.uniform(0, 1)  # set unfiform distribution
    vecList = list(vec.setrand(self.rand))  # fill in vector
    allRands = {
        (preGid, postGid): vecList[(ipre * lenPost) + ipost]
        for ipre, preGid in enumerate(sortedPre)
        for ipost, postGid in enumerate(sortedPost)
    }  # convert to dict

    return allRands


# -----------------------------------------------------------------------------
# Probabilistic connectivity
# -----------------------------------------------------------------------------
def probConn(self, preCellsTags, postCellsTags, connParam):
    """
    Function for/to <short description of `netpyne.network.conn.probConn`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*

    preCellsTags : <type>
        <Short description of preCellsTags>
        **Default:** *required*

    postCellsTags : <type>
        <Short description of postCellsTags>
        **Default:** *required*

    connParam : <type>
        <Short description of connParam>
        **Default:** *required*
    """

    from .. import sim

    if sim.cfg.verbose:
        print('Generating set of probabilistic connections (rule: %s) ...' % (connParam['label']))

    allRands = self.generateRandsPrePost(preCellsTags, postCellsTags)

    # get list of params that have a lambda function
    paramsStrFunc = [param for param in [p + 'Func' for p in self.connStringFuncParams] if param in connParam]

    # copy the vars into args immediately and work out which keys are associated with lambda functions only once per method
    funcKeys = {}
    for paramStrFunc in paramsStrFunc:
        connParam[paramStrFunc + 'Args'] = connParam[paramStrFunc + 'Vars'].copy()
        funcKeys[paramStrFunc] = [
            key for key in connParam[paramStrFunc + 'Vars'] if callable(connParam[paramStrFunc + 'Vars'][key])
        ]

    # probabilistic connections with disynapticBias (deprecated)
    if isinstance(connParam.get('disynapticBias', None), Number):
        allPreGids = sim._gatherAllCellConnPreGids()
        prePreGids = {gid: allPreGids[gid] for gid in preCellsTags}
        postPreGids = {gid: allPreGids[gid] for gid in postCellsTags}

        probMatrix = {
            (preCellGid, postCellGid): connParam['probabilityFunc'][preCellGid, postCellGid]
            if 'probabilityFunc' in connParam
            else connParam['probability']
            for postCellGid, postCellTags in postCellsTags.items()  # for each postsyn cell
            for preCellGid, preCellTags in preCellsTags.items()  # for each presyn cell
            if postCellGid in self.gid2lid
        }  # check if postsyn is in this node

        connGids = self._disynapticBiasProb2(
            probMatrix, allRands, connParam['disynapticBias'], prePreGids, postPreGids
        )
        for preCellGid, postCellGid in connGids:
            for paramStrFunc in paramsStrFunc:  # call lambda functions to get weight func args
                connParam[paramStrFunc + 'Args'] = {
                    k: v if isinstance(v, Number) else v(preCellsTags[preCellGid], postCellsTags[postCellGid])
                    for k, v in connParam[paramStrFunc + 'Vars'].items()
                }
            self._addCellConn(connParam, preCellGid, postCellGid, preCellsTags)  # add connection

    # standard probabilistic conenctions
    else:
        # print('rank %d'%(sim.rank))
        # print(connParam)
        # calculate the conn preGids of the each pre and post cell
        # for postCellGid,postCellTags in sorted(postCellsTags.items()):  # for each postsyn cell
        for postCellGid, postCellTags in postCellsTags.items():  # for each postsyn cell  # for each postsyn cell
            if postCellGid in self.gid2lid:  # check if postsyn is in this node
                for preCellGid, preCellTags in preCellsTags.items():  # for each presyn cell
                    probability = (
                        connParam['probabilityFunc'][preCellGid, postCellGid]
                        if 'probabilityFunc' in connParam
                        else connParam['probability']
                    )
                    if probability >= allRands[preCellGid, postCellGid]:
                        for paramStrFunc in paramsStrFunc:  # call lambda functions to get weight func args
                            # update the relevant FuncArgs dict where lambda functions are known to exist in the corresponding FuncVars dict
                            for funcKey in funcKeys[paramStrFunc]:
                                connParam[paramStrFunc + 'Args'][funcKey] = connParam[paramStrFunc + 'Vars'][funcKey](
                                    preCellTags, postCellTags
                                )
                            # connParam[paramStrFunc+'Args'] = {k:v if isinstance(v, Number) else v(preCellTags,postCellTags) for k,v in connParam[paramStrFunc+'Vars'].items()}
                        self._addCellConn(connParam, preCellGid, postCellGid, preCellsTags)  # add connection


# -----------------------------------------------------------------------------
# Generate random unique integers
# -----------------------------------------------------------------------------
def randUniqueInt(self, r, N, vmin, vmax):
    """
    Function for/to <short description of `netpyne.network.conn.randUniqueInt`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*

    r : <type>
        <Short description of r>
        **Default:** *required*

    N : <type>
        <Short description of N>
        **Default:** *required*

    vmin : <type>
        <Short description of vmin>
        **Default:** *required*

    vmax : <type>
        <Short description of vmax>
        **Default:** *required*


    """

    r.discunif(vmin, vmax)
    out = []
    while len(out) < N:
        x = int(r.repick())
        if x not in out:
            out.append(x)
    return out


# -----------------------------------------------------------------------------
# Convergent connectivity
# -----------------------------------------------------------------------------
def convConn(self, preCellsTags, postCellsTags, connParam):
    """
    Function for/to <short description of `netpyne.network.conn.convConn`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*

    preCellsTags : <type>
        <Short description of preCellsTags>
        **Default:** *required*

    postCellsTags : <type>
        <Short description of postCellsTags>
        **Default:** *required*

    connParam : <type>
        <Short description of connParam>
        **Default:** *required*
    """

    from .. import sim

    if sim.cfg.verbose:
        print('Generating set of convergent connections (rule: %s) ...' % (connParam['label']))

    # get list of params that have a lambda function
    paramsStrFunc = [param for param in [p + 'Func' for p in self.connStringFuncParams] if param in connParam]

    # copy the vars into args immediately and work out which keys are associated with lambda functions only once per method
    funcKeys = {}
    for paramStrFunc in paramsStrFunc:
        connParam[paramStrFunc + 'Args'] = connParam[paramStrFunc + 'Vars'].copy()
        funcKeys[paramStrFunc] = [
            key for key in connParam[paramStrFunc + 'Vars'] if callable(connParam[paramStrFunc + 'Vars'][key])
        ]

    # converted to list only once
    preCellsTagsKeys = sorted(preCellsTags)

    # calculate hash for post cell gids
    hashPreCells = sim.hashList(preCellsTagsKeys)

    for postCellGid, postCellTags in postCellsTags.items():  # for each postsyn cell
        if postCellGid in self.gid2lid:  # check if postsyn is in this node
            convergence = (
                connParam['convergenceFunc'][postCellGid]
                if 'convergenceFunc' in connParam
                else connParam['convergence']
            )  # num of presyn conns / postsyn cell
            convergence = max(min(int(round(convergence)), len(preCellsTags) - 1), 0)
            self.rand.Random123(hashPreCells, postCellGid, sim.cfg.seeds['conn'])  # init randomizer
            randSample = self.randUniqueInt(self.rand, convergence + 1, 0, len(preCellsTags) - 1)

            # note: randSample[divergence] is an extra value used only if one of the random postGids coincided with the preGid
            preCellsSample = {
                preCellsTagsKeys[randSample[convergence]]
                if preCellsTagsKeys[i] == postCellGid
                else preCellsTagsKeys[i]: 0
                for i in randSample[0:convergence]
            }  # dict of selected gids of postsyn cells with removed post gid
            preCellsConv = {
                k: v for k, v in preCellsTags.items() if k in preCellsSample
            }  # dict of selected presyn cells tags

            for preCellGid, preCellTags in preCellsConv.items():  # for each presyn cell

                for paramStrFunc in paramsStrFunc:  # call lambda functions to get weight func args
                    # update the relevant FuncArgs dict where lambda functions are known to exist in the corresponding FuncVars dict
                    for funcKey in funcKeys[paramStrFunc]:
                        connParam[paramStrFunc + 'Args'][funcKey] = connParam[paramStrFunc + 'Vars'][funcKey](
                            preCellTags, postCellTags
                        )

                if preCellGid != postCellGid:  # if not self-connection
                    self._addCellConn(connParam, preCellGid, postCellGid, preCellsTags)  # add connection


# -----------------------------------------------------------------------------
# Divergent connectivity
# -----------------------------------------------------------------------------
def divConn(self, preCellsTags, postCellsTags, connParam):
    """
    Function for/to <short description of `netpyne.network.conn.divConn`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*

    preCellsTags : <type>
        <Short description of preCellsTags>
        **Default:** *required*

    postCellsTags : <type>
        <Short description of postCellsTags>
        **Default:** *required*

    connParam : <type>
        <Short description of connParam>
        **Default:** *required*
    """

    from .. import sim

    if sim.cfg.verbose:
        print('Generating set of divergent connections (rule: %s) ...' % (connParam['label']))

    # get list of params that have a lambda function
    paramsStrFunc = [param for param in [p + 'Func' for p in self.connStringFuncParams] if param in connParam]

    # copy the vars into args immediately and work out which keys are associated with lambda functions only once per method
    funcKeys = {}
    for paramStrFunc in paramsStrFunc:
        connParam[paramStrFunc + 'Args'] = connParam[paramStrFunc + 'Vars'].copy()
        funcKeys[paramStrFunc] = [
            key for key in connParam[paramStrFunc + 'Vars'] if callable(connParam[paramStrFunc + 'Vars'][key])
        ]

    # converted to list only once
    postCellsTagsKeys = sorted(postCellsTags)

    # calculate hash for post cell gids
    hashPostCells = sim.hashList(postCellsTagsKeys)

    for preCellGid, preCellTags in preCellsTags.items():  # for each presyn cell
        divergence = (
            connParam['divergenceFunc'][preCellGid] if 'divergenceFunc' in connParam else connParam['divergence']
        )  # num of presyn conns / postsyn cell
        divergence = max(min(int(round(divergence)), len(postCellsTags) - 1), 0)
        self.rand.Random123(hashPostCells, preCellGid, sim.cfg.seeds['conn'])  # init randomizer
        randSample = self.randUniqueInt(self.rand, divergence + 1, 0, len(postCellsTags) - 1)

        # note: randSample[divergence] is an extra value used only if one of the random postGids coincided with the preGid
        postCellsSample = {
            postCellsTagsKeys[randSample[divergence]]
            if postCellsTagsKeys[i] == preCellGid
            else postCellsTagsKeys[i]: 0
            for i in randSample[0:divergence]
        }  # dict of selected gids of postsyn cells with removed pre gid

        for postCellGid in [c for c in postCellsSample if c in self.gid2lid]:
            postCellTags = postCellsTags[postCellGid]
            for paramStrFunc in paramsStrFunc:  # call lambda functions to get weight func args
                # update the relevant FuncArgs dict where lambda functions are known to exist in the corresponding FuncVars dict
                for funcKey in funcKeys[paramStrFunc]:
                    connParam[paramStrFunc + 'Args'][funcKey] = connParam[paramStrFunc + 'Vars'][funcKey](
                        preCellTags, postCellTags
                    )

            if preCellGid != postCellGid:  # if not self-connection
                self._addCellConn(connParam, preCellGid, postCellGid, preCellsTags)  # add connection


# -----------------------------------------------------------------------------
# From list connectivity
# -----------------------------------------------------------------------------
def fromListConn(self, preCellsTags, postCellsTags, connParam):
    """
    Function for/to <short description of `netpyne.network.conn.fromListConn`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*

    preCellsTags : <type>
        <Short description of preCellsTags>
        **Default:** *required*

    postCellsTags : <type>
        <Short description of postCellsTags>
        **Default:** *required*

    connParam : <type>
        <Short description of connParam>
        **Default:** *required*
    """

    from .. import sim

    if sim.cfg.verbose:
        print('Generating set of connections from list (rule: %s) ...' % (connParam['label']))

    orderedPreGids = sorted(preCellsTags)
    orderedPostGids = sorted(postCellsTags)

    # list of params that can have a lambda function
    paramsStrFunc = [param for param in [p + 'Func' for p in self.connStringFuncParams] if param in connParam]
    for paramStrFunc in paramsStrFunc:
        # replace lambda function (with args as dict of lambda funcs) with list of values
        connParam[paramStrFunc[:-4] + 'List'] = {
            (orderedPreGids[preId], orderedPostGids[postId]): connParam[paramStrFunc](
                **{
                    k: v
                    if isinstance(v, Number)
                    else v(preCellsTags[orderedPreGids[preId]], postCellsTags[orderedPostGids[postId]])
                    for k, v in connParam[paramStrFunc + 'Vars'].items()
                }
            )
            for preId, postId in connParam['connList']
        }

    if 'weight' in connParam and isinstance(connParam['weight'], list):
        connParam['weightFromList'] = list(connParam['weight'])  # if weight is a list, copy to weightFromList
    if 'delay' in connParam and isinstance(connParam['delay'], list):
        connParam['delayFromList'] = list(connParam['delay'])  # if delay is a list, copy to delayFromList
    if 'loc' in connParam and isinstance(connParam['loc'], list):
        connParam['locFromList'] = list(connParam['loc'])  # if delay is a list, copy to locFromList

    for iconn, (relativePreId, relativePostId) in enumerate(connParam['connList']):  # for each postsyn cell
        preCellGid = orderedPreGids[relativePreId]
        postCellGid = orderedPostGids[relativePostId]
        if postCellGid in self.gid2lid:  # check if postsyn is in this node's list of gids

            if 'weightFromList' in connParam:
                connParam['weight'] = connParam['weightFromList'][iconn]
            if 'delayFromList' in connParam:
                connParam['delay'] = connParam['delayFromList'][iconn]
            if 'locFromList' in connParam:
                connParam['loc'] = connParam['locFromList'][iconn]

            if preCellGid != postCellGid:  # if not self-connection
                self._addCellConn(connParam, preCellGid, postCellGid, preCellsTags)  # add connection


# -----------------------------------------------------------------------------
# Set parameters and create connection
# -----------------------------------------------------------------------------
def _addCellConn(self, connParam, preCellGid, postCellGid, preCellsTags={}):
    from .. import sim
    from ..specs.netParams import SynMechParams

    # set final param values
    paramStrFunc = self.connStringFuncParams
    finalParam = {}

    # Set final parameter values; initialize randomizer for string-based funcs that use rand to ensue replicability
    # Note: could potentially speed up by generating list of values for all rand funcs used (e.g. rand.uniform())
    # and then selecting a value from list based of pre- and post- gid -- that way only seed once at beginning in connectCells()
    # Howeve, not clear if faster in all cases since need to generate values for len(pre)*len(post), whereas here only a subset
    randSeeded = False

    for param in paramStrFunc:
        if param + 'List' in connParam:
            finalParam[param] = connParam[param + 'List'][preCellGid, postCellGid]
        elif param + 'Func' in connParam:
            if not randSeeded and 'rand' in connParam[param + 'FuncArgs']:
                self.rand.Random123(preCellGid, postCellGid, sim.cfg.seeds['conn'])
                randSeeded = True
            finalParam[param] = connParam[param + 'Func'](**connParam[param + 'FuncArgs'])
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
            finalParam[param + 'SynMech'] = finalParam.get(param)
            if len(connParam['synMech']) > 1:
                if isinstance(finalParam.get(param), list):  # get weight from list for each synMech
                    finalParam[param + 'SynMech'] = finalParam[param][i]
                elif 'synMech' + param.title() + 'Factor' in connParam:  # adapt weight for each synMech
                    finalParam[param + 'SynMech'] = (
                        finalParam[param] * connParam['synMech' + param.title() + 'Factor'][i]
                    )

        params = {
            'preGid': preCellGid,
            'sec': connParam.get('sec'),
            'loc': finalParam['locSynMech'],
            'synMech': synMech,
            'weight': finalParam['weightSynMech'],
            'delay': finalParam['delaySynMech'],
            'synsPerConn': finalParam['synsPerConn'],
        }

        # if 'threshold' in connParam: params['threshold'] = connParam.get('threshold')  # deprecated, use threshold in preSyn cell sec
        if 'shape' in connParam:
            params['shape'] = connParam.get('shape')
        if 'plast' in connParam:
            params['plast'] = connParam.get('plast')
        if 'weightIndex' in connParam:
            params['weightIndex'] = connParam.get('weightIndex')

        isGapJunction = 'gapJunction' in connParam  # deprecated way of defining gap junction
        if self.params.synMechParams.isPointerConn(params['synMech']) or isGapJunction:
            params['preLoc'] = connParam.get('preLoc')
            params['preSec'] = connParam.get('preSec', 'soma')
            if isGapJunction:
                params['gapJunction'] = connParam['gapJunction']
        # TODO: synMech can be None here (meaning 'use default'). Then need to use default label while checking below
        elif SynMechParams.stringFuncsReferPreLoc(synMech):
            # save synapse pre-cell location to be used in stringFunc for synMech.
            # for optimization purpose, do it only if preLoc is referenced for a given synMech
            cellType = preCellsTags[preCellGid].get('cellType')
            if cellType:
                from ..cell import CompartCell

                secs = self.params.cellParams[cellType].secs
                loc, _ = CompartCell.spikeGenLocAndSec(secs)
                params['preLoc'] = loc

        if sim.cfg.includeParamsLabel:
            params['label'] = connParam.get('label')

        postCell.addConn(params=params)
