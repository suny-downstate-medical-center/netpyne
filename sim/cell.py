"""
cell.py 

Contains cell and population classes 

Version: 2015may26 by salvadordura@gmail.com
"""

from pylab import arange, seed, rand, array
import collections
from neuron import h # Import NEURON
import params as p
import shared as s

###############################################################################
### GENERIC CELL CLASS
###############################################################################
class Cell:
    ''' Generic 'Cell' class used to instantiate individual neurons based on (Harrison & Sheperd, 2105) '''
    def __init__(self, gid, popid, EorI = [], topClass = [], subClass = [], yfrac = [], xloc = [], zloc = []):
        self.gid = gid  # global cell id 
        self.popid = popid  # id of population
        self.EorI = EorI # excitatory or inhibitory 
        self.topClass = topClass # top-level class (IT, PT, CT,...) 
        self.subClass = subClass # subclass (L4, Basket, ...)
        self.yfrac = yfrac  # normalized cortical depth
        self.xloc = xloc  # x location in um
        self.zloc = zloc  # y location in um 
        self.m = []  # NEURON object containing cell model
        
        self.make()  # create cell 
        self.associateGid() # register cell for this node



###############################################################################
### HODGKIN-HUXLEY CELL CLASS
###############################################################################

class HH(Cell):
    ''' Python class for Hodgkin-Huxley cell model'''

    def make (self):
        self.soma = h.Section(name='soma')
        self.soma.diam = 18.8
        self.soma.L = 18.8
        self.soma.Ra = 123.0
        self.soma.insert('hh')
        self.activate()

    def activate (self):
        self.stim = h.IClamp(0.5, sec=self.soma)
        self.stim.amp = 0.1
        self.stim.dur = 0.1

    def associateGid (self):
        s.pc.set_gid2node(self.gid, s.rank) # this is the key call that assigns cell gid to a particular node
        nc = h.NetCon(self.soma(0.5)._ref_v, None, sec=self.soma) # nc determines spike threshold but then discarded
        nc.threshold = p.threshold
        s.pc.cell(self.gid, nc, 1)  # associate a particular output stream of events
        del nc # discard netcon
    
    def addBackground (self):
        self.backgroundRand = h.Random()
        self.backgroundRand.MCellRan4(self.gid,self.gid*2)
        self.backgroundRand.negexp(1)
        self.backgroundSource = h.NetStim() # Create a NetStim
        self.backgroundSource.interval = p.backgroundRate**-1*1e3 # Take inverse of the frequency and then convert from Hz^-1 to ms
        self.backgroundSource.noiseFromRandom(self.backgroundRand) # Set it to use this random number generator
        self.backgroundSource.noise = p.backgroundNoise # Fractional noise in timing
        self.backgroundSource.number = p.backgroundNumber # Number of spikes
        self.backgroundSyn = h.ExpSyn(0,sec=self.soma)
        self.backgroundConn = h.NetCon(self.backgroundSource, self.backgroundSyn) # Connect this noisy input to a cell
        for r in range(p.numReceptors): self.backgroundConn.weight[r]=0 # Initialize weights to 0, otherwise get memory leaks
        self.backgroundConn.weight[0] = p.backgroundWeight[0] # Specify the weight -- 1 is NMDA receptor for smoother, more summative activation
        self.backgroundConn.delay=2 # Specify the delay in ms -- shouldn't make a spot of difference
    
    def record (self):
        # set up voltage recording; recdict will be taken from global context
        for k,v in p.recdict.iteritems():
            try: ptr=eval('self.'+v) # convert string to a pointer to something to record; eval() is unsafe
            except: print 'bad state variable pointer: ',v
            s.simdata[k]['cell_'+str(self.gid)] = h.Vector(p.tstop/p.recordStep+10).resize(0)
            s.simdata[k]['cell_'+str(self.gid)].record(ptr, p.recordStep)



###############################################################################
### IZHIKEVICH 2007a CELL CLASS 
###############################################################################

