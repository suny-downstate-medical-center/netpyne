"""
cell.py 

Contains Synapse, Conn, Cell and Population classes 

Contributors: salvadordura@gmail.com
"""

from pylab import arange, seed, rand, array
import collections
from neuron import h # Import NEURON
import shared as s


###############################################################################
#
# SYNAPSE CLASS
#
###############################################################################

class Synapse(object):
    ''' Class used to instantiate synapses inside a Cell object''' 
    def __init__(self, postGid, postSect=None, sectObj, synParams):
        self.postGid = postGid
        self.postSect = postSect
        self.synm = getattr(h, synParams['type'])(loc=synParams['loc'], sec=sectObj)
        for paramName,paramValue in synParams.iteritems():
            if paramName not in ['type','loc']:
                setattr(self, paramName, paramValue)
    



###############################################################################
#
# CONNECTION CLASS
#
###############################################################################
class Conn(object):
    ''' Class used to instantiate connections inside a Cell object''' 
    def connect(self, preGid, delay, weight):
        self.preGid = preGid  
        self.delay = delay
        self.weight = weight
        self.netcon = s.pc.gid_connect(preGid, self.synm)  # create Netcon between global gid and local cell object
        self.netcon.delay = delay  # set Netcon delay
        for i in range(s.net.param['numReceptors']): self.netcon.weight[i] = weight[i]  # set Netcon weights
        if p.sim['verbose']: print('Created Conn pre=%d post=%d delay=%0.2f, weights=[%.2f, %.2f, %.2f, %.2f]'\
            %(self.preGid, self.postGid, self.delay, weight[0], weight[1], weight[2], weight[3] ))
        pass


###############################################################################
#
# GENERIC CELL CLASS
#
###############################################################################

class Cell(object):
    ''' Generic 'Cell' class used to instantiate individual neurons based on (Harrison & Sheperd, 2105) '''
    
    def __init__(self, gid, tags):
        self.gid = gid  # global cell id 
        self.tags = tags  # dictionary of cell tags/attributes 
        self.syns = {}  # dict of Synapse objects

        self.make()  # create cell 
        self.associateGid() # register cell for this node


    def associateGid (self, threshold = 10.0):
        s.pc.set_gid2node(self.gid, s.rank) # this is the key call that assigns cell gid to a particular node
        nc = h.NetCon(self.soma(0.5)._ref_v, None, sec=self.soma)
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
        self.backgroundSource.interval = s.net.param['backgroundRate']**-1*1e3 # Take inverse of the frequency and then convert from Hz^-1 to ms
        self.backgroundSource.noiseFromRandom(self.backgroundRand) # Set it to use this random number generator
        self.backgroundSource.noise = s.net.param['backgroundNoise'] # Fractional noise in timing
        self.backgroundSource.number = s.net.param['backgroundNumber'] # Number of spikes
        self.backgroundSyn = h.ExpSyn(0,sec=self.soma)
        self.backgroundConn = h.NetCon(self.backgroundSource, self.backgroundSyn) # Connect this noisy input to a cell
        for r in range(s.net.param['numReceptors']): self.backgroundConn.weight[r]=0 # Initialize weights to 0, otherwise get memory leaks
        self.backgroundConn.weight[0] = s.net.param['backgroundWeight'][0] # Specify the weight -- 1 is NMDA receptor for smoother, more summative activation
        self.backgroundConn.delay=2 # Specify the delay in ms -- shouldn't make a spot of difference

    
    def record (self):
        # set up voltage recording; recdict will be taken from global context
        for k,v in p.sim['recdict'].iteritems():
            try: ptr=eval('self.'+v) # convert string to a pointer to something to record; eval() is unsafe
            except: print 'bad state variable pointer: ',v
            s.simdata[k]['cell_'+str(self.gid)] = h.Vector(p.sim['tstop']/p.sim['recordStep']+10).resize(0)
            s.simdata[k]['cell_'+str(self.gid)].record(ptr, p.sim['recordStep'])




    def __getstate__(self): # MAKE GENERIC! REMOVE ALL NON-PICKABLE OBJECTS!!
        ''' Removes self.soma and self.dummy so can be pickled and sent via py_alltoall'''
        odict = self.__dict__.copy() # copy the dict since we change it
        del odict['sec']  # remove fields that cannot be pickled       
        del odict['m']     
        return odict



