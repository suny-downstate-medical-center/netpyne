"""
cell.py 

Contains Cell related classes 

Contributors: salvadordura@gmail.com
"""

from numbers import Number
from copy import deepcopy
from time import sleep
from neuron import h # Import NEURON
from specs import Dict
import numpy as np
from random import seed, uniform
import sim


###############################################################################
#
# GENERIC CELL CLASS 
#
###############################################################################

class Cell (object):
    ''' Generic class for neuron models '''
    
    def __init__ (self, gid, tags):
        self.gid = gid  # global cell id 
        self.tags = tags  # dictionary of cell tags/attributes 
        self.conns = []  # list of connections
        self.stims = []  # list of stimuli


    def recordStimSpikes (self):
        sim.simData['stims'].update({'cell_'+str(self.gid): Dict()})
        for conn in self.conns:
            if conn['preGid'] == 'NetStim':
                stimSpikeVecs = h.Vector() # initialize vector to store 
                conn['hNetcon'].record(stimSpikeVecs)
                sim.simData['stims']['cell_'+str(self.gid)].update({conn['preLabel']: stimSpikeVecs})


    # Custom code for time-dependently shaping the weight of a NetCon corresponding to a NetStim.
    def _shapeStim(self, isi=1, variation=0, width=0.05, weight=10, start=0, finish=1, stimshape='gaussian'):
        from pylab import r_, convolve, shape, exp, zeros, hstack, array, rand
        
        # Create event times
        timeres = 0.001 # Time resolution = 1 ms = 500 Hz (DJK to CK: 500...?)
        pulselength = 10 # Length of pulse in units of width
        currenttime = 0
        timewindow = finish-start
        allpts = int(timewindow/timeres)
        output = []
        while currenttime<timewindow:
            # Note: The timeres/2 subtraction acts as an eps to avoid later int rounding errors.
            if currenttime>=0 and currenttime<timewindow-timeres/2: output.append(currenttime)
            currenttime = currenttime+isi+variation*(rand()-0.5)
        
        # Create single pulse
        npts = pulselength*width/timeres
        x = (r_[0:npts]-npts/2+1)*timeres
        if stimshape=='gaussian': 
            pulse = exp(-2*(2*x/width-1)**2) # Offset by 2 standard deviations from start
            pulse = pulse/max(pulse)
        elif stimshape=='square': 
            pulse = zeros(shape(x))
            pulse[int(npts/2):int(npts/2)+int(width/timeres)] = 1 # Start exactly on time
        else:
            raise Exception('Stimulus shape "%s" not recognized' % stimshape)
        
        # Create full stimulus
        events = zeros((allpts))
        events[array(array(output)/timeres,dtype=int)] = 1
        fulloutput = convolve(events,pulse,mode='full')*weight # Calculate the convolved input signal, scaled by rate
        fulloutput = fulloutput[npts/2-1:-npts/2]   # Slices out where the convolved pulse train extends before and after sequence of allpts.
        fulltime = (r_[0:allpts]*timeres+start)*1e3 # Create time vector and convert to ms
        
        fulltime = hstack((0,fulltime,fulltime[-1]+timeres*1e3)) # Create "bookends" so always starts and finishes at zero
        fulloutput = hstack((0,fulloutput,0)) # Set weight to zero at either end of the stimulus period
        events = hstack((0,events,0)) # Ditto
        stimvecs = deepcopy([fulltime, fulloutput, events]) # Combine vectors into a matrix                   
        
        return stimvecs  


    def addNetStim (self, params, stimContainer=None):
        if not stimContainer:
            self.stims.append(Dict(params.copy()))  # add new stim to Cell object
            stimContainer = self.stims[-1]

            if sim.cfg.verbose: print('  Created %s NetStim for cell gid=%d'% (params['source'], self.gid))
        
        if sim.cfg.createNEURONObj:
            rand = h.Random()
            stimContainer['hRandom'] = rand  # add netcon object to dict in conns list

            if isinstance(params['rate'], basestring):
                if params['rate'] == 'variable':
                    try:
                        netstim = h.NSLOC()
                        netstim.interval = 0.1**-1*1e3 # inverse of the frequency and then convert from Hz^-1 to ms (set very low)
                        netstim.noise = params['noise']
                    except:
                        print 'Error: tried to create variable rate NetStim but NSLOC mechanism not available'
                else:
                    print 'Error: Unknown stimulation rate type: %s'%(h.params['rate'])
            else:
                netstim = h.NetStim() 
                netstim.interval = params['rate']**-1*1e3 # inverse of the frequency and then convert from Hz^-1 to ms
                netstim.noise = params['noise'] # note: random number generator initialized via noiseFromRandom() from sim.preRun()
                netstim.start = params['start']
            netstim.noiseFromRandom(rand)  # use random number generator 
            netstim.number = params['number']   
                
            stimContainer['hNetStim'] = netstim  # add netstim object to dict in stim list

            return stimContainer['hNetStim']


    def __getstate__ (self): 
        ''' Removes non-picklable h objects so can be pickled and sent via py_alltoall'''
        odict = self.__dict__.copy() # copy the dict since we change it
        odict = sim.copyReplaceItemObj(odict, keystart='h', newval=None)  # replace h objects with None so can be pickled
        return odict


    def recordTraces (self):
        # set up voltagse recording; recdict will be taken from global context
        for key, params in sim.cfg.recordTraces.iteritems():
            
            conditionsMet = 1
            
            if 'conds' in params:
                for (condKey,condVal) in params['conds'].iteritems():  # check if all conditions are met
                    # choose what to comapare to 
                    if condKey in ['postGid']:
                        compareTo = self.gid
                    else:
                        compareTo = self.tags[condKey]

                    # check if conditions met
                    if isinstance(condVal, list) and isinstance(condVal[0], Number):
                        if compareTo < condVal[0] or compareTo > condVal[1]:
                            conditionsMet = 0
                            break
                    elif isinstance(condVal, list) and isinstance(condVal[0], basestring):
                        if compareTo not in condVal:
                            conditionsMet = 0
                            break 
                    elif compareTo != condVal: 
                        conditionsMet = 0
                        break
                        
            if conditionsMet:
                try:
                    ptr = None
                    if 'loc' in params:
                        if 'mech' in params:  # eg. soma(0.5).hh._ref_gna
                            ptr = self.secs[params['sec']]['hSec'](params['loc']).__getattribute__(params['mech']).__getattribute__('_ref_'+params['var'])
                        elif 'synMech' in params:  # eg. soma(0.5).AMPA._ref_g
                            sec = self.secs[params['sec']]
                            synMech = next((synMech for synMech in sec['synMechs'] if synMech['label']==params['synMech'] and synMech['loc']==params['loc']), None)
                            ptr = synMech['hSyn'].__getattribute__('_ref_'+params['var'])
                        else:  # eg. soma(0.5)._ref_v
                            ptr = self.secs[params['sec']]['hSec'](params['loc']).__getattribute__('_ref_'+params['var'])
                    elif 'synMech' in params:  # special case where want to record from multiple synMechs
                        if 'sec' in params:
                            sec = self.secs[params['sec']]
                            synMechs = [synMech for synMech in sec['synMechs'] if synMech['label']==params['synMech']]
                            ptr = [synMech['hSyn'].__getattribute__('_ref_'+params['var']) for synMech in synMechs]
                            secLocs = [params.sec+str(synMech['loc']) for synMech in synMechs]
                        else: 
                            ptr = []
                            secLocs = []
                            for secName,sec in self.secs.iteritems():
                                synMechs = [synMech for synMech in sec['synMechs'] if synMech['label']==params['synMech']]
                                ptr.extend([synMech['hSyn'].__getattribute__('_ref_'+params['var']) for synMech in synMechs])
                                secLocs.extend([secName+'_'+str(synMech['loc']) for synMech in synMechs])

                    else:
                        if 'pointp' in params: # eg. soma.izh._ref_u
                            if params['pointp'] in self.secs[params['sec']]['pointps']:
                                ptr = self.secs[params['sec']]['pointps'][params['pointp']]['hPointp'].__getattribute__('_ref_'+params['var'])
                        elif 'var' in params: # point process cell eg. cell._ref_v
                            ptr = self.hPointp.__getattribute__('_ref_'+params['var'])

                    if ptr:  # if pointer has been created, then setup recording
                        if isinstance(ptr, list):
                            sim.simData[key]['cell_'+str(self.gid)] = {}
                            for ptrItem,secLoc in zip(ptr, secLocs):
                                sim.simData[key]['cell_'+str(self.gid)][secLoc] = h.Vector(sim.cfg.duration/sim.cfg.recordStep+1).resize(0)
                                sim.simData[key]['cell_'+str(self.gid)][secLoc].record(ptrItem, sim.cfg.recordStep)
                        else:
                            sim.simData[key]['cell_'+str(self.gid)] = h.Vector(sim.cfg.duration/sim.cfg.recordStep+1).resize(0)
                            sim.simData[key]['cell_'+str(self.gid)].record(ptr, sim.cfg.recordStep)
                        if sim.cfg.verbose: print '  Recording ', key, 'from cell ', self.gid, ' with parameters: ',str(params)
                except:
                    if sim.cfg.verbose: print '  Cannot record ', key, 'from cell ', self.gid
            else:
                if sim.cfg.verbose: print '  Conditions preclude recording ', key, ' from cell ', self.gid
        #else:
        #    if sim.cfg.verbose: print '  NOT recording ', key, 'from cell ', self.gid, ' with parameters: ',str(params)