class Izhi2007a(Cell):
    """
    Python class for the different celltypes of Izhikevich neuron. 

    Equations and parameter values taken from
      Izhikevich EM (2007).
      "Dynamical systems in neuroscience"
      MIT Press

    Equation for synaptic inputs taken from
      Izhikevich EM, Edelman GM (2008).
      "Large-scale model of mammalian thalamocortical systems." 
      PNAS 105(9) 3593-3598.

    Cell types available are based on Izhikevich, 2007 book:
        1. RS - Layer 5 regular spiking pyramidal cell (fig 8.12 from 2007 book)
        2. IB - Layer 5 intrinsically bursting cell (fig 8.19 from 2007 book)
        3. CH - Cat primary visual cortex chattering cell (fig8.23 from 2007 book)
        4. LTS - Rat barrel cortex Low-threshold  spiking interneuron (fig8.25 from 2007 book)
        5. FS - Rat visual cortex layer 5 fast-spiking interneuron (fig8.27 from 2007 book)
        6. TC - Cat dorsal LGN thalamocortical (TC) cell (fig8.31 from 2007 book)
        7. RTN - Rat reticular thalamic nucleus (RTN) cell  (fig8.32 from 2007 book)
    """

    type2007 = collections.OrderedDict([
      #              C    k     vr  vt vpeak   a      b   c    d  celltype
      ('RS',        (100, 0.7,  -60, -40, 35, 0.03,   -2, -50,  100,  1)),
      ('IB',        (150, 1.2,  -75, -45, 50, 0.01,   5, -56,  130,   2)),
      ('CH',        (50,  1.5,  -60, -40, 25, 0.03,   1, -40,  150,   3)),
      ('LTS',       (100, 1.0,  -56, -42, 40, 0.03,   8, -53,   20,   4)),
      ('FS',        (20,  1.0,  -55, -40, 25, 0.2,   -2, -45,  -55,   5)),
      ('TC',        (200, 1.6,  -60, -50, 35, 0.01,  15, -60,   10,   6)),
      ('RTN',       (40,  0.25, -65, -45,  0, 0.015, 10, -55,   50,   7))])


    def make (self):
        # Instantiate cell model 
        self.sec = h.Section()
        if self.topClass in [p.IT, p.PT, p.CT]: # if excitatory cell use RS
            izhType = 'RS' 
        elif self.topClass == p.Pva: # if Pva use FS
            izhType = 'FS' 
        elif self.topClass == p.Sst: # if Sst us LTS
            izhType = 'LTS' 

        self.sec = h.Section(name='izhi2007'+izhType+str(self.gid))  # create Section
        self.m = h.Izhi2007a(0.5, sec=self.sec) # Create a new u,V 2007 neuron at location 0.5 (doesn't matter where) 

    def associateGid (self, threshold = 10.0):
        s.pc.set_gid2node(self.gid, s.rank) # this is the key call that assigns cell gid to a particular node
        nc = h.NetCon(self.m, None) 
        nc.threshold = threshold
        s.pc.cell(self.gid, nc, 1)  # associate a particular output stream of events
        s.gidVec.append(self.gid) # index = local id; value = global id
        s.gidDic[self.gid] = len(s.gidVec)
        del nc # discard netcon

    def addBackground (self):
        self.backgroundRand = h.Random()
        self.backgroundRand.MCellRan4(self.gid,self.gid*2)
        self.backgroundRand.negexp(1)
        self.backgroundSource = h.NetStim() # Create a NetStim
        self.backgroundSource.interval = p.backgroundRate**-1*1e3 # Take inverse of the frequency and then convert from Hz^-1 to ms
        self.backgroundSource.noiseFromRandom(self.backgroundRand) # Set it to use this random number generator
        self.backgroundSource.noise = p.backgroundNoise # Fractional noise in timing
        self.backgroundSource.number = p.backgroundNumber # Number of spikes
        self.backgroundConn = h.NetCon(self.backgroundSource, self.m) # Connect this noisy input to a cell
        for r in range(p.numReceptors): self.backgroundConn.weight[r]=0 # Initialize weights to 0, otherwise get memory leaks
        self.backgroundConn.weight[p.backgroundReceptor] = p.backgroundWeight[0] # Specify the weight -- 1 is NMDA receptor for smoother, more summative activation
        self.backgroundConn.delay=2 # Specify the delay in ms -- shouldn't make a spot of difference


    def record(self):
        # set up voltage recording; recdict will be taken from global context
        for k,v in p.recdict.iteritems():
            try: ptr=eval('self.'+v) # convert string to a pointer to something to record; eval() is unsafe
            except: print 'bad state variable pointer: ',v
            s.simdata[k]['cell_'+str(self.gid)] = h.Vector(p.tstop/p.recordStep+10).resize(0)
            s.simdata[k]['cell_'+str(self.gid)].record(ptr, p.recordStep)


    def __getstate__(self):
        ''' Removes self.soma and self.dummy so can be pickled and sent via py_alltoall'''
        odict = self.__dict__.copy() # copy the dict since we change it
        del odict['m']  # remove fields that cannot be pickled
        del odict['sec']              
        return odict