###############################################################################
#
# HODGKIN-HUXLEY CELL CLASS
#
###############################################################################

class HH(Cell):
    ''' Python class for Hodgkin-Huxley cell model'''

    def make(self):
        for key,val in s.net.param['cellParams'].iteritems():  # for each set of cell params 
            conditionsMet = 1
            for (condKey,condVal) in zip(key[0::2], key[1::2]):  # check if all conditions in key tuple are met
                if self.tags[condKey] != condVal: 
                    conditionsMet = 0
                    break
            if conditionsMet:  # if all conditions are met, set values for this cell
                self.setParams(val)


    def setParams(self, params):
        # set params for all sections
        for sectName,sectParams in params['sections'].iteritems(): 
            # create section
            if sectName not in self.__dict__:
                self.__dict__[sectName] = h.Section(name=sectName)  # create Neuron section object if doesn't exist
            sect = self.__dict__[sectName]  # pointer
            
            # add mechanisms 
            for mechName,mechParams in sect['mechs'].iteritems():  
                if mechName not in sect.__dict__: 
                    sect(0.5).insert(mechName)
                for mechParamName,mechParamValue in mechParams:  # add params of the mechanism
                    setattr(sect(0.5).__dict__[mechName], mechParamName, mechParamValue)

            # add synapses 
            if sect['syns']:  
                for synName,synParams in sect['syns'].iteritems():
                    self.syns[(sectName,synName)] = s.Synapse(sect=sect, postGid=self.gid, postSect=sectName, synParams=synParams)

            # set geometry params 
            for geomParamName,geomParamValue in sect['geom'].iteritems():  
                    if not type(geomParamValue) in [list, dict]:  # skip any list or dic params
                        setattr(sect(0.5), geomParamName, geomParamValue)

            # set 3d geometry
            if ['geom']['pt3d']:  
                h.pt3dclear(sec=sect)
                x = self.tags['x']
                y = self.tags['yfrac'] * s.net.param['corticalthick']/1e3  # y as a func of yfrac and cortical thickness
                z = self.tags['z']
                for pt3d in sect['geom']['pt3d']:
                    h.pt3dadd(x+pt3d['x'], y+pt3d['y'], z+pt3d['z'], pt3d['d'], sec=sect)

        # set topology 
        for sectName,sectParams in params['sections'].iteritems():  # iterate sects again for topology (ensures all exist)
            sect = self.__dict__[sectName]  # pointer to child sec
            sect.connect(self.__dict__[sect['topol']['parentSec']], sect['topol']['parentX'], sect['topol']['childX'])  # make topol connection
   

    def activate (self):
        self.stim = h.IClamp(0.5, sec=self.soma)
        self.stim.amp = 0.1
        self.stim.dur = 0.1




###############################################################################
#
# IZHIKEVICH 2007a CELL CLASS (Euler explicit integration; include synapses)
#
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
        # Instantiate cell model based on cellType
        if self.tags['cellType'] in ['IT', 'PT', 'CT']: # if excitatory cell use RS
            izhType = 'RS' 
        elif self.tags['cellType'] == 'PV': # if Pva use FS
            izhType = 'FS' 
        elif self.tags['cellType'] == 'SOM': # if Sst us LTS
            izhType = 'LTS' 

        self.sec = h.Section(name='izhi2007a'+izhType+str(self.gid))  # create Section
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
        self.backgroundSource.interval = s.net.param['backgroundRate']**-1*1e3 # Take inverse of the frequency and then convert from Hz^-1 to ms
        self.backgroundSource.noiseFromRandom(self.backgroundRand) # Set it to use this random number generator
        self.backgroundSource.noise = s.net.param['backgroundNoise'] # Fractional noise in timing
        self.backgroundSource.number = s.net.param['backgroundNumber'] # Number of spikes
        self.backgroundConn = h.NetCon(self.backgroundSource, self.m) # Connect this noisy input to a cell
        for r in range(s.net.param['numReceptors']): self.backgroundConn.weight[r]=0 # Initialize weights to 0, otherwise get memory leaks
        self.backgroundConn.weight[s.net.param['backgroundReceptor']] = s.net.param['backgroundWeight'][0] # Specify the weight -- 1 is NMDA receptor for smoother, more summative activation
        self.backgroundConn.delay=2 # Specify the delay in ms -- shouldn't make a spot of difference


    def record(self):
        # set up voltage recording; recdict will be taken from global context
        for k,v in p.sim['recdict'].iteritems():
            try: ptr=eval('self.'+v) # convert string to a pointer to something to record; eval() is unsafe
            except: print 'bad state variable pointer: ',v
            s.simdata[k]['cell_'+str(self.gid)] = h.Vector(p.sim['tstop']/p.sim['recordStep']+10).resize(0)
            s.simdata[k]['cell_'+str(self.gid)].record(ptr, p.sim['recordStep'])



