"""
analysis.py

Functions to plot and analyse results

Contributors: salvadordura@gmail.com
"""

from netpyne import __gui__

if __gui__:
    import matplotlib.pyplot as plt
import numpy as np
from numbers import Number
from utils import exception

# -------------------------------------------------------------------------------------------------------------------
## Support function for plotConn() - calculate conn using data from sim object
# -------------------------------------------------------------------------------------------------------------------

def _plotConnCalculateFromSim(includePre, includePost, feature, orderBy, groupBy, groupByIntervalPre, groupByIntervalPost, synOrConn, synMech):

    import sim

    def list_of_dict_unique_by_key(seq, key):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if x[key] not in seen and not seen_add(x[key])]

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
            print "  Error: cfg.compactConnFormat missing:"
            print missing
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
            print 'Conn matrix with groupBy="cell" only supports features= "weight", "delay" or "numConns"'
            return fig
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
                            connMatrix[cellIndsPre[conn[preGidIndex]], cellIndsPost[cell['gid']]] += conn[featureIndex]
                    countMatrix[cellIndsPre[conn[preGidIndex]], cellIndsPost[cell['gid']]] += 1

        if feature in ['weight', 'delay']: connMatrix = connMatrix / countMatrix 
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
                        weightMatrix[popIndsPre[prePopLabel], popIndsPost[cell['tags']['pop']]] += conn[weightIndex]
                    elif feature == 'delay': 
                        delayMatrix[popIndsPre[prePopLabel], popIndsPost[cell['tags']['pop']]] += conn[delayIndex] 
                    countMatrix[popIndsPre[prePopLabel], popIndsPost[cell['tags']['pop']]] += 1    

        pre, post = popsPre, popsPost 
    
    # Calculate matrix if grouped by numeric tag (eg. 'y')
    elif groupBy in sim.net.allCells[0]['tags'] and isinstance(sim.net.allCells[0]['tags'][groupBy], Number):
        if not isinstance(groupByIntervalPre, Number) or not isinstance(groupByIntervalPost, Number):
            print 'groupByIntervalPre or groupByIntervalPost not specified'
            return

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
        #     print 'groupBy %s with groupByIntervalPre %s and groupByIntervalPost %s results in <2 groups'%(str(groupBy), str(groupByIntervalPre), str(groupByIntervalPre))
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
        print 'groupBy (%s) is not valid'%(str(groupBy))
        return

    # normalize by number of postsyn cells
    if groupBy != 'cell':
        if feature == 'weight': 
            connMatrix = weightMatrix / countMatrix  # avg weight per conn (fix to remove divide by zero warning) 
        elif feature == 'delay': 
            connMatrix = delayMatrix / countMatrix
        elif feature == 'numConns':
            connMatrix = countMatrix
        elif feature in ['probability', 'strength']:
            connMatrix = countMatrix / maxConnMatrix  # probability
            if feature == 'strength':
                connMatrix = connMatrix * weightMatrix  # strength
        elif feature == 'convergence':
            connMatrix = countMatrix / maxPostConnMatrix
        elif feature == 'divergence':
            connMatrix = countMatrix / maxPreConnMatrix



    return connMatrix, pre, post


# -------------------------------------------------------------------------------------------------------------------
## Support function for plotConn() - calculate conn using data from files with short format (no keys)
# -------------------------------------------------------------------------------------------------------------------

