
"""
network.py 

Contains cell and population classes 

Contributors: salvadordura@gmail.com
"""

from pylab import seed, rand, sqrt, exp, transpose, ceil, concatenate, array, zeros, ones, vstack, show, disp, mean, inf, concatenate
from time import time, sleep
import pickle
import warnings
from neuron import h  # import NEURON

warnings.filterwarnings('error')

class Network(object):

    ###############################################################################
    # initialize variables
    ###############################################################################
    def __init__(self, params = None, sim = None):
        self.params = params
        self.sim = sim


    ###############################################################################
    # Instantiate network populations (objects of class 'Pop')
    ###############################################################################
    def createPops(self):
        self.pops = []  # list to store populations ('Pop' objects)
        for popParam in self.params['popParams']: # for each set of population parameters 
            self.pops.append(self.Pop(popParam))  # instantiate a new object of class Pop and add to list pop


    ###############################################################################
    # Create Cells
    ###############################################################################
    def createCells(self):
        self.sim.pc.barrier()
        if self.rank==0: print("\nCreating simulation of %i cell populations for %0.1f s on %i hosts..." % (len(self.pops), self.sim.params['duration']/1000.,self.sim.nhosts)) 
        self.gidVec = [] # Empty list for storing GIDs (index = local id; value = gid)
        self.gidDic = {} # Empty dict for storing GIDs (key = gid; value = local id) -- ~x6 faster than gidVec.index()  
        self.cells = []
        for ipop in self.pops: # For each pop instantiate the network cells (objects of class 'Cell')
            newCells = ipop.createCells() # create cells for this pop using Pop method
            self.cells.extend(newCells)  # add to list of cells
            self.sim.pc.barrier()
            if self.rank==0 and p.verbose: print('Instantiated %d cells of population %d'%(ipop.numCells, ipop.popgid))    
        self.simdata.update({name:h.Vector(1e4).resize(0) for name in ['spkt','spkid']})
        print('  Number of cells on node %i: %i ' % (self.rank,len(self.cells)))            
        

    ###############################################################################
    # Connect Cells
    ###############################################################################
    def connectCells(self):
        # Instantiate network connections (objects of class 'Conn') - connects object cells based on pre and post cell's type, class and yfrac
        if self.rank==0: print('Making connections...'); connstart = time()

        if self.params['connType'] == 'random':  # if random connectivity
            connClass = self.RandConn  # select ConnRand class
            arg = self.params['ncell']  # pass as argument num of presyn cell
        
        elif self.params['connType'] == 'yfrac':  # if yfrac-based connectivity
            connClass = self.YfracConn  # select ConnYfrac class
            data = [s.cells]*s.nhosts  # send cells data to other nodes
            gather = self.pc.py_alltoall(data)  # collect cells data from other nodes (required to generate connections)
            self.pc.barrier()
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
        
        print('  Number of connections on host %i: %i ' % (self.rank, len(self.conns)))
        self.pc.barrier()
        if self.rank==0: conntime = time()-connstart; print('  Done; time = %0.1f s' % conntime) # See how long it took


    ###############################################################################
    # Add background inputs
    ###############################################################################
    def addBackground(self):
        if self.rank==0: print('Creating background inputs...')
        for c in self.cells: 
            c.addBackground()
        print('  Number created on host %i: %i' % (self.rank, len(self.cells)))
        self.pc.barrier()





