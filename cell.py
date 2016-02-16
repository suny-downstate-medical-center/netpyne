"""
cell.py 

Contains Synapse, Conn, Cell and Population classes 

Contributors: salvadordura@gmail.com
"""

from pylab import arange, seed, rand, array
from neuron import h # Import NEURON
import framework as f


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

        self.create()  # create cell 
        self.associateGid() # register cell for this node

    def create(self):
        for prop in f.net.params['cellParams']:  # for each set of cell properties
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
                if f.cfg['createPyStruct']:
                    self.createPyStruct(prop)
                if f.cfg['createNEURONObj']:
                    self.createNEURONObj(prop)  # add sections, mechanisms, synapses, geometry and topolgy specified by this property set


    def createPyStruct(self, prop):
        # set params for all sections
        for sectName,sectParams in prop['sections'].iteritems(): 
            # create section
            if sectName not in self.secs:
                self.secs[sectName] = {}  # create section dict
            sec = self.secs[sectName]  # pointer to section
            
            # add distributed mechanisms 
            if 'mechs' in sectParams:
                for mechName,mechParams in sectParams['mechs'].iteritems(): 
                    if 'mechs' not in sec:
                        sec['mechs'] = {}
                    if mechName not in sec['mechs']: 
                        sec['mechs'][mechName] = {}  
                    for mechParamName,mechParamValue in mechParams.iteritems():  # add params of the mechanism
                        sec['mechs'][mechName][mechParamName] = mechParamValue

            # add point processes
            if 'pointps' in sectParams:
                for pointpName,pointpParams in sectParams['pointps'].iteritems(): 
                    #if self.tags['cellModel'] == pointpName: # only required if want to allow setting various cell models in same rule
                    if 'pointps' not in sec:
                        sec['pointps'] = {}
                    if pointpName not in sec['pointps']: 
                        sec['pointps'][pointpName] = {}  
                    for pointpParamName,pointpParamValue in pointpParams.iteritems():  # add params of the mechanism
                        sec['pointps'][pointpName][pointpParamName] = pointpParamValue


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

            # add other params
            if 'spikeGenLoc' in sectParams:
                sec['spikeGenLoc'] = sectParams['spikeGenLoc']

            if 'vinit' in sectParams:
                sec['vinit'] = sectParams['vinit']


    def initV(self): 
        for sec in self.secs.values():
            if 'vinit' in sec:
                sec['hSection'](0.5).v = sec['vinit']

    def createNEURONObj(self, prop):
        # set params for all sections
        for sectName,sectParams in prop['sections'].iteritems(): 
            # create section
            if sectName not in self.secs:
                self.secs[sectName] = {}  # create sect dict if doesn't exist
            self.secs[sectName]['hSection'] = h.Section(name=sectName)  # create h Section object
            sec = self.secs[sectName]  # pointer to section
            
            # add distributed mechanisms 
            if 'mechs' in sectParams:
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

            # add point processes
            if 'pointps' in sectParams:
                for pointpName,pointpParams in sectParams['pointps'].iteritems(): 
                    #if self.tags['cellModel'] == pointpParams:  # only required if want to allow setting various cell models in same rule
                    if pointpName not in sec['pointps']:
                        sec['pointps'][pointpName] = {} 
                    pointpObj = getattr(h, pointpParams['_type'])
                    loc = pointpParams['_loc'] if '_loc' in pointpParams else 0.5  # set location
                    sec['pointps'][pointpName]['hPointp'] = pointpObj(loc, sec = sec['hSection'])  # create h Pointp object (eg. h.Izhi2007b)
                    for pointpParamName,pointpParamValue in pointpParams.iteritems():  # add params of the point process
                        if not pointpParamName.startswith('_'):
                            setattr(sec['pointps'][pointpName]['hPointp'], pointpParamName, pointpParamValue)
                        
            # add synapses 
            if 'syns' in sectParams:
                for synName,synParams in sectParams['syns'].iteritems(): 
                    if synName not in sec['syns']:
                        sec['syns'][synName] = {} 
                    synObj = getattr(h, synParams['_type'])
                    loc = synParams['_loc'] if '_loc' in synParams else 0.5  # set location
                    sec['syns'][synName]['hSyn'] = synObj(loc, sec = sec['hSection'])  # create h Syn object (eg. h.Exp2Syn)
                    for synParamName,synParamValue in synParams.iteritems():  # add params of the synapse
                        if not synParamName.startswith('_'):
                            setattr(sec['syns'][synName]['hSyn'], synParamName, synParamValue)

            # set geometry params 
            if 'geom' in sectParams:
                for geomParamName,geomParamValue in sectParams['geom'].iteritems():  
                    if not type(geomParamValue) in [list, dict]:  # skip any list or dic params
                        setattr(sec['hSection'], geomParamName, geomParamValue)

            # set 3d geometry
            if 'pt3d' in sectParams['geom']:  
                h.pt3dclear(sec=sec['hSection'])
                x = self.tags['x']
                if 'ynorm' in self.tags and 'sizeY' in f.net.params:
                    y = self.tags['ynorm'] * f.net.params['sizeY']/1e3  # y as a func of ynorm and cortical thickness
                else:
                    y = self.tags['y']
                z = self.tags['z']
                for pt3d in sectParams['geom']['pt3d']:
                    h.pt3dadd(x+pt3d[0], y+pt3d[1], z+pt3d[2], pt3d[3], sec=sec['hSection'])

        # set topology 
        for sectName,sectParams in prop['sections'].iteritems():  # iterate sects again for topology (ensures all exist)
            sec = self.secs[sectName]  # pointer to section # pointer to child sec
            if 'topol' in sectParams:
                if sectParams['topol']:
                    sec['hSection'].connect(self.secs[sectParams['topol']['parentSec']]['hSection'], sectParams['topol']['parentX'], sectParams['topol']['childX'])  # make topol connection



    def associateGid (self, threshold = 10.0):
        if self.secs:
            f.pc.set_gid2node(self.gid, f.rank) # this is the key call that assigns cell gid to a particular node
            sec = next((secParams for secName,secParams in self.secs.iteritems() if 'spikeGenLoc' in secParams), None) # check if any section has been specified as spike generator
            if sec:
                loc = sec['spikeGenLoc']  # get location of spike generator within section
            else:
                sec = self.secs['soma'] if 'soma' in self.secs else self.secs[self.secs.keys()[0]]  # use soma if exists, otherwise 1st section
                loc = 0.5
            nc = None
            if 'pointps' in sec:  # if no syns, check if point processes with '_vref' (artificial cell)
                for pointpName, pointpParams in sec['pointps'].iteritems():
                    if '_vref' in pointpParams:
                        nc = h.NetCon(sec['pointps'][pointpName]['hPointp'].__getattribute__('_ref_'+pointpParams['_vref']), None, sec=sec['hSection'])
                        break
            if not nc:  # if still haven't created netcon  
                nc = h.NetCon(sec['hSection'](loc)._ref_v, None, sec=sec['hSection'])
            nc.threshold = threshold
            f.pc.cell(self.gid, nc, 1)  # associate a particular output stream of events
            f.gidVec.append(self.gid) # index = local id; value = global id
            f.gidDic[self.gid] = len(f.gidVec)
            del nc # discard netcon




    def addConn(self, params):
        if params['preGid'] == self.gid:
            print 'Error: attempted to create self-connection on cell gid=%d, section=%s '%(self.gid, params['sec'])
            return  # if self-connection return

        if not params['sec'] or not params['sec'] in self.secs:  # if no section specified or section specified doesnt exist
            if 'soma' in self.secs:  
                params['sec'] = 'soma'  # use 'soma' if exists
            elif self.secs:  
                params['sec'] = self.secs.keys()[0]  # if no 'soma', use first sectiona available
                for secName, secParams in self.secs.iteritems():              # replace with first section that includes synapse
                    if 'syns' in secParams:
                        if secParams['syns']:
                            params['sec'] = secName
                            break
            else:  
                print 'Error: no Section available on cell gid=%d to add connection'%(self.gid)
                return  # if no Sections available print error and exit
        sec = self.secs[params['sec']]

        weightIndex = 0  # set default weight matrix index

        pointp = None
        if 'pointps' in self.secs[params['sec']]:  #  check if point processes with '_vref' (artificial cell)
            for pointpName, pointpParams in self.secs[params['sec']]['pointps'].iteritems():
                if '_vref' in pointpParams:  # if includes vref param means doesn't use Section v or synapses
                    pointp = pointpName
                    if '_synList' in pointpParams:
                        if params['syn'] in pointpParams['_synList']: 
                            weightIndex = pointpParams['_synList'].index(params['syn'])  # udpate weight index based pointp synList


        if not pointp: # not a point process
            if 'syns' in sec: # section has synapses
                if params['syn']: # desired synapse specified in conn params
                    if params['syn'] not in sec['syns']:  # if exact name of desired synapse doesn't exist
                        synIndex = [0]  # by default use syn 0
                        synIndex.extend([i for i,syn in enumerate(sec['syns']) if params['syn'] in syn])  # check if contained in any of the synapse names
                        params['syn'] = sec['syns'].keys()[synIndex[-1]]
                else:  # if no synapse specified            
                    params['syn'] = sec['syns'].keys()[0]  # use first synapse available in section
            else: # if still no synapse  
                print 'Error: no Synapse or point process available on cell gid=%d, section=%s to add stim'%(self.gid, params['sec'])
                return  # if no Synapse available print error and exit

        if not params['threshold']:
            params['threshold'] = 10.0

        self.conns.append(params)
        if pointp:
            netcon = f.pc.gid_connect(params['preGid'], sec['pointps'][pointp]['hPointp']) # create Netcon between global gid and local point neuron
        else:
            netcon = f.pc.gid_connect(params['preGid'], sec['syns'][params['syn']]['hSyn']) # create Netcon between global gid and local synapse
        
        netcon.weight[weightIndex] = f.net.params['scaleConnWeight']*params['weight']  # set Netcon weight
        netcon.delay = params['delay']  # set Netcon delay
        netcon.threshold = params['threshold']  # set Netcon delay
        self.conns[-1]['hNetcon'] = netcon  # add netcon object to dict in conns list
        if f.cfg['verbose']: print('Created connection preGid=%d, postGid=%d, sec=%s, syn=%s, weight=%.4g, delay=%.1f'%
            (params['preGid'], self.gid, params['sec'], params['syn'], f.net.params['scaleConnWeight']*params['weight'], params['delay']))


    def addStim (self, params):
        if not params['sec'] or not params['sec'] in self.secs:  # if no section specified or section specified doesnt exist
            if 'soma' in self.secs:  
                params['sec'] = 'soma'  # use 'soma' if exists
            elif self.secs:  
                params['sec'] = self.secs.keys()[0]  # if no 'soma', use first sectiona available
                for secName, secParams in self.secs.iteritems():              # replace with first section that includes synapse
                    if 'syns' in secParams:
                        if secParams['syns']:
                            params['sec'] = secName
                            break
            else:  
                print 'Error: no Section available on cell gid=%d to add connection'%(self.gid)
                return  # if no Sections available print error and exit
        sec = self.secs[params['sec']]

        weightIndex = 0  # set default weight matrix index

        pointp = None
        if 'pointps' in sec:  # check if point processes (artificial cell)
            for pointpName, pointpParams in sec['pointps'].iteritems():
                  if '_vref' in pointpParams:  # if includes vref param means doesn't use Section v or synapses
                    pointp = pointpName
                    if '_synList' in pointpParams:
                        if params['syn'] in pointpParams['_synList']: 
                            weightIndex = pointpParams['_synList'].index(params['syn'])  # udpate weight index based pointp synList


        if not pointp: # not a point process
            if 'syns' in sec: # section has synapses
                if params['syn']: # desired synapse specified in conn params
                    if params['syn'] not in sec['syns']:  # if exact name of desired synapse doesn't exist
                        synIndex = [0]  # by default use syn 0
                        synIndex.extend([i for i,syn in enumerate(sec['syns']) if params['syn'] in syn])  # check if contained in any of the synapse names
                        params['syn'] = sec['syns'].keys()[synIndex[-1]]
                else:  # if no synapse specified            
                    params['syn'] = sec['syns'].keys()[0]  # use first synapse available in section
            else: # if still no synapse  
                print 'Error: no Synapse or point process available on cell gid=%d, section=%s to add stim'%(self.gid, params['sec'])
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
            netstim.number = params['number']   
            self.stims[-1]['hNetStim'] = netstim  # add netstim object to dict in stim list

        if pointp:
            netcon = h.NetCon(netstim, sec['pointps'][pointp]['hPointp'])  # create Netcon between global gid and local point neuron
        else:
            netcon = h.NetCon(netstim, sec['syns'][params['syn']]['hSyn']) # create Netcon between global gid and local synapse
        netcon.weight[weightIndex] = params['weight']  # set Netcon weight
        netcon.delay = params['delay']  # set Netcon delay
        netcon.threshold = params['threshold']  # set Netcon delay
        self.stims[-1]['hNetcon'] = netcon  # add netcon object to dict in conns list
        if f.cfg['verbose']: print('Created stim prePop=%s, postGid=%d, sec=%s, syn=%s, weight=%.4g, delay=%.4g'%
            (params['popLabel'], self.gid, params['sec'], params['syn'], params['weight'], params['delay']))


    def recordTraces (self):
        # set up voltagse recording; recdict will be taken from global context
        for key, params in f.cfg['recordDict'].iteritems():
            ptr = None
            try: 
                if 'pos' in params:
                    if 'mech' in params:  # eg. soma(0.5).hh._ref_gna
                        ptr = self.secs[params['sec']]['hSection'](params['pos']).__getattribute__(params['mech']).__getattribute__('_ref_'+params['var'])
                    elif 'syn' in params:  # eg. soma(0.5).AMPA._ref_g
                        ptr = self.secs[params['sec']]['syns'][params['syn']]['hSyn'].__getattribute__('_ref_'+params['var'])
                    else:  # eg. soma(0.5)._ref_v
                        ptr = self.secs[params['sec']]['hSection'](params['pos']).__getattribute__('_ref_'+params['var'])
                else:
                    if 'pointp' in params: # eg. soma.izh._ref_u
                        #print self.secs[params['sec']]
                        if params['pointp'] in self.secs[params['sec']]['pointps']:
                            ptr = self.secs[params['sec']]['pointps'][params['pointp']]['hPointp'].__getattribute__('_ref_'+params['var'])

                if ptr:  # if pointer has been created, then setup recording
                    f.simData[key]['cell_'+str(self.gid)] = h.Vector(f.cfg['tstop']/f.cfg['recordStep']+1).resize(0)
                    f.simData[key]['cell_'+str(self.gid)].record(ptr, f.cfg['recordStep'])
                    if f.cfg['verbose']: print 'Recording ', key, 'from cell ', self.gid
            except:
                if f.cfg['verbose']: print 'Cannot record ', key, 'from cell ', self.gid


    def recordStimSpikes (self):
        f.simData['stims'].update({'cell_'+str(self.gid): {}})
        for stim in self.stims:
            stimSpikeVecs = h.Vector() # initialize vector to store 
            stim['hNetcon'].record(stimSpikeVecs)
            f.simData['stims']['cell_'+str(self.gid)].update({stim['popLabel']: stimSpikeVecs})


    def __getstate__(self): 
        ''' Removes non-picklable h objects so can be pickled and sent via py_alltoall'''
        odict = self.__dict__.copy() # copy the dict since we change it
        odict = f.sim.replaceItemObj(odict, keystart='h', newval=None)  # replace h objects with None so can be pickled
        return odict



