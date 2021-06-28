"""
Module containing a point cell class

cell/pointCell.py 

Contains pointCell class 

Contributors: salvadordura@gmail.com, samnemo@gmail.com
"""
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from builtins import super
from builtins import zip
from builtins import range

from future import standard_library
standard_library.install_aliases()
from copy import deepcopy
from neuron import h # Import NEURON
import numpy as np
from .cell import Cell
from ..specs import Dict


###############################################################################
#
# POINT CELL CLASS (no compartments/sections)
#
###############################################################################

class PointCell (Cell):
    """
    Class for/to <short description of `netpyne.cell.pointCell.PointCell`>


    Point Neuron that doesn't use v from Section eg. NetStim, IntFire1, 
    """
    

    def __init__ (self, gid, tags, create=True, associateGid=True):
        from .. import sim

        # enable defining pointCell properties directly in cellParams
        exclude = ['cellType']

        #import IPython; IPython.embed()

        if 'cellType' in tags and tags['cellType'] in sim.net.params.cellParams:
            tags.update({k: v for k,v in sim.net.params.cellParams[tags['cellType']].items() if k not in exclude})

        # call parent calls (Cell) constructor to set gid and tags
        super(PointCell, self).__init__(gid, tags)
        self.hPointp = None
        if 'params' in self.tags:
            dictParams = sim.replaceDictODict(self.tags.pop('params'))
            self.params = deepcopy(dictParams)

        if create and sim.cfg.createNEURONObj:
            self.createNEURONObj()  # create cell
        if associateGid: self.associateGid() # register cell for this node

    def __str__ (self):
        try:
            gid, cmo = self.gid, self.tags['cellModel'] # only use if these exist
            return 'pointCell_%s_%d'%(cmo, gid)
        except: return 'pointCell%d'%self.gid

    def __repr__ (self):
        return self.__str__()

    def createNEURONObj (self):
        from .. import sim

        # add point processes
        try:
            self.hPointp = getattr(h, self.tags['cellModel'])()
        except:
            print("Error creating point process mechanism %s in cell with gid %d" % (self.tags['cellModel'], self.gid))
            return

        # if rate is list with 2 items generate random value from uniform
        if 'rate' in self.params and isinstance(self.params['rate'], list) and len(self.params['rate']) == 2:
            rand = h.Random()
            rand.Random123(sim.hashStr('point_rate'), self.gid, sim.cfg.seeds['stim']) # initialize randomizer
            self.params['rate'] = rand.uniform(self.params['rate'][0], self.params['rate'][1])


        # if rates is list with 2 items generate time-depenedent rates using vector.play()
        if 'rates' in self.params and isinstance(self.params['rates'], list) and len(self.params['rates']) == 2:
                interval = [1000.0/r if r>0.0 else 1e10 for r in self.params['rates'][0]]
                self.hVectorIntervals = h.Vector(interval)
                self.hVectorTimes = h.Vector(self.params['rates'][1])
                self.hVectorIntervals.play(self.hPointp._ref_interval, self.hVectorTimes)  # set continuous = True?

        # set pointp params - for PointCells these are stored in self.params
        params = {k: v for k,v in self.params.items()}
        for paramName, paramValue in params.items():
            try:
                if paramName == 'rate':
                    self.params['interval'] = 1000.0 / paramValue
                    setattr(self.hPointp, 'interval', self.params['interval'])
                else:
                    setattr(self.hPointp, paramName, paramValue)
            except:
                pass

        # add random num generator, and set number and seed for NetStims
        if self.tags['cellModel'] == 'NetStim':
            if sim.cfg.verbose: print("Creating a NetStim pointcell")
            rand = h.Random()
            self.hRandom = rand
            if 'number' not in self.params:
                params['number'] = 1e9
                setattr(self.hPointp, 'number', params['number'])
            if 'seed' not in self.params:
                self.params['seed'] = sim.cfg.seeds['stim'] # note: random number generator initialized from sim.preRun()


        # VecStim - generate spike vector based on params
        if self.tags['cellModel'] == 'VecStim':
            # seed
            if 'seed' not in self.params:
                self.params['seed'] = sim.cfg.seeds['stim']

            # convert rate to interval
            if 'rate' in self.params:
                self.params['interval'] = 1000.0/self.params['rate']

            # if interval
            if 'interval' in self.params:
                # set interval, start and noise params
                interval = self.params['interval']
                start = self.params['start'] if 'start' in self.params else 0.0
                noise = self.params['noise'] if 'noise' in self.params else 0.0

                maxReproducibleSpks = 1e4  # num of rand spikes generated; only a subset is used; ensures reproducibility

                # fixed interval of duration (1 - noise)*interval
                fixedInterval = np.full(int(((1+1.5*noise)*sim.cfg.duration/interval)), [(1.0-noise)*interval])  # generate 1+1.5*noise spikes to account for noise
                numSpks = len(fixedInterval)

                # randomize the first spike so on average it occurs at start + noise*interval
                # invl = (1. - noise)*mean + noise*mean*erand() - interval*(1. - noise)
                if noise == 0.0:
                    vec = h.Vector(len(fixedInterval))
                    spkTimes =  np.cumsum(fixedInterval) + (start - interval)
                else:
                    # plus negexp interval of mean duration noise*interval. Note that the most likely negexp interval has duration 0.
                    rand = h.Random()
                    rand.Random123(sim.hashStr('vecstim_spkt'), self.gid, self.params['seed'])

                    # Method 1: vec length depends on duration -- not reproducible
                    # vec = h.Vector(numSpks)
                    # rand.negexp(noise*interval)
                    # vec.setrand(rand)
                    # negexpInterval= np.array(vec)
                    # #print negexpInterval
                    # spkTimes = np.cumsum(fixedInterval + negexpInterval) + (start - interval*(1-noise))

                    if numSpks < 100:
                        # Method 2: vec length=1, slower but reproducible
                        vec = h.Vector(1)
                        rand.negexp(noise*interval)
                        negexpInterval = []
                        for i in range(numSpks):
                            vec.setrand(rand)
                            negexpInterval.append(vec.x[0])  # = np.array(vec)[0:len(fixedInterval)]
                        spkTimes = np.cumsum(fixedInterval + np.array(negexpInterval)) + (start - interval*(1-noise))

                    elif numSpks < maxReproducibleSpks:
                        # Method 3: vec length=maxReproducibleSpks, then select subset; slower but reproducible
                        vec = h.Vector(maxReproducibleSpks)
                        rand.negexp(noise*interval)
                        vec.setrand(rand)
                        negexpInterval = np.array(vec.c(0,len(fixedInterval)-1))
                        spkTimes = np.cumsum(fixedInterval + negexpInterval) + (start - interval*(1-noise))

                    else:
                        print('\nError: exceeded the maximum number of VecStim spikes per cell (%d > %d)' % (numSpks, maxReproducibleSpks))
                        return

            # spikePattern
            elif 'spikePattern' in self.params:
                patternType = self.params['spikePattern'].get('type', None)
                rand = h.Random()

                if self.params['spikePattern'].get('sync', False):
                    rand.Random123(sim.hashStr('vecstim_spikePattern'), self.params['seed'])
                else:
                    rand.Random123(sim.hashStr('vecstim_spikePattern'), self.gid, self.params['seed'])

                if patternType == 'rhythmic':
                    from .inputs import createRhythmicPattern
                    spkTimes = createRhythmicPattern(self.params['spikePattern'], rand)
                elif patternType == 'evoked':
                    from .inputs import createEvokedPattern
                    spkTimes = createEvokedPattern(self.params['spikePattern'], rand)
                elif patternType == 'poisson':
                    from .inputs import createPoissonPattern
                    if self.params['spikePattern']['stop'] == -1:
                        self.params['spikePattern']['stop'] = sim.cfg.duration
                    spkTimes = createPoissonPattern(self.params['spikePattern'], rand)
                elif patternType == 'gauss':
                    from .inputs import createGaussPattern
                    spkTimes = createGaussPattern(self.params['spikePattern'], rand)
                else:
                    print('\nError: invalid spikePattern type %s' % (patternType))
                    return

                vec = h.Vector(len(spkTimes))

            # if spkTimess
            elif 'spkTimes' in self.params:
                spkTimes = self.params['spkTimes']
                if type(spkTimes) not in (list,tuple,np.array):
                    print('\nError: VecStim "spkTimes" needs to be a list, tuple or numpy array')
                    return
                spkTimes = np.array(spkTimes)
                vec = h.Vector(len(spkTimes))

            # if spkTimess
            elif 'spkTimes' in self.tags:
                spkTimes = self.tags['spkTimes']
                if type(spkTimes) not in (list,tuple,np.array):
                    print('\nError: VecStim "spkTimes" needs to be a list, tuple or numpy array')
                    return
                spkTimes = np.array(spkTimes)
                vec = h.Vector(len(spkTimes))

            # missing params
            else:
                print('\nError: VecStim requires interval, rate or spkTimes')
                return

            # pulse list: start, end, rate, noise
            if 'pulses' in self.params:
                for ipulse, pulse in enumerate(self.params['pulses']):

                    # if rate is list with 2 items generate random value from uniform
                    if 'rate' in pulse and isinstance(pulse['rate'], list) and len(pulse['rate']) == 2:
                        rand = h.Random()
                        rand.Random123(sim.hashStr('point_rate_pulse'+str(ipulse)), self.gid, sim.cfg.seeds['stim']) # initialize randomizer
                        pulse['rate'] = rand.uniform(pulse['rate'][0], pulse['rate'][1])

                    # check interval or rate params
                    if 'interval' in pulse:
                        interval = pulse['interval']
                    elif 'rate' in pulse:
                        interval = 1000.0/pulse['rate']
                    else:
                        print('Error: Vecstim pulse missing "rate" or "interval" parameter')
                        return

                    # check start,end and noise params
                    if any([x not in pulse for x in ['start', 'end']]):
                        print('Error: Vecstim pulse missing "start" and/or "end" parameter')
                        return
                    else:
                        noise = pulse['noise'] if 'noise' in pulse else 0.0
                        start = pulse['start']
                        end = pulse['end']

                        # fixed interval of duration (1 - noise)*interval
                        fixedInterval = np.full(int(((1+1.5*noise)*(end-start)/interval)), [(1.0-noise)*interval])  # generate 1+0.5*noise spikes to account for noise
                        numSpks = len(fixedInterval)

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
                            rand.Random123(ipulse, self.gid, self.params['seed'])

                            # Method 1: vec length depends on duration -- not reproducible
                            # vec = h.Vector(len(fixedInterval))
                            # rand.negexp(noise*interval)
                            # vec.setrand(rand)
                            # negexpInterval = np.array(vec)
                            # pulseSpikes = np.cumsum(fixedInterval + negexpInterval) + (start - interval*(1-noise))

                            # Method 2: vec length=1, slower but reproducible
                            vec = h.Vector(1)
                            rand.negexp(noise*interval)
                            negexpInterval = []
                            for i in range(numSpks):
                                vec.setrand(rand)
                                negexpInterval.append(vec.x[0])  # = np.array(vec)[0:len(fixedInterval)]
                            pulseSpikes = np.cumsum(fixedInterval + np.array(negexpInterval)) + (start - interval*(1-noise))

                            pulseSpikes[pulseSpikes < start] = start
                            spkTimes = np.append(spkTimes, pulseSpikes[pulseSpikes <= end])

            spkTimes[spkTimes < 0] = 0
            spkTimes = np.sort(spkTimes)
            spkTimes = spkTimes[spkTimes <= sim.cfg.duration]
            self.hSpkTimes = vec  # store the vector containins spikes to avoid seg fault
            self.hPointp.play(self.hSpkTimes.from_python(spkTimes))


    def associateGid (self, threshold = None):
        from .. import sim

        if sim.cfg.createNEURONObj:
            sim.pc.set_gid2node(self.gid, sim.rank) # this is the key call that assigns cell gid to a particular node
            if 'vref' in self.tags:
                nc = h.NetCon(getattr(self.hPointp, '_ref_'+self.tags['vref']), None)
            else:
                nc = h.NetCon(self.hPointp, None)
            threshold = threshold if threshold is not None else sim.net.params.defaultThreshold
            nc.threshold = threshold
            sim.pc.cell(self.gid, nc, 1)  # associate a particular output stream of events
            del nc # discard netcon
        sim.net.gid2lid[self.gid] = len(sim.net.gid2lid)


    def _setConnWeights (self, params, netStimParams):
        from .. import sim

        if netStimParams:
            scaleFactor = sim.net.params.scaleConnWeightNetStims
        elif isinstance(sim.net.params.scaleConnWeightModels, dict) and sim.net.params.scaleConnWeightModels.get(self.tags['cellModel'], None) is not None:
            scaleFactor = sim.net.params.scaleConnWeightModels[self.tags['cellModel']]  # use scale factor specific for this cell model
        else:
            scaleFactor = sim.net.params.scaleConnWeight # use global scale factor

        if isinstance(params['weight'],list):
            weights = [scaleFactor * w for w in params['weight']]
        else:
            weights = [scaleFactor * params['weight']] * params['synsPerConn']

        return weights


    def addConn (self, params, netStimParams = None):
        from .. import sim

        #threshold = params.get('threshold', sim.net.params.defaultThreshold)  # if no threshold specified, set default
        if params.get('weight') is None: params['weight'] = sim.net.params.defaultWeight # if no weight, set default
        if params.get('delay') is None: params['delay'] = sim.net.params.defaultDelay # if no delay, set default
        if params.get('synsPerConn') is None: params['synsPerConn'] = 1 # if no synsPerConn, set default

        # Avoid self connections
        if params['preGid'] == self.gid:
            if sim.cfg.verbose: print('  Error: attempted to create self-connection on cell gid=%d, section=%s '%(self.gid, params.get('sec')))
            return  # if self-connection return

        # Weight
        weights = self._setConnWeights(params, netStimParams)

        if params.get('weightIndex') is None: params['weightIndex'] = 0 # set default weight matrix index   
        weightIndex = params.get('weightIndex') # note that loop below will overwrite the weights value in weights[i]


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
                connParams = {k:v for k,v in params.items() if k not in ['synsPerConn']}
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
                    postTarget = getattr(self.hPointp, '_ref_'+self.tags['vref']) #  local point neuron
                else:
                    postTarget = self.hPointp

                if netStimParams:
                    netcon = h.NetCon(netstim, postTarget) # create Netcon between netstim and target
                else:
                    netcon = sim.pc.gid_connect(params['preGid'], postTarget) # create Netcon between global gid and target

                
                netcon.weight[weightIndex] = weights[i]  # set Netcon weight - note that this gets over-written in loop
                netcon.delay = delays[i]  # set Netcon delay
                #netcon.threshold = threshold # set Netcon threshold
                self.conns[-1]['hObj'] = netcon  # add netcon object to dict in conns list

                # Add plasticity 
                if self.conns[-1].get('plast'):
                     self.conns[-1]['dummySec'] = {'hObj':h.Section(name='dummySec',cell=self)}
                     self._addConnPlasticity(self.conns[-1], self.conns[-1]['dummySec'], netcon, weightIndex)

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
                    switchpairs = list(zip(switchiter,switchiter))
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
                try:
                    print(('  Created connection preGid=%s, postGid=%s, sec=%s, loc=%.4g, synMech=%s, weight=%.4g, delay=%.2f'
                        % (preGid, self.gid, sec, loc, params['synMech'], weights[i], delays[i])))
                except:
                    print(('  Created connection preGid=%s' % (preGid)))


    def initV (self):
        pass

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            from .. import sim
            try:
                name(*args,**kwargs)
            except:
                if sim.cfg.verbose:
                    print("Error: Function '%s' not yet implemented for Point Neurons" % name)
        return wrapper

    def _addConnPlasticity (self, params, sec, netcon, weightIndex):
        from .. import sim
        plasticity = params.get('plast')
        if plasticity and sim.cfg.createNEURONObj:
            try:
                plastMech = getattr(h, plasticity['mech'], None)(0, sec=sec['hObj'])  # create plasticity mechanism (eg. h.STDP)
                for plastParamName,plastParamValue in plasticity['params'].items():  # add params of the plasticity mechanism
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
                print('Error: exception when adding plasticity using %s mechanism' % (plasticity['mech']))

      

    # def modify (self):
    #     print 'Error: Function not yet implemented for Point Neurons'

    # def addSynMechsNEURONObj (self):
    #     print 'Error: Function not yet implemented for Point Neurons'