def _plotConnCalculateFromFile(includePre, includePost, feature, orderBy, groupBy, groupByIntervalPre, groupByIntervalPost, synOrConn, synMech, connsFile, tagsFile):
    
    import sim
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
        print 'Loading tags file...'
        with open(tagsFile, 'r') as fileObj: tagsTmp = json.load(fileObj)['tags']
        tagsFormat = tagsTmp.pop('format', [])
        tags = {int(k): v for k,v in tagsTmp.iteritems()} # find method to load json with int keys?
        del tagsTmp
    if connsFile:
        print 'Loading conns file...'
        with open(connsFile, 'r') as fileObj: connsTmp = json.load(fileObj)['conns']
        connsFormat = connsTmp.pop('format', [])
        conns = {int(k): v for k,v in connsTmp.iteritems()}
        del connsTmp

    print 'Finished loading; total time (s): %.2f'%(time()-start)
         
    # find pre and post cells
    if tags and conns:
        cellGidsPre = getCellsIncludeTags(includePre, tags, tagsFormat)
        if includePre == includePost:
            cellGidsPost = cellGidsPre
        else:
            cellGidsPost = getCellsIncludeTags(includePost, tags, tagsFormat)
    else:
        print 'Error loading tags and conns from file' 
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
        print "Missing:"
        print missing
        return None, None, None 

    if isinstance(synMech, basestring): synMech = [synMech]  # make sure synMech is a list
    
    # Calculate matrix if grouped by cell
    if groupBy == 'cell': 
        print 'plotConn from file for groupBy=cell not implemented yet'
        return None, None, None 

    # Calculate matrix if grouped by pop
    elif groupBy == 'pop': 
        
        # get list of pops
        print '    Obtaining list of populations ...'
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
        print '    Calculating max num conns for each pair of population ...'
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
        print '    Calculating weights, strength, prob, delay etc matrices ...'
        for postGid in cellGidsPost:  # for each postsyn cell
            print '     cell %d'%(int(postGid))
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
        print 'plotConn from file for groupBy=[arbitrary property] not implemented yet'
        return None, None, None 

    # no valid groupBy
    else:  
        print 'groupBy (%s) is not valid'%(str(groupBy))
        return

    if groupBy != 'cell':
        if feature == 'weight': 
            connMatrix = weightMatrix / countMatrix  # avg weight per conn (fix to remove divide by zero warning) 
        elif feature == 'delay': 
            connMatrix = delayMatrix / countMatrix
        elif feature == 'numConns':
            connMatrix = countMatrix
        elif feature in ['probability', 'strength']:
            connMatrix = countMatrix / maxConnMatrix  # probability
            if feature == 'strength':
                connMatrix = connMatrix * weightMatrix  # strength
        elif feature == 'convergence':
            connMatrix = countMatrix / maxPostConnMatrix
        elif feature == 'divergence':
            connMatrix = countMatrix / maxPreConnMatrix

    print '    plotting ...'
    return connMatrix, pre, post


# -------------------------------------------------------------------------------------------------------------------
## Plot connectivity
# -------------------------------------------------------------------------------------------------------------------
@exception
def plotConn (includePre = ['all'], includePost = ['all'], feature = 'strength', orderBy = 'gid', figSize = (10,10), groupBy = 'pop', groupByIntervalPre = None, groupByIntervalPost = None,
            graphType = 'matrix', synOrConn = 'syn', synMech = None, connsFile = None, tagsFile = None, clim = None, saveData = None, saveFig = None, showFig = True): 
    ''' 
    Plot network connectivity
        - includePre (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Cells to show (default: ['all'])
        - includePost (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Cells to show (default: ['all'])
        - feature ('weight'|'delay'|'numConns'|'probability'|'strength'|'convergence'|'divergence'): Feature to show in connectivity matrix; 
            the only features applicable to groupBy='cell' are 'weight', 'delay' and 'numConns';  'strength' = weight * probability (default: 'strength')
        - groupBy ('pop'|'cell'|'y'|: Show matrix for individual cells, populations, or by other numeric tag such as 'y' (default: 'pop')
        - groupByInterval (int or float): Interval of groupBy feature to group cells by in conn matrix, e.g. 100 to group by cortical depth in steps of 100 um   (default: None)
        - orderBy ('gid'|'y'|'ynorm'|...): Unique numeric cell property to order x and y axes by, e.g. 'gid', 'ynorm', 'y' (requires groupBy='cells') (default: 'gid')
        - graphType ('matrix','bar','pie'): Type of graph to represent data (default: 'matrix')
        - synOrConn ('syn'|'conn'): Use synapses or connections; note 1 connection can have multiple synapses (default: 'syn')
        - figSize ((width, height)): Size of figure (default: (10,10))
        - synMech (['AMPA', 'GABAA',...]): Show results only for these syn mechs (default: None)
        - saveData (None|True|'fileName'): File name where to save the final data used to generate the figure; 
            if set to True uses filename from simConfig (default: None)
        - saveFig (None|True|'fileName'): File name where to save the figure; 
            if set to True uses filename from simConfig (default: None)
        - showFig (True|False): Whether to show the figure or not (default: True)

        - Returns figure handles
    '''
    
    import sim

    print('Plotting connectivity matrix...')

    if connsFile and tagsFile:
        connMatrix, pre, post = _plotConnCalculateFromFile(includePre, includePost, feature, orderBy, groupBy, groupByIntervalPre, groupByIntervalPost, synOrConn, synMech, connsFile, tagsFile)
    else:
        connMatrix, pre, post = _plotConnCalculateFromSim(includePre, includePost, feature, orderBy, groupBy, groupByIntervalPre, groupByIntervalPost, synOrConn, synMech)


    if connMatrix is None:
        print "Error calculating connMatrix in plotConn()"
        return None

    # matrix plot
    if graphType == 'matrix':
        # Create plot
        fig = plt.figure(figsize=figSize)
        fig.subplots_adjust(right=0.98) # Less space on right
        fig.subplots_adjust(top=0.96) # Less space on top
        fig.subplots_adjust(bottom=0.02) # Less space on bottom
        h = plt.axes()

        plt.imshow(connMatrix, interpolation='nearest', cmap='jet', vmin=np.nanmin(connMatrix), vmax=np.nanmax(connMatrix))  #_bicolormap(gap=0)

        # Plot grid lines
        plt.hold(True)
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
            plt.xlim(-0.5,len(cellsPost)-0.5)
            plt.ylim(len(cellsPre)-0.5,-0.5)

        elif groupBy == 'pop':
            popsPre, popsPost = pre, post

            for ipop, pop in enumerate(popsPre):
                plt.plot(np.array([0,len(popsPre)])-0.5,np.array([ipop,ipop])-0.5,'-',c=(0.7,0.7,0.7))
            for ipop, pop in enumerate(popsPost):
                plt.plot(np.array([ipop,ipop])-0.5,np.array([0,len(popsPost)])-0.5,'-',c=(0.7,0.7,0.7))

            # Make pretty
            h.set_xticks(range(len(popsPost)))
            h.set_yticks(range(len(popsPre)))
            h.set_xticklabels(popsPost)
            h.set_yticklabels(popsPre)
            h.xaxis.set_ticks_position('top')
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
            plt.xlim(-0.5,len(groupsPost)-0.5)
            plt.ylim(len(groupsPre)-0.5,-0.5)

        if not clim: clim = [np.nanmin(connMatrix), np.nanmax(connMatrix)]
        plt.clim(clim[0], clim[1])
        plt.colorbar(label=feature, shrink=0.8) #.set_label(label='Fitness',size=20,weight='bold')
        plt.xlabel('post')
        h.xaxis.set_label_coords(0.5, 1.06)
        plt.ylabel('pre')
        plt.title ('Connection '+feature+' matrix', y=1.08)

    # stacked bar graph
    elif graphType == 'bar':
        if groupBy == 'pop':
            popsPre, popsPost = pre, post

            from netpyne.support import stackedBarGraph 
            SBG = stackedBarGraph.StackedBarGrapher()
    
            fig = plt.figure(figsize=figSize)
            ax = fig.add_subplot(111)
            SBG.stackedBarPlot(ax, connMatrix.transpose(), colorList, xLabels=popsPost, gap = 0.1, scale=False, xlabel='postsynaptic', ylabel = feature)
            plt.title ('Connection '+feature+' stacked bar graph')
            plt.legend(popsPre)
            plt.tight_layout()

        elif groupBy == 'cell':
            print 'Error: plotConn graphType="bar" with groupBy="cell" not implemented'

    elif graphType == 'pie':
        print 'Error: plotConn graphType="pie" not yet implemented'


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
            filename = sim.cfg.filename+'_'+'conn_'+feature+'.png'
        plt.savefig(filename)

    # show fig 
    if showFig: _showFigure()

    return fig, {}


