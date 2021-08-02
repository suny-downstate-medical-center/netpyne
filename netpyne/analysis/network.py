"""
Module for analyzing and plotting connectivity-related results

"""

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
from .utils import colorList, exception, _roundFigures, getCellsInclude, getCellsIncludeTags
from .utils import _saveFigData, _showFigure
from netpyne.logger import logger

# -------------------------------------------------------------------------------------------------------------------
## Support function for plotConn() - calculate conn using data from sim object
# -------------------------------------------------------------------------------------------------------------------

def _plotConnCalculateFromSim(includePre, includePost, feature, orderBy, groupBy, groupByIntervalPre, groupByIntervalPost, synOrConn, synMech, removeWeightNorm, logPlot=False):

    from .. import sim

    def list_of_dict_unique_by_key(seq, key):
        seen = set()
        seen_add = seen.add

        try:
            return [x for x in seq if x[key] not in seen and not seen_add(x[key])]
        except:
            logger.warning('  Error calculating list of dict unique by key...')
            return []

    # adapt indices/keys based on compact vs long conn format
    if sim.cfg.compactConnFormat:
        connsFormat = sim.cfg.compactConnFormat

        # set indices of fields to read compact format (no keys)
        missing = []
        preGidIndex = connsFormat.index('preGid') if 'preGid' in connsFormat else missing.append('preGid')
        synMechIndex = connsFormat.index('synMech') if 'synMech' in connsFormat else missing.append('synMech')
        weightIndex = connsFormat.index('weight') if 'weight' in connsFormat else missing.append('weight')
        delayIndex = connsFormat.index('delay') if 'delay' in connsFormat else missing.append('delay')
        preLabelIndex = connsFormat.index('preLabel') if 'preLabel' in connsFormat else -1

        if len(missing) > 0:
            logger.warning("  Error: cfg.compactConnFormat missing:")
            logger.warning(missing)
            return None, None, None
    else:
        # using long conn format (dict)
        preGidIndex = 'preGid'
        synMechIndex = 'synMech'
        weightIndex = 'weight'
        delayIndex = 'delay'
        preLabelIndex = 'preLabel'

    # Calculate pre and post cells involved
    cellsPre, cellGidsPre, netStimPopsPre = getCellsInclude(includePre)
    if includePre == includePost:
        cellsPost, cellGidsPost, netStimPopsPost = cellsPre, cellGidsPre, netStimPopsPre
    else:
        cellsPost, cellGidsPost, netStimPopsPost = getCellsInclude(includePost)

    if isinstance(synMech, basestring): synMech = [synMech]  # make sure synMech is a list

    # Calculate matrix if grouped by cell
    if groupBy == 'cell':
        if feature in ['weight', 'delay', 'numConns']:
            connMatrix = np.zeros((len(cellGidsPre), len(cellGidsPost)))
            countMatrix = np.zeros((len(cellGidsPre), len(cellGidsPost)))
        else:
            logger.warning('  Conn matrix with groupBy="cell" only supports features= "weight", "delay" or "numConns"')
            return None, None, None
        cellIndsPre = {cell['gid']: ind for ind,cell in enumerate(cellsPre)}
        cellIndsPost = {cell['gid']: ind for ind,cell in enumerate(cellsPost)}

        # Order by
        if len(cellsPre) > 0 and len(cellsPost) > 0:
            if orderBy not in cellsPre[0]['tags'] or orderBy not in cellsPost[0]['tags']:  # if orderBy property doesn't exist or is not numeric, use gid
                orderBy = 'gid'
            elif not isinstance(cellsPre[0]['tags'][orderBy], Number) or not isinstance(cellsPost[0]['tags'][orderBy], Number):
                orderBy = 'gid'

            if orderBy == 'gid':
                yorderPre = [cell[orderBy] for cell in cellsPre]
                yorderPost = [cell[orderBy] for cell in cellsPost]
            else:
                yorderPre = [cell['tags'][orderBy] for cell in cellsPre]
                yorderPost = [cell['tags'][orderBy] for cell in cellsPost]

            sortedGidsPre = {gid:i for i,(y,gid) in enumerate(sorted(zip(yorderPre,cellGidsPre)))}
            cellIndsPre = sortedGidsPre
            if includePre == includePost:
                sortedGidsPost = sortedGidsPre
                cellIndsPost = cellIndsPre
            else:
                sortedGidsPost = {gid:i for i,(y,gid) in enumerate(sorted(zip(yorderPost,cellGidsPost)))}
                cellIndsPost = sortedGidsPost


        # Calculate conn matrix
        for cell in cellsPost:  # for each postsyn cell

            if synOrConn=='syn':
                cellConns = cell['conns'] # include all synapses
            else:
                cellConns = list_of_dict_unique_by_key(cell['conns'], preGidIndex)

            if synMech:
                cellConns = [conn for conn in cellConns if conn[synMechIndex] in synMech]

            for conn in cellConns:
                if conn[preGidIndex] != 'NetStim' and conn[preGidIndex] in cellIndsPre:
                    if feature in ['weight', 'delay']:
                        featureIndex = weightIndex if feature == 'weight' else delayIndex
                        if conn[preGidIndex] in cellIndsPre:
                            if removeWeightNorm and feature=='weight':
                                try:
                                    sec = conn['sec']
                                    loc = conn['loc']
                                    nseg = cell['secs'][sec]['geom']['nseg']
                                    segIndex = int(round(loc*nseg))-1
                                    weightNorm = cell['secs'][sec]['weightNorm'][segIndex]
                                    connMatrix[cellIndsPre[conn[preGidIndex]], cellIndsPost[cell['gid']]] += conn[featureIndex] / weightNorm
                                except:
                                    pass
                            else:
                                connMatrix[cellIndsPre[conn[preGidIndex]], cellIndsPost[cell['gid']]] += conn[featureIndex]


                    countMatrix[cellIndsPre[conn[preGidIndex]], cellIndsPost[cell['gid']]] += 1

        if feature in ['weight', 'delay']:
            if logPlot:
                connMatrix = np.log10(connMatrix / countMatrix)
            else:
                connMatrix = connMatrix / countMatrix
        elif feature in ['numConns']: connMatrix = countMatrix

        pre, post = cellsPre, cellsPost

    # Calculate matrix if grouped by pop
    elif groupBy == 'pop':

        # get list of pops
        popsTempPre = list(set([cell['tags']['pop'] for cell in cellsPre]))
        popsPre = [pop for pop in sim.net.allPops if pop in popsTempPre]+netStimPopsPre
        popIndsPre = {pop: ind for ind,pop in enumerate(popsPre)}

        if includePre == includePost:
            popsPost = popsPre
            popIndsPost = popIndsPre
        else:
            popsTempPost = list(set([cell['tags']['pop'] for cell in cellsPost]))
            popsPost = [pop for pop in sim.net.allPops if pop in popsTempPost]+netStimPopsPost
            popIndsPost = {pop: ind for ind,pop in enumerate(popsPost)}

        # initialize matrices
        if feature in ['weight', 'strength']:
            weightMatrix = np.zeros((len(popsPre), len(popsPost)))
        elif feature == 'delay':
            delayMatrix = np.zeros((len(popsPre), len(popsPost)))
        countMatrix = np.zeros((len(popsPre), len(popsPost)))

        # calculate max num conns per pre and post pair of pops
        numCellsPopPre = {}
        for pop in popsPre:
            if pop in netStimPopsPre:
                numCellsPopPre[pop] = -1
            else:
                numCellsPopPre[pop] = len([cell for cell in cellsPre if cell['tags']['pop']==pop])

        if includePre == includePost:
            numCellsPopPost = numCellsPopPre
        else:
            numCellsPopPost = {}
            for pop in popsPost:
                if pop in netStimPopsPost:
                    numCellsPopPost[pop] = -1
                else:
                    numCellsPopPost[pop] = len([cell for cell in cellsPost if cell['tags']['pop']==pop])

        maxConnMatrix = np.zeros((len(popsPre), len(popsPost)))
        if feature == 'convergence': maxPostConnMatrix = np.zeros((len(popsPre), len(popsPost)))
        if feature == 'divergence': maxPreConnMatrix = np.zeros((len(popsPre), len(popsPost)))
        for prePop in popsPre:
            for postPop in popsPost:
                if numCellsPopPre[prePop] == -1: numCellsPopPre[prePop] = numCellsPopPost[postPop]
                maxConnMatrix[popIndsPre[prePop], popIndsPost[postPop]] = numCellsPopPre[prePop]*numCellsPopPost[postPop]
                if feature == 'convergence': maxPostConnMatrix[popIndsPre[prePop], popIndsPost[postPop]] = numCellsPopPost[postPop]
                if feature == 'divergence': maxPreConnMatrix[popIndsPre[prePop], popIndsPost[postPop]] = numCellsPopPre[prePop]

        # Calculate conn matrix
        for cell in cellsPost:  # for each postsyn cell

            if synOrConn=='syn':
                cellConns = cell['conns'] # include all synapses
            else:
                cellConns = list_of_dict_unique_by_key(cell['conns'], preGidIndex)

            if synMech:
                cellConns = [conn for conn in cellConns if conn[synMechIndex] in synMech]

            for conn in cellConns:
                if conn[preGidIndex] == 'NetStim':
                    prePopLabel = conn[preLabelIndex] if preLabelIndex in conn else 'NetStim'
                else:
                    preCell = next((cell for cell in cellsPre if cell['gid']==conn[preGidIndex]), None)
                    prePopLabel = preCell['tags']['pop'] if preCell else None

                if prePopLabel in popIndsPre:
                    if feature in ['weight', 'strength']:
                        if removeWeightNorm:
                            try:
                                sec = conn['sec']
                                loc = conn['loc']
                                nseg = cell['secs'][sec]['geom']['nseg']
                                segIndex = int(round(loc*nseg))-1
                                weightNorm = cell['secs'][sec]['weightNorm'][segIndex]
                                weightMatrix[popIndsPre[prePopLabel], popIndsPost[cell['tags']['pop']]] += conn[weightIndex] / weightNorm
                            except:
                                import IPython; IPython.embed()
                        else:
                            weightMatrix[popIndsPre[prePopLabel], popIndsPost[cell['tags']['pop']]] += conn[weightIndex]

                    elif feature == 'delay':
                        delayMatrix[popIndsPre[prePopLabel], popIndsPost[cell['tags']['pop']]] += conn[delayIndex]
                    countMatrix[popIndsPre[prePopLabel], popIndsPost[cell['tags']['pop']]] += 1

        pre, post = popsPre, popsPost

    # Calculate matrix if grouped by numeric tag (eg. 'y')
    elif groupBy in sim.net.allCells[0]['tags'] and isinstance(sim.net.allCells[0]['tags'][groupBy], Number):
        if not isinstance(groupByIntervalPre, Number) or not isinstance(groupByIntervalPost, Number):
            logger.warning('  groupByIntervalPre or groupByIntervalPost not specified')
            return None, None, None

        # group cells by 'groupBy' feature (eg. 'y') in intervals of 'groupByInterval')
        cellValuesPre = [cell['tags'][groupBy] for cell in cellsPre]
        minValuePre = _roundFigures(groupByIntervalPre * np.floor(min(cellValuesPre) / groupByIntervalPre), 3)
        maxValuePre  = _roundFigures(groupByIntervalPre * np.ceil(max(cellValuesPre) / groupByIntervalPre), 3)
        groupsPre = np.arange(minValuePre, maxValuePre, groupByIntervalPre)
        groupsPre = [_roundFigures(x,3) for x in groupsPre]

        if includePre == includePost:
            groupsPost = groupsPre
        else:
            cellValuesPost = [cell['tags'][groupBy] for cell in cellsPost]
            minValuePost = _roundFigures(groupByIntervalPost * np.floor(min(cellValuesPost) / groupByIntervalPost), 3)
            maxValuePost  = _roundFigures(groupByIntervalPost * np.ceil(max(cellValuesPost) / groupByIntervalPost), 3)
            groupsPost = np.arange(minValuePost, maxValuePost, groupByIntervalPost)
            groupsPost = [_roundFigures(x,3) for x in groupsPost]


        # only allow matrix sizes >= 2x2 [why?]
        # if len(groupsPre) < 2 or len(groupsPost) < 2:
        #     logger.info 'groupBy %s with groupByIntervalPre %s and groupByIntervalPost %s results in <2 groups'%(str(groupBy), str(groupByIntervalPre), str(groupByIntervalPre))
        #     return

        # set indices for pre and post groups
        groupIndsPre = {group: ind for ind,group in enumerate(groupsPre)}
        groupIndsPost = {group: ind for ind,group in enumerate(groupsPost)}

        # initialize matrices
        if feature in ['weight', 'strength']:
            weightMatrix = np.zeros((len(groupsPre), len(groupsPost)))
        elif feature == 'delay':
            delayMatrix = np.zeros((len(groupsPre), len(groupsPost)))
        countMatrix = np.zeros((len(groupsPre), len(groupsPost)))

        # calculate max num conns per pre and post pair of pops
        numCellsGroupPre = {}
        for groupPre in groupsPre:
            numCellsGroupPre[groupPre] = len([cell for cell in cellsPre if groupPre <= cell['tags'][groupBy] < (groupPre+groupByIntervalPre)])

        if includePre == includePost:
            numCellsGroupPost = numCellsGroupPre
        else:
            numCellsGroupPost = {}
            for groupPost in groupsPost:
                numCellsGroupPost[groupPost] = len([cell for cell in cellsPost if groupPost <= cell['tags'][groupBy] < (groupPost+groupByIntervalPost)])


        maxConnMatrix = np.zeros((len(groupsPre), len(groupsPost)))
        if feature == 'convergence': maxPostConnMatrix = np.zeros((len(groupsPre), len(groupsPost)))
        if feature == 'divergence': maxPreConnMatrix = np.zeros((len(groupsPre), len(groupsPost)))
        for preGroup in groupsPre:
            for postGroup in groupsPost:
                if numCellsGroupPre[preGroup] == -1: numCellsGroupPre[preGroup] = numCellsGroupPost[postGroup]
                maxConnMatrix[groupIndsPre[preGroup], groupIndsPost[postGroup]] = numCellsGroupPre[preGroup]*numCellsGroupPost[postGroup]
                if feature == 'convergence': maxPostConnMatrix[groupIndsPre[preGroup], groupIndsPost[postGroup]] = numCellsGroupPost[postGroup]
                if feature == 'divergence': maxPreConnMatrix[groupIndsPre[preGroup], groupIndsPost[postGroup]] = numCellsGroupPre[preGroup]

        # Calculate conn matrix
        for cell in cellsPost:  # for each postsyn cell
            if synOrConn=='syn':
                cellConns = cell['conns'] # include all synapses
            else:
                cellConns = list_of_dict_unique_by_key(cell['conns'], preGidIndex)

            if synMech:
                cellConns = [conn for conn in cellConns if conn[synMechIndex] in synMech]

            for conn in cellConns:
                if conn[preGidIndex] == 'NetStim':
                    prePopLabel = -1  # maybe add in future
                else:
                    preCell = next((c for c in cellsPre if c['gid']==conn[preGidIndex]), None)
                    if preCell:
                        preGroup = _roundFigures(groupByIntervalPre * np.floor(preCell['tags'][groupBy] / groupByIntervalPre), 3)
                    else:
                        preGroup = None

                postGroup = _roundFigures(groupByIntervalPost * np.floor(cell['tags'][groupBy] / groupByIntervalPost), 3)
                if preGroup in groupIndsPre:
                    if feature in ['weight', 'strength']:
                        weightMatrix[groupIndsPre[preGroup], groupIndsPost[postGroup]] += conn[weightIndex]

                    elif feature == 'delay':
                        delayMatrix[groupIndsPre[preGroup], groupIndsPost[postGroup]] += conn[delayIndex]
                    countMatrix[groupIndsPre[preGroup], groupIndsPost[postGroup]] += 1


        pre, post = groupsPre, groupsPost

    # no valid groupBy
    else:
        logger.warning('  groupBy (%s) is not valid'%(str(groupBy)))
        return None, None, None

    # normalize by number of postsyn cells
    if groupBy != 'cell':
        if feature == 'weight':
            if logPlot:
                connMatrix = np.log10(weightMatrix / countMatrix)  # avg log weight per conn
            else:
                connMatrix = weightMatrix / countMatrix  # avg weight per conn
                connMatrix = np.nan_to_num(connMatrix, nan=0)  # if the count is 0 we get NaNs, but the weight is 0
        elif feature == 'delay':
            connMatrix = delayMatrix / countMatrix
            connMatrix = np.nan_to_num(connMatrix, nan=0)  # if the count is 0 we get NaNs, but the delay is 0
        elif feature == 'numConns':
            connMatrix = countMatrix
        elif feature in ['probability', 'strength']:
            connMatrix = countMatrix / maxConnMatrix  # probability
            if feature == 'strength':
                if logPlot:
                    connMatrix = np.log10(connMatrix * weightMatrix)  # log strength
                else:
                    connMatrix = connMatrix * weightMatrix  # strength
        elif feature == 'convergence':
            connMatrix = countMatrix / maxPostConnMatrix
        elif feature == 'divergence':
            connMatrix = countMatrix / maxPreConnMatrix



    return connMatrix, pre, post


