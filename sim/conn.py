"""
cell.py 

Contains class 'Conn' used to instantiate connections, and contains methods to connect cells (eg. random, yfrac-based)

Version: 2015may26 by salvadordura@gmail.com
"""

from pylab import array, sqrt, exp, rand, seed, transpose
import random
from neuron import h # Import NEURON
import params as p
import shared as s

###############################################################################
### CONN CLASS
###############################################################################

class Conn:
    ''' Class used to instantiate connections, and containing methods to connect cells (eg. random, yfrac-based)''' 
    def __init__(self, preGid, postGid, targetObj, delay, weight):
        self.preid = preGid  
        self.postid = postGid
        self.delay = delay
        self.weight = weight
        self.netcon = s.pc.gid_connect(preGid, targetObj)  # create Netcon between global gid and local cell object
        self.netcon.delay = delay  # set Netcon delay
        for i in range(p.numReceptors): self.netcon.weight[i] = weight[i]  # set Netcon weights
        if p.verbose: print('Created Conn pre=%d post=%d delay=%0.2f, weights=[%.2f, %.2f, %.2f, %.2f]'\
            %(preGid, postGid, delay, weight[0], weight[1], weight[2], weight[3] ))



###############################################################################
### RANDOM CONN CLASS
###############################################################################

class RandConn(Conn):         
    @classmethod
    def connect(cls, ncell, cellPost):
        ''' Calculate connectivity as a func of cellPre.topClass, cellPre.yfrac, cellPost.topClass, cellPost.yfrac'''
        random.seed(s.id32('%d'%(p.randseed+cellPost.gid)))  # Reset random number generator  
        randPre = random.sample(xrange(ncell-1), random.randint(0, p.maxcons)) # select random subset of pre cells
        randDelays = [random.gauss(p.delaymean, p.delayvar) for i in randPre] # select random delays based on mean and var params
        cellPost.syns = [h.ExpSyn(0,sec=cellPost.soma) for i in randPre] # create syn objects for each connection (store syn objects inside post cell object)
        newConns = [RandConn(x, cellPost.gid, cellPost.syns[i], randDelays[i], [p.weight]) for i,x in enumerate(randPre)] # create new conn objects 
        return newConns


###############################################################################
### YFRAC CONN CLASS
###############################################################################

class YfracConn(Conn):

    @classmethod
    def connect(cls, cellsPre, cellPost):
        ''' Calculate connectivity as a func of cellPre.topClass, cellPre.yfrac, cellPost.topClass, cellPost.yfrac'''
        # calculate distances of pre to post
        if p.toroidal: 
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
           distances3d = sqrt([(x.xloc-cellPost.xloc)**2 + (x.yfrac*p.corticalthick-cellPost.yfrac)**2 + (x.zloc-cellPost.zloc)**2 for x in cellsPre])  # Calculate all pairwise distances
        allconnprobs = p.scaleconnprob[[x.EorI for x in cellsPre], cellPost.EorI] \
                * exp(-distances/p.connfalloff[[x.EorI for x in  cellsPre]]) \
                * [p.connProbs[x.topClass][cellPost.topClass](x.yfrac, cellPost.yfrac) for x in cellsPre] # Calculate pairwise probabilities
        allconnprobs[cellPost.gid] = 0  # Prohibit self-connections using the cell's GID

        seed(s.id32('%d'%(p.randseed+cellPost.gid)))  # Reset random number generator  
        allrands = rand(len(allconnprobs))  # Create an array of random numbers for checking each connection
        makethisconnection = allconnprobs>allrands # Perform test to see whether or not this connection should be made
        preids = array(makethisconnection.nonzero()[0],dtype='int') # Return True elements of that array for presynaptic cell IDs
        delays = p.mindelay + distances[preids]/float(p.velocity) # Calculate the delays
        wt1 = p.scaleconnweight[[x.EorI for x in [cellsPre[i] for i in preids]], cellPost.EorI] # N weight scale factors
        wt2 = [[cls.connWeights[x.topClass][cellPost.topClass][iReceptor](x.yfrac, cellPost.yfrac) \
            for iReceptor in range(p.numReceptors)] for x in [cellsPre[i] for i in preids]] # NxM inter-population weights
        wt3 = p.receptorweight[:] # M receptor weights
        finalweights = transpose(wt1*transpose(array(wt2)*wt3)) # Multiply out population weights with receptor weights to get NxM matrix
        cellPost.syns = [h.ExpSyn(0,sec=cellPost.sec) for i in preids] # create syn objects for each connection (store syn objects inside post cell object)
        # create list of Conn objects
        newConns = [YfracConn(preGid=preids[i], postGid=cellPost.gid, targetObj = cellPost.syns[i], delay=delays[i], weight=finalweights[i]) for i in range(len(preids))]
        #newConns = [YfracConn(preGid=preids[i], postGid=cellPost.gid, targetObj = cellPost.m, delay=delays[i], weight=finalweights[i]) for i in range(len(preids))]
        return newConns