###############################################################################
### IZHIKEVICH 2007b CELL CLASS 
###############################################################################

class Izhi2007b(Cell):
    """
    Python class for the different celltypes of Izhikevich neuron. 

    Equations and parameter values taken from
      Izhikevich EM (2007).
      "Dynamical systems in neuroscience"
      MIT Press

    Equation for synaptic inputs taken from
      Izhikevich EM, Edelman GM (2008).
      "Large-scale model of mammalian thalamocortical systems." 
      PNAS 105(9) 3593-3598.

    Cell types available are based on Izhikevich, 2007 book:
        1. RS - Layer 5 regular spiking pyramidal cell (fig 8.12 from 2007 book)
        2. IB - Layer 5 intrinsically bursting cell (fig 8.19 from 2007 book)
        3. CH - Cat primary visual cortex chattering cell (fig8.23 from 2007 book)
        4. LTS - Rat barrel cortex Low-threshold  spiking interneuron (fig8.25 from 2007 book)
        5. FS - Rat visual cortex layer 5 fast-spiking interneuron (fig8.27 from 2007 book)
        6. TC - Cat dorsal LGN thalamocortical (TC) cell (fig8.31 from 2007 book)
        7. RTN - Rat reticular thalamic nucleus (RTN) cell  (fig8.32 from 2007 book)
    """

    type2007 = collections.OrderedDict([
      #              C    k     vr  vt vpeak   a      b   c    d  celltype
      ('RS',        (100, 0.7,  -60, -40, 35, 0.03,   -2, -50,  100,  1)),
      ('IB',        (150, 1.2,  -75, -45, 50, 0.01,   5, -56,  130,   2)),
      ('CH',        (50,  1.5,  -60, -40, 25, 0.03,   1, -40,  150,   3)),
      ('LTS',       (100, 1.0,  -56, -42, 40, 0.03,   8, -53,   20,   4)),
      ('FS',        (20,  1.0,  -55, -40, 25, 0.2,   -2, -45,  -55,   5)),
      ('TC',        (200, 1.6,  -60, -50, 35, 0.01,  15, -60,   10,   6)),
      ('RTN',       (40,  0.25, -65, -45,  0, 0.015, 10, -55,   50,   7))])

    def make (self):
        # Instantiate cell model 
        if self.topClass in [p.IT, p.PT, p.CT]: # if excitatory cell use RS
            izhType = 'RS' 
        elif self.topClass == p.Pva: # if Pva use FS
            izhType = 'FS' 
        elif self.topClass == p.Sst: # if Sst us LTS
            izhType = 'LTS' 

        self.sec = h.Section(name='izhi2007'+izhType+str(self.gid))  # create Section
        self.sec.L, self.sec.diam = 6.3, 5  # empirically tuned L and diam 
        self.m = h.Izhi2007b(0.5, sec=self.sec)  # create point process object  
        self.vinit = -60  # set vinit
        self.m.C, self.m.k, self.m.vr, self.m.vt, self.m.vpeak, self.m.a, \
         self.m.b, self.m.c, self.m.d, self.m.celltype = self.type2007[izhType]
        self.m.cellid = self.gid # Cell ID for keeping track which cell this is
        s.fih.append(s.h.FInitializeHandler(self.init))

    def init(self): 
        self.sec.v=-60


    def associateGid (self, threshold = 10.0):
        s.pc.set_gid2node(self.gid, s.rank) # this is the key call that assigns cell gid to a particular node
        nc = h.NetCon(self.sec(0.5)._ref_v, None,sec=self.sec)
        nc.threshold = threshold
        s.pc.cell(self.gid, nc, 1)  # associate a particular output stream of events
        s.gidVec.append(self.gid) # index = local id; value = global id
        s.gidDic[self.gid] = len(s.gidVec)
        del nc # discard netcon


    def addBackground (self):
        self.backgroundRand = h.Random()
        self.backgroundRand.MCellRan4(self.gid,self.gid*2)
        self.backgroundRand.negexp(1)
        self.backgroundSource = h.NetStim() # Create a NetStim
        self.backgroundSource.interval = p.backgroundRate**-1*1e3 # Take inverse of the frequency and then convert from Hz^-1 to ms
        self.backgroundSource.noiseFromRandom(self.backgroundRand) # Set it to use this random number generator
        self.backgroundSource.noise = p.backgroundNoise # Fractional noise in timing
        self.backgroundSource.number = p.backgroundNumber # Number of spikes
        self.backgroundSyn = h.ExpSyn(0,sec=self.sec)
        self.backgroundConn = h.NetCon(self.backgroundSource, self.backgroundSyn) # Connect this noisy input to a cell
        for r in range(p.numReceptors): self.backgroundConn.weight[r]=0 # Initialize weights to 0, otherwise get memory leaks
        self.backgroundConn.weight[p.backgroundReceptor] = p.backgroundWeight[0] # Specify the weight -- 1 is NMDA receptor for smoother, more summative activation
        self.backgroundConn.delay=2 # Specify the delay in ms -- shouldn't make a spot of difference


    def record(self):
        # set up voltage recording; recdict will be taken from global context
        for k,v in p.recdict.iteritems():
            try: ptr=eval('self.'+v) # convert string to a pointer to something to record; eval() is unsafe
            except: print 'bad state variable pointer: ',v
            s.simdata[k]['cell_'+str(self.gid)] = h.Vector(p.tstop/p.recordStep+10).resize(0)
            s.simdata[k]['cell_'+str(self.gid)].record(ptr, p.recordStep)


    def __getstate__(self):
        ''' Removes self.soma and self.dummy so can be pickled and sent via py_alltoall'''
        odict = self.__dict__.copy() # copy the dict since we change it
        del odict['sec']  # remove fields that cannot be pickled
        del odict['dummy']        
        del odict['m']          
        return odict