# -------------------------------------------------------------------------------------------------------------------
## Support function for plotConn() - calculate conn using data from files with short format (no keys)
# -------------------------------------------------------------------------------------------------------------------

def _plotConnCalculateFromFile(includePre, includePost, feature, orderBy, groupBy, groupByIntervalPre, groupByIntervalPost, synOrConn, synMech, connsFile, tagsFile,removeWeightNorm, logPlot=False):

    from .. import sim
    import json
    from time import time

    def list_of_dict_unique_by_key(seq, index):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if x[index] not in seen and not seen_add(x[index])]

    # load files with tags and conns
    start = time()
    tags, conns = None, None
    if tagsFile:
        logger.info('Loading tags file...')
        with open(tagsFile, 'r') as fileObj: tagsTmp = json.load(fileObj)['tags']
        tagsFormat = tagsTmp.pop('format', [])
        tags = {int(k): v for k,v in tagsTmp.items()} # find method to load json with int keys?
        del tagsTmp
    if connsFile:
        logger.info('Loading conns file...')
        with open(connsFile, 'r') as fileObj: connsTmp = json.load(fileObj)['conns']
        connsFormat = connsTmp.pop('format', [])
        conns = {int(k): v for k,v in connsTmp.items()}
        del connsTmp

    logger.info('Finished loading; total time (s): %.2f'%(time()-start))

    # find pre and post cells
    if tags and conns:
        cellGidsPre = getCellsIncludeTags(includePre, tags, tagsFormat)
        if includePre == includePost:
            cellGidsPost = cellGidsPre
        else:
            cellGidsPost = getCellsIncludeTags(includePost, tags, tagsFormat)
    else:
        logger.warning('Error loading tags and conns from file')
        return None, None, None


    # set indices of fields to read compact format (no keys)
    missing = []
    popIndex = tagsFormat.index('pop') if 'pop' in tagsFormat else missing.append('pop')
    preGidIndex = connsFormat.index('preGid') if 'preGid' in connsFormat else missing.append('preGid')
    synMechIndex = connsFormat.index('synMech') if 'synMech' in connsFormat else missing.append('synMech')
    weightIndex = connsFormat.index('weight') if 'weight' in connsFormat else missing.append('weight')
    delayIndex = connsFormat.index('delay') if 'delay' in connsFormat else missing.append('delay')
    preLabelIndex = connsFormat.index('preLabel') if 'preLabel' in connsFormat else -1

    if len(missing) > 0:
        logger.warning("Missing:")
        logger.warning(missing)
        return None, None, None

    if isinstance(synMech, basestring): synMech = [synMech]  # make sure synMech is a list

    # Calculate matrix if grouped by cell
    if groupBy == 'cell':
        logger.warning('  plotConn from file for groupBy=cell not implemented yet')
        return None, None, None

    # Calculate matrix if grouped by pop
    elif groupBy == 'pop':

        # get list of pops
        logger.info('    Obtaining list of populations ...')
        popsPre = list(set([tags[gid][popIndex] for gid in cellGidsPre]))
        popIndsPre = {pop: ind for ind,pop in enumerate(popsPre)}
        netStimPopsPre = []  # netstims not yet supported
        netStimPopsPost = []

        if includePre == includePost:
            popsPost = popsPre
            popIndsPost = popIndsPre
        else:
            popsPost = list(set([tags[gid][popIndex] for gid in cellGidsPost]))
            popIndsPost = {pop: ind for ind,pop in enumerate(popsPost)}

        # initialize matrices
        if feature in ['weight', 'strength']:
            weightMatrix = np.zeros((len(popsPre), len(popsPost)))
        elif feature == 'delay':
            delayMatrix = np.zeros((len(popsPre), len(popsPost)))
        countMatrix = np.zeros((len(popsPre), len(popsPost)))

        # calculate max num conns per pre and post pair of pops
        logger.info('    Calculating max num conns for each pair of population ...')
        numCellsPopPre = {}
        for pop in popsPre:
            if pop in netStimPopsPre:
                numCellsPopPre[pop] = -1
            else:
                numCellsPopPre[pop] = len([gid for gid in cellGidsPre if tags[gid][popIndex]==pop])

        if includePre == includePost:
            numCellsPopPost = numCellsPopPre
        else:
            numCellsPopPost = {}
            for pop in popsPost:
                if pop in netStimPopsPost:
                    numCellsPopPost[pop] = -1
                else:
                    numCellsPopPost[pop] = len([gid for gid in cellGidsPost if tags[gid][popIndex]==pop])

        maxConnMatrix = np.zeros((len(popsPre), len(popsPost)))
        if feature == 'convergence': maxPostConnMatrix = np.zeros((len(popsPre), len(popsPost)))
        if feature == 'divergence': maxPreConnMatrix = np.zeros((len(popsPre), len(popsPost)))
        for prePop in popsPre:
            for postPop in popsPost:
                if numCellsPopPre[prePop] == -1: numCellsPopPre[prePop] = numCellsPopPost[postPop]
                maxConnMatrix[popIndsPre[prePop], popIndsPost[postPop]] = numCellsPopPre[prePop]*numCellsPopPost[postPop]
                if feature == 'convergence': maxPostConnMatrix[popIndsPre[prePop], popIndsPost[postPop]] = numCellsPopPost[postPop]
                if feature == 'divergence': maxPreConnMatrix[popIndsPre[prePop], popIndsPost[postPop]] = numCellsPopPre[prePop]

        # Calculate conn matrix
        logger.info('    Calculating weights, strength, prob, delay etc matrices ...')
        for postGid in cellGidsPost:  # for each postsyn cell
            logger.info('     cell %d'%(int(postGid)))
            if synOrConn=='syn':
                cellConns = conns[postGid] # include all synapses
            else:
                cellConns = list_of_dict_unique_by_index(conns[postGid], preGidIndex)

            if synMech:
                cellConns = [conn for conn in cellConns if conn[synMechIndex] in synMech]

            for conn in cellConns:
                if conn[preGidIndex] == 'NetStim':
                    prePopLabel = conn[preLabelIndex] if preLabelIndex >=0 else 'NetStims'
                else:
                    preCellGid = next((gid for gid in cellGidsPre if gid==conn[preGidIndex]), None)
                    prePopLabel = tags[preCellGid][popIndex] if preCellGid else None

                if prePopLabel in popIndsPre:
                    if feature in ['weight', 'strength']:
                        weightMatrix[popIndsPre[prePopLabel], popIndsPost[tags[postGid][popIndex]]] += conn[weightIndex]
                    elif feature == 'delay':
                        delayMatrix[popIndsPre[prePopLabel], popIndsPost[tags[postGid][popIndex]]] += conn[delayIndex]
                    countMatrix[popIndsPre[prePopLabel], popIndsPost[tags[postGid][popIndex]]] += 1

        pre, post = popsPre, popsPost

    # Calculate matrix if grouped by numeric tag (eg. 'y')
    elif groupBy in sim.net.allCells[0]['tags'] and isinstance(sim.net.allCells[0]['tags'][groupBy], Number):
        logger.warning('plotConn from file for groupBy=[arbitrary property] not implemented yet')
        return None, None, None

    # no valid groupBy
    else:
        logger.warning('groupBy (%s) is not valid'%(str(groupBy)))
        return None, None, None

    if groupBy != 'cell':
        if feature == 'weight':
            if logPlot:
                connMatrix = np.log10(weightMatrix / countMatrix)  # avg log weight per conn
            else:
                connMatrix = weightMatrix / countMatrix  # avg weight per conn (fix to remove divide by zero warning)
                connMatrix = np.nan_to_num(connMatrix, nan=0)  # if the count is 0 we get NaNs, but the weight is 0
        elif feature == 'delay':
            connMatrix = delayMatrix / countMatrix
            connMatrix = np.nan_to_num(connMatrix, nan=0)  # if the count is 0 we get NaNs, but the delay is 0
        elif feature == 'numConns':
            connMatrix = countMatrix
        elif feature in ['probability', 'strength']:
            connMatrix = countMatrix / maxConnMatrix  # probability
            if feature == 'strength':
                if logPlot:
                    connMatrix = np.log10(connMatrix * weightMatrix) # log strength
                else:
                    connMatrix = connMatrix * weightMatrix  # strength
        elif feature == 'convergence':
            connMatrix = countMatrix / maxPostConnMatrix
        elif feature == 'divergence':
            connMatrix = countMatrix / maxPreConnMatrix

    logger.info('    plotting ...')
    return connMatrix, pre, post


