
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
        self.lid2gid = [] # Empty list for storing local index -> GID (index = local id; value = gid)
        self.gid2lid = {} # Empty dict for storing GID -> local index (key = gid; value = local id) -- ~x6 faster than .index() 
        self.lastGid = 0  # keep track of last cell gid 
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
            if 'synMech' not in connParam: connParam['synMech'] = None  # if synaptic mechanism not specified, make None (will be assigned to first synaptic mechanism in cell)  
            if 'threshold' not in connParam: connParam['threshold'] = None  # if no threshold specified, make None (will be assigned default value)
            if 'weight' not in connParam: connParam['weight'] = f.net.params['defaultWeight'] # if no weight, set default
            if 'delay' not in connParam: connParam['delay'] = f.net.params['defaultDelay'] # if no delay, set default

            preCellsTags = dict(allCellTags)  # initialize with all presyn cells (make copy)
            prePops = allPopTags  # initialize with all presyn pops

            for condKey,condValue in connParam['preTags'].iteritems():  # Find subset of cells that match presyn criteria
                if condKey in ['x','y','z','xnorm','ynorm','znorm']:
                    preCellsTags = {gid: tags for (gid,tags) in preCellsTags.iteritems() if condValue[0] <= tags[condKey] < condValue[1]}  # dict with pre cell tags
                    prePops = {}
                else:
                    if isinstance(condValue, list): 
                        preCellsTags = {gid: tags for (gid,tags) in preCellsTags.iteritems() if tags[condKey] in condValue}  # dict with pre cell tags
                    else:
                        preCellsTags = {gid: tags for (gid,tags) in preCellsTags.iteritems() if tags[condKey] == condValue}  # dict with pre cell tags
                    prePops = {i: tags for (i,tags) in prePops.iteritems() if (condKey in tags) and (tags[condKey] in condValue)}

            if not preCellsTags: # if no presyn cells, check if netstim
                if any (prePopTags['cellModel'] == 'NetStim' for prePopTags in prePops.values()):
                    for prePop in prePops.values():
                        if not 'number' in prePop: prePop['number'] = 1e12  # add default number 
                        if not 'source' in prePop: prePop['source'] = 'random'  # add default source
                    preCellsTags = prePops
            
            if preCellsTags:  # only check post if there are pre
                postCellsTags = allCellTags
                for condKey,condValue in connParam['postTags'].iteritems():  # Find subset of cells that match postsyn criteria
                    if condKey in ['x','y','z','xnorm','ynorm','znorm']:
                        postCellsTags = {gid: tags for (gid,tags) in postCellsTags.iteritems() if condValue[0] <= tags[condKey] < condValue[1]}  # dict with post Cell objects}  # dict with pre cell tags
                    elif isinstance(condValue, list): 
                        postCellsTags = {gid: tags for (gid,tags) in postCellsTags.iteritems() if tags[condKey] in condValue}  # dict with post Cell objects
                    else:
                        postCellsTags = {gid: tags for (gid,tags) in postCellsTags.iteritems() if tags[condKey] == condValue}  # dict with post Cell objects


                if 'connFunc' not in connParam:  # if conn function not specified, select based on params
                    if 'probability' in connParam: connParam['connFunc'] = 'probConn'  # probability based func
                    elif 'convergence' in connParam: connParam['connFunc'] = 'convConn'  # convergence function
                    elif 'divergence' in connParam: connParam['connFunc'] = 'divConn'  # divergence function
                    else: connParam['connFunc'] = 'fullConn'  # convergence function

                connFunc = getattr(self, connParam['connFunc'])  # get function name from params
                if preCellsTags and postCellsTags:
                    self.strToFunc(preCellsTags, postCellsTags, connParam)  # convert strings to functions (for the delay, and probability params)
                    connFunc(preCellsTags, postCellsTags, connParam)  # call specific conn function
        
        print('  Number of connections on node %i: %i ' % (f.rank, sum([len(cell.conns) for cell in f.net.cells])))
        f.pc.barrier()
        f.sim.timing('stop', 'connectTime')
        if f.rank == 0 and f.cfg['timing']: print('  Done; cell connection time = %0.2f s.' % f.timing['connectTime'])

    ###############################################################################
    # Convert string to function
    ###############################################################################
    def strToFunc(self, preCellsTags, postCellsTags, connParam):
        # list of params that have a function passed in as a string
        paramsStrFunc = [param for param in ['weight', 'delay', 'probability', 'convergence', 'divergence'] if param in connParam and isinstance(connParam[param], str)]  

        # dict to store correspondence between string and actual variable
        dictVars = {}  
        dictVars['pre_x']       = lambda preTags,postTags: preTags['x'] 
        dictVars['pre_y']       = lambda preTags,postTags: preTags['y'] 
        dictVars['pre_z']       = lambda preTags,postTags: preTags['z'] 
        dictVars['pre_xnorm']   = lambda preTags,postTags: preTags['xnorm'] 
        dictVars['pre_ynorm']   = lambda preTags,postTags: preTags['ynorm'] 
        dictVars['pre_znorm']   = lambda preTags,postTags: preTags['znorm'] 
        dictVars['post_x']      = lambda preTags,postTags: postTags['x'] 
        dictVars['post_y']      = lambda preTags,postTags: postTags['y'] 
        dictVars['post_z']      = lambda preTags,postTags: postTags['z'] 
        dictVars['post_xnorm']  = lambda preTags,postTags: postTags['xnorm'] 
        dictVars['post_ynorm']  = lambda preTags,postTags: postTags['ynorm'] 
        dictVars['post_znorm']  = lambda preTags,postTags: postTags['znorm'] 
        dictVars['dist_x']      = lambda preTags,postTags: abs(preTags['x'] - postTags['x'])
        dictVars['dist_y']      = lambda preTags,postTags: abs(preTags['y'] - postTags['y']) 
        dictVars['dist_z']      = lambda preTags,postTags: abs(preTags['z'] - postTags['z'])
        dictVars['dist_3D']    = lambda preTags,postTags: sqrt((preTags['x'] - postTags['x'])**2 +
                                (preTags['y'] - postTags['y'])**2 + 
                                (preTags['z'] - postTags['z'])**2)
        dictVars['dist_2D']     = lambda preTags,postTags: sqrt((preTags['x'] - postTags['x'])**2 +
                                (preTags['z'] - postTags['z'])**2)
        dictVars['dist_xnorm']  = lambda preTags,postTags: abs(preTags['xnorm'] - postTags['xnorm'])
        dictVars['dist_ynorm']  = lambda preTags,postTags: abs(preTags['ynorm'] - postTags['ynorm']) 
        dictVars['dist_znorm']  = lambda preTags,postTags: abs(preTags['znorm'] - postTags['znorm'])
        dictVars['dist_norm3D'] = lambda preTags,postTags: sqrt((preTags['xnorm'] - postTags['xnorm'])**2 +
                                sqrt(preTags['ynorm'] - postTags['ynorm']) + 
                                sqrt(preTags['znorm'] - postTags['znorm']))
        dictVars['dist_norm2D'] = lambda preTags,postTags: sqrt((preTags['xnorm'] - postTags['xnorm'])**2 +
                                sqrt(preTags['znorm'] - postTags['znorm']))
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
            seed(f.sim.id32('%d'%(f.cfg['randseed'])))

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
                # store lambda function and func vars in connParam (for weight and delay, since only calcualted for certain conns)
                connParam[paramStrFunc+'Func'] = lambdaFunc
                connParam[paramStrFunc+'FuncVars'] = {strVar: dictVars[strVar] for strVar in strVars} 
                

    ###############################################################################
    ### Full connectivity
    ###############################################################################
    def fullConn(self, preCellsTags, postCellsTags, connParam):
        ''' Generates connections between all pre and post-syn cells '''
        if f.cfg['verbose']: print 'Generating set of all-to-all connections...'

        # list of params that can have a lambda function
        paramsStrFunc = [param for param in ['weightFunc', 'delayFunc'] if param in connParam] 
        for paramStrFunc in paramsStrFunc:
            # replace lambda function (with args as dict of lambda funcs) with list of values
            seed(f.sim.id32('%d'%(f.cfg['randseed']+preCellsTags.keys()[0]+postCellsTags.keys()[0])))
            connParam[paramStrFunc] = {(preGid,postGid): connParam[paramStrFunc](**{k:v if isinstance(v, Number) else v(preCellTags,postCellTags) for k,v in connParam[paramStrFunc+'Vars'].iteritems()})  
                    for preGid,preCellTags in preCellsTags.iteritems() for postGid,postCellTags in postCellsTags.iteritems()}
         
        for postCellGid in postCellsTags:  # for each postsyn cell
            if postCellGid in f.net.lid2gid:  # check if postsyn is in this node's list of gids
                postCell = f.net.cells[f.net.gid2lid[postCellGid]]  # get Cell object 
                for preCellGid, preCellTags in preCellsTags.iteritems():  # for each presyn cell
                    if preCellTags['cellModel'] == 'NetStim':  # if NetStim
                        params = {'popLabel': preCellTags['popLabel'],
                        'rate': preCellTags['rate'],
                        'noise': preCellTags['noise'],
                        'source': preCellTags['source'], 
                        'number': preCellTags['number'],
                        'sec': connParam['sec'], 
                        'synMech': connParam['synMech'], 
                        'weight': connParam['weightFunc'][preCellGid,postCellGid] if 'weightFunc' in connParam else connParam['weight'],
                        'delay': connParam['delayFunc'][preCellGid,postCellGid] if 'delayFunc' in connParam else connParam['delay'],
                        'threshold': connParam['threshold']}
                        postCell.addStim(params)  # call cell method to add connections              
                    elif preCellGid != postCellGid:
                        # if not self-connection
                        params = {'preGid': preCellGid, 
                        'sec': connParam['sec'], 
                        'synMech': connParam['synMech'], 
                        'weight': connParam['weightFunc'][preCellGid,postCellGid] if 'weightFunc' in connParam else connParam['weight'],
                        'delay': connParam['delayFunc'][preCellGid,postCellGid] if 'delayFunc' in connParam else connParam['delay'],
                        'threshold': connParam['threshold'],
                        'plasticity': connParam.get('plasticity')}
                        postCell.addConn(params)  # call cell method to add connections



    ###############################################################################
    ### Probabilistic connectivity 
    ###############################################################################
    def probConn(self, preCellsTags, postCellsTags, connParam):
        ''' Generates connections between all pre and post-syn cells based on probability values'''
        if f.cfg['verbose']: print 'Generating set of probabilistic connections...'

        seed(f.sim.id32('%d'%(f.cfg['randseed']+preCellsTags.keys()[0]+postCellsTags.keys()[0])))  
        allRands = {(preGid,postGid): random() for preGid in preCellsTags for postGid in postCellsTags}  # Create an array of random numbers for checking each connection

        for postCellGid,postCellTags in postCellsTags.iteritems():  # for each postsyn cell
            if postCellGid in f.net.lid2gid:  # check if postsyn is in this node
                postCell = f.net.cells[f.net.gid2lid[postCellGid]]  # get Cell object
                for preCellGid, preCellTags in preCellsTags.iteritems():  # for each presyn cell
                    probability = connParam['probabilityFunc'][preCellGid,postCellGid] if 'probabilityFunc' in connParam else connParam['probability']
                    if 'weightFunc' in connParam: 
                        weightVars = {k:v if isinstance(v, Number) else v(preCellTags,postCellTags) for k,v in connParam['weightFuncVars'].iteritems()}  # call lambda functions to get weight func args
                    if 'delayFunc' in connParam: 
                        delayVars = {k:v if isinstance(v, Number) else v(preCellTags,postCellTags) for k,v in connParam['delayFuncVars'].iteritems()}  # call lambda functions to get delay func args
                    if probability >= allRands[preCellGid,postCellGid]:
                        seed(f.sim.id32('%d'%(f.cfg['randseed']+postCellGid+preCellGid)))  
                        if preCellTags['cellModel'] == 'NetStim':  # if NetStim
                            params = {'popLabel': preCellTags['popLabel'],
                                    'rate': preCellTags['rate'],
                                    'noise': preCellTags['noise'],
                                    'source': preCellTags['source'], 
                                    'number': preCellTags['number'],
                                    'sec': connParam['sec'], 
                                    'synMech': connParam['synMech'], 
                                    'weight': connParam['weightFunc'](**weightVars) if 'weightFunc' in connParam else connParam['weight'],
                                    'delay': connParam['delayFunc'](**delayVars) if 'delayFunc' in connParam else connParam['delay'], 
                                    'threshold': connParam['threshold']}
                            postCell.addStim(params)  # call cell method to add connections              
                        elif preCellGid != postCellGid:
                            # if not self-connection
                            params = {'preGid': preCellGid, 
                                    'sec': connParam['sec'], 
                                    'synMech': connParam['synMech'], 
                                    'weight': connParam['weightFunc'](**weightVars) if 'weightFunc' in connParam else connParam['weight'],
                                    'delay': connParam['delayFunc'](**delayVars) if 'delayFunc' in connParam else connParam['delay'], 
                                    'threshold': connParam['threshold'],
                                    'plasticity': connParam.get('plasticity')}
                            postCell.addConn(params)  # call cell method to add connections
       


    ###############################################################################
    ### Convergent connectivity 
    ###############################################################################
    def convConn(self, preCellsTags, postCellsTags, connParam):
        ''' Generates connections between all pre and post-syn cells based on probability values'''
        if f.cfg['verbose']: print 'Generating set of convergent connections...'
               
        for postCellGid,postCellTags in postCellsTags.iteritems():  # for each postsyn cell
            if postCellGid in f.net.lid2gid:  # check if postsyn is in this node
                postCell = f.net.cells[f.net.gid2lid[postCellGid]]  # get Cell object
                convergence = connParam['convergenceFunc'][postCellGid] if 'convergenceFunc' in connParam else connParam['convergence']  # num of presyn conns / postsyn cell
                convergence = max(min(int(round(convergence)), len(preCellsTags)), 0)
                seed(f.sim.id32('%d'%(f.cfg['randseed']+postCellGid)))  
                preCellsSample = sample(preCellsTags.keys(), convergence)  # selected gids of presyn cells
                preCellsConv = {k:v for k,v in preCellsTags.iteritems() if k in preCellsSample}  # dict of selected presyn cells tags
                for preCellGid, preCellTags in preCellsConv.iteritems():  # for each presyn cell
                    if 'weightFunc' in connParam:
                        weightVars = {k:v if isinstance(v, Number) else v(preCellTags,postCellTags) for k,v in connParam['weightFuncVars'].iteritems()}  # call lambda functions to get weight func args
                    if 'delayFunc' in connParam: 
                        delayVars = {k:v if isinstance(v, Number) else v(preCellTags, postCellTags) for k,v in connParam['delayFuncVars'].iteritems()}  # call lambda functions to get delay func args
                    seed(f.sim.id32('%d'%(f.cfg['randseed']+postCellGid+preCellGid)))  
                    if preCellTags['cellModel'] == 'NetStim':  # if NetStim
                        print 'Error: Convergent connectivity for NetStims is not implemented'
                    elif preCellGid != postCellGid: # if not self-connection
                        params = {'preGid': preCellGid, 
                                'sec': connParam['sec'], 
                                'synMech': connParam['synMech'], 
                                'weight': connParam['weightFunc'](**weightVars) if 'weightFunc' in connParam else connParam['weight'],
                                'delay': connParam['delayFunc'](**delayVars) if 'delayFunc' in connParam else connParam['delay'], 
                                'threshold': connParam['threshold'],
                                'plasticity': connParam.get('plasticity')}
                        postCell.addConn(params)  # call cell method to add connections


    ###############################################################################
    ### Divergent connectivity 
    ###############################################################################
    def divConn(self, preCellsTags, postCellsTags, connParam):
        ''' Generates connections between all pre and post-syn cells based on probability values'''
        if f.cfg['verbose']: print 'Generating set of divergent connections...'
         
        for preCellGid, preCellTags in preCellsTags.iteritems():  # for each presyn cell
            divergence = connParam['divergenceFunc'][preCellGid] if 'divergenceFunc' in connParam else connParam['divergence']  # num of presyn conns / postsyn cell
            divergence = max(min(int(round(divergence)), len(postCellsTags)), 0)
            seed(f.sim.id32('%d'%(f.cfg['randseed']+preCellGid)))  
            postCellsSample = sample(postCellsTags, divergence)  # selected gids of postsyn cells
            postCellsDiv = {postGid:postTags  for postGid,postTags in postCellsTags.iteritems() if postGid in postCellsSample and postGid in f.net.lid2gid}  # dict of selected postsyn cells tags
            for postCellGid, postCellTags in postCellsDiv.iteritems():  # for each postsyn cell
                postCell = f.net.cells[f.net.gid2lid[postCellGid]]
                if 'weightFunc' in connParam:
                    weightVars = {k:v if isinstance(v, Number) else v(preCellTags,postCellTags) for k,v in connParam['weightFuncVars'].iteritems()}  # call lambda functions to get weight func args
                if 'delayFunc' in connParam: 
                    delayVars = {k:v if isinstance(v, Number) else v(preCellTags, postCellTags) for k,v in connParam['delayFuncVars'].iteritems()}  # call lambda functions to get delay func args
                seed(f.sim.id32('%d'%(f.cfg['randseed']+postCellGid+preCellGid)))  
                if preCellTags['cellModel'] == 'NetStim':  # if NetStim
                    print 'Error: Divergent connectivity for NetStims is not implemented'           
                elif preCellGid != postCellGid: # if not self-connection
                    params = {'preGid': preCellGid, 
                            'sec': connParam['sec'], 
                            'synMech': connParam['synMech'], 
                            'weight': connParam['weightFunc'](**weightVars) if 'weightFunc' in connParam else connParam['weight'],
                            'delay': connParam['delayFunc'](**delayVars) if 'delayFunc' in connParam else connParam['delay'], 
                            'threshold': connParam['threshold'],
                            'plasticity': connParam.get('plasticity')}
                    postCell.addConn(params)  # call cell method to add connections
                    
                    
    

    ###############################################################################
    ### Get connection centric network representation as used in NeuroML2
    ###############################################################################  
    def _convertNetworkRepresentation(self,gids_vs_pop_indices):
        
        nn = {}
        
        for np_pop in self.pops: 
            print("Adding conns for: %s"%np_pop.tags)
            if not np_pop.tags['cellModel'] ==  'NetStim':
                for cell in self.cells:
                    if cell.gid in np_pop.cellGids:
                        popPost, indexPost = gids_vs_pop_indices[cell.gid]
                        print("Cell %s: %s\n    %s[%i]\n"%(cell.gid,cell.tags,popPost, indexPost))
                        for conn in cell.conns:
                            preGid = conn['preGid']
                            popPre, indexPre = gids_vs_pop_indices[preGid]
                            loc = conn['loc']
                            weight = conn['weight']
                            delay = conn['delay']
                            sec = conn['sec']
                            synMech = conn['synMech']
                            threshold = conn['threshold']

                            print("      Conn %s[%i]->%s[%i] with %s"%(popPre, indexPre,popPost, indexPost, synMech))
                            
                            projection_info = (popPre,popPost,synMech)
                            if not projection_info in nn.keys():
                                nn[projection_info] = []
                            
                            nn[projection_info].append({'indexPre':indexPre,'indexPost':indexPost,'weight':weight,'delay':delay})
        return nn                 
    

    ###############################################################################
    ### Get stimulations in representation as used in NeuroML2
    ###############################################################################  
    def _convertStimulationRepresentation(self,gids_vs_pop_indices, nml_doc):
        
        stims = {}
        
        for np_pop in self.pops: 
            if not np_pop.tags['cellModel'] ==  'NetStim':
                print("Adding stims for: %s"%np_pop.tags)
                for cell in self.cells:
                    if cell.gid in np_pop.cellGids:
                        pop, index = gids_vs_pop_indices[cell.gid]
                        print("    Cell %s: %s\n    %s[%i]\n    %s\n"%(cell.gid,cell.tags,pop, index,cell.stims))
                        for stim in cell.stims:
                            '''
                            [{'noise': 0, 'weight': 0.1, 'popLabel': 'background', 'number': 1000000000000.0, 'rate': 10, 
                            'sec': 'soma', 'synMech': 'NMDA', 'threshold': 10.0, 'weightIndex': 0, 'loc': 0.5, 
                            'hRandom': <hoc.HocObject object at 0x7fda27f1fd20>, 'hNetcon': <hoc.HocObject object at 0x7fda27f1fdb0>, 
                            'hNetStim': <hoc.HocObject object at 0x7fda27f1fd68>, 'delay': 0, 'source': 'random'}]'''
                            ref = stim['popLabel']
                            rate = stim['rate']
                            synMech = stim['synMech']
                            threshold = stim['threshold']
                            delay = stim['delay']
                            weight = stim['weight']
                            noise = stim['noise']
                            
                            name_stim = 'NetStim_%s_%s_%s_%s'%(ref,rate,noise,synMech)
                            
                            stim_info = (name_stim, pop, rate, noise,synMech)
                            if not stim_info in stims.keys():
                                stims[stim_info] = []
                                    
                             
                            stims[stim_info].append({'index':index,'weight':weight,'delay':delay,'threshold':threshold})   
                                
        print stims             
        return stims
    
    
    ###############################################################################
    ### Export synapses to NeuroML2
    ############################################################################### 
    def _export_synapses(self, nml_doc):
        
        import neuroml
        
        for syn in f.net.params['synMechParams']:

            print('Exporting details of syn: %s'%syn)
            if syn['mod'] == 'Exp2Syn':
                syn0 = neuroml.ExpTwoSynapse(id=syn['label'], 
                                             gbase='1nS',
                                             erev='%smV'%syn['e'],
                                             tau_rise='%sms'%syn['tau1'],
                                             tau_decay='%sms'%syn['tau2'])

                nml_doc.exp_two_synapses.append(syn0)
            elif syn['mod'] == 'ExpSyn':
                syn0 = neuroml.ExpOneSynapse(id=syn['label'], 
                                             gbase='1nS',
                                             erev='%smV'%syn['e'],
                                             tau_decay='%sms'%syn['tau'])

                nml_doc.exp_one_synapses.append(syn0)
            else:
                raise Exception("Cannot yet export synapse type: %s"%syn['mod'])
                
        

    ###############################################################################
    ### Export generated structure of network to NeuroML 2 
    ###############################################################################         
    def exportNeuroML2(self, reference, connections=True, stimulations=True):

        print("Exporting network to NeuroML 2, reference: %s"%reference)
        # Only import libNeuroML if this method is called...
        import neuroml
        import neuroml.writers as writers

        nml_doc = neuroml.NeuroMLDocument(id='%s'%reference)
        net = neuroml.Network(id='%s'%reference)
        nml_doc.networks.append(net)

        nml_doc.notes = 'NeuroML 2 file exported from NetPyNE'
        
        gids_vs_pop_indices ={}
        populations_vs_components = {}

        for np_pop in self.pops: 
            index = 0
            print("Adding: %s"%np_pop.tags)
            positioned = len(np_pop.cellGids)>0
            type = 'populationList'
            if not np_pop.tags['cellModel'] ==  'NetStim':
                pop = neuroml.Population(id=np_pop.tags['popLabel'],component=np_pop.tags['cellModel'], type=type)
                populations_vs_components[pop.id]=pop.component
                net.populations.append(pop)
                nml_doc.includes.append(neuroml.IncludeType('%s.cell.nml'%np_pop.tags['cellModel']))

                for cell in self.cells:
                    if cell.gid in np_pop.cellGids:
                        gids_vs_pop_indices[cell.gid] = (np_pop.tags['popLabel'],index)
                        inst = neuroml.Instance(id=index)
                        index+=1
                        pop.instances.append(inst)
                        inst.location = neuroml.Location(cell.tags['x'],cell.tags['y'],cell.tags['z'])
                        
        self._export_synapses(nml_doc)
            
        if connections:
            nn = self._convertNetworkRepresentation(gids_vs_pop_indices)

            for proj_info in nn.keys():

                prefix = "NetConn"
                popPre,popPost,synMech = proj_info

                projection = neuroml.Projection(id="%s_%s_%s_%s"%(prefix,popPre, popPost,synMech), 
                                  presynaptic_population=popPre, 
                                  postsynaptic_population=popPost, 
                                  synapse=synMech)
                index = 0      
                for conn in nn[proj_info]:

                    connection = neuroml.ConnectionWD(id=index, \
                                pre_cell_id="../%s/%i/%s"%(popPre, conn['indexPre'], populations_vs_components[popPre]), \
                                pre_segment_id=0, \
                                pre_fraction_along=0.5,
                                post_cell_id="../%s/%i/%s"%(popPost, conn['indexPost'], populations_vs_components[popPost]), \
                                post_segment_id=0,
                                post_fraction_along=0.5,
                                delay = '%s ms'%conn['delay'],
                                weight = conn['weight'])
                    index+=1

                    projection.connection_wds.append(connection)

                net.projections.append(projection)
        
        if stimulations:
            stims = self._convertStimulationRepresentation(gids_vs_pop_indices, nml_doc)
            
            for stim_info in stims.keys():
                name_stim, pop, rate, noise, synMech = stim_info
                
                print("Adding stim: %s"%name_stim)
                
                if noise==0:
                    source = neuroml.SpikeGenerator(id=name_stim,period="%ss"%(1./rate))
                    nml_doc.spike_generators.append(source)
                else:
                    raise Exception("Noise = %s is not yet supported!"%noise)
                    
                
                pop = neuroml.Population(id=name_stim,component=source.id,size=len(stims[stim_info]))
                net.populations.append(pop)
                
                
                proj = neuroml.Projection(id="NetConn_%s_%s"%(name_stim, pop.id), 
                      presynaptic_population=name_stim, 
                      postsynaptic_population=pop.id, 
                      synapse=synMech)
                      
                net.projections.append(proj)
                
                for stim in stims[stim_info]:
                    print("  Adding stim: %s"%stim)
            

        nml_file_name = '%s.net.nml'%reference

        writers.NeuroMLWriter.write(nml_doc, nml_file_name)
        
        '''
        from pyneuroml.lems import LEMSSimulation
         
        ls = LEMSSimulation('Sim_%s'%reference, f.cfg['dt'],f.cfg['duration'],reference)
        
        ls.include_neuroml2_file(nml_file_name)'''
        
        import pyneuroml.lems
        
        pyneuroml.lems.generate_lems_file_for_neuroml("Sim_%s"%reference, 
                                   nml_file_name, 
                                   reference, 
                                   f.cfg['duration'], 
                                   f.cfg['dt'], 
                                   'LEMS_%s.xml'%reference,
                                   '.',
                                   copy_neuroml = False,
                                   include_extra_files = [],
                                   gen_plots_for_all_v = True,
                                   plot_all_segments = False, 
                                   gen_saves_for_all_v = True,
                                   save_all_segments = False,
                                   seed=1234)
        


   

