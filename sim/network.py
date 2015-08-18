
"""
network.py 

Contains cell and population classes 

Contributors: salvadordura@gmail.com
"""

###############################################################################
### IMPORT MODULES
###############################################################################

from neuron import h  # import NEURON
from pylab import seed, rand, sqrt, exp, transpose, ceil, concatenate, array, zeros, ones, vstack, show, disp, mean, inf, concatenate
from time import time, sleep
import pickle
import warnings

import params as p  # Import all shared variables and parameters
import shared as s

warnings.filterwarnings('error')


###############################################################################
### Instantiate network populations (objects of class 'Pop')
###############################################################################
def createPops():
    s.pops = []  # list to store populations ('Pop' objects)
    for popParam in p.net['popParams']: # for each set of population parameters 
        s.pops.append(s.Pop(popParam))  # instantiate a new object of class Pop and add to list pop


###############################################################################
### Create Cells
###############################################################################
def createCells():
    s.pc.barrier()
    if s.rank==0: print("\nCreating simulation of %i cell populations for %0.1f s on %i hosts..." % (len(s.pops),p.sim['duration']/1000.,s.nhosts)) 
    s.gidVec=[] # Empty list for storing GIDs (index = local id; value = gid)
    s.gidDic = {} # Empty dict for storing GIDs (key = gid; value = local id) -- ~x6 faster than gidVec.index()  
    s.cells = []
    for ipop in s.pops: # For each pop instantiate the network cells (objects of class 'Cell')
        newCells = ipop.createCells() # create cells for this pop using Pop method
        s.cells.extend(newCells)  # add to list of cells
        s.pc.barrier()
        if s.rank==0 and p.sim['verbose']: print('Instantiated %d cells of population %d'%(ipop.numCells, ipop.popgid))           
    s.simdata.update({name:h.Vector(1e4).resize(0) for name in ['spkt','spkid']})
    print('  Number of cells on node %i: %i ' % (s.rank,len(s.cells)))            
    

###############################################################################
### Connect Cells
###############################################################################
def connectCells():
    # Instantiate network connections (objects of class 'Conn') - connects object cells based on pre and post cell's type, class and yfrac
    if s.rank==0: print('Making connections...'); connstart = time()

    if p.net['connType'] == 'random':  # if random connectivity
        connClass = s.RandConn  # select ConnRand class
        arg = p.net['ncell']  # pass as argument num of presyn cell
    
    elif p.net['connType'] == 'yfrac':  # if yfrac-based connectivity
        connClass = s.YfracConn  # select ConnYfrac class
        data = [s.cells]*s.nhosts  # send cells data to other nodes
        gather = s.pc.py_alltoall(data)  # collect cells data from other nodes (required to generate connections)
        s.pc.barrier()
        allCells = []
        for x in gather:    allCells.extend(x)  # concatenate cells data from all nodes
        del gather, data  # removed unnecesary variables
        allCellsGids = [x.gid for x in allCells] # order gids
        allCells = [x for (y,x) in sorted(zip(allCellsGids,allCells))]
        arg = allCells  # pass as argument the list of presyn cell objects

    s.conns = []  # list to store connections   
    for ipost in s.cells: # for each postsynaptic cell in this node
        newConns = connClass.connect(arg, ipost)  # calculate all connections
        if newConns: s.conns.extend(newConns)  # add to list of connections in this node
    
    print('  Number of connections on host %i: %i ' % (s.rank, len(s.conns)))
    s.pc.barrier()
    if s.rank==0: conntime = time()-connstart; print('  Done; time = %0.1f s' % conntime) # See how long it took


###############################################################################
### Add background inputs
###############################################################################
def addBackground():
    if s.rank==0: print('Creating background inputs...')
    for c in s.cells: 
        c.addBackground()
    print('  Number created on host %i: %i' % (s.rank, len(s.cells)))
    s.pc.barrier()





