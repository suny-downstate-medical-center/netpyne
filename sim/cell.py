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
# GENERIC CELL CLASS
#
###############################################################################

class Cell(object):
    ''' Generic 'Cell' class used to instantiate individual neurons based on (Harrison & Sheperd, 2105) '''
    
    def __init__(self, gid, tags):
        self.gid = gid  # global cell id 
        self.tags = tags  # dictionary of cell tags/attributes 
        self.secs = {}  # dict of sections
        self.conns = []  # list of connections
        self.stims = []  # list of stimuli

        self.make()  # create cell 
        self.associateGid() # register cell for this node

    def make(self):
        for prop in s.net.params['cellProps']:  # for each set of cell properties
            conditionsMet = 1
            for (condKey,condVal) in prop['conditions'].iteritems():  # check if all conditions are met
                if self.tags[condKey] != condVal: 
                    conditionsMet = 0
                    break
            if conditionsMet:  # if all conditions are met, set values for this cell
                if 'propList' not in self.tags:
                    self.tags['propList'] = [prop['label']] # create list of property sets
                else:
                    self.tags['propList'].append(prop['label'])  # add label of cell property set to list of property sets for this cell
                if s.cfg['createPyStruct']:
                    self.createPyStruct(prop)
                if s.cfg['createNEURONObj']:
                    self.createNEURONObj(prop)  # add sections, mechanisms, synapses, geometry and topolgy specified by this property set


    def associateGid (self, threshold = 10.0):
        s.pc.set_gid2node(self.gid, s.rank) # this is the key call that assigns cell gid to a particular node
        nc = h.NetCon(self.secs['soma']['hSection'](0.5)._ref_v, None, sec=self.secs['soma']['hSection'])
        nc.threshold = threshold
        s.pc.cell(self.gid, nc, 1)  # associate a particular output stream of events
        s.gidVec.append(self.gid) # index = local id; value = global id
        s.gidDic[self.gid] = len(s.gidVec)
        del nc # discard netcon



    def addConn(self, connParams):
        self.conns.append(connParams)
        netcon = s.pc.gid_connect(connParams['preGid'], self.secs[connParams['sec']][connParams['synReceptor']]['hSyn']) # create Netcon between global gid and local cell object
        netcon.weight = connParams['weight']  # set Netcon weight
        netcon.delay = connParams['delay']  # set Netcon delay
        self.conns[-1]['hNetcon'] = netcon  # add netcon object to dict in conns list
        if s.cfg['verbose']: print('Created Conn pre=%d post=%d'%(connParams['preGid'], connParams['postGid']))



    def addBackground (self):
        self.backgroundRand = h.Random()
        self.backgroundRand.MCellRan4(self.gid,self.gid*2)
        self.backgroundRand.negexp(1)
        self.backgroundSource = h.NetStim() # Create a NetStim
        self.backgroundSource.interval = s.net.params['backgroundRate']**-1*1e3 # Take inverse of the frequency and then convert from Hz^-1 to ms
        self.backgroundSource.noiseFromRandom(self.backgroundRand) # Set it to use this random number generator
        self.backgroundSource.noise = s.net.params['backgroundNoise'] # Fractional noise in timing
        self.backgroundSource.number = s.net.params['backgroundNumber'] # Number of spikes
        self.backgroundSyn = h.ExpSyn(0,sec=self.soma)
        self.backgroundConn = h.NetCon(self.backgroundSource, self.backgroundSyn) # Connect this noisy input to a cell
        for r in range(s.net.params['numReceptors']): self.backgroundConn.weight[r]=0 # Initialize weights to 0, otherwise get memory leaks
        self.backgroundConn.weight[0] = s.net.params['backgroundWeight'][0] # Specify the weight -- 1 is NMDA receptor for smoother, more summative activation
        self.backgroundConn.delay=2 # Specify the delay in ms -- shouldn't make a spot of difference

    
    def record (self):
        # set up voltagse recording; recdict will be taken from global context
        for k,v in s.cfg['recdict'].iteritems():
            try: ptr=eval('self.'+v) # convert string to a pointer to something to record; eval() is unsafe
            except: print 'bad state variable pointer: ',v
            s.simdata[k]['cell_'+str(self.gid)] = h.Vector(s.cfg['tstop']/s.cfg['recordStep']+10).resize(0)
            s.simdata[k]['cell_'+str(self.gid)].record(ptr, s.cfg['recordStep'])


    def __getstate__(self): 
        ''' Removes non-picklable h objects so can be pickled and sent via py_alltoall'''
        odict = self.__dict__.copy() # copy the dict since we change it
        odict = s.replaceItemObj(odict, keystart='h', newval=None)  # replace h objects with None so can be pickled
        return odict



