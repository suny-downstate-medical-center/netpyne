
"""
pop.py 

Contains Population related classes 

Contributors: salvadordura@gmail.com
"""

from matplotlib.pylab import arange, seed, rand, array
from neuron import h # Import NEURON
import framework as f


###############################################################################
# 
# POPULATION CLASS
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
        cellModelClass = f.Cell
        cells = []
        seed(f.sim.id32('%d'%(f.cfg['seeds']['loc']+self.tags['numCells']+f.net.lastGid)))
        randLocs = rand(self.tags['numCells'], 3)  # create random x,y,z locations
        for icoord, coord in enumerate(['x', 'y', 'z']):
            if coord+'Range' in self.tags:  # if user provided absolute range, convert to normalized
                self.tags[coord+'normRange'] = [float(point) / f.net.params['size'+coord.upper()] for point in self.tags[coord+'Range']]
                print self.tags[coord+'normRange'] 
            if coord+'normRange' in self.tags:  # if normalized range, rescale random locations
                minv = self.tags[coord+'normRange'][0] 
                maxv = self.tags[coord+'normRange'][1] 
                randLocs[:,icoord] = randLocs[:,icoord] * (maxv-minv) + minv
        
        for i in xrange(int(f.rank), f.net.params['scale'] * self.tags['numCells'], f.nhosts):
            gid = f.net.lastGid+i
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
        f.net.lastGid = f.net.lastGid + self.tags['numCells'] 
        return cells

                
    def createCellsDensity(self):
        ''' Create population cells based on density'''
        cellModelClass = f.Cell
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
            
            seed(f.sim.id32('%d' % f.cfg['seeds']['loc']))  # reset random number generator
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
        seed(f.sim.id32('%d'%(f.cfg['seeds']['loc']+self.tags['numCells'])))
        randLocs = rand(self.tags['numCells'], 3)  # create random x,y,z locations
        for icoord, coord in enumerate(['x', 'y', 'z']):
            if coord+'normRange' in self.tags:  # if normalized range, rescale random locations
                minv = self.tags[coord+'normRange'][0] 
                maxv = self.tags[coord+'normRange'][1] 
                randLocs[:,icoord] = randLocs[:,icoord] * (maxv-minv) + minv
            if funcLocs and coordFunc == coord+'norm':  # if locations for this coordinate calcualated using density function
                randLocs[:,icoord] = funcLocs

        if f.cfg['verbose'] and not funcLocs: print 'Volume=%.4f, density=%.2f, numCells=%.0f'%(volume, self.tags['density'], self.tags['numCells'])


        for i in xrange(int(f.rank), self.tags['numCells'], f.nhosts):
            gid = f.net.lastGid+i
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
        f.net.lastGid = f.net.lastGid + self.tags['numCells'] 
        return cells


    def createCellsList(self):
        ''' Create population cells based on list of individual cells'''
        cellModelClass = f.Cell
        cells = []
        self.tags['numCells'] = len(self.tags['cellsList'])
        for i in xrange(int(f.rank), len(self.tags['cellsList']), f.nhosts):
            #if 'cellModel' in self.tags['cellsList'][i]:
            #    cellModelClass = getattr(f, self.tags['cellsList'][i]['cellModel'])  # select cell class to instantiate cells based on the cellModel tags
            gid = f.net.lastGid+i
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
        f.net.lastGid = f.net.lastGid + len(self.tags['cellsList'])
        return cells


    def __getstate__(self): 
        ''' Removes non-picklable h objects so can be pickled and sent via py_alltoall'''
        odict = self.__dict__.copy() # copy the dict since we change it
        odict = f.sim.replaceFuncObj(odict)  # replace h objects with None so can be pickled
        return odict