# -------------------------------------------------------------------------------------------------------------------
## Plot 2D representation of network cell positions and connections
# -------------------------------------------------------------------------------------------------------------------
@exception
def plot2Dnet (include = ['allCells'], figSize = (12,12), view = 'xy', showConns = True, popColors = None, 
                tagsFile = None, saveData = None, saveFig = None, showFig = True): 
    ''' 
    Plot 2D representation of network cell positions and connections
        - include (['all',|'allCells','allNetStims',|,120,|,'E1'|,('L2', 56)|,('L5',[4,5,6])]): Cells to show (default: ['all'])
        - showConns (True|False): Whether to show connections or not (default: True)
        - figSize ((width, height)): Size of figure (default: (12,12))
        - view ('xy', 'xz'): Perspective view: front ('xy') or top-down ('xz')
        - popColors (dict): Dictionary with color (value) used for each population (key) (default: None)
        - saveData (None|'fileName'): File name where to save the final data used to generate the figure (default: None)
        - saveFig (None|'fileName'): File name where to save the figure;
            if set to True uses filename from simConfig (default: None)(default: None)
        - showFig (True|False): Whether to show the figure or not;
            if set to True uses filename from simConfig (default: None)

        - Returns figure handles
    '''
    import sim

    print('Plotting 2D representation of network cell locations and connections...')

    fig = plt.figure(figsize=figSize)

    # front view
    if view == 'xy':
        ycoord = 'y'
    elif view == 'xz':
        ycoord = 'z'

    if tagsFile:
        print 'Loading tags file...'
        import json
        with open(tagsFile, 'r') as fileObj: tagsTmp = json.load(fileObj)['tags']
        tagsFormat = tagsTmp.pop('format', [])
        tags = {int(k): v for k,v in tagsTmp.iteritems()} # find method to load json with int keys?
        del tagsTmp

        # set indices of fields to read compact format (no keys)
        missing = []
        popIndex = tagsFormat.index('pop') if 'pop' in tagsFormat else missing.append('pop')
        xIndex = tagsFormat.index('x') if 'x' in tagsFormat else missing.append('x')
        yIndex = tagsFormat.index('y') if 'y' in tagsFormat else missing.append('y')
        zIndex = tagsFormat.index('z') if 'z' in tagsFormat else missing.append('z')
        if len(missing) > 0:
            print "Missing:"
            print missing
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
            print 'Error loading tags from file' 
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
    if showConns and not tagsFile:
        for postCell in cells:
            for con in postCell['conns']:  # plot connections between cells
                if not isinstance(con['preGid'], basestring) and con['preGid'] in cellGids:
                    posXpre,posYpre = next(((cell['tags']['x'],cell['tags'][ycoord]) for cell in cells if cell['gid']==con['preGid']), None)  
                    posXpost,posYpost = postCell['tags']['x'], postCell['tags'][ycoord] 
                    color='red'
                    if con['synMech'] in ['inh', 'GABA', 'GABAA', 'GABAB']:
                        color = 'blue'
                    width = 0.1 #50*con['weight']
                    plt.plot([posXpre, posXpost], [posYpre, posYpost], color=color, linewidth=width) # plot line from pre to post
    
    plt.xlabel('x (um)')
    plt.ylabel(ycoord+' (um)') 
    plt.xlim([min(posX)-0.05*max(posX),1.05*max(posX)]) 
    plt.ylim([min(posY)-0.05*max(posY),1.05*max(posY)])
    fontsiz = 12

    for popLabel in popLabels:
        plt.plot(0,0,color=popColors[popLabel],label=popLabel)
    plt.legend(fontsize=fontsiz, bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
    ax = plt.gca()
    ax.invert_yaxis()

    # save figure data
    if saveData:
        figData = {'posX': posX, 'posY': posY, 'posX': cellColors, 'posXpre': posXpre, 'posXpost': posXpost, 'posYpre': posYpre, 'posYpost': posYpost,
         'include': include, 'saveData': saveData, 'saveFig': saveFig, 'showFig': showFig}
    
        _saveFigData(figData, saveData, '2Dnet')
 
    # save figure
    if saveFig: 
        if isinstance(saveFig, basestring):
            filename = saveFig
        else:
            filename = sim.cfg.filename+'_'+'2Dnet.png'
        plt.savefig(filename)

    # show fig 
    if showFig: _showFigure()

    return fig, {}

# -------------------------------------------------------------------------------------------------------------------
## Calculate number of disynaptic connections
# ------------------------------------------------------------------------------------------------------------------- 
@exception
def calculateDisynaptic(includePost = ['allCells'], includePre = ['allCells'], includePrePre = ['allCells'], 
        tags=None, conns=None, tagsFile=None, connsFile=None):

    import json
    from time import time
    import sim

    numDis = 0
    totCon = 0

    start = time()
    if tagsFile:
        print 'Loading tags file...'
        with open(tagsFile, 'r') as fileObj: tagsTmp = json.load(fileObj)['tags']
        tags = {int(k): v for k,v in tagsTmp.iteritems()}
        del tagsTmp
    if connsFile:
        print 'Loading conns file...'
        with open(connsFile, 'r') as fileObj: connsTmp = json.load(fileObj)['conns']
        conns = {int(k): v for k,v in connsTmp.iteritems()}
        del connsTmp
         
    print '  Calculating disynaptic connections...'
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
                print '   Error: cfg.compactConnFormat does not include "preGid"'
                return -1
        else:  
            preGidIndex = 'preGid' # using long conn format (dict)

        _, cellsPreGids, _ =  getCellsInclude(includePre)
        _, cellsPrePreGids, _ = getCellsInclude(includePrePre)
        cellsPost, _, _ = getCellsInclude(includePost)

        for postCell in cellsPost:
            print postCell['gid']
            preGidsAll = [conn[preGidIndex] for conn in postCell['conns'] if isinstance(conn[preGidIndex], Number) and conn[preGidIndex] in cellsPreGids+cellsPrePreGids]
            preGids = [gid for gid in preGidsAll if gid in cellsPreGids]
            for preGid in preGids:
                preCell = sim.net.allCells[preGid]
                prePreGids = [conn[preGidIndex] for conn in preCell['conns'] if conn[preGidIndex] in cellsPrePreGids]
                totCon += 1
                if not set(prePreGids).isdisjoint(preGidsAll):
                    numDis += 1

    print '    Total disynaptic connections: %d / %d (%.2f%%)' % (numDis, totCon, float(numDis)/float(totCon)*100 if totCon>0 else 0.0)
    try:
        sim.allSimData['disynConns'] = numDis
    except:
        pass

    print '    time ellapsed (s): ', time() - start
    
    return numDis