###############################################################################
#
# HODGKIN-HUXLEY CELL CLASS
#
###############################################################################

class HH(Cell):
    ''' Python class for Hodgkin-Huxley cell model'''

    def createPyStruct(self, prop):
        # set params for all sections
        for sectName,sectParams in prop['sections'].iteritems(): 
            # create section
            if sectName not in self.secs:
                self.secs[sectName] = {}  # create section dict
            sec = self.secs[sectName]  # pointer to section
            
            # add mechanisms 
            for mechName,mechParams in sectParams['mechs'].iteritems(): 
                if 'mech' not in sec:
                    sec['mech'] = {}
                if mechName not in sec['mech']: 
                    sec['mech'][mechName] = {}  
                for mechParamName,mechParamValue in mechParams.iteritems():  # add params of the mechanism
                    sec['mech'][mechName][mechParamName] = mechParamValue

            # add synapses 
            for synName,synParams in sectParams['syns'].iteritems(): 
                if 'syn' not in sec:
                    sec['syn'] = {}
                if synName not in sec['syn']:
                    sec['syn'][synName] = {}
                for synParamName,synParamValue in synParams.iteritems():  # add params of the synapse
                    sec['syn'][synName][synParamName] = synParamValue

            # add geometry params 
            for geomParamName,geomParamValue in sectParams['geom'].iteritems():  
                if 'geom' not in sec:
                    sec['geom'] = {}
                if not type(geomParamValue) in [list, dict]:  # skip any list or dic params
                    sec['geom'][geomParamName] = geomParamValue

            # add 3d geometry
            if sectParams['geom']['pt3d']:
                if 'pt3d' not in sec['geom']:  
                    sec['geom']['pt3d'] = []
                for pt3d in sectParams['geom']['pt3d']:
                    sec['geom']['pt3d'].append(pt3d)

            # add topolopgy params
            if sectParams['topol']:
                if 'topol' not in sec:
                    sec['topol'] = {}
                for topolParamName,topolParamValue in sectParams['topol'].iteritems(): 
                    sec['topol'][topolParamName] = topolParamValue
              
   
    def createNEURONObj(self, prop):
        # set params for all sections
        for sectName,sectParams in prop['sections'].iteritems(): 
            # create section
            if sectName not in self.secs:
                self.secs[sectName] = {}  # create sect dict if doesn't exist
            self.secs[sectName]['hSection'] = h.Section(name=sectName)  # create h Section object
            sec = self.secs[sectName]  # pointer to section
            
            # add mechanisms 
            for mechName,mechParams in sectParams['mechs'].iteritems():  
                if mechName not in sec['mech']: 
                    sec['mech'][mechName] = {}
                sec['hSection'].insert(mechName)
                for mechParamName,mechParamValue in mechParams.iteritems():  # add params of the mechanism
                    sec['hSection'](0.5).__getattribute__(mechName).__setattr__(mechParamName,mechParamValue)
                
            # add synapses 
            for synName,synParams in sectParams['syns'].iteritems(): 
                if synName not in sec['syn']:
                    sec['syn'][synName] = {} 
                synObj = getattr(h, synParams['type'])
                sec['syn'][synName]['hSyn'] = synObj(synParams['loc'], sec = sec['hSection'])  # create h Syn object (eg. h.Ex)
                for synParamName,synParamValue in synParams.iteritems():  # add params of the synapse
                    if synParamName not in ['type','loc']:
                        setattr(sec['syn'][synName]['hSyn'], synParamName, synParamValue)

            # set geometry params 
            for geomParamName,geomParamValue in sectParams['geom'].iteritems():  
                if not type(geomParamValue) in [list, dict]:  # skip any list or dic params
                    setattr(sec['hSection'], geomParamName, geomParamValue)

            # set 3d geometry
            if sectParams['geom']['pt3d']:  
                h.pt3dclear(sec=sec['hSection'])
                x = self.tags['x']
                y = self.tags['yfrac'] * s.net.params['corticalthick']/1e3  # y as a func of yfrac and cortical thickness
                z = self.tags['z']
                for pt3d in sectParams['geom']['pt3d']:
                    h.pt3dadd(x+pt3d['x'], y+pt3d['y'], z+pt3d['z'], pt3d['d'], sec=sec['hSection'])

        # set topology 
        for sectName,sectParams in prop['sections'].iteritems():  # iterate sects again for topology (ensures all exist)
            sec = self.secs[sectName]  # pointer to section # pointer to child sec
            if sectParams['topol']:
                sec['hSection'].connect(self.secs[sectParams['topol']['parentSec']]['hSection'], sectParams['topol']['parentX'], sectParams['topol']['childX'])  # make topol connection


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
        self.backgroundSource.interval = s.net.params['backgroundRate']**-1*1e3 # Take inverse of the frequency and then convert from Hz^-1 to ms
        self.backgroundSource.noiseFromRandom(self.backgroundRand) # Set it to use this random number generator
        self.backgroundSource.noise = s.net.params['backgroundNoise'] # Fractional noise in timing
        self.backgroundSource.number = s.net.params['backgroundNumber'] # Number of spikes
        self.backgroundConn = h.NetCon(self.backgroundSource, self.m) # Connect this noisy input to a cell
        for r in range(s.net.params['numReceptors']): self.backgroundConn.weight[r]=0 # Initialize weights to 0, otherwise get memory leaks
        self.backgroundConn.weight[s.net.params['backgroundReceptor']] = s.net.params['backgroundWeight'][0] # Specify the weight -- 1 is NMDA receptor for smoother, more summative activation
        self.backgroundConn.delay=2 # Specify the delay in ms -- shouldn't make a spot of difference


    def record(self):
        # set up voltagse recording; recdict will be taken from global context
        for k,v in s.cfg['recdict'].iteritems():
            try: ptr=eval('self.'+v) # convert string to a pointer to something to record; eval() is unsafe
            except: print 'bad state variable pointer: ',v
            s.simdata[k]['cell_'+str(self.gid)] = h.Vector(s.cfg['tstop']/s.cfg['recordStep']+10).resize(0)
            s.simdata[k]['cell_'+str(self.gid)].record(ptr, s.cfg['recordStep'])



