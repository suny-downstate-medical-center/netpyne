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


    def createPyStruct(self, prop):
        # set params for all sections
        for sectName,sectParams in prop['sections'].iteritems(): 
            # create section
            if sectName not in self.secs:
                self.secs[sectName] = {}  # create section dict
            sec = self.secs[sectName]  # pointer to section
            
            # add mechanisms 
            if 'mechs' in sectParams:
                for mechName,mechParams in sectParams['mechs'].iteritems(): 
                    if 'mechs' not in sec:
                        sec['mechs'] = {}
                    if mechName not in sec['mechs']: 
                        sec['mechs'][mechName] = {}  
                    for mechParamName,mechParamValue in mechParams.iteritems():  # add params of the mechanism
                        sec['mechs'][mechName][mechParamName] = mechParamValue

            # add synapses 
            if 'syns' in sectParams:
                for synName,synParams in sectParams['syns'].iteritems(): 
                    if 'syns' not in sec:
                        sec['syns'] = {}
                    if synName not in sec['syns']:
                        sec['syns'][synName] = {}
                    for synParamName,synParamValue in synParams.iteritems():  # add params of the synapse
                        sec['syns'][synName][synParamName] = synParamValue

            # add geometry params 
            if 'geom' in sectParams:
                for geomParamName,geomParamValue in sectParams['geom'].iteritems():  
                    if 'geom' not in sec:
                        sec['geom'] = {}
                    if not type(geomParamValue) in [list, dict]:  # skip any list or dic params
                        sec['geom'][geomParamName] = geomParamValue

            # add 3d geometry
            if 'pt3d' in sectParams['geom']:
                if 'pt3d' not in sec['geom']:  
                    sec['geom']['pt3d'] = []
                for pt3d in sectParams['geom']['pt3d']:
                    sec['geom']['pt3d'].append(pt3d)

            # add topolopgy params
            if 'topol' in sectParams:
                if 'topol' not in sec:
                    sec['topol'] = {}
                for topolParamName,topolParamValue in sectParams['topol'].iteritems(): 
                    sec['topol'][topolParamName] = topolParamValue

        # set params for point neuron
        if 'pointNeuron' in prop:
            for pointName, pointParams in prop['pointNeuron'].iteritems():
                  if pointName == self.tags['cellModel']: # add param values only if this cell uses that point neuron model
                      self.tags[pointName] = pointParams

    def associateGid (self, threshold = 10.0):
        s.pc.set_gid2node(self.gid, s.rank) # this is the key call that assigns cell gid to a particular node
        nc = h.NetCon(self.secs['soma']['hSection'](0.5)._ref_v, None, sec=self.secs['soma']['hSection'])
        nc.threshold = threshold
        s.pc.cell(self.gid, nc, 1)  # associate a particular output stream of events
        s.gidVec.append(self.gid) # index = local id; value = global id
        s.gidDic[self.gid] = len(s.gidVec)
        del nc # discard netcon



    def addConn(self, params):
        if params['preGid'] == self.gid:
            print 'Error: attempted to create self-connection on cell gid=%d, section=%s '%(self.gid, params['sec'])
            return  # if self-connection return

        if not params['sec']:  # if no section specified 
            if 'soma' in self.secs:  
                params['sec'] = 'soma'  # use 'soma' if exists
            elif self.secs:  
                params['sec'] = self.secs.keys()[0]  # if no 'soma', use first sectiona available
            else:  
                print 'Error: no Section available on cell gid=%d to add connection'%(self.gid)
                return  # if no Sections available print error and exit

        if not params['synReceptor']:  # if no synapse specified 
            if 'syns' in self.secs[params['sec']]:  
                params['synReceptor'] = self.secs[params['sec']]['syns'].keys()[0]  # use first synapse available in section
            else:  
                print 'Error: no Synapse available on cell gid=%d, section=%s to add connection'%(self.gid, params['sec'])
                return  # if no Synapse available print error and exit

        if not params['threshold']:
            params['threshold'] = 10.0

        self.conns.append(params)
        netcon = s.pc.gid_connect(params['preGid'], self.secs[params['sec']]['syns'][params['synReceptor']]['hSyn']) # create Netcon between global gid and local cell object
        netcon.weight[0] = params['weight']  # set Netcon weight
        netcon.delay = params['delay']  # set Netcon delay
        netcon.threshold = params['threshold']  # set Netcon delay
        self.conns[-1]['hNetcon'] = netcon  # add netcon object to dict in conns list
        if s.cfg['verbose']: print('Created connection preGid=%d, postGid=%d, sec=%s, syn=%s, weight=%.2f, delay=%.1f'%
            (params['preGid'], self.gid, params['sec'], params['synReceptor'], params['weight'], params['delay']))


    def addStim (self, params):
        if not params['sec']:  # if no section specified 
            if 'soma' in self.secs:  
                params['sec'] = 'soma'  # use 'soma' if exists
            elif self.secs:  
                params['sec'] = self.secs.keys()[0]  # if no 'soma', use first sectiona available
            else:  
                print 'Error: no Section available on cell gid=%d to add connection'%(self.gid)
                return  # if no Sections available print error and exit

        if not params['synReceptor']:  # if no synapse specified 
            if 'syns' in self.secs[params['sec']]:  
                params['synReceptor'] = self.secs[params['sec']]['syns'].keys()[0]  # use first synapse available in section
            else:  
                print 'Error: no Synapse available on cell gid=%d, section=%s to add connection'%(self.gid, params['sec'])
                return  # if no Synapse available print error and exit

        if not params['threshold']:
            params['threshold'] = 10.0

        self.stims.append(params)

        if params['source'] == 'random':
            rand = h.Random()
            rand.Random123(self.gid,self.gid*2)
            rand.negexp(1)
            self.stims[-1]['hRandom'] = rand  # add netcon object to dict in conns list

            netstim = h.NetStim()
            netstim.interval = params['rate']**-1*1e3 # inverse of the frequency and then convert from Hz^-1 to ms
            netstim.noiseFromRandom(rand)  # use random number generator
            netstim.noise = params['noise']
            netstim.number = 1e12   
            self.stims[-1]['hNetStim'] = netstim  # add netstim object to dict in stim list

        netcon = h.NetCon(netstim, self.secs[params['sec']]['syns'][params['synReceptor']]['hSyn']) # create Netcon between global gid and local cell object
        netcon.weight[0] = params['weight']  # set Netcon weight
        netcon.delay = params['delay']  # set Netcon delay
        netcon.threshold = params['threshold']  # set Netcon delay
        self.stims[-1]['hNetcon'] = netcon  # add netcon object to dict in conns list
        if s.cfg['verbose']: print('Created stim prePop=%s, postGid=%d, sec=%s, syn=%s, weight=%.2f, delay=%.1f'%
            (params['popLabel'], self.gid, params['sec'], params['synReceptor'], params['weight'], params['delay']))

    def recordTraces (self):
        # set up voltagse recording; recdict will be taken from global context
        for key, params in s.cfg['recdict'].iteritems():
            ptr = None
            try: 
                if 'pos' in params:
                    if 'mech' in params:  # eg. soma(0.5).hh._ref_gna
                        ptr = self.secs[params['sec']]['hSection'](params['pos']).__getattribute__(params['mech']).__getattribute__('_ref_'+params['var'])
                    elif 'syn' in params:  # eg. soma(0.5).AMPA._ref_g
                        print key,params
                        print self.secs[params['sec']]['syns'][params['syn']]['hSyn'].i
                        ptr = self.secs[params['sec']]['syns'][params['syn']]['hSyn'].__getattribute__('_ref_'+params['var'])
                        print 'ok'
                    else:  # eg. soma(0.5)._ref_v
                        ptr = self.secs[params['sec']]['hSection'](params['pos']).__getattribute__('_ref_'+params['var'])
                else:
                    if 'pointProcess' in params: # eg. soma.izh._ref_u
                        if params['pointProcess'] in self.secs[params['sec']]:
                            ptr = self.secs[params['sec']][params['pointProcess']].__getattribute__('_ref_'+params['var'])

                if ptr:  # if pointer has been created, then setup recording
                    s.simData[key]['cell_'+str(self.gid)] = h.Vector(s.cfg['tstop']/s.cfg['recordStep']+1).resize(0)
                    s.simData[key]['cell_'+str(self.gid)].record(ptr, s.cfg['recordStep'])
                    if s.cfg['verbose']: print 'Recording ', key, 'from cell ', self.gid
            except:
                if s.cfg['verbose']: print 'Cannot record ', key, 'from cell ', self.gid


    def recordStimSpikes (self):
        s.simData['stims'].update({'cell_'+str(self.gid): {}})
        for stim in self.stims:
            stimSpikeVecs = h.Vector() # initialize vector to store 
            stim['hNetcon'].record(stimSpikeVecs)
            s.simData['stims']['cell_'+str(self.gid)].update({stim['popLabel']: stimSpikeVecs})


    def __getstate__(self): 
        ''' Removes non-picklable h objects so can be pickled and sent via py_alltoall'''
        odict = self.__dict__.copy() # copy the dict since we change it
        odict = s.sim.replaceItemObj(odict, keystart='h', newval=None)  # replace h objects with None so can be pickled
        return odict



