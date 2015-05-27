"""
cell.py 

Contains cell and population classes 

Version: 2015may26 by salvadordura@gmail.com
"""

from pylab import arange, seed, rand, array
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
### IZHIKEVICH 2007 CELL CLASS
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

    def make (self):
        # Instantiate cell model 
        self.dummy = h.Section()
        if self.topClass in [p.IT, p.PT, p.CT]: # if excitatory cell use RS
            self.m = self.RS(self.dummy, cellid=self.gid)
        elif self.topClass == p.Pva: # if Pva use FS
            self.m = self.FS(self.dummy, cellid=self.gid)
        elif self.topClass == p.Sst: # if Sst us LTS
            self.m = self.LTS(self.dummy, cellid=self.gid)

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


        # recvecs = [h.Vector() for q in range(4)] # Initialize vectors
        # recvecs[0].record(h._ref_t) # Record simulation time
        # recvecs[1].record(self.m._ref_V) # Record cell voltage
        # recvecs[2].record(self.m._ref_u) # Record cell recovery variable
        # recvecs[3].record(self.m._ref_I) # Record cell current
        # s.simdata[('cellTraces_%i'%self.gid)] = array(recvecs)
        # s.simdataVecs.append(('cellTraces_%i'%self.gid))


    def __getstate__(self):
        ''' Removes self.m and self.dummy so can be pickled and sent via py_alltoall'''
        odict = self.__dict__.copy() # copy the dict since we change it
        del odict['m']  # remove fields that cannot be pickled
        del odict['dummy']              
        return odict

    ## Create basic Izhikevich neuron with default parameters -- not to be called directly, only via one of the other functions
    def createcell(self, section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid):
        from neuron import h # Open NEURON
        cell = h.Izhi2007a(0,sec=section) # Create a new Izhikevich neuron at location 0 (doesn't matter where) in h.Section() "section"
        cell.C = C # Capacitance
        cell.k = k
        cell.vr = vr # Resting membrane potential
        cell.vt = vt # Membrane threhsold
        cell.vpeak = vpeak # Peak voltage
        cell.a = a
        cell.b = b
        cell.c = c
        cell.d = d
        cell.celltype = celltype # Set cell celltype (used for setting celltype-specific dynamics)
        cell.cellid = cellid # Cell ID for keeping track which cell this is
        cell.t0 = .0
        return cell

    ## Cell types based on Izhikevich, 2007 book
    ## Layer 5 regular spiking (RS) pyramidal cell (fig 8.12 from 2007 book)
    def RS(self, section, C=100, k=0.7, vr=-60, vt=-40, vpeak=35, a=0.03, b=-2, c=-50, d=100, celltype=1, cellid=-1):
        cell = self.createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
        return cell

    ## Layer 5 intrinsically bursting (IB) cell (fig 8.19 from 2007 book)
    def IB(self, section, C=150, k=1.2, vr=-75, vt=-45, vpeak=50, a=0.01, b=5, c=-56, d=130, celltype=2, cellid=-1):
        cell = self.createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
        return cell

    ## Cat primary visual cortex chattering (CH) cell (fig8.23 from 2007 book)
    def CH(self, section, C=50, k=1.5, vr=-60, vt=-40, vpeak=25, a=0.03, b=1, c=-40, d=150, celltype=3, cellid=-1):
        cell = self.createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
        return cell

    ## Rat barrel cortex Low-threshold  spiking (LTS) interneuron (fig8.25 from 2007 book)
    def LTS(self, section, C=100, k=1, vr=-56, vt=-42, vpeak=40, a=0.03, b=8, c=-53, d=20, celltype=4, cellid=-1):
        cell = self.createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
        return cell

    ## layer 5 rat visual cortex fast-spiking (FS) interneuron (fig8.27 from 2007 book)
    def FS(self, section, C=20, k=1, vr=-55, vt=-40, vpeak=25, a=0.2, b=-2, c=-45, d=-55, celltype=5, cellid=-1):
        cell = self.createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
        return cell

    ## Cat dorsal LGN thalamocortical (TC) cell (fig8.31 from 2007 book)
    def TC(self, section, C=200, k=1.6, vr=-60, vt=-50, vpeak=35, a=0.01, b=15, c=-60, d=10, celltype=6, cellid=-1):
        cell = self.createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
        return cell

    ## Rat reticular thalamic nucleus (RTN) cell  (fig8.32 from 2007 book)
    def RTN(self, section, C=40, k=0.25, vr=-65, vt=-45, vpeak=0, a=0.015, b=10, c=-55, d=50, celltype=7, cellid=-1):
        cell = self.createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
        return cell



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
        if self.cellModel == p.Izhi2007a:    cellClass = s.Izhi2007a
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
        if self.cellModel == p.Izhi2007a:    cellClass = s.Izhi2007a
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