###############################################################################
#
# COMPARTMENTAL CELL CLASS 
#
###############################################################################

class CompartCell (Cell):
    ''' Class for section-based neuron models '''
    
    def __init__ (self, gid, tags, create=True, associateGid=True):
        super(CompartCell, self).__init__(gid, tags)
        self.secs = Dict()  # dict of sections
        self.secLists = Dict()  # dict of sectionLists

        if create: self.create()  # create cell 
        if associateGid: self.associateGid() # register cell for this node


    def create (self):
        for propLabel, prop in sim.net.params.cellParams.iteritems():  # for each set of cell properties
            conditionsMet = 1
            for (condKey,condVal) in prop['conds'].iteritems():  # check if all conditions are met
                if isinstance(condVal, list): 
                    if isinstance(condVal[0], Number):
                        if self.tags.get(condKey) < condVal[0] or self.tags.get(condKey) > condVal[1]:
                            conditionsMet = 0
                            break
                    elif isinstance(condVal[0], basestring):
                        if self.tags.get(condKey) not in condVal:
                            conditionsMet = 0
                            break 
                elif self.tags.get(condKey) != condVal: 
                    conditionsMet = 0
                    break
            if conditionsMet:  # if all conditions are met, set values for this cell
                if sim.cfg.includeParamsLabel:
                    if 'label' not in self.tags:
                        self.tags['label'] = [propLabel] # create list of property sets
                    else:
                        self.tags['label'].append(propLabel)  # add label of cell property set to list of property sets for this cell
                if sim.cfg.createPyStruct:
                    self.createPyStruct(prop)
                if sim.cfg.createNEURONObj:
                    self.createNEURONObj(prop)  # add sections, mechanisms, synaptic mechanisms, geometry and topolgy specified by this property set


    def modify (self, prop):
        conditionsMet = 1
        for (condKey,condVal) in prop['conds'].iteritems():  # check if all conditions are met
            if condKey=='label':
                if condVal not in self.tags['label']:
                    conditionsMet = 0
                    break
            elif isinstance(condVal, list): 
                if isinstance(condVal[0], Number):
                    if self.tags.get(condKey) < condVal[0] or self.tags.get(condKey) > condVal[1]:
                        conditionsMet = 0
                        break
                elif isinstance(condVal[0], basestring):
                    if self.tags.get(condKey) not in condVal:
                        conditionsMet = 0
                        break 
            elif self.tags.get(condKey) != condVal: 
                conditionsMet = 0
                break

        if conditionsMet:  # if all conditions are met, set values for this cell
            if sim.cfg.createPyStruct:
                self.createPyStruct(prop)
            if sim.cfg.createNEURONObj:
                self.createNEURONObj(prop)  # add sections, mechanisms, synaptic mechanisms, geometry and topolgy specified by this property set


    def createPyStruct (self, prop):
        # set params for all sections
        for sectName,sectParams in prop['secs'].iteritems(): 
            # create section
            if sectName not in self.secs:
                self.secs[sectName] = Dict()  # create section dict
            sec = self.secs[sectName]  # pointer to section
            
            # add distributed mechanisms 
            if 'mechs' in sectParams:
                for mechName,mechParams in sectParams['mechs'].iteritems(): 
                    if 'mechs' not in sec:
                        sec['mechs'] = Dict()
                    if mechName not in sec['mechs']: 
                        sec['mechs'][mechName] = Dict()  
                    for mechParamName,mechParamValue in mechParams.iteritems():  # add params of the mechanism
                        sec['mechs'][mechName][mechParamName] = mechParamValue
            
            # add ion info 
            if 'ions' in sectParams:
                for ionName,ionParams in sectParams['ions'].iteritems(): 
                    if 'ions' not in sec:
                        sec['ions'] = Dict()
                    if ionName not in sec['ions']: 
                        sec['ions'][ionName] = Dict()  
                    for ionParamName,ionParamValue in ionParams.iteritems():  # add params of the ion
                        sec['ions'][ionName][ionParamName] = ionParamValue


            # add synMechs
            if 'synMechs' in sectParams:
                for synMech in sectParams['synMechs']:
                    if 'label' in synMech and 'loc' in synMech:
                        self.addSynMech(synLabel=synMech['label'], secLabel=sectName, loc=synMech['loc'])

            # add point processes
            if 'pointps' in sectParams:
                for pointpName,pointpParams in sectParams['pointps'].iteritems(): 
                    #if self.tags['cellModel'] == pointpName: # only required if want to allow setting various cell models in same rule
                    if 'pointps' not in sec:
                        sec['pointps'] = Dict()
                    if pointpName not in sec['pointps']: 
                        sec['pointps'][pointpName] = Dict()  
                    for pointpParamName,pointpParamValue in pointpParams.iteritems():  # add params of the mechanism
                        sec['pointps'][pointpName][pointpParamName] = pointpParamValue


            # add geometry params 
            if 'geom' in sectParams:
                for geomParamName,geomParamValue in sectParams['geom'].iteritems():  
                    if 'geom' not in sec:
                        sec['geom'] = Dict()
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
                    sec['topol'] = Dict()
                for topolParamName,topolParamValue in sectParams['topol'].iteritems(): 
                    sec['topol'][topolParamName] = topolParamValue

            # add other params
            if 'spikeGenLoc' in sectParams:
                sec['spikeGenLoc'] = sectParams['spikeGenLoc']

            if 'vinit' in sectParams:
                sec['vinit'] = sectParams['vinit']

            if 'weightNorm' in sectParams:
                sec['weightNorm'] = sectParams['weightNorm']

        # add sectionLists
        if 'secLists' in prop:
            self.secLists.update(prop['secLists'])  # diction of section lists


    def initV (self): 
        for sec in self.secs.values():
            if 'vinit' in sec:
                sec['hSec'].v = sec['vinit']


    def createNEURONObj (self, prop):
        # set params for all sections
        for sectName,sectParams in prop['secs'].iteritems(): 
            # create section
            if sectName not in self.secs:
                self.secs[sectName] = Dict()  # create sect dict if doesn't exist
            if 'hSec' not in self.secs[sectName] or self.secs[sectName]['hSec'] == None: 
                self.secs[sectName]['hSec'] = h.Section(name=sectName, cell=self)  # create h Section object
            sec = self.secs[sectName]  # pointer to section

            # set geometry params 
            if 'geom' in sectParams:
                for geomParamName,geomParamValue in sectParams['geom'].iteritems():  
                    if not type(geomParamValue) in [list, dict]:  # skip any list or dic params
                        setattr(sec['hSec'], geomParamName, geomParamValue)

                # set 3d geometry
                if 'pt3d' in sectParams['geom']:  
                    h.pt3dclear(sec=sec['hSec'])
                    x = self.tags['x']
                    y = -self.tags['y'] # Neuron y-axis positive = upwards, so assume pia=0 and cortical depth = neg
                    z = self.tags['z']
                    for pt3d in sectParams['geom']['pt3d']:
                        h.pt3dadd(x+pt3d[0], y+pt3d[1], z+pt3d[2], pt3d[3], sec=sec['hSec'])

            # add distributed mechanisms 
            if 'mechs' in sectParams:
                for mechName,mechParams in sectParams['mechs'].iteritems(): 
                    if mechName not in sec['mechs']: 
                        sec['mechs'][mechName] = Dict()
                    sec['hSec'].insert(mechName)
                    for mechParamName,mechParamValue in mechParams.iteritems():  # add params of the mechanism
                        mechParamValueFinal = mechParamValue
                        for iseg,seg in enumerate(sec['hSec']):  # set mech params for each segment
                            if type(mechParamValue) in [list]: 
                                mechParamValueFinal = mechParamValue[iseg]
                            if mechParamValueFinal is not None:  # avoid setting None values
                                seg.__getattribute__(mechName).__setattr__(mechParamName,mechParamValueFinal)
                            
            # add ions
            if 'ions' in sectParams:
                for ionName,ionParams in sectParams['ions'].iteritems(): 
                    if ionName not in sec['ions']: 
                        sec['ions'][ionName] = Dict()
                    sec['hSec'].insert(ionName+'_ion')    # insert mechanism
                    for ionParamName,ionParamValue in ionParams.iteritems():  # add params of the mechanism
                        ionParamValueFinal = ionParamValue
                        for iseg,seg in enumerate(sec['hSec']):  # set ion params for each segment
                            if type(ionParamValue) in [list]: 
                                ionParamValueFinal = ionParamValue[iseg]
                            if ionParamName == 'e':
                                seg.__setattr__(ionParamName+ionName,ionParamValueFinal)
                            elif ionParamName == 'init_ext_conc':
                                seg.__setattr__('%so'%ionName,ionParamValueFinal)
                                h('%so0_%s_ion = %s'%(ionName,ionName,ionParamValueFinal))  # e.g. cao0_ca_ion, the default initial value
                            elif ionParamName == 'init_int_conc':
                                seg.__setattr__('%si'%ionName,ionParamValueFinal)
                                h('%si0_%s_ion = %s'%(ionName,ionName,ionParamValueFinal))  # e.g. cai0_ca_ion, the default initial value
                                
                    #if sim.cfg.verbose: print("Updated ion: %s in %s, e: %s, o: %s, i: %s" % \
                    #         (ionName, sectName, seg.__getattribute__('e'+ionName), seg.__getattribute__(ionName+'o'), seg.__getattribute__(ionName+'i')))

            # add synMechs (only used when loading)
            if 'synMechs' in sectParams:
                for synMech in sectParams['synMechs']:
                    if 'label' in synMech and 'loc' in synMech:
                        self.addSynMech(synLabel=synMech['label'], secLabel=sectName, loc=synMech['loc'])

            # add point processes
            if 'pointps' in sectParams:
                for pointpName,pointpParams in sectParams['pointps'].iteritems(): 
                    #if self.tags['cellModel'] == pointpParams:  # only required if want to allow setting various cell models in same rule
                    if pointpName not in sec['pointps']:
                        sec['pointps'][pointpName] = Dict() 
                    pointpObj = getattr(h, pointpParams['mod'])
                    loc = pointpParams['loc'] if 'loc' in pointpParams else 0.5  # set location
                    sec['pointps'][pointpName]['hPointp'] = pointpObj(loc, sec = sec['hSec'])  # create h Pointp object (eg. h.Izhi2007b)
                    for pointpParamName,pointpParamValue in pointpParams.iteritems():  # add params of the point process
                        if pointpParamName not in ['mod', 'loc', 'vref', 'synList'] and not pointpParamName.startswith('_'):
                            setattr(sec['pointps'][pointpName]['hPointp'], pointpParamName, pointpParamValue)


        # set topology 
        for sectName,sectParams in prop['secs'].iteritems():  # iterate sects again for topology (ensures all exist)
            sec = self.secs[sectName]  # pointer to section # pointer to child sec
            if 'topol' in sectParams:
                if sectParams['topol']:
                    sec['hSec'].connect(self.secs[sectParams['topol']['parentSec']]['hSec'], sectParams['topol']['parentX'], sectParams['topol']['childX'])  # make topol connection


    def addSynMechsNEURONObj(self):
        # set params for all sections
        for sectName,sectParams in self.secs.iteritems(): 
            # add synMechs (only used when loading)
            if 'synMechs' in sectParams:
                for synMech in sectParams['synMechs']:
                    if 'label' in synMech and 'loc' in synMech:
                        self.addSynMech(synLabel=synMech['label'], secLabel=sectName, loc=synMech['loc'])


    # Create NEURON objs for conns and syns if included in prop (used when loading)
    def addStimsNEURONObj(self):
        # assumes python structure exists
        for stimParams in self.stims:
            if stimParams['type'] == 'NetStim':
                self.addNetStim(stimParams, stimContainer=stimParams)
       
            elif stimParams['type'] in ['IClamp', 'VClamp', 'SEClamp', 'AlphaSynapse']:
                stim = getattr(h, stimParams['type'])(self.secs[stimParams['sec']]['hSec'](stimParams['loc']))
                stimProps = {k:v for k,v in stimParams.iteritems() if k not in ['label', 'type', 'source', 'loc', 'sec', 'h'+stimParams['type']]}
                for stimPropName, stimPropValue in stimProps.iteritems(): # set mechanism internal stimParams
                    if isinstance(stimPropValue, list):
                        if stimPropName == 'amp': 
                            for i,val in enumerate(stimPropValue):
                                stim.amp[i] = val
                        elif stimPropName == 'dur': 
                            for i,val in enumerate(stimPropValue):
                                stim.dur[i] = val
                        #setattr(stim, stimParamName._ref_[0], stimParamValue[0])
                    else: 
                        setattr(stim, stimPropName, stimPropValue)
                stimParams['h'+stimParams['type']] = stim  # add stim object to dict in stims list
           

    # Create NEURON objs for conns and syns if included in prop (used when loading)
    def addConnsNEURONObj(self):
        # Note: loading connections to point process (eg. Izhi2007a) not yet supported
        # Note: assumes weight is in index 0 (netcon.weight[0])
        # assumes python structure exists
        for conn in self.conns:
            # set postsyn target
            synMech = next((synMech for synMech in self.secs[conn['sec']]['synMechs'] if synMech['label']==conn['synMech'] and synMech['loc']==conn['loc']), None)
            if not synMech: 
                synMech = self.addSynMech(conn['synMech'], conn['sec'], conn['loc'])
                #continue  # go to next conn
            try:
                postTarget = synMech['hSyn']
            except:
                print '\nError: no synMech available for conn: ', conn
                print ' cell tags: ',self.tags
                print ' cell synMechs: ',self.secs[conn['sec']]['synMechs']
                exit()

            # create NetCon
            if conn['preGid'] == 'NetStim':
                netstim = next((stim['hNetStim'] for stim in self.stims if stim['source']==conn['preLabel']), None)
                if netstim:
                    netcon = h.NetCon(netstim, postTarget)
                else: continue
            else:
                #cell = next((c for c in sim.net.cells if c.gid == conn['preGid']), None)
                netcon = sim.pc.gid_connect(conn['preGid'], postTarget)

            netcon.weight[0] = conn['weight']
            netcon.delay = conn['delay']
            netcon.threshold = conn.get('threshold', sim.net.params.defaultThreshold)
            conn['hNetcon'] = netcon
            
            # Add plasticity 
            if conn.get('plast'):
                self._addConnPlasticity(conn['plast'], self.secs[conn['sec']], netcon, 0)


    def associateGid (self, threshold = 10.0):
        if self.secs:
            if sim.cfg.createNEURONObj: 
                sim.pc.set_gid2node(self.gid, sim.rank) # this is the key call that assigns cell gid to a particular node
                sec = next((secParams for secName,secParams in self.secs.iteritems() if 'spikeGenLoc' in secParams), None) # check if any section has been specified as spike generator
                if sec:
                    loc = sec['spikeGenLoc']  # get location of spike generator within section
                else:
                    sec = self.secs['soma'] if 'soma' in self.secs else self.secs[self.secs.keys()[0]]  # use soma if exists, otherwise 1st section
                    loc = 0.5
                nc = None
                if 'pointps' in sec:  # if no syns, check if point processes with 'vref' (artificial cell)
                    for pointpName, pointpParams in sec['pointps'].iteritems():
                        if 'vref' in pointpParams:
                            nc = h.NetCon(sec['pointps'][pointpName]['hPointp'].__getattribute__('_ref_'+pointpParams['vref']), None, sec=sec['hSec'])
                            break
                if not nc:  # if still haven't created netcon  
                    nc = h.NetCon(sec['hSec'](loc)._ref_v, None, sec=sec['hSec'])
                nc.threshold = threshold
                sim.pc.cell(self.gid, nc, 1)  # associate a particular output stream of events
                del nc # discard netcon
        sim.net.gid2lid[self.gid] = len(sim.net.lid2gid)
        sim.net.lid2gid.append(self.gid) # index = local id; value = global id


    def addSynMech (self, synLabel, secLabel, loc):
        synMechParams = sim.net.params.synMechParams.get(synLabel)  # get params for this synMech
        sec = self.secs.get(secLabel, None)
        # add synaptic mechanism to python struct
        if 'synMechs' not in sec or not isinstance(sec['synMechs'], list):
            sec['synMechs'] = []

        if synMechParams and sec:  # if both the synMech and the section exist
            if sim.cfg.createPyStruct and sim.cfg.addSynMechs:
                synMech = next((synMech for synMech in sec['synMechs'] if synMech['label']==synLabel and synMech['loc']==loc), None)
                if not synMech:  # if synMech not in section, then create
                    synMech = Dict({'label': synLabel, 'loc': loc})
                    for paramName, paramValue in synMechParams.iteritems():
                        synMech[paramName] = paramValue
                    sec['synMechs'].append(synMech)
            else:
                synMech = None

            if sim.cfg.createNEURONObj and sim.cfg.addSynMechs: 
                # add synaptic mechanism NEURON objectes 
                if not synMech:  # if pointer not created in createPyStruct, then check 
                    synMech = next((synMech for synMech in sec['synMechs'] if synMech['label']==synLabel and synMech['loc']==loc), None)
                if not synMech:  # if still doesnt exist, then create
                    synMech = Dict()
                    sec['synMechs'].append(synMech)
                if not synMech.get('hSyn'):  # if synMech doesn't have NEURON obj, then create
                    synObj = getattr(h, synMechParams['mod'])
                    synMech['hSyn'] = synObj(loc, sec=sec['hSec'])  # create h Syn object (eg. h.Exp2Syn)
                    for synParamName,synParamValue in synMechParams.iteritems():  # add params of the synaptic mechanism
                        if synParamName not in ['label', 'mod', 'selfNetCon', 'loc']:
                            setattr(synMech['hSyn'], synParamName, synParamValue)
                        elif synParamName == 'selfNetcon':  # create self netcon required for some synapses (eg. homeostatic)
                            secLabelNetCon = synParamValue.get('sec', 'soma')
                            locNetCon = synParamValue.get('loc', 0.5)
                            secNetCon = self.secs.get(secLabelNetCon, None)
                            synMech['hNetcon'] = h.NetCon(secNetCon['hSec'](locNetCon)._ref_v, synMech[''], sec=secNetCon['hSec'])
                            for paramName,paramValue in synParamValue.iteritems():
                                if paramName == 'weight':
                                    synMech['hNetcon'].weight[0] = paramValue
                                elif paramName not in ['sec', 'loc']:
                                    setattr(synMech['hNetcon'], paramName, paramValue)
            else:
                synMech = None
            return synMech


    def modifySynMechs (self, params):
        conditionsMet = 1
        if 'cellConds' in params:
            if conditionsMet:
                for (condKey,condVal) in params['cellConds'].iteritems():  # check if all conditions are met
                    # check if conditions met
                    if isinstance(condVal, list):
                        if self.tags.get(condKey) < condVal[0] or self.tags.get(condKey) > condVal[1]:
                            conditionsMet = 0
                            break
                    elif self.tags.get(condKey) != condVal: 
                        conditionsMet = 0
                        break

        if conditionsMet:
            for secLabel,sec in self.secs.iteritems():
                for synMech in sec['synMechs']:
                    conditionsMet = 1
                    if 'conds' in params:
                        for (condKey,condVal) in params['conds'].iteritems():  # check if all conditions are met
                            # check if conditions met
                            if condKey == 'sec':
                                if condVal != secLabel:
                                    conditionsMet = 0
                                    break
                            elif isinstance(condVal, list) and isinstance(condVal[0], Number):
                                if synMech.get(condKey) < condVal[0] or synMech.get(condKey) > condVal[1]:
                                    conditionsMet = 0
                                    break
                            elif isinstance(condVal, list) and isinstance(condVal[0], basestring):
                                if synMech.get(condKey) not in condVal:
                                    conditionsMet = 0
                                    break 
                            elif synMech.get(condKey) != condVal: 
                                conditionsMet = 0
                                break

                    if conditionsMet:  # if all conditions are met, set values for this cell
                        exclude = ['conds', 'cellConds', 'label', 'mod', 'selfNetCon', 'loc']
                        for synParamName,synParamValue in {k: v for k,v in params.iteritems() if k not in exclude}.iteritems():
                            if sim.cfg.createPyStruct: 
                                synMech[synParamName] = synParamValue
                            if sim.cfg.createNEURONObj:
                                try: 
                                    setattr(synMech['hSyn'], synParamName, synParamValue)
                                except:
                                    print 'Error setting %s=%s on synMech' % (synParamName, str(synParamValue))
    



    def addConn (self, params, netStimParams = None):
        threshold = params.get('threshold', sim.net.params.defaultThreshold)  # if no threshold specified, set default
        if params.get('weight') is None: params['weight'] = sim.net.params.defaultWeight # if no weight, set default
        if params.get('delay') is None: params['delay'] = sim.net.params.defaultDelay # if no delay, set default
        if params.get('loc') is None: params['loc'] = 0.5 # if no loc, set default
        if params.get('synsPerConn') is None: params['synsPerConn'] = 1 # if no synsPerConn, set default

        # Avoid self connections
        if params['preGid'] == self.gid:
            if sim.cfg.verbose: print '  Error: attempted to create self-connection on cell gid=%d, section=%s '%(self.gid, params.get('sec'))
            return  # if self-connection return

        # Get list of section labels
        secLabels = self._setConnSections(params)
        if secLabels == -1: return  # if no section available exit func 

        # Weight
        weights = self._setConnWeights(params, netStimParams, secLabels)
        weightIndex = 0  # set default weight matrix index   

        # Delays
        if isinstance(params['delay'],list):
            delays = params['delay'] 
        else:
            delays = [params['delay']] * params['synsPerConn']

        # Check if target is point process (artificial cell) with V not in section
        pointp, weightIndex = self._setConnPointP(params, secLabels, weightIndex)
        if pointp == -1: return

        # Add synaptic mechanisms
        if not pointp: # check not a point process
            synMechs, synMechSecs, synMechLocs = self._setConnSynMechs(params, secLabels)
            if synMechs == -1: return

        # Adapt weight based on section weightNorm (normalization based on section location)
        for i,(sec,loc) in enumerate(zip(synMechSecs, synMechLocs)):
            if 'weightNorm' in self.secs[sec] and isinstance(self.secs[sec]['weightNorm'], list): 
                nseg = self.secs[sec]['geom']['nseg']
                weights[i] = weights[i] * self.secs[sec]['weightNorm'][int(round(loc*nseg))-1] 

        # Create connections
        for i in range(params['synsPerConn']):

            if netStimParams:
                    netstim = self.addNetStim(netStimParams)

            if params.get('gapJunction', False) == True:  # only run for post gap junc (not pre)
                preGapId = 10e9*sim.rank + sim.net.lastGapId  # global index for presyn gap junc
                postGapId = preGapId + 1  # global index for postsyn gap junc
                sim.net.lastGapId += 2  # keep track of num of gap juncs in this node
                if not getattr(sim.net, 'preGapJunctions', False): 
                    sim.net.preGapJunctions = []  # if doesn't exist, create list to store presynaptic cell gap junctions
                preGapParams = {'gid': params['preGid'],
                                'preGid': self.gid, 
                                'sec': params.get('preSec', 'soma'), 
                                'loc': params.get('preLoc', 0.5), 
                                'weight': params['weight'], 
                                'gapId': preGapId,
                                'preGapId': postGapId,
                                'synMech': params['synMech'],
                                'gapJunction': 'pre'}
                sim.net.preGapJunctions.append(preGapParams)  # add conn params to add pre gap junction later

            # Python Structure
            if sim.cfg.createPyStruct:
                connParams = {k:v for k,v in params.iteritems() if k not in ['synsPerConn']} 
                connParams['weight'] = weights[i]
                connParams['delay'] = delays[i]
                if not pointp:
                    connParams['sec'] = synMechSecs[i]
                    connParams['loc'] = synMechLocs[i]
                if netStimParams:
                    connParams['preGid'] = 'NetStim'
                    connParams['preLabel'] = netStimParams['source']
                if params.get('gapJunction', 'False') == True:  # only run for post gap junc (not pre)
                    connParams['gapId'] = postGapId
                    connParams['preGapId'] = preGapId
                    connParams['gapJunction'] = 'post'
                self.conns.append(Dict(connParams))                
            else:  # do not fill in python structure (just empty dict for NEURON obj)
                self.conns.append(Dict())

            # NEURON objects
            if sim.cfg.createNEURONObj:
                # gap junctions
                if params.get('gapJunction', 'False') in [True, 'pre', 'post']:  # create NEURON obj for pre and post
                    synMechs[i]['hSyn'].weight = weights[i]
                    sourceVar = self.secs[synMechSecs[i]]['hSec'](synMechLocs[i])._ref_v
                    targetVar = synMechs[i]['hSyn']._ref_vpeer  # assumes variable is vpeer -- make a parameter
                    sec = self.secs[synMechSecs[i]]
                    sim.pc.target_var(targetVar, connParams['gapId'])
                    self.secs[synMechSecs[i]]['hSec'].push()
                    sim.pc.source_var(sourceVar, connParams['preGapId'])
                    h.pop_section()
                    netcon = None

                # connections using NetCons
                else:  
                    if pointp:
                        sec = self.secs[secLabels[0]]
                        postTarget = sec['pointps'][pointp]['hPointp'] #  local point neuron 
                    else:
                        sec = self.secs[synMechSecs[i]]
                        postTarget = synMechs[i]['hSyn'] # local synaptic mechanism

                    if netStimParams:
                        netcon = h.NetCon(netstim, postTarget) # create Netcon between netstim and target
                    else:
                        netcon = sim.pc.gid_connect(params['preGid'], postTarget) # create Netcon between global gid and target
                    
                    netcon.weight[weightIndex] = weights[i]  # set Netcon weight
                    netcon.delay = delays[i]  # set Netcon delay
                    netcon.threshold = threshold  # set Netcon threshold
                    self.conns[-1]['hNetcon'] = netcon  # add netcon object to dict in conns list
            

                # Add time-dependent weight shaping
                if 'shape' in params and params['shape']:
                    
                    temptimevecs = []
                    tempweightvecs = []
                    
                    # Default shape
                    pulsetype = params['shape']['pulseType'] if 'pulseType' in params['shape'] else 'square'
                    pulsewidth = params['shape']['pulseWidth'] if 'pulseWidth' in params['shape'] else 100.0
                    pulseperiod = params['shape']['pulsePeriod'] if 'pulsePeriod' in params['shape'] else 100.0
                    
                    # Determine on-off switching time pairs for stimulus, where default is always on
                    if 'switchOnOff' not in params['shape']:
                        switchtimes = [0, sim.cfg.duration]
                    else:
                        if not params['shape']['switchOnOff'] == sorted(params['shape']['switchOnOff']):
                            raise Exception('On-off switching times for a particular stimulus are not monotonic')   
                        switchtimes = deepcopy(params['shape']['switchOnOff'])
                        switchtimes.append(sim.cfg.duration)
                    
                    switchiter = iter(switchtimes)
                    switchpairs = zip(switchiter,switchiter)
                    for pair in switchpairs:
                        # Note: Cliff's makestim code is in seconds, so conversions from ms to s occurs in the args.
                        stimvecs = self._shapeStim(width=float(pulsewidth)/1000.0, isi=float(pulseperiod)/1000.0, weight=params['weight'], start=float(pair[0])/1000.0, finish=float(pair[1])/1000.0, stimshape=pulsetype)
                        temptimevecs.extend(stimvecs[0])
                        tempweightvecs.extend(stimvecs[1])
                    
                    self.conns[-1]['shapeTimeVec'] = h.Vector().from_python(temptimevecs)
                    self.conns[-1]['shapeWeightVec'] = h.Vector().from_python(tempweightvecs)
                    self.conns[-1]['shapeWeightVec'].play(netcon._ref_weight[weightIndex], self.conns[-1]['shapeTimeVec'])


                # Add plasticity
                self._addConnPlasticity(params, sec, netcon, weightIndex)

            if sim.cfg.verbose: 
                sec = params['sec'] if pointp else synMechSecs[i]
                loc = params['loc'] if pointp else synMechLocs[i]
                preGid = netStimParams['source']+' NetStim' if netStimParams else params['preGid']
                print('  Created connection preGid=%s, postGid=%s, sec=%s, loc=%.4g, synMech=%s, weight=%.4g, delay=%.2f, threshold=%s'%
                    (preGid, self.gid, sec, loc, params['synMech'], weights[i], delays[i], threshold))


    def modifyConns (self, params):
        for conn in self.conns:
            conditionsMet = 1
            
            if 'conds' in params:
                for (condKey,condVal) in params['conds'].iteritems():  # check if all conditions are met
                    # choose what to comapare to 
                    if condKey in ['postGid']:
                        compareTo = self.gid
                    else:
                        compareTo = conn.get(condKey)

                    # check if conditions met
                    if isinstance(condVal, list) and isinstance(condVal[0], Number):
                        if compareTo < condVal[0] or compareTo > condVal[1]:
                            conditionsMet = 0
                            break
                    elif isinstance(condVal, list) and isinstance(condVal[0], basestring):
                        if compareTo not in condVal:
                            conditionsMet = 0
                            break 
                    elif compareTo != condVal: 
                        conditionsMet = 0
                        break

            if conditionsMet and 'postConds' in params:
                for (condKey,condVal) in params['postConds'].iteritems():  # check if all conditions are met
                    # check if conditions met
                    if isinstance(condVal, list) and isinstance(condVal[0], Number):
                        if self.tags.get(condKey) < condVal[0] or self.tags.get(condKey) > condVal[1]:
                            conditionsMet = 0
                            break
                    elif isinstance(condVal, list) and isinstance(condVal[0], basestring):
                        if self.tags.get(condKey) not in condVal:
                            conditionsMet = 0
                            break 
                    elif self.tags.get(condKey) != condVal: 
                        conditionsMet = 0
                        break

            if conditionsMet and 'preConds' in params: 
                print 'Warning: modifyConns() does not yet support conditions of presynaptic cells'

            if conditionsMet:  # if all conditions are met, set values for this cell
                if sim.cfg.createPyStruct:
                    for paramName, paramValue in {k: v for k,v in params.iteritems() if k not in ['conds','preConds','postConds']}.iteritems():
                        conn[paramName] = paramValue
                if sim.cfg.createNEURONObj:
                    for paramName, paramValue in {k: v for k,v in params.iteritems() if k not in ['conds','preConds','postConds']}.iteritems():
                        try:
                            if paramName == 'weight':
                                conn['hNetcon'].weight[0] = paramValue
                            else:
                                setattr(conn['hNetcon'], paramName, paramValue)
                        except:
                            print 'Error setting %s=%s on Netcon' % (paramName, str(paramValue))


    def modifyStims (self, params):
        conditionsMet = 1
        if 'cellConds' in params:
            if conditionsMet:
                for (condKey,condVal) in params['cellConds'].iteritems():  # check if all conditions are met
                    # check if conditions met
                    if isinstance(condVal, list):
                        if self.tags.get(condKey) < condVal[0] or self.tags.get(condKey) > condVal[1]:
                            conditionsMet = 0
                            break
                    elif self.tags.get(condKey) != condVal: 
                        conditionsMet = 0
                        break

        if conditionsMet == 1:
            for stim in self.stims:
                conditionsMet = 1

                if 'conds' in params:
                    for (condKey,condVal) in params['conds'].iteritems():  # check if all conditions are met
                        # check if conditions met
                        if isinstance(condVal, list) and isinstance(condVal[0], Number):
                            if stim.get(condKey) < condVal[0] or stim.get(condKey) > condVal[1]:
                                conditionsMet = 0
                                break
                        elif isinstance(condVal, list) and isinstance(condVal[0], basestring):
                            if stim.get(condKey) not in condVal:
                                conditionsMet = 0
                                break 
                        elif stim.get(condKey) != condVal: 
                            conditionsMet = 0
                            break

                if conditionsMet:  # if all conditions are met, set values for this cell
                    if stim['type'] == 'NetStim':  # for netstims, find associated netcon
                        conn = next((conn for conn in self.conns if conn['source'] == stim['source']), None)
                    if sim.cfg.createPyStruct:
                        for paramName, paramValue in {k: v for k,v in params.iteritems() if k not in ['conds','cellConds']}.iteritems():
                            if stim['type'] == 'NetStim' and paramName in ['weight', 'delay', 'threshold']:
                                conn[paramName] = paramValue
                            else:
                                stim[paramName] = paramValue
                    if sim.cfg.createNEURONObj:
                        for paramName, paramValue in {k: v for k,v in params.iteritems() if k not in ['conds','cellConds']}.iteritems():
                            try:
                                if stim['type'] == 'NetStim':
                                    if paramName == 'weight':
                                        conn['hNetcon'].weight[0] = paramValue
                                    elif paramName in ['delay', 'threshold']:
                                        setattr(conn['hNetcon'], paramName, paramValue)
                                else:
                                    setattr(stim['h'+stim['type']], paramName, paramValue)
                            except:
                                print 'Error setting %s=%s on stim' % (paramName, str(paramValue))



    def addStim (self, params):
        if not params['sec'] or (isinstance(params['sec'], basestring) and not params['sec'] in self.secs.keys()+self.secLists.keys()):  
            if sim.cfg.verbose: print '  Warning: no valid sec specified for stim on cell gid=%d so using soma or 1st available. Existing secs: %s; params: %s'%(self.gid, self.secs.keys(),params)
            if 'soma' in self.secs:  
                params['sec'] = 'soma'  # use 'soma' if exists
            elif self.secs:  
                params['sec'] = self.secs.keys()[0]  # if no 'soma', use first sectiona available
            else:  
                if sim.cfg.verbose: print '  Error: no Section available on cell gid=%d to add stim'%(self.gid)
                return 

        sec = self.secs[params['sec']]
        
        if not 'loc' in params: params['loc'] = 0.5  # default stim location 

        if params['type'] == 'NetStim':
            if not 'start' in params: params['start'] = 0  # add default start time
            if not 'number' in params: params['number'] = 1e9  # add default number 

            connParams = {'preGid': params['type'], 
                'sec': params.get('sec'), 
                'loc': params.get('loc'), 
                'synMech': params.get('synMech'), 
                'weight': params.get('weight'),
                'delay': params.get('delay'),
                'synsPerConn': params.get('synsPerConn')}

            if 'threshold' in params: connParams['threshold'] = params.get('threshold')    
            if 'shape' in params: connParams['shape'] = params.get('shape')    
            if 'plast' in params: connParams['plast'] = params.get('plast')    

            netStimParams = {'source': params['source'],
                'type': params['type'],
                'rate': params['rate'] if 'rate' in params else 1000.0/params['interval'],
                'noise': params['noise'],
                'number': params['number'],
                'start': params['start'],
                'seed': params['seed'] if 'seed' in params else sim.cfg.seeds['stim']}
        
            self.addConn(connParams, netStimParams)
       

        elif params['type'] in ['IClamp', 'VClamp', 'SEClamp', 'AlphaSynapse']:
            stim = getattr(h, params['type'])(sec['hSec'](params['loc']))
            stimParams = {k:v for k,v in params.iteritems() if k not in ['type', 'source', 'loc', 'sec', 'label']}
            stringParams = ''
            for stimParamName, stimParamValue in stimParams.iteritems(): # set mechanism internal params
                if isinstance(stimParamValue, list):
                    if stimParamName == 'amp': 
                        for i,val in enumerate(stimParamValue):
                            stim.amp[i] = val
                    elif stimParamName == 'dur': 
                        for i,val in enumerate(stimParamValue):
                            stim.dur[i] = val
                    #setattr(stim, stimParamName._ref_[0], stimParamValue[0])
                else: 
                    setattr(stim, stimParamName, stimParamValue)
                    stringParams = stringParams + ', ' + stimParamName +'='+ str(stimParamValue)
            self.stims.append(Dict(params)) # add to python structure
            self.stims[-1]['h'+params['type']] = stim  # add stim object to dict in stims list

            if sim.cfg.verbose: print('  Added %s %s to cell gid=%d, sec=%s, loc=%.4g%s'%
                (params['source'], params['type'], self.gid, params['sec'], params['loc'], stringParams))
                
        else:
            if sim.cfg.verbose: print('Adding exotic stim (NeuroML 2 based?): %s'% params)   
            stim = getattr(h, params['type'])(sec['hSec'](params['loc']))
            stimParams = {k:v for k,v in params.iteritems() if k not in ['type', 'source', 'loc', 'sec', 'label']}
            stringParams = ''
            for stimParamName, stimParamValue in stimParams.iteritems(): # set mechanism internal params
                if isinstance(stimParamValue, list):
                    print "Can't set point process paramaters of type vector eg. VClamp.amp[3]"
                    pass
                    #setattr(stim, stimParamName._ref_[0], stimParamValue[0])
                elif 'originalFormat' in params:
                    if sim.cfg.verbose: print('   originalFormat: %s'%(params['originalFormat']))
                    if params['originalFormat']=='NeuroML2_stochastic_input':
                        rand = h.Random()
                        rand.Random123(params['stim_count'], sim.id32('%d'%(sim.cfg.seeds['stim'])))
                        rand.negexp(1)
                        stim.noiseFromRandom(rand)
                        self.stims.append(Dict())  # add new stim to Cell object
                        randContainer = self.stims[-1]
                        randContainer['NeuroML2_stochastic_input_rand'] = rand 
                else: 
                    setattr(stim, stimParamName, stimParamValue)
                    stringParams = stringParams + ', ' + stimParamName +'='+ str(stimParamValue)
            self.stims.append(params) # add to python structure
            self.stims[-1]['h'+params['type']] = stim  # add stim object to dict in stims list
            if sim.cfg.verbose: print('  Added %s %s to cell gid=%d, sec=%s, loc=%.4g%s'%
                (params['source'], params['type'], self.gid, params['sec'], params['loc'], stringParams))


    def _setConnSections (self, params):
        # if no section specified or single section specified does not exist
        if not params.get('sec') or (isinstance(params.get('sec'), basestring) and not params.get('sec') in self.secs.keys()+self.secLists.keys()):  
            if sim.cfg.verbose: print '  Warning: no valid sec specified for connection to cell gid=%d so using soma or 1st available'%(self.gid)
            if 'soma' in self.secs:  
                params['sec'] = 'soma'  # use 'soma' if exists
            elif self.secs:  
                params['sec'] = self.secs.keys()[0]  # if no 'soma', use first sectiona available
            else:  
                if sim.cfg.verbose: print '  Error: no Section available on cell gid=%d to add connection'%(self.gid)
                sec = -1  # if no Sections available print error and exit
                return sec

            secLabels = [params['sec']]

        # if sectionList or list of sections
        elif isinstance(params.get('sec'), list) or params.get('sec') in self.secLists:
            secList = list(params['sec']) if isinstance(params['sec'], list) else list(self.secLists[params['sec']])
            secLabels = []
            for i,section in enumerate(secList): 
                if section not in self.secs: # remove sections that dont exist; and corresponding weight and delay 
                    if sim.cfg.verbose: print '  Error: Section %s not available so removing from list of sections for connection to cell gid=%d'%(self.gid)
                    secList.remove(section)
                    if isinstance(params['weight'], list): params['weight'].remove(params['weight'][i])
                    if isinstance(params['delay'], list): params['delay'].remove(params['delay'][i])

                else:
                    secLabels.append(section)

        # if section is string
        else:
            secLabels = [params['sec']]
        
        return secLabels


    def _setConnWeights (self, params, netStimParams, secLabels):
        if netStimParams:
            scaleFactor = sim.net.params.scaleConnWeightNetStims
        elif sim.net.params.scaleConnWeightModels.get(self.tags['cellModel'], None) is not None:
            scaleFactor = sim.net.params.scaleConnWeightModels[self.tags['cellModel']]  # use scale factor specific for this cell model
        else:
            scaleFactor = sim.net.params.scaleConnWeight # use global scale factor

        if isinstance(params['weight'],list):
            weights = [scaleFactor * w for w in params['weight']]
        else:
            weights = [scaleFactor * params['weight']] * params['synsPerConn']
        
        return weights


    def _setConnPointP(self, params, secLabels, weightIndex):
        # Find if any point process with V not calculated in section (artifical cell, eg. Izhi2007a)
        pointp = None
        if len(secLabels)==1 and 'pointps' in self.secs[secLabels[0]]:  #  check if point processes with 'vref' (artificial cell)
            for pointpName, pointpParams in self.secs[secLabels[0]]['pointps'].iteritems():
                if 'vref' in pointpParams:  # if includes vref param means doesn't use Section v or synaptic mechanisms
                    pointp = pointpName
                    if 'synList' in pointpParams:
                        if params.get('synMech') in pointpParams['synList']: 
                            if isinstance(params.get('synMech'), list):
                                weightIndex = [pointpParams['synList'].index(synMech) for synMech in params.get('synMech')]
                            else:
                                weightIndex = pointpParams['synList'].index(params.get('synMech'))  # udpate weight index based pointp synList

        if pointp and params['synsPerConn'] > 1: # only single synapse per connection rule allowed
            if sim.cfg.verbose: print '  Error: Multiple synapses per connection rule not allowed for cells where V is not in section (cell gid=%d) '%(self.gid)
            return -1, weightIndex

        return pointp, weightIndex


    def _setConnSynMechs (self, params, secLabels):
        synsPerConn = params['synsPerConn']
        if not params.get('synMech'):
            if sim.net.params.synMechParams:  # if no synMech specified, but some synMech params defined
                synLabel = sim.net.params.synMechParams.keys()[0]  # select first synMech from net params and add syn
                params['synMech'] = synLabel
                if sim.cfg.verbose: print '  Warning: no synaptic mechanisms specified for connection to cell gid=%d so using %s '%(self.gid, synLabel)
            else: # if no synaptic mechanism specified and no synMech params available 
                if sim.cfg.verbose: print '  Error: no synaptic mechanisms available to add conn on cell gid=%d '%(self.gid)
                return -1  # if no Synapse available print error and exit

        # if desired synaptic mechanism specified in conn params
        if synsPerConn > 1:  # if more than 1 synapse
            if len(secLabels) == 1:  # if single section, create all syns there
                synMechSecs = [secLabels[0]] * synsPerConn  # same section for all 
                if isinstance(params['loc'], list):
                    if len(params['loc']) == synsPerConn: synMechLocs = params['loc']
                else:
                    synMechLocs = [i*(1.0/synsPerConn)+1.0/synsPerConn/2 for i in range(synsPerConn)]
            else:  # if multiple sections, distribute syns
                synMechSecs, synMechLocs = self._distributeSynsUniformly(secList=secLabels, numSyns=synsPerConn)
        else:
            synMechSecs = secLabels
            synMechLocs = [params['loc']]

        # add synaptic mechanism to section based on synMechSecs and synMechLocs (if already exists won't be added)
        synMechs = [self.addSynMech(synLabel=params['synMech'], secLabel=synMechSecs[i], loc=synMechLocs[i]) for i in range(synsPerConn)] 

        return synMechs, synMechSecs, synMechLocs


    def _distributeSynsUniformly (self, secList, numSyns):
        from numpy import cumsum
        if 'L' in self.secs[secList[0]]['geom']:
            secLengths = [self.secs[s]['geom']['L'] for s in secList]
        elif getattr(self.secs[secList[0]]['hSec'], 'L', None):
            secLengths = [self.secs[s]['hSec'].L for s in secList]
        else:
            secLengths = [1.0 for s in secList]
            if sim.cfg.verbose: 
                print('  Section lengths not available to distribute synapses in cell %d'%self.gid)
            
        try:
            totLength = sum(secLengths)
            cumLengths = list(cumsum(secLengths))
            absLocs = [i*(totLength/numSyns)+totLength/numSyns/2 for i in range(numSyns)]
            inds = [cumLengths.index(next(x for x in cumLengths if x >= absLoc)) for absLoc in absLocs] 
            secs = [secList[ind] for ind in inds]
            locs = [(cumLengths[ind] - absLoc) / secLengths[ind] for absLoc,ind in zip(absLocs,inds)]
        except:
            secs, locs = [],[]
        return secs, locs


    def _addConnPlasticity (self, params, sec, netcon, weightIndex):
        plasticity = params.get('plast')
        if plasticity and sim.cfg.createNEURONObj:
            try:
                plastMech = getattr(h, plasticity['mech'], None)(0, sec=sec['hSec'])  # create plasticity mechanism (eg. h.STDP)
                for plastParamName,plastParamValue in plasticity['params'].iteritems():  # add params of the plasticity mechanism
                    setattr(plastMech, plastParamName, plastParamValue)
                if plasticity['mech'] == 'STDP':  # specific implementation steps required for the STDP mech
                    precon = sim.pc.gid_connect(params['preGid'], plastMech); precon.weight[0] = 1 # Send presynaptic spikes to the STDP adjuster
                    pstcon = sim.pc.gid_connect(self.gid, plastMech); pstcon.weight[0] = -1 # Send postsynaptic spikes to the STDP adjuster
                    h.setpointer(netcon._ref_weight[weightIndex], 'synweight', plastMech) # Associate the STDP adjuster with this weight
                    #self.conns[-1]['hPlastSection'] = plastSection
                    self.conns[-1]['hSTDP']         = plastMech
                    self.conns[-1]['hSTDPprecon']   = precon
                    self.conns[-1]['hSTDPpstcon']   = pstcon
                    self.conns[-1]['STDPdata']      = {'preGid':params['preGid'], 'postGid': self.gid, 'receptor': weightIndex} # Not used; FYI only; store here just so it's all in one place
                    if sim.cfg.verbose: print('  Added STDP plasticity to synaptic mechanism')
            except:
                print 'Error: exception when adding plasticity using %s mechanism' % (plasticity['mech'])





