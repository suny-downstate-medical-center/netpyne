
"""
stims.py 

Methods to create stims in the network

Contributors: salvadordura@gmail.com
"""

from numbers import Number


# -----------------------------------------------------------------------------
#  Add stims
# -----------------------------------------------------------------------------
def addStims (self):
    from .. import sim

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
                    postCellsTags = {gid: tags for (gid,tags) in postCellsTags.iteritems() if condValue[0] <= tags.get(condKey, None) < condValue[1]}  # dict with post Cell objects}  # dict with pre cell tags
                elif condKey == 'cellList':
                    pass
                elif isinstance(condValue, list): 
                    postCellsTags = {gid: tags for (gid,tags) in postCellsTags.iteritems() if tags.get(condKey, None) in condValue}  # dict with post Cell objects
                else:
                    postCellsTags = {gid: tags for (gid,tags) in postCellsTags.iteritems() if tags.get(condKey, None) == condValue}  # dict with post Cell objects
            
            # subset of cells from selected pops (by relative indices)                     
            if 'cellList' in target['conds']:
                orderedPostGids = sorted(postCellsTags.keys())
                gidList = [orderedPostGids[i] for i in target['conds']['cellList']]
                postCellsTags = {gid: tags for (gid,tags) in postCellsTags.iteritems() if gid in gidList}

            # initialize randomizer in case used in string-based function (see issue #89 for more details)
            self.rand.Random123(sim.id32('stim_'+source['type']), sim.id32('%d%d'%(len(postCellsTags), sum(postCellsTags))), sim.cfg.seeds['stim'])

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
                        for p in ['Weight', 'Delay', 'loc']:
                            if 'synMech'+p+'Factor' in target:
                                params['synMech'+p+'Factor'] = target.get('synMech'+p+'Factor')
                        
                    
                    if 'originalFormat' in source and source['originalFormat'] == 'NeuroML2':
                        if 'weight' in target:
                            params['weight'] = target['weight']

                    for sourceParam in source: # copy source params
                        params[sourceParam] = strParams[sourceParam+'List'][postCellGid] if sourceParam+'List' in strParams else source.get(sourceParam)

                    if source['type'] == 'NetStim':
                        self._addCellStim(params, postCell)  # call method to add connections (sort out synMechs first)
                    else:
                        postCell.addStim(params)  # call cell method to add connection

    print('  Number of stims on node %i: %i ' % (sim.rank, sum([len(cell.stims) for cell in self.cells])))
    sim.pc.barrier()
    sim.timing('stop', 'stimsTime')
    if sim.rank == 0 and sim.cfg.timing: print('  Done; cell stims creation time = %0.2f s.' % sim.timingData['stimsTime'])

    return [cell.stims for cell in self.cells]


# -----------------------------------------------------------------------------
# Set parameters and add stim
# -----------------------------------------------------------------------------
def _addCellStim (self, stimParam, postCell):

    # convert synMech param to list (if not already)
    if not isinstance(stimParam.get('synMech'), list):
        stimParam['synMech'] = [stimParam.get('synMech')]


    # generate dict with final params for each synMech
    paramPerSynMech = ['weight', 'delay', 'loc']
    finalParam = {}
    for i, synMech in enumerate(stimParam.get('synMech')):

        for param in paramPerSynMech:
            finalParam[param+'SynMech'] = stimParam.get(param)
            if len(stimParam['synMech']) > 1:
                if isinstance (stimParam.get(param), list):  # get weight from list for each synMech
                    finalParam[param+'SynMech'] = stimParam[param][i]
                elif 'synMech'+param.title()+'Factor' in stimParam: # adapt weight for each synMech
                    finalParam[param+'SynMech'] = stimParam[param] * stimParam['synMech'+param.title()+'Factor'][i]

        params = {k: stimParam.get(k) for k,v in stimParam.iteritems()}

        params['synMech'] = synMech 
        params['loc'] = finalParam['locSynMech'] 
        params['weight'] = finalParam['weightSynMech']
        params['delay'] = finalParam['delaySynMech']

        postCell.addStim(params=params)



# -----------------------------------------------------------------------------
# Convert stim param string to function
# -----------------------------------------------------------------------------
def _stimStrToFunc (self, postCellsTags, sourceParams, targetParams):

    # list of params that have a function passed in as a string
    #params = sourceParams+targetParams
    params = sourceParams.copy()
    params.update(targetParams)

    paramsStrFunc = [param for param in self.stimStringFuncParams+self.connStringFuncParams 
        if param in params and isinstance(params[param], basestring) and params[param] not in ['variable']]  

    # dict to store correspondence between string and actual variable
    dictVars = {}   
    dictVars['post_x']      = lambda postConds: postConds['x'] 
    dictVars['post_y']      = lambda postConds: postConds['y'] 
    dictVars['post_z']      = lambda postConds: postConds['z'] 
    dictVars['post_xnorm']  = lambda postConds: postConds['xnorm'] 
    dictVars['post_ynorm']  = lambda postConds: postConds['ynorm'] 
    dictVars['post_znorm']  = lambda postConds: postConds['znorm'] 
    dictVars['rand']        = lambda unused1: self.rand
     
    # add netParams variables
    for k,v in self.params.__dict__.iteritems():
        if isinstance(v, Number):
            dictVars[k] = v

    # for each parameter containing a function, calculate lambda function and arguments
    strParams = {}
    for paramStrFunc in paramsStrFunc:
        strFunc = params[paramStrFunc]  # string containing function
        for randmeth in self.stringFuncRandMethods: strFunc = strFunc.replace(randmeth, 'rand.'+randmeth)  # append rand. to h.Random() methods
        strVars = [var for var in dictVars.keys() if var in strFunc and var+'norm' not in strFunc]  # get list of variables used (eg. post_ynorm or dist_xyz)
        lambdaStr = 'lambda ' + ','.join(strVars) +': ' + strFunc # convert to lambda function 
        lambdaFunc = eval(lambdaStr)

        # store lambda function and func vars in connParam (for weight, delay and synsPerConn since only calculated for certain conns)
        params[paramStrFunc+'Func'] = lambdaFunc
        params[paramStrFunc+'FuncVars'] = {strVar: dictVars[strVar] for strVar in strVars} 


        # replace lambda function (with args as dict of lambda funcs) with list of values
        strParams[paramStrFunc+'List'] = {postGid: params[paramStrFunc+'Func'](**{k:v if isinstance(v, Number) else v(postCellTags) for k,v in params[paramStrFunc+'FuncVars'].iteritems()})  
                for postGid,postCellTags in postCellsTags.iteritems()}

    return strParams



