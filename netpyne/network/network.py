
"""
Module defining Network class and methods

"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from ..specs import ODict
from neuron import h  # import NEURON

class Network(object):
    """
    Class for/to <short description of `netpyne.network.network.Network`>


    """



    # -----------------------------------------------------------------------------
    # initialize variables
    # -----------------------------------------------------------------------------
    def __init__(self, params = None):
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
        self.cells_dpls = {} # dict with vectors of dipole over time for each cell
        self.cells_dpl = {} # dict with vectors of dipole at one time for each cell

        self.gid2lid = {} # Empty dict for storing GID -> local index (key = gid; value = local id) -- ~x6 faster than .index()
        self.lastGid = 0  # keep track of last cell gid
        self.lastGapId = 0  # keep track of last gap junction gid


    # -----------------------------------------------------------------------------
    # Set network params
    # -----------------------------------------------------------------------------
    def setParams(self, params):
        self.params = params

    # -----------------------------------------------------------------------------
    # Instantiate network populations (objects of class 'Pop')
    # -----------------------------------------------------------------------------
    def createPops(self):
        from .. import sim

        for popLabel, popParam in self.params.popParams.items(): # for each set of population paramseters
            self.pops[popLabel] = sim.Pop(popLabel, popParam)  # instantiate a new object of class Pop and add to list pop
        return self.pops


    # -----------------------------------------------------------------------------
    # Create Cells
    # -----------------------------------------------------------------------------
    def createCells(self):
        from .. import sim

        sim.pc.barrier()
        sim.timing('start', 'createTime')
        if sim.rank==0:
            print(("\nCreating network of %i cell populations on %i hosts..." % (len(self.pops), sim.nhosts)))

        self._setDiversityRanges()  # update fractions for rules

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
    # Set fraction of cells for populations with cell diversity
    # -----------------------------------------------------------------------------
    def _setDiversityRanges(self):
        from .. import sim

        condFracs = {}
        for cellRule in sim.net.params.cellParams.values():
            if 'diversityFraction' in cellRule:
                divFrac = cellRule['diversityFraction']
                cellType = cellRule['conds'].get('cellType', None)
                cellModel = cellRule['conds'].get('CellModel', None)
                pop = cellRule['conds'].get('pop', None)

                correction = 1e-12

                if (cellType, cellModel, pop) in condFracs:
                    startFrac = float(condFracs[(cellType, cellModel, pop)])
                    endFrac = startFrac + divFrac
                    cellRule['conds']['fraction'] = [startFrac - correction, endFrac - correction]
                    condFracs[(cellType, cellModel, pop)] = endFrac
                else:
                    startFrac = 0
                    endFrac = startFrac + divFrac
                    cellRule['conds']['fraction'] = [startFrac, endFrac - correction]
                    condFracs[(cellType, cellModel, pop)] = endFrac

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
    # Import rxd methods
    # -----------------------------------------------------------------------------
    from .netrxd import addRxD, _addRegions, _addExtracellularRegion, _addSpecies,  \
        _addStates,  _addReactions, _addRates, _replaceRxDStr, _addParameters

    # -----------------------------------------------------------------------------
    # Import shape methods
    # -----------------------------------------------------------------------------
    from .shape import calcSegCoords, defineCellShapes

    # -----------------------------------------------------------------------------
    # Import modify methods
    # -----------------------------------------------------------------------------
    from .modify import modifyCells, modifySynMechs, modifyConns, modifyStims