###############################################################################
#
# POINT CELL CLASS (no compartments/sections)
#
###############################################################################

class PointCell (Cell):
    '''
    Point Neuron that doesn't use v from Section eg. NetStim, IntFire1, 
    '''
    
    def __init__ (self, gid, tags, create=True, associateGid=True):
        super(PointCell, self).__init__(gid, tags)
        self.hPointp = None
        self.params = deepcopy(self.tags.pop('params'))

        if create and sim.cfg.createNEURONObj:
            self.createNEURONObj()  # create cell 
        if associateGid: self.associateGid() # register cell for this node


    def createNEURONObj (self):
        # add point processes
        try:
            self.hPointp = getattr(h, self.tags['cellModel'])()
        except:
            print "Error creating point process mechanism %s in cell with gid %d" % (self.tags['cellModel'], self.gid)
            return 

        # if rate is list with 2 items generate random value from uniform distribution
        if 'rate' in self.params and isinstance(self.params['rate'], list) and len(self.params['rate']) == 2:
            seed(sim.id32('%d'%(sim.cfg.seeds['conn']+self.gid)))  # initialize randomizer 
            self.params['rate'] = uniform(self.params['rate'][0], self.params['rate'][1])
 
        # set pointp params - for PointCells these are stored in self.params
        params = {k: v for k,v in self.params.iteritems()}
        for paramName, paramValue in params.iteritems():
            try:
                if paramName == 'rate':
                    self.params['interval'] = 1000.0/paramValue
                    setattr(self.hPointp, 'interval', self.params['interval'])
                else:
                    setattr(self.hPointp, paramName, paramValue)
            except:
                pass

        # set number and seed for NetStims
        if self.tags['cellModel'] == 'NetStim':
            if 'number' not in self.params:
                params['number'] = 1e9 
                setattr(self.hPointp, 'number', params['number']) 
            if 'seed' not in self.params: 
                self.params['seed'] = sim.cfg.seeds['stim'] # note: random number generator initialized via noiseFromRandom() from sim.preRun()
        

        # VecStim - generate spike vector based on params
        if self.tags['cellModel'] == 'VecStim':
            # seed
            if 'seed' not in self.params: 
                self.params['seed'] = sim.cfg.seeds['stim']

            # interval
            if 'interval' in self.params:
                interval = self.params['interval'] 
            else:
                return

            # set start and noise params
            start = self.params['start'] if 'start' in self.params else 0.0
            noise = self.params['noise'] if 'noise' in self.params else 0.0

            # fixed interval of duration (1 - noise)*interval 
            fixedInterval = np.full(((1+0.5*noise)*sim.cfg.duration/interval), [(1.0-noise)*interval])  # generate 1+0.5*noise spikes to account for noise

            # randomize the first spike so on average it occurs at start + noise*interval
            # invl = (1. - noise)*mean + noise*mean*erand() - interval*(1. - noise)
            if noise == 0.0:
                vec = h.Vector(len(fixedInterval))
                spkTimes =  np.cumsum(fixedInterval) + (start - interval) 
            else:
                # plus negexp interval of mean duration noise*interval. Note that the most likely negexp interval has duration 0.
                rand = h.Random()
                rand.Random123(self.gid, sim.id32('%d'%(self.params['seed'])))
                vec = h.Vector(len(fixedInterval))
                rand.negexp(noise*interval)
                vec.setrand(rand)
                negexpInterval = np.array(vec) 
                spkTimes = np.cumsum(fixedInterval + negexpInterval) + (start - interval*(1-noise)) 

            # pulse list: start, end, rate, noise
            if 'pulses' in self.params:
                for pulse in self.params['pulses']:
                    
                    # check interval or rate params
                    if 'interval' in pulse:
                        interval = pulse['interval'] 
                    elif 'rate' in pulse:
                        interval = 1000/pulse['rate']
                    else:
                        print 'Error: Vecstim pulse missing "rate" or "interval" parameter'
                        return

                    # check start,end and noise params
                    if any([x not in pulse for x in ['start', 'end']]):  
                        print 'Error: Vecstim pulse missing "start" and/or "end" parameter'
                        return
                    else:
                        noise = pulse['noise'] if 'noise' in pulse else 0.0
                        start = pulse['start']
                        end = pulse['end']

                        # fixed interval of duration (1 - noise)*interval 
                        fixedInterval = np.full(((1+1.5*noise)*(end-start)/interval), [(1.0-noise)*interval])  # generate 1+0.5*noise spikes to account for noise

                        # randomize the first spike so on average it occurs at start + noise*interval
                        # invl = (1. - noise)*mean + noise*mean*erand() - interval*(1. - noise)
                        if noise == 0.0:
                            vec = h.Vector(len(fixedInterval))
                            pulseSpikes = np.cumsum(fixedInterval) + (start - interval)
                            pulseSpikes[pulseSpikes < start] = start
                            spkTimes = np.append(spkTimes, pulseSpikes[pulseSpikes <= end])
                        else:
                            # plus negexp interval of mean duration noise*interval. Note that the most likely negexp interval has duration 0.
                            rand = h.Random()
                            rand.Random123(self.gid, sim.id32('%d'%(self.params['seed'])))
                            vec = h.Vector(len(fixedInterval))
                            rand.negexp(noise*interval)
                            vec.setrand(rand)
                            negexpInterval = np.array(vec) 
                            pulseSpikes = np.cumsum(fixedInterval + negexpInterval) + (start - interval*(1-noise))
                            pulseSpikes[pulseSpikes < start] = start
                            spkTimes = np.append(spkTimes, pulseSpikes[pulseSpikes <= end])

            spkTimes[spkTimes < 0] = 0
            spkTimes = np.sort(spkTimes)
            spkTimes = spkTimes[spkTimes <= sim.cfg.duration]
            self.hSpkTimes = vec  # store the vector containins spikes to avoid seg fault
            self.hPointp.play(self.hSpkTimes.from_python(spkTimes))


    def associateGid (self, threshold = 10.0):
        if sim.cfg.createNEURONObj: 
            sim.pc.set_gid2node(self.gid, sim.rank) # this is the key call that assigns cell gid to a particular node
            if 'vref' in self.tags:
                nc = h.NetCon(self.hPointp.__getattribute__('_ref_'+self.tags['vref']), None)
            else:
                nc = h.NetCon(self.hPointp, None)
            nc.threshold = threshold
            sim.pc.cell(self.gid, nc, 1)  # associate a particular output stream of events
            del nc # discard netcon
        sim.net.gid2lid[self.gid] = len(sim.net.lid2gid)
        sim.net.lid2gid.append(self.gid) # index = local id; value = global id


    def _setConnWeights (self, params, netStimParams):
        if netStimParams:
            scaleFactor = sim.net.params.scaleConnWeightNetStims
        elif sim.net.params.scaleConnWeightModels.get(self.tags['cellModel'], None) is not None:
            scaleFactor = sim.net.params.scaleConnWeightModels[self.tags['cellModel']]  # use scale factor specific for this cell model
        else:
            scaleFactor = sim.net.params.scaleConnWeight # use global scale factor

        if isinstance(params['weight'],list):
            weights = [scaleFactor * w for w in params['weight']]
        else:
            weights = [scaleFactor * params['weight']] * params['synsPerConn']
        
        return weights


    def addConn (self, params, netStimParams = None):
        threshold = params.get('threshold', sim.net.params.defaultThreshold)  # if no threshold specified, set default
        if params.get('weight') is None: params['weight'] = sim.net.params.defaultWeight # if no weight, set default
        if params.get('delay') is None: params['delay'] = sim.net.params.defaultDelay # if no delay, set default
        if params.get('synsPerConn') is None: params['synsPerConn'] = 1 # if no synsPerConn, set default

        # Avoid self connections
        if params['preGid'] == self.gid:
            if sim.cfg.verbose: print '  Error: attempted to create self-connection on cell gid=%d, section=%s '%(self.gid, params.get('sec'))
            return  # if self-connection return

        # Weight
        weights = self._setConnWeights(params, netStimParams)
        weightIndex = 0  # set default weight matrix index   

        # Delays
        if isinstance(params['delay'],list):
            delays = params['delay'] 
        else:
            delays = [params['delay']] * params['synsPerConn']

        # Create connections
        for i in range(params['synsPerConn']):

            if netStimParams:
                netstim = self.addNetStim(netStimParams)

            # Python Structure
            if sim.cfg.createPyStruct:
                connParams = {k:v for k,v in params.iteritems() if k not in ['synsPerConn']} 
                connParams['weight'] = weights[i]
                connParams['delay'] = delays[i]
                if netStimParams:
                    connParams['preGid'] = 'NetStim'
                    connParams['preLabel'] = netStimParams['source']
                self.conns.append(Dict(connParams))                
            else:  # do not fill in python structure (just empty dict for NEURON obj)
                self.conns.append(Dict())

            # NEURON objects
            if sim.cfg.createNEURONObj:
                if 'vref' in self.tags:
                    postTarget = self.hPointp.__getattribute__('_ref_'+self.tags['vref']) #  local point neuron 
                else: 
                    postTarget = self.hPointp

                if netStimParams:
                    netcon = h.NetCon(netstim, postTarget) # create Netcon between netstim and target
                else:
                    netcon = sim.pc.gid_connect(params['preGid'], postTarget) # create Netcon between global gid and target
                
                netcon.weight[weightIndex] = weights[i]  # set Netcon weight
                netcon.delay = delays[i]  # set Netcon delay
                netcon.threshold = threshold # set Netcon threshold
                self.conns[-1]['hNetcon'] = netcon  # add netcon object to dict in conns list
        

                # Add time-dependent weight shaping
                if 'shape' in params and params['shape']:
                    temptimevecs = []
                    tempweightvecs = []
                    
                    # Default shape
                    pulsetype = params['shape']['pulseType'] if 'pulseType' in params['shape'] else 'square'
                    pulsewidth = params['shape']['pulseWidth'] if 'pulseWidth' in params['shape'] else 100.0
                    pulseperiod = params['shape']['pulsePeriod'] if 'pulsePeriod' in params['shape'] else 100.0
                    
                    # Determine on-off switching time pairs for stimulus, where default is always on
                    if 'switchOnOff' not in params['shape']:
                        switchtimes = [0, sim.cfg.duration]
                    else:
                        if not params['shape']['switchOnOff'] == sorted(params['shape']['switchOnOff']):
                            raise Exception('On-off switching times for a particular stimulus are not monotonic')   
                        switchtimes = deepcopy(params['shape']['switchOnOff'])
                        switchtimes.append(sim.cfg.duration)
                    
                    switchiter = iter(switchtimes)
                    switchpairs = zip(switchiter,switchiter)
                    for pair in switchpairs:
                        # Note: Cliff's makestim code is in seconds, so conversions from ms to s occurs in the args.
                        stimvecs = self._shapeStim(width=float(pulsewidth)/1000.0, isi=float(pulseperiod)/1000.0, weight=params['weight'], start=float(pair[0])/1000.0, finish=float(pair[1])/1000.0, stimshape=pulsetype)
                        temptimevecs.extend(stimvecs[0])
                        tempweightvecs.extend(stimvecs[1])
                    
                    self.conns[-1]['shapeTimeVec'] = h.Vector().from_python(temptimevecs)
                    self.conns[-1]['shapeWeightVec'] = h.Vector().from_python(tempweightvecs)
                    self.conns[-1]['shapeWeightVec'].play(netcon._ref_weight[weightIndex], self.conns[-1]['shapeTimeVec'])


            if sim.cfg.verbose: 
                sec = params['sec']
                loc = params['loc']
                preGid = netStimParams['source']+' NetStim' if netStimParams else params['preGid']
                print('  Created connection preGid=%s, postGid=%s, sec=%s, loc=%.4g, synMech=%s, weight=%.4g, delay=%.2f, threshold=%s'%
                    (preGid, self.gid, sec, loc, params['synMech'], weights[i], delays[i],params['threshold']))


    def initV (self):
        pass

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            try: 
                name(*args,**kwargs)
            except:
                print "Error: Function '%s' not yet implemented for Point Neurons" % name
        return wrapper

    # def modify (self):
    #     print 'Error: Function not yet implemented for Point Neurons'

    # def addSynMechsNEURONObj (self):
    #     print 'Error: Function not yet implemented for Point Neurons'


