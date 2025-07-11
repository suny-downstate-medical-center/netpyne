"""
Module defining Population class and methods

"""

try:
    basestring
except NameError:
    basestring = str

from numpy import pi, sqrt, sin, cos, arccos
import numpy as np
from neuron import h  # Import NEURON
from netpyne import sim


###############################################################################
#
# POPULATION CLASS
#
###############################################################################


class Pop(object):
    """
    Class for/to <short description of `netpyne.network.pop.Pop`>
    """

    def __init__(self, label, tags):
        self.tags = tags  # list of tags/attributes of population (eg. numCells, cellModel,...)
        self.tags['pop'] = label
        self.cellGids = []  # list of cell gids beloging to this pop

        self.cellModelClass, cellRuleForPointCell = self._resolveCellClass()

        if self.cellModelClass == sim.PointCell:
            self.__handlePointCellParams(cellRuleForPointCell)

        self.rand = h.Random()  # random number generator

    def _distributeCells(self, numCellsPop):
        """
        Distribute cells across compute nodes using round-robin
        """

        hostCells = {}
        for i in range(sim.nhosts):
            hostCells[i] = []

        for i in range(numCellsPop):
            hostCells[sim.nextHost].append(i)

            sim.nextHost += 1
            if sim.nextHost >= sim.nhosts:
                sim.nextHost = 0

        if sim.cfg.verbose:
            print(
                (
                    "Distributed population of %i cells on %s hosts: %s, next: %s"
                    % (numCellsPop, sim.nhosts, hostCells, sim.nextHost)
                )
            )
        return hostCells

    def createCells(self):
        """
        Function to instantiate Cell objects based on the characteristics of this population
        """

        # add individual cells
        if 'cellsList' in self.tags:
            cells = self.createCellsList()

        # create cells based on fixed number of cells
        elif 'numCells' in self.tags:
            cells = self.createCellsFixedNum()

        # create cells based on density (optional ynorm-dep)
        elif 'density' in self.tags:
            cells = self.createCellsDensity()

        # create cells based on density (optional ynorm-dep)
        elif 'gridSpacing' in self.tags:
            cells = self.createCellsGrid()

        # not enough tags to create cells
        else:
            self.tags['numCells'] = 1
            print(
                'Warninig: number or density of cells not specified for population %s; defaulting to numCells = 1'
                % (self.tags['pop'])
            )
            cells = self.createCellsFixedNum()

        return cells

    def createCellsFixedNum(self):
        """
        Create population cells based on fixed number of cells
        """

        cells = []
        self.rand.Random123(self.tags['numCells'], sim.net.lastGid, sim.cfg.seeds['loc'])
        self.rand.uniform(0, 1)
        vec = h.Vector(self.tags['numCells'] * 3)
        vec.setrand(self.rand)
        randLocs = np.array(vec).reshape(self.tags['numCells'], 3)  # create random x,y,z locations

        if sim.net.params.shape == 'cylinder':
            # Use the x,z random vales
            rho = randLocs[:, 0]  # use x rand value as the radius rho in the interval [0, 1)
            phi = 2 * pi * randLocs[:, 2]  # use z rand value as the angle phi in the interval [0, 2*pi)
            x = (1 + sqrt(rho) * cos(phi)) / 2.0
            z = (1 + sqrt(rho) * sin(phi)) / 2.0
            randLocs[:, 0] = x
            randLocs[:, 2] = z

        elif sim.net.params.shape == 'ellipsoid':
            # Use the x,y,z random vales
            rho = np.power(
                randLocs[:, 0], 1.0 / 3.0
            )  # use x rand value as the radius rho in the interval [0, 1); cuberoot
            phi = 2 * pi * randLocs[:, 1]  # use y rand value as the angle phi in the interval [0, 2*pi)
            costheta = (
                2 * randLocs[:, 2]
            ) - 1  # use z rand value as cos(theta) in the interval [-1, 1); ensures uniform dist
            theta = arccos(costheta)  # obtain theta from cos(theta)
            x = (1 + rho * cos(phi) * sin(theta)) / 2.0
            y = (1 + rho * sin(phi) * sin(theta)) / 2.0
            z = (1 + rho * cos(theta)) / 2.0
            randLocs[:, 0] = x
            randLocs[:, 1] = y
            randLocs[:, 2] = z

        for icoord, coord in enumerate(['x', 'y', 'z']):
            if coord + 'Range' in self.tags:  # if user provided absolute range, convert to normalized
                self.tags[coord + 'normRange'] = [
                    float(point) / getattr(sim.net.params, 'size' + coord.upper())
                    for point in self.tags[coord + 'Range']
                ]
            # constrain to range set by user
            if coord + 'normRange' in self.tags:  # if normalized range, rescale random locations
                minv = self.tags[coord + 'normRange'][0]
                maxv = self.tags[coord + 'normRange'][1]
                randLocs[:, icoord] = randLocs[:, icoord] * (maxv - minv) + minv

        numCells = int(sim.net.params.scale * self.tags['numCells'])

        diversityFractions = self._diversityFractions(numCells)

        for i in self._distributeCells(numCells)[sim.rank]:
            gid = sim.net.lastGid + i
            self.cellGids.append(gid)  # add gid list of cells belonging to this population - not needed?
            cellTags = self._createCellTags(i, diversityFractions)
            cellTags['xnorm'] = randLocs[i, 0]  # set x location (um)
            cellTags['ynorm'] = randLocs[i, 1]  # set y location (um)
            cellTags['znorm'] = randLocs[i, 2]  # set z location (um)
            cellTags['x'] = sim.net.params.sizeX * randLocs[i, 0]  # set x location (um)
            cellTags['y'] = sim.net.params.sizeY * randLocs[i, 1]  # set y location (um)
            cellTags['z'] = sim.net.params.sizeZ * randLocs[i, 2]  # set z location (um)
            if 'spkTimes' in self.tags:  # if VecStim, copy spike times to params
                if isinstance(self.tags['spkTimes'][0], list):
                    try:
                        cellTags['params']['spkTimes'] = self.tags['spkTimes'][i]  # 2D list
                    except:
                        pass
                else:
                    cellTags['params']['spkTimes'] = self.tags['spkTimes']  # 1D list (same for all)

            if 'dynamicRates' in self.tags:  # if NetStim, copy rates array to params
                if 'rates' in self.tags['dynamicRates'] and 'times' in self.tags['dynamicRates']:
                    if isinstance(self.tags['dynamicRates']['rates'][0], list):
                        try:
                            cellTags['params']['rates'] = [
                                self.tags['dynamicRates']['rates'][i],
                                self.tags['dynamicRates']['times'],
                            ]  # 2D list
                        except:
                            pass
                    else:
                        cellTags['params']['rates'] = [
                            self.tags['dynamicRates']['rates'],
                            self.tags['dynamicRates']['times'],
                        ]  # 1D list (same for all)
            cells.append(self.cellModelClass(gid, cellTags))  # instantiate Cell object

            if sim.cfg.verbose:
                print(
                    (
                        'Cell %d/%d (gid=%d) of pop %s, on node %d, '
                        % (i, sim.net.params.scale * self.tags['numCells'] - 1, gid, self.tags['pop'], sim.rank)
                    )
                )
        sim.net.lastGid = sim.net.lastGid + self.tags['numCells']
        return cells

    def createCellsDensity(self):
        """
        Create population cells based on density
        """

        cells = []
        shape = sim.net.params.shape
        sizeX = sim.net.params.sizeX
        sizeY = sim.net.params.sizeY
        sizeZ = sim.net.params.sizeZ

        # calculate volume
        if shape == 'cuboid':
            volume = sizeY / 1e3 * sizeX / 1e3 * sizeZ / 1e3
        elif shape == 'cylinder':
            volume = sizeY / 1e3 * sizeX / 1e3 / 2 * sizeZ / 1e3 / 2 * pi
        elif shape == 'ellipsoid':
            volume = sizeY / 1e3 / 2.0 * sizeX / 1e3 / 2.0 * sizeZ / 1e3 / 2.0 * pi * 4.0 / 3.0

        for coord in ['x', 'y', 'z']:
            if coord + 'Range' in self.tags:  # if the user provided absolute range: 'xRange', 'yRange', 'zRange'
                self.tags[coord + 'normRange'] = [  # as a tag, convert to normalized range.
                    point / getattr(sim.net.params, 'size' + coord.upper()) for point in self.tags[coord + 'Range']
                ]
            if coord + 'normRange' in self.tags:  # if normalized range, rescale volume
                minv = self.tags[coord + 'normRange'][0]
                maxv = self.tags[coord + 'normRange'][1]
                volume = volume * (maxv - minv)

        funcLocs = None  # start with no locations as a function of density function
        if isinstance(self.tags['density'], basestring):  # check if density is given as a function
            if shape == 'cuboid':  # only available for cuboids
                strFunc = self.tags['density']  # string containing function
                strVars = [var for var in ['xnorm', 'ynorm', 'znorm'] if var in strFunc]  # get list of variables used
                if not len(strVars) == 1:
                    print(
                        'Error: density function (%s) for population %s does not include "xnorm", "ynorm" or "znorm"'
                        % (strFunc, self.tags['pop'])
                    )
                    return
                coordFunc = strVars[0]
                lambdaStr = 'lambda ' + coordFunc + ': ' + strFunc  # convert to lambda function
                densityFunc = eval(lambdaStr)
                minRange = self.tags[coordFunc + 'Range'][0]
                maxRange = self.tags[coordFunc + 'Range'][1]

                interval = 0.001  # interval of location values to evaluate func in order to find the max cell density
                maxDensity = max(list(map(densityFunc, (np.arange(minRange, maxRange, interval)))))  # max cell density
                maxCells = volume * maxDensity  # max number of cells based on max value of density func

                self.rand.Random123(int(maxDensity), sim.net.lastGid, sim.cfg.seeds['loc'])
                locsAll = minRange + ((maxRange - minRange)) * np.array(
                    [self.rand.uniform(0, 1) for i in range(int(maxCells))]
                )  # random location values
                locsProb = (
                    np.array(list(map(densityFunc, locsAll))) / maxDensity
                )  # calculate normalized density for each location value (used to prune)
                allrands = np.array(
                    [self.rand.uniform(0, 1) for i in range(len(locsProb))]
                )  # create an array of random numbers for checking each location pos

                makethiscell = (
                    locsProb > allrands
                )  # perform test to see whether or not this cell should be included (pruning based on density func)
                funcLocs = [
                    locsAll[i] for i in range(len(locsAll)) if i in np.array(makethiscell.nonzero()[0], dtype='int')
                ]  # keep only subset of yfuncLocs based on density func
                self.tags['numCells'] = len(
                    funcLocs
                )  # final number of cells after pruning of location values based on density func
                if sim.cfg.verbose:
                    print(
                        'Volume=%.2f, maxDensity=%.2f, maxCells=%.0f, numCells=%.0f'
                        % (volume, maxDensity, maxCells, self.tags['numCells'])
                    )
            else:
                print('Error: Density functions are only implemented for cuboid shaped networks')
                exit(0)
        else:  # NO ynorm-dep
            self.tags['numCells'] = int(self.tags['density'] * volume)  # = density (cells/mm^3) * volume (mm^3)

        # calculate locations of cells
        self.rand.Random123(self.tags['numCells'], sim.net.lastGid, sim.cfg.seeds['loc'])
        self.rand.uniform(0, 1)
        vec = h.Vector(self.tags['numCells'] * 3)
        vec.setrand(self.rand)
        try:
            randLocs = np.array(vec).reshape(self.tags['numCells'], 3)  # create random x,y,z locations
        except Exception as e:
            if 'numCells' in self.tags and self.tags['numCells'] == 0 or self.tags['numCells'] < 1:
                print(f"Unable to create network, please validate that '{self.tags['pop']}' population size is > 0 ")
            raise e


        if sim.net.params.shape == 'cylinder':
            # Use the x,z random vales
            rho = randLocs[:, 0]  # use x rand value as the radius rho in the interval [0, 1)
            phi = 2 * pi * randLocs[:, 2]  # use z rand value as the angle phi in the interval [0, 2*pi)
            x = (1 + sqrt(rho) * cos(phi)) / 2.0
            z = (1 + sqrt(rho) * sin(phi)) / 2.0
            randLocs[:, 0] = x
            randLocs[:, 2] = z

        elif sim.net.params.shape == 'ellipsoid':
            # Use the x,y,z random vales
            rho = np.power(
                randLocs[:, 0], 1.0 / 3.0
            )  # use x rand value as the radius rho in the interval [0, 1); cuberoot
            phi = 2 * pi * randLocs[:, 1]  # use y rand value as the angle phi in the interval [0, 2*pi)
            costheta = (
                2 * randLocs[:, 2]
            ) - 1  # use z rand value as cos(theta) in the interval [-1, 1); ensures uniform dist
            theta = arccos(costheta)  # obtain theta from cos(theta)
            x = (1 + rho * cos(phi) * sin(theta)) / 2.0
            y = (1 + rho * sin(phi) * sin(theta)) / 2.0
            z = (1 + rho * cos(theta)) / 2.0
            randLocs[:, 0] = x
            randLocs[:, 1] = y
            randLocs[:, 2] = z

        for icoord, coord in enumerate(['x', 'y', 'z']):
            if coord + 'normRange' in self.tags:  # if normalized range, rescale random locations
                minv = self.tags[coord + 'normRange'][0]
                maxv = self.tags[coord + 'normRange'][1]
                randLocs[:, icoord] = randLocs[:, icoord] * (maxv - minv) + minv
            if (
                funcLocs and coordFunc == coord + 'norm'
            ):  # if locations for this coordinate calculated using density function
                randLocs[:, icoord] = funcLocs

        if sim.cfg.verbose and not funcLocs:
            print('Volume=%.4f, density=%.2f, numCells=%.0f' % (volume, self.tags['density'], self.tags['numCells']))

        numCells = self.tags['numCells']
        diversityFractions = self._diversityFractions(numCells)

        for i in self._distributeCells(numCells)[sim.rank]:
            gid = sim.net.lastGid + i
            self.cellGids.append(gid)  # add gid list of cells belonging to this population - not needed?
            cellTags = self._createCellTags(i, diversityFractions)
            cellTags['xnorm'] = randLocs[i, 0]  # calculate x location (um)
            cellTags['ynorm'] = randLocs[i, 1]  # calculate y location (um)
            cellTags['znorm'] = randLocs[i, 2]  # calculate z location (um)
            cellTags['x'] = sizeX * randLocs[i, 0]  # calculate x location (um)
            cellTags['y'] = sizeY * randLocs[i, 1]  # calculate y location (um)
            cellTags['z'] = sizeZ * randLocs[i, 2]  # calculate z location (um)
            cells.append(self.cellModelClass(gid, cellTags))  # instantiate Cell object
            if sim.cfg.verbose:
                print(
                    (
                        'Cell %d/%d (gid=%d) of pop %s, pos=(%2.f, %2.f, %2.f), on node %d, '
                        % (
                            i,
                            numCells - 1,
                            gid,
                            self.tags['pop'],
                            cellTags['x'],
                            cellTags['y'],
                            cellTags['z'],
                            sim.rank,
                        )
                    )
                )
        sim.net.lastGid = sim.net.lastGid + self.tags['numCells']
        return cells

    def createCellsList(self):
        """
        Create population cells based on list of individual cells
        """

        cells = []
        cellsList = self.tags['cellsList']
        numCells = len(cellsList)
        self.tags['numCells'] = numCells

        diversityFractions = self._diversityFractions(numCells)

        for i in self._distributeCells(numCells)[sim.rank]:
            # if 'cellModel' in self.tags['cellsList'][i]:
            #    self.cellModelClass = getattr(f, self.tags['cellsList'][i]['cellModel'])  # select cell class to instantiate cells based on the cellModel tags
            gid = sim.net.lastGid + i
            self.cellGids.append(gid)  # add gid list of cells belonging to this population - not needed?
            cellTags = self._createCellTags(i, diversityFractions)
            cellTags.update(cellsList[i])  # add tags specific to this cells
            for coord in ['x', 'y', 'z']:
                if coord in cellTags:  # if absolute coord exists
                    cellTags[coord + 'norm'] = cellTags[coord] / getattr(
                        sim.net.params, 'size' + coord.upper()
                    )  # calculate norm coord
                elif coord + 'norm' in cellTags:  # elif norm coord exists
                    cellTags[coord] = cellTags[coord + 'norm'] * getattr(
                        sim.net.params, 'size' + coord.upper()
                    )  # calculate norm coord
                else:
                    cellTags[coord + 'norm'] = cellTags[coord] = 0
            if (
                'cellModel' in self.tags.keys() and self.tags['cellModel'] == 'VecStim'
            ):  # if VecStim, copy spike times to params
                cellTags['params']['spkTimes'] = cellsList[i]['spkTimes']
            cells.append(self.cellModelClass(gid, cellTags))  # instantiate Cell object
            if sim.cfg.verbose:
                print(
                    ('Cell %d/%d (gid=%d) of pop %d, on node %d, ' % (i, self.tags['numCells'] - 1, gid, i, sim.rank))
                )
        sim.net.lastGid = sim.net.lastGid + numCells
        return cells

    def createCellsGrid(self):
        """
        Create population cells based on fixed number of cells
        """

        cells = []

        rangeLocs = [[0, getattr(sim.net.params, 'size' + coord)] for coord in ['X', 'Y', 'Z']]
        for icoord, coord in enumerate(['x', 'y', 'z']):
            # constrain to range set by user
            if coord + 'normRange' in self.tags:  # if normalized range, convert to normalized
                self.tags[coord + 'Range'] = [
                    float(point) * getattr(sim.net.params, 'size' + coord.upper())
                    for point in self.tags[coord + 'normRange']
                ]
            if coord + 'Range' in self.tags:  # if user provided absolute range, calculate range
                self.tags[coord + 'normRange'] = [
                    float(point) / getattr(sim.net.params, 'size' + coord.upper())
                    for point in self.tags[coord + 'Range']
                ]
                rangeLocs[icoord] = [self.tags[coord + 'Range'][0], self.tags[coord + 'Range'][1]]

        gridSpacing = self.tags['gridSpacing']
        gridLocs = []
        if isinstance(gridSpacing, list):
            for x in np.arange(rangeLocs[0][0], rangeLocs[0][1] + 1, gridSpacing[0]):
                for y in np.arange(rangeLocs[1][0], rangeLocs[1][1] + 1, gridSpacing[1]):
                    for z in np.arange(rangeLocs[2][0], rangeLocs[2][1] + 1, gridSpacing[2]):
                        gridLocs.append((x, y, z))
        else:
            for x in np.arange(rangeLocs[0][0], rangeLocs[0][1] + 1, gridSpacing):
                for y in np.arange(rangeLocs[1][0], rangeLocs[1][1] + 1, gridSpacing):
                    for z in np.arange(rangeLocs[2][0], rangeLocs[2][1] + 1, gridSpacing):
                        gridLocs.append((x, y, z))

        numCells = len(gridLocs)

        diversityFractions = self._diversityFractions(numCells, shuffled=True)

        for i in self._distributeCells(numCells)[sim.rank]:
            gid = sim.net.lastGid + i
            self.cellGids.append(gid)  # add gid list of cells belonging to this population - not needed?
            cellTags = self._createCellTags(i, diversityFractions)
            cellTags['xnorm'] = gridLocs[i][0] / sim.net.params.sizeX  # set x location (um)
            cellTags['ynorm'] = gridLocs[i][1] / sim.net.params.sizeY  # set y location (um)
            cellTags['znorm'] = gridLocs[i][2] / sim.net.params.sizeZ  # set z location (um)
            cellTags['x'] = gridLocs[i][0]  # set x location (um)
            cellTags['y'] = gridLocs[i][1]  # set y location (um)
            cellTags['z'] = gridLocs[i][2]  # set z location (um)
            cells.append(self.cellModelClass(gid, cellTags))  # instantiate Cell object
            if sim.cfg.verbose:
                print(('Cell %d/%d (gid=%d) of pop %s, on node %d, ' % (i, numCells, gid, self.tags['pop'], sim.rank)))
        sim.net.lastGid = sim.net.lastGid + numCells
        return cells

    def _diversityFractions(self, numCells, shuffled=False):
        """
        Calculates diversity fraction (0 to 1) for each cell. Returns list of fractions or None, if no diversity involved
        """
        if not self.tags.get('diversity', False):
            return None

        rng = np.random.default_rng(seed=sim.cfg.seeds['cell'])
        diversityFractions = np.arange(0, numCells, dtype=np.float64) / numCells
        if shuffled:
            rng.shuffle(diversityFractions)
        return diversityFractions

    def _createCellTags(self, ind=None, diversityFractions=None):

        # copy all pop tags to cell tags, except those that are pop-specific
        cellTags = {k: v for (k, v) in self.tags.items() if k in sim.net.params.popTagsCopiedToCells}
        cellTags['pop'] = self.tags['pop']

        if diversityFractions is not None:
            cellTags['fraction'] = diversityFractions[ind]

        return cellTags

    def _resolveCellClass(self):
        """
        Determines cell class (CompartCell, PointCell, etc). Returns it, and a cellRule for PointCell if it refers to cellParams entry.
        """
        cellRule = None

        # Check whether it's a NeuroML2 based cell
        # ! needs updating to read cellModel info from cellParams
        if origFormat := self.tags.get('originalFormat'):
            if origFormat == 'NeuroML2':
                cellClass = sim.NML2Cell
            elif origFormat == 'NeuroML2_SpikeSource':
                cellClass = sim.NML2SpikeSource
            else:
                print(f"Warning: unknown original format {origFormat} for population {self.tags['pop']}")
                cellClass = None
        else:
            # obtain cellModel either from popParams..
            cellModel = self.tags.get('cellModel')

            if cellModel is None:
                # .. or from cellParams
                cellType = self.tags.get('cellType')
                if cellType:
                    cellRule = sim.net.params.cellParams.get(cellType, {})
                    cellModel = cellRule.get('cellModel')
                else:
                    print(f"Warning: no 'cellType' or 'cellModel' found for population {self.tags['pop']}. Cells will be created as CompartCell, but with no sections.")

            # set cell class: CompartCell for compartmental cells of PointCell for point neurons (NetStims, IntFire1,...)
            if cellModel and hasattr(h, cellModel):
                # check if cellModel corresponds to an existing point process mechanism; if so, use PointCell
                cellClass = sim.PointCell
            else:
                # otherwise assume has sections and some cellParam rules apply to it; use CompartCell
                cellClass = sim.CompartCell
                # if model is known but wasn't recognized, issue warning
                knownPointps = ['NetStim', 'DynamicNetStim', 'VecStim', 'IntFire1', 'IntFire2', 'IntFire4']
                if getattr(self.tags, 'cellModel', None) in knownPointps:
                    print(
                        'Warning: could not find %s point process mechanism required for population %s'
                        % (cellModel, self.tags['pop'])
                    )
        return cellClass, cellRule

    def __handlePointCellParams(self, cellRule=None):

        if 'params' in self.tags and isinstance(self.tags['params'], dict):
            # in some cases, params for point cell may already be grouped in the nested 'params' dict.
            params = self.tags['params']
        else:
            # otherwise, try extracting them from the top level of tags dict
            excludeTags = [
                'pop',
                'cellModel',
                'cellType',
                'numCells',
                'density',
                'cellsList',
                'gridSpacing',
                'xRange',
                'yRange',
                'zRange',
                'xnormRange',
                'ynormRange',
                'znormRange',
                'vref',
                'spkTimes',
                'dynamicRates',
            ]
            params = {k: v for k, v in self.tags.items() if k not in excludeTags}
            self.tags['params'] = params
            for k in self.tags['params']:
                self.tags.pop(k)
        sim.net.params.popTagsCopiedToCells.append('params')

        # if point cell params defined directly in pop params, need to scan them for string functions
        if len(params):
            from ..specs.netParams import CellParams

            CellParams.updateStringFuncsWithPopParams(self.tags['pop'], params)

        # if popParams for PointCell contain 'cellType' and it exists in cellParams, take from there cellModel and params (if any)
        if cellRule:
            self.tags['cellModel'] = cellRule['cellModel']

            for k,v in cellRule.get('params', {}).items():
                # But don't override! If param is already there, it comes from popParams, which takes precedence
                if k not in self.tags['params']:
                    self.tags['params'][k] = v


    def calcRelativeSegCoords(self):
        """Calculate segment coordinates from 3d point coordinates
        Used for LFP calc (one per population cell; assumes same morphology)"""

        localPopGids = list(set(sim.net.gid2lid.keys()).intersection(set(self.cellGids)))
        if localPopGids:
            cells = []
            cellLabels_Ids = {}
            # consider diversity
            if 'diversity' not in self.tags.keys():
                label = ['no_diversity']
                cellLabels_Ids.update({label[0]: localPopGids})
                cells.append(sim.net.cells[sim.net.gid2lid[localPopGids[0]]])              # single cell per pop
            else:
                # enumerate the different cell labels (corresponding to the different cell variants)
                for nn in localPopGids:
                    for label in sim.net.cells[sim.net.gid2lid[nn]].tags['label']:
                        if label not in cellLabels_Ids.keys():
                            cellLabels_Ids.update({label:[]})
                        cellLabels_Ids[label].append(nn)
                # obtain cells with these cell rules (one per subpopulation)
                for label in cellLabels_Ids.keys():
                    cells.append(sim.net.cells[sim.net.gid2lid[cellLabels_Ids[label][0]]])
        else:
            return -1

        self._morphSegCoords = {}
        #print(cellLabels_Ids)
        for cell,label in zip(cells,cellLabels_Ids.keys()):
            ix = 0  # segment index

            p3dsoma = cell.getSomaPos()
            nseg = sum([sec['hObj'].nseg for sec in list(cell.secs.values())])

            p0 = np.zeros((3, nseg))  # hold the coordinates of segment starting points
            p1 = np.zeros((3, nseg))  # hold the coordinates of segment end points
            d0 = np.zeros(nseg)
            d1 = np.zeros(nseg)

            for sec in list(cell.secs.values()):
                hSec = sec['hObj']
                hSec.push()
                n3d = int(h.n3d())  # get number of n3d points in each section
                p3d = np.zeros((3, n3d))  # to hold locations of 3D morphology for the current section
                l3d = np.zeros(n3d)  # to hold locations of 3D morphology for the current section
                diam3d = np.zeros(n3d)  # to diameters

                for i in range(n3d):
                    p3d[0, i] = h.x3d(i) - p3dsoma[0]
                    p3d[1, i] = h.y3d(i) - p3dsoma[1]  # shift coordinates such to place soma at the origin.
                    p3d[2, i] = h.z3d(i) - p3dsoma[2]
                    diam3d[i] = h.diam3d(i)
                    l3d[i] = h.arc3d(i)

                l3d /= hSec.L  # normalize
                nseg = hSec.nseg

                l0 = np.zeros(nseg)  # keep range of segment starting point
                l1 = np.zeros(nseg)  # keep range of segment ending point

                for iseg, seg in enumerate(hSec):
                    l0[iseg] = (
                        seg.x - 0.5 * 1 / nseg
                        )  # x (normalized distance along the section) for the beginning of the segment
                    l1[iseg] = seg.x + 0.5 * 1 / nseg  # x for the end of the segment

                p0[0, ix : ix + nseg] = np.interp(l0, l3d, p3d[0, :])
                p0[1, ix : ix + nseg] = np.interp(l0, l3d, p3d[1, :])
                p0[2, ix : ix + nseg] = np.interp(l0, l3d, p3d[2, :])
                d0[ix : ix + nseg] = np.interp(l0, l3d, diam3d[:])

                p1[0, ix : ix + nseg] = np.interp(l1, l3d, p3d[0, :])
                p1[1, ix : ix + nseg] = np.interp(l1, l3d, p3d[1, :])
                p1[2, ix : ix + nseg] = np.interp(l1, l3d, p3d[2, :])
                d1[ix : ix + nseg] = np.interp(l1, l3d, diam3d[:])
                ix += nseg
                h.pop_section()

            if len(cells)==1:
                self._morphSegCoords['p0'] = p0
                self._morphSegCoords['p1'] = p1

                self._morphSegCoords['d0'] = d0
                self._morphSegCoords['d1'] = d1

            else:  # diversity
                self._morphSegCoords[label] = {} 

                self._morphSegCoords[label]['p0'] = p0
                self._morphSegCoords[label]['p1'] = p1

                self._morphSegCoords[label]['d0'] = d0
                self._morphSegCoords[label]['d1'] = d1


        #print(self._morphSegCoords)
        return self._morphSegCoords

    def __getstate__(self):
        """Removes non-picklable h objects so can be pickled and sent via py_alltoall"""

        odict = self.__dict__.copy()  # copy the dict since we change it
        odict = sim.replaceFuncObj(odict)  # replace h objects with None so can be pickled
        # odict['cellModelClass'] = str(odict['cellModelClass'])
        if 'cellModelClass' in odict:
            del odict['cellModelClass']
        if 'rand' in odict:
            del odict['rand']
        return odict