###############################################################################
#
# IZHIKEVICH 2007b CELL CLASS (integrates STATE u; v in Section)
#
###############################################################################

class izhi2007b(Cell):
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

    # Izhikevich equation parameters for the different cell types
    type2007 = collections.OrderedDict([
      #              C    k     vr  vt vpeak   a      b   c    d  celltype
      ('paramNames',('C', 'k', 'vr', 'vt', 'vpeak', 'a', 'b', 'c', 'd', 'celltype')),
      ('RS',        (100, 0.7,  -60, -40, 35, 0.03,   -2, -50,  100,  1)),
      ('IB',        (150, 1.2,  -75, -45, 50, 0.01,   5, -56,  130,   2)),
      ('CH',        (50,  1.5,  -60, -40, 25, 0.03,   1, -40,  150,   3)),
      ('LTS',       (100, 1.0,  -56, -42, 40, 0.03,   8, -53,   20,   4)),
      ('FS',        (20,  1.0,  -55, -40, 25, 0.2,   -2, -45,  -55,   5)),
      ('TC',        (200, 1.6,  -60, -50, 35, 0.01,  15, -60,   10,   6)),
      ('RTN',       (40,  0.25, -65, -45,  0, 0.015, 10, -55,   50,   7))])


    def setParams(self, params):
        # set params for soma 
        sectName = 'soma'  # selected section for Izhi mechanism

        if sectName in params['sections'].iterkeys():  # if soma is included in the cell params
            
            # create section
            if sectName not in self.__dict__:  
                self.soma = h.Section(name=sectName+params['Izhi2007'])
                sect = self.soma

            # set geometry params 
            for geomParamName,geomParamValue in sect['geom'].iteritems():  
                    if not type(geomParamValue) in [list, dict]:  # skip any list or dic params
                        setattr(sect(0.5), geomParamName, geomParamValue)

            # create Izhi object
            if 'izh' not in self.__dict__:
                self.izh = h.Izhi2007b(0.5, sec=sect)

            # set Izhi params
            izhParamNames = self.type2007['paramNames']
            izhParamValues = self.type2007[params['Izhi2007Type']]
            for (izhParamName, izhParamValue) in zip(izhParamNames, izhParamValues):
                setattr(self.izh, izhParamName, izhParamValue)
            self.izh.vinit = izhParamValues['vr']  # check if can make vinit part of the type2007 params
            self.izh.cellid = self.gid 
            s.fih.append(s.h.FInitializeHandler(self.init))  # check why this is needed

            # add synapses 
            if sect['syns']:  
                for synName,synParams in sect['syns'].iteritems():
                    self.syns[(sectName,synName)] = s.Synapse(sect=sect, postGid=self.gid, postSect=sectName, synParams=synParams)

        else: 
            print 'Error: soma section not found for Izhi2007 model'

    def init(self): 
        self.soma.v = -60  # check why this is needed



###############################################################################
### POP CLASS
###############################################################################