###############################################################################
#
# NeuroML2 CELL CLASS 
#
###############################################################################

class NML2Cell (CompartCell):
    ''' Class for NeuroML2 neuron models: No different than CompartCell '''


###############################################################################
#
# NeuroML2 SPIKE SOURCE CLASS 
#
###############################################################################

class NML2SpikeSource (CompartCell):
    ''' Class for NeuroML2 spiking neuron models: based on CompartCell,
        but the NetCon connects to the mechanism on the one section whose NET_RECEIVE
        block will emit events
    '''
        
    def associateGid (self, threshold = 10.0):
        
        if sim.cfg.createNEURONObj: 
            sim.pc.set_gid2node(self.gid, sim.rank) # this is the key call that assigns cell gid to a particular node
         
            nc = h.NetCon(self.secs['soma']['pointps'][self.tags['cellType']].hPointp, None)
                
            #### nc.threshold = threshold  # not used....
            sim.pc.cell(self.gid, nc, 1)  # associate a particular output stream of events
            del nc # discard netcon
        sim.net.gid2lid[self.gid] = len(sim.net.lid2gid)
        sim.net.lid2gid.append(self.gid) # index = local id; value = global id
        
    def initRandom(self):
        
        rand = h.Random()
        self.stims.append(Dict())  # add new stim to Cell object
        randContainer = self.stims[-1]
        randContainer['hRandom'] = rand 
        seed = sim.cfg.seeds['stim']
        randContainer['seed'] = seed 
        self.secs['soma']['pointps'][self.tags['cellType']].hPointp.noiseFromRandom(rand)  # use random number generator 
        #print("Created Random: %s with %s (%s)"%(rand,seed, sim.cfg.seeds))
    