###############################################################################
#
# HODGKIN-HUXLEY CELL CLASS
#
###############################################################################

class HH(Cell):
    ''' Python class for Hodgkin-Huxley cell model'''

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
                if mechName not in sec['mechs']: 
                    sec['mechs'][mechName] = {}
                sec['hSection'].insert(mechName)
                for mechParamName,mechParamValue in mechParams.iteritems():  # add params of the mechanism
                    mechParamValueFinal = mechParamValue
                    for iseg,seg in enumerate(sec['hSection']):  # set mech params for each segment
                        if type(mechParamValue) in [list]: 
                            mechParamValueFinal = mechParamValue[iseg]
                        seg.__getattribute__(mechName).__setattr__(mechParamName,mechParamValueFinal)
                
            # add synapses 
            for synName,synParams in sectParams['syns'].iteritems(): 
                if synName not in sec['syns']:
                    sec['syns'][synName] = {} 
                synObj = getattr(h, synParams['type'])
                sec['syns'][synName]['hSyn'] = synObj(synParams['loc'], sec = sec['hSection'])  # create h Syn object (eg. h.Ex)
                for synParamName,synParamValue in synParams.iteritems():  # add params of the synapse
                    if synParamName not in ['type','loc']:
                        setattr(sec['syns'][synName]['hSyn'], synParamName, synParamValue)

            # set geometry params 
            for geomParamName,geomParamValue in sectParams['geom'].iteritems():  
                if not type(geomParamValue) in [list, dict]:  # skip any list or dic params
                    setattr(sec['hSection'], geomParamName, geomParamValue)

            # set 3d geometry
            if 'pt3d' in sectParams['geom']:  
                h.pt3dclear(sec=sec['hSection'])
                x = self.tags['x']
                if 'yfrac' in self.tags and 'corticalthick' in s.net.params:
                    y = self.tags['yfrac'] * s.net.params['corticalthick']/1e3  # y as a func of yfrac and cortical thickness
                else:
                    y = self.tags['y']
                z = self.tags['z']
                for pt3d in sectParams['geom']['pt3d']:
                    h.pt3dadd(x+pt3d[0], y+pt3d[1], z+pt3d[2], pt3d[3], sec=sec['hSection'])

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
# POINT NEURON CLASS (point process placed in Section; v calculated in Section)
#
###############################################################################

