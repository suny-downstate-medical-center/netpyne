from pylab import array, sqrt, exp, seed, rand, transpose
from neuron import h # Import NEURON
import params as p
import shared as s

###############################################################################
### CONN CLASS
###############################################################################

# definition of python class 'Conn' to store and calcualte connections
class Conn:

    def __init__(self, preGid, cellPost, delay, weight):
        self.preid = preGid  # 
        self.postid = cellPost.gid
        self.delay = delay
        self.weight = weight
        self.netcon = s.pc.gid_connect(preGid, cellPost.m)  # create Netcon between global gid and local cell object
        self.netcon.delay = delay  # set Netcon delay
        for i in range(p.numReceptors): self.netcon.weight[i] = weight[i]  # set Netcon weights
        if p.verbose: print('Created Conn pre=%d post=%d delay=%0.2f, weights=[%.2f, %.2f, %.2f, %.2f]'\
            %(preGid, cellPost.gid, delay, weight[0], weight[1], weight[2], weight[3] ))
               

    @classmethod
    def connect(cls, cellsPre, cellPost):
        pass

    @classmethod
    def connectYfrac(cls, cellsPre, cellPost):
            # class variables to store matrix of connection probabilities (constant or function) for pre and post cell topClass
        connProbs=[[(lambda x: 0)]*p.numTopClass]*p.numTopClass
        connProbs[p.IT][p.IT]   = (lambda x,y: 0.1*x+0.01/y)  # example of yfrac-dep function (x=presyn yfrac, y=postsyn yfrac)
        connProbs[p.IT][p.PT]   = (lambda x,y: 0.02*x if (x>0.5 and x<0.8) else 0)
        connProbs[p.IT][p.CT]   = (lambda x,y: 0.1)  # constant function
        connProbs[p.IT][p.Pva]  = (lambda x,y: 0.1)
        connProbs[p.IT][p.Sst]  = (lambda x,y: 0.1)
        connProbs[p.PT][p.IT]   = (lambda x,y: 0)
        connProbs[p.PT][p.PT]   = (lambda x,y: 0.1)
        connProbs[p.PT][p.CT]   = (lambda x,y: 0)
        connProbs[p.PT][p.Pva]  = (lambda x,y: 0.1)
        connProbs[p.PT][p.Sst]  = (lambda x,y: 0.1)
        connProbs[p.CT][p.IT]   = (lambda x,y: 0.1)
        connProbs[p.CT][p.PT]   = (lambda x,y: 0)
        connProbs[p.CT][p.CT]   = (lambda x,y: 0.1)
        connProbs[p.CT][p.Pva]  = (lambda x,y: 0.1)
        connProbs[p.CT][p.Sst]  = (lambda x,y: 0.1)
        connProbs[p.Pva][p.IT]  = (lambda x,y: 0.1)
        connProbs[p.Pva][p.PT]  = (lambda x,y: 0.1)
        connProbs[p.Pva][p.CT]  = (lambda x,y: 0.1)
        connProbs[p.Pva][p.Pva] = (lambda x,y: 0.1)
        connProbs[p.Pva][p.Sst] = (lambda x,y: 0.1)
        connProbs[p.Sst][p.IT]  = (lambda x,y: 0.1)
        connProbs[p.Sst][p.PT]  = (lambda x,y: 0.1)
        connProbs[p.Sst][p.CT]  = (lambda x,y: 0.1)
        connProbs[p.Sst][p.Pva] = (lambda x,y: 0.1)
        connProbs[p.Sst][p.Sst] = (lambda x,y: 0.1)

        # class variables to store matrix of connection weights (constant or function) for pre and post cell topClass
        #connWeights=zeros((p.numTopClass,p.numTopClass,p.numReceptors))
        connWeights=[[[(lambda x,y: 0)]*p.numReceptors]*p.numTopClass]*p.numTopClass    
        connWeights[p.IT][p.IT][p.AMPA]   = (lambda x,y: 1)
        connWeights[p.IT][p.PT][p.AMPA]   = (lambda x,y: 1)
        connWeights[p.IT][p.CT][p.AMPA]   = (lambda x,y: 1)
        connWeights[p.IT][p.Pva][p.AMPA]  = (lambda x,y: 1)
        connWeights[p.IT][p.Sst][p.AMPA]  = (lambda x,y: 1)
        connWeights[p.PT][p.IT][p.AMPA]   = (lambda x,y: 0)
        connWeights[p.PT][p.PT][p.AMPA]   = (lambda x,y: 1)
        connWeights[p.PT][p.CT][p.AMPA]   = (lambda x,y: 0)
        connWeights[p.PT][p.Pva][p.AMPA]  = (lambda x,y: 1)
        connWeights[p.PT][p.Sst][p.AMPA]  = (lambda x,y: 1)
        connWeights[p.CT][p.IT][p.AMPA]   = (lambda x,y: 1)
        connWeights[p.CT][p.PT][p.AMPA]   = (lambda x,y: 0)
        connWeights[p.CT][p.CT][p.AMPA]   = (lambda x,y: 1)
        connWeights[p.CT][p.Pva][p.AMPA]  = (lambda x,y: 1)
        connWeights[p.CT][p.Sst][p.AMPA]  = (lambda x,y: 1)
        connWeights[p.Pva][p.IT][p.GABAA]  = (lambda x,y: 1)
        connWeights[p.Pva][p.PT][p.GABAA]  = (lambda x,y: 1)
        connWeights[p.Pva][p.CT][p.GABAA]  = (lambda x,y: 1)
        connWeights[p.Pva][p.Pva][p.GABAA] = (lambda x,y: 1)
        connWeights[p.Pva][p.Sst][p.GABAA] = (lambda x,y: 1)
        connWeights[p.Sst][p.IT][p.GABAB]  = (lambda x,y: 1)
        connWeights[p.Sst][p.PT][p.GABAB]  = (lambda x,y: 1)
        connWeights[p.Sst][p.CT][p.GABAB]  = (lambda x,y: 1)
        connWeights[p.Sst][p.Pva][p.GABAB] = (lambda x,y: 1)
        connWeights[p.Sst][p.Sst][p.GABAB] = (lambda x,y: 1)

        #calculate as a func of cellPre.topClass, cellPre.yfrac, cellPost.topClass, cellPost.yfrac etc (IN PROGRESS!!)
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
                * [connProbs[x.topClass][cellPost.topClass](x.yfrac, cellPost.yfrac) for x in cellsPre] # Calculate pairwise probabilities
        allconnprobs[cellPost.gid] = 0  # Prohibit self-connections using the cell's GID

        seed(s.id32('%d'%(p.randseed+cellPost.gid)))  # Reset random number generator  
        allrands = rand(len(allconnprobs))  # Create an array of random numbers for checking each connection
        makethisconnection = allconnprobs>allrands # Perform test to see whether or not this connection should be made
        preids = array(makethisconnection.nonzero()[0],dtype='int') # Return True elements of that array for presynaptic cell IDs
        delays = p.mindelay + distances[preids]/float(p.velocity) # Calculate the delays
        wt1 = p.scaleconnweight[[x.EorI for x in [cellsPre[i] for i in preids]], cellPost.EorI] # N weight scale factors
        wt2 = [[connWeights[x.topClass][cellPost.topClass][iReceptor](x.yfrac, cellPost.yfrac) \
            for iReceptor in range(p.numReceptors)] for x in [cellsPre[i] for i in preids]] # NxM inter-population weights
        wt3 = p.receptorweight[:] # M receptor weights
        finalweights = transpose(wt1*transpose(array(wt2)*wt3)) # Multiply out population weights with receptor weights to get NxM matrix
        # create list of Conn objects
        newConns = [Conn(preGid=preids[i], cellPost=cellPost, delay=delays[i], weight=finalweights[i]) for i in range(len(preids))]
        return newConns