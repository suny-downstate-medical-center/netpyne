
"""
network.py 

Defines Network class which contains cell objects and network-realated methods

Contributors: salvadordura@gmail.com
"""

from pylab import array, sin, cos, tan, exp, sqrt, mean, inf, rand
from random import seed, random, randint, sample, uniform, triangular, gauss, betavariate, expovariate, gammavariate
from time import time
from numbers import Number
from copy import copy
from neuron import h  # import NEURON
import framework as f


class Network(object):

    ###############################################################################
    # initialize variables
    ###############################################################################
    def __init__(self, params = None):
        self.params = params

    ###############################################################################
    # Set network params
    ###############################################################################
    def setParams(self, params):
        self.params = params

    ###############################################################################
    # Instantiate network populations (objects of class 'Pop')
    ###############################################################################
    def createPops(self):
        self.pops = []  # list to store populations ('Pop' objects)
        for popParam in self.params['popParams']: # for each set of population paramseters 
            self.pops.append(f.Pop(popParam))  # instantiate a new object of class Pop and add to list pop


    ###############################################################################
    # Create Cells
    ###############################################################################
    def createCells(self):
        f.pc.barrier()
        f.sim.timing('start', 'createTime')
        if f.rank==0: print("\nCreating simulation of %i cell populations for %0.1f s on %i hosts..." % (len(self.pops), f.cfg['duration']/1000.,f.nhosts)) 
        self.gidVec = [] # Empty list for storing GIDs (index = local id; value = gid)
        self.gidDic = {} # Empty dict for storing GIDs (key = gid; value = local id) -- ~x6 faster than gidVec.index()  
        self.cells = []
        for ipop in self.pops: # For each pop instantiate the network cells (objects of class 'Cell')
            newCells = ipop.createCells() # create cells for this pop using Pop method
            self.cells.extend(newCells)  # add to list of cells
            f.pc.barrier()
            if f.rank==0 and f.cfg['verbose']: print('Instantiated %d cells of population %s'%(len(newCells), ipop.tags['popLabel']))    
        f.simData.update({name:h.Vector(1e4).resize(0) for name in ['spkt','spkid']})
        print('  Number of cells on node %i: %i ' % (f.rank,len(self.cells))) 
        f.pc.barrier()
        f.sim.timing('stop', 'createTime')
        if f.rank == 0 and f.cfg['timing']: print('  Done; cell creation time = %0.2f s.' % f.timing['createTime'])
        

    ###############################################################################
    # Connect Cells
    ###############################################################################
    def connectCells(self):
        # Instantiate network connections based on the connectivity rules defined in params
        if f.rank==0: 
            print('Making connections...')
            f.sim.timing('start', 'connectTime')

        if f.nhosts > 1: # Gather tags from all cells 
            allCellTags = f.sim.gatherAllCellTags()  
        else:
            allCellTags = {cell.gid: cell.tags for cell in self.cells}
        allPopTags = {i: pop.tags for i,pop in enumerate(self.pops)}  # gather tags from pops so can connect NetStim pops

        for connParam in self.params['connParams']:  # for each conn rule or parameter set
            if 'sec' not in connParam: connParam['sec'] = None  # if section not specified, make None (will be assigned to first section in cell)
            if 'syn' not in connParam: connParam['syn'] = None  # if synapse not specified, make None (will be assigned to first synapse in cell)  
            if 'threshold' not in connParam: connParam['threshold'] = None  # if no threshold specified, make None (will be assigned default value)
            if 'weight' not in connParam: connParam['weight'] = f.net.params['defaultWeight'] # if no weight, set default
            if 'delay' not in connParam: connParam['delay'] = f.net.params['defaultDelay'] # if no delay, set default

            preCellsTags = allCellTags  # initialize with all presyn cells 
            prePops = allPopTags  # initialize with all presyn pops
            for condKey,condValue in connParam['preTags'].iteritems():  # Find subset of cells that match presyn criteria
                if condKey == 'ynorm':
                    preCellsTags = {gid: tags for (gid,tags) in preCellsTags.iteritems() if condValue[0] <= tags[condKey] < condValue[1]}  # dict with pre cell tags
                    prePops = {}
                else:
                    preCellsTags = {gid: tags for (gid,tags) in preCellsTags.iteritems() if tags[condKey] in condValue}  # dict with pre cell tags
                    prePops = {i: tags for (i,tags) in prePops.iteritems() if (condKey in tags) and (tags[condKey] in condValue)}

            if not preCellsTags: # if no presyn cells, check if netstim
                if any (prePopTags['cellModel'] == 'NetStim' for prePopTags in prePops.values()):
                    for prePop in prePops.values():
                        if not 'number' in prePop: prePop['number'] = 1e12  # add default number 
                        if not 'source' in prePop: prePop['source'] = 'random'  # add default source
                    preCellsTags = prePops
            
            postCells = {cell.gid:cell for cell in self.cells}
            for condKey,condValue in connParam['postTags'].iteritems():  # Find subset of cells that match postsyn criteria
                if condKey == 'ynorm':
                    postCells = {gid: cell for (gid,cell) in postCells.iteritems() if condValue[0] <= cell.tags[condKey] < condValue[1]}  # dict with post Cell objects}  # dict with pre cell tags
                else:
                    postCells = {gid: cell for (gid,cell) in postCells.iteritems() if cell.tags[condKey] in condValue}  # dict with post Cell objects

            if 'connFunc' not in connParam:  # if conn function not specified, select based on params
                if 'probability' in connParam: connParam['connFunc'] = 'probConn'  # probability based func
                elif 'convergence' in connParam: connParam['connFunc'] = 'convConn'  # convergence function
                elif 'divergence' in connParam: connParam['connFunc'] = 'divConn'  # divergence function
                else: connParam['connFunc'] = 'fullConn'  # convergence function

            connFunc = getattr(self, connParam['connFunc'])  # get function name from params
            if preCellsTags and postCells:
                self.strToFunc(preCellsTags, postCells, connParam)  # convert strings to functions (for the delay, and probability params)
                connFunc(preCellsTags, postCells, connParam)  # call specific conn function
        
        print('  Number of connections on node %i: %i ' % (f.rank, sum([len(cell.conns) for cell in f.net.cells])))
        f.pc.barrier()
        f.sim.timing('stop', 'connectTime')
        if f.rank == 0 and f.cfg['timing']: print('  Done; cell connection time = %0.2f s.' % f.timing['connectTime'])

    ###############################################################################
    # Convert string to function
    ###############################################################################
    def strToFunc(self, preCellsTags, postCells, connParam):
        # list of params that have a function passed in as a string
        paramsStrFunc = [param for param in ['weight', 'delay', 'probability', 'convergence', 'divergence'] if param in connParam and isinstance(connParam[param], str)]  
        
        # dict to store correspondence between string and actual variable
        dictVars = {}  
        dictVars['pre_x']       = lambda preTags,postCell: preTags['x'] 
        dictVars['pre_y']       = lambda preTags,postCell: preTags['y'] 
        dictVars['pre_z']       = lambda preTags,postCell: preTags['z'] 
        dictVars['pre_xnorm']   = lambda preTags,postCell: preTags['xnorm'] 
        dictVars['pre_ynorm']   = lambda preTags,postCell: preTags['ynorm'] 
        dictVars['pre_znorm']   = lambda preTags,postCell: preTags['znorm'] 
        dictVars['post_x']      = lambda preTags,postCell: postCell.tags['x'] 
        dictVars['post_y']      = lambda preTags,postCell: postCell.tags['y'] 
        dictVars['post_z']      = lambda preTags,postCell: postCell.tags['z'] 
        dictVars['post_xnorm']  = lambda preTags,postCell: postCell['tags']['xnorm'] 
        dictVars['post_ynorm']  = lambda preTags,postCell: postCell['tags']['ynorm'] 
        dictVars['post_znorm']  = lambda preTags,postCell: postCell['tags']['znorm'] 
        dictVars['dist_x']      = lambda preTags,postCell: abs(preTags['x'] - postCell.tags['x'])
        dictVars['dist_y']      = lambda preTags,postCell: abs(preTags['y'] - postCell.tags['y']) 
        dictVars['dist_z']      = lambda preTags,postCell: abs(preTags['z'] - postCell.tags['z'])
        dictVars['dist_3D']    = lambda preTags,postCell: sqrt((preTags['x'] - postCell.tags['x'])**2 +
                                (preTags['y'] - postCell.tags['y'])**2 + 
                                (preTags['z'] - postCell.tags['z'])**2)
        dictVars['dist_2D']     = lambda preTags,postCell: sqrt((preTags['x'] - postCell.tags['x'])**2 +
                                (preTags['z'] - postCell.tags['z'])**2)
        dictVars['dist_xnorm']  = lambda preTags,postCell: abs(preTags['xnorm'] - postCell.tags['xnorm'])
        dictVars['dist_ynorm']  = lambda preTags,postCell: abs(preTags['ynorm'] - postCell.tags['ynorm']) 
        dictVars['dist_znorm']  = lambda preTags,postCell: abs(preTags['znorm'] - postCell.tags['znorm'])
        dictVars['dist_norm3D'] = lambda preTags,postCell: sqrt((preTags['xnorm'] - postCell.tags['xnorm'])**2 +
                                sqrt(preTags['ynorm'] - postCell.tags['ynorm']) + 
                                sqrt(preTags['znorm'] - postCell.tags['znorm']))
        dictVars['dist_norm2D'] = lambda preTags,postCell: sqrt((preTags['xnorm'] - postCell.tags['xnorm'])**2 +
                                sqrt(preTags['znorm'] - postCell.tags['znorm']))
        # add netParams variables
        for k,v in f.net.params.iteritems():
            if isinstance(v, Number):
                dictVars[k] = v

        # for each parameter containing a function
        for paramStrFunc in paramsStrFunc:
            strFunc = connParam[paramStrFunc]  # string containing function
            strVars = [var for var in dictVars.keys() if var in strFunc and var+'norm' not in strFunc]  # get list of variables used (eg. post_ynorm or dist_xyz)
            lambdaStr = 'lambda ' + ','.join(strVars) +': ' + strFunc # convert to lambda function 
            lambdaFunc = eval(lambdaStr)
       
             # initialize randomizer in case used in function
            seed(f.sim.id32('%d'%(f.cfg['randseed']+postCells.keys()[0]+preCellsTags.keys()[0])))

            if paramStrFunc in ['probability']:
                # replace function with list of values derived from function (one per pre+post cell)
                connParam[paramStrFunc+'Func'] = [lambdaFunc(
                    **{strVar: dictVars[strVar] if isinstance(dictVars[strVar], Number) else dictVars[strVar](preCellTags, postCell) for strVar in strVars})  
                    for preCellTags in preCellsTags.values() for postCell in postCells.values()]

            elif paramStrFunc in ['convergence']:
                # replace function with list of values derived from function (one per post cell)
                connParam[paramStrFunc+'Func'] = [lambdaFunc(
                    **{strVar: dictVars[strVar] if isinstance(dictVars[strVar], Number) else dictVars[strVar](None, postCell) for strVar in strVars}) 
                    for postCell in postCells.values()]

            elif paramStrFunc in ['divergence']:
                # replace function with list of values derived from function (one per post cell)
                connParam[paramStrFunc+'Func'] = [lambdaFunc(
                    **{strVar: dictVars[strVar] if isinstance(dictVars[strVar], Number) else dictVars[strVar](preCellTags, None) for strVar in strVars}) 
                    for preCellTags in preCellsTags.values()]

            else:
                # store lambda function and func vars in connParam (for weight and delay, since only calcualted for certain conns)
                connParam[paramStrFunc+'Func'] = lambdaFunc
                connParam[paramStrFunc+'FuncVars'] = {strVar: dictVars[strVar] for strVar in strVars} 
                

    ###############################################################################
    ### Full connectivity
    ###############################################################################
    def fullConn(self, preCellsTags, postCells, connParam):
        ''' Generates connections between all pre and post-syn cells '''
        if f.cfg['verbose']: print 'Generating set of all-to-all connections...'

        # list of params that can have a lambda function
        paramsStrFunc = [param for param in ['weightFunc', 'delayFunc'] if param in connParam] 
        for paramStrFunc in paramsStrFunc:
            # replace lambda function (with args as dict of lambda funcs) with list of values
            seed(f.sim.id32('%d'%(f.cfg['randseed']+postCells.keys()[0]+preCellsTags.keys()[0])))  
            connParam[paramStrFunc] = [connParam[paramStrFunc](**{k:v if isinstance(v, Number) else v(preCellTags,postCell) for k,v in connParam[paramStrFunc+'Vars'].iteritems()})  
                    for preCellTags in preCellsTags.values() for postCell in postCells.values()]
        
        for postCellGid, postCell in postCells.iteritems():  # for each postsyn cell
            for preCellGid, preCellTags in preCellsTags.iteritems():  # for each presyn cell
                if preCellTags['cellModel'] == 'NetStim':  # if NetStim
                    params = {'popLabel': preCellTags['popLabel'],
                    'rate': preCellTags['rate'],
                    'noise': preCellTags['noise'],
                    'source': preCellTags['source'], 
                    'number': preCellTags['number'],
                    'sec': connParam['sec'], 
                    'syn': connParam['syn'], 
                    'weight': connParam['weightFunc'].pop(0) if 'weightFunc' in connParam else connParam['weight'],
                    'delay': connParam['delayFunc'].pop(0) if 'delayFunc' in connParam else connParam['delay'],
                    'threshold': connParam['threshold']}
                    postCell.addStim(params)  # call cell method to add connections              
                elif preCellGid != postCellGid:
                    # if not self-connection
                    params = {'preGid': preCellGid, 
                    'sec': connParam['sec'], 
                    'syn': connParam['syn'], 
                    'weight': connParam['weightFunc'].pop(0) if 'weightFunc' in connParam else connParam['weight'],
                    'delay': connParam['delayFunc'].pop(0) if 'delayFunc' in connParam else connParam['delay'],
                    'threshold': connParam['threshold']}
                    postCell.addConn(params)  # call cell method to add connections



    ###############################################################################
    ### Probabilistic connectivity 
    ###############################################################################
    def probConn(self, preCellsTags, postCells, connParam):
        ''' Generates connections between all pre and post-syn cells based on probability values'''
        if f.cfg['verbose']: print 'Generating set of probabilistic connections...'
        
        seed(f.sim.id32('%d'%(f.cfg['randseed']+postCells.keys()[0]+preCellsTags.keys()[0])))  
        allRands = [random() for i in range(len(preCellsTags)*len(postCells))]  # Create an array of random numbers for checking each connection
        for postCellGid, postCell in postCells.iteritems():  # for each postsyn cell
            for preCellGid, preCellTags in preCellsTags.iteritems():  # for each presyn cell
                probability = connParam['probabilityFunc'].pop(0) if 'probabilityFunc' in connParam else connParam['probability']
                if 'weightFunc' in connParam: 
                    weightVars = {k:v if isinstance(v, Number) else v(preCellTags,postCell) for k,v in connParam['weightFuncVars'].iteritems()}  # call lambda functions to get weight func args
                if 'delayFunc' in connParam: 
                    delayVars = {k:v if isinstance(v, Number) else v(preCellTags,postCell) for k,v in connParam['delayFuncVars'].iteritems()}  # call lambda functions to get delay func args
                if probability >= allRands.pop():
                    seed(f.sim.id32('%d'%(f.cfg['randseed']+postCellGid+preCellGid)))  
                    if preCellTags['cellModel'] == 'NetStim':  # if NetStim
                        params = {'popLabel': preCellTags['popLabel'],
                                'rate': preCellTags['rate'],
                                'noise': preCellTags['noise'],
                                'source': preCellTags['source'], 
                                'number': preCellTags['number'],
                                'sec': connParam['sec'], 
                                'syn': connParam['syn'], 
                                'weight': connParam['weightFunc'](**weightVars) if 'weightFunc' in connParam else connParam['weight'],
                                'delay': connParam['delayFunc'](**delayVars) if 'delayFunc' in connParam else connParam['delay'], 
                                'threshold': connParam['threshold']}
                        postCell.addStim(params)  # call cell method to add connections              
                    elif preCellGid != postCellGid:
                        # if not self-connection
                        params = {'preGid': preCellGid, 
                                'sec': connParam['sec'], 
                                'syn': connParam['syn'], 
                                'weight': connParam['weightFunc'](**weightVars) if 'weightFunc' in connParam else connParam['weight'],
                                'delay': connParam['delayFunc'](**delayVars) if 'delayFunc' in connParam else connParam['delay'], 
                                'threshold': connParam['threshold']}
                        postCell.addConn(params)  # call cell method to add connections
       


    ###############################################################################
    ### Convergent connectivity 
    ###############################################################################
    def convConn(self, preCellsTags, postCells, connParam):
        ''' Generates connections between all pre and post-syn cells based on probability values'''
        if f.cfg['verbose']: print 'Generating set of convergent connections...'
        
        seed(f.sim.id32('%d'%(f.cfg['randseed']+postCells.keys()[0]+preCellsTags.keys()[0])))  
        for postCellGid, postCell in postCells.iteritems():  # for each postsyn cell
            convergence = connParam['convergenceFunc'].pop(0) if 'convergenceFunc' in connParam else connParam['convergence']  # num of presyn conns / postsyn cell
            convergence = max(min(int(round(convergence)), len(preCellsTags)), 0)
            preCellsSample = sample(preCellsTags.keys(), convergence)  # selected gids of presyn cells
            preCellsConv = {k:v for k,v in preCellsTags.iteritems() if k in preCellsSample}  # dict of selected presyn cells tags
            for preCellGid, preCellTags in preCellsConv.iteritems():  # for each presyn cell
                if 'weightFunc' in connParam:
                    weightVars = {k:v if isinstance(v, Number) else v(preCellTags,postCell) for k,v in connParam['weightFuncVars'].iteritems()}  # call lambda functions to get weight func args
                if 'delayFunc' in connParam: 
                    delayVars = {k:v if isinstance(v, Number) else v(preCellTags, postCell) for k,v in connParam['delayFuncVars'].iteritems()}  # call lambda functions to get delay func args
                seed(f.sim.id32('%d'%(f.cfg['randseed']+postCellGid+preCellGid)))  
                if preCellTags['cellModel'] == 'NetStim':  # if NetStim
                    print 'Error: Convergent connectivity for NetStims is not implemented'
                elif preCellGid != postCellGid: # if not self-connection
                    params = {'preGid': preCellGid, 
                            'sec': connParam['sec'], 
                            'syn': connParam['syn'], 
                            'weight': connParam['weightFunc'](**weightVars) if 'weightFunc' in connParam else connParam['weight'],
                            'delay': connParam['delayFunc'](**delayVars) if 'delayFunc' else connParam['delay'], 
                            'threshold': connParam['threshold']}
                    postCell.addConn(params)  # call cell method to add connections


    ###############################################################################
    ### Divergent connectivity 
    ###############################################################################
    def divConn(self, preCellsTags, postCells, connParam):
        ''' Generates connections between all pre and post-syn cells based on probability values'''
        if f.cfg['verbose']: print 'Generating set of divergent connections...'
        
        seed(f.sim.id32('%d'%(f.cfg['randseed']+postCells.keys()[0]+preCellsTags.keys()[0])))  
        for preCellGid, preCellTags in preCellsTags.iteritems():  # for each presyn cell
            divergence = connParam['divergenceFunc'].pop(0) if 'divergenceFunc' in connParam else connParam['divergence']  # num of presyn conns / postsyn cell
            divergence = max(min(int(round(divergence)), len(postCells)), 0)
            postCellsSample = sample(postCells, divergence)  # selected gids of postsyn cells
            postCellsDiv = {k:v for k,v in postCells.iteritems() if k in postCellsSample}  # dict of selected postsyn cells tags
            for postCellGid, postCell in postCellsDiv.iteritems():  # for each postsyn cell
                if 'weightFunc' in connParam:
                    weightVars = {k: v(preCellTags, postCell) for k,v in connParam['weightFuncVars'].iteritems()}  # call lambda functions to get weight func args
                if 'delayFunc' in connParam: 
                    delayVars = {k: v(preCellTags, postCell) for k,v in connParam['delayFuncVars'].iteritems()}  # call lambda functions to get delay func args
                seed(f.sim.id32('%d'%(f.cfg['randseed']+postCellGid+preCellGid)))  
                if preCellTags['cellModel'] == 'NetStim':  # if NetStim
                    print 'Error: Divergent connectivity for NetStims is not implemented'           
                elif preCellGid != postCellGid: # if not self-connection
                    params = {'preGid': preCellGid, 
                            'sec': connParam['sec'], 
                            'syn': connParam['syn'], 
                            'weight': connParam['weightFunc'](**weightVars) if 'weightFunc' in connParam else connParam['weight'],
                            'delay': connParam['delayFunc'](**delayVars) if 'delayFunc' in connParam else connParam['delay'], 
                            'threshold': connParam['threshold']}
                    postCell.addConn(params)  # call cell method to add connections
   