class PointNeuron(Cell):
    """
    Python class for poin neurons (eg.Izhikevich 2003 or 2007 models)
    Point process in placed in a section and v calculated in section
    Point process and parameter values are passed as argument
    """

    def createNEURONObj(self, prop):
        # set params for soma 
        sectName = 'soma'  # selected section by default for point process
        pointProc = self.__class__.__name__ # prop['pointNeuron']['model']
        if pointProc == 'PointNeuron':
            pointProc = 'Izhi2007b'  # default to Izhi2007b

        pointProcParams = prop['pointNeuron'][pointProc]

        if sectName in prop['sections'].iterkeys():  # if soma is included in the cell params
            # create section
            if sectName not in self.secs:
                self.secs[sectName] = {}  # create h Section object
            sectParams = prop['sections'][sectName]  # pointer to section parameters
            self.secs[sectName]['hSection'] = h.Section(name=sectName+'_'+pointProc)
            sec = self.secs[sectName]  # pointer to section

            # set geometry params 
            for geomParamName,geomParamValue in sectParams['geom'].iteritems():  
                    if not type(geomParamValue) in [list, dict]:  # skip any list or dic params
                        setattr(sec['hSection'], geomParamName, geomParamValue)

            # create Izhi object
            if 'hPoint' not in sec:
                sec['hPoint'] = getattr(h, pointProc)(0.5, sec=sec['hSection'])

            # set Izhi params
            for izhParamName, izhParamValue in pointProcParams.iteritems():
                setattr(sec['hPoint'], izhParamName, izhParamValue)
            sec['hPoint'].cellid = self.gid 

           # add synapses 
            for synName,synParams in sectParams['syns'].iteritems(): 
                if 'syns' not in sec:
                    sec['syns'] = {}
                if synName not in sec['syns']:
                    sec['syns'][synName] = {} 
                sec['syns'][synName]['hSyn'] = getattr(h, synParams['type'])(synParams['loc'], sec = sec['hSection'])  # create h Syn object (eg. h.Ex)
                for synParamName,synParamValue in synParams.iteritems():  # add params of the synapse
                    if synParamName not in ['type', 'loc']:
                        setattr(sec['syns'][synName]['hSyn'], synParamName, synParamValue)
        else: 
            print 'Error: soma section not found to place point neuron model'

