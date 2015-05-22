import params as p
import shared as s

###############################################################################
### CELL CLASS
###############################################################################

# definition of python class 'Cell' used to instantiate individual neurons
# based on (Harrison & Sheperd, 2105)
class Cell:
    def __init__(self, gid, popid, EorI, topClass, subClass, yfrac, xloc, zloc, cellModel, s):
        self.gid = gid  # global cell id 
        self.popid = popid  # id of population
        self.EorI = EorI # excitatory or inhibitory 
        self.topClass = topClass # top-level class (IT, PT, CT,...) 
        self.subClass = subClass # subclass (L4, Basket, ...)
        self.yfrac = yfrac  # normalized cortical depth
        self.xloc = xloc  # x location in um
        self.zloc = zloc  # y location in um 
        self.cellModel = cellModel  # type of cell model (eg. Izhikevich, Friesen, HH ...)
        self.m = []  # NEURON object containing cell model
        
        self.make()  # create cell 
        self.associateGid(s) # register cell for this node

    def make (self):
        # Instantiate cell model (eg. Izhi2007 point process, HH MC, ...)
        if self.cellModel == l.Izhi2007: # Izhikevich 2007 neuron model
            self.dummy = h.Section()
            if self.topClass in range(0,3): # if excitatory cell use RS
                self.m = izhi.RS(self.dummy, cellid=self.gid)
            elif self.topClass == l.Pva: # if Pva use FS
                self.m = izhi.FS(self.dummy, cellid=self.gid)
            elif self.topClass == l.Sst: # if Sst us LTS
                self.m = izhi.LTS(self.dummy, cellid=self.gid)
        else:
            print('Selected cell model %d not yet implemented' % (self.cellModel))

    def associateGid (self, s, threshold = 10.0):
        s.pc.set_gid2node(self.gid, s.rank) # this is the key call that assigns cell gid to a particular node
        if self.cellModel == l.Izhi2007:
            nc = h.NetCon(self.m, None) 
        else:
            nc = h.NetCon(self.soma(0.5)._ref_v, None, sec=self.m) # nc determines spike threshold but then discarded
        nc.threshold = threshold
        s.pc.cell(self.gid, nc, 1)  # associate a particular output stream of events
        s.gidVec.append(self.gid) # index = local id; value = global id
        s.gidDic[self.gid] = len(s.gidVec)
        del nc # discard netcon
        # print "node:",s.rank
        # print "gid:",self.gid

    def record(self):
        # set up voltage recording; acc and recdict will be taken from global context
        # for k,v in recdict.iteritems():
        # try: ptr=eval('self.'+v) # convert string to a pointer to something to record; eval() is unsafe
        # except: print 'bad state variable pointer: ',v
        # acc[(k, self.gid)] = h.Vector(h.tstop/Dt+10).resize(0)
        # acc[(k, self.gid)].record(ptr, Dt)
        # recvecs = [h.Vector() for q in range(s.nquantities)] # Initialize vectors
        # recvecs[0].record(h._ref_t) # Record simulation time
        # recvecs[1].record(s.cells[c]._ref_V) # Record cell voltage
        # recvecs[2].record(s.cells[c]._ref_u) # Record cell recovery variable
        # recvecs[3].record(s.cells[c]._ref_I) # Record cell current
        pass


    def __getstate__(self):
        ''' Removes self.m and self.dummy so can be pickled and sent via py_alltoall'''
        odict = self.__dict__.copy() # copy the dict since we change it
        del odict['m']  # remove fields that cannot be pickled
        del odict['dummy']              
        return odict


class Izhi(Cell):
    """
    IZHI

    Python wrappers for the different celltypes of Izhikevich neuron. 

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


    Usage example:
        from neuron import h
        from izhi import pyramidal
        dummy = h.Section()
        cell = pyramidal(dummy)

    Version: 2013oct16 by cliffk
    Version: 2015mar30 by Salvador Dura-Bernal (salvadordura@gmail.com)
    """

    ## Create basic Izhikevich neuron with default parameters -- not to be called directly, only via one of the other functions
    def createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid):
        from neuron import h # Open NEURON
        cell = h.Izhi2007(0,sec=section) # Create a new Izhikevich neuron at location 0 (doesn't matter where) in h.Section() "section"
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
    def RS(section, C=100, k=0.7, vr=-60, vt=-40, vpeak=35, a=0.03, b=-2, c=-50, d=100, celltype=1, cellid=-1):
        cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
        return cell

    ## Layer 5 intrinsically bursting (IB) cell (fig 8.19 from 2007 book)
    def IB(section, C=150, k=1.2, vr=-75, vt=-45, vpeak=50, a=0.01, b=5, c=-56, d=130, celltype=2, cellid=-1):
        cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
        return cell

    ## Cat primary visual cortex chattering (CH) cell (fig8.23 from 2007 book)
    def CH(section, C=50, k=1.5, vr=-60, vt=-40, vpeak=25, a=0.03, b=1, c=-40, d=150, celltype=3, cellid=-1):
        cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
        return cell

    ## Rat barrel cortex Low-threshold  spiking (LTS) interneuron (fig8.25 from 2007 book)
    def LTS(section, C=100, k=1, vr=-56, vt=-42, vpeak=40, a=0.03, b=8, c=-53, d=20, celltype=4, cellid=-1):
        cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
        return cell

    ## layer 5 rat visual cortex fast-spiking (FS) interneuron (fig8.27 from 2007 book)
    def FS(section, C=20, k=1, vr=-55, vt=-40, vpeak=25, a=0.2, b=-2, c=-45, d=-55, celltype=5, cellid=-1):
        cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
        return cell

    ## Cat dorsal LGN thalamocortical (TC) cell (fig8.31 from 2007 book)
    def TC(section, C=200, k=1.6, vr=-60, vt=-50, vpeak=35, a=0.01, b=15, c=-60, d=10, celltype=6, cellid=-1):
        cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
        return cell

    ## Rat reticular thalamic nucleus (RTN) cell  (fig8.32 from 2007 book)
    def RTN(section, C=40, k=0.25, vr=-65, vt=-45, vpeak=0, a=0.015, b=10, c=-55, d=50, celltype=7, cellid=-1):
        cell = createcell(section, C, k, vr, vt, vpeak, a, b, c, d, celltype, cellid)
        return cell