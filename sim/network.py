
"""
network.py 

Defines Network class which contains cell objects and network-realated methods

Contributors: salvadordura@gmail.com
"""

from pylab import seed, rand, sqrt, exp, transpose, ceil, concatenate, array, zeros, ones, vstack, show, disp, mean, inf, concatenate
from time import time, sleep
import pickle
import warnings
from neuron import h  # import NEURON
import shared as s


class Network(object):

    ###############################################################################
    # initialize variables
    ###############################################################################
    def __init__(self, param = None):
        self.param = param


    ###############################################################################
    # Instantiate network populations (objects of class 'Pop')
    ###############################################################################
    def createPops(self):
        self.pops = []  # list to store populations ('Pop' objects)
        for popParam in self.param['popParams']: # for each set of population parameters 
            self.pops.append(self.Pop(popParam))  # instantiate a new object of class Pop and add to list pop


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
            if s.rank==0 and s.cfg['verbose']: print('Instantiated %d cells of population %d'%(ipop.numCells, ipop.popgid))    
        s.simdata.update({name:h.Vector(1e4).resize(0) for name in ['spkt','spkid']})
        print('  Number of cells on node %i: %i ' % (s.rank,len(self.cells)))            
        

    ###############################################################################
    # Connect Cells
    ###############################################################################
    def connectCells(self):
        # Instantiate network connections (objects of class 'Conn') - connects object cells based on pre and post cell's type, class and yfrac
        if s.rank==0: print('Making connections...'); connstart = time()

        if self.param['connType'] == 'random':  # if random connectivity
            connClass = self.RandConn  # select ConnRand class
            arg = self.param['ncell']  # pass as argument num of presyn cell
        
        elif self.param['connType'] == 'yfrac':  # if yfrac-based connectivity
            connClass = self.YfracConn  # select ConnYfrac class
            data = [s.cells]*s.nhosts  # send cells data to other nodes
            gather = s.pc.py_alltoall(data)  # collect cells data from other nodes (required to generate connections)
            s.pc.barrier()
            allCells = []
            for x in gather:    allCells.extend(x)  # concatenate cells data from all nodes
            del gather, data  # removed unnecesary variables
            allCellsGids = [x.gid for x in allCells] # order gids
            allCells = [x for (y,x) in sorted(zip(allCellsGids,allCells))]
            arg = allCells  # pass as argument the list of presyn cell objects

        self.conns = []  # list to store connections   
        for ipost in self.cells: # for each postsynaptic cell in this node
            newConns = connClass.connect(arg, ipost)  # calculate all connections
            if newConns: self.conns.extend(newConns)  # add to list of connections in this node
        
        print('  Number of connections on host %i: %i ' % (s.rank, len(self.conns)))
        s.pc.barrier()
        if s.rank==0: conntime = time()-connstart; print('  Done; time = %0.1f s' % conntime) # See how long it took


    ###############################################################################
    # Add background inputs
    ###############################################################################
    def addBackground(self):
        if s.rank==0: print('Creating background inputs...')
        for c in self.cells: 
            c.addBackground()
        print('  Number created on host %i: %i' % (s.rank, len(self.cells)))
        s.pc.barrier()



###############################################################################
### RANDOM CONN CLASS
###############################################################################

class RandConn(Conn):         
    @classmethod
    def connect(cls, ncell, cellPost):
        ''' Generates random connectivity based on maxcons - no conn rules'''
        random.seed(s.id32('%d'%(p.sim['randseed']+cellPost.gid)))  # Reset random number generator  
        randPre = random.sample(xrange(ncell-1), random.randint(0, p.net['maxcons'])) # select random subset of pre cells
        randDelays = [random.gauss(p.net['delaymean'], p.net['delayvar']) for i in randPre] # select random delays based on mean and var params
        cellPost.syns = [h.ExpSyn(0,sec=cellPost.soma) for i in randPre] # create syn objects for each connection (store syn objects inside post cell object)
        newConns = [RandConn(x, cellPost.gid, cellPost.syns[i], randDelays[i], [p.net['weight']]) for i,x in enumerate(randPre)] # create new conn objects 
        return newConns