# Cell classes that inherit from PointNeuron
# Should match the POINTPROCESS mechanism name
# Required so can generate cell objects dynamically using the 'cellModel' property of populations

class Izhi2003b(PointNeuron):
    pass

class Izhi2007b(PointNeuron):
    pass

class clausIzhi2007b(PointNeuron):
    pass


###############################################################################
#
# POINT NEURON CLASS (artificial cell, independent point process outside of section)
#
###############################################################################

class PointNeuronIndep(Cell):
    '''
    Point Neuron that doesn't require a Section - TO DO
    '''
    pass


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

        # add individual cells
        if 'cellsList' in self.tags:
            cells = self.createCellsList()

        # if NetStim pop do not create cell objects (Netstims added to postsyn cell object when creating connections)
        elif self.tags['cellModel'] == 'NetStim':
            cells = []

        # create cells based on fixed number of cells
        elif 'numCells' in self.tags:
            cells = self.createCellsFixedNum()

        # create cells based on density (optional yfrac-dep)
        elif 'yfracRange' in self.tags and 'density' in self.tags:
            cells = self.createCellsDensity()

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
            cellTags['y'] = 0 # set yfrac value for this cell
            cellTags['x'] = 0  # calculate x location (um)
            cellTags['z'] = 0 # calculate z location (um)
            if 'propList' not in cellTags: cellTags['propList'] = []  # initalize list of property sets if doesn't exist
            cells.append(cellModelClass(gid, cellTags)) # instantiate Cell object
            if s.cfg['verbose']: print('Cell %d/%d (gid=%d) of pop %s, on node %d, '%(i, self.tags['numCells']-1, gid, self.tags['popLabel'], s.rank))
        s.lastGid = s.lastGid + self.tags['numCells'] 
        return cells

                
    # population based on YfracRange
    def createCellsDensity(self):
        cellModelClass = getattr(s, self.tags['cellModel'])  # select cell class to instantiate cells based on the cellModel tags
        cells = []
        volume = s.net.params['scale'] * s.net.params['sparseness'] * (s.net.params['modelsize']/1e3)**2 \
             * ((self.tags['yfracRange'][1]-self.tags['yfracRange'][0]) * s.net.params['corticalthick']/1e3)  # calculate num of cells based on scale, density, modelsize and yfracRange
        
        if hasattr(self.tags['density'], '__call__'): # check if conn is yfrac-dep density func 
            yfracInterval = 0.001  # interval of yfrac values to evaluate in order to find the max cell density
            maxDensity = max(map(self.tags['density'], (arange(self.tags['yfracRange'][0],self.tags['yfracRange'][1], yfracInterval))))  # max cell density 
            maxCells = volume * maxDensity  # max number of cells based on max value of density func 
            
            seed(s.sim.id32('%d' % s.cfg['randseed']))  # reset random number generator
            yfracsAll = self.tags['yfracRange'][0] + ((self.tags['yfracRange'][1]-self.tags['yfracRange'][0])) * rand(int(maxCells), 1)  # random yfrac values 
            yfracsProb = array(map(self.tags['density'], yfracsAll)) / maxDensity  # calculate normalized density for each yfrac value (used to prune)
            allrands = rand(len(yfracsProb))  # create an array of random numbers for checking each yfrac pos 
            
            makethiscell = yfracsProb>allrands  # perform test to see whether or not this cell should be included (pruning based on density func)
            yfracs = [yfracsAll[i] for i in range(len(yfracsAll)) if i in array(makethiscell.nonzero()[0],dtype='int')] # keep only subset of yfracs based on density func
            self.tags['numCells'] = len(yfracs)  # final number of cells after pruning of yfrac values based on density func
            if s.cfg['verbose']: print 'Volume=%.2f, maxDensity=%.2f, maxCells=%.0f, numCells=%.0f'%(volume, maxDensity, maxCells, self.tags['numCells'])

        else:  # NO yfrac-dep
            self.tags['numCells'] = int(self.tags['density'] * volume)  # = density (cells/mm^3) * volume (mm^3)
            seed(s.sim.id32('%d' % s.cfg['randseed']))  # reset random number generator
            yfracs = self.tags['yfracRange'][0] + ((self.tags['yfracRange'][1]-self.tags['yfracRange'][0])) * rand(self.tags['numCells'], 1)  # random yfrac values 
            if s.cfg['verbose']: print 'Volume=%.4f, density=%.2f, numCells=%.0f'%(volume, self.tags['density'], self.tags['numCells'])

        randLocs = rand(self.tags['numCells'], 2)  # create random x,z locations

        for i in xrange(int(s.rank), self.tags['numCells'], s.nhosts):
            gid = s.lastGid+i
            self.cellGids.append(gid)  # add gid list of cells belonging to this population - not needed?
            cellTags = {k: v for (k, v) in self.tags.iteritems() if k in s.net.params['popTagsCopiedToCells']}  # copy all pop tags to cell tags, except those that are pop-specific
            cellTags['yfrac'] = yfracs[i][0]  # set yfrac value for this cell
            cellTags['x'] = s.net.params['modelsize'] * randLocs[i,0]  # calculate x location (um)
            cellTags['z'] = s.net.params['modelsize'] * randLocs[i,1]  # calculate z location (um)
            if 'propList' not in cellTags: cellTags['propList'] = []  # initalize list of property sets if doesn't exist
            cells.append(cellModelClass(gid, cellTags)) # instantiate Cell object
            if s.cfg['verbose']: 
                print('Cell %d/%d (gid=%d) of pop %s, pos=(%2.f, %2.f, %2.f), on node %d, '%(i, self.tags['numCells']-1, gid, self.tags['popLabel'],cellTags['x'], cellTags['yfrac'], cellTags['z'], s.rank))
        s.lastGid = s.lastGid + self.tags['numCells'] 
        return cells


    def createCellsList(self):
        if 'cellModel' in self.tags: 
            cellModelClass = getattr(s, self.tags['cellModel'])  # select cell class to instantiate cells based on the cellModel tags
        cells = []
        self.tags['numCells'] = len(self.tags['cellsList'])
        for i in xrange(int(s.rank), len(self.tags['cellsList']), s.nhosts):
            if 'cellModel' in self.tags['cellsList'][i]:
                cellModelClass = getattr(s, self.tags['cellsList'][i]['cellModel'])  # select cell class to instantiate cells based on the cellModel tags
            gid = s.lastGid+i
            self.cellGids.append(gid)  # add gid list of cells belonging to this population - not needed?
            cellTags = {k: v for (k, v) in self.tags.iteritems() if k in s.net.params['popTagsCopiedToCells']}  # copy all pop tags to cell tags, except those that are pop-specific
            cellTags.update(self.tags['cellsList'][i])  # add tags specific to this cells
            if 'propList' not in cellTags: cellTags['propList'] = []  # initalize list of property sets if doesn't exist
            cells.append(cellModelClass(gid, cellTags)) # instantiate Cell object
            if s.cfg['verbose']: print('Cell %d/%d (gid=%d) of pop %d, on node %d, '%(i, self.tags['numCells']-1, gid, i, s.rank))
        s.lastGid = s.lastGid + len(self.tags['cellsList'])
        return cells


    def __getstate__(self): 
        ''' Removes non-picklable h objects so can be pickled and sent via py_alltoall'''
        odict = self.__dict__.copy() # copy the dict since we change it
        odict = s.sim.replaceFuncObj(odict)  # replace h objects with None so can be pickled
        return odict