###############################################################################
#
# POINT NEURON CLASS (v not from Section)
#
###############################################################################

class PointNeuron(Cell):
    '''
    Point Neuron that doesn't use v from Section - TO DO
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

        # create cells based on density (optional ynorm-dep)
        elif 'ynormRange' in self.tags and 'density' in self.tags:
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
        ''' Create population cells based on fixed number of cells'''
        cellModelClass = Cell
        cells = []
        seed(f.sim.id32('%d'%(f.cfg['randseed']+self.tags['numCells'])))
        randLocs = rand(self.tags['numCells'], 3)  # create random x,y,z locations
        for icoord, coord in enumerate(['x', 'y', 'z']):
            if coord+'Range' in self.tags:  # if user provided absolute range, convert to normalized
                self.tags[coord+'normRange'] = [point / f.net.params['size'+coord.upper()] for point in self.tags[coord+'Range']]
            if coord+'normRange' in self.tags:  # if normalized range, rescale random locations
                minv = self.tags[coord+'normRange'][0] 
                maxv = self.tags[coord+'normRange'][1] 
                randLocs[:,icoord] = randLocs[:,icoord] / (maxv-minv) + minv
        
        for i in xrange(int(f.rank), f.net.params['scale'] * self.tags['numCells'], f.nhosts):
            gid = f.lastGid+i
            self.cellGids.append(gid)  # add gid list of cells belonging to this population - not needed?
            cellTags = {k: v for (k, v) in self.tags.iteritems() if k in f.net.params['popTagsCopiedToCells']}  # copy all pop tags to cell tags, except those that are pop-specific
            cellTags['xnorm'] = randLocs[i,0] # set x location (um)
            cellTags['ynorm'] = randLocs[i,1] # set y location (um)
            cellTags['znorm'] = randLocs[i,2] # set z location (um)
            cellTags['x'] = f.net.params['sizeX'] * randLocs[i,0] # set x location (um)
            cellTags['y'] = f.net.params['sizeY'] * randLocs[i,1] # set y location (um)
            cellTags['z'] = f.net.params['sizeZ'] * randLocs[i,2] # set z location (um)
            if 'propList' not in cellTags: cellTags['propList'] = []  # initalize list of property sets if doesn't exist
            cells.append(cellModelClass(gid, cellTags)) # instantiate Cell object
            if f.cfg['verbose']: print('Cell %d/%d (gid=%d) of pop %s, on node %d, '%(i, f.net.params['scale'] * self.tags['numCells']-1, gid, self.tags['popLabel'], f.rank))
        f.lastGid = f.lastGid + self.tags['numCells'] 
        return cells

                
    def createCellsDensity(self):
        ''' Create population cells based on density'''
        cellModelClass = Cell
        cells = []
        volume =  f.net.params['sizeY']/1e3 * f.net.params['sizeX']/1e3 * f.net.params['sizeZ']/1e3  # calculate full volume
        for coord in ['x', 'y', 'z']:
            if coord+'Range' in self.tags:  # if user provided absolute range, convert to normalized
                self.tags[coord+'normRange'] = [point / f.net.params['size'+coord.upper()] for point in self.tags[coord+'Range']]
            if coord+'normRange' in self.tags:  # if normalized range, rescale volume
                minv = self.tags[coord+'normRange'][0] 
                maxv = self.tags[coord+'normRange'][1] 
                volume = volume * (maxv-minv)

        funcLocs = None  # start with no locations as a function of density function
        if isinstance(self.tags['density'], str): # check if density is given as a function
            strFunc = self.tags['density']  # string containing function
            strVars = [var for var in ['xnorm', 'ynorm', 'znorm'] if var in strFunc]  # get list of variables used 
            if not len(strVars) == 1:
                print 'Error: density function (%s) for population %s does not include "xnorm", "ynorm" or "znorm"'%(strFunc,self.tags['popLabel'])
                return
            coordFunc = strVars[0] 
            lambdaStr = 'lambda ' + coordFunc +': ' + strFunc # convert to lambda function 
            densityFunc = eval(lambdaStr)
            minRange = self.tags[coordFunc+'Range'][0]
            maxRange = self.tags[coordFunc+'Range'][1]

            interval = 0.001  # interval of location values to evaluate func in order to find the max cell density
            maxDensity = max(map(densityFunc, (arange(minRange, maxRange, interval))))  # max cell density 
            maxCells = volume * maxDensity  # max number of cells based on max value of density func 
            
            seed(f.sim.id32('%d' % f.cfg['randseed']))  # reset random number generator
            locsAll = minRange + ((maxRange-minRange)) * rand(int(maxCells), 1)  # random location values 
            locsProb = array(map(densityFunc, locsAll)) / maxDensity  # calculate normalized density for each location value (used to prune)
            allrands = rand(len(locsProb))  # create an array of random numbers for checking each location pos 
            
            makethiscell = locsProb>allrands  # perform test to see whether or not this cell should be included (pruning based on density func)
            funcLocs = [locsAll[i] for i in range(len(locsAll)) if i in array(makethiscell.nonzero()[0],dtype='int')] # keep only subset of yfuncLocs based on density func
            self.tags['numCells'] = len(funcLocs)  # final number of cells after pruning of location values based on density func
            if f.cfg['verbose']: print 'Volume=%.2f, maxDensity=%.2f, maxCells=%.0f, numCells=%.0f'%(volume, maxDensity, maxCells, self.tags['numCells'])

        else:  # NO ynorm-dep
            self.tags['numCells'] = int(self.tags['density'] * volume)  # = density (cells/mm^3) * volume (mm^3)

        # calculate locations of cells 
        seed(f.sim.id32('%d'%(f.cfg['randseed']+self.tags['numCells'])))
        randLocs = rand(self.tags['numCells'], 3)  # create random x,y,z locations
        for icoord, coord in enumerate(['x', 'y', 'z']):
            if coord+'normRange' in self.tags:  # if normalized range, rescale random locations
                minv = self.tags[coord+'normRange'][0] 
                maxv = self.tags[coord+'normRange'][1] 
                randLocs[:,icoord] = randLocs[:,icoord] / (maxv-minv) + minv
            if funcLocs and coordFunc == coord+'norm':  # if locations for this coordinate calcualated using density function
                randLocs[:,icoord] = funcLocs

        if f.cfg['verbose'] and not funcLocs: print 'Volume=%.4f, density=%.2f, numCells=%.0f'%(volume, self.tags['density'], self.tags['numCells'])


        for i in xrange(int(f.rank), self.tags['numCells'], f.nhosts):
            gid = f.lastGid+i
            self.cellGids.append(gid)  # add gid list of cells belonging to this population - not needed?
            cellTags = {k: v for (k, v) in self.tags.iteritems() if k in f.net.params['popTagsCopiedToCells']}  # copy all pop tags to cell tags, except those that are pop-specific
            cellTags['xnorm'] = randLocs[i,0]  # calculate x location (um)
            cellTags['ynorm'] = randLocs[i,1]  # calculate x location (um)
            cellTags['znorm'] = randLocs[i,2]  # calculate z location (um)
            cellTags['x'] = f.net.params['sizeX'] * randLocs[i,0]  # calculate x location (um)
            cellTags['y'] = f.net.params['sizeY'] * randLocs[i,1]  # calculate x location (um)
            cellTags['z'] = f.net.params['sizeZ'] * randLocs[i,2]  # calculate z location (um)
            if 'propList' not in cellTags: cellTags['propList'] = []  # initalize list of property sets if doesn't exist
            cells.append(cellModelClass(gid, cellTags)) # instantiate Cell object
            if f.cfg['verbose']: 
                print('Cell %d/%d (gid=%d) of pop %s, pos=(%2.f, %2.f, %2.f), on node %d, '%(i, self.tags['numCells']-1, gid, self.tags['popLabel'],cellTags['x'], cellTags['ynorm'], cellTags['z'], f.rank))
        f.lastGid = f.lastGid + self.tags['numCells'] 
        return cells


    def createCellsList(self):
        ''' Create population cells based on list of individual cells'''
        cellModelClass = Cell
        cells = []
        self.tags['numCells'] = len(self.tags['cellsList'])
        for i in xrange(int(f.rank), len(self.tags['cellsList']), f.nhosts):
            #if 'cellModel' in self.tags['cellsList'][i]:
            #    cellModelClass = getattr(f, self.tags['cellsList'][i]['cellModel'])  # select cell class to instantiate cells based on the cellModel tags
            gid = f.lastGid+i
            self.cellGids.append(gid)  # add gid list of cells belonging to this population - not needed?
            cellTags = {k: v for (k, v) in self.tags.iteritems() if k in f.net.params['popTagsCopiedToCells']}  # copy all pop tags to cell tags, except those that are pop-specific
            cellTags.update(self.tags['cellsList'][i])  # add tags specific to this cells
            for coord in ['x','y','z']:
                if coord in cellTags:  # if absolute coord exists
                    cellTags[coord+'norm'] = cellTags[coord]/f.net.params['size'+coord.upper()]  # calculate norm coord
                elif coord+'norm' in cellTags:  # elif norm coord exists
                    cellTags[coord] = cellTags[coord+'norm']*f.net.params['size'+coord.upper()]  # calculate norm coord
                else:
                    cellTags[coord+'norm'] = cellTags[coord] = 0
            if 'propList' not in cellTags: cellTags['propList'] = []  # initalize list of property sets if doesn't exist
            cells.append(cellModelClass(gid, cellTags)) # instantiate Cell object
            if f.cfg['verbose']: print('Cell %d/%d (gid=%d) of pop %d, on node %d, '%(i, self.tags['numCells']-1, gid, i, f.rank))
        f.lastGid = f.lastGid + len(self.tags['cellsList'])
        return cells


    def __getstate__(self): 
        ''' Removes non-picklable h objects so can be pickled and sent via py_alltoall'''
        odict = self.__dict__.copy() # copy the dict since we change it
        odict = f.sim.replaceFuncObj(odict)  # replace h objects with None so can be pickled
        return odict

