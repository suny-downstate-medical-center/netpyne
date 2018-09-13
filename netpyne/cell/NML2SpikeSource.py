"""
cell/NML2SpikeSource.py 

Contains pointCell class 

Contributors: salvadordura@gmail.com
"""
from neuron import h # Import NEURON
from specs import Dict
from .compartCell import CompartCell


###############################################################################
#
# NeuroML2 SPIKE SOURCE CLASS 
#
###############################################################################

class NML2SpikeSource (CompartCell):
    ''' Class for NeuroML2 spiking neuron models: based on CompartCell,
        but the NetCon connects to the mechanism on the one section whose NET_RECEIVE
        block will emit events
    '''
        
    def associateGid (self, threshold = 10.0):
        import sim
        
        if sim.cfg.createNEURONObj: 
            sim.pc.set_gid2node(self.gid, sim.rank) # this is the key call that assigns cell gid to a particular node
         
            nc = h.NetCon(self.secs['soma']['pointps'][self.tags['cellType']].hPointp, None)
                
            #### nc.threshold = threshold  # not used....
            sim.pc.cell(self.gid, nc, 1)  # associate a particular output stream of events
            del nc # discard netcon
        sim.net.gid2lid[self.gid] = len(sim.net.lid2gid)
        sim.net.lid2gid.append(self.gid) # index = local id; value = global id
        
    def initRandom(self):
        import sim
        
        rand = h.Random()
        self.stims.append(Dict())  # add new stim to Cell object
        randContainer = self.stims[-1]
        randContainer['hRandom'] = rand 
        randContainer['type'] = self.tags['cellType'] 
        seed = sim.cfg.seeds['stim']
        randContainer['seed'] = seed 
        self.secs['soma']['pointps'][self.tags['cellType']].hPointp.noiseFromRandom(rand)  # use random number generator 
        sim._init_stim_randomizer(rand, self.tags['pop'], self.tags['cellLabel'], seed)
        randContainer['hRandom'].negexp(1)
        #print("Created Random: %s with %s (%s)"%(rand,seed, sim.cfg.seeds))
    