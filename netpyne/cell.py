"""
cell.py 

Contains Cell related classes 

Contributors: salvadordura@gmail.com
"""

from numbers import Number
from neuron import h # Import NEURON
from specs import Dict
import sim


###############################################################################
#
# GENERIC CELL CLASS
#
###############################################################################

class Cell (object):
    ''' Generic class for section-based neuron models '''
    
    def __init__ (self, gid, tags, create=True, associateGid=True):
        self.gid = gid  # global cell id 
        self.tags = tags  # dictionary of cell tags/attributes 
        self.secs = Dict()  # dict of sections
        self.secLists = Dict()  # dict of sectionLists
        self.conns = []  # list of connections
        self.stims = []  # list of stimuli

        if create: self.create()  # create cell 
        if associateGid and sim.cfg.createNEURONObj: self.associateGid() # register cell for this node

    def create (self):
        for propLabel, prop in sim.net.params.cellParams.iteritems():  # for each set of cell properties
            conditionsMet = 1
            for (condKey,condVal) in prop['conds'].iteritems():  # check if all conditions are met
                if self.tags[condKey] != condVal: 
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
            elif isinstance(condVal, list) and isinstance(condVal[0], Number):
                if self.tags.get(condKey) < condVal[0] or self.tags.get(condKey) > condVal[1]:
                    conditionsMet = 0
                    break
            elif isinstance(condVal, list) and isinstance(condVal[0], str):
                if self.tags[condKey] not in condVal:
                    conditionsMet = 0
                    break 
            elif self.tags[condKey] != condVal: 
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

        # add sectionLists
        if prop.get('secLists'):
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
            if not self.secs[sectName].get('hSec'): 
                self.secs[sectName]['hSec'] = h.Section(name=sectName)  # create h Section object
            sec = self.secs[sectName]  # pointer to section
            
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
                            seg.__getattribute__(mechName).__setattr__(mechParamName,mechParamValueFinal)

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

            # set geometry params 
            if 'geom' in sectParams:
                for geomParamName,geomParamValue in sectParams['geom'].iteritems():  
                    if not type(geomParamValue) in [list, dict]:  # skip any list or dic params
                        setattr(sec['hSec'], geomParamName, geomParamValue)

                # set 3d geometry
                if 'pt3d' in sectParams['geom']:  
                    h.pt3dclear(sec=sec['hSec'])
                    x = self.tags['x']
                    if 'ynorm' in self.tags and hasattr(sim.net.params, 'sizeY'):
                        y = self.tags['ynorm'] * sim.net.params.sizeY/1e3  # y as a func of ynorm and cortical thickness
                    else:
                        y = self.tags['y']
                    z = self.tags['z']
                    for pt3d in sectParams['geom']['pt3d']:
                        h.pt3dadd(x+pt3d[0], y+pt3d[1], z+pt3d[2], pt3d[3], sec=sec['hSec'])

        # set topology 
        for sectName,sectParams in prop['secs'].iteritems():  # iterate sects again for topology (ensures all exist)
            sec = self.secs[sectName]  # pointer to section # pointer to child sec
            if 'topol' in sectParams:
                if sectParams['topol']:
                    sec['hSec'].connect(self.secs[sectParams['topol']['parentSec']]['hSec'], sectParams['topol']['parentX'], sectParams['topol']['childX'])  # make topol connection


    # Create NEURON objs for conns and syns if included in prop (used when loading)
    def addStimsNEURONObj(self):
        # assumes python structure exists
        for stimParams in self.stims:
            if stimParams['type'] == 'NetStim':
                self.addNetStim (stimParams, stimContainer=stimParams)
       
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
            if not synMech: continue  # go to next conn
            postTarget = synMech['hSyn']

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
            netcon.threshold = conn['threshold']
            conn['hNetcon'] = netcon

            # Add plasticity 
            if conn.get('plasticity'):
                self._addConnPlasticity(conn['plasticity'], self.secs[conn['sec']], netcon, 0)



    def associateGid (self, threshold = 10.0):
        if self.secs:
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
            sim.net.gid2lid[self.gid] = len(sim.net.lid2gid)
            sim.net.lid2gid.append(self.gid) # index = local id; value = global id
            del nc # discard netcon


    def addSynMech (self, synLabel, secLabel, loc):
        synMechParams = sim.net.params.synMechParams.get(synLabel)  # get params for this synMech
        sec = self.secs.get(secLabel, None)
        if synMechParams and sec:  # if both the synMech and the section exist
            if sim.cfg.createPyStruct:
                # add synaptic mechanism to python struct
                if 'synMechs' not in sec:
                    sec['synMechs'] = []
                synMech = next((synMech for synMech in sec['synMechs'] if synMech['label']==synLabel and synMech['loc']==loc), None)
                if not synMech:  # if synMech not in section, then create
                    synMech = Dict({'label': synLabel, 'loc': loc})
                    sec['synMechs'].append(synMech)

            if sim.cfg.createNEURONObj:
                # add synaptic mechanism NEURON objectes 
                if 'synMechs' not in sec:
                    sec['synMechs'] = []
                if not synMech:  # if pointer not created in createPyStruct, then check 
                    synMech = next((synMech for synMech in sec['synMechs'] if synMech['label']==synLabel and synMech['loc']==loc), None)
                if not synMech:  # if still doesnt exist, then create
                    synMech = Dict()
                    sec['synMechs'].append(synMech)
                if not synMech.get('hSyn'):  # if synMech doesn't have NEURON obj, then create
                    synObj = getattr(h, synMechParams['mod'])
                    synMech['hSyn'] = synObj(loc, sec = sec['hSec'])  # create h Syn object (eg. h.Exp2Syn)
                    for synParamName,synParamValue in synMechParams.iteritems():  # add params of the synaptic mechanism
                        if synParamName not in ['label', 'mod']:
                            setattr(synMech['hSyn'], synParamName, synParamValue)
            return synMech


    def addConn (self, params, netStimParams = None):
        if params.get('threshold') is None: params['threshold'] = sim.net.params.defaultThreshold  # if no threshold specified, set default
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
        weights = self._setConnWeights(params, netStimParams)
        weightIndex = 0  # set default weight matrix index   

        # Delays
        if isinstance(params['delay'],list):
            delays = params['delay'] 
        else:
            delays = [params['delay']] * params['synsPerConn']

        # Check if target is point process (artificial cell) with V not in section
        pointp = self._setConnPointP(params, secLabels, weightIndex)
        if pointp == -1: return

        # Add synaptic mechanisms
        if not pointp: # check not a point process
            synMechs, synMechSecs, synMechLocs = self._setConnSynMechs(params, secLabels)
            if synMechs == -1: return

        # Create connections
        for i in range(params['synsPerConn']):

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
                self.conns.append(Dict(connParams))
                    
            else:  # do not fill in python structure (just empty dict for NEURON obj)
                self.conns.append(Dict())

            # NEURON objects
            if sim.cfg.createNEURONObj:
                if pointp:
                    sec = self.secs[secLabels[0]]
                    postTarget = sec['pointps'][pointp]['hPointp'] #  local point neuron 
                else:
                    sec = self.secs[synMechSecs[i]]
                    postTarget = synMechs[i]['hSyn'] # local synaptic mechanism

                if netStimParams:
                    netstim = self.addNetStim(netStimParams)
                    netcon = h.NetCon(netstim, postTarget) # create Netcon between netstim and target
                else:
                    netcon = sim.pc.gid_connect(params['preGid'], postTarget) # create Netcon between global gid and target
                
                netcon.weight[weightIndex] = weights[i]  # set Netcon weight
                netcon.delay = delays[i]  # set Netcon delay
                netcon.threshold = params['threshold']  # set Netcon threshold
                self.conns[-1]['hNetcon'] = netcon  # add netcon object to dict in conns list
            
            # Add plasticity
            self._addConnPlasticity(params, sec, netcon, weightIndex)

            if sim.cfg.verbose: 
                sec = params['sec'] if pointp else synMechSecs[i]
                loc = params['loc'] if pointp else synMechLocs[i]
                preGid = netStimParams['source']+' NetStim' if netStimParams else params['preGid']
                print('  Created connection preGid=%s, postGid=%s, sec=%s, loc=%.4g, synMech=%s, weight=%.4g, delay=%.1f'%
                    (preGid, self.gid, sec, loc, params['synMech'], weights[i], delays[i]))


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
                    elif isinstance(condVal, list) and isinstance(condVal[0], str):
                        if self.tags[condKey] not in condVal:
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
                    elif isinstance(condVal, list) and isinstance(condVal[0], str):
                        if self.tags[condKey] not in condVal:
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
        for stim in self.stims:
            conditionsMet = 1
            
            for (condKey,condVal) in params['conds'].iteritems():  # check if all conditions are met
                # check if conditions met
                if isinstance(condVal, list) and isinstance(condVal[0], Number):
                    if stim.get(condKey) < condVal[0] or stim.get(condKey) > condVal[1]:
                        conditionsMet = 0
                        break
                elif isinstance(condVal, list) and isinstance(condVal[0], str):
                    if self.tags[condKey] not in condVal:
                        conditionsMet = 0
                        break 
                elif stim[condKey] != stim[condKey]: 
                    conditionsMet = 0
                    break

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


    def addNetStim (self, params, stimContainer=None):
        if not stimContainer:
            self.stims.append(Dict(params.copy()))  # add new stim to Cell object
            stimContainer = self.stims[-1]
        
        rand = h.Random()
        #rand.Random123(self.gid,self.gid*2) # moved to sim.runSim() to ensure reproducibility
        #rand.negexp(1)
        stimContainer['hRandom'] = rand  # add netcon object to dict in conns list

        if isinstance(params['rate'], str):
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
            netstim.noise = params['noise']
            netstim.start = params['start']
        netstim.noiseFromRandom(rand)  # use random number generator (replace with noiseFromRandom123()!)
        netstim.number = params['number']   
            
        stimContainer['hNetStim'] = netstim  # add netstim object to dict in stim list

        if sim.cfg.verbose: print('  Created %s NetStim for cell gid=%d'% (params['source'], self.gid))

        return stimContainer['hNetStim']


    def addStim (self, params):
        if not params['sec'] or (isinstance(params['sec'], str) and not params['sec'] in self.secs.keys()+self.secLists.keys()):  
            if sim.cfg.verbose: print '  Warning: no valid sec specified for stim on cell gid=%d so using soma or 1st available'%(self.gid)
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
                'threshold': params.get('threshold'),
                'synsPerConn': params.get('synsPerConn'),
                'plasticity': params.get('plasticity')}

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



    def _setConnSections (self, params):
        # if no section specified or single section specified does not exist
        if not params.get('sec') or (isinstance(params.get('sec'), str) and not params.get('sec') in self.secs.keys()+self.secLists.keys()):  
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
            return -1

        return pointp

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
        secLengths = [self.secs[s]['hSec'].L for s in secList]
        totLength = sum(secLengths)
        cumLengths = list(cumsum(secLengths))
        absLocs = [i*(totLength/numSyns)+totLength/numSyns/2 for i in range(numSyns)]
        inds = [cumLengths.index(next(x for x in cumLengths if x >= absLoc)) for absLoc in absLocs] 
        secs = [secList[ind] for ind in inds]
        locs = [(cumLengths[ind] - absLoc) / secLengths[ind] for absLoc,ind in zip(absLocs,inds)]
        return secs, locs


    def _addConnPlasticity (self, params, sec, netcon, weightIndex):
        plasticity = params.get('plasticity')
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


    def recordTraces (self):
        # set up voltagse recording; recdict will be taken from global context
        for key, params in sim.cfg.recordTraces.iteritems():
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
                else:
                    if 'pointp' in params: # eg. soma.izh._ref_u
                        if params['pointp'] in self.secs[params['sec']]['pointps']:
                            ptr = self.secs[params['sec']]['pointps'][params['pointp']]['hPointp'].__getattribute__('_ref_'+params['var'])

                if ptr:  # if pointer has been created, then setup recording
                    sim.simData[key]['cell_'+str(self.gid)] = h.Vector(sim.cfg.duration/sim.cfg.recordStep+1).resize(0)
                    sim.simData[key]['cell_'+str(self.gid)].record(ptr, sim.cfg.recordStep)
                    if sim.cfg.verbose: print '  Recording ', key, 'from cell ', self.gid
            except:
                if sim.cfg.verbose: print '  Cannot record ', key, 'from cell ', self.gid


    def recordStimSpikes (self):
        sim.simData['stims'].update({'cell_'+str(self.gid): Dict()})
        for conn in self.conns:
            if conn['preGid'] == 'NetStim':
                stimSpikeVecs = h.Vector() # initialize vector to store 
                conn['hNetcon'].record(stimSpikeVecs)
                sim.simData['stims']['cell_'+str(self.gid)].update({conn['preLabel']: stimSpikeVecs})


    def __getstate__ (self): 
        ''' Removes non-picklable h objects so can be pickled and sent via py_alltoall'''
        odict = self.__dict__.copy() # copy the dict since we change it
        odict = sim.copyReplaceItemObj(odict, keystart='h', newval=None)  # replace h objects with None so can be pickled
        return odict



###############################################################################
#
# POINT NEURON CLASS (v not from Section)
#
###############################################################################

class PointNeuron (Cell):
    '''
    Point Neuron that doesn't use v from Section - TO DO
    '''
    pass

