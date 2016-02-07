
"""
network.py 

Defines Network class which contains cell objects and network-realated methods

Contributors: salvadordura@gmail.com
"""

from pylab import array, sin, cos, tan, exp, sqrt, mean, inf, rand
from random import seed, random, randint, sample, uniform, triangular, gauss, betavariate, expovariate, gammavariate
from time import time
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
    

    ###############################################################################
    # Connect Cells
    ###############################################################################
    def connectCells(self):
        # Instantiate network connections based on the connectivity rules defined in params
        if f.rank==0: print('Making connections...'); connstart = time()

        if f.nhosts > 1: # Gather tags from all cells 
            allCellTags = f.sim.gatherAllCellTags()  
        else:
            allCellTags = {cell.gid: cell.tags for cell in self.cells}
        allPopTags = {i: pop.tags for i,pop in enumerate(self.pops)}  # gather tags from pops so can connect NetStim pops

        for connParam in self.params['connParams']:  # for each conn rule or parameter set
            if 'sec' not in connParam: connParam['sec'] = None  # if section not specified, make None (will be assigned to first section in cell)
            if 'synReceptor' not in connParam: connParam['synReceptor'] = None  # if section not specified, make None (will be assigned to first synapse in cell)  
            if 'threshold' not in connParam: connParam['threshold'] = None  # if section not specified, make None (will be assigned to first synapse in cell)    
            
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
    

    ###############################################################################
    # Convert string to function
    ###############################################################################
    def strToFunc(self, preCellsTags, postCells, connParam):
        paramsStrFunc = [param for param in ['delay', 'weight', 'probability', 'convergence', 'divergence'] if param in connParam and isinstance(connParam[param], str)]  # list of params that have a function passed in as a string
        
        # list of spatial variables allowed in function -- needs to be ordered with longest 1st since strings overlap
        allFuncVars = ['pre_xnorm', 'pre_ynorm', 'pre_znorm', 'pre_x', 'pre_y', 'pre_z',
                    'post_xnorm', 'post_ynorm', 'post_znorm', 'post_x', 'post_y', 'post_z', 
                    'dist_xznorm', 'post_xyznorm', 'dist_xz', 'dist_xyz',
                    'dist_xnorm', 'dist_ynorm', 'dist_znorm', 'dist_x', 'dist_y', 'dist_z']  

        # dict to store correspondence between string and actual variable
        dictVars = {}  
        dictVars['pre_x'] = lambda: preCellTags['x'] 
        dictVars['pre_y'] = lambda: preCellTags['y'] 
        dictVars['pre_z'] = lambda: preCellTags['z'] 
        dictVars['pre_xnorm'] = lambda: preCellTags['xnorm'] 
        dictVars['pre_ynorm'] = lambda: preCellTags['ynorm'] 
        dictVars['pre_znorm'] = lambda: preCellTags['znorm'] 
        dictVars['post_x'] = lambda: postCell.tags['x'] 
        dictVars['post_y'] = lambda: postCell.tags['y'] 
        dictVars['post_z'] = lambda: postCell.tags['z'] 
        dictVars['post_xnorm'] = lambda: postCell['tags']['xnorm'] 
        dictVars['post_ynorm'] = lambda: postCell['tags']['ynorm'] 
        dictVars['post_znorm'] = lambda: postCell['tags']['znorm'] 
        dictVars['dist_x'] = lambda: abs(preCellTags['x'] - postCell.tags['x'])
        dictVars['dist_y'] = lambda: abs(preCellTags['y'] - postCell.tags['y']) 
        dictVars['dist_z'] = lambda: abs(preCellTags['z'] - postCell.tags['z'])
        dictVars['dist_xyz'] = lambda: sqrt((preCellTags['x'] - postCell.tags['x'])**2 +
            (preCellTags['y'] - postCell.tags['y'])**2 + 
            (preCellTags['z'] - postCell.tags['z'])**2)
        dictVars['dist_xz'] = lambda: sqrt((preCellTags['x'] - postCell.tags['x'])**2 +
            (preCellTags['z'] - postCell.tags['z'])**2)
        dictVars['dist_xnorm'] = lambda: abs(preCellTags['xnorm'] - postCell.tags['xnorm'])
        dictVars['dist_ynorm'] = lambda: abs(preCellTags['ynorm'] - postCell.tags['ynorm']) 
        dictVars['dist_znorm'] = lambda: abs(preCellTags['znorm'] - postCell.tags['znorm'])
        dictVars['dist_xyznorm'] = lambda: sqrt((preCellTags['x'] - postCell.tags['x'])**2 +
            sqrt(preCellTags['y'] - postCell.tags['y']) + 
            sqrt(preCellTags['z'] - postCell.tags['z']))
        dictVars['dist_xznorm'] = lambda: sqrt((preCellTags['x'] - postCell.tags['x'])**2 +
            sqrt(preCellTags['z'] - postCell.tags['z']))

        # for each parameter containing a function
        for paramStrFunc in paramsStrFunc:
            strFunc = connParam[paramStrFunc]  # string containing function
            strVars = [var for var in allFuncVars if var in strFunc]  # get list of variables used (eg. post_ynorm or dist_xyz)
            lambdaStr = 'lambda ' + ','.join(strVars) +': ' + strFunc # convert to lambda function 
            lambdaFunc = eval(lambdaStr)
       
             # initialize randomizer in case used in function
            seed(f.sim.id32('%d'%(f.cfg['randseed']+postCells.keys()[0]+preCellsTags.keys()[0])))

            if paramStrFunc in ['probability', 'delay', 'weight']:
                # replace function with list of values derived from function (one per pre+post cell)
                connParam[paramStrFunc] = [lambdaFunc(**{strVar: dictVars[strVar]() for strVar in strVars})  
                    for preCellTags in preCellsTags.values() for postCell in postCells.values()]

            elif paramStrFunc in ['convergence']:
                # replace function with list of values derived from function (one per post cell)
                connParam[paramStrFunc] = [lambdaFunc(**{strVar: dictVars[strVar]() for strVar in strVars}) 
                    for postCell in postCells.values()]

            elif paramStrFunc in ['divergence']:
                # replace function with list of values derived from function (one per post cell)
                connParam[paramStrFunc] = [lambdaFunc(**{strVar: dictVars[strVar]() for strVar in strVars}) 
                    for preCellTags in preCellsTags.values()]

    ###############################################################################
    ### Full connectivity
    ###############################################################################
    def fullConn(self, preCellsTags, postCells, connParam):
        ''' Generates connections between all pre and post-syn cells '''

        for postCellGid, postCell in postCells.iteritems():  # for each postsyn cell
            for preCellGid, preCellTags in preCellsTags.iteritems():  # for each presyn cell
                if preCellTags['cellModel'] == 'NetStim':  # if NetStim
                    if not 'number' in preCellTags: preCellTags['number'] = 1e12
                    params = {'popLabel': preCellTags['popLabel'],
                    'rate': preCellTags['rate'],
                    'noise': preCellTags['noise'],
                    'source': preCellTags['source'], 
                    'number': preCellTags['number'],
                    'sec': connParam['sec'], 
                    'synReceptor': connParam['synReceptor'], 
                    'weight': connParam['weight'], 
                    'delay': connParam['delay'], 
                    'threshold': connParam['threshold']}
                    postCell.addStim(params)  # call cell method to add connections              
                elif preCellGid != postCellGid:
                    # if not self-connection
                    params = {'preGid': preCellGid, 
                    'sec': connParam['sec'], 
                    'synReceptor': connParam['synReceptor'], 
                    'weight': connParam['weight'].pop(0) if isinstance(connParam['weight'],list) else connParam['weight'],
                    'delay': connParam['delay'].pop(0) if isinstance(connParam['delay'],list) else connParam['delay'],
                    'threshold': connParam['threshold']}
                    postCell.addConn(params)  # call cell method to add connections



    ###############################################################################
    ### Probabilistic connectivity 
    ###############################################################################
    def probConn(self, preCellsTags, postCells, connParam):
        ''' Generates connections between all pre and post-syn cells based on probability values'''
        seed(f.sim.id32('%d'%(f.cfg['randseed']+postCells.keys()[0]+preCellsTags.keys()[0])))  
        allRands = [random() for i in range(len(preCellsTags)*len(postCells))]  # Create an array of random numbers for checking each connection
        probsList = True if isinstance(connParam['probability'], list) else False
        weightsList = True if isinstance(connParam['weight'], list) else False
        delaysList = True if isinstance(connParam['delays'], list) else False
        for postCellGid, postCell in postCells.iteritems():  # for each postsyn cell
            for preCellGid, preCellTags in preCellsTags.iteritems():  # for each presyn cell
                probability = connParam['probability'].pop(0) if probsList else connParam['probability']
                weight = connParam['weight'].pop(0) if weightsList else connParam['weight']
                delay = connParam['delay'].pop(0) if delaysList else connParam['delay']
                if probability >= allRands.pop():
                    if preCellTags['cellModel'] == 'NetStim':  # if NetStim
                        if not 'number' in preCellTags: preCellTags['number'] = 1e12
                        params = {'popLabel': preCellTags['popLabel'],
                        'rate': preCellTags['rate'],
                        'noise': preCellTags['noise'],
                        'source': preCellTags['source'], 
                        'number': preCellTags['number'],
                        'sec': connParam['sec'], 
                        'synReceptor': connParam['synReceptor'], 
                        'weight': weight, 
                        'delay': delay, 
                        'threshold': connParam['threshold']}
                        postCell.addStim(params)  # call cell method to add connections              
                    elif preCellGid != postCellGid:
                        # if not self-connection
                        params = {'preGid': preCellGid, 
                        'sec': connParam['sec'], 
                        'synReceptor': connParam['synReceptor'], 
                        'weight': weight,
                        'delay': delay,
                        'threshold': connParam['threshold']}
                        postCell.addConn(params)  # call cell method to add connections
       


    ###############################################################################
    ### Convergent connectivity 
    ###############################################################################
    def convConn(self, preCellsTags, postCells, connParam):
        ''' Generates connections between all pre and post-syn cells based on probability values'''
        seed(f.sim.id32('%d'%(f.cfg['randseed']+postCells.keys()[0]+preCellsTags.keys()[0])))  
        convsList = True if isinstance(connParam['convergence'], list) else False
        weightsList = True if isinstance(connParam['weight'], list) else False
        delaysList = True if isinstance(connParam['delays'], list) else False
        for postCellGid, postCell in postCells.iteritems():  # for each postsyn cell
            convergence = connParam['convergence'].pop(0) if convsList else connParam['convergence']  # num of presyn conns / postsyn cell
            preCellsSample = sample(preCellsTags.keys(), convergence)  # selected gids of presyn cells
            preCellsConv = {k:v for k,v in preCellsTags.iteritems() if k in preCellsSample}  # dict of selected presyn cells tags
            for preCellGid, preCellTags in preCellsTags.iteritems():  # for each presyn cell
                weight = connParam['weight'].pop(0) if weightsList else connParam['weight']
                delay = connParam['delay'].pop(0) if delaysList else connParam['delay']
                for preCellGid, preCellTags in preCellsConv:  # for each presyn cell
                    if preCellTags['cellModel'] == 'NetStim':  # if NetStim
                        if not 'number' in preCellTags: preCellTags['number'] = 1e12
                        params = {'popLabel': preCellTags['popLabel'],
                        'rate': preCellTags['rate'],
                        'noise': preCellTags['noise'],
                        'source': preCellTags['source'], 
                        'number': preCellTags['number'],
                        'sec': connParam['sec'], 
                        'synReceptor': connParam['synReceptor'], 
                        'weight': weight, 
                        'delay': delay, 
                        'threshold': connParam['threshold']}
                        postCell.addStim(params)  # call cell method to add connections              
                    elif preCellGid != postCellGid:
                        # if not self-connection
                        params = {'preGid': preCellGid, 
                        'sec': connParam['sec'], 
                        'synReceptor': connParam['synReceptor'], 
                        'weight': weight,
                        'delay': delay,
                        'threshold': connParam['threshold']}
                        postCell.addConn(params)  # call cell method to add connections
       

   #  ###############################################################################
   #  # Connect Cells
   #  ###############################################################################
   #  def connectCells(self):
   #      # Instantiate network connections based on the connectivity rules defined in params
   #      if f.rank==0: print('Making connections...'); connstart = time()

   #      if f.nhosts > 1: # Gather tags from all cells 
   #          allCellTags = f.sim.gatherAllCellTags()  
   #      else:
   #          allCellTags = {cell.gid: cell.tags for cell in self.cells}
   #      allPopTags = {i: pop.tags for i,pop in enumerate(self.pops)}  # gather tags from pops so can connect NetStim pops

   #      for connParam in self.params['connParams']:  # for each conn rule or parameter set
   #          if 'sec' not in connParam: connParam['sec'] = None  # if section not specified, make None (will be assigned to first section in cell)
   #          if 'synReceptor' not in connParam: connParam['synReceptor'] = None  # if section not specified, make None (will be assigned to first synapse in cell)  
   #          if 'threshold' not in connParam: connParam['threshold'] = None  # if section not specified, make None (will be assigned to first synapse in cell)    
            
   #          preCells = allCellTags  # initialize with all presyn cells 
   #          prePops = allPopTags  # initialize with all presyn pops
   #          for condKey,condValue in connParam['preTags'].iteritems():  # Find subset of cells that match presyn criteria
   #              if condKey == 'ynorm':
   #                  preCells = {gid: tags for (gid,tags) in preCells.iteritems() if condValue[0] <= tags[condKey] < condValue[1]}  # dict with pre cell tags
   #                  prePops = {}
   #              else:
   #                  preCells = {gid: tags for (gid,tags) in preCells.iteritems() if tags[condKey] in condValue}  # dict with pre cell tags
   #                  prePops = {i: tags for (i,tags) in prePops.iteritems() if (condKey in tags) and (tags[condKey] in condValue)}

   #          if not preCells: # if no presyn cells, check if netstim
   #              if any (prePopTags['cellModel'] == 'NetStim' for prePopTags in prePops.values()):
   #                  preCells = prePops
            
   #          postCells = {cell.gid:cell for cell in self.cells}
   #          for condKey,condValue in connParam['postTags'].iteritems():  # Find subset of cells that match postsyn criteria
   #              if condKey == 'ynorm':
   #                  postCells = {gid: cell for (gid,cell) in postCells.iteritems() if condValue[0] <= cell.tags[condKey] < condValue[1]}  # dict with post Cell objects}  # dict with pre cell tags
   #              else:
   #                  postCells = {gid: cell for (gid,cell) in postCells.iteritems() if cell.tags[condKey] in condValue}  # dict with post Cell objects

   #          connFunc = getattr(self, connParam['connFunc'])  # get function name from params
   #          if preCells and postCells:
   #              connFunc(preCells, postCells, connParam)  # call specific conn function
       

   # ###############################################################################
   #  ### Full connectivity
   #  ###############################################################################
   #  def fullConn(self, preCells, postCells, connParam):
   #      ''' Generates connections between all pre and post-syn cells '''
   #      if all (k in connParam for k in ('delayMean', 'delayVar')):  # generate list of delays based on mean and variance
   #          seed(f.sim.id32('%d'%(f.cfg['randseed']+postCells.keys()[0])))  # Reset random number generator  
   #          randDelays = [gauss(connParam['delayMean'], connParam['delayVar']) for pre in range(len(preCells)*len(postCells))]  # select random delays based on mean and var params    
   #      else:
   #          randDelays = None   
   #          delay = connParam['delay']  # fixed delay
   #      for postCellGid, postCell in postCells.iteritems():  # for each postsyn cell
   #          for preCellGid,preCellTags in preCells.iteritems():  # for each presyn cell
   #              if preCellTags['cellModel'] == 'NetStim':  # if NetStim
   #                  if not 'number' in preCellTags: preCellTags['number'] = 1e12
   #                  params = {'popLabel': preCellTags['popLabel'],
   #                  'rate': preCellTags['rate'],
   #                  'noise': preCellTags['noise'],
   #                  'source': preCellTags['source'], 
   #                  'number': preCellTags['number'],
   #                  'sec': connParam['sec'], 
   #                  'synReceptor': connParam['synReceptor'], 
   #                  'weight': connParam['weight'], 
   #                  'delay': delay, 
   #                  'threshold': connParam['threshold']}
   #                  postCell.addStim(params)  # call cell method to add connections              
   #              elif preCellGid != postCellGid:
   #                  if randDelays:  delay = randDelays.pop()  # set random delay
   #                  # if not self-connection
   #                  params = {'preGid': preCellGid, 
   #                  'sec': connParam['sec'], 
   #                  'synReceptor': connParam['synReceptor'], 
   #                  'weight': connParam['weight'], 
   #                  'delay': delay, 
   #                  'threshold': connParam['threshold']}
   #                  postCell.addConn(params)  # call cell method to add connections


     
   #  ###############################################################################
   #  ### Random connectivity
   #  ###############################################################################
   #  def randConn(self, preCells, postCells, connParam):
   #      ''' Generates connections between  maxcons random pre and postsyn cells'''
   #      if 'maxConns' not in connParam: connParam['maxConns'] = len(preCells)
   #      if all (k in connParam for k in ('delayMean', 'delayVar')):  # generate list of delays based on mean and variance
   #          seed(f.sim.id32('%d'%(f.cfg['randseed']+postCells.keys()[0])))  # Reset random number generator  
   #          randDelays = [gauss(connParam['delayMean'], connParam['delayVar']) for pre in range(connParam['maxConns']*len(postCells))] # select random delays based on mean and var params    
   #      else:
   #          randDelays = None   
   #          delay = connParam['delay']  # fixed delay
   #      for postCellGid, postCell in postCells.iteritems():  # for each postsyn cell
   #          preCellGids = preCells.keys()
   #          if postCellGid in preCellGids: preCellGids.remove(postCellGid)
   #          seed(f.sim.id32('%d'%(f.cfg['randseed']+postCellGid))) 
   #          randPreCellGids = sample(preCellGids, randint(0, min(connParam['maxConns'], len(preCellGids)))) # select random subset of pre cells
   #          for randPreCellGid in randPreCellGids: # for each presyn cell
   #              if randDelays:  delay = randDelays.pop()  # set random delay
   #              params = {'preGid': randPreCellGid, 
   #              'sec': connParam['sec'], 
   #              'synReceptor': connParam['synReceptor'], 
   #              'weight': connParam['weight'], 'delay': delay, 
   #              'threshold': connParam['threshold']}
   #              postCell.addConn(params)  # call cell method to add connections



   #  ###############################################################################
   #  ### Probabilistic connectivity (option for distance-dep and ynorm-dep weight+prob)
   #  ###############################################################################
   #  def probConn(self, preCells, postCells, connParam):
   #      ''' Calculate connectivity as a func of preCell.topClass, preCell['ynorm'], postCell.topClass, postCell.tags['ynorm']
   #          preCells = {gid: tags} 
   #          postCells = {gid: Cell object}
   #          '''
   #      for postCell in postCells.values():
   #          if 'lengthConst' in connParam: 
   #              # calculate distances of pre to post (used for delay and dist-dep conn)
   #              if 'toroidal' not in self.params: 
   #                  self.params['toroidal'] = False
   #              if self.params['toroidal']: 
   #                  xpath=[(preCellTags['x']-postCell.tags['x'])**2 for preCellTags in preCells.values()]
   #                  xpath2=[(f.modelsize - abs(preCellTags['x']-postCell.tags['x']))**2 for preCellTags in preCells.values()]
   #                  xpath[xpath2<xpath]=xpath2[xpath2<xpath]
   #                  xpath=array(xpath)
   #                  ypath=array([((preCellTags['ynorm']-postCell.tags['ynorm'])*self.params['corticalthick'])**2 for preCellTags in preCells.values()])
   #                  zpath=[(preCellTags['z']-postCell.tags['z'])**2 for preCellTags in preCells.values()]
   #                  zpath2=[(f.modelsize - abs(preCellTags['z']-postCell.tags['z']))**2 for preCellTags in preCells.values()]
   #                  zpath[zpath2<zpath]=zpath2[zpath2<zpath]
   #                  zpath=array(zpath)
   #                  #distances = array(sqrt(xpath + zpath)) # Calculate all pairwise distances
   #                  distances3d = sqrt(array(xpath) + array(ypath) + array(zpath)) # Calculate all pairwise 3d distances
   #              else: 
   #                  #distances = [sqrt((preCellTags['x']-postCell.tags['x'])**2 + \
   #                  #    (preCellTags['z']-postCell.tags['z'])**2) for preCellTags in preCells.values()]  # Calculate all pairwise distances
   #                  distances3d = sqrt([(preCellTags['x']-postCell.tags['x'])**2 + \
   #                      (preCellTags['ynorm']*self.params['corticalthick']-postCell.tags['ynorm'])**2 + \
   #                      (preCellTags['z']-postCell.tags['z'])**2 for preCellTags in preCells.values()])  # Calculate all pairwise distances

   #               # distance-dependent conn with length constant param
   #                  if hasattr(connParam['probability'], '__call__'): # check if conn is ynorm-dep func 
   #                      allConnProbs = [self.params['scaleconnprob'] * exp(-distances3d[i]/connParam['lengthConst']) * \
   #                          connParam['probability'](preCellTags['ynorm'], postCell.tags['ynorm']) \
   #                          for i,preCellTags in enumerate(preCells.values())] # Calculate pairwise probabilities
   #                  else:
   #                      allConnProbs = [self.params['scaleconnprob'] * exp(-distances3d[i]/connParam['lengthConst']) * connParam['probability'] \
   #                      for i,preCellTags in enumerate(preCells.values())] # Calculate pairwise probabilities
   #          else:  # NO distance-dependence
   #              if hasattr(connParam['probability'], '__call__'): # check if conn is ynorm-dep func 
   #                  allConnProbs = [self.params['scaleconnprob'] * connParam['probability'](preCellTags['ynorm'], postCell.tags['ynorm']) \
   #                  for i,preCellTags in enumerate(preCells.values())] # Calculate pairwise probabilities
   #              else:
   #                  allConnProbs = [self.params['scaleconnprob'] * connParam['probability'] \
   #                  for i,preCellTags in enumerate(preCells.values())] # Calculate pairwise probabilities
           
   #          seed(f.sim.id32('%d'%(f.cfg['randseed']+postCell.gid)))  # Reset random number generator  
   #          allRands = rand(len(allConnProbs))  # Create an array of random numbers for checking each connection
   #          makeThisConnection = allConnProbs>allRands # Perform test to see whether or not this connection should be made
   #          preInds = array(makeThisConnection.nonzero()[0],dtype='int') # Return True elements of that array for presynaptic cell IDs

   #          if all (k in connParam for k in ('delayMean', 'delayVar')):  # generate list of delays based on mean and variance
   #              seed(f.sim.id32('%d'%(f.cfg['randseed']+postCells.keys()[0])))  # Reset random number generator  
   #              delays = [gauss(connParam['delayMean'], connParam['delayVar']) for pre in range(len(preInds))] # select random delays based on mean and var params    
   #          elif 'lengthConst' in connParam: # generate list of delays based on distance between cells (only happens when prob also dist-dep)
   #              delays = [self.params['mindelay'] + distances3d[preInd]/float(self.params['velocity']) for preInd in preInds]  # Calculate the delays
   #          elif 'delay' in connParam:  # fixed delay specified in conn params
   #              delays = [connParam['delay'] for preInd in preInds]
   #          else: # fixed minDelay
   #              delays = [self.params['mindelay'] for preInd in preInds]

   #          if hasattr(connParam['weight'], '__call__'): # if ynorm-dep weight
   #              weights = [self.params['scaleconnweight'] * connParam['weight'](preCellTags['ynorm'], postCell.tags['ynorm']) for preCellTags in preCells.values()]
   #          else:  # NO ynorm-dep weight
   #              weights = [self.params['scaleconnweight'] * connParam['weight'] for preCellTags in preCells.values()]
   #          for i,preInd in enumerate(preInds):
   #              if preCells.keys()[preInd] == postCell.gid: break
   #              params = {'preGid': preCells.keys()[preInd], 
   #              'sec': connParam['sec'], 
   #              'synReceptor': connParam['synReceptor'], 
   #              'weight': weights[i], 
   #              'delay': delays[i], 
   #              'threshold': connParam['threshold']}
   #              postCell.addConn(params)  # call cell method to add connections

      