###############################################################################
### BASIC POP CLASS
###############################################################################

class BasicPop:
    ''' Python class used to instantiate the network population '''

    def __init__(self,  popgid, cellModel, numCells):
        self.popgid = popgid  # id of population
        self.cellModel = cellModel  # cell model for this population
        self.numCells = numCells  # number of cells in this population
        self.cellGids = []  # list of cell gids in this population

    # Function to instantiate Cell objects based on the characteristics of this population
    def createCells(self):
        # select cell class to instantiate cells based on the cellModel attribute
        if self.cellModel == p.Izhi2007b:    cellClass = s.Izhi2007b
        elif self.cellModel == p.HH:    cellClass = s.HH
        else: print 'Unknown cell model'

        # use numCells variable to instantiate cells
        cells = []
        for i in xrange(int(s.rank), self.numCells, s.nhosts):
            gid = s.lastGid+i
            self.cellGids.append(gid)  # add gid list of cells belonging to this population    
            cells.append(cellClass(gid, self.popgid)) # instantiate Cell object
            if p.verbose: print('Cell %d/%d (gid=%d) of pop %d, on node %d, '%(i, self.numCells-1, gid, self.popgid, s.rank))
        s.lastGid = s.lastGid + self.numCells 
        return cells


###############################################################################
### YFRAC POP CLASS
###############################################################################