###############################################################################
#
# IZHIKEVICH 2007b CELL CLASS (integrates STATE u; v in Section)
#
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


    def createPyStruct(self, prop):
        # set params for soma 
        sectName = 'soma'  # selected section by default for Izhi mechanism

        if sectName in prop['sections'].iterkeys():  # if soma is included in the cell params
            # create section
            if sectName not in self.secs:
                self.secs[sectName] = {}  # create h Section object
            sectParams = prop['sections'][sectName]  # pointer to section parameters
            sec = self.secs[sectName]  # pointer to Section

            # set geometry params 
            for geomParamName,geomParamValue in sectParams['geom'].iteritems():   
                if 'geom' not in sec:
                    sec['geom'] = {}
                if not type(geomParamValue) in [list, dict]:  # skip any list or dic params
                    sec['geom'][geomParamName] = geomParamValue

            # add synapses 
            for synName,synParams in sectParams['syns'].iteritems(): 
                if synName not in sec['syn']:
                    sec['syn'][synName] = {}
                for synParamName,synParamValue in synParams.iteritems():  # add params of the synapse
                    sec['syn'][synName][synParamName] = synParamValue

            # add Izhi type to tagss
            self.tags['Izhi2007Type'] = sectParams['Izhi2007Type']

        else: 
            print 'Error: soma section not found for Izhi2007 model'


    def createNEURONObj(self, prop):
        # set params for soma 
        sectName = 'soma'  # selected section by default for Izhi mechanism

        if sectName in prop['sections'].iterkeys():  # if soma is included in the cell params
            # create section
            if sectName not in self.secs:
                self.secs[sectName] = {}  # create h Section object
            sectParams = prop['sections'][sectName]  # pointer to section parameters
            self.secs[sectName]['hSection'] = h.Section(name=sectName+sectParams['Izhi2007'])
            sec = self.secs[sectName]  # pointer to section

            # set geometry params 
            for geomParamName,geomParamValue in sectParams['geom'].iteritems():  
                    if not type(geomParamValue) in [list, dict]:  # skip any list or dic params
                        setattr(sec['hSection'](0.5), geomParamName, geomParamValue)

            # create Izhi object
            if 'hIzhi' not in sec:
                sec['hIzhi'] = h.Izhi2007b(0.5, sec=sec)

            # set Izhi params
            izhParamNames = self.type2007['paramNames']
            izhParamValues = self.type2007[sectParams['Izhi2007Type']]
            for (izhParamName, izhParamValue) in zip(izhParamNames, izhParamValues):
                setattr(sec['hIzhi'], izhParamName, izhParamValue)
            sec['hIzhi'].vinit = izhParamValues['vr']  # check if can make vinit part of the type2007 params
            sec['hIzhi'].cellid = self.gid 
            s.fih.append(s.h.FInitializeHandler(self.init))  # check why this is needed

           # add synapses 
            for synName,synParams in sectParams['syns'].iteritems(): 
                if synName not in sec['syn']:
                    sec['syn'][synName] = {} 
                self.syns[synName]['hSyn'] = getattr(h, synParams['type'])(synParams['loc'], sec = sec['hSection'])  # create h Syn object (eg. h.Ex)
                for synParamName,synParamValue in synParams.iteritems():  # add params of the synapse
                    setattr(sec['syn'][synName]['hSyn'], synParamName, synParamValue)

        else: 
            print 'Error: soma section not found for Izhi2007 model'


    def init(self): 
        self.soma.v = -60  # check why this is needed




