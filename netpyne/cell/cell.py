"""
Module containing a generic cell class

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import


from builtins import zip
from builtins import next
from builtins import str
try:
    basestring
except NameError:
    basestring = str
from future import standard_library
standard_library.install_aliases()
from numbers import Number
from copy import deepcopy
from neuron import h # Import NEURON
from ..specs import Dict


###############################################################################
#
# GENERIC CELL CLASS
#
###############################################################################

class Cell (object):
    """
    Class for/to <short description of `netpyne.cell.cell.Cell`>

    """

    def __init__ (self, gid, tags):
        from .. import sim

        self.gid = gid  # global cell id
        self.tags = tags  # dictionary of cell tags/attributes
        self.conns = []  # list of connections
        self.stims = []  # list of stimuli

        # calculate border distance correction to avoid conn border effect
        if sim.net.params.correctBorder:
            self.calculateCorrectBorderDist()


    def recordStimSpikes (self):
        from .. import sim

        sim.simData['stims'].update({'cell_'+str(self.gid): Dict()})
        for conn in self.conns:
            if conn['preGid'] == 'NetStim':
                stimSpikeVecs = h.Vector() # initialize vector to store
                conn['hObj'].record(stimSpikeVecs)
                sim.simData['stims']['cell_'+str(self.gid)].update({conn['preLabel']: stimSpikeVecs})


    def calculateCorrectBorderDist (self):
        from .. import sim

        pop = self.tags['pop']
        popParams = sim.net.params.popParams
        coords = ['x', 'y', 'z']
        borderCorrect = [0,0,0]
        for icoord,coord in enumerate(coords):
            # calculate borders
            size = getattr(sim.net.params, 'size'+coord.upper())
            borders = [0, size]
            if coord+'borders' in sim.net.params.correctBorder:
                borders = [b*size for b in sim.net.params.correctBorder[coord+'borders']]
            elif coord+'Range' in popParams[pop]:
                borders = popParams[pop][coord+'Range']
            elif coord+'normRange' in popParams[pop]:
                borders = [popParams[pop][coord+'normRange'][0] * size,
                        popParams[pop][coord+'normRange'][1] * size]

            # calcualte distance to border
            borderDist = min([abs(self.tags[coord] - border) for border in borders])
            borderThreshold = sim.net.params.correctBorder['threshold'][icoord]
            borderCorrect[icoord] = max(0, borderThreshold - borderDist)
        self.tags['borderCorrect'] = borderCorrect

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
        npts = int(pulselength*width/timeres)
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
        fulloutput = fulloutput[int(npts/2-1):int(-npts/2)]   # Slices out where the convolved pulse train extends before and after sequence of allpts.
        fulltime = (r_[0:allpts]*timeres+start)*1e3 # Create time vector and convert to ms

        fulltime = hstack((0,fulltime,fulltime[-1]+timeres*1e3)) # Create "bookends" so always starts and finishes at zero
        fulloutput = hstack((0,fulloutput,0)) # Set weight to zero at either end of the stimulus period
        events = hstack((0,events,0)) # Ditto
        stimvecs = deepcopy([fulltime, fulloutput, events]) # Combine vectors into a matrix

        return stimvecs


    def addNetStim (self, params, stimContainer=None):
        from .. import sim

        if not stimContainer:
            self.stims.append(Dict(params.copy()))  # add new stim to Cell object
            stimContainer = self.stims[-1]

            if sim.cfg.verbose: print(('  Created %s NetStim for cell gid=%d'% (params['source'], self.gid)))

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
                        print('Error: tried to create variable rate NetStim but NSLOC mechanism not available')
                else:
                    print('Error: Unknown stimulation rate type: %s'%(h.params['rate']))
            else:
                netstim = h.NetStim()
                netstim.interval = params['rate']**-1*1e3 # inverse of the frequency and then convert from Hz^-1 to ms
                netstim.noise = params['noise'] # note: random number generator initialized via Random123() from sim.preRun()
                netstim.start = params['start']
            netstim.number = params['number']

            stimContainer['hObj'] = netstim  # add netstim object to dict in stim list

            return stimContainer['hObj']


    def recordTraces (self):
        from .. import sim

        # set up voltagse recording; recdict will be taken from global context
        for key, params in sim.cfg.recordTraces.items():
            conditionsMet = 1

            if 'conds' in params:
                for (condKey,condVal) in params['conds'].items():  # check if all conditions are met
                    # choose what to comapare to
                    if condKey in ['gid']:  # CHANGE TO GID
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
                    if 'loc' in params and params['sec'] in self.secs:
                        if 'mech' in params:  # eg. soma(0.5).hh._ref_gna
                            ptr = getattr(getattr(self.secs[params['sec']]['hObj'](params['loc']), params['mech']), '_ref_'+params['var'])
                        elif 'synMech' in params:  # eg. soma(0.5).AMPA._ref_g
                            sec = self.secs[params['sec']]
                            synMechList = [synMech for synMech in sec['synMechs'] if synMech['label']==params['synMech'] and synMech['loc']==params['loc']] # make list with this label/loc
                            ptr = None
                            if len(synMechList) > 0:
                                if 'index' in params:
                                    if params['index'] < len(synMechList):
                                        synMech = synMechList[params['index']]
                                        ptr = getattr(synMech['hObj'], '_ref_'+params['var'])
                                else:
                                    synMech = synMechList[0] # 0th one which would have been returned by next()
                                    ptr = getattr(synMech['hObj'], '_ref_' + params['var'])
                        elif 'stim' in params: # e.g. sim.net.cells[0].stims[0]['hObj'].i
                            if 'sec' in params and 'loc' in params and 'var' in params:
                                sec = self.secs[params['sec']]
                                stimList = [stim for stim in self.stims if stim['label']==params['stim'] and stim['loc']==params['loc']] # make list with this label/loc
                                ptr = None
                                if len(stimList) > 0:
                                    if 'index' in params:
                                        if params['index'] < len(stimList):
                                            stim = stimList[params['index']]
                                            ptr = getattr(stim['hObj'], '_ref_'+params['var'])
                                    else:
                                        stim = stimList[0] # 0th one which would have been returned by next()
                                        ptr = getattr(stim['hObj'], '_ref_'+params['var'])
                        else:  # eg. soma(0.5)._ref_v
                            ptr = getattr(self.secs[params['sec']]['hObj'](params['loc']), '_ref_'+params['var'])
                    elif 'synMech' in params:  # special case where want to record from multiple synMechs
                        if 'sec' in params:
                            sec = self.secs[params['sec']]
                            synMechs = [synMech for synMech in sec['synMechs'] if synMech['label']==params['synMech']]
                            ptr = [getattr(synMech['hObj'], '_ref_'+params['var']) for synMech in synMechs]
                            secLocs = [params.sec+str(synMech['loc']) for synMech in synMechs]
                        else:
                            ptr = []
                            secLocs = []
                            for secName,sec in self.secs.items():
                                synMechs = [synMech for synMech in sec['synMechs'] if synMech['label']==params['synMech']]
                                ptr.extend([getattr(synMech['hObj'], '_ref_'+params['var']) for synMech in synMechs])
                                secLocs.extend([secName+'_'+str(synMech['loc']) for synMech in synMechs])

                    else:
                        if 'pointp' in params: # eg. soma.izh._ref_u
                            if params['pointp'] in self.secs[params['sec']]['pointps']:
                                ptr = getattr(self.secs[params['sec']]['pointps'][params['pointp']]['hObj'], '_ref_'+params['var'])
                        elif 'conns' in params: # e.g. cell.conns
                            if 'mech' in params:
                                ptr = []
                                secLocs = []
                                for conn_idx,conn in enumerate(self.conns):
                                    if params['mech'] in conn.keys():
                                        if isinstance(conn[params['mech']],dict) and 'hObj' in conn[params['mech']].keys():
                                            ptr.extend([getattr(conn[params['mech']]['hObj'], '_ref_'+params['var'])])
                                        else:
                                            ptr.extend([getattr(conn[params['mech']], '_ref_'+params['var'])])
                                        secLocs.extend([params['sec']+'_conn_'+str(conn_idx)])
                            else:
                                print("Error recording conn trace, you need to specify the conn mech to record from.")

                        elif 'var' in params: # point process cell eg. cell._ref_v
                            ptr = getattr(self.hPointp, '_ref_'+params['var'])

                    if ptr:  # if pointer has been created, then setup recording
                        if isinstance(ptr, list):
                            sim.simData[key]['cell_'+str(self.gid)] = {}
                            for ptrItem,secLoc in zip(ptr, secLocs):
                                if sim.cfg.recordStep == 'adaptive':
                                    recordStep = 0.1
                                else:
                                    recordStep = sim.cfg.recordStep
                                if hasattr(sim.cfg,'use_local_dt') and sim.cfg.use_local_dt:
                                    self.secs[params['sec']]['hObj'].push()
                                    if hasattr(sim.cfg,'recordStep') and sim.cfg.recordStep == 'adaptive':
                                        sim.simData[key]['cell_time_'+str(self.gid)][secLoc] = h.Vector()
                                        sim.simData[key]['cell_'+str(self.gid)][secLoc] = h.Vector()
                                        sim.cvode.record(ptrItem, sim.simData[key]['cell_'+str(self.gid)][secLoc],
                                                         sim.simData[key]['cell_time_'+str(self.gid)][secLoc])
                                    else:
                                        sim.simData[key]['cell_'+str(self.gid)][secLoc] = h.Vector(sim.cfg.duration/recordStep+1).resize(0)
                                        sim.cvode.record(ptrItem, sim.simData[key]['cell_'+str(self.gid)][secLoc],
                                                         sim.simData['t'], 1)
                                    h.pop_section()
                                else:

                                    sim.simData[key]['cell_'+str(self.gid)][secLoc] = h.Vector(sim.cfg.duration/recordStep+1).resize(0)
                                    sim.simData[key]['cell_'+str(self.gid)][secLoc].record(ptrItem, recordStep)
                        else:
                            if hasattr(sim.cfg,'use_local_dt') and sim.cfg.use_local_dt:
                                self.secs[params['sec']]['hObj'].push()
                                sim.simData[key]['cell_'+str(self.gid)] = h.Vector()
                                if hasattr(sim.cfg,'recordStep') and sim.cfg.recordStep == 'adaptive':
                                    sim.simData[key]['cell_time_'+str(self.gid)] = h.Vector()
                                    sim.cvode.record(ptr, sim.simData[key]['cell_'+str(self.gid)],
                                                     sim.simData[key]['cell_time_'+str(self.gid)])
                                else:
                                    sim.cvode.record(ptr, sim.simData[key]['cell_'+str(self.gid)],
                                                     sim.simData['t'], 1)
                                h.pop_section()
                            else:
                                sim.simData[key]['cell_'+str(self.gid)] = h.Vector(sim.cfg.duration/sim.cfg.recordStep+1).resize(0)
                                sim.simData[key]['cell_'+str(self.gid)].record(ptr, sim.cfg.recordStep)
                        if sim.cfg.verbose:
                            print('  Recording ', key, 'from cell ', self.gid, ' with parameters: ',str(params))
                            print(sim.simData[key]['cell_'+str(self.gid)])
                except:
                    if sim.cfg.verbose: print('  Cannot record ', key, 'from cell ', self.gid)
            else:
                if sim.cfg.verbose: print('  Conditions preclude recording ', key, ' from cell ', self.gid)
        #else:
        #    if sim.cfg.verbose: print '  NOT recording ', key, 'from cell ', self.gid, ' with parameters: ',str(params)



    def __getstate__ (self):
        """
        Removes non-picklable h objects so can be pickled and sent via py_alltoall
        """

        from .. import sim

        odict = self.__dict__.copy() # copy the dict since we change it
        odict = sim.copyRemoveItemObj(odict, keystart='h', exclude_list=['hebbwt']) #, newval=None)  # replace h objects with None so can be pickled
        odict = sim.copyReplaceItemObj(odict, keystart='NeuroML', newval='---Removed_NeuroML_obj---')  # replace NeuroML objects with str so can be pickled
        return odict
