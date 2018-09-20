
"""
network.py 

Defines Network class which contains cell objects and network-realated methods

Contributors: salvadordura@gmail.com
"""

from ..specs import ODict
from neuron import h  # import NEURON

class Network (object):

    # -----------------------------------------------------------------------------
    # initialize variables
    # -----------------------------------------------------------------------------
    def __init__ (self, params = None):
        self.params = params

        # params that can be expressed using string-based functions in connections
        self.connStringFuncParams = ['weight', 'delay', 'synsPerConn', 'loc']  

        # params that can be expressed using string-based functions in stims
        self.stimStringFuncParams = ['delay', 'dur', 'amp', 'gain', 'rstim', 'tau1', 'tau2', 
        'onset', 'tau', 'gmax', 'e', 'i', 'interval', 'rate', 'number', 'start', 'noise']  

        # list of h.Random() methods allowed in string-based functions (both for conns and stims)
        self.stringFuncRandMethods = ['binomial', 'discunif', 'erlang', 'geometric', 'hypergeo', 
        'lognormal', 'negexp', 'normal', 'poisson', 'uniform', 'weibull']

        self.rand = h.Random()  # random number generator

        self.pops = ODict()  # list to store populations ('Pop' objects)
        self.cells = [] # list to store cells ('Cell' objects)

        self.lid2gid = [] # Empty list for storing local index -> GID (index = local id; value = gid)
        self.gid2lid = {} # Empty dict for storing GID -> local index (key = gid; value = local id) -- ~x6 faster than .index() 
        self.lastGid = 0  # keep track of last cell gid 
        self.lastGapId = 0  # keep track of last gap junction gid 


    # -----------------------------------------------------------------------------
    # Set network params
    # -----------------------------------------------------------------------------
    def setParams (self, params):
        self.params = params

    # -----------------------------------------------------------------------------
    # Instantiate network populations (objects of class 'Pop')
    # -----------------------------------------------------------------------------
    def createPops (self):
        from .. import sim

        for popLabel, popParam in self.params.popParams.items(): # for each set of population paramseters 
            self.pops[popLabel] = sim.Pop(popLabel, popParam)  # instantiate a new object of class Pop and add to list pop
        return self.pops


    # -----------------------------------------------------------------------------
    # Create Cells
    # -----------------------------------------------------------------------------
    def createCells (self):
        from .. import sim

        sim.pc.barrier()
        sim.timing('start', 'createTime')
        if sim.rank==0: 
            print(("\nCreating network of %i cell populations on %i hosts..." % (len(self.pops), sim.nhosts))) 
        
        for ipop in list(self.pops.values()): # For each pop instantiate the network cells (objects of class 'Cell')
            newCells = ipop.createCells() # create cells for this pop using Pop method
            self.cells.extend(newCells)  # add to list of cells
            sim.pc.barrier()
            if sim.rank==0 and sim.cfg.verbose: print(('Instantiated %d cells of population %s'%(len(newCells), ipop.tags['pop'])))  

        if self.params.defineCellShapes: self.defineCellShapes()
  
        print(('  Number of cells on node %i: %i ' % (sim.rank,len(self.cells)))) 
        sim.pc.barrier()
        sim.timing('stop', 'createTime')
        if sim.rank == 0 and sim.cfg.timing: print(('  Done; cell creation time = %0.2f s.' % sim.timingData['createTime']))

        return self.cells

    # -----------------------------------------------------------------------------
    # Import stim methods
    # -----------------------------------------------------------------------------
    from .stim import addStims, _addCellStim, _stimStrToFunc

    # -----------------------------------------------------------------------------
    # Import conn methods
    # -----------------------------------------------------------------------------
    from .conn import connectCells, _findPrePostCellsCondition, _connStrToFunc, \
        fullConn, generateRandsPrePost, probConn, randUniqueInt, convConn, divConn, fromListConn, \
        _addCellConn, _disynapticBiasProb, _disynapticBiasProb2

    # -----------------------------------------------------------------------------
    # Import subconn methods
    # -----------------------------------------------------------------------------
    from .subconn import fromtodistance, _posFromLoc, _interpolateSegmentSigma, subcellularConn

    # -----------------------------------------------------------------------------
    # Import shape methods
    # -----------------------------------------------------------------------------
    from .shape import calcSegCoords, defineCellShapes

    # -----------------------------------------------------------------------------
    # Import modify methods
    # -----------------------------------------------------------------------------
    from .modify import modifyCells, modifySynMechs, modifyConns, modifyStims