class YfracPop:
    ''' Pop '''

    def __init__(self,  popgid, cellModel, EorI, topClass, subClass, yfracRange, density):
        self.popgid = popgid  # id of population
        self.EorI = EorI  # excitatory or inhibitory 
        self.topClass = topClass  # top-level class (IT, PT, CT,...) 
        self.subClass = subClass  # subclass (L4, Basket, ...)
        self.yfracRange = yfracRange  # normalized cortical depth
        self.density = density  # cell density function (of yfrac) (in mm^3?)
        self.cellModel = cellModel  # cell model for this population
        self.numCells = 0  # number of cells in this population
        self.cellGids = []  # list of cell gids in this population
        

    # Function to instantiate Cell objects based on the characteristics of this population
    def createCells(self):
        # select cell class to instantiate cells based on the cellModel attribute
        if self.cellModel == p.Izhi2007b:    cellClass = s.Izhi2007b
        elif self.cellModel == p.Izhi2007a:    cellClass = s.Izhi2007a
        elif self.cellModel == p.HH:    cellClass = s.HH
        else: print 'Unknown cell model'

        # use yfrac-dep density if pop object has yfrac and density variables
        cells = []
        volume = p.scale*p.sparseness*(p.modelsize/1e3)**2*((self.yfracRange[1]-self.yfracRange[0])*p.corticalthick/1e3) # calculate num of cells based on scale, density, modelsize and yfracRange
        yfracInterval = 0.001  # interval of yfrac values to evaluate in order to find the max cell density
        maxDensity = max(map(self.density, (arange(self.yfracRange[0],self.yfracRange[1], yfracInterval)))) # max cell density 
        maxCells = volume * maxDensity  # max number of cells based on max value of density func 
        seed(s.id32('%d' % p.randseed))  # reset random number generator
        yfracsAll = self.yfracRange[0] + ((self.yfracRange[1]-self.yfracRange[0])) * rand(int(maxCells), 1) # random yfrac values 
        yfracsProb = array(map(self.density, yfracsAll)) / maxDensity  # calculate normalized density for each yfrac value (used to prune)
        allrands = rand(len(yfracsProb))  # create an array of random numbers for checking each yfrac pos 
        makethiscell = yfracsProb>allrands # perform test to see whether or not this cell should be included (pruning based on density func)
        yfracs = [yfracsAll[i] for i in range(len(yfracsAll)) if i in array(makethiscell.nonzero()[0],dtype='int')] # keep only subset of yfracs based on density func
        self.numCells = len(yfracs)  # final number of cells after pruning of yfrac values based on density func
        if p.verbose: print 'Volume=%.2f, maxDensity=%.2f, maxCells=%.0f, numCells=%.0f'%(volume, maxDensity, maxCells, self.numCells)
        randLocs = rand(self.numCells, 2)  # create random x,z locations
        for i in xrange(int(s.rank), self.numCells, s.nhosts):
            gid = s.lastGid+i
            self.cellGids.append(gid)  # add gid list of cells belonging to this population    
            x = p.modelsize * randLocs[i,0] # calculate x location (um)
            z = p.modelsize * randLocs[i,1] # calculate z location (um) 
            cells.append(cellClass(gid, self.popgid, self.EorI, self.topClass, self.subClass, yfracs[i], x, z)) # instantiate Cell object
            if p.verbose: print('Cell %d/%d (gid=%d) of pop %d, pos=(%2.f, %2.f, %2.f), on node %d, '%(i, self.numCells-1, gid, self.popgid, x, yfracs[i], z, s.rank))
        s.lastGid = s.lastGid + self.numCells 
        return cells

