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
