
"""
pop.py 

Contains Population related classes 

Contributors: salvadordura@gmail.com
"""

from matplotlib.pylab import arange, seed, rand, array, pi, sqrt, sin, cos, arccos
import numpy as np
from neuron import h # Import NEURON
import sim


###############################################################################
# 
# POPULATION CLASS
#
###############################################################################

class Pop (object):
    ''' Python class used to instantiate the network population '''
    def __init__(self, label, tags):
        self.tags = tags # list of tags/attributes of population (eg. numCells, cellModel,...)
        self.tags['popLabel'] = label
        self.cellGids = []  # list of cell gids beloging to this pop
        self._setCellClass()


    # Function to instantiate Cell objects based on the characteristics of this population
    def createCells(self):
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
            print 'Warninig: number or density of cells not specified for population %s; defaulting to numCells = 1' % (self.tags['popLabel'])
            cells = self.createCellsFixedNum()

        return cells


    def createCellsFixedNum (self):
        ''' Create population cells based on fixed number of cells'''
        cells = []
        seed(sim.id32('%d'%(sim.cfg.seeds['loc']+self.tags['numCells']+sim.net.lastGid)))
        randLocs = rand(self.tags['numCells'], 3)  # create random x,y,z locations

        if sim.net.params.shape == 'cylinder':
            # Use the x,z random vales 
            rho = randLocs[:,0] # use x rand value as the radius rho in the interval [0, 1)
            phi = 2 * pi * randLocs[:,2] # use z rand value as the angle phi in the interval [0, 2*pi) 
            x = (1 + sqrt(rho) * cos(phi))/2.0
            z = (1 + sqrt(rho) * sin(phi))/2.0
            randLocs[:,0] = x
            randLocs[:,2] = z
    
        elif sim.net.params.shape == 'ellipsoid':
            # Use the x,y,z random vales 
            rho = np.power(randLocs[:,0], 1.0/3.0) # use x rand value as the radius rho in the interval [0, 1); cuberoot
            phi = 2 * pi * randLocs[:,1] # use y rand value as the angle phi in the interval [0, 2*pi) 
            costheta = (2 * randLocs[:,2]) - 1 # use z rand value as cos(theta) in the interval [-1, 1); ensures uniform dist 
            theta = arccos(costheta)  # obtain theta from cos(theta)
            x = (1 + rho * cos(phi) * sin(theta))/2.0
            y = (1 + rho * sin(phi) * sin(theta))/2.0
            z = (1 + rho * cos(theta))/2.0 
            randLocs[:,0] = x
            randLocs[:,1] = y
            randLocs[:,2] = z
        
        for icoord, coord in enumerate(['x', 'y', 'z']):
            if coord+'Range' in self.tags:  # if user provided absolute range, convert to normalized
                self.tags[coord+'normRange'] = [float(point) / getattr(sim.net.params, 'size'+coord.upper()) for point in self.tags[coord+'Range']]
            # constrain to range set by user
            if coord+'normRange' in self.tags:  # if normalized range, rescale random locations
                minv = self.tags[coord+'normRange'][0] 
                maxv = self.tags[coord+'normRange'][1] 
                randLocs[:,icoord] = randLocs[:,icoord] * (maxv-minv) + minv

        for i in xrange(int(sim.rank), int(sim.net.params.scale * self.tags['numCells']), sim.nhosts):
            gid = sim.net.lastGid+i
            self.cellGids.append(gid)  # add gid list of cells belonging to this population - not needed?
            cellTags = {k: v for (k, v) in self.tags.iteritems() if k in sim.net.params.popTagsCopiedToCells}  # copy all pop tags to cell tags, except those that are pop-specific
            cellTags['popLabel'] = self.tags['popLabel']
            cellTags['xnorm'] = randLocs[i,0] # set x location (um)
            cellTags['ynorm'] = randLocs[i,1] # set y location (um)
            cellTags['znorm'] = randLocs[i,2] # set z location (um)
            cellTags['x'] = sim.net.params.sizeX * randLocs[i,0] # set x location (um)
            cellTags['y'] = sim.net.params.sizeY * randLocs[i,1] # set y location (um)
            cellTags['z'] = sim.net.params.sizeZ * randLocs[i,2] # set z location (um)
            cells.append(self.cellModelClass(gid, cellTags)) # instantiate Cell object
            if sim.cfg.verbose: print('Cell %d/%d (gid=%d) of pop %s, on node %d, '%(i, sim.net.params.scale * self.tags['numCells']-1, gid, self.tags['popLabel'], sim.rank))
        sim.net.lastGid = sim.net.lastGid + self.tags['numCells'] 
        return cells

                
    def createCellsDensity (self):
        ''' Create population cells based on density'''
        cells = []
        shape = sim.net.params.shape
        sizeX = sim.net.params.sizeX
        sizeY = sim.net.params.sizeY
        sizeZ = sim.net.params.sizeZ
        
        # calculate volume
        if shape == 'cuboid':
            volume = sizeY/1e3 * sizeX/1e3 * sizeZ/1e3  
        elif shape == 'cylinder':
            volume = sizeY/1e3 * sizeX/1e3/2 * sizeZ/1e3/2 * pi
        elif shape == 'ellipsoid':
            volume = sizeY/1e3/2.0 * sizeX/1e3/2.0 * sizeZ/1e3/2.0 * pi * 4.0 / 3.0

        for coord in ['x', 'y', 'z']:
            if coord+'Range' in self.tags:  # if user provided absolute range, convert to normalized
                self.tags[coord+'normRange'] = [point / sim.net.params['size'+coord.upper()] for point in self.tags[coord+'Range']]
            if coord+'normRange' in self.tags:  # if normalized range, rescale volume
                minv = self.tags[coord+'normRange'][0] 
                maxv = self.tags[coord+'normRange'][1] 
                volume = volume * (maxv-minv)

        funcLocs = None  # start with no locations as a function of density function
        if isinstance(self.tags['density'], str): # check if density is given as a function 
            if shape == 'cuboid':  # only available for cuboids
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
                
                seed(sim.id32('%d' % sim.cfg.seeds['loc']+sim.net.lastGid))  # reset random number generator
                locsAll = minRange + ((maxRange-minRange)) * rand(int(maxCells), 1)  # random location values 
                locsProb = array(map(densityFunc, locsAll)) / maxDensity  # calculate normalized density for each location value (used to prune)
                allrands = rand(len(locsProb))  # create an array of random numbers for checking each location pos 
                
                makethiscell = locsProb>allrands  # perform test to see whether or not this cell should be included (pruning based on density func)
                funcLocs = [locsAll[i] for i in range(len(locsAll)) if i in array(makethiscell.nonzero()[0],dtype='int')] # keep only subset of yfuncLocs based on density func
                self.tags['numCells'] = len(funcLocs)  # final number of cells after pruning of location values based on density func
                if sim.cfg.verbose: print 'Volume=%.2f, maxDensity=%.2f, maxCells=%.0f, numCells=%.0f'%(volume, maxDensity, maxCells, self.tags['numCells'])
            else:
                print 'Error: Density functions are only implemented for cuboid shaped networks'
                exit(0)
        else:  # NO ynorm-dep
            self.tags['numCells'] = int(self.tags['density'] * volume)  # = density (cells/mm^3) * volume (mm^3)

        # calculate locations of cells 
        seed(sim.id32('%d'%(sim.cfg.seeds['loc']+self.tags['numCells']+sim.net.lastGid)))
        randLocs = rand(self.tags['numCells'], 3)  # create random x,y,z locations

        if sim.net.params.shape == 'cylinder':
            # Use the x,z random vales 
            rho = randLocs[:,0] # use x rand value as the radius rho in the interval [0, 1)
            phi = 2 * pi * randLocs[:,2] # use z rand value as the angle phi in the interval [0, 2*pi) 
            x = (1 + sqrt(rho) * cos(phi))/2.0
            z = (1 + sqrt(rho) * sin(phi))/2.0
            randLocs[:,0] = x
            randLocs[:,2] = z
    
        elif sim.net.params.shape == 'ellipsoid':
            # Use the x,y,z random vales 
            rho = np.power(randLocs[:,0], 1.0/3.0) # use x rand value as the radius rho in the interval [0, 1); cuberoot
            phi = 2 * pi * randLocs[:,1] # use y rand value as the angle phi in the interval [0, 2*pi) 
            costheta = (2 * randLocs[:,2]) - 1 # use z rand value as cos(theta) in the interval [-1, 1); ensures uniform dist 
            theta = arccos(costheta)  # obtain theta from cos(theta)
            x = (1 + rho * cos(phi) * sin(theta))/2.0
            y = (1 + rho * sin(phi) * sin(theta))/2.0
            z = (1 + rho * cos(theta))/2.0 
            randLocs[:,0] = x
            randLocs[:,1] = y
            randLocs[:,2] = z

        for icoord, coord in enumerate(['x', 'y', 'z']):
            if coord+'normRange' in self.tags:  # if normalized range, rescale random locations
                minv = self.tags[coord+'normRange'][0] 
                maxv = self.tags[coord+'normRange'][1] 
                randLocs[:,icoord] = randLocs[:,icoord] * (maxv-minv) + minv
            if funcLocs and coordFunc == coord+'norm':  # if locations for this coordinate calculated using density function
                randLocs[:,icoord] = funcLocs

        if sim.cfg.verbose and not funcLocs: print 'Volume=%.4f, density=%.2f, numCells=%.0f'%(volume, self.tags['density'], self.tags['numCells'])

        for i in xrange(int(sim.rank), self.tags['numCells'], sim.nhosts):
            gid = sim.net.lastGid+i
            self.cellGids.append(gid)  # add gid list of cells belonging to this population - not needed?
            cellTags = {k: v for (k, v) in self.tags.iteritems() if k in sim.net.params.popTagsCopiedToCells}  # copy all pop tags to cell tags, except those that are pop-specific
            cellTags['popLabel'] = self.tags['popLabel']
            cellTags['xnorm'] = randLocs[i,0]  # calculate x location (um)
            cellTags['ynorm'] = randLocs[i,1]  # calculate y location (um)
            cellTags['znorm'] = randLocs[i,2]  # calculate z location (um)
            cellTags['x'] = sizeX * randLocs[i,0]  # calculate x location (um)
            cellTags['y'] = sizeY * randLocs[i,1]  # calculate y location (um)
            cellTags['z'] = sizeZ * randLocs[i,2]  # calculate z location (um)
            cells.append(self.cellModelClass(gid, cellTags)) # instantiate Cell object
            if sim.cfg.verbose: 
                print('Cell %d/%d (gid=%d) of pop %s, pos=(%2.f, %2.f, %2.f), on node %d, '%(i, self.tags['numCells']-1, gid, self.tags['popLabel'],cellTags['x'], cellTags['y'], cellTags['z'], sim.rank))
        sim.net.lastGid = sim.net.lastGid + self.tags['numCells'] 
        return cells


    def createCellsList (self):
        ''' Create population cells based on list of individual cells'''
        cells = []
        self.tags['numCells'] = len(self.tags['cellsList'])
        for i in xrange(int(sim.rank), len(self.tags['cellsList']), sim.nhosts):
            #if 'cellModel' in self.tags['cellsList'][i]:
            #    self.cellModelClass = getattr(f, self.tags['cellsList'][i]['cellModel'])  # select cell class to instantiate cells based on the cellModel tags
            gid = sim.net.lastGid+i
            self.cellGids.append(gid)  # add gid list of cells belonging to this population - not needed?
            cellTags = {k: v for (k, v) in self.tags.iteritems() if k in sim.net.params.popTagsCopiedToCells}  # copy all pop tags to cell tags, except those that are pop-specific
            cellTags['popLabel'] = self.tags['popLabel']
            cellTags.update(self.tags['cellsList'][i])  # add tags specific to this cells
            for coord in ['x','y','z']:
                if coord in cellTags:  # if absolute coord exists
                    cellTags[coord+'norm'] = cellTags[coord]/getattr(sim.net.params, 'size'+coord.upper())  # calculate norm coord
                elif coord+'norm' in cellTags:  # elif norm coord exists
                    cellTags[coord] = cellTags[coord+'norm']*getattr(sim.net.params, 'size'+coord.upper())  # calculate norm coord
                else:
                    cellTags[coord+'norm'] = cellTags[coord] = 0
            if 'propList' not in cellTags: cellTags['propList'] = []  # initalize list of property sets if doesn't exist
            cells.append(self.cellModelClass(gid, cellTags)) # instantiate Cell object
            if sim.cfg.verbose: print('Cell %d/%d (gid=%d) of pop %d, on node %d, '%(i, self.tags['numCells']-1, gid, i, sim.rank))
        sim.net.lastGid = sim.net.lastGid + len(self.tags['cellsList'])
        return cells


    def createCellsGrid (self):
        ''' Create population cells based on fixed number of cells'''
        cells = []
        seed(sim.id32('%d'%(sim.cfg.seeds['loc']+self.tags['gridSpacing']+sim.net.lastGid)))
        
        rangeLocs = [[0, getattr(sim.net.params, 'size'+coord)] for coord in ['X','Y','Z']]
        for icoord, coord in enumerate(['x', 'y', 'z']):
            # constrain to range set by user
            if coord+'normRange' in self.tags:  # if normalized range, convert to normalized
                self.tags[coord+'Range'] = [float(point) * getattr(sim.net.params, 'size'+coord.upper()) for point in self.tags[coord+'Range']]                
            if coord+'Range' in self.tags:  # if user provided absolute range, calculate range
                self.tags[coord+'normRange'] = [float(point) / getattr(sim.net.params, 'size'+coord.upper()) for point in self.tags[coord+'Range']]
                rangeLocs[icoord] = [self.tags[coord+'Range'][0], self.tags[coord+'Range'][1]] 
              
        gridSpacing = self.tags['gridSpacing']
        gridLocs = []
        for x in np.arange(rangeLocs[0][0], rangeLocs[0][1]+1, gridSpacing):
            for y in np.arange(rangeLocs[1][0], rangeLocs[1][1]+1, gridSpacing):
                for z in np.arange(rangeLocs[2][0], rangeLocs[2][1]+1, gridSpacing):
                    gridLocs.append((x, y, z))

        numCells = len(gridLocs)

        for i in xrange(int(sim.rank), numCells, sim.nhosts):
            gid = sim.net.lastGid+i
            self.cellGids.append(gid)  # add gid list of cells belonging to this population - not needed?
            cellTags = {k: v for (k, v) in self.tags.iteritems() if k in sim.net.params.popTagsCopiedToCells}  # copy all pop tags to cell tags, except those that are pop-specific
            cellTags['popLabel'] = self.tags['popLabel']
            cellTags['xnorm'] = gridLocs[i][0] / sim.net.params.sizeX # set x location (um)
            cellTags['ynorm'] = gridLocs[i][1] / sim.net.params.sizeY # set y location (um)
            cellTags['znorm'] = gridLocs[i][2] / sim.net.params.sizeZ # set z location (um)
            cellTags['x'] = gridLocs[i][0]   # set x location (um)
            cellTags['y'] = gridLocs[i][1] # set y location (um)
            cellTags['z'] = gridLocs[i][2] # set z location (um)
            cells.append(self.cellModelClass(gid, cellTags)) # instantiate Cell object
            if sim.cfg.verbose: print('Cell %d/%d (gid=%d) of pop %s, on node %d, '%(i, numCells, gid, self.tags['popLabel'], sim.rank))
        sim.net.lastGid = sim.net.lastGid + numCells
        return cells



    def _setCellClass (self):
        # set cell class: CompartCell for compartmental cells of PointCell for point neurons (NetStims, IntFire1,...)
        try: # check if cellModel corresponds to an existing point process mechanism; if so, use PointCell
            tmp = getattr(h, self.tags['cellModel'])
            self.cellModelClass = sim.PointCell
            excludeTags = ['popLabel', 'cellModel', 'cellType', 'numCells', 'density', 
                        'xRange', 'yRange', 'zRange', 'xnormRange', 'ynormRange', 'znormRange', 'vref']
            params = {k: v for k,v in self.tags.iteritems() if k not in excludeTags}
            self.tags['params'] = params
            for k in self.tags['params']: self.tags.pop(k)
            sim.net.params.popTagsCopiedToCells.append('params')
        except:
            self.cellModelClass = sim.CompartCell  # otherwise assume has sections and some cellParam rules apply to it; use CompartCell
            # print "Error: cellModel=%s not a key in netParam.cellParams or a point process mechanism (eg. NetStim or IntFire1)" % (self.tags['cellModel'])


    def __getstate__ (self): 
        ''' Removes non-picklable h objects so can be pickled and sent via py_alltoall'''
        odict = self.__dict__.copy() # copy the dict since we change it
        odict = sim.replaceFuncObj(odict)  # replace h objects with None so can be pickled
        odict['cellModelClass'] = str(odict['cellModelClass'])
        return odict