###############################################################################
# 
# POP CLASS
#
###############################################################################

class Pop(object):
    ''' Python class used to instantiate the network population '''
    def __init__(self,  tags):
        self.tags = tags # list of tags/attributes of population (eg. numCells, cellModel,...)
        self.cellGids = []  # list of cell gids beloging to this pop

    # Function to instantiate Cell objects based on the characteristics of this population
    def createCells(self):

        # if NetStim pop do not create cell objects (Netstims added to postsyn cell object when creating connections)
        if self.tags['cellModel'] == 'NetStim':
            cells = []

        # create cells based on fixed number of cells
        elif 'numCells' in self.tags:
            cells = self.createCellsFixedNum()

        # create cells based on yfrac density
        elif 'yFracRange' in self.tags and 'density' in self.tags:
            cells = self.createCellsYfrac()

        # add individual cells
        if 'cellList' in self.tags:
            cells = self.createCellsList()

        # not enough tags to create cells
        else:
            cells = []
            if 'popLabel' not in self.tags:
                self.tags['popLabel'] = 'unlabeled'
            print 'Not enough tags to create cells of population %s'%(self.tags['popLabel'])
            
        return cells


    # population based on numCells
    def createCellsFixedNum(self):
         # select cell class to instantiate cells based on the cellModel tags
        cellModelClass = getattr(s, self.tags['cellModel'])
        cells = []
        for i in xrange(int(s.rank), self.tags['numCells'], s.nhosts):
            gid = s.lastGid+i
            self.cellGids.append(gid)  # add gid list of cells belonging to this population - not needed?
            cellTags = {k: v for (k, v) in self.tags.iteritems() if k in s.net.params['popTagsCopiedToCells']}  # copy all pop tags to cell tags, except those that are pop-specific
            cellTags['yfrac'] = 0 # set yfrac value for this cell
            cellTags['x'] = 0  # calculate x location (um)
            cellTags['z'] = 0 # calculate z location (um)
            if 'propList' not in cellTags: cellTags['propList'] = []  # initalize list of property sets if doesn't exist
            cells.append(cellModelClass(gid, cellTags)) # instantiate Cell object
            if s.cfg['verbose']: print('Cell %d/%d (gid=%d) of pop %d, on node %d, '%(i, self.tags['numCells']-1, gid, i, s.rank))
        s.lastGid = s.lastGid + self.tags['numCells'] 
        return cells

                
    # population based on YfracRange
    def createCellsYfrac(self):
        cellModelClass = getattr(s, self.tags['cellModel'])  # select cell class to instantiate cells based on the cellModel tags
        cells = []
        volume = s.net.params['scale'] * s.net.params['sparseness'] * (s.net.params['modelsize']/1e3)**2 \
             * ((self.tags['yfracRange'][1]-self.tags['yfracRange'][0]) * s.net.params['corticalthick']/1e3)  # calculate num of cells based on scale, density, modelsize and yfracRange
        yfracInterval = 0.001  # interval of yfrac values to evaluate in order to find the max cell density
        maxDensity = max(map(self.tags['density'], (arange(self.tags['yfracRange'][0],self.tags['yfracRange'][1], yfracInterval))))  # max cell density 
        maxCells = volume * maxDensity  # max number of cells based on max value of density func 
        
        seed(s.id32('%d' % s.cfg['randseed']))  # reset random number generator
        yfracsAll = self.tags['yfracRange'][0] + ((self.tags['yfracRange'][1]-self.tags['yfracRange'][0])) * rand(int(maxCells), 1)  # random yfrac values 
        yfracsProb = array(map(self.tags['density'], self.tags['yfracsAll'])) / maxDensity  # calculate normalized density for each yfrac value (used to prune)
        allrands = rand(len(yfracsProb))  # create an array of random numbers for checking each yfrac pos 
        
        makethiscell = yfracsProb>allrands  # perform test to see whether or not this cell should be included (pruning based on density func)
        yfracs = [yfracsAll[i] for i in range(len(yfracsAll)) if i in array(makethiscell.nonzero()[0],dtype='int')] # keep only subset of yfracs based on density func
        self.tags['numCells'] = len(yfracs)  # final number of cells after pruning of yfrac values based on density func
        
        if s.cfg['verbose']: print 'Volume=%.2f, maxDensity=%.2f, maxCells=%.0f, numCells=%.0f'%(volume, maxDensity, maxCells, self.tags['numCells'])
        randLocs = rand(self.tags['numCells'], 2)  # create random x,z locations

        for i in xrange(int(s.rank), self.tags['numCells'], s.nhosts):
            gid = s.lastGid+i
            self.cellGids.append(gid)  # add gid list of cells belonging to this population - not needed?
            cellTags = {k: v for (k, v) in self.tags.iteritems() if k in s.net.params['popTagsCopiedToCells']}  # copy all pop tags to cell tags, except those that are pop-specific
            cellTags['yfrac'] = yfracs[i]  # set yfrac value for this cell
            cellTags['x'] = s.net.params['modelsize'] * randLocs[i,0]  # calculate x location (um)
            cellTags['z'] = s.net.params['modelsize'] * randLocs[i,1]  # calculate z location (um)
            if 'propList' not in cellTags: cellTags['propList'] = []  # initalize list of property sets if doesn't exist
            cells.append(cellModelClass(gid, cellTags)) # instantiate Cell object
            if s.cfg['verbose']: print('Cell %d/%d (gid=%d) of pop %d, pos=(%2.f, %2.f, %2.f), on node %d, '%(i, self.numCells-1, gid, cellTags['x'], cellTags['yfrac'], cellTags['z'], s.rank))
        s.lastGid = s.lastGid + self.tags['numCells'] 
        return cells


    def createCellsList(self):
        cellModelClass = getattr(s, self.tags['cellModel'])  # select cell class to instantiate cells based on the cellModel tags
        cells = []
        for i in xrange(int(s.rank), len(self.tags['listCells']), s.nhosts):
            gid = s.lastGid+1
            self.cellGids.append(gid)  # add gid list of cells belonging to this population - not needed?
            cellTags = {k: v for (k, v) in self.tags.iteritems() if k in s.net.params['popTagsCopiedToCells']}  # copy all pop tags to cell tags, except those that are pop-specific
            cellTags.update(self.tags['listCells'][i])  # add tags specific to this cells
            if 'propList' not in cellTags: cellTags['propList'] = []  # initalize list of property sets if doesn't exist
            cells.append(cellModelClass(gid, cellTags)) # instantiate Cell object
            if s.cfg['verbose']: print('Cell %d/%d (gid=%d) of pop %d, on node %d, '%(i, self.tags['numCells']-1, gid, i, s.rank))
        s.lastGid = s.lastGid + len(self.tags['listCells'])
        return cells


