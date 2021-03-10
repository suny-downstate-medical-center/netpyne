"""
Module containing NeuroML2 spike source class

"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from neuron import h # Import NEURON
from .compartCell import CompartCell
from ..specs import Dict


###############################################################################
#
# NeuroML2 SPIKE SOURCE CLASS
#
###############################################################################

class NML2SpikeSource(CompartCell):
    """
    Class for/to <short description of `netpyne.cell.NML2SpikeSource.NML2SpikeSource`>

    """

    def associateGid(self, threshold = 10.0):
        from .. import sim

        if sim.cfg.createNEURONObj:
            sim.pc.set_gid2node(self.gid, sim.rank) # this is the key call that assigns cell gid to a particular node

            nc = h.NetCon(self.secs['soma']['pointps'][self.tags['cellType']].hObj, None)

            #### nc.threshold = threshold  # not used....
            sim.pc.cell(self.gid, nc, 1)  # associate a particular output stream of events
            del nc # discard netcon
        sim.net.gid2lid[self.gid] = len(sim.net.gid2lid)

    def initRandom(self):
        from .. import sim

        rand = h.Random()
        self.stims.append(Dict())  # add new stim to Cell object
        randContainer = self.stims[-1]
        randContainer['hRandom'] = rand
        randContainer['type'] = self.tags['cellType']
        seed = sim.cfg.seeds['stim']
        randContainer['seed'] = seed
        self.secs['soma']['pointps'][self.tags['cellType']].hObj.noiseFromRandom(rand)  # use random number generator
        sim._init_stim_randomizer(rand, self.tags['pop'], self.tags['cellLabel'], seed)
        randContainer['hRandom'].negexp(1)
        #print("Created Random: %s with %s (%s)"%(rand,seed, sim.cfg.seeds))

    pass