class Pop(object):
    ''' Python class used to instantiate the network population '''
    def __init__(self,  tags):
        self.tags = tags # list of tags/attributes of population (eg. numCells, cellModel,...)
        self.cellGids = []  # list of cell gids beloging to this pop

    # Function to instantiate Cell objects based on the characteristics of this population
    def createCells(self):
        # select cell class to instantiate cells based on the cellModel tag
        cellClass = getattr(s, self.tags['cellModel']) 

        # population based on numCells
        if 'numCells' in self.tags:
            cells = []
            for i in xrange(int(s.rank), self.tags['numCells'], s.nhosts):
                cellTags = {}
                gid = s.lastGid+i
                cells.append(cellClass(gid, cellTags)) # instantiate Cell object
                if p.sim['verbose']: print('Cell %d/%d (gid=%d) of pop %d, on node %d, '%(i, self.tags['numCells']-1, gid, i, s.rank))
            s.lastGid = s.lastGid + self.tags['numCells'] 
            return cells

        # population based on yFracRange
        elif 'yFracRange' in self.tags:
            # use yfrac-dep density if pop object has yfrac and density variables
            cells = []
            volume = s.net.param['scale'] * s.net.param['sparseness'] * (s.net.param['modelsize']/1e3)**2 \
                 * ((self.tags['yfracRange'][1]-self.tags['yfracRange'][0]) * s.net.param['corticalthick']/1e3)  # calculate num of cells based on scale, density, modelsize and yfracRange
            yfracInterval = 0.001  # interval of yfrac values to evaluate in order to find the max cell density
            maxDensity = max(map(self.tags['density'], (arange(self.tags['yfracRange'][0],self.tags['yfracRange'][1], yfracInterval))))  # max cell density 
            maxCells = volume * maxDensity  # max number of cells based on max value of density func 
            
            seed(s.id32('%d' % p.sim['randseed']))  # reset random number generator
            yfracsAll = self.tags['yfracRange'][0] + ((self.tags['yfracRange'][1]-self.tags['yfracRange'][0])) * rand(int(maxCells), 1)  # random yfrac values 
            yfracsProb = array(map(self.tags['density'], self.tags['yfracsAll'])) / maxDensity  # calculate normalized density for each yfrac value (used to prune)
            allrands = rand(len(yfracsProb))  # create an array of random numbers for checking each yfrac pos 
            
            makethiscell = yfracsProb>allrands  # perform test to see whether or not this cell should be included (pruning based on density func)
            yfracs = [yfracsAll[i] for i in range(len(yfracsAll)) if i in array(makethiscell.nonzero()[0],dtype='int')] # keep only subset of yfracs based on density func
            self.tags['numCells'] = len(yfracs)  # final number of cells after pruning of yfrac values based on density func
            
            if p.sim['verbose']: print 'Volume=%.2f, maxDensity=%.2f, maxCells=%.0f, numCells=%.0f'%(volume, maxDensity, maxCells, self.tags['numCells'])
            randLocs = rand(self.tags['numCells'], 2)  # create random x,z locations

            for i in xrange(int(s.rank), self.tags['numCells'], s.nhosts):
                gid = s.lastGid+i
                self.cellGids.append(gid)  # add gid list of cells belonging to this population - not needed?
                cellTags = {k: v for (k, v) in self.tags.iteritems() if k not in ['yFracRange', 'density']}  # copy all pop tags to cell tags, except those that are pop-specific
                cellTags['yfrac'] = yfracs[i]  # set yfrac value for this cell
                cellTags['x'] = s.net.param['modelsize'] * randLocs[i,0]  # calculate x location (um)
                cellTags['z'] = s.net.param['modelsize'] * randLocs[i,1]  # calculate z location (um)
                cellTags['pop'] =  
                cells.append(cellClass(gid, cellTags)) # instantiate Cell object
                if p.sim['verbose']: print('Cell %d/%d (gid=%d) of pop %d, pos=(%2.f, %2.f, %2.f), on node %d, '%(i, self.numCells-1, gid, cellTags['x'], cellTags['yfrac'], cellTags['z'], s.rank))
            s.lastGid = s.lastGid + self.numCells 
            return cells

