"""
Module containing a compartmental cell class

"""

from netpyne.specs.netParams import CellParams, SynMechParams

try:
    basestring
except NameError:
    basestring = str

from numbers import Number
from copy import deepcopy
from neuron import h  # Import NEURON
import numpy as np
from math import sin, cos, sqrt
from .cell import Cell
from ..specs import Dict
from ..specs.netParams import SynMechParams
from .. import sim


###############################################################################
#
# COMPARTMENTAL CELL CLASS
#
###############################################################################


class CompartCell(Cell):
    """
    Class for/to <short description of `netpyne.cell.compartCell.CompartCell`>

    """

    def __init__(self, gid, tags, create=True, associateGid=True):
        super(CompartCell, self).__init__(gid, tags)
        self.secs = Dict()  # dict of sections
        self.secLists = Dict()  # dict of sectionLists

        if create:
            self.create()  # create cell
        if associateGid:
            self.associateGid()  # register cell for this node

    def __str__(self):
        try:
            gid, cty, cmo = self.gid, self.tags['cellType'], self.tags['cellModel']  # only use if these exist
            return 'compartCell_%s_%s_%d' % (cty, cmo, gid)
        except:
            return 'compartCell%d' % self.gid

    def __repr__(self):
        return self.__str__()

    def create(self, createNEURONObj=None):
        from .. import sim

        if createNEURONObj is None:
            createNEURONObj = sim.cfg.createNEURONObj

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
                conditionsMet = self.checkConditions(prop['conds'])

            elif self.tags['cellType'] != propLabel:  # simplified method for defining cell params (when no 'conds')
                conditionsMet = False

            if conditionsMet:  # if all conditions are met, set values for this cell

                # Intercept possible issue where the cell is designed to be PointCell but misclassfied as CompartCell in Pop._setCellClass()
                # (may happen if .mod not compiled or mech name misspelled)
                assert 'secs' in prop, \
                    f"""Cell rule labeled '{propLabel}' is a compartment cell, but it doesn't have required entry 'secs'.
If this cell is expected to be a point cell instead, make sure the correspondent mechanism is included and compiled."""

                if sim.cfg.includeParamsLabel:
                    if 'label' not in self.tags:
                        self.tags['label'] = [propLabel]  # create list of property sets
                    else:
                        self.tags['label'].append(
                            propLabel
                        )  # add label of cell property set to list of property sets for this cell
                if sim.cfg.createPyStruct:
                    self.createPyStruct(prop)
                if createNEURONObj:
                    self.createNEURONObj(
                        prop, propLabel
                    )  # add sections, mechanisms, synaptic mechanisms, geometry and topolgy specified by this property set

    def modify(self, prop):
        from .. import sim

        conditionsMet = self.checkConditions(prop['conds'])

        if conditionsMet:  # if all conditions are met, set values for this cell
            if sim.cfg.createPyStruct:
                self.createPyStruct(prop)
            if sim.cfg.createNEURONObj:
                # add sections, mechanisms, synaptic mechanisms, geometry and topolgy specified by this property set
                self.createNEURONObj(prop)

    def createPyStruct(self, prop):
        from .. import sim

        # set params for all sections
        for sectName, sectParams in prop['secs'].items():
            # create section
            if sectName not in self.secs:
                self.secs[sectName] = Dict()  # create section dict
            sec = self.secs[sectName]  # pointer to section

            # add distributed mechanisms
            if 'mechs' in sectParams:
                for mechName, mechParams in sectParams['mechs'].items():
                    if 'mechs' not in sec:
                        sec['mechs'] = Dict()
                    if mechName not in sec['mechs']:
                        sec['mechs'][mechName] = Dict()
                    for mechParamName, mechParamValue in mechParams.items():  # add params of the mechanism
                        sec['mechs'][mechName][mechParamName] = mechParamValue

            # add ion info
            if 'ions' in sectParams:
                for ionName, ionParams in sectParams['ions'].items():
                    if 'ions' not in sec:
                        sec['ions'] = Dict()
                    if ionName not in sec['ions']:
                        sec['ions'][ionName] = Dict()
                    for ionParamName, ionParamValue in ionParams.items():  # add params of the ion
                        sec['ions'][ionName][ionParamName] = ionParamValue

            # add synMechs
            if 'synMechs' in sectParams:
                for synMech in sectParams['synMechs']:
                    if 'label' in synMech and 'loc' in synMech:
                        self.addSynMech(synLabel=synMech['label'], secLabel=sectName, loc=synMech['loc'])

            # add point processes
            if 'pointps' in sectParams:
                for pointpName, pointpParams in sectParams['pointps'].items():
                    # if self.tags['cellModel'] == pointpName: # only required if want to allow setting various cell models in same rule
                    if 'pointps' not in sec:
                        sec['pointps'] = Dict()
                    if pointpName not in sec['pointps']:
                        sec['pointps'][pointpName] = Dict()
                    for pointpParamName, pointpParamValue in pointpParams.items():  # add params of the mechanism
                        if pointpParamValue == 'gid':
                            pointpParamValue = self.gid
                        sec['pointps'][pointpName][pointpParamName] = pointpParamValue

            # add geometry params
            if 'geom' in sectParams:
                for geomParamName, geomParamValue in sectParams['geom'].items():
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
                for topolParamName, topolParamValue in sectParams['topol'].items():
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

    def initV(self):
        for sec in list(self.secs.values()):
            if 'vinit' in sec:
                sec['hObj'].v = sec['vinit']

    # Create dictionary of section names with entries to scale section lengths to length along z-axis
    def __dipoleGetSecLength(self, secName):
        L = 1
        # basal_2 and basal_3 at 45 degree angle to z-axis.
        if 'basal_2' in secName:
            L = np.sqrt(2) / 2.0
        elif 'basal_3' in secName:
            L = np.sqrt(2) / 2.0
        # apical_oblique at 90 perpendicular to z-axis
        elif 'apical_oblique' in secName:
            L = 0.0
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
            sec['hDipole_pp'] = h.Dipole(1.0, sec=sec['hObj'])
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
                h.setpointer(sec['hObj'](loc[i - 1])._ref_v, 'pv', sec['hObj'](loc[i]).dipole)
            else:
                h.setpointer(sec['hObj'](0)._ref_v, 'pv', sec['hObj'](loc[i]).dipole)

            # set aggregate pointers
            h.setpointer(dpp._ref_Qsum, 'Qsum', sec['hObj'](loc[i]).dipole)
            h.setpointer(self.dipole['hRef']._ref_x[0], 'Qtotal', sec['hObj'](loc[i]).dipole)

            # add ztan values
            sec['hObj'](loc[i]).dipole.ztan = y_diff[i]

        # set the pp dipole's ztan value to the last value from y_diff
        dpp.ztan = y_diff[-1]

    def createNEURONObj(self, prop, propLabel=None):
        from .. import sim

        mechInsertError = False  # flag to print error inserting mechanisms

        if propLabel and propLabel in sim.net.params.cellParams:
            cellType = propLabel
        else:
            cellType = self.tags['cellType']

        cellVars = {}
        cvars = sim.net.params.cellParams[cellType].get('vars', {})
        # cellVars get evaluated once per cell. If there are multiple sections or segments referring to it, all they will use this same value
        for name, val in cvars.items():
            func, vars = CellParams.stringFuncAndVarsForCellVar(cellType, name)
            if func:
                val = self.__evaluateCellParamsStringFunc(func, vars)
            cellVars[name] = val

        # set params for all sections
        for sectName, sectParams in prop['secs'].items():
            # create section
            if sectName not in self.secs:
                self.secs[sectName] = Dict()  # create sect dict if doesn't exist
            if 'hObj' not in self.secs[sectName] or self.secs[sectName]['hObj'] in [None, {}, []]:
                self.secs[sectName]['hObj'] = h.Section(name=sectName, cell=self)  # create h Section object

        # set topology
        for sectName, sectParams in prop['secs'].items():  # iterate sects again for topology (ensures all exist)
            sec = self.secs[sectName]  # pointer to section # pointer to child sec
            if 'topol' in sectParams:
                if sectParams['topol']:
                    sec['hObj'].connect(
                        self.secs[sectParams['topol']['parentSec']]['hObj'],
                        sectParams['topol']['parentX'],
                        sectParams['topol']['childX'],
                    )  # make topol connection

        for sectName, sectParams in prop['secs'].items():
            sec = self.secs[sectName]  # pointer to section

            if 'geom' in sectParams:
                self._setGeometryParams(sectName, sectParams, cellType, cellVars)

            # add distributed mechanisms
            if 'mechs' in sectParams:
                mechInsertError |= self._addDistributedMechs(sectName, sectParams, cellType, cellVars)

            # add ions
            if 'ions' in sectParams:
                mechInsertError |= self._addIons(sectName, sectParams)

            # add synMechs (only used when loading because python synMechs already exist)
            if 'synMechs' in sectParams:
                for synMech in sectParams['synMechs']:
                    if 'label' in synMech and 'loc' in synMech:
                        synMechParams = sim.net.params.synMechParams.get(
                            synMech['label']
                        )  # get params for this synMech
                        self.addSynMechNEURONObj(synMech, synMech['label'], synMechParams, sec, synMech['loc'])

            # add point processes
            if 'pointps' in sectParams:
                self._addPointProcesses(sectName, sectParams, cellType, cellVars)

        # add dipoles
        if sim.cfg.recordDipolesHNN:

            # create a 1-element Vector to store the dipole value for this cell and record from this Vector
            self.dipole = {'hRef': h.Vector(1)}  # _ref_[0]} #h._ref_dpl_ref}  #h.Vector(1)
            self.dipole['hRec'] = h.Vector((sim.cfg.duration / sim.cfg.recordStep) + 1)
            self.dipole['hRec'].record(self.dipole['hRef']._ref_x[0])

            for sectName, sectParams in prop['secs'].items():
                sec = self.secs[sectName]
                if 'mechs' in sectParams and 'dipole' in sectParams['mechs']:
                    self.__dipoleInsert(sectName, sec)  # add dipole mechanisms to each section

        # Print message about error inserting mechanisms
        if mechInsertError:
            print(
                "ERROR: Some mechanisms and/or ions were not inserted (for details run with cfg.verbose=True). Make sure the required mod files are compiled."
            )

    def _setGeometryParams(self, sectName, sectParams, cellType, cellVars):
        sec = self.secs[sectName]

        for geomParamName, geomParamValue in sectParams['geom'].items():
            if not type(geomParamValue) in [list, dict]:  # skip any list or dic params
                func, vars = CellParams.stringFuncAndVarsForGeom(cellType, sectName, geomParamName)
                if func:
                    geomParamValue = self.__evaluateCellParamsStringFunc(func, vars, sec, cellVars=cellVars)
                setattr(sec['hObj'], geomParamName, geomParamValue)

        # set 3d geometry
        if 'pt3d' in sectParams['geom']:
            h.pt3dclear(sec=sec['hObj'])
            if sim.cfg.pt3dRelativeToCellLocation:
                x = self.tags['x']
                y = (
                    -self.tags['y'] if sim.cfg.invertedYCoord else self.tags['y']
                )  # Neuron y-axis positive = upwards, so assume pia=0 and cortical depth = neg
                z = self.tags['z']
            else:
                x = y = z = 0
            for pt3d in sectParams['geom']['pt3d']:
                h.pt3dadd(x + pt3d[0], y + pt3d[1], z + pt3d[2], pt3d[3], sec=sec['hObj'])

    def _addDistributedMechs(self, sectName, sectParams, cellType, cellVars):
        mechInsertError = False
        excludeMechs = ['dipole']  # dipole is special case
        sec = self.secs[sectName]
        mechsInclude = {k: v for k, v in sectParams['mechs'].items() if k not in excludeMechs}
        for mechName, mechParams in mechsInclude.items():
            if mechName not in sec['mechs']:
                sec['mechs'][mechName] = Dict()
            try:
                sec['hObj'].insert(mechName)
            except:
                mechInsertError = True
                if sim.cfg.verbose:
                    print(
                        '# Error inserting %s mechanims in %s section! (check mod files are compiled)'
                        % (mechName, sectName)
                    )
                continue
            for mechParamName, mechParamValue in mechParams.items():  # add params of the mechanism
                for iseg, seg in enumerate(sec['hObj']):  # set mech params for each segment
                    if type(mechParamValue) in [list]:
                        if len(mechParamValue) == 1:
                            mechParamValueFinal = mechParamValue[0]
                        else:
                            mechParamValueFinal = mechParamValue[iseg]
                    else:
                        mechParamValueFinal = mechParamValue
                    if mechParamValueFinal is not None:  # avoid setting None values
                        if isinstance(mechParamValueFinal, basestring):
                            func, vars = CellParams.stringFuncAndVarsForMod(
                                cellType, sectName, 'mechs', mechName, mechParamName
                            )
                            if func:
                                mechParamValueFinal = self.__evaluateCellParamsStringFunc(
                                    func, vars, sec, seg.x, cellVars
                                )
                        setattr(getattr(seg, mechName), mechParamName, mechParamValueFinal)
        return mechInsertError

    def _addIons(self, sectName, sectParams):
        mechInsertError = False
        sec = self.secs[sectName]
        for ionName, ionParams in sectParams['ions'].items():
            if ionName not in sec['ions']:
                sec['ions'][ionName] = Dict()
            try:
                sec['hObj'].insert(ionName + '_ion')  # insert mechanism
            except:
                mechInsertError = True
                if sim.cfg.verbose:
                    print('# Error inserting %s ion in %s section!' % (ionName, sectName))
                continue
            for ionParamName, ionParamValue in ionParams.items():  # add params of the mechanism
                ionParamValueFinal = ionParamValue
                for iseg, seg in enumerate(sec['hObj']):  # set ion params for each segment
                    if type(ionParamValue) in [list]:
                        ionParamValueFinal = ionParamValue[iseg]
                    if ionParamName == 'e':
                        setattr(seg, ionParamName + ionName, ionParamValueFinal)
                    elif ionParamName == 'o':
                        setattr(seg, '%so' % ionName, ionParamValueFinal)
                        h(
                            '%so0_%s_ion = %s' % (ionName, ionName, ionParamValueFinal)
                        )  # e.g. cao0_ca_ion, the default initial value
                    elif ionParamName == 'i':
                        setattr(seg, '%si' % ionName, ionParamValueFinal)
                        h(
                            '%si0_%s_ion = %s' % (ionName, ionName, ionParamValueFinal)
                        )  # e.g. cai0_ca_ion, the default initial value

            # if sim.cfg.verbose: print("Updated ion: %s in %s, e: %s, o: %s, i: %s" % \
            #         (ionName, sectName, seg.__getattribute__('e'+ionName), seg.__getattribute__(ionName+'o'), seg.__getattribute__(ionName+'i')))
        return mechInsertError

    def _addPointProcesses(self, sectName, sectParams, cellType, cellVars):
        sec = self.secs[sectName]
        for pointpName, pointpParams in sectParams['pointps'].items():
            # if self.tags['cellModel'] == pointpParams:  # only required if want to allow setting various cell models in same rule

            # warning: `pointpParams object is the same as `sec['pointps'][pointpName]` if came here from `loadNet()` (see also TODO there)
            # beware of implicit modification

            if pointpName not in sec['pointps']:
                sec['pointps'][pointpName] = Dict()
            loc = pointpParams['loc'] if 'loc' in pointpParams else 0.5  # set location
            Pointp = getattr(h, pointpParams['mod'])
            pointpObj = Pointp(loc, sec=sec['hObj'])  # create h Pointp object (eg. h.Izhi2007b)

            for pointpParamName, pointpParamValue in pointpParams.items():  # add params of the point process
                if pointpParamValue == 'gid':
                    pointpParamValue = self.gid
                if pointpParamName not in CellParams.pointpParamsReservedKeys() and not pointpParamName.startswith(
                    '_'
                ):
                    func, vars = CellParams.stringFuncAndVarsForMod(
                        cellType, sectName, 'pointps', pointpName, pointpParamName
                    )
                    if func:
                        pointpParamValue = self.__evaluateCellParamsStringFunc(func, vars, sec, cellVars=cellVars)
                    setattr(pointpObj, pointpParamName, pointpParamValue)
            if 'params' in self.tags.keys():  # modify cell specific params
                for pointpParamName, pointpParamValue in self.tags['params'].items():
                    setattr(pointpObj, pointpParamName, pointpParamValue)

            sec['pointps'][pointpName]['hObj'] = pointpObj

    def addSynMechNEURONObj(self, synMech, synMechLabel, synMechParams, sec, loc, preLoc=None):
        if not synMech.get('hObj'):  # if synMech doesn't have NEURON obj, then create
            synObj = getattr(h, synMechParams['mod'])
            synMech['hObj'] = synObj(loc, sec=sec['hObj'])  # create h Syn object (eg. h.Exp2Syn)
            for synParamName, synParamValue in synMechParams.items():  # add params of the synaptic mechanism
                if synParamName == 'selfNetcon':  # create self netcon required for some synapses (eg. homeostatic)
                    secLabelNetCon = synParamValue.get('sec', 'soma')
                    locNetCon = synParamValue.get('loc', 0.5)
                    secNetCon = self.secs.get(secLabelNetCon, None)
                    synMech['hObj'] = h.NetCon(secNetCon['hObj'](locNetCon)._ref_v, synMech[''], sec=secNetCon['hObj'])
                    for paramName, paramValue in synParamValue.items():
                        if paramName == 'weight':
                            synMech['hObj'].weight[0] = paramValue
                        elif paramName not in ['sec', 'loc']:
                            setattr(synMech['hObj'], paramName, paramValue)
                elif synParamName not in SynMechParams.reservedKeys():
                    func, vars = SynMechParams.stringFunctionAndVars(synMechLabel, synParamName)
                    if func:
                        synParamValue = self.__evaluateSynMechStringFuncs(func, vars, sec, loc, preLoc)
                    setattr(synMech['hObj'], synParamName, synParamValue)

    @staticmethod
    def stringFuncVarNames():
        return list(CompartCell.__stringFuncVarsEvaluators().keys())

    @staticmethod
    def stringFuncVarNamesForCellVars():
        # segment-specific vars are not applicable for cellVars
        return [v for v in CompartCell.stringFuncVarNames() if v not in ['dist_path', 'dist_euclidean']]

    @staticmethod
    def __stringFuncVarsEvaluators():
        return {
            'rand': lambda cell, dist, rand: rand,
            'dist_path': lambda cell, dist, rand: dist,
            'dist_euclidean': lambda cell, dist, rand: dist,
            'x': lambda cell, dist, rand: cell.tags['x'],
            'y': lambda cell, dist, rand: cell.tags['y'],
            'z': lambda cell, dist, rand: cell.tags['z'],
            'xnorm': lambda cell, dist, rand: cell.tags['xnorm'],
            'ynorm': lambda cell, dist, rand: cell.tags['ynorm'],
            'znorm': lambda cell, dist, rand: cell.tags['znorm'],
        }

    def __evaluateCellParamsStringFunc(self, func, varNames, sec=None, loc=0.5, cellVars={}):
        from ..network.subconn import pathDistance, posFromLoc

        args = {}
        for varName in varNames:
            if varName in cellVars:
                # cellVars are already evaluated
                args[varName] = cellVars[varName]
            else:
                # rest of vars should be evaluated
                if varName == 'dist_euclidean':
                    # euclidian distance
                    x0, y0, z0 = posFromLoc(self.originSec(), 0.5)
                    x, y, z = posFromLoc(sec, sec['hObj'](loc).x)
                    dist = sqrt((x - x0) ** 2 + (y - y0) ** 2 + (z - z0) ** 2)
                elif varName == 'dist_path':
                    # distance based on the topology
                    segOrigObj = self.originSec()['hObj'](0.5)
                    dist = pathDistance(segOrigObj, sec['hObj'](loc))
                else:
                    dist = None
                varEvaluator = CompartCell.__stringFuncVarsEvaluators()[varName]
                args[varName] = varEvaluator(self, dist, self._randomizer())
        # once vars are evaluated, evaluate function value
        return func(**args)

    def __evaluateSynMechStringFuncs(self, func, varNames, sec, loc, preLoc=None):
        from .. import sim
        from ..network.subconn import pathDistance, posFromLoc

        args = {}
        for varName in varNames:
            if not preLoc and varName in SynMechParams.stringFuncVarsReferringPreLoc():
                preLoc = 0.5
                if sim.cfg.verbose:
                    print('No preLoc for synMech string function provided. Defaulting to 0.5')
            if varName == 'post_dist_euclidean':
                # euclidian distance
                x0, y0, z0 = posFromLoc(self.originSec(), 0.5)
                x, y, z = posFromLoc(sec, sec['hObj'](loc).x)
                dist = sqrt((x - x0) ** 2 + (y - y0) ** 2 + (z - z0) ** 2)
            elif varName == 'post_dist_path':
                # distance based on the topology
                segOrigObj = self.originSec()['hObj'](0.5)
                dist = pathDistance(segOrigObj, sec['hObj'](loc))
            else:
                dist = None
            varEvaluator = SynMechParams.stringFuncVarsEvaluators()[varName]
            args[varName] = varEvaluator(self, dist, self._randomizer())

        return func(**args)

    def addSynMechsNEURONObj(self):
        # set params for all sections
        for sectName, sectParams in self.secs.items():
            sec = self.secs[sectName]  # pointer to section
            # add synMechs (only used when loading)
            if 'synMechs' in sectParams:
                for synMech in sectParams['synMechs']:
                    if 'label' in synMech and 'loc' in synMech:
                        synMechParams = sim.net.params.synMechParams.get(
                            synMech['label']
                        )  # get params for this synMech
                        self.addSynMechNEURONObj(synMech, synMech['label'], synMechParams, sec, synMech['loc'])

    # Create NEURON objs for conns and syns if included in prop (used when loading)
    def addStimsNEURONObj(self):
        # assumes python structure exists
        for stimParams in self.stims:
            if stimParams['type'] == 'NetStim':
                self.addNetStim(stimParams, stimContainer=stimParams)

            else:  # if stimParams['type'] in ['IClamp', 'VClamp', 'SEClamp', 'AlphaSynapse']:
                stim = getattr(h, stimParams['type'])(self.secs[stimParams['sec']]['hObj'](stimParams['loc']))
                stimProps = {
                    k: v for k, v in stimParams.items() if k not in ['label', 'type', 'source', 'loc', 'sec', 'hObj']
                }
                for stimPropName, stimPropValue in stimProps.items():  # set mechanism internal stimParams
                    if isinstance(stimPropValue, list):
                        if stimPropName == 'amp':
                            for i, val in enumerate(stimPropValue):
                                stim.amp[i] = val
                        elif stimPropName == 'dur':
                            for i, val in enumerate(stimPropValue):
                                stim.dur[i] = val
                        # setattr(stim, stimParamName._ref_[0], stimParamValue[0])
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
                synMech = next(
                    (
                        synMech
                        for synMech in self.secs[conn['sec']]['synMechs']
                        if synMech['label'] == conn['synMech'] and synMech['loc'] == conn['loc']
                    ),
                    None,
                )

            if not synMech:
                synMech = self.addSynMech(conn['synMech'], conn['sec'], conn['loc'])
                # continue  # go to next conn

            try:
                postTarget = synMech['hObj']
            except:
                print('\nError: no synMech available for conn: ', conn)
                print(' cell tags: ', self.tags)
                print(' cell synMechs: ', self.secs[conn['sec']]['synMechs'])
                import sys

                sys.exit()

            # create NetCon
            if conn['preGid'] == 'NetStim':
                netstim = next((stim['hObj'] for stim in self.stims if stim['source'] == conn['preLabel']), None)
                if netstim:
                    netcon = h.NetCon(netstim, postTarget)
                else:
                    continue
            else:
                # cell = next((c for c in sim.net.cells if c.gid == conn['preGid']), None)
                netcon = sim.pc.gid_connect(conn['preGid'], postTarget)

            netcon.weight[0] = conn['weight']
            netcon.delay = conn['delay']
            # netcon.threshold = conn.get('threshold', sim.net.params.defaultThreshold)
            conn['hObj'] = netcon

            # Add plasticity
            if conn.get('plast'):
                self._addConnPlasticity(conn['plast'], self.secs[conn['sec']], netcon, 0)

    @staticmethod
    def spikeGenLocAndSec(secs):

        sec = next(
            (secParams for secName, secParams in secs.items() if 'spikeGenLoc' in secParams), None
        )  # check if any section has been specified as spike generator
        if sec:
            loc = sec['spikeGenLoc']  # get location of spike generator within section
        else:
            # sec = self.secs['soma'] if 'soma' in self.secs else self.secs[self.secs.keys()[0]]  # use soma if exists, otherwise 1st section
            sec = next(
                (sec for secName, sec in secs.items() if len(sec['topol']) == 0), secs[list(secs.keys())[0]]
            )  # root sec (no parents)
            loc = 0.5
        return loc, sec

    def associateGid(self, threshold=None):
        from .. import sim

        if self.secs:
            if sim.cfg.createNEURONObj:
                if hasattr(sim, 'rank'):
                    sim.pc.set_gid2node(
                        self.gid, sim.rank
                    )  # this is the key call that assigns cell gid to a particular node
                else:
                    sim.pc.set_gid2node(self.gid, 0)
                loc, sec = CompartCell.spikeGenLocAndSec(self.secs)
                nc = None
                if 'pointps' in sec:  # if no syns, check if point processes with 'vref' (artificial cell)
                    for pointpName, pointpParams in sec['pointps'].items():
                        if 'vref' in pointpParams:
                            nc = h.NetCon(
                                getattr(sec['pointps'][pointpName]['hObj'], '_ref_' + pointpParams['vref']),
                                None,
                                sec=sec['hObj'],
                            )
                            break
                if not nc:  # if still haven't created netcon
                    nc = h.NetCon(sec['hObj'](loc)._ref_v, None, sec=sec['hObj'])
                if 'threshold' in sec:
                    threshold = sec['threshold']
                threshold = threshold if threshold is not None else sim.net.params.defaultThreshold
                nc.threshold = threshold
                sim.pc.cell(self.gid, nc, 1)  # associate a particular output stream of events
                del nc  # discard netcon
        sim.net.gid2lid[self.gid] = len(sim.net.gid2lid)

    def addSynMech(self, synLabel, secLabel, loc, preLoc=None):
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
                    synMech = next(
                        (
                            synMech
                            for synMech in sec['synMechs']
                            if synMech['label'] == synLabel and synMech['loc'] == loc
                        ),
                        None,
                    )
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
                    synMech = next(
                        (
                            synMech
                            for synMech in sec['synMechs']
                            if synMech['label'] == synLabel and synMech['loc'] == loc
                        ),
                        None,
                    )
                if not synMech:  # if still doesnt exist, then create
                    synMech = Dict()
                    sec['synMechs'].append(synMech)
                # add the NEURON object
                self.addSynMechNEURONObj(synMech, synLabel, synMechParams, sec, loc, preLoc)
            else:
                synMech = None
        else:
            synMech = None
        return synMech

    def modifySynMechs(self, params):
        from .. import sim

        conditionsMet = 1
        if 'cellConds' in params:
            conditionsMet = self.checkConditions(params['cellConds'])

        if conditionsMet:
            for secLabel, sec in self.secs.items():
                for synMech in sec['synMechs']:
                    conditionsMet = 1
                    if 'conds' in params:
                        # first check if section matches
                        secLabelInConds = params['conds'].get('sec')
                        if secLabelInConds and (secLabelInConds != secLabel):
                            # skip to next section
                            break

                        # then check the rest of conds
                        synMechConds = deepcopy(params['conds'])
                        synMechConds.pop('sec')
                        conditionsMet = sim.utils.checkConditions(synMechConds, against=synMech)

                    if conditionsMet:  # if all conditions are met, set values for this cell
                        exclude = ['conds', 'cellConds'] + SynMechParams.reservedKeys()
                        paramsToModify = {k: v for k, v in params.items() if k not in exclude}
                        for synParamName, synParamValue in paramsToModify.items():
                            if sim.cfg.createPyStruct:
                                synMech[synParamName] = synParamValue
                            if sim.cfg.createNEURONObj:
                                try:
                                    setattr(synMech['hObj'], synParamName, synParamValue)
                                except:
                                    print('Error setting %s=%s on synMech' % (synParamName, str(synParamValue)))

    def addConn(self, params, netStimParams=None):
        from .. import sim

        # try getting params of pointer-based connection (if applicable)
        pointerParams, isPreToPostPointerConn = self.__parsePointerParams(params)

        if pointerParams and not pointerParams['bidirectional'] and not isPreToPostPointerConn:
            # If this is a second iteration and connection is unidirectional (pre->post only), use appropriate variable of this cell (normally, voltage)
            # as a source of pointer connection.
            # see comments in `__parsePointerParams()` for more details
            sec = self.secs[params['sec']]
            self.__setPointerSource(pointerParams['source_var'], pointerParams['postToPreId'], sec, params['loc'])
            return  # the rest was already done on postCell side (firs step)

        # threshold = params.get('threshold', sim.net.params.defaultThreshold)  # depreacated -- use threshold in preSyn cell sec
        if params.get('weight') is None:
            params['weight'] = sim.net.params.defaultWeight  # if no weight, set default
        if params.get('delay') is None:
            params['delay'] = sim.net.params.defaultDelay  # if no delay, set default
        if params.get('preLoc') is None:
            params['preLoc'] = 0.5  # if no preLoc, set default

        # same logic for `loc` is no longer here, it will be processed later in `_setConnSynMechs()` (see `isExplicitLoc` there)

        if params.get('synsPerConn') is None:
            params['synsPerConn'] = 1  # if no synsPerConn, set default

        # Get list of section labels
        secLabels = self._setConnSections(params)
        if secLabels == -1:
            return  # if no section available exit func

        # Warning or error if self connections
        if params['preGid'] == self.gid:
            # Only allow self connections if option selected by user
            # !!!! AD HOC RULE FOR HNN!!! -  or 'soma' in secLabels and not self.tags['cellType'] == 'L5Basket' (removed)
            if sim.cfg.allowSelfConns:
                if sim.cfg.verbose:
                    print(
                        '  Warning: creating self-connection on cell gid=%d, section=%s '
                        % (self.gid, params.get('sec'))
                    )
            else:
                if sim.cfg.verbose:
                    print(
                        '  Error: attempted to create self-connection on cell gid=%d, section=%s '
                        % (self.gid, params.get('sec'))
                    )
                return  # if self-connection return

        # Weights and delays:
        weights, delays = self._connWeightsAndDelays(params, netStimParams)

        weightIndex = 0  # set default weight matrix index

        # Check if target is point process (artificial cell) with V not in section
        pointp, weightIndex = self._setConnPointP(params, secLabels, weightIndex)
        if pointp == -1:
            return

        # Add synaptic mechanisms
        if not pointp:  # check not a point process
            synMechs, synMechSecs, synMechLocs = self._setConnSynMechs(params, secLabels)
            if synMechs == -1:
                return

            # Adapt weight based on section weightNorm (normalization based on section location)
            for i, (sec, loc) in enumerate(zip(synMechSecs, synMechLocs)):
                if 'weightNorm' in self.secs[sec] and isinstance(self.secs[sec]['weightNorm'], list):
                    nseg = self.secs[sec]['geom']['nseg']
                    weights[i] = weights[i] * self.secs[sec]['weightNorm'][int(round(loc * nseg)) - 1]

        # Create connections
        for i in range(params['synsPerConn']):
            if not sim.cfg.allowConnsWithWeight0 and weights[i] == 0.0:
                continue

            if netStimParams:
                netstim = self.addNetStim(netStimParams)

            if pointerParams:
                if isPreToPostPointerConn:
                    # generate new ids
                    # TODO: will it even works with synsPerConn > 1? (in particular, loc in params now can be None)
                    preToPostPointerId, postToPrePointerId = self.__generatePointerIds(pointerParams, params)
                else:
                    # use pre-generated
                    preToPostPointerId = pointerParams['preToPostId']
                    postToPrePointerId = pointerParams.get('postToPreId')

            # Python Structure
            if sim.cfg.createPyStruct:
                connParams = {k: v for k, v in params.items() if k not in ['synsPerConn']}
                connParams['weight'] = weights[i]
                connParams['delay'] = delays[i]
                if not pointp:
                    connParams['sec'] = synMechSecs[i]
                    connParams['loc'] = synMechLocs[i]
                if netStimParams:
                    connParams['preGid'] = 'NetStim'
                    connParams['preLabel'] = netStimParams['source']
                if pointerParams:
                    connParams['hObj'] = synMechs[i]['hObj']
                    connParams['pointer'] = {
                        'id': preToPostPointerId,
                        'source': 'pre' if isPreToPostPointerConn else 'post',
                        'sourceVar': pointerParams['source_var'],
                        'targetVar': pointerParams['target_var'],
                    }
                    if postToPrePointerId is not None:
                        connParams['pointer']['reverseConnId'] = postToPrePointerId

                self.conns.append(Dict(connParams))
            else:  # do not fill in python structure (just empty dict for NEURON obj)
                self.conns.append(Dict())

            # NEURON objects
            if sim.cfg.createNEURONObj:
                # pointer-based connection (e.g. gap junctions)
                if pointerParams:
                    sec = self.secs[synMechSecs[i]]
                    netcon = None
                    # set appropriate synMech's variable as target of pointer connection (see comments in `__parsePointerParams()` for more details)
                    self.__setPointerTarget(pointerParams['target_var'], preToPostPointerId, synMechs[i], weights[i])
                    if postToPrePointerId is not None:  # i.e. connection is bidirectional
                        # set this cell as a source of inverse pointer connection
                        self.__setPointerSource(pointerParams['source_var'], postToPrePointerId, sec, synMechLocs[i])
                # connections using NetCons
                else:
                    if pointp:
                        sec = self.secs[secLabels[0]]
                        postTarget = sec['pointps'][pointp]['hObj']  #  local point neuron
                    else:
                        sec = self.secs[synMechSecs[i]]
                        postTarget = synMechs[i]['hObj']  # local synaptic mechanism

                    if netStimParams:
                        netcon = h.NetCon(netstim, postTarget)  # create Netcon between netstim and target
                    else:
                        netcon = sim.pc.gid_connect(
                            params['preGid'], postTarget
                        )  # create Netcon between global gid and target

                    netcon.weight[weightIndex] = weights[i]  # set Netcon weight
                    netcon.delay = delays[i]  # set Netcon delay
                    # netcon.threshold = threshold  # set Netcon threshold
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
                    switchpairs = list(zip(switchiter, switchiter))
                    for pair in switchpairs:
                        # Note: Cliff's makestim code is in seconds, so conversions from ms to s occurs in the args.
                        stimvecs = self._shapeStim(
                            width=float(pulsewidth) / 1000.0,
                            isi=float(pulseperiod) / 1000.0,
                            weight=params['weight'],
                            start=float(pair[0]) / 1000.0,
                            finish=float(pair[1]) / 1000.0,
                            stimshape=pulsetype,
                        )
                        temptimevecs.extend(stimvecs[0])
                        tempweightvecs.extend(stimvecs[1])

                    self.conns[-1]['shapeTimeVec'] = h.Vector().from_python(temptimevecs)
                    self.conns[-1]['shapeWeightVec'] = h.Vector().from_python(tempweightvecs)
                    self.conns[-1]['shapeWeightVec'].play(
                        netcon._ref_weight[weightIndex], self.conns[-1]['shapeTimeVec']
                    )

                # Add plasticity
                self._addConnPlasticity(params, sec, netcon, weightIndex)

            if sim.cfg.verbose:
                sec = params['sec'] if pointp else synMechSecs[i]
                loc = params['loc'] if pointp else synMechLocs[i]
                preGid = netStimParams['source'] + ' NetStim' if netStimParams else params['preGid']
                try:
                    print(
                        (
                            '  Created connection preGid=%s, postGid=%s, sec=%s, loc=%.4g, synMech=%s, weight=%.4g, delay=%.2f'
                            % (preGid, self.gid, sec, loc, params['synMech'], weights[i], delays[i])
                        )
                    )
                except:
                    print(('  Created connection preGid=%s' % (preGid)))

    def __parsePointerParams(self, params):
        from .. import sim

        # Establishing pointer connection requires two steps, performed in separate iterations of `addConn()`
        # On first step, appropriate variable of current postsynaptic cell's synapse is used as a target for forward pointer connection (pre->post),
        # Additionally, if connection is bidirectional, variable of current cell (normally, voltage) is used as a source of reverse connection (post->pre).
        # On the second step, variable of presynaptic cell is used as a source of forward connection,
        # and if connection is bidirectional, var of synapse of presynaptic cell is set as a target of reverse connection.

        # Try getting prepopulated params, created on previous step. If it's there, then this is the second step.
        if '__preCellSidePointerParams__' in params:
            return params['__preCellSidePointerParams__'], False

        # if no, this is the first step. Try getting pointer params from synMechParams
        synLabel = params['synMech']
        synMech = sim.net.params.synMechParams.get(synLabel, {})
        pointerParams = synMech.get('pointerParams', None)

        # if no, try to get from connParams (deprecated) for backward compatibility
        if pointerParams is None and params.get('gapJunction'):
            pointerParams = {'source_var': 'v', 'target_var': 'vpeer'}

        # populate absent params with default values
        if isinstance(pointerParams, dict):
            if 'source_var' not in pointerParams:
                pointerParams['source_var'] = 'v'
            if 'bidirectional' not in pointerParams:
                pointerParams['bidirectional'] = True

        return pointerParams, True

    def __generatePointerIds(self, pointerParams, params):
        from .. import sim
        # see comments in `__parsePointerParams()` for more details

        if sim.net.lastPointerId > sim.net.maxPointerIdForGivenNode:
            print(f"WARNING: potential overflow of pointer connection id!")
        preToPostId = sim.net.lastPointerId
        sim.net.lastPointerId += 1  # keep track of num of gap juncs in this node

        if pointerParams['bidirectional']:
            postToPreId = preToPostId + 1  # global index for postsyn gap junc
            sim.net.lastPointerId += 1  # keep track of num of gap juncs in this node
        else:
            postToPreId = None

        # save to be used on second step (see comments in `__parsePointerParams()` above)
        preCellSideParams = deepcopy(pointerParams)
        # at the preCell side, source and target are swapped
        preCellSideParams['postToPreId'] = preToPostId
        if postToPreId is not None:  # i.e. connection is bidirectional
            preCellSideParams['preToPostId'] = postToPreId

        preGapParams = {
            'gid': params['preGid'],
            'preGid': self.gid,
            'sec': params.get('preSec', 'soma'),
            'loc': params.get('preLoc', 0.5),
            'preSec': params.get('sec', 'soma'),
            'preLoc': params.get('loc', 0.5),
            'weight': params.get('weight', 0.0),
            'synMech': params['synMech'],
            '__preCellSidePointerParams__': preCellSideParams,
        }

        if not getattr(sim.net, 'preCellPointerConns', False):
            sim.net.preCellPointerConns = (
                []
            )  # if doesn't exist, create list to store pointer connections targeting presynaptic cells
        sim.net.preCellPointerConns.append(preGapParams)

        return preToPostId, postToPreId

    def __setPointerTarget(self, ref, id, synMech, weight):
        synObj = synMech['hObj']
        try:  # weight is optional
            synObj.weight = weight
        except:
            pass
        targetVar = getattr(synObj, '_ref_' + ref)
        sim.pc.target_var(synObj, targetVar, id)

    def __setPointerSource(self, ref, id, sec, loc):
        secObj = sec['hObj']
        sourceVar = getattr(secObj(loc), '_ref_' + ref)
        secObj.push()
        sim.pc.source_var(sourceVar, id)
        h.pop_section()

    def modifyConns(self, params):
        from .. import sim

        for conn in self.conns:
            conditionsMet = 1

            if 'conds' in params:
                conds = params['conds']

                # `conds` may contain `postGid` key, which is deprecated in favour of having `gid` key in `postConds`,
                # but for backward compatibility, try to detect it here and replace with `gid`, so checkConditions() can process it:
                if 'postGid' in conds:
                    conds['gid'] = conds.pop('postGid')
                conditionsMet = sim.utils.checkConditions(conds, against=conn, cellGid=self.gid)

            if conditionsMet and 'postConds' in params:
                conditionsMet = self.checkConditions(params['postConds'])

            if conditionsMet and 'preConds' in params:
                try:
                    cell = sim.net.cells[conn['preGid']]
                    if cell:
                        conditionsMet = cell.checkConditions(params['preConds'])
                except:
                    pass
                    # print('Warning: modifyConns() does not yet support conditions of presynaptic cells when running parallel sims')

            if conditionsMet:  # if all conditions are met, set values for this cell
                if sim.cfg.createPyStruct:
                    for paramName, paramValue in {
                        k: v for k, v in params.items() if k not in ['conds', 'preConds', 'postConds']
                    }.items():
                        conn[paramName] = paramValue
                if sim.cfg.createNEURONObj:
                    for paramName, paramValue in {
                        k: v for k, v in params.items() if k not in ['conds', 'preConds', 'postConds']
                    }.items():
                        try:
                            if paramName == 'weight':
                                conn['hObj'].weight[0] = paramValue
                            else:
                                setattr(conn['hObj'], paramName, paramValue)
                        except:
                            print('Error setting %s=%s on Netcon' % (paramName, str(paramValue)))

    def modifyStims(self, params):
        from .. import sim

        conditionsMet = 1
        if 'cellConds' in params:
            if conditionsMet:
                conditionsMet = self.checkConditions(params['cellConds'])

        if conditionsMet == 1:
            for stim in self.stims:
                conditionsMet = 1

                if 'conds' in params:
                    conditionsMet = sim.utils.checkConditions(params['conds'], against=stim)

                if conditionsMet:  # if all conditions are met, set values for this cell
                    if stim['type'] == 'NetStim':  # for netstims, find associated netcon
                        conn = next((conn for conn in self.conns if conn['source'] == stim['source']), None)
                    if sim.cfg.createPyStruct:
                        for paramName, paramValue in {
                            k: v for k, v in params.items() if k not in ['conds', 'cellConds']
                        }.items():
                            if stim['type'] == 'NetStim' and paramName in ['weight', 'delay']:
                                conn[paramName] = paramValue
                            else:
                                stim[paramName] = paramValue
                    if sim.cfg.createNEURONObj:
                        for paramName, paramValue in {
                            k: v for k, v in params.items() if k not in ['conds', 'cellConds']
                        }.items():
                            try:
                                if stim['type'] == 'NetStim':
                                    if paramName == 'weight':
                                        conn['hObj'].weight[0] = paramValue
                                    elif paramName in ['delay']:
                                        setattr(conn['hObj'], paramName, paramValue)
                                    elif paramName in ['rate']:
                                        stim['interval'] = 1.0 / paramValue
                                        setattr(stim['hObj'], 'interval', stim['interval'])
                                    elif paramName in ['interval']:
                                        stim['rate'] = 1.0 / paramValue
                                        setattr(stim['hObj'], 'interval', stim['interval'])
                                    else:
                                        setattr(stim['hObj'], paramName, paramValue)
                                else:
                                    setattr(stim['hObj'], paramName, paramValue)
                            except:
                                print('Error setting %s=%s on stim' % (paramName, str(paramValue)))

    def addStim(self, params):
        from .. import sim

        if not params['sec'] or (
            isinstance(params['sec'], basestring)
            and not params['sec'] in list(self.secs.keys()) + list(self.secLists.keys())
        ):
            if sim.cfg.verbose:
                print(
                    '  Warning: no valid sec specified for stim on cell gid=%d so using soma or 1st available. Existing secs: %s; params: %s'
                    % (self.gid, list(self.secs.keys()), params)
                )
            if 'soma' in self.secs:
                params['sec'] = 'soma'  # use 'soma' if exists
            elif self.secs:
                params['sec'] = list(self.secs.keys())[0]  # if no 'soma', use first sectiona available
            else:
                if sim.cfg.verbose:
                    print('  Error: no Section available on cell gid=%d to add stim' % (self.gid))
                return

        if not 'loc' in params:
            params['loc'] = 0.5  # default stim location

        if params['type'] == 'NetStim':
            if not 'start' in params:
                params['start'] = 0  # add default start time
            if not 'number' in params:
                params['number'] = 1e9  # add default number

            connParams = {
                'preGid': params['type'],
                'sec': params.get('sec'),
                'loc': params.get('loc'),
                'synMech': params.get('synMech'),
                'weight': params.get('weight'),
                'delay': params.get('delay'),
                'synsPerConn': params.get('synsPerConn'),
            }

            # if 'threshold' in params: connParams['threshold'] = params.get('threshold')   # depreacted, set threshold in preSyn cell
            if 'shape' in params:
                connParams['shape'] = params.get('shape')
            if 'plast' in params:
                connParams['plast'] = params.get('plast')

            netStimParams = {
                'source': params['source'],
                'type': params['type'],
                'rate': params['rate'] if 'rate' in params else 1000.0 / params['interval'],
                'noise': params['noise'] if 'noise' in params else 0.0,
                'number': params['number'],
                'start': params['start'],
                'seed': params['seed'] if 'seed' in params else sim.cfg.seeds['stim'],
            }

            self.addConn(connParams, netStimParams)

        elif params['type'] in ['IClamp', 'VClamp', 'SEClamp', 'AlphaSynapse']:
            sec = self.secs[params['sec']]
            stim = getattr(h, params['type'])(sec['hObj'](params['loc']))
            stimParams = {k: v for k, v in params.items() if k not in ['type', 'source', 'loc', 'sec', 'label']}
            stringParams = ''
            for stimParamName, stimParamValue in stimParams.items():  # set mechanism internal params
                if isinstance(stimParamValue, list):
                    if stimParamName == 'amp':
                        for i, val in enumerate(stimParamValue):
                            stim.amp[i] = val
                    elif stimParamName == 'dur':
                        for i, val in enumerate(stimParamValue):
                            stim.dur[i] = val
                    # setattr(stim, stimParamName._ref_[0], stimParamValue[0])
                else:
                    setattr(stim, stimParamName, stimParamValue)
                    stringParams = stringParams + ', ' + stimParamName + '=' + str(stimParamValue)
            self.stims.append(Dict(params))  # add to python structure
            self.stims[-1]['hObj'] = stim  # add stim object to dict in stims list

            if sim.cfg.verbose:
                print(
                    (
                        '  Added %s %s to cell gid=%d, sec=%s, loc=%.4g%s'
                        % (params['source'], params['type'], self.gid, params['sec'], params['loc'], stringParams)
                    )
                )

        elif params['type'] == 'XStim':

            # Addition of extracellular mechanism in all sections/segments
            segCoords = params['segCoords']
            r05 = (segCoords['p0'] + segCoords['p1']) / 2
            nseg = r05.shape[1]

            ## OPTIONS ABOUT EXTRACELLULAR STIMULATION
            if isinstance(params['field'],dict):
                if params['field']['class'] == 'pointSource':
                    from math import pi

                    if 'sigma' in  params['field']:
                        sigma = params['field']['sigma']
                    else:
                        sigma = 0.3  # mS/mm   --- same value used in LFP calculations

                    if 'location' in  params['field']:
                        electrodePos = params['field']['location']
                    else:
                        print(" Electrode position not defined for extracellular stimulation")
                        # set at the midpoint
                        electrodePos = [sim.net.params.sizeX/2, -sim.net.params.sizeY/2, sim.net.params.sizeZ/2]

                    # transfer resistance
                    tr = np.zeros(nseg)          # single electrode (for now)

                    # Segment position relative to the point source                
                    rel_05 = r05 - np.expand_dims(electrodePos, axis=1)
                    r2 = np.einsum('ij,ij->j', rel_05, rel_05)  # compute dot product column-wise, the resulting array has as many columns as original
                    r = np.sqrt(r2)
                    tr += 1. / r
                    tr *= 1 / (4 * pi * sigma)

                elif params['field']['class'] == 'uniform':
                    from math import pi

                    # set a nominal transfer resistance based on the shortcut depicted by Ted Carnevale
                    # see discussion in https://www.neuron.yale.edu/phpbb/viewtopic.php?p=20131&hilit=Applying+Sinusoidal+Voltage+to+Membrane#p20131
                    # and relevant code in https://modeldb.science/239006
                    # BUT ... the direction of the field is incorporated here (transfer resistance is a scalar value)

                    if 'referencePoint' in  params['field']:
                        referencePoint = params['field']['referencePoint']
                    else:
                        # set at the midpoint
                        referencePoint = [sim.net.params.sizeX/2, -sim.net.params.sizeY/2, sim.net.params.sizeZ/2]

                    if 'fieldDirection' in  params['field']:
                        phi, theta = [val*pi/180 for val in params['field']['fieldDirection']]
                    else:
                        # default values
                        phi, theta = [val*pi/180 for val in [0, 180]]    # vertical field, pointing down 

                    # transfer resistance
                    tr = np.zeros(nseg)          # single electrode (for now)

                    # Segment position relative to the point source                
                    rel_05 = r05 - np.expand_dims(referencePoint, axis=1)
                    Ex = sin(theta)*cos(phi)
                    Ey = cos(theta)
                    Ez = sin(theta)*sin(phi)
                    E_field = np.expand_dims([Ex, Ey, Ez], axis=1)
                    tr = np.einsum('ij,ij->j', E_field, rel_05)  # compute dot product column-wise, the resulting array has as many columns as original
                    tr *= 1e-9
                else:
                    print(" Extracellular stimulation not defined")

            else:
                print(" Extracellular stimulation not defined")

            ## Addition of extracellular mechanisms in all segments
            ## Running through all segments
            nseg = 0
            self.hvec = []
            for secLabel,sec in self.secs.items():

                hSec = sec['hObj']
                hSec.push()

                if not h.ismembrane('extracellular',sec = hSec): 
                    hSec.insert('extracellular')

                    # if the extracellular mechanism is associated to the xtra.mod, then
                    if 'mod_based' in params and params['mod_based']==True:
                        hSec.insert('xtra')
                    else:
                        # not using .mod
                        # saving in case we have multiple stimulations (only defined with params['mod_based'] == False)
                        self.secs[secLabel]['geom']['xtra_stim'] = []

                        # for development (only saves properly for single stimulation)
                        #self.secs[secLabel]['geom'].update({'r05':[]})
                        #self.secs[secLabel]['geom'].update({'rel_05':[]})
                        #self.secs[secLabel]['geom'].update({'tr':[]})

                    #h.psection(hSec)

                    for ns, seg in enumerate(hSec):

                        # if the extracellular mechanism is associated to the xtra.mod, then
                        if 'mod_based' in params and params['mod_based']==True:
                            # using xtra.mod - link extracellular and xtra
                            sourceVar = seg.xtra._ref_ex
                            targetVar = seg._ref_e_extracellular
                            sim.pc.source_var(sourceVar, sim.net.lastPointerId)
                            sim.pc.target_var(targetVar, sim.net.lastPointerId)
                            sim.net.lastPointerId += 1

                            # # setting coordinates in xtra (not neccesary)
                            # seg.xtra.x = r05[0,nseg]
                            # seg.xtra.y = r05[1,nseg]
                            # seg.xtra.z = r05[2,nseg]

                            # # setting transfer resistance in xtra
                            seg.xtra.rx = tr[nseg]

                        else:
                            # not using .mod
                            #self.secs[secLabel]['geom']['r05'].append(r05[:,nseg])
                            #self.secs[secLabel]['geom']['rel_05'].append(rel_05[:,nseg])
                            #self.secs[secLabel]['geom']['tr'].append(tr[nseg])

                            vec = [val*tr[nseg]*(1e6) for val in params['stim']]
                            hStim = h.Vector(vec)  # add stim object to dict in stims list

                            self.stims.append(Dict(params))  # add to python structure
                            self.stims[-1]['sec_xtra'] = secLabel
                            self.stims[-1]['seg_xtra'] = ns
                            self.stims[-1]['hObj'] = hStim

                            self.secs[secLabel]['geom']['xtra_stim'].append({})
                            self.secs[secLabel]['geom']['xtra_stim'][ns].update({'vec' : vec, 
                                                                                 'stim_index': len(self.stims)-1})

                            self.hvec.append(hStim)
                            self.hvec[nseg].play(seg._ref_e_extracellular, params['time'],1)

                        nseg += 1

                else: ## Extracellular mechanism already inserted: Putatively multiple stimulation
                    #print("Multiple stimulation")
                    for ns, seg in enumerate(hSec):

                        vec_previous = self.secs[secLabel]['geom']['xtra_stim'][ns]['vec']
                        vec_new = [val*tr[nseg]*(1e6) for val in params['stim']]
                        if len(vec_previous)==len(vec_new):
                            vec = [vec_previous[ii] + vec_new[ii] for ii in range(len(vec_new))]
                        else:
                            print('Loading multiple Xtra stimulation failed')
                            vec = vec_previous
                        
                        # saving in case we have more multiple stimulations
                        #self.secs[secLabel]['geom']['xtra_stim'][ns].update({'old_vec': vec_previous})
                        self.secs[secLabel]['geom']['xtra_stim'][ns]['vec'] = vec

                        # update the value in the vector to be play for extracellular stimulation
                        for index in range(len(vec)):
                            nst = self.secs[secLabel]['geom']['xtra_stim'][ns]['stim_index']
                            self.stims[nst]['hObj'].x[index] = vec[index]

                        nseg += 1

                h.pop_section()

            #print(nseg)
            if nseg != r05.shape[1]:
                print('We have an issue setting extracellular mechanism at segments')

        else:
            if sim.cfg.verbose:
                print(('Adding exotic stim (NeuroML 2 based?): %s' % params))
            sec = self.secs[params['sec']]
            stim = getattr(h, params['type'])(sec['hObj'](params['loc']))
            stimParams = {k: v for k, v in params.items() if k not in ['type', 'source', 'loc', 'sec', 'label']}
            stringParams = ''
            for stimParamName, stimParamValue in stimParams.items():  # set mechanism internal params
                if isinstance(stimParamValue, list):
                    print("Can't set point process paramaters of type vector eg. VClamp.amp[3]")
                    pass
                    # setattr(stim, stimParamName._ref_[0], stimParamValue[0])
                elif 'originalFormat' in params and stimParamName == 'originalFormat':
                    if params['originalFormat'] == 'NeuroML2_stochastic_input':
                        if sim.cfg.verbose:
                            print(('   originalFormat: %s' % (params['originalFormat'])))

                        rand = h.Random()
                        stim_ref = params['label'][: params['label'].rfind(self.tags['pop'])]

                        # e.g. Stim3_2_popPyrS_2_soma_0_5 -> 2
                        index_in_stim = int(stim_ref.split('_')[-2])
                        stim_id = stim_ref.split('_')[0]
                        sim._init_stim_randomizer(rand, stim_id, index_in_stim, sim.cfg.seeds['stim'])
                        rand.negexp(1)
                        stim.noiseFromRandom(rand)
                        params['h%s' % params['originalFormat']] = rand
                else:
                    if stimParamName in ['weight']:
                        setattr(stim, stimParamName, stimParamValue)
                        stringParams = stringParams + ', ' + stimParamName + '=' + str(stimParamValue)
                    else:
                        setattr(stim, stimParamName, stimParamValue)

            self.stims.append(params)  # add to python structure
            self.stims[-1]['hObj'] = stim  # add stim object to dict in stims list
            if sim.cfg.verbose:
                print(
                    (
                        '  Added %s %s to cell gid=%d, sec=%s, loc=%.4g%s'
                        % (params['source'], params['type'], self.gid, params['sec'], params['loc'], stringParams)
                    )
                )

    def _setConnSections(self, params):
        from .. import sim

        # if no section specified or single section specified does not exist
        if not params.get('sec') or (
            isinstance(params.get('sec'), basestring)
            and not params.get('sec') in list(self.secs.keys()) + list(self.secLists.keys())
        ):
            if sim.cfg.verbose:
                print(
                    '  Warning: no valid sec specified for connection to cell gid=%d so using soma or 1st available'
                    % (self.gid)
                )
            if 'soma' in self.secs:
                params['sec'] = 'soma'  # use 'soma' if exists
            elif self.secs:
                params['sec'] = list(self.secs.keys())[0]  # if no 'soma', use first sectiona available
            else:
                if sim.cfg.verbose:
                    print('  Error: no Section available on cell gid=%d to add connection' % (self.gid))
                sec = -1  # if no Sections available print error and exit
                return sec

            secLabels = [params['sec']]

        # if sectionList or list of sections
        elif isinstance(params.get('sec'), list) or params.get('sec') in self.secLists:
            secList = list(params['sec']) if isinstance(params['sec'], list) else list(self.secLists[params['sec']])
            secLabels = []
            for i, section in enumerate(secList):
                if section not in self.secs:  # remove sections that dont exist; and corresponding weight and delay
                    if sim.cfg.verbose:
                        print(
                            '  Error: Section %s not available so removing from list of sections for connection to cell gid=%d'
                            % (section, self.gid)
                        )
                    secList.remove(section)
                    if isinstance(params['weight'], list):
                        params['weight'].remove(params['weight'][i])
                    if isinstance(params['delay'], list):
                        params['delay'].remove(params['delay'][i])

                else:
                    secLabels.append(section)

        # if section is string
        else:
            secLabels = [params['sec']]

        return secLabels

    def _setConnPointP(self, params, secLabels, weightIndex):
        from .. import sim

        # Find if any point process with V not calculated in section (artifical cell, eg. Izhi2007a)
        pointp = None
        if (
            len(secLabels) == 1 and 'pointps' in self.secs[secLabels[0]]
        ):  #  check if point processes with 'vref' (artificial cell)
            for pointpName, pointpParams in self.secs[secLabels[0]]['pointps'].items():
                if 'vref' in pointpParams:  # if includes vref param means doesn't use Section v or synaptic mechanisms
                    pointp = pointpName
                    if 'synList' in pointpParams:
                        if params.get('synMech') in pointpParams['synList']:
                            if isinstance(params.get('synMech'), list):
                                weightIndex = [
                                    pointpParams['synList'].index(synMech) for synMech in params.get('synMech')
                                ]
                            else:
                                weightIndex = pointpParams['synList'].index(
                                    params.get('synMech')
                                )  # udpate weight index based pointp synList

        if pointp and params['synsPerConn'] > 1:  # only single synapse per connection rule allowed
            if sim.cfg.verbose:
                print(
                    '  Error: Multiple synapses per connection rule not allowed for cells where V is not in section (cell gid=%d) '
                    % (self.gid)
                )
            return -1, weightIndex

        return pointp, weightIndex

    def _setConnSynMechs(self, params, secLabels):
        from .. import sim
        connRandomSecFromList = params.get('connRandomSecFromList', sim.cfg.connRandomSecFromList)
        distributeSynsUniformly = params.get('distributeSynsUniformly', sim.cfg.distributeSynsUniformly)

        synsPerConn = params['synsPerConn']
        if not params.get('synMech'):
            if sim.net.params.synMechParams:  # if no synMech specified, but some synMech params defined
                # select first synMech from net params and add syn:
                synLabel = list(sim.net.params.synMechParams.keys())[0] 
                params['synMech'] = synLabel
                if sim.cfg.verbose:
                    print(
                        '  Warning: no synaptic mechanisms specified for connection to cell gid=%d so using %s '
                        % (self.gid, synLabel)
                    )
            else:  # if no synaptic mechanism specified and no synMech params available
                _ensure(False, params, f"no synaptic mechanisms available to add conn on cell gid={self.gid}")

        # make difference between loc explicitly specified by user vs set by default
        if params.get('loc') is None:
            params['loc'] = 0.5
            isExplicitLoc = False
        else:
            isExplicitLoc = True

        if synsPerConn > 1:  # if more than 1 synapse
            synMechSecs, synMechLocs = self._secsAndLocsForMultisynapse(params, isExplicitLoc, secLabels, connRandomSecFromList, distributeSynsUniformly)
        else:  # if 1 synapse
            synMechSecs, synMechLocs = self._secsAndLocsForSingleSynapse(params, secLabels, connRandomSecFromList)

        # add synaptic mechanism to section based on synMechSecs and synMechLocs (if already exists won't be added unless nonLinear set to True)
        synMechs = []
        for i in range(synsPerConn):
            synMech = self.addSynMech(synLabel=params['synMech'], secLabel=synMechSecs[i], loc=synMechLocs[i], preLoc=params['preLoc'])
            synMechs.append(synMech)
        return synMechs, synMechSecs, synMechLocs

    def _secsAndLocsForSingleSynapse(self, params, secLabels, connRandomSecFromList):

        # by default place on 1st section of list and location available
        synMechSecs = secLabels
        loc = params['loc']
        synMechLocs = loc if isinstance(loc, list) else [loc]

        # randomize the section to connect to and move it to beginning of list
        if connRandomSecFromList and len(synMechSecs) > 1:
            if len(synMechLocs) > 1: # if loc was specified as list, its length should match the number of sections
                _ensure(len(synMechSecs) == len(synMechLocs), params, "With connRandomSecFromList == True and synsPerConn == 1 (defaults), the lengths of the list of locations and the list of sections must be the same, in order to use the same randomly generated index for both")
            else: # for single loc (or 1-element list), adjust it to match the number of sections
                synMechLocs = synMechLocs * len(synMechSecs)

            rand = h.Random()
            preGid = params['preGid'] if isinstance(params['preGid'], int) else 0
            rand.Random123(sim.hashStr('connSynMechsSecs'), self.gid, preGid)  # initialize randomizer
            pos = int(rand.discunif(0, len(synMechSecs) - 1))
            synMechSecs = [synMechSecs[pos]]
            synMechLocs = [synMechLocs[pos]]
        return synMechSecs, synMechLocs

    def _secsAndLocsForMultisynapse(self, params, isExplicitLoc, secLabels, connRandomSecFromList, distributeSynsUniformly):

        synsPerConn = params['synsPerConn']
        loc = params['loc']
    
        if len(secLabels) == 1:  # if single section, create all syns there
            synMechSecs = [secLabels[0]] * synsPerConn  # same section for all
            if isinstance(loc, list):
                _ensure(len(loc) == synsPerConn, params, "The length of the list of locations does not match synsPerConn")
                synMechLocs = loc
            else: # single value or no value
                _ensure(isExplicitLoc == False, params, f"specifiyng the `loc` as single value when synsPerConn > 1 ({synsPerConn} in your case) is deprecated. To silence this warning, remove `loc` from the connection parameters (locations will be distributed uniformly along the section) or provide a list of {synsPerConn} values (or list of such lists, if your connParams has multiple synMechs).")
                synMechLocs = [i / synsPerConn + 1 / synsPerConn / 2 for i in range(synsPerConn)]
        else:
            # if multiple sections, distribute syns uniformly
            if distributeSynsUniformly:
                _ensure(isExplicitLoc == False, params, f"specifiyng the `loc` explicitly when distributeSynsUniformly is True (default) and multiple sections are provided is deprecated. To silence this warning, remove `loc` from the connection parameters or set distributeSynsUniformly to False.")
                synMechSecs, synMechLocs = self._distributeSynsUniformly(secList=secLabels, numSyns=synsPerConn)
            else:
                if connRandomSecFromList:
                    synMechSecs, synMechLocs = self._randomSecAndLocFromList(params, synsPerConn, secLabels, loc, isExplicitLoc)
                else:
                    # Deterministic. Need to have lists of secs and locs that matches num syns
                    if not isinstance(loc, list):
                        loc = [loc] * synsPerConn

                    _ensure(synsPerConn == len(secLabels), params,
                            f"With connRandomSecFromList = False, the length of the list of sections should match synsPerConn")
                    _ensure(synsPerConn == len(loc), params, 
                            f"The length of the list of locations does not match synsPerConn (with distributeSynsUniformly = False, connRandomSecFromList = False)")

                    synMechSecs = secLabels
                    synMechLocs = loc
        return synMechSecs, synMechLocs

    def _randomSecAndLocFromList(self, params, synsPerConn, secLabels, loc, isExplicitLoc):
        rand = h.Random()
        preGid = params['preGid'] if isinstance(params['preGid'], int) else 0
        rand.Random123(sim.hashStr('connSynMechsSecs'), self.gid, preGid)  # initialize randomizer

        from ..network.conn import randInt
        maxval = len(secLabels) - 1
        isUnique = synsPerConn <= maxval + 1
        randSecPos = randInt(rand, N=synsPerConn, vmin=0, vmax=maxval, unique=isUnique)
        synMechSecs = [secLabels[i] for i in randSecPos]

        if isinstance(loc, list):
            maxval = len(loc) - 1
            isUnique = synsPerConn <= maxval + 1
            randLocPos = randInt(rand, N=synsPerConn, vmin=0, vmax=maxval, unique=isUnique)
            synMechLocs = [loc[i] for i in randLocPos]
        else:
            _ensure(isExplicitLoc == False, params, f"specifiyng the `loc` as single value when connRandomSecFromList is True (with multiple sections provided) is deprecated. To silence this warning, provide a list, or remove `loc` from the connection parameters (locations will be picked from a uniform distribution).")

            rand.uniform(0, 1)
            synMechLocs = h.Vector(synsPerConn).setrand(rand).to_python()
        return synMechSecs, synMechLocs

    def _distributeSynsUniformly(self, secList, numSyns):
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
                    print(('  Section lengths not available to distribute synapses in cell %d' % self.gid))

            secLengths = [x for x in secLengths if isinstance(x, Number)]
            totLength = sum(secLengths)
            cumLengths = list(cumsum(secLengths))
            absLocs = [i * (totLength / numSyns) + totLength / numSyns / 2 for i in range(numSyns)]
            inds = [cumLengths.index(next(x for x in cumLengths if x >= absLoc)) for absLoc in absLocs]
            secs = [secList[ind] for ind in inds]
            locs = [(cumLengths[ind] - absLoc) / secLengths[ind] for absLoc, ind in zip(absLocs, inds)]
        except:
            secs, locs = [], []
        return secs, locs

    def _addConnPlasticity(self, params, sec, netcon, weightIndex):
        from .. import sim

        plasticity = params.get('plast')
        if plasticity and sim.cfg.createNEURONObj:
            try:
                plastMech = getattr(h, plasticity['mech'], None)(
                    0, sec=sec['hObj']
                )  # create plasticity mechanism (eg. h.STDP)
                for plastParamName, plastParamValue in plasticity[
                    'params'
                ].items():  # add params of the plasticity mechanism
                    setattr(plastMech, plastParamName, plastParamValue)
                if plasticity['mech'] == 'STDP':  # specific implementation steps required for the STDP mech
                    precon = sim.pc.gid_connect(params['preGid'], plastMech)
                    precon.weight[0] = 1  # Send presynaptic spikes to the STDP adjuster
                    pstcon = sim.pc.gid_connect(self.gid, plastMech)
                    pstcon.weight[0] = -1  # Send postsynaptic spikes to the STDP adjuster
                    h.setpointer(
                        netcon._ref_weight[weightIndex], 'synweight', plastMech
                    )  # Associate the STDP adjuster with this weight
                    # self.conns[-1]['hPlastSection'] = plastSection
                    self.conns[-1]['hSTDP'] = plastMech
                    self.conns[-1]['hSTDPprecon'] = precon
                    self.conns[-1]['hSTDPpstcon'] = pstcon
                    self.conns[-1]['STDPdata'] = {
                        'preGid': params['preGid'],
                        'postGid': self.gid,
                        'receptor': weightIndex,
                    }  # Not used; FYI only; store here just so it's all in one place
                    if sim.cfg.verbose:
                        print('  Added STDP plasticity to synaptic mechanism')
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

            # check whether there is a single cell per pop or multiple subpopulations (diversity)
            if 'diversity' not in sim.net.pops[pop].tags.keys():
                # rotated coordinates around z axis first then shift relative to the soma
                morphSegCoords = sim.net.pops[pop]._morphSegCoords
            else:
                label = self.tags['label'][0]
                morphSegCoords = sim.net.pops[pop]._morphSegCoords[label]

            self._segCoords['p0'] = p3dsoma + morphSegCoords['p0']
            self._segCoords['p1'] = p3dsoma + morphSegCoords['p1']
            
            # moved here, as morphSegCoords are defined here exclusively 
            self._segCoords['d0'] = morphSegCoords['d0']
            self._segCoords['d1'] = morphSegCoords['d1']

        else:
            # rotated coordinates around z axis
            self._segCoords['p0'] = p3dsoma
            self._segCoords['p1'] = p3dsoma

    def getNumberOfSegments(self) -> int:
        if hasattr(self, '_segCoords'):
            return self._segCoords['p0'].shape[1]
        else:
            return sum(sec['hObj'].nseg for sec in self.secs.values())

    def setImembPtr(self):
        """Set PtrVector to point to the `i_membrane_`"""
        jseg = 0
        for sec in list(self.secs.values()):
            hSec = sec['hObj']
            for iseg, seg in enumerate(hSec):
                try:
                    self.imembPtr.pset(jseg, seg._ref_i_membrane_)  # notice the underscore at the end (in nA)
                except:
                    'Error setting Vector to point to i_membrane_'
                jseg += 1

    def getImemb(self):
        """Gather membrane currents from PtrVector into imVec (does not need a loop!)"""
        self.imembPtr.gather(self.imembVec)
        return self.imembVec.as_numpy()  # (nA)

    def updateShape(self):
        """Call after h.define_shape() to update cell coords"""
        x = self.tags['x']
        y = -self.tags['y']  # Neuron y-axis positive = upwards, so assume pia=0 and cortical depth = neg
        z = self.tags['z']

        for sec in list(self.secs.values()):
            if (
                'geom' in sec and 'pt3d' not in sec['geom'] and isinstance(sec['hObj'], type(h.Section()))
            ):  # only cells that didn't have pt3d before
                sec['geom']['pt3d'] = []
                sec['hObj'].push()
                n3d = int(h.n3d())  # get number of n3d points in each section
                for i in range(n3d):
                    # by default L is added in x-axis; shift to y-axis; z increases 100um for each cell so set to 0
                    pt3d = [h.y3d(i), h.x3d(i), 0, h.diam3d(i)]
                    sec['geom']['pt3d'].append(pt3d)
                    h.pt3dchange(i, x + pt3d[0], y + pt3d[1], z + pt3d[2], pt3d[3], sec=sec['hObj'])
                h.pop_section()

    def originSecName(self):
        if 'soma' in self.secs:
            secOrig = 'soma'
        elif any([secName.startswith('som') for secName in list(self.secs.keys())]):
            secOrig = next(secName for secName in list(self.secs.keys()) if secName.startswith('soma'))
        else:
            secOrig = list(self.secs.keys())[0]
        return secOrig

    def originSec(self):
        return self.secs[self.originSecName()]

def _ensure(condition, params, message):
    connLabel = params.get('label')
    connLabelStr = f'[{connLabel}]' if connLabel else ''
    assert condition, f"  Error in connParams{connLabelStr}: {message}"
