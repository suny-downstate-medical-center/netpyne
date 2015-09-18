
"""
network.py 

Defines Network class which contains cell objects and network-realated methods

Contributors: salvadordura@gmail.com
"""

from pylab import seed, rand, sqrt, exp, transpose, ceil, concatenate, array, zeros, ones, vstack, show, disp, mean, inf, concatenate
import random
from time import time, sleep
import pickle
import warnings
from neuron import h  # import NEURON
import shared as s


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
            self.pops.append(s.Pop(popParam))  # instantiate a new object of class Pop and add to list pop


    ###############################################################################
    # Create Cells
    ###############################################################################
    def createCells(self):
        s.pc.barrier()
        if s.rank==0: print("\nCreating simulation of %i cell populations for %0.1f s on %i hosts..." % (len(self.pops), s.cfg['duration']/1000.,s.nhosts)) 
        self.gidVec = [] # Empty list for storing GIDs (index = local id; value = gid)
        self.gidDic = {} # Empty dict for storing GIDs (key = gid; value = local id) -- ~x6 faster than gidVec.index()  
        self.cells = []
        for ipop in self.pops: # For each pop instantiate the network cells (objects of class 'Cell')
            newCells = ipop.createCells() # create cells for this pop using Pop method
            self.cells.extend(newCells)  # add to list of cells
            s.pc.barrier()
            if s.rank==0 and s.cfg['verbose']: print('Instantiated %d cells of population %s'%(len(newCells), ipop.tags['popLabel']))    
        s.simData.update({name:h.Vector(1e4).resize(0) for name in ['spkt','spkid']})
        print('  Number of cells on node %i: %i ' % (s.rank,len(self.cells)))            
        

    ###############################################################################
    # Connect Cells
    ###############################################################################
    def connectCells(self):
        # Instantiate network connections based on the connectivity rules defined in params
        if s.rank==0: print('Making connections...'); connstart = time()

        if s.nhosts > 1: # Gather tags from all cells 
            allCellTags = s.sim.gatherAllCellTags()  
        else:
            allCellTags = {cell.gid: cell.tags for cell in self.cells}
        allPopTags = {i: pop.tags for i,pop in enumerate(self.pops)}  # gather tags from pops so can connect NetStim pops

        for connParam in self.params['connParams']:  # for each conn rule or parameter set
            if 'sec' not in connParam: connParam['sec'] = None  # if section not specified, make None (will be assigned to first section in cell)
            if 'synReceptor' not in connParam: connParam['synReceptor'] = None  # if section not specified, make None (will be assigned to first synapse in cell)  
            if 'threshold' not in connParam: connParam['threshold'] = None  # if section not specified, make None (will be assigned to first synapse in cell)    
            
            preCells = allCellTags  # initialize with all presyn cells 
            prePops = allPopTags  # initialize with all presyn pops
            for condKey,condValue in connParam['preTags'].iteritems():  # Find subset of cells that match presyn criteria
                preCells = {gid: tags for (gid,tags) in preCells.iteritems() if tags[condKey] == condValue}  # dict with pre cell tags
                prePops = {i: tags for (i,tags) in prePops.iteritems() if (condKey in tags) and (tags[condKey] == condValue)}
                
            if not preCells: # if no presyn cells, check if netstim
                if any (prePopTags['cellModel'] == 'NetStim' for prePopTags in prePops.values()):
                    preCells = prePops
            
            postCells = {cell.gid:cell for cell in self.cells}
            for condKey,condValue in connParam['postTags'].iteritems():  # Find subset of cells that match postsyn criteria
                postCells = {gid: cell for (gid,cell) in postCells.iteritems() if cell.tags[condKey] == condValue}  # dict with post Cell objects

            connFunc = getattr(self, connParam['connFunc'])  # get function name from params
            connFunc(preCells, postCells, connParam)  # call specific conn function
       

   ###############################################################################
    ### Full connectivity
    ###############################################################################
    def fullConn(self, preCells, postCells, connParam):
        ''' Generates connections between all pre and post-syn cells '''
        if all (k in connParam for k in ('delayMean', 'delayVar')):  # generate list of delays based on mean and variance
            random.seed(s.sim.id32('%d'%(s.cfg['randseed']+postCells.keys()[0])))  # Reset random number generator  
            randDelays = [random.gauss(connParam['delayMean'], connParam['delayVar']) for pre in range(len(preCells)*len(postCells))]  # select random delays based on mean and var params    
        else:
            randDelays = None   
            delay = connParam['delay']  # fixed delay
        for postCellGid, postCell in postCells.iteritems():  # for each postsyn cell
            for preCellGid,preCellTags in preCells.iteritems():  # for each presyn cell
                if preCellTags['cellModel'] == 'NetStim':  # if NetStim 
                    params = {'popLabel': preCellTags['popLabel'],
                    'rate': preCellTags['rate'],
                    'noise': preCellTags['noise'],
                    'source': preCellTags['source'], 
                    'sec': connParam['sec'], 
                    'synReceptor': connParam['synReceptor'], 
                    'weight': connParam['weight'], 
                    'delay': delay, 
                    'threshold': connParam['threshold']}
                    postCell.addStim(params)  # call cell method to add connections              
                elif preCellGid != postCellGid:
                    if randDelays:  delay = randDelays.pop()  # set random delay
                    # if not self-connection
                    params = {'preGid': preCellGid, 
                    'sec': connParam['sec'], 
                    'synReceptor': connParam['synReceptor'], 
                    'weight': connParam['weight'], 
                    'delay': delay, 
                    'threshold': connParam['threshold']}
                    postCell.addConn(params)  # call cell method to add connections


     
    ###############################################################################
    ### Random connectivity
    ###############################################################################
    def randConn(self, preCells, postCells, connParam):
        ''' Generates connections between  maxcons random pre and postsyn cells'''
        if 'maxConns' not in connParam: connParam['maxConns'] = len(preCells)
        if all (k in connParam for k in ('delayMean', 'delayVar')):  # generate list of delays based on mean and variance
            random.seed(s.sim.id32('%d'%(s.cfg['randseed']+postCells.keys()[0])))  # Reset random number generator  
            randDelays = [random.gauss(connParam['delayMean'], connParam['delayVar']) for pre in range(connParam['maxConns']*len(postCells))] # select random delays based on mean and var params    
        else:
            randDelays = None   
            delay = connParam['delay']  # fixed delay
        for postCellGid, postCell in postCells.iteritems():  # for each postsyn cell
            preCellGids = preCells.keys()
            if postCellGid in preCellGids: preCellGids.remove(postCellGid)
            randPreCellGids = random.sample(preCellGids, random.randint(0, min(connParam['maxConns'], len(preCellGids)))) # select random subset of pre cells
            for randPreCellGid in randPreCellGids: # for each presyn cell
                if randDelays:  delay = randDelays.pop()  # set random delay
                params = {'preGid': randPreCellGid, 
                'sec': connParam['sec'], 
                'synReceptor': connParam['synReceptor'], 
                'weight': connParam['weight'], 'delay': delay, 
                'threshold': connParam['threshold']}
                postCell.addConn(params)  # call cell method to add connections


    ###############################################################################
    ### Yfrac-based connectivity
    ###############################################################################
    def yfracProbConn(self, preCells, postCells, connParam):
        ''' Calculate connectivity as a func of preCell.topClass, preCell['yfrac'], postCell.topClass, postCell.tags['yfrac']
            preCells = {gid: tags} 
            postCells = {gid: Cell object}
            '''
        for postCell in postCells.values():
            # calculate distances of pre to post
            if self.params['toroidal']: 
                xpath=[(preCellTags['x']-postCell.tags['x'])**2 for preCellTags in preCells.values()]
                xpath2=[(s.modelsize - abs(preCellTags['x']-postCell.tags['x']))**2 for preCellTags in preCells.values()]
                xpath[xpath2<xpath]=xpath2[xpath2<xpath]
                xpath=array(xpath)
                ypath=array([((preCellTags['yfrac']-postCell.tags['yfrac'])*self.params['corticalthick'])**2 for preCellTags in preCells.values()])
                zpath=[(preCellTags['z']-postCell.tags['z'])**2 for preCellTags in preCells.values()]
                zpath2=[(s.modelsize - abs(preCellTags['z']-postCell.tags['z']))**2 for preCellTags in preCells.values()]
                zpath[zpath2<zpath]=zpath2[zpath2<zpath]
                zpath=array(zpath)
                distances = array(sqrt(xpath + zpath)) # Calculate all pairwise distances
                #distances3d = sqrt(array(xpath) + array(ypath) + array(zpath)) # Calculate all pairwise 3d distances
            else: 
                distances = [sqrt((preCellTags['x']-postCell.tags['x'])**2 + \
                    (preCellTags['z']-postCell.tags['z'])**2) for preCellTags in preCells.values()]  # Calculate all pairwise distances
                # distances3d = sqrt([(preCellTags['x']-postCell.tags['x'])**2 + \
                #     (preCellTags['yfrac']*self.params['corticalthick']-postCell.tags['yfrac'])**2 + \
                #     (preCellTags['z']-postCell.tags['z'])**2 for preCellTags in preCells.values()])  # Calculate all pairwise distances

            allConnProbs = [self.params['scaleconnprob'] * exp(-distances[i]/self.params['connfalloff']) * \
                connParam['probability'](preCellTags['yfrac'], postCell.tags['yfrac']) \
                for i,preCellTags in enumerate(preCells.values())] # Calculate pairwise probabilities

            seed(s.sim.id32('%d'%(s.cfg['randseed']+postCell.gid)))  # Reset random number generator  
            allRands = rand(len(allConnProbs))  # Create an array of random numbers for checking each connection
            makeThisConnection = allConnProbs>allRands # Perform test to see whether or not this connection should be made
            preInds = array(makeThisConnection.nonzero()[0],dtype='int') # Return True elements of that array for presynaptic cell IDs
            delays = [self.params['mindelay'] + distances[preInd]/float(self.params['velocity']) for preInd in preInds]  # Calculate the delays
            weights = [self.params['scaleconnweight'] * connParam['weight'](preCellTags['yfrac'], postCell.tags['yfrac']) for preCellTags in preCells.values()]
            for i,preInd in enumerate(preInds):
                if preCells.keys()[preInd] == postCell.gid: break
                params = {'preGid': preCells.keys()[preInd], 
                'sec': connParam['sec'], 
                'synReceptor': connParam['synReceptor'], 
                'weight': weights[i], 
                'delay': delays[i], 
                'threshold': connParam['threshold']}
                postCell.addConn(params)  # call cell method to add connections

      
