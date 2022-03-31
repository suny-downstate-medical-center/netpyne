"""
Module containing a compartmental cell class

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from builtins import super
from builtins import next
from builtins import zip
from builtins import range

from builtins import round
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
import numpy as np
from math import sin, cos
from .cell import Cell
from ..specs import Dict


###############################################################################
#
# COMPARTMENTAL CELL CLASS
#
###############################################################################


class CompartCell (Cell):
    """
    Class for/to <short description of `netpyne.cell.compartCell.CompartCell`>

    """

    def __init__ (self, gid, tags, create=True, associateGid=True):
        super(CompartCell, self).__init__(gid, tags)
        self.secs = Dict()  # dict of sections
        self.secLists = Dict()  # dict of sectionLists

        if create: self.create()  # create cell
        if associateGid: self.associateGid()  # register cell for this node

    def __str__ (self):
        try:
            gid, cty, cmo = self.gid, self.tags['cellType'], self.tags['cellModel'] # only use if these exist
            return 'compartCell_%s_%s_%d'%(cty, cmo, gid)
        except: return 'compartCell%d'%self.gid

    def __repr__ (self):
        return self.__str__()

    def create (self):
        from .. import sim

        # generate random rotation angle for each cell
        if sim.net.params.rotateCellsRandomly:
            if isinstance(sim.net.params.rotateCellsRandomly, list):
                [rotMin, rotMax] = sim.net.params.rotateCellsRandomly
            else:
                [rotMin, rotMax] = 0, 6.2832
            rand = h.Random()
            rand.Random123(self.gid)
            self.randRotationAngle = rand.uniform(0, 6.2832)  # 0 to 2pi

        # apply cell rules
        for propLabel, prop in sim.net.params.cellParams.items():  # for each set of cell properties
            conditionsMet = 1
            if 'conds' in prop and len(prop['conds']) > 0:
                for (condKey,condVal) in prop['conds'].items():  # check if all conditions are met
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

            elif self.tags['cellType'] != propLabel:  # simplified method for defining cell params (when no 'conds')
                conditionsMet = False

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
        from .. import sim

        conditionsMet = 1
        for (condKey,condVal) in prop['conds'].items():  # check if all conditions are met
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
        from .. import sim

        # set params for all sections
        for sectName,sectParams in prop['secs'].items():
            # create section
            if sectName not in self.secs:
                self.secs[sectName] = Dict()  # create section dict
            sec = self.secs[sectName]  # pointer to section

            # add distributed mechanisms
            if 'mechs' in sectParams:
                for mechName,mechParams in sectParams['mechs'].items():
                    if 'mechs' not in sec:
                        sec['mechs'] = Dict()
                    if mechName not in sec['mechs']:
                        sec['mechs'][mechName] = Dict()
                    for mechParamName,mechParamValue in mechParams.items():  # add params of the mechanism
                        sec['mechs'][mechName][mechParamName] = mechParamValue

            # add ion info
            if 'ions' in sectParams:
                for ionName,ionParams in sectParams['ions'].items():
                    if 'ions' not in sec:
                        sec['ions'] = Dict()
                    if ionName not in sec['ions']:
                        sec['ions'][ionName] = Dict()
                    for ionParamName,ionParamValue in ionParams.items():  # add params of the ion
                        sec['ions'][ionName][ionParamName] = ionParamValue


            # add synMechs
            if 'synMechs' in sectParams:
                for synMech in sectParams['synMechs']:
                    if 'label' in synMech and 'loc' in synMech:
                        self.addSynMech(synLabel=synMech['label'], secLabel=sectName, loc=synMech['loc'])

            # add point processes
            if 'pointps' in sectParams:
                for pointpName,pointpParams in sectParams['pointps'].items():
                    #if self.tags['cellModel'] == pointpName: # only required if want to allow setting various cell models in same rule
                    if 'pointps' not in sec:
                        sec['pointps'] = Dict()
                    if pointpName not in sec['pointps']:
                        sec['pointps'][pointpName] = Dict()
                    for pointpParamName,pointpParamValue in pointpParams.items():  # add params of the mechanism
                        if pointpParamValue == 'gid':
                            pointpParamValue = self.gid
                        sec['pointps'][pointpName][pointpParamName] = pointpParamValue


            # add geometry params
            if 'geom' in sectParams:
                for geomParamName,geomParamValue in sectParams['geom'].items():
                    if 'geom' not in sec:
                        sec['geom'] = Dict()
                    if not type(geomParamValue) in [list, dict]:  # skip any list or dic params
                        sec['geom'][geomParamName] = geomParamValue

                # add 3d geometry
                if 'pt3d' in sectParams['geom']:
                    if 'pt3d' not in sec['geom']:
                        sec['geom']['pt3d'] = []
                    for ipt, pt3d in enumerate(sectParams['geom']['pt3d']):
                        if sim.net.params.rotateCellsRandomly == True:
                            """Rotate the cell about the Z axis."""
                            x = pt3d[0]
                            z = pt3d[2]
                            c = cos(self.randRotationAngle)
                            s = sin(self.randRotationAngle)
                            pt3d = (x * c - z * s, pt3d[1], x * s + z * c, pt3d[3])
                            sectParams['geom']['pt3d'][ipt] = pt3d

                        sec['geom']['pt3d'].append(pt3d)

            # add topolopgy params
            if 'topol' in sectParams:
                if 'topol' not in sec:
                    sec['topol'] = Dict()
                for topolParamName,topolParamValue in sectParams['topol'].items():
                    sec['topol'][topolParamName] = topolParamValue

            # add other params
            if 'spikeGenLoc' in sectParams:
                sec['spikeGenLoc'] = sectParams['spikeGenLoc']

            if 'vinit' in sectParams:
                sec['vinit'] = sectParams['vinit']

            if 'weightNorm' in sectParams:
                sec['weightNorm'] = sectParams['weightNorm']

            if 'threshold' in sectParams:
                sec['threshold'] = sectParams['threshold']

        # add sectionLists
        if 'secLists' in prop:
            self.secLists.update(prop['secLists'])  # diction of section lists


    def initV (self):
        for sec in list(self.secs.values()):
            if 'vinit' in sec:
                sec['hObj'].v = sec['vinit']


    # Create dictionary of section names with entries to scale section lengths to length along z-axis
    def __dipoleGetSecLength (self, secName):
        L = 1
        # basal_2 and basal_3 at 45 degree angle to z-axis.
        if 'basal_2' in secName:
            L = np.sqrt(2) / 2.
        elif 'basal_3' in secName:
            L = np.sqrt(2) / 2.
        # apical_oblique at 90 perpendicular to z-axis
        elif 'apical_oblique' in secName:
            L = 0.
        # All basalar dendrites extend along negative z-axis
        if 'basal' in secName:
            L = -L
        return L



    # insert dipole in section
    def __dipoleInsert(self, secName, sec):

        # insert dipole mech (dipole.mod)
        try:
            sec['hObj'].insert('dipole')
        except:
            print('Error inserting dipole mechanism')
            return -1

        # insert Dipole point process (dipole_pp.mod)
        try:
            sec['hDipole_pp'] = h.Dipole(1.0, sec = sec['hObj'])
        except:
            print('Error inserting Dipole point process')
            return -1
        dpp = sec['hDipole_pp']

        # assign internal resistance values to dipole point process (dpp)
        dpp.ri = h.ri(1, sec=sec['hObj'])

        # sets pointers in dipole mod file to the correct locations -- h.setpointer(ref, ptr, obj)
        h.setpointer(sec['hObj'](0.99)._ref_v, 'pv', dpp)
        h.setpointer(self.dipole['hRef']._ref_x[0], 'Qtotal', dpp)


        # gives INTERNAL segments of the section, non-endpoints
        # creating this because need multiple values simultaneously
        loc = np.array([seg.x for seg in sec['hObj']])

        # these are the positions, including 0 but not L
        pos = np.array([seg.x for seg in sec['hObj'].allseg()])

        # diff in yvals, scaled against the pos np.array. y_long as in longitudinal
        y_scale = (self.__dipoleGetSecLength(secName) * sec['hObj'].L) * pos

        # y_long = (h.y3d(1, sec=sect) - h.y3d(0, sec=sect)) * pos
        # diff values calculate length between successive section points
        y_diff = np.diff(y_scale)

        for i in range(len(loc)):
            # assign the ri value to the dipole
            sec['hObj'](loc[i]).dipole.ri = h.ri(loc[i], sec=sec['hObj'])

            # range variable 'dipole'
            # set pointers to previous segment's voltage, with boundary condition
            if i > 0:
                h.setpointer(sec['hObj'](loc[i-1])._ref_v, 'pv', sec['hObj'](loc[i]).dipole)
            else:
                h.setpointer(sec['hObj'](0)._ref_v, 'pv', sec['hObj'](loc[i]).dipole)

            # set aggregate pointers
            h.setpointer(dpp._ref_Qsum, 'Qsum', sec['hObj'](loc[i]).dipole)
            h.setpointer(self.dipole['hRef']._ref_x[0], 'Qtotal', sec['hObj'](loc[i]).dipole)

            # add ztan values
            sec['hObj'](loc[i]).dipole.ztan = y_diff[i]

        # set the pp dipole's ztan value to the last value from y_diff
        dpp.ztan = y_diff[-1]



    def createNEURONObj (self, prop):
        from .. import sim

        excludeMechs = ['dipole']  # dipole is special case
        mechInsertError = False  # flag to print error inserting mechanisms

        # set params for all sections
        for sectName,sectParams in prop['secs'].items():
            # create section
            if sectName not in self.secs:
                self.secs[sectName] = Dict()  # create sect dict if doesn't exist
            if 'hObj' not in self.secs[sectName] or self.secs[sectName]['hObj'] in [None, {}, []]:
                self.secs[sectName]['hObj'] = h.Section(name=sectName, cell=self)  # create h Section object
            sec = self.secs[sectName]  # pointer to section

            # set geometry params
            if 'geom' in sectParams:
                for geomParamName,geomParamValue in sectParams['geom'].items():
                    if not type(geomParamValue) in [list, dict]:  # skip any list or dic params
                        setattr(sec['hObj'], geomParamName, geomParamValue)

                # set 3d geometry
                if 'pt3d' in sectParams['geom']:
                    h.pt3dclear(sec=sec['hObj'])
                    if sim.cfg.pt3dRelativeToCellLocation:
                        x = self.tags['x']
                        y = -self.tags['y'] if sim.cfg.invertedYCoord else self.tags['y'] # Neuron y-axis positive = upwards, so assume pia=0 and cortical depth = neg
                        z = self.tags['z']
                    else:
                        x = y = z = 0
                    for pt3d in sectParams['geom']['pt3d']:
                        h.pt3dadd(x+pt3d[0], y+pt3d[1], z+pt3d[2], pt3d[3], sec=sec['hObj'])

            # add distributed mechanisms
            if 'mechs' in sectParams:
                mechsInclude = {k: v for k,v in sectParams['mechs'].items() if k not in excludeMechs}
                for mechName, mechParams in mechsInclude.items():
                    if mechName not in sec['mechs']:
                        sec['mechs'][mechName] = Dict()
                    try:
                        sec['hObj'].insert(mechName)
                    except:
                        mechInsertError = True
                        if sim.cfg.verbose:
                            print('# Error inserting %s mechanims in %s section! (check mod files are compiled)'%(mechName, sectName))
                        continue
                    for mechParamName,mechParamValue in mechParams.items():  # add params of the mechanism
                        mechParamValueFinal = mechParamValue
                        for iseg,seg in enumerate(sec['hObj']):  # set mech params for each segment
                            if type(mechParamValue) in [list]:
                                if len(mechParamValue) == 1:
                                    mechParamValueFinal = mechParamValue[0]
                                else:
                                    mechParamValueFinal = mechParamValue[iseg]
                            if mechParamValueFinal is not None:  # avoid setting None values
                                setattr(getattr(seg, mechName), mechParamName,mechParamValueFinal)

            # add ions
            if 'ions' in sectParams:
                for ionName,ionParams in sectParams['ions'].items():
                    if ionName not in sec['ions']:
                        sec['ions'][ionName] = Dict()
                    try:
                        sec['hObj'].insert(ionName+'_ion')    # insert mechanism
                    except:
                        mechInsertError = True
                        if sim.cfg.verbose:
                            print('# Error inserting %s ion in %s section!'%(ionName, sectName))
                        continue
                    for ionParamName,ionParamValue in ionParams.items():  # add params of the mechanism
                        ionParamValueFinal = ionParamValue
                        for iseg,seg in enumerate(sec['hObj']):  # set ion params for each segment
                            if type(ionParamValue) in [list]:
                                ionParamValueFinal = ionParamValue[iseg]
                            if ionParamName == 'e':
                                setattr(seg, ionParamName+ionName, ionParamValueFinal)
                            elif ionParamName == 'o':
                                setattr(seg, '%so'%ionName, ionParamValueFinal)
                                h('%so0_%s_ion = %s'%(ionName,ionName,ionParamValueFinal))  # e.g. cao0_ca_ion, the default initial value
                            elif ionParamName == 'i':
                                setattr(seg, '%si'%ionName, ionParamValueFinal)
                                h('%si0_%s_ion = %s'%(ionName,ionName,ionParamValueFinal))  # e.g. cai0_ca_ion, the default initial value

                    #if sim.cfg.verbose: print("Updated ion: %s in %s, e: %s, o: %s, i: %s" % \
                    #         (ionName, sectName, seg.__getattribute__('e'+ionName), seg.__getattribute__(ionName+'o'), seg.__getattribute__(ionName+'i')))

            # add synMechs (only used when loading because python synMechs already exist)
            if 'synMechs' in sectParams:
                for synMech in sectParams['synMechs']:
                    if 'label' in synMech and 'loc' in synMech:
                        synMechParams = sim.net.params.synMechParams.get(synMech['label'])  # get params for this synMech
                        self.addSynMechNEURONObj(synMech, synMechParams, sec, synMech['loc'])

            # add point processes
            if 'pointps' in sectParams:
                for pointpName,pointpParams in sectParams['pointps'].items():
                    #if self.tags['cellModel'] == pointpParams:  # only required if want to allow setting various cell models in same rule
                    if pointpName not in sec['pointps']:
                        sec['pointps'][pointpName] = Dict()
                    pointpObj = getattr(h, pointpParams['mod'])
                    loc = pointpParams['loc'] if 'loc' in pointpParams else 0.5  # set location
                    sec['pointps'][pointpName]['hObj'] = pointpObj(loc, sec = sec['hObj'])  # create h Pointp object (eg. h.Izhi2007b)
                    for pointpParamName,pointpParamValue in pointpParams.items():  # add params of the point process
                        if pointpParamValue == 'gid':
                            pointpParamValue = self.gid
                        if pointpParamName not in ['mod', 'loc', 'vref', 'synList'] and not pointpParamName.startswith('_'):
                            setattr(sec['pointps'][pointpName]['hObj'], pointpParamName, pointpParamValue)
                    if 'params' in self.tags.keys(): # modify cell specific params
                      for pointpParamName,pointpParamValue in self.tags['params'].items():
                        setattr(sec['pointps'][pointpName]['hObj'], pointpParamName, pointpParamValue)

        # set topology
        for sectName,sectParams in prop['secs'].items():  # iterate sects again for topology (ensures all exist)
            sec = self.secs[sectName]  # pointer to section # pointer to child sec
            if 'topol' in sectParams:
                if sectParams['topol']:
                    sec['hObj'].connect(self.secs[sectParams['topol']['parentSec']]['hObj'], sectParams['topol']['parentX'], sectParams['topol']['childX'])  # make topol connection

        # add dipoles
        if sim.cfg.recordDipolesHNN:

            # create a 1-element Vector to store the dipole value for this cell and record from this Vector
            self.dipole = {'hRef': h.Vector(1)}#_ref_[0]} #h._ref_dpl_ref}  #h.Vector(1)
            self.dipole['hRec'] = h.Vector((sim.cfg.duration / sim.cfg.recordStep) + 1)
            self.dipole['hRec'].record(self.dipole['hRef']._ref_x[0])

            for sectName,sectParams in prop['secs'].items():
                sec = self.secs[sectName]
                if 'mechs' in sectParams and 'dipole' in sectParams['mechs']:
                    self.__dipoleInsert(sectName, sec)  # add dipole mechanisms to each section

        # Print message about error inserting mechanisms
        if mechInsertError:
            print("ERROR: Some mechanisms and/or ions were not inserted (for details run with cfg.verbose=True). Make sure the required mod files are compiled.")


    def addSynMechNEURONObj(self, synMech, synMechParams, sec, loc):
        if not synMech.get('hObj'):  # if synMech doesn't have NEURON obj, then create
            synObj = getattr(h, synMechParams['mod'])
            synMech['hObj'] = synObj(loc, sec=sec['hObj'])  # create h Syn object (eg. h.Exp2Syn)
            for synParamName,synParamValue in synMechParams.items():  # add params of the synaptic mechanism
                if synParamName not in ['label', 'mod', 'selfNetCon', 'loc']:
                    setattr(synMech['hObj'], synParamName, synParamValue)
                elif synParamName == 'selfNetcon':  # create self netcon required for some synapses (eg. homeostatic)
                    secLabelNetCon = synParamValue.get('sec', 'soma')
                    locNetCon = synParamValue.get('loc', 0.5)
                    secNetCon = self.secs.get(secLabelNetCon, None)
                    synMech['hObj'] = h.NetCon(secNetCon['hObj'](locNetCon)._ref_v, synMech[''], sec=secNetCon['hObj'])
                    for paramName,paramValue in synParamValue.items():
                        if paramName == 'weight':
                            synMech['hObj'].weight[0] = paramValue
                        elif paramName not in ['sec', 'loc']:
                            setattr(synMech['hObj'], paramName, paramValue)


    def addSynMechsNEURONObj(self):
        # set params for all sections
        for sectName, sectParams in self.secs.items():
            sec = self.secs[sectName]  # pointer to section
            # add synMechs (only used when loading)
            if 'synMechs' in sectParams:
                for synMech in sectParams['synMechs']:
                    if 'label' in synMech and 'loc' in synMech:
                        synMechParams = sim.net.params.synMechParams.get(synMech['label'])  # get params for this synMech
                        self.addSynMechNEURONObj(synMech, synMechParams, sec, synMech['loc'])


    # Create NEURON objs for conns and syns if included in prop (used when loading)
    def addStimsNEURONObj(self):
        # assumes python structure exists
        for stimParams in self.stims:
            if stimParams['type'] == 'NetStim':
                self.addNetStim(stimParams, stimContainer=stimParams)

            else: #if stimParams['type'] in ['IClamp', 'VClamp', 'SEClamp', 'AlphaSynapse']:
                stim = getattr(h, stimParams['type'])(self.secs[stimParams['sec']]['hObj'](stimParams['loc']))
                stimProps = {k:v for k,v in stimParams.items() if k not in ['label', 'type', 'source', 'loc', 'sec', 'hObj']}
                for stimPropName, stimPropValue in stimProps.items(): # set mechanism internal stimParams
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
                stimParams['hObj'] = stim  # add stim object to dict in stims list


    # Create NEURON objs for conns and syns if included in prop (used when loading)
    def addConnsNEURONObj(self):
        # Note: loading connections to point process (eg. Izhi2007a) not yet supported
        # Note: assumes weight is in index 0 (netcon.weight[0])

        from .. import sim

        # assumes python structure exists
        for conn in self.conns:
            # set postsyn target
            if sim.cfg.oneSynPerNetcon:
                synMech = None
            else:
                synMech = next((synMech for synMech in self.secs[conn['sec']]['synMechs'] if synMech['label'] == conn['synMech'] and synMech['loc'] == conn['loc']), None)

            if not synMech:
                synMech = self.addSynMech(conn['synMech'], conn['sec'], conn['loc'])
                #continue  # go to next conn

            try:
                postTarget = synMech['hObj']
            except:
                print('\nError: no synMech available for conn: ', conn)
                print(' cell tags: ',self.tags)
                print(' cell synMechs: ',self.secs[conn['sec']]['synMechs'])
                import sys
                sys.exit()

            # create NetCon
            if conn['preGid'] == 'NetStim':
                netstim = next((stim['hObj'] for stim in self.stims if stim['source']==conn['preLabel']), None)
                if netstim:
                    netcon = h.NetCon(netstim, postTarget)
                else: continue
            else:
                #cell = next((c for c in sim.net.cells if c.gid == conn['preGid']), None)
                netcon = sim.pc.gid_connect(conn['preGid'], postTarget)

            netcon.weight[0] = conn['weight']
            netcon.delay = conn['delay']
            #netcon.threshold = conn.get('threshold', sim.net.params.defaultThreshold)
            conn['hObj'] = netcon

            # Add plasticity
            if conn.get('plast'):
                self._addConnPlasticity(conn['plast'], self.secs[conn['sec']], netcon, 0)


    def associateGid (self, threshold = None):
        from .. import sim

        if self.secs:
            if sim.cfg.createNEURONObj:
                if hasattr(sim, 'rank'):
                    sim.pc.set_gid2node(self.gid, sim.rank) # this is the key call that assigns cell gid to a particular node
                else:
                    sim.pc.set_gid2node(self.gid, 0)
                sec = next((secParams for secName,secParams in self.secs.items() if 'spikeGenLoc' in secParams), None) # check if any section has been specified as spike generator
                if sec:
                    loc = sec['spikeGenLoc']  # get location of spike generator within section
                else:
                    #sec = self.secs['soma'] if 'soma' in self.secs else self.secs[self.secs.keys()[0]]  # use soma if exists, otherwise 1st section
                    sec = next((sec for secName, sec in self.secs.items() if len(sec['topol']) == 0), self.secs[list(self.secs.keys())[0]])  # root sec (no parents)
                    loc = 0.5
                nc = None
                if 'pointps' in sec:  # if no syns, check if point processes with 'vref' (artificial cell)
                    for pointpName, pointpParams in sec['pointps'].items():
                        if 'vref' in pointpParams:
                            nc = h.NetCon(getattr(sec['pointps'][pointpName]['hObj'], '_ref_'+pointpParams['vref']), None, sec=sec['hObj'])
                            break
                if not nc:  # if still haven't created netcon
                    nc = h.NetCon(sec['hObj'](loc)._ref_v, None, sec=sec['hObj'])
                if 'threshold' in sec: threshold = sec['threshold']
                threshold = threshold if threshold is not None else sim.net.params.defaultThreshold
                nc.threshold = threshold
                sim.pc.cell(self.gid, nc, 1)  # associate a particular output stream of events
                del nc # discard netcon
        sim.net.gid2lid[self.gid] = len(sim.net.gid2lid)


    def addSynMech (self, synLabel, secLabel, loc):
        from .. import sim

        synMechParams = sim.net.params.synMechParams.get(synLabel)  # get params for this synMech
        sec = self.secs.get(secLabel, None)

        # add synaptic mechanism to python struct
        if 'synMechs' not in sec or not isinstance(sec['synMechs'], list):
            sec['synMechs'] = []

        if synMechParams and sec:  # if both the synMech and the section exist
            if sim.cfg.createPyStruct and sim.cfg.addSynMechs:
                if sim.cfg.oneSynPerNetcon:
                    synMech = None
                else:
                    synMech = next((synMech for synMech in sec['synMechs'] if synMech['label']==synLabel and synMech['loc']==loc), None)
                if not synMech:  # if synMech not in section, or need multiple synMech per section, then create
                    synMech = Dict({'label': synLabel, 'loc': loc})
                    for paramName, paramValue in synMechParams.items():
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
                # add the NEURON object
                self.addSynMechNEURONObj(synMech, synMechParams, sec, loc)
            else:
                synMech = None
            return synMech


    def modifySynMechs (self, params):
        from .. import sim

        conditionsMet = 1
        if 'cellConds' in params:
            if conditionsMet:
                for (condKey,condVal) in params['cellConds'].items():  # check if all conditions are met
                    # check if conditions met
                    if isinstance(condVal, list):
                        if self.tags.get(condKey) < condVal[0] or self.tags.get(condKey) > condVal[1]:
                            conditionsMet = 0
                            break
                    elif self.tags.get(condKey) != condVal:
                        conditionsMet = 0
                        break

        if conditionsMet:
            for secLabel,sec in self.secs.items():
                for synMech in sec['synMechs']:
                    conditionsMet = 1
                    if 'conds' in params:
                        for (condKey,condVal) in params['conds'].items():  # check if all conditions are met
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
                        for synParamName,synParamValue in {k: v for k,v in params.items() if k not in exclude}.items():
                            if sim.cfg.createPyStruct:
                                synMech[synParamName] = synParamValue
                            if sim.cfg.createNEURONObj:
                                try:
                                    setattr(synMech['hObj'], synParamName, synParamValue)
                                except:
                                    print('Error setting %s=%s on synMech' % (synParamName, str(synParamValue)))




    def addConn (self, params, netStimParams = None):
        from .. import sim

        # threshold = params.get('threshold', sim.net.params.defaultThreshold)  # depreacated -- use threshold in preSyn cell sec
        if params.get('weight') is None: params['weight'] = sim.net.params.defaultWeight # if no weight, set default
        if params.get('delay') is None: params['delay'] = sim.net.params.defaultDelay # if no delay, set default
        if params.get('loc') is None: params['loc'] = 0.5 # if no loc, set default
        if params.get('synsPerConn') is None: params['synsPerConn'] = 1  # if no synsPerConn, set default

        # Get list of section labels
        secLabels = self._setConnSections(params)
        if secLabels == -1: return  # if no section available exit func

        # Warning or error if self connections
        if params['preGid'] == self.gid:
            # Only allow self connections if option selected by user
            # !!!! AD HOC RULE FOR HNN!!! -  or 'soma' in secLabels and not self.tags['cellType'] == 'L5Basket' (removed)
            if sim.cfg.allowSelfConns:
                if sim.cfg.verbose: print('  Warning: creating self-connection on cell gid=%d, section=%s '%(self.gid, params.get('sec')))
            else:
                if sim.cfg.verbose: print('  Error: attempted to create self-connection on cell gid=%d, section=%s '%(self.gid, params.get('sec')))
                return  # if self-connection return

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
            if not sim.cfg.allowConnsWithWeight0 and weights[i] == 0.0:
                continue

            if netStimParams:
                    netstim = self.addNetStim(netStimParams)

            if params.get('gapJunction', False) == True:  # only run for post gap junc (not pre)
                if hasattr(sim, 'rank'):
                    preGapId = 1e9*sim.rank + sim.net.lastGapId  # global index for presyn gap junc
                else:
                    preGapId = sim.net.lastGapId
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
                connParams = {k:v for k,v in params.items() if k not in ['synsPerConn']}
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
                    synMechs[i]['hObj'].weight = weights[i]
                    sourceVar = self.secs[synMechSecs[i]]['hObj'](synMechLocs[i])._ref_v
                    targetVar = synMechs[i]['hObj']._ref_vpeer  # assumes variable is vpeer -- make a parameter
                    sec = self.secs[synMechSecs[i]]
                    sim.pc.target_var(targetVar, connParams['gapId'])
                    self.secs[synMechSecs[i]]['hObj'].push()
                    sim.pc.source_var(sourceVar, connParams['preGapId'])
                    h.pop_section()
                    netcon = None

                # connections using NetCons
                else:
                    if pointp:
                        sec = self.secs[secLabels[0]]
                        postTarget = sec['pointps'][pointp]['hObj'] #  local point neuron
                    else:
                        sec = self.secs[synMechSecs[i]]
                        postTarget = synMechs[i]['hObj'] # local synaptic mechanism

                    if netStimParams:
                        netcon = h.NetCon(netstim, postTarget) # create Netcon between netstim and target
                    else:
                        netcon = sim.pc.gid_connect(params['preGid'], postTarget) # create Netcon between global gid and target

                    netcon.weight[weightIndex] = weights[i]  # set Netcon weight
                    netcon.delay = delays[i]  # set Netcon delay
                    #netcon.threshold = threshold  # set Netcon threshold
                    self.conns[-1]['hObj'] = netcon  # add netcon object to dict in conns list


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


                # Add plasticity
                self._addConnPlasticity(params, sec, netcon, weightIndex)

            if sim.cfg.verbose:
                sec = params['sec'] if pointp else synMechSecs[i]
                loc = params['loc'] if pointp else synMechLocs[i]
                preGid = netStimParams['source']+' NetStim' if netStimParams else params['preGid']
                try:
                    print(('  Created connection preGid=%s, postGid=%s, sec=%s, loc=%.4g, synMech=%s, weight=%.4g, delay=%.2f'
                        % (preGid, self.gid, sec, loc, params['synMech'], weights[i], delays[i])))
                except:
                    print(('  Created connection preGid=%s' % (preGid)))


    def modifyConns (self, params):
        from .. import sim

        for conn in self.conns:
            conditionsMet = 1

            if 'conds' in params:
                for (condKey,condVal) in params['conds'].items():  # check if all conditions are met
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
                for (condKey,condVal) in params['postConds'].items():  # check if all conditions are met
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
                try:
                    cell = sim.net.cells[conn['preGid']]

                    if cell:
                        for (condKey,condVal) in params['preConds'].items():  # check if all conditions are met
                            # check if conditions met
                            if isinstance(condVal, list) and isinstance(condVal[0], Number):
                                if cell.tags.get(condKey) < condVal[0] or cell.tags.get(condKey) > condVal[1]:
                                    conditionsMet = 0
                                    break
                            elif isinstance(condVal, list) and isinstance(condVal[0], basestring):
                                if cell.tags.get(condKey) not in condVal:
                                    conditionsMet = 0
                                    break
                            elif cell.tags.get(condKey) != condVal:
                                conditionsMet = 0
                                break
                except:
                    pass
                    #print('Warning: modifyConns() does not yet support conditions of presynaptic cells when running parallel sims')

            if conditionsMet:  # if all conditions are met, set values for this cell
                if sim.cfg.createPyStruct:
                    for paramName, paramValue in {k: v for k,v in params.items() if k not in ['conds','preConds','postConds']}.items():
                        conn[paramName] = paramValue
                if sim.cfg.createNEURONObj:
                    for paramName, paramValue in {k: v for k,v in params.items() if k not in ['conds','preConds','postConds']}.items():
                        try:
                            if paramName == 'weight':
                                conn['hObj'].weight[0] = paramValue
                            else:
                                setattr(conn['hObj'], paramName, paramValue)
                        except:
                            print('Error setting %s=%s on Netcon' % (paramName, str(paramValue)))


    def modifyStims (self, params):
        from .. import sim

        conditionsMet = 1
        if 'cellConds' in params:
            if conditionsMet:
                for (condKey,condVal) in params['cellConds'].items():  # check if all conditions are met
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
                    for (condKey,condVal) in params['conds'].items():  # check if all conditions are met
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
                        for paramName, paramValue in {k: v for k,v in params.items() if k not in ['conds','cellConds']}.items():
                            if stim['type'] == 'NetStim' and paramName in ['weight', 'delay']:
                                conn[paramName] = paramValue
                            else:
                                stim[paramName] = paramValue
                    if sim.cfg.createNEURONObj:
                        for paramName, paramValue in {k: v for k,v in params.items() if k not in ['conds','cellConds']}.items():
                            try:
                                if stim['type'] == 'NetStim':
                                    if paramName == 'weight':
                                        conn['hObj'].weight[0] = paramValue
                                    elif paramName in ['delay']:
                                        setattr(conn['hObj'], paramName, paramValue)
                                    elif paramName in ['rate']:
                                        stim['interval'] = 1.0/paramValue
                                        setattr(stim['hObj'], 'interval', stim['interval'])
                                    elif paramName in ['interval']:
                                        stim['rate'] = 1.0/paramValue
                                        setattr(stim['hObj'], 'interval', stim['interval'])
                                    else:
                                        setattr(stim['hObj'], paramName, paramValue)
                                else:
                                    setattr(stim['hObj'], paramName, paramValue)
                            except:
                                print('Error setting %s=%s on stim' % (paramName, str(paramValue)))



    def addStim (self, params):
        from .. import sim

        if not params['sec'] or (isinstance(params['sec'], basestring) and not params['sec'] in list(self.secs.keys())+list(self.secLists.keys())):
            if sim.cfg.verbose: print('  Warning: no valid sec specified for stim on cell gid=%d so using soma or 1st available. Existing secs: %s; params: %s'%(self.gid, list(self.secs.keys()),params))
            if 'soma' in self.secs:
                params['sec'] = 'soma'  # use 'soma' if exists
            elif self.secs:
                params['sec'] = list(self.secs.keys())[0]  # if no 'soma', use first sectiona available
            else:
                if sim.cfg.verbose: print('  Error: no Section available on cell gid=%d to add stim'%(self.gid))
                return

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

            # if 'threshold' in params: connParams['threshold'] = params.get('threshold')   # depreacted, set threshold in preSyn cell
            if 'shape' in params: connParams['shape'] = params.get('shape')
            if 'plast' in params: connParams['plast'] = params.get('plast')

            netStimParams = {'source': params['source'],
                'type': params['type'],
                'rate': params['rate'] if 'rate' in params else 1000.0/params['interval'],
                'noise': params['noise'] if 'noise' in params else 0.0,
                'number': params['number'],
                'start': params['start'],
                'seed': params['seed'] if 'seed' in params else sim.cfg.seeds['stim']}

            self.addConn(connParams, netStimParams)


        elif params['type'] in ['IClamp', 'VClamp', 'SEClamp', 'AlphaSynapse']:
            sec = self.secs[params['sec']]
            stim = getattr(h, params['type'])(sec['hObj'](params['loc']))
            stimParams = {k:v for k,v in params.items() if k not in ['type', 'source', 'loc', 'sec', 'label']}
            stringParams = ''
            for stimParamName, stimParamValue in stimParams.items(): # set mechanism internal params
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
            self.stims[-1]['hObj'] = stim  # add stim object to dict in stims list

            if sim.cfg.verbose: print(('  Added %s %s to cell gid=%d, sec=%s, loc=%.4g%s'%
                (params['source'], params['type'], self.gid, params['sec'], params['loc'], stringParams)))

        else:
            if sim.cfg.verbose: print(('Adding exotic stim (NeuroML 2 based?): %s'% params))
            sec = self.secs[params['sec']]
            stim = getattr(h, params['type'])(sec['hObj'](params['loc']))
            stimParams = {k:v for k,v in params.items() if k not in ['type', 'source', 'loc', 'sec', 'label']}
            stringParams = ''
            for stimParamName, stimParamValue in stimParams.items(): # set mechanism internal params
                if isinstance(stimParamValue, list):
                    print("Can't set point process paramaters of type vector eg. VClamp.amp[3]")
                    pass
                    #setattr(stim, stimParamName._ref_[0], stimParamValue[0])
                elif 'originalFormat' in params and stimParamName=='originalFormat':
                    if params['originalFormat']=='NeuroML2_stochastic_input':
                        if sim.cfg.verbose: print(('   originalFormat: %s'%(params['originalFormat'])))

                        rand = h.Random()
                        stim_ref = params['label'][:params['label'].rfind(self.tags['pop'])]

                        # e.g. Stim3_2_popPyrS_2_soma_0_5 -> 2
                        index_in_stim = int(stim_ref.split('_')[-2])
                        stim_id = stim_ref.split('_')[0]
                        sim._init_stim_randomizer(rand, stim_id, index_in_stim, sim.cfg.seeds['stim'])
                        rand.negexp(1)
                        stim.noiseFromRandom(rand)
                        params['h%s'%params['originalFormat']] = rand
                else:
                    if stimParamName in ['weight']:
                        setattr(stim, stimParamName, stimParamValue)
                        stringParams = stringParams + ', ' + stimParamName +'='+ str(stimParamValue)
                    else:
                        setattr(stim, stimParamName, stimParamValue)


            self.stims.append(params) # add to python structure
            self.stims[-1]['hObj'] = stim  # add stim object to dict in stims list
            if sim.cfg.verbose: print(('  Added %s %s to cell gid=%d, sec=%s, loc=%.4g%s'%
                (params['source'], params['type'], self.gid, params['sec'], params['loc'], stringParams)))


    def _setConnSections (self, params):
        from .. import sim

        # if no section specified or single section specified does not exist
        if not params.get('sec') or (isinstance(params.get('sec'), basestring) and not params.get('sec') in list(self.secs.keys())+list(self.secLists.keys())):
            if sim.cfg.verbose: print('  Warning: no valid sec specified for connection to cell gid=%d so using soma or 1st available'%(self.gid))
            if 'soma' in self.secs:
                params['sec'] = 'soma'  # use 'soma' if exists
            elif self.secs:
                params['sec'] = list(self.secs.keys())[0]  # if no 'soma', use first sectiona available
            else:
                if sim.cfg.verbose: print('  Error: no Section available on cell gid=%d to add connection'%(self.gid))
                sec = -1  # if no Sections available print error and exit
                return sec

            secLabels = [params['sec']]

        # if sectionList or list of sections
        elif isinstance(params.get('sec'), list) or params.get('sec') in self.secLists:
            secList = list(params['sec']) if isinstance(params['sec'], list) else list(self.secLists[params['sec']])
            secLabels = []
            for i,section in enumerate(secList):
                if section not in self.secs: # remove sections that dont exist; and corresponding weight and delay
                    if sim.cfg.verbose: print('  Error: Section %s not available so removing from list of sections for connection to cell gid=%d'%(section, self.gid))
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
        from .. import sim

        if netStimParams:
            scaleFactor = sim.net.params.scaleConnWeightNetStims
        elif isinstance(sim.net.params.scaleConnWeightModels, dict) and sim.net.params.scaleConnWeightModels.get(self.tags['cellModel'], None) is not None:
            scaleFactor = sim.net.params.scaleConnWeightModels[self.tags['cellModel']]  # use scale factor specific for this cell model
        else:
            scaleFactor = sim.net.params.scaleConnWeight # use global scale factor

        if isinstance(params['weight'],list):
            weights = [scaleFactor * w for w in params['weight']]
            if len(weights) == 1: weights = [weights[0]] * params['synsPerConn']
        else:
            weights = [scaleFactor * params['weight']] * params['synsPerConn']

        return weights


    def _setConnPointP(self, params, secLabels, weightIndex):
        from .. import sim

        # Find if any point process with V not calculated in section (artifical cell, eg. Izhi2007a)
        pointp = None
        if len(secLabels)==1 and 'pointps' in self.secs[secLabels[0]]:  #  check if point processes with 'vref' (artificial cell)
            for pointpName, pointpParams in self.secs[secLabels[0]]['pointps'].items():
                if 'vref' in pointpParams:  # if includes vref param means doesn't use Section v or synaptic mechanisms
                    pointp = pointpName
                    if 'synList' in pointpParams:
                        if params.get('synMech') in pointpParams['synList']:
                            if isinstance(params.get('synMech'), list):
                                weightIndex = [pointpParams['synList'].index(synMech) for synMech in params.get('synMech')]
                            else:
                                weightIndex = pointpParams['synList'].index(params.get('synMech'))  # udpate weight index based pointp synList

        if pointp and params['synsPerConn'] > 1: # only single synapse per connection rule allowed
            if sim.cfg.verbose: print('  Error: Multiple synapses per connection rule not allowed for cells where V is not in section (cell gid=%d) '%(self.gid))
            return -1, weightIndex

        return pointp, weightIndex


    def _setConnSynMechs (self, params, secLabels):
        from .. import sim

        synsPerConn = params['synsPerConn']
        if not params.get('synMech'):
            if sim.net.params.synMechParams:  # if no synMech specified, but some synMech params defined
                synLabel = list(sim.net.params.synMechParams.keys())[0]  # select first synMech from net params and add syn
                params['synMech'] = synLabel
                if sim.cfg.verbose: print('  Warning: no synaptic mechanisms specified for connection to cell gid=%d so using %s '%(self.gid, synLabel))
            else: # if no synaptic mechanism specified and no synMech params available
                if sim.cfg.verbose: print('  Error: no synaptic mechanisms available to add conn on cell gid=%d '%(self.gid))
                return -1  # if no Synapse available print error and exit

        # if desired synaptic mechanism specified in conn params
        if synsPerConn > 1:  # if more than 1 synapse
            if len(secLabels) == 1:  # if single section, create all syns there
                synMechSecs = [secLabels[0]] * synsPerConn  # same section for all
                if isinstance(params['loc'], list):
                    if len(params['loc']) == synsPerConn:
                        synMechLocs = params['loc']
                    else:
                        print("Error: The length of the list of locations does not match synsPerConn (distributing uniformly)")
                        synMechSecs, synMechLocs = self._distributeSynsUniformly(secList=secLabels, numSyns=synsPerConn)
                else:
                    synMechLocs = [i*(1.0/synsPerConn)+1.0/synsPerConn/2 for i in range(synsPerConn)]
            else:
                # if multiple sections, distribute syns uniformly
                if sim.cfg.distributeSynsUniformly:
                    synMechSecs, synMechLocs = self._distributeSynsUniformly(secList=secLabels, numSyns=synsPerConn)
                else:
                    if not sim.cfg.connRandomSecFromList and synsPerConn == len(secLabels):  # have list of secs that matches num syns
                        synMechSecs = secLabels
                        if isinstance(params['loc'], list):
                            if len(params['loc']) == synsPerConn:  # list of locs matches num syns
                                synMechLocs = params['loc']
                            else:  # list of locs does not match num syns
                                print("Error: The length of the list of locations does not match synsPerConn (with cfg.distributeSynsUniformly = False")
                                return
                        else: # single loc
                            synMechLocs = [params['loc']] * synsPerConn
                    else:
                        synMechSecs = secLabels
                        synMechLocs = params['loc'] if isinstance(params['loc'], list) else [params['loc']]

                        # randomize the section to connect to and move it to beginning of list
                        if sim.cfg.connRandomSecFromList and len(synMechSecs) >= synsPerConn:
                            if len(synMechLocs) == 1: synMechLocs = [params['loc']] * synsPerConn
                            rand = h.Random()
                            preGid = params['preGid'] if isinstance(params['preGid'], int) else 0
                            rand.Random123(sim.hashStr('connSynMechsSecs'), self.gid, preGid) # initialize randomizer

                            randSecPos = sim.net.randUniqueInt(rand, synsPerConn, 0, len(synMechSecs)-1)
                            synMechSecs = [synMechSecs[i] for i in randSecPos]

                            if isinstance(params['loc'], list):
                                randLocPos = sim.net.randUniqueInt(rand, synsPerConn, 0, len(synMechLocs)-1)
                                synMechLocs = [synMechLocs[i] for i in randLocPos]
                            else:
                                randLoc = rand.uniform(0, 1)
                                synMechLocs = [rand.uniform(0, 1) for i in range(synsPerConn)]
                        else:
                                print("\nError: The length of the list of sections needs to be greater or equal to the synsPerConn (with cfg.connRandomSecFromList = True")
                                return

        else:  # if 1 synapse
            # by default place on 1st section of list and location available
            synMechSecs = secLabels
            synMechLocs = params['loc'] if isinstance(params['loc'], list) else [params['loc']]

            # randomize the section to connect to and move it to beginning of list
            if sim.cfg.connRandomSecFromList and len(synMechSecs)>1:
                rand = h.Random()
                preGid = params['preGid'] if isinstance(params['preGid'], int) else 0
                rand.Random123(sim.hashStr('connSynMechsSecs'), self.gid, preGid) # initialize randomizer
                pos = int(rand.discunif(0, len(synMechSecs)-1))
                synMechSecs[pos], synMechSecs[0] = synMechSecs[0], synMechSecs[pos]
                if len(synMechLocs)>1:
                    synMechLocs[pos], synMechLocs[0] = synMechLocs[0], synMechLocs[pos]

        # add synaptic mechanism to section based on synMechSecs and synMechLocs (if already exists won't be added unless nonLinear set to True)
        synMechs = [self.addSynMech(synLabel=params['synMech'], secLabel=synMechSecs[i], loc=synMechLocs[i]) for i in range(synsPerConn)]
        return synMechs, synMechSecs, synMechLocs


    def _distributeSynsUniformly (self, secList, numSyns):
        from .. import sim

        from numpy import cumsum
        try:
            if 'L' in self.secs[secList[0]]['geom']:
                secLengths = [self.secs[s]['geom']['L'] for s in secList]
            elif getattr(self.secs[secList[0]]['hObj'], 'L', None):
                secLengths = [self.secs[s]['hObj'].L for s in secList]
            else:
                secLengths = [1.0 for s in secList]
                if sim.cfg.verbose:
                    print(('  Section lengths not available to distribute synapses in cell %d'%self.gid))

            secLengths = [x for x in secLengths if isinstance(x, Number)]
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



    def getSomaPos(self):
        """
        Get soma position;
        Used to calculate seg coords for LFP calc (one per population cell; assumes same morphology)
        """

        n3dsoma = 0
        r3dsoma = np.zeros(3)
        for sec in [sec for secName, sec in self.secs.items() if 'soma' in secName]:
            sec['hObj'].push()
            n3d = int(h.n3d())  # get number of n3d points in each section
            r3d = np.zeros((3, n3d))  # to hold locations of 3D morphology for the current section
            n3dsoma += n3d

            for i in range(n3d):
                r3dsoma[0] += h.x3d(i)
                r3dsoma[1] += h.y3d(i)
                r3dsoma[2] += h.z3d(i)

            h.pop_section()

        r3dsoma /= n3dsoma

        return r3dsoma

    def calcAbsSegCoords(self):
        """
        Calculate absolute seg coords by translating the relative seg coords -- used for LFP calc
        """

        from .. import sim

        p3dsoma = self.getSomaPos()
        pop = self.tags['pop']

        self._segCoords = {}
        p3dsoma = p3dsoma[np.newaxis].T  # trasnpose 1d array to enable matrix calculation

        if hasattr(sim.net.pops[pop], '_morphSegCoords'):
            # rotated coordinates around z axis first then shift relative to the soma
            morphSegCoords = sim.net.pops[pop]._morphSegCoords
            self._segCoords['p0'] = p3dsoma + morphSegCoords['p0']
            self._segCoords['p1'] = p3dsoma + morphSegCoords['p1']
        else:
            # rotated coordinates around z axis
            self._segCoords['p0'] = p3dsoma
            self._segCoords['p1'] = p3dsoma

        self._segCoords['d0'] = morphSegCoords['d0']
        self._segCoords['d1'] = morphSegCoords['d1']


    def setImembPtr(self):
        """Set PtrVector to point to the i_membrane_"""
        jseg = 0
        for sec in list(self.secs.values()):
            hSec = sec['hObj']
            for iseg, seg in enumerate(hSec):
                try:
                    self.imembPtr.pset(jseg, seg._ref_i_membrane_)  # notice the underscore at the end (in nA)
                except:
                    '  Error setting Vector to point to i_membrane_'
                jseg += 1


    def getImemb(self):
        """Gather membrane currents from PtrVector into imVec (does not need a loop!)"""
        self.imembPtr.gather(self.imembVec)
        return self.imembVec.as_numpy()  # (nA)


    def updateShape(self):
        """Call after h.define_shape() to update cell coords"""
        x = self.tags['x']
        y = -self.tags['y'] # Neuron y-axis positive = upwards, so assume pia=0 and cortical depth = neg
        z = self.tags['z']

        for sec in list(self.secs.values()):
            if 'geom' in sec and 'pt3d' not in sec['geom'] and isinstance(sec['hObj'], type(h.Section())):  # only cells that didn't have pt3d before
                sec['geom']['pt3d'] = []
                sec['hObj'].push()
                n3d = int(h.n3d())  # get number of n3d points in each section
                for i in range(n3d):
                    # by default L is added in x-axis; shift to y-axis; z increases 100um for each cell so set to 0
                    pt3d = [h.y3d(i), h.x3d(i), 0, h.diam3d(i)]
                    sec['geom']['pt3d'].append(pt3d)
                    h.pt3dchange(i, x+pt3d[0], y+pt3d[1], z+pt3d[2], pt3d[3], sec=sec['hObj'])
                h.pop_section()