# -------------------------------------------------------------------------------------------------------------------
## Plot connectivity
# -------------------------------------------------------------------------------------------------------------------
@exception
def plotConn(includePre=['all'], includePost=['all'], feature='strength', orderBy='gid', groupBy='pop', groupByIntervalPre=None, groupByIntervalPost=None, graphType='matrix', removeWeightNorm=False, synOrConn='syn', synMech=None, connsFile=None, tagsFile=None, clim=None, figSize=(8,8), fontSize=12, saveData=None, saveFig=None, showFig=True, logPlot=False):
    """
    Function for/to <short description of `netpyne.analysis.network.plotConn`>

    Parameters
    ----------
    includePre : list
        List of presynaptic cells to include.
        **Default:** ``['all']``
        **Options:**
        ``['all']`` plots all cells and stimulations,
        ``['allNetStims']`` plots just stimulations,
        ``['popName1']`` plots a single population,
        ``['popName1', 'popName2']`` plots multiple populations,
        ``[120]`` plots a single cell,
        ``[120, 130]`` plots multiple cells,
        ``[('popName1', 56)]`` plots a cell from a specific population,
        ``[('popName1', [0, 1]), ('popName2', [4, 5, 6])]``, plots cells from multiple populations

    includePost : list
        List of postsynaptic cells to include.
        **Default:** ``['all']``
        **Options:** same as in `includePre`

    feature : str
        Feature to show in the connectivity plot.  The only features applicable to ``groupBy='cell'`` are ``'weight'``, ``'delay'`` and ``'numConns'``.
        **Default:** ``'strength'``
        **Options:**
        ``'weight'`` weight of connection,
        ``'delay'`` delay in connection,
        ``'numConns'`` number of connections,
        ``'probability'`` probabiluty of connection,
        ``'strength'`` weight * probability,
        ``'convergence'`` number of presynaptic cells per postynaptic one,
        ``'divergence'`` number of postsynaptic cells per presynaptic one

    orderBy : str
        Unique numeric cell property by which to order x and y axes.
        **Default:** ``'gid'``
        **Options:** ``'gid'``, ``'y'``, ``'ynorm'``

    groupBy : str
        Plot connectivity for populations, individual cells, or by other numeric tags such as ``'y'``.
        **Default:** ``'pop'``
        **Options:** ``'pop'``, ``'cell'``, ``'y'``

    groupByIntervalPre : int or float
        Interval of `groupBy` feature to group presynaptic cells by in connectivity plot, e.g. ``100`` to group by cortical depth in steps of 100 um.
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    groupByIntervalPost : int or float
        Interval of `groupBy` feature to group postsynaptic cells by in connectivity plot, e.g. ``100`` to group by cortical depth in steps of 100 um.
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    graphType : str
        Type of graph to represent data.
        **Default:** ``'matrix'``
        **Options:** ``'matrix'``, ``'bar'``, ``'pie'``

    removeWeightNorm : bool
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    synOrConn : str
        Use synapses or connections; note one connection can have multiple synapses.
        **Default:** ``'syn'``
        **Options:** ``'syn'``, ``'conn'``

    synMech : list
        Show results only for these synaptic mechanisms, e.g. ``['AMPA', 'GABAA', ...]``.
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    connsFile : str
        Path to a saved data file of connectivity to plot from.
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    tagsFile : str
        Path to a saved tags file to use in connectivity plot.
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    clim : list [min, max]
        List of numeric values for the limits of the colorbar.
        **Default:** ``None`` uses the min and max of the connectivity matrix
        **Options:** ``<option>`` <description of option>

    figSize : list [width, height]
        Size of figure in inches.
        **Default:** ``(8, 8)``
        **Options:** ``<option>`` <description of option>

    fontSize : int
        Font size on figure.
        **Default:** ``12``
        **Options:** ``<option>`` <description of option>

    saveData : bool or str
        Whether and where to save the data used to generate the plot.
        **Default:** ``False``
        **Options:** ``True`` autosaves the data,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.pkl'`` and ``'.json'``

    saveFig : bool or str
        Whether and where to save the figure.
        **Default:** ``False``
        **Options:** ``True`` autosaves the figure,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.png'``, ``'.jpg'``, ``'.eps'``, and ``'.tiff'``

    showFig : bool
        Shows the figure if ``True``.
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    Returns
    -------


"""

    from .. import sim

    logger.info('Plotting connectivity matrix...')

    if groupBy == 'cell' and feature == 'strength':
        feature = 'weight'

    if connsFile and tagsFile:
        connMatrix, pre, post = _plotConnCalculateFromFile(includePre, includePost, feature, orderBy, groupBy, groupByIntervalPre, groupByIntervalPost, synOrConn, synMech, connsFile, tagsFile, removeWeightNorm, logPlot)
    else:
        connMatrix, pre, post = _plotConnCalculateFromSim(includePre, includePost, feature, orderBy, groupBy, groupByIntervalPre, groupByIntervalPost, synOrConn, synMech, removeWeightNorm, logPlot)

    if connMatrix is None:
        logger.warning("  Error calculating connMatrix in plotConn()")
        return None

    # set font size
    plt.rcParams.update({'font.size': fontSize})

    # matrix plot
    if graphType == 'matrix':
        # Create plot
        fig = plt.figure(figsize=figSize)
        fig.subplots_adjust(right=0.98) # Less space on right
        fig.subplots_adjust(top=0.96) # Less space on top
        fig.subplots_adjust(bottom=0.02) # Less space on bottom
        h = plt.axes()
        plt.imshow(connMatrix, interpolation='nearest', cmap='viridis', vmin=np.nanmin(connMatrix), vmax=np.nanmax(connMatrix))  #_bicolormap(gap=0)

        # Plot grid lines
        if groupBy == 'cell':
            cellsPre, cellsPost = pre, post

            # Make pretty
            stepy = max(1, int(len(cellsPre)/10.0))
            basey = 100 if stepy>100 else 10
            stepy = max(1, int(basey * np.floor(float(stepy)/basey)))
            stepx = max(1, int(len(cellsPost)/10.0))
            basex = 100 if stepx>100 else 10
            stepx = max(1, int(basex * np.floor(float(stepx)/basex)))

            h.set_xticks(np.arange(0,len(cellsPost),stepx))
            h.set_yticks(np.arange(0,len(cellsPre),stepy))
            h.set_xticklabels(np.arange(0,len(cellsPost),stepx))
            h.set_yticklabels(np.arange(0,len(cellsPost),stepy))
            h.xaxis.set_ticks_position('top')
            plt.xticks(rotation=90)
            plt.xlim(-0.5,len(cellsPost)-0.5)
            plt.ylim(len(cellsPre)-0.5,-0.5)

        elif groupBy == 'pop':
            popsPre, popsPost = pre, post

            for ipop, pop in enumerate(popsPre):
                plt.plot(np.array([0,len(popsPost)])-0.5,np.array([ipop,ipop])-0.5,'-',c=(0.7,0.7,0.7))
            for ipop, pop in enumerate(popsPost):
                plt.plot(np.array([ipop,ipop])-0.5,np.array([0,len(popsPre)])-0.5,'-',c=(0.7,0.7,0.7))

            # Make pretty
            h.set_xticks(list(range(len(popsPost))))
            h.set_yticks(list(range(len(popsPre))))
            h.set_xticklabels(popsPost)
            h.set_yticklabels(popsPre)
            h.xaxis.set_ticks_position('top')
            plt.xticks(rotation=90)
            plt.xlim(-0.5,len(popsPost)-0.5)
            plt.ylim(len(popsPre)-0.5,-0.5)

        else:
            groupsPre, groupsPost = pre, post

            for igroup, group in enumerate(groupsPre):
                plt.plot(np.array([0,len(groupsPre)])-0.5,np.array([igroup,igroup])-0.5,'-',c=(0.7,0.7,0.7))
            for igroup, group in enumerate(groupsPost):
                plt.plot(np.array([igroup,igroup])-0.5,np.array([0,len(groupsPost)])-0.5,'-',c=(0.7,0.7,0.7))

            # Make pretty
            h.set_xticks([i-0.5 for i in range(len(groupsPost))])
            h.set_yticks([i-0.5 for i in range(len(groupsPre))])
            h.set_xticklabels([int(x) if x>1 else x for x in groupsPost])
            h.set_yticklabels([int(x) if x>1 else x for x in groupsPre])
            h.xaxis.set_ticks_position('top')
            plt.xticks(rotation=90)
            plt.xlim(-0.5,len(groupsPost)-0.5)
            plt.ylim(len(groupsPre)-0.5,-0.5)

        if not clim: clim = [np.nanmin(connMatrix), np.nanmax(connMatrix)]
        plt.clim(clim[0], clim[1])

        if logPlot:
            plt.colorbar(label=feature + ' (log)', shrink=0.8)
        else:
            plt.colorbar(label=feature, shrink=0.8)


        plt.xlabel('post')
        h.xaxis.set_label_coords(0.5, 1.09)
        plt.ylabel('pre')
        if logPlot:
            plt.title('Connection '+feature+' matrix (log)', y=1.12)
        else:
            plt.title('Connection '+feature+' matrix', y=1.12)

    # stacked bar graph
    elif graphType == 'bar':
        if groupBy == 'pop':
            popsPre, popsPost = pre, post

            from netpyne.support import stackedBarGraph
            SBG = stackedBarGraph.StackedBarGrapher()
            fig = plt.figure(figsize=figSize)
            ax = fig.add_subplot(111)
            SBG.stackedBarPlot(ax, connMatrix.transpose(), colorList, xLabels=popsPost, gap = 0.1, scale=False, xlabel='Post', ylabel = feature)
            plt.title ('Connection '+feature+' stacked bar graph')
            plt.legend(popsPre, title='Pre')
            plt.tight_layout()

        elif groupBy == 'cell':
            logger.warning('  Error: plotConn graphType="bar" with groupBy="cell" not implemented')
            return None

    elif graphType == 'pie':
        logger.warning('  Error: plotConn graphType="pie" not yet implemented')
        return None


    #save figure data
    if saveData:
        figData = {'connMatrix': connMatrix, 'feature': feature, 'groupBy': groupBy,
         'includePre': includePre, 'includePost': includePost, 'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}

        _saveFigData(figData, saveData, 'conn')

    # save figure
    if saveFig:
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_plot_conn_'+groupBy+'_'+feature+'_'+graphType+'.png'
        plt.savefig(filename)

    # show fig
    if showFig: _showFigure()

    return fig, {'connMatrix': connMatrix, 'feature': feature, 'groupBy': groupBy, 'includePre': includePre, 'includePost': includePost}


# -------------------------------------------------------------------------------------------------------------------
## Plot 2D representation of network cell positions and connections
# -------------------------------------------------------------------------------------------------------------------
@exception
def plot2Dnet(include=['allCells'], view='xy', showConns=True, popColors=None, tagsFile=None,
    figSize=(12,12), fontSize=12, saveData=None, saveFig=None, showFig=True, lineWidth=0.1):
    """
    Function for/to <short description of `netpyne.analysis.network.plot2Dnet`>

    Parameters
    ----------
    include : list
        List of presynaptic cells to include.
        **Default:** ``['allCells']``
        **Options:**
        ``['all']`` plots all cells and stimulations,
        ``['allNetStims']`` plots just stimulations,
        ``['popName1']`` plots a single population,
        ``['popName1', 'popName2']`` plots multiple populations,
        ``[120]`` plots a single cell,
        ``[120, 130]`` plots multiple cells,
        ``[('popName1', 56)]`` plots a cell from a specific population,
        ``[('popName1', [0, 1]), ('popName2', [4, 5, 6])]``, plots cells from multiple populations

    view : str
        Perspective of view.
        **Default:** ``'xy'`` front view,
        **Options:** ``'xz'`` top-down view

    showConns : bool
        Whether to show connections or not.
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    popColors : dict
        Dictionary with custom color (value) used for each population (key).
        **Default:** ``None`` uses standard colors
        **Options:** ``<option>`` <description of option>

    tagsFile : str
        Path to a saved tags file to use in connectivity plot.
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    figSize : list [width, height]
        Size of figure in inches.
        **Default:** ``(12, 12)``
        **Options:** ``<option>`` <description of option>

    fontSize : int
        Font size on figure.
        **Default:** ``12``
        **Options:** ``<option>`` <description of option>

    saveData : bool or str
        Whether and where to save the data used to generate the plot.
        **Default:** ``False``
        **Options:** ``True`` autosaves the data,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.pkl'`` and ``'.json'``

    saveFig : bool or str
        Whether and where to save the figure.
        **Default:** ``False``
        **Options:** ``True`` autosaves the figure,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.png'``, ``'.jpg'``, ``'.eps'``, and ``'.tiff'``

    showFig : bool
        Shows the figure if ``True``.
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

     lineWidth: float
        Width of connection lines.
        **Default:** ``0.1``
        **Options:** ``<option>`` <description of option>

    Returns
    -------


"""

    from .. import sim

    logger.info('Plotting 2D representation of network cell locations and connections...')

    fig = plt.figure(figsize=figSize)

    # front view
    if view == 'xy':
        ycoord = 'y'
    elif view == 'xz':
        ycoord = 'z'

    if tagsFile:
        logger.info('Loading tags file...')
        import json
        with open(tagsFile, 'r') as fileObj: tagsTmp = json.load(fileObj)['tags']
        tagsFormat = tagsTmp.pop('format', [])
        tags = {int(k): v for k,v in tagsTmp.items()} # find method to load json with int keys?
        del tagsTmp

        # set indices of fields to read compact format (no keys)
        missing = []
        popIndex = tagsFormat.index('pop') if 'pop' in tagsFormat else missing.append('pop')
        xIndex = tagsFormat.index('x') if 'x' in tagsFormat else missing.append('x')
        yIndex = tagsFormat.index('y') if 'y' in tagsFormat else missing.append('y')
        zIndex = tagsFormat.index('z') if 'z' in tagsFormat else missing.append('z')
        if len(missing) > 0:
            logger.warning("Missing:")
            logger.warning(missing)
            return None, None, None

        # find pre and post cells
        if tags:
            cellGids = getCellsIncludeTags(include, tags, tagsFormat)
            popLabels = list(set([tags[gid][popIndex] for gid in cellGids]))

            # pop and cell colors
            popColorsTmp = {popLabel: colorList[ipop%len(colorList)] for ipop,popLabel in enumerate(popLabels)} # dict with color for each pop
            if popColors: popColorsTmp.update(popColors)
            popColors = popColorsTmp
            cellColors = [popColors[tags[gid][popIndex]] for gid in cellGids]

            # cell locations
            posX = [tags[gid][xIndex] for gid in cellGids]  # get all x positions
            if ycoord == 'y':
                posY = [tags[gid][yIndex] for gid in cellGids]  # get all y positions
            elif ycoord == 'z':
                posY = [tags[gid][zIndex] for gid in cellGids]  # get all y positions
        else:
            logger.warning('Error loading tags from file')
            return None

    else:
        cells, cellGids, _ = getCellsInclude(include)
        selectedPops = [cell['tags']['pop'] for cell in cells]
        popLabels = [pop for pop in sim.net.allPops if pop in selectedPops] # preserves original ordering

        # pop and cell colors
        popColorsTmp = {popLabel: colorList[ipop%len(colorList)] for ipop,popLabel in enumerate(popLabels)} # dict with color for each pop
        if popColors: popColorsTmp.update(popColors)
        popColors = popColorsTmp
        cellColors = [popColors[cell['tags']['pop']] for cell in cells]

        # cell locations
        posX = [cell['tags']['x'] for cell in cells]  # get all x positions
        posY = [cell['tags'][ycoord] for cell in cells]  # get all y positions

    plt.scatter(posX, posY, s=60, color = cellColors) # plot cell soma positions
    posXpre, posYpre = [], []
    posXpost, posYpost = [], []
    if showConns and not tagsFile:
        for postCell in cells:
            for con in postCell['conns']:  # plot connections between cells
                if not isinstance(con['preGid'], basestring) and con['preGid'] in cellGids:
                    posXpre,posYpre = next(((cell['tags']['x'],cell['tags'][ycoord]) for cell in cells if cell['gid']==con['preGid']), None)
                    posXpost,posYpost = postCell['tags']['x'], postCell['tags'][ycoord]
                    color='red'
                    if con['synMech'] in ['inh', 'GABA', 'GABAA', 'GABAB']:
                        color = 'blue'
                    width = lineWidth #50*con['weight']
                    plt.plot([posXpre, posXpost], [posYpre, posYpost], color=color, linewidth=width) # plot line from pre to post

    plt.xlabel('x (um)')
    plt.ylabel(ycoord+' (um)')
    plt.xlim([min(posX)-0.05*max(posX),1.05*max(posX)])
    plt.ylim([min(posY)-0.05*max(posY),1.05*max(posY)])
    fontsiz = fontSize

    for popLabel in popLabels:
        plt.plot(0,0,color=popColors[popLabel],label=popLabel)
    plt.legend(fontsize=fontsiz, bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
    ax = plt.gca()
    ax.invert_yaxis()

    # save figure data
    if saveData:
        figData = {'posX': posX, 'posY': posY, 'posX': cellColors, 'posXpre': posXpre, 'posXpost': posXpost, 'posYpre': posYpre, 'posYpost': posYpost,
         'include': include, 'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig, 'lineWidth': lineWidth}

        _saveFigData(figData, saveData, '2Dnet')

    # save figure
    if saveFig:
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename + '_plot_2Dnet.png'
        plt.savefig(filename)

    # show fig
    if showFig: _showFigure()

    return fig, {'include': include, 'posX': posX, 'posY': posY, 'posXpre': posXpre, 'posXpost': posXpost, 'posYpre': posYpre, 'posYpost': posYpost}



# -------------------------------------------------------------------------------------------------------------------
## Plot 2D representation of network activity 
# -------------------------------------------------------------------------------------------------------------------
@exception
def plot2Dfiring(include=['allCells'], view='xy', popColors=None, timeRange=None, spikeBin=5, 
    figSize=(12,12), fontSize=12, saveData=None, saveFig=None, showFig=True, lineWidth=0.1):
    """
    Function for/to <short description of `netpyne.analysis.network.plot2Dnet`>

    Parameters
    ----------
    include : list
        List of presynaptic cells to include.
        **Default:** ``['allCells']``
        **Options:**
        ``['all']`` plots all cells and stimulations,
        ``['allNetStims']`` plots just stimulations,
        ``['popName1']`` plots a single population,
        ``['popName1', 'popName2']`` plots multiple populations,
        ``[120]`` plots a single cell,
        ``[120, 130]`` plots multiple cells,
        ``[('popName1', 56)]`` plots a cell from a specific population,
        ``[('popName1', [0, 1]), ('popName2', [4, 5, 6])]``, plots cells from multiple populations

    view : str
        Perspective of view.
        **Default:** ``'xy'`` front view,
        **Options:** ``'xz'`` top-down view


    popColors : dict
        Dictionary with custom color (value) used for each population (key).
        **Default:** ``None`` uses standard colors
        **Options:** ``<option>`` <description of option>

    figSize : list [width, height]
        Size of figure in inches.
        **Default:** ``(12, 12)``
        **Options:** ``<option>`` <description of option>

    fontSize : int
        Font size on figure.
        **Default:** ``12``
        **Options:** ``<option>`` <description of option>

    saveData : bool or str
        Whether and where to save the data used to generate the plot.
        **Default:** ``False``
        **Options:** ``True`` autosaves the data,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.pkl'`` and ``'.json'``

    saveFig : bool or str
        Whether and where to save the figure.
        **Default:** ``False``
        **Options:** ``True`` autosaves the figure,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.png'``, ``'.jpg'``, ``'.eps'``, and ``'.tiff'``

    showFig : bool
        Shows the figure if ``True``.
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

     lineWidth: float
        Width of connection lines.
        **Default:** ``0.1``
        **Options:** ``<option>`` <description of option>

    Returns
    -------


"""

    from .. import sim
    from matplotlib import animation

    logger.info('Plotting 2D representation of network cell locations and connections...')

    fig = plt.figure(figsize=figSize)

    # front view
    if view == 'xy':
        ycoord = 'y'
    elif view == 'xz':
        ycoord = 'z'

    # get tags
    cells, cellGids, _ = getCellsInclude(include)
    selectedPops = [cell['tags']['pop'] for cell in cells]
    popLabels = [pop for pop in sim.net.allPops if pop in selectedPops] # preserves original ordering

    # pop and cell colors
    popColorsTmp = {popLabel: colorList[ipop%len(colorList)] for ipop,popLabel in enumerate(popLabels)} # dict with color for each pop
    if popColors: popColorsTmp.update(popColors)
    popColors = popColorsTmp
    cellColors = [popColors[cell['tags']['pop']] for cell in cells]

    # cell locations
    posX = [cell['tags']['x'] for cell in cells]  # get all x positions
    posY = [cell['tags'][ycoord] for cell in cells]  # get all y positions

    sc = plt.scatter(posX, posY, s=60, color=cellColors) # plot cell soma positions
    posXpre, posYpre = [], []
    posXpost, posYpost = [], []

    plt.xlabel('x (um)')
    plt.ylabel(ycoord+' (um)')
    plt.xlim([min(posX)-0.05*max(posX),1.05*max(posX)])
    plt.ylim([min(posY)-0.05*max(posY),1.05*max(posY)])
    fontsiz = fontSize

    for popLabel in popLabels:
        plt.plot(0,0,color=popColors[popLabel],label=popLabel)
    plt.legend(fontsize=fontsiz, bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
    ax = plt.gca()
    ax.invert_yaxis()

    # generate animation with time-resolved spiking activity
    spktsAll = sim.allSimData['spkt']
    spkidsAll = sim.allSimData['spkid']

    if not isinstance(timeRange, list):  # True or None
        timeRange = [0, sim.cfg.duration]

    def animate(i, sc, timeRange, spikeBin, ycoord, spkidsAll, spktsAll, cells, cellGids, popColors):
        timeInterval = [timeRange[0] + i*spikeBin, timeRange[0] + (i+1)*spikeBin]

        out = list(zip(*[(spkid, spkt) for spkid, spkt in zip(spkidsAll, spktsAll) if timeInterval[0] <= spkt <= timeInterval[1]]))
        if len(out) == 2:
            spkids, spkts = out

            spkids = [int(x) for x in list(set(spkids) & set(cellGids))]

            posX = np.array([cells[gid]['tags']['x'] for gid in spkids])  # get all x positions
            posY = np.array([cells[gid]['tags'][ycoord] for gid in spkids])  # get all y positions
            cellColors = [popColors[cells[gid]['tags']['pop']] for gid in spkids]
            
            sc.set_offsets(np.c_[posX,posY])
            sc.set_color(cellColors)
            plt.gca().set_title('t = %d' % int(timeRange[0] + (i+1)*spikeBin))



    frames = int((timeRange[1]-timeRange[0]) / spikeBin)
    ani = animation.FuncAnimation(fig, animate, frames=frames, interval=100, repeat=True, fargs=(sc, timeRange, spikeBin, ycoord, spkidsAll, spktsAll, cells, cellGids, popColors,)) 


    # save figure data
    if saveData:
        figData = {'posX': posX, 'posY': posY, 'posX': cellColors, 'posXpre': posXpre, 'posXpost': posXpost, 'posYpre': posYpre, 'posYpost': posYpost,
         'include': include, 'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig, 'lineWidth': lineWidth}

        _saveFigData(figData, saveData, '2Dnet')

    # save figure
    if saveFig:
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename + '_plot_2Dfiring.gif'
        ani.save(filename)

    # show fig
    if showFig: _showFigure()

    return fig, {'include': include, 'posX': posX, 'posY': posY, 'posXpre': posXpre, 'posXpost': posXpost, 'posYpre': posYpre, 'posYpost': posYpost}



# -------------------------------------------------------------------------------------------------------------------
## Plot cell shape
# -------------------------------------------------------------------------------------------------------------------
@exception
def plotShape(includePre=['all'], includePost=['all'], showSyns=False, showElectrodes=False, synStyle='.', synSize=3, dist=0.6, elev=90, azim=-90, cvar=None, cvals=None, clim=None, iv=False, ivprops=None, includeAxon=True, bkgColor=None, axis='auto', axisLabels=False, figSize=(10,8), fontSize=12, saveData=None, dpi=300, saveFig=None, showFig=True, **kwargs):
    """
    Function for/to <short description of `netpyne.analysis.network.plotShape`>

    Parameters
    ----------
    includePre : list
        List of presynaptic cells to include.
        **Default:** ``['all']``
        **Options:**
        ``['all']`` plots all cells and stimulations,
        ``['allNetStims']`` plots just stimulations,
        ``['popName1']`` plots a single population,
        ``['popName1', 'popName2']`` plots multiple populations,
        ``[120]`` plots a single cell,
        ``[120, 130]`` plots multiple cells,
        ``[('popName1', 56)]`` plots a cell from a specific population,
        ``[('popName1', [0, 1]), ('popName2', [4, 5, 6])]``, plots cells from multiple populations

    includePost : list
        List of postsynaptic cells to include.
        **Default:** ``['all']``
        **Options:** same as in `includePre`

    showSyns : bool
        Show synaptic connections in 3D view.
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    showElectrodes : bool
        Show LFP electrodes in 3D view.
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    synStyle : str
        Style of marker to show synapses.
        **Default:** ``'.'``
        **Options:** ``<option>`` <description of option>

    synSize : int
        Size of marker to show synapses.
        **Default:** ``3``
        **Options:** ``<option>`` <description of option>

    dist : float
        3D distance (like zoom).
        **Default:** ``0.6``
        **Options:** ``<option>`` <description of option>

    cvar : str
        Variable to represent in shape plot.
        **Default:** ``None``
        **Options:** ``'numSyns'`` represents the number of synapses, ``'weightNorm'`` represents the normalized synaptic weight

    cvals : list
        List of values to represent in shape plot; must be same as number of segments.
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    iv : bool
        Use NEURON Interviews (instead of Matplotlib) to show shape plot.
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    ivprops : dict
        Dictionary of properties to plot using Interviews (default: None)
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    includeAxon : bool
        Include axon in shape plot.
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    bkgColor : list or tuple
        RGBA list/tuple with background color.  E.g.: (0.5, 0.2, 0.1, 1.0)
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    figSize : list [width, height]
        Size of figure in inches.
        **Default:** ``(10, 8)``
        **Options:** ``<option>`` <description of option>

    fontSize : int
        Font size on figure.
        **Default:** ``12``
        **Options:** ``<option>`` <description of option>

    saveData : bool or str
        Whether and where to save the data used to generate the plot.
        **Default:** ``False``
        **Options:** ``True`` autosaves the data,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.pkl'`` and ``'.json'``

    dpi : int
        Resolution of figure in dots per inch.
        **Default:** ``300``
        **Options:** ``<option>`` <description of option>

    saveFig : bool or str
        Whether and where to save the figure.
        **Default:** ``False``
        **Options:** ``True`` autosaves the figure,
        ``'/path/filename.ext'`` saves to a custom path and filename, valid file extensions are ``'.png'``, ``'.jpg'``, ``'.eps'``, and ``'.tiff'``

    showFig : bool
        Shows the figure if ``True``.
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    Returns
    -------


"""

    from .. import sim
    from neuron import h

    logger.info('Plotting 3D cell shape ...')

    cellsPreGids = [c.gid for c in sim.getCellsList(includePre)] if includePre else []
    cellsPost = sim.getCellsList(includePost)

    if not hasattr(sim.net, 'compartCells'): sim.net.compartCells = [c for c in cellsPost if type(c) is sim.CompartCell]
    try:
        sim.net.defineCellShapes()  # in case some cells had stylized morphologies without 3d pts
    except:
        pass

    if not iv: # plot using Python instead of interviews
        from mpl_toolkits.mplot3d import Axes3D
        from netpyne.support import morphology as morph # code adapted from https://github.com/ahwillia/PyNeuron-Toolbox

        # create secList from include
        secs = None

        # Set cvals and secs
        if not cvals and cvar:
            cvals = []
            secs = []
            # weighNorm
            if cvar == 'weightNorm':
                for cellPost in cellsPost:
                    cellSecs = list(cellPost.secs.values()) if includeAxon else [s for s in list(cellPost.secs.values()) if 'axon' not in s['hObj'].hname()]
                    for sec in cellSecs:
                        if 'weightNorm' in sec:
                            secs.append(sec['hObj'])
                            cvals.extend(sec['weightNorm'])

                cvals = np.array(cvals)
                cvals = cvals/min(cvals)

            # numSyns
            elif cvar == 'numSyns':
                for cellPost in cellsPost:
                    cellSecs = cellPost.secs if includeAxon else {k:s for k,s in cellPost.secs.items() if 'axon' not in s['hObj'].hname()}
                    for secLabel,sec in cellSecs.items():
                        nseg=sec['hObj'].nseg
                        nsyns = [0] * nseg
                        secs.append(sec['hObj'])
                        conns = [conn for conn in cellPost.conns if conn['sec']==secLabel and conn['preGid'] in cellsPreGids]
                        for conn in conns: nsyns[int(round(conn['loc']*nseg))-1] += 1
                        cvals.extend(nsyns)

                cvals = np.array(cvals)

            # voltage
            elif cvar == 'voltage':
                for cellPost in cellsPost:
                    cellSecs = cellPost.secs if includeAxon else {k:s for k,s in cellPost.secs.items() if 'axon' not in s['hObj'].hname()}
                    for secLabel,sec in cellSecs.items():
                        for seg in sec['hObj']:
                            cvals.append(seg.v)
    
                cvals = np.array(cvals)

        if not isinstance(cellsPost[0].secs, dict):
            logger.warning('Error: Cell sections not available')
            return -1

        if not secs: secs = [s['hObj'] for cellPost in cellsPost for s in list(cellPost.secs.values())]
        if not includeAxon:
            secs = [sec for sec in secs if 'axon' not in sec.hname()]

        # Plot shapeplot
        cbLabels = {'numSyns': 'Number of synapses per segment', 
                    'weightNorm': 'Weight scaling',
                    'voltage': 'Voltage (mV)'}
        plt.rcParams.update({'font.size': fontSize})
        fig=plt.figure(figsize=figSize)
        shapeax = plt.subplot(111, projection='3d')
        shapeax.elev=elev # 90
        shapeax.azim=azim  # -90
        shapeax.dist=dist*shapeax.dist
        plt.axis(axis)
        cmap = plt.cm.viridis #plt.cm.jet  #plt.cm.rainbow #plt.cm.jet #YlOrBr_r
        morph.shapeplot(h, shapeax, sections=secs, cvals=cvals, cmap=cmap, clim=clim)

        # fix so that axes can be scaled
        ax = plt.gca()
        def set_axes_equal(ax):
            """Set 3D plot axes to equal scale.

            Make axes of 3D plot have equal scale so that spheres appear as
            spheres and cubes as cubes.  Required since `ax.axis('equal')`
            and `ax.set_aspect('equal')` don't work on 3D.
            """
            limits = np.array([
                ax.get_xlim3d(),
                ax.get_ylim3d(),
                ax.get_zlim3d(),
            ])
            origin = np.mean(limits, axis=1)
            radius = 0.5 * np.max(np.abs(limits[:, 1] - limits[:, 0]))
            _set_axes_radius(ax, origin, radius)

        def _set_axes_radius(ax, origin, radius):
            x, y, z = origin
            ax.set_xlim3d([x - radius, x + radius])
            ax.set_ylim3d([y - radius, y + radius])
            ax.set_zlim3d([z - radius, z + radius])

        ax.set_box_aspect([1,1,1]) # IMPORTANT - this is the new, key line
        set_axes_equal(ax) 

        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        if cvals is not None and len(cvals)>0:
            vmin = np.min(cvals)
            vmax = np.max(cvals)
            
            if clim is not None:
                vmin = np.min(clim)
                vmax = np.max(clim)

            sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
            sm._A = []  # fake up the array of the scalar mappable
            cb = plt.colorbar(sm, fraction=0.15, shrink=0.5, pad=0.05, aspect=20)
            if cvar: cb.set_label(cbLabels[cvar], rotation=90, fontsize=fontSize)
            cb.ax.set_title('Time = ' + str(round(h.t, 1)), fontsize=fontSize)

        if bkgColor:
            shapeax.w_xaxis.set_pane_color(bkgColor)
            shapeax.w_yaxis.set_pane_color(bkgColor)
            shapeax.w_zaxis.set_pane_color(bkgColor)
        #shapeax.grid(False)

        # Synapses
        if showSyns:
            synColor='red'
            for cellPost in cellsPost:
                for sec in list(cellPost.secs.values()):
                    for synMech in sec['synMechs']:
                        morph.mark_locations(h, sec['hObj'], synMech['loc'], markspec=synStyle, color=synColor, markersize=synSize)

        # Electrodes
        if showElectrodes:
            ax = plt.gca()
            colorOffset = 0
            if 'avg' in showElectrodes:
                showElectrodes.remove('avg')
                colorOffset = 1
            coords = sim.net.recXElectrode.pos.T[np.array(showElectrodes).astype(int),:]
            ax.scatter(coords[:,0],coords[:,1],coords[:,2], s=150, c=colorList[colorOffset:len(coords)+colorOffset],
                marker='v', depthshade=False, edgecolors='k', linewidth=2)
            for i in range(coords.shape[0]):
                ax.text(coords[i,0],coords[i,1],coords[i,2], '  '+str(showElectrodes[i]), fontweight='bold' )
            cb.set_label('Segment total transfer resistance to electrodes (kiloohm)', rotation=90, fontsize=fontSize)

        if axisLabels:
            shapeax.set_xlabel('x (um)')
            shapeax.set_ylabel('y (um)')
            shapeax.set_zlabel('z (um)')
        else:
            shapeax.set_xticklabels([])
            shapeax.set_yticklabels([])
            shapeax.set_zticklabels([])

        # save figure
        if saveFig:
            if isinstance(saveFig, basestring):
                if saveFig == 'movie':
                    filename = sim.cfg.filename + '_shape_movie_' + str(round(h.t, 1)) + '.png'
                else:
                    filename = saveFig
            else:
                filename = sim.cfg.filename+'_shape.png'
            plt.savefig(filename, dpi=dpi)

        # show fig
        if showFig: _showFigure()

    else:  # Plot using Interviews
        # colors: 0 white, 1 black, 2 red, 3 blue, 4 green, 5 orange, 6 brown, 7 violet, 8 yellow, 9 gray
        from neuron import gui
        fig = h.Shape()
        secList = h.SectionList()
        if not ivprops:
            ivprops = {'colorSecs': 1, 'colorSyns':2 ,'style': 'O', 'siz':5}

        for cell in [c for c in cellsPost]:
            for sec in list(cell.secs.values()):
                if 'axon' in sec['hObj'].hname() and not includeAxon: continue
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
        fig.show(0) # show real diam
            # save figure
        if saveFig:
            if isinstance(saveFig, basestring):
                filename = saveFig
            else:
                filename = sim.cfg.filename+'_'+'shape.ps'
            fig.printfile(filename)

    return fig, {}




# -------------------------------------------------------------------------------------------------------------------
## Calculate number of disynaptic connections
# -------------------------------------------------------------------------------------------------------------------
@exception
def calculateDisynaptic(includePost = ['allCells'], includePre = ['allCells'], includePrePre = ['allCells'],
        tags=None, conns=None, tagsFile=None, connsFile=None):
    """
    Function for/to <short description of `netpyne.analysis.network.calculateDisynaptic`>

    Parameters
    ----------
    includePost : list
        <Short description of includePost>
        **Default:** ``['allCells']``
        **Options:** ``<option>`` <description of option>

    includePre : list
        <Short description of includePre>
        **Default:** ``['allCells']``
        **Options:** ``<option>`` <description of option>

    includePrePre : list
        <Short description of includePrePre>
        **Default:** ``['allCells']``
        **Options:** ``<option>`` <description of option>

    tags : <``None``?>
        <Short description of tags>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    conns : <``None``?>
        <Short description of conns>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    tagsFile : <``None``?>
        <Short description of tagsFile>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>

    connsFile : <``None``?>
        <Short description of connsFile>
        **Default:** ``None``
        **Options:** ``<option>`` <description of option>


    """



    import json
    from time import time
    from .. import sim

    numDis = 0
    totCon = 0

    start = time()
    if tagsFile:
        logger.info('Loading tags file...')
        with open(tagsFile, 'r') as fileObj: tagsTmp = json.load(fileObj)['tags']
        tags = {int(k): v for k,v in tagsTmp.items()}
        del tagsTmp
    if connsFile:
        logger.info('Loading conns file...')
        with open(connsFile, 'r') as fileObj: connsTmp = json.load(fileObj)['conns']
        conns = {int(k): v for k,v in connsTmp.items()}
        del connsTmp

    logger.info('  Calculating disynaptic connections...')
    # loading from json files
    if tags and conns:
        cellsPreGids = getCellsIncludeTags(includePre, tags)
        cellsPrePreGids = getCellsIncludeTags(includePrePre, tags)
        cellsPostGids = getCellsIncludeTags(includePost, tags)

        preGidIndex = conns['format'].index('preGid') if 'format' in conns else 0
        for postGid in cellsPostGids:
            preGidsAll = [conn[preGidIndex] for conn in conns[postGid] if isinstance(conn[preGidIndex], Number) and conn[preGidIndex] in cellsPreGids+cellsPrePreGids]
            preGids = [gid for gid in preGidsAll if gid in cellsPreGids]
            for preGid in preGids:
                prePreGids = [conn[preGidIndex] for conn in conns[preGid] if conn[preGidIndex] in cellsPrePreGids]
                totCon += 1
                if not set(prePreGids).isdisjoint(preGidsAll):
                    numDis += 1

    else:
        if sim.cfg.compactConnFormat:
            if 'preGid' in sim.cfg.compactConnFormat:
                preGidIndex = sim.cfg.compactConnFormat.index('preGid')  # using compact conn format (list)
            else:
                logger.warning('   Error: cfg.compactConnFormat does not include "preGid"')
                return -1
        else:
            preGidIndex = 'preGid' # using long conn format (dict)

        _, cellsPreGids, _ =  getCellsInclude(includePre)
        _, cellsPrePreGids, _ = getCellsInclude(includePrePre)
        cellsPost, _, _ = getCellsInclude(includePost)

        for postCell in cellsPost:
            preGidsAll = [conn[preGidIndex] for conn in postCell['conns'] if isinstance(conn[preGidIndex], Number) and conn[preGidIndex] in cellsPreGids+cellsPrePreGids]
            preGids = [gid for gid in preGidsAll if gid in cellsPreGids]
            for preGid in preGids:
                preCell = sim.net.allCells[preGid]
                prePreGids = [conn[preGidIndex] for conn in preCell['conns'] if conn[preGidIndex] in cellsPrePreGids]
                totCon += 1
                if not set(prePreGids).isdisjoint(preGidsAll):
                    numDis += 1

    logger.info('    Total disynaptic connections: %d / %d (%.2f%%)' % (numDis, totCon, float(numDis)/float(totCon)*100 if totCon>0 else 0.0))
    try:
        sim.allSimData['disynConns'] = numDis
    except:
        pass

    logger.info('    time ellapsed (s): ', time() - start)

    return numDis