###############################################################################
### YFRAC CONN CLASS
###############################################################################

class YfracConn(Conn):

    @classmethod
    def connect(cls, cellsPre, cellPost):
        ''' Calculate connectivity as a func of cellPre.topClass, cellPre.yfrac, cellPost.topClass, cellPost.yfrac'''
        # calculate distances of pre to post
        if p.net['toroidal']: 
            xpath=[(x.xloc-cellPost.xloc)**2 for x in cellsPre]
            xpath2=[(s.modelsize - abs(x.xloc-cellPost.xloc))**2 for x in cellsPre]
            xpath[xpath2<xpath]=xpath2[xpath2<xpath]
            xpath=array(xpath)
            ypath=array([((x.yfrac-cellPost.yfrac)*s.corticalthick)**2 for x in cellsPre])
            zpath=[(x.zloc-cellPost.zloc)**2 for x in cellsPre]
            zpath2=[(s.modelsize - abs(x.zloc-cellPost.zloc))**2 for x in cellsPre]
            zpath[zpath2<zpath]=zpath2[zpath2<zpath]
            zpath=array(zpath)
            distances = array(sqrt(xpath + zpath)) # Calculate all pairwise distances
            distances3d = sqrt(array(xpath) + array(ypath) + array(zpath)) # Calculate all pairwise 3d distances
        else: 
           distances = sqrt([(x.xloc-cellPost.xloc)**2 + (x.zloc-cellPost.zloc)**2 for x in cellsPre])  # Calculate all pairwise distances
           distances3d = sqrt([(x.xloc-cellPost.xloc)**2 + (x.yfrac*p.net['corticalthick']-cellPost.yfrac)**2 + (x.zloc-cellPost.zloc)**2 for x in cellsPre])  # Calculate all pairwise distances
        allconnprobs = p.net['scaleconnprob'][[x.EorI for x in cellsPre], cellPost.EorI] \
                * exp(-distances/p.net['connfalloff'][[x.EorI for x in  cellsPre]]) \
                * [p.net['connProbs'][x.topClass][cellPost.topClass](x.yfrac, cellPost.yfrac) for x in cellsPre] # Calculate pairwise probabilities
        allconnprobs[cellPost.gid] = 0  # Prohibit self-connections using the cell's GID

        seed(s.id32('%d'%(p.sim['randseed']+cellPost.gid)))  # Reset random number generator  
        allrands = rand(len(allconnprobs))  # Create an array of random numbers for checking each connection
        makethisconnection = allconnprobs>allrands # Perform test to see whether or not this connection should be made
        preids = array(makethisconnection.nonzero()[0],dtype='int') # Return True elements of that array for presynaptic cell IDs
        delays = p.net['mindelay'] + distances[preids]/float(p.net['velocity']) # Calculate the delays
        wt1 = p.net['scaleconnweight'][[x.EorI for x in [cellsPre[i] for i in preids]], cellPost.EorI] # N weight scale factors
        wt2 = [[p.net['connWeights'][x.topClass][cellPost.topClass][iReceptor](x.yfrac, cellPost.yfrac) \
            for iReceptor in range(p.net['numReceptors'])] for x in [cellsPre[i] for i in preids]] # NxM inter-population weights
        wt3 = p.net['receptorweight'][:] # M receptor weights
        finalweights = transpose(wt1*transpose(array(wt2)*wt3)) # Multiply out population weights with receptor weights to get NxM matrix
        cellPost.syns = [h.ExpSyn(0,sec=cellPost.sec) for i in preids] # create syn objects for each connection (store syn objects inside post cell object)
        # create list of Conn objects
        newConns = [YfracConn(preGid=preids[i], postGid=cellPost.gid, targetObj = cellPost.syns[i], delay=delays[i], weight=finalweights[i]) for i in range(len(preids))]
        #newConns = [YfracConn(preGid=preids[i], postGid=cellPost.gid, targetObj = cellPost.m, delay=delays[i], weight=finalweights[i]) for i in range(len(preids))]
        return newConns


