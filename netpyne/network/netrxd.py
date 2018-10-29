
"""
network/rxd.py 

Network class methods to add RxD  

Contributors: salvadordura@gmail.com
"""
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from builtins import dict
from builtins import range

from builtins import round
from future import standard_library
standard_library.install_aliases()
import numpy as np 



# -----------------------------------------------------------------------------
# Add RxD
# -----------------------------------------------------------------------------
def addRxD (self):
    from .. import sim

    if len(self.params.rxdParams):
        try:
            global rxd
            from neuron import crxd as rxd 
            sim.net.rxd = {'species': {}, 'regions': {}}  # dictionary for rxd  
        except:
            print('cRxD module not available')
            return -1
    else:
        return -1


    # Instantiate network connections based on the connectivity rules defined in params
    sim.timing('start', 'rxdTime')
    if sim.rank==0: 
        print('Adding RxD...')

    if sim.nhosts > 1: # Gather tags from all cells 
        allCellTags = sim._gatherAllCellTags()  
    else:
        allCellTags = {cell.gid: cell.tags for cell in self.cells}
    allPopTags = {-i: pop.tags for i,pop in enumerate(self.pops.values())}  # gather tags from pops so can connect NetStim pops

    # make copy of Python structure
    #if sim.cfg.createPyStruct: -- don't make conditional since need to have Python structure
    sim.net.rxd = sim.net.params.rxdParams

    # add NEURON objects
    if sim.cfg.createNEURONObj:
        for rxdParamLabel,rxdParam in self.params.rxdParams.items():  # for each conn rule or parameter set
            if rxdParamLabel == 'species':
                self.addSpecies(rxdParam)
            elif rxdParamLabel == 'region':
                self.addRegions(rxdParam)
            elif rxdParamLabel == 'reaction':
                self.addReactions(rxdParam)
            elif rxdParamLabel == 'multicompartmentReaction':
                self.addMulticompartmentReactions(rxdParam)
            elif rxdParamLabel == 'rate':
                self.addRates(rxdParam)
            elif rxdParamLabel == 'extracellular':
                self.addExtracellular(rxdParam)

    sim.pc.barrier()
    sim.timing('stop', 'add RxD')
    if sim.rank == 0 and sim.cfg.timing: print(('  Done; RxD setup time = %0.2f s.' % sim.timingData['rxdTime']))

    return sim.net.rxd


# -----------------------------------------------------------------------------
# Add RxD
# -----------------------------------------------------------------------------
def addSpecies(params):
    from .. import sim

    for speciesLabel, speciesParams in params:
        pass
    #secs=None, nrn_region=None, geometry=None, dimension=None, dx=None, name=None



        # find pre and post cells that match conditions
        #preCellsTags, postCellsTags = self._findPrePostCellsCondition(allCellTags, connParam['preConds'], connParam['postConds'])
