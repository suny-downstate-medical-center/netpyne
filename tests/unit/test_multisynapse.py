import pytest
import sys
from netpyne import sim, specs
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

@pytest.fixture()
def pkg_setup():
    pass

class TestMultiSynapse():

    def setUp(self):
        netParams = specs.NetParams()
        simConfig = specs.SimConfig()

        netParams.popParams['src'] = {'cellType': 'PYR', 'numCells': 1} # add dict with params for this pop
        netParams.popParams['dst'] = {'cellType': 'PYR', 'numCells': 3} # add dict with params for this pop

        # Cell parameters
        ## PYR cell properties
        PYRcell = {'secs': {}} # cell rule dict
        PYRcell['secs']['soma'] = {'geom': {}, 'mechs': {}} # soma params dict
        PYRcell['secs']['soma']['geom'] = {'diam': 18.8, 'L': 10.0, 'Ra': 123.0} # soma geometry
        PYRcell['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70} # soma hh mechanism
        PYRcell['secs']['soma']['vinit'] = -71 # set initial membrane potential

        from copy import deepcopy
        dend = deepcopy(PYRcell['secs']['soma'])
        dend['geom']['L'] = 20
        PYRcell['secs']['dend'] = dend

        adend = deepcopy(PYRcell['secs']['soma'])
        dend['geom']['L'] = 20
        PYRcell['secs']['adend'] = adend

        bdend = deepcopy(PYRcell['secs']['soma'])
        dend['geom']['L'] = 20
        PYRcell['secs']['bdend'] = bdend

        netParams.cellParams['PYR'] = PYRcell # add dict to list of cell params


        # Synaptic mechanism parameters
        netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': 0}
        netParams.synMechParams['GABA'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': -70}

        return netParams, simConfig


    # [1] synsPerConn > 1, single section specified
    def test_one_pos(self, pkg_setup): # loc not specified, distribute uniformly
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synsPerConn': 2,
            'weight': [0.1, 0.2],
            'delay': 0.1,
        }

        sim.create(netParams = netParams, simConfig = simConfig)

        conns = sim.net.cells[sim.net.pops['dst'].cellGids[0]].conns

        assert conns[0].weight == 0.1
        assert conns[1].weight == 0.2

        assert conns[0].delay == 0.1
        assert conns[1].delay == 0.1

        assert conns[0].loc == 0.25
        assert conns[1].loc == 0.75

    def test_one_pos2(self, pkg_setup): # loc as list of correct length
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synsPerConn': 2,
            'weight': [0.1, 0.2],
            'delay': 0.1,
            'loc': [0.5, 1.0]
        }

        sim.create(netParams = netParams, simConfig = simConfig)

        conns = sim.net.cells[sim.net.pops['dst'].cellGids[0]].conns

        assert conns[0].weight == 0.1
        assert conns[1].weight == 0.2

        assert conns[0].delay == 0.1
        assert conns[1].delay == 0.1

        assert conns[0].loc == 0.5
        assert conns[1].loc == 1.0

    def test_one_neg(self, pkg_setup): # loc as a single value
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synsPerConn': 2,
            'weight': [0.1, 0.2],
            'delay': 0.1,
            'loc': 0.5
        }

        try:
            sim.create(netParams = netParams, simConfig = simConfig)
        except Exception as e:
            return
        assert False, "This scenario should generate exception"

    # [2] synsPerConn > 1, single section specified

    def test_two_pos(self, pkg_setup):
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synsPerConn': 2,
            'loc': [0.3, 0.6]
        }

        sim.create(netParams = netParams, simConfig = simConfig)

        conns = sim.net.cells[sim.net.pops['dst'].cellGids[0]].conns

        assert conns[0].loc == 0.3
        assert conns[1].loc == 0.6

    def test_two_neg(self, pkg_setup): # loc as wrong size list
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synsPerConn': 2,
            'loc': [0.3]
        }
        try:
            sim.create(netParams = netParams, simConfig = simConfig)
        except Exception as e:
            return
        assert False, "This scenario should generate exception"

    def test_two_neg2(self, pkg_setup):  # loc as a single value
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synsPerConn': 2,
            'loc': 0.3
        }

        try:
            sim.create(netParams = netParams, simConfig = simConfig)
        except Exception as e:
            return
        assert False, "This scenario should generate exception"

    # [3] synsPerConn > 1 and list of sections specified (distributeSynsUniformly is True by default)
    def test_three_pos(self, pkg_setup):
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synsPerConn': 5,
            'sec': ['soma', 'dend']
        }

        sim.create(netParams = netParams, simConfig = simConfig)

        conns = sim.net.cells[sim.net.pops['dst'].cellGids[0]].conns
        secs = [conn['sec'] for conn in conns]
        locs = [conn['loc'] for conn in conns]
        
        assert secs == ['soma', 'soma', 'dend', 'dend', 'dend']
        assert locs == [0.7, 0.1, 0.75, 0.45, 0.15]


    def test_three_neg(self, pkg_setup): # loc as a single value
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synsPerConn': 5,
            'sec': ['soma', 'dend'],
            'loc': 0.5
        }

        try:
            sim.create(netParams = netParams, simConfig = simConfig)
        except Exception as e:
            return
        assert False, "This scenario should generate exception"

    # [4] distributeSynsUniformly == False (connRandomSecFromList is True by default)
    def test_four_pos(self, pkg_setup):
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synsPerConn': 3,
            'sec': ['soma', 'dend', 'dend'],
            'loc': [0.3, 0.6, 0.9],
            'distributeSynsUniformly': False, # can also be set globally in simConfig
        }

        sim.create(netParams = netParams, simConfig = simConfig)

        conns = sim.net.cells[sim.net.pops['dst'].cellGids[0]].conns
        secs = [conn['sec'] for conn in conns]
        locs = [conn['loc'] for conn in conns]

        # randomly chosen (with replacement in this case)
        assert secs == ['dend', 'dend', 'soma']
        assert locs == [0.9, 0.3, 0.6]


    def test_four_pos2(self, pkg_setup): # providing arbitrary number of secs/locs allowed
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synsPerConn': 3,
            'sec': ['soma', 'dend'],
            'loc': [0.3, 0.6, 0.9, 1.0],
            'distributeSynsUniformly': False, # can also be set globally in simConfig
        }
        sim.create(netParams = netParams, simConfig = simConfig)

        conns = sim.net.cells[sim.net.pops['dst'].cellGids[0]].conns
        secs = [conn['sec'] for conn in conns]
        locs = [conn['loc'] for conn in conns]

        # randomly chosen (potentially with replacement in this case)
        assert secs == ['soma', 'soma', 'dend']
        assert locs == [1.0, 0.6, 0.9]

    def test_four_pos3(self, pkg_setup): # providing no loc is allowed and results in random uniform(0, 1)
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synsPerConn': 2,
            'sec': ['soma', 'dend'],
            'distributeSynsUniformly': False, # can also be set globally in simConfig
        }
        sim.create(netParams = netParams, simConfig = simConfig)

        conns = sim.net.cells[sim.net.pops['dst'].cellGids[0]].conns
        secs = [conn['sec'] for conn in conns]
        locs = [conn['loc'] for conn in conns]

        # randomly chosen (potentially with replacement in this case)
        assert secs == ['soma', 'dend']
        assert locs == [0.877143270597527, 0.3635414011395673]

    def test_four_neg(self, pkg_setup): # providing single value for loc results in error
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synsPerConn': 3,
            'sec': ['soma', 'dend'],
            'loc': 0.3,
            'distributeSynsUniformly': False, # can also be set globally in simConfig
        }
        try:
            sim.create(netParams = netParams, simConfig = simConfig)
        except Exception as e:
            return
        assert False, "This scenario should generate exception"


    # [5] connRandomSecFromList = False
    def test_five_pos(self, pkg_setup):
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synsPerConn': 3,
            'sec': ['soma', 'dend', 'dend'],
            'loc': [0.3, 0.6, 0.9],
            'distributeSynsUniformly': False, # can also be set globally in simConfig
            'connRandomSecFromList': False, # can also be set globally in simConfig
        }

        sim.create(netParams = netParams, simConfig = simConfig)

        conns = sim.net.cells[sim.net.pops['dst'].cellGids[0]].conns
        secs = [conn['sec'] for conn in conns]
        locs = [conn['loc'] for conn in conns]

        # randomly chosen (with replacement in this case)
        assert secs == ['soma', 'dend', 'dend']
        assert locs == [0.3, 0.6, 0.9]

    # sec or/and loc len doesn't correspond tp synsPerConn -> error
    def test_five_neg(self, pkg_setup):
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synsPerConn': 3,
            'sec': ['soma', 'dend'],
            'loc': [0.3, 0.6, 0.9],
            'distributeSynsUniformly': False, # can also be set globally in simConfig
            'connRandomSecFromList': False, # can also be set globally in simConfig
        }
        try:
            sim.create(netParams = netParams, simConfig = simConfig)
        except Exception as e:
            return
        assert False, "This scenario should generate exception"

    def test_five_neg2(self, pkg_setup): # wrong lenght of locations list
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synsPerConn': 3,
            'sec': ['soma', 'dend', 'dend'],
            'loc': [0.3, 0.6, 0.9, 1.0],
            'distributeSynsUniformly': False, # can also be set globally in simConfig
            'connRandomSecFromList': False, # can also be set globally in simConfig
        }
        try:
            sim.create(netParams = netParams, simConfig = simConfig)
        except Exception as e:
            return
        assert False, "This scenario should generate exception"

    # [6] synsPerConn == 1 and list of sections specified
    def test_six_pos(self, pkg_setup):
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synsPerConn': 1,
            'sec': ['soma', 'dend', 'adend', 'bdend'],
            'loc': [0.1, 0.2, 0.3, 0.4],
            'connRandomSecFromList': True, # can also be set globally in simConfig
        }

        sim.create(netParams = netParams, simConfig = simConfig)

        # unlike previous test, here we collect values from different conns
        dstCellGids = sim.net.pops['dst'].cellGids
        conns = [sim.net.cells[gid].conns[0] for gid in dstCellGids]

        secs = [conn['sec'] for conn in conns]
        locs = [conn['loc'] for conn in conns]

        assert secs == ['adend', 'soma', 'bdend']
        assert locs == [0.3, 0.1, 0.4]

    def test_six_pos2(self, pkg_setup): # use alway first sec and loc from list
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synsPerConn': 1,
            'sec': ['soma', 'dend', 'adend', 'bdend'],
            'loc': [0.1, 0.2, 0.3, 0.4],
            'connRandomSecFromList': False, # can also be set globally in simConfig
        }

        sim.create(netParams = netParams, simConfig = simConfig)

        # unlike previous test, here we collect values from different conns
        dstCellGids = sim.net.pops['dst'].cellGids
        conns = [sim.net.cells[gid].conns[0] for gid in dstCellGids]

        secs = [conn['sec'] for conn in conns]
        locs = [conn['loc'] for conn in conns]

        assert secs == ['soma', 'soma', 'soma']
        assert locs == [0.1, 0.1, 0.1]


    def test_six_neg(self, pkg_setup): # len of secs and locs don't match
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synsPerConn': 1,
            'sec': ['soma', 'dend', 'adend', 'bdend'],
            'loc': [0.1, 0.2],
            'connRandomSecFromList': True, # can also be set globally in simConfig
        }
        try:
            sim.create(netParams = netParams, simConfig = simConfig)
        except Exception as e:
            return
        assert False, "This scenario should generate exception"

    # [7] multiple synMechs

    def test_seven_pos(self, pkg_setup): # weight/delay/loc can be either single value or list of same length as synMech
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synMech': ['AMPA', 'GABA'],
            'loc': [0.1, 0.2],
            'weight': 3,
            'delay': [1, 2]
        }

        sim.create(netParams = netParams, simConfig = simConfig)
        conns = sim.net.cells[sim.net.pops['dst'].cellGids[0]].conns
        
        synMechs = [conn['synMech'] for conn in conns]
        locs = [conn['loc'] for conn in conns]
        weights = [conn['weight'] for conn in conns]
        dels = [conn['delay'] for conn in conns]

        assert synMechs == ['AMPA', 'GABA']
        assert locs == [0.1, 0.2]
        assert weights == [3, 3]
        assert dels == [1, 2]


    def test_seven_neg(self, pkg_setup): # wrong length of list of weights
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synMech': ['AMPA', 'GABA'],
            'weight': [3],
        }
        try:
            sim.create(netParams = netParams, simConfig = simConfig)
        except Exception as e:
            return
        assert False, "This scenario should generate exception"

    # [8] multiple synMechs, multyple synsPerConns
    # weight/delay/loc's outer dimension should correspond to synMech, for inner dimension same rules as for [1]-[6] apply.

    def test_eight_pos(self, pkg_setup):
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synMech': ['AMPA', 'GABA'],
            'synsPerConn': 3,
            'weight': 3, # will be used for all synapses of all synMechs
            'delay': [1, 2], # 1 to be used with all synapses of 1st synMech, 2 - for the 2nd
            'loc': [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]], # all values listed will be used
            'distributeSynsUniformly': False,
            'connRandomSecFromList': False
        }

        sim.create(netParams = netParams, simConfig = simConfig)
        conns = sim.net.cells[sim.net.pops['dst'].cellGids[0]].conns
        
        synMechs = [conn['synMech'] for conn in conns]
        locs = [conn['loc'] for conn in conns]
        weights = [conn['weight'] for conn in conns]
        dels = [conn['delay'] for conn in conns]

        assert synMechs == ['AMPA', 'AMPA', 'AMPA',
                            'GABA', 'GABA', 'GABA']
        assert weights == [3, 3, 3,
                        3, 3, 3]
        assert dels == [1, 1, 1,
                        2, 2, 2]
        assert locs == [0.1, 0.2, 0.3,
                        0.4, 0.5, 0.6] # because it is distributeSynsUniformaly by default


    def test_eight_pos2(self, pkg_setup):
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synMech': ['AMPA', 'GABA'],
            'synsPerConn': 3,
            # 'distributeSynsUniformly': True, # it is here by default
        }

        sim.create(netParams = netParams, simConfig = simConfig)
        conns = sim.net.cells[sim.net.pops['dst'].cellGids[0]].conns
        locs = [conn['loc'] for conn in conns]

        assert locs == [0.16666666666666666, 0.5, 0.8333333333333333, 0.16666666666666666, 0.5, 0.8333333333333333]

    def test_eight_pos3(self, pkg_setup): # connRandomSecFromList is True, and there are several sections: locs are randomized along with secs
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synMech': ['AMPA', 'GABA'],
            'sec': ['soma', 'adend', 'bdend'],
            'synsPerConn': 3,
            'loc': [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            'distributeSynsUniformly': False,
            # 'connRandomSecFromList': True, # it is here by default
        }

        sim.create(netParams = netParams, simConfig = simConfig)
        conns = sim.net.cells[sim.net.pops['dst'].cellGids[0]].conns
        locs = [conn['loc'] for conn in conns]
        secs = [conn['sec'] for conn in conns]

        assert locs == [0.3, 0.1, 0.2, 0.6, 0.4, 0.5] # locs are randomized
        assert secs == ['adend', 'bdend', 'soma',
                        'adend', 'bdend', 'soma'] # note that same sections list is used for each synMech (not one-to-one as for weight/delay)

    def test_eight_pos4(self, pkg_setup): # connRandomSecFromList is True, but section is only one: locs are not randomized
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synMech': ['AMPA', 'GABA'],
            # 'sec': 'soma', # it is here by default
            'synsPerConn': 3,
            'loc': [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            'distributeSynsUniformly': False,
            # 'connRandomSecFromList': True, # it is here by default
        }
        sim.create(netParams = netParams, simConfig = simConfig)
        conns = sim.net.cells[sim.net.pops['dst'].cellGids[0]].conns
        locs = [conn['loc'] for conn in conns]

        assert locs == [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]


    def test_eight_pos5(self, pkg_setup):
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synMech': ['AMPA', 'GABA'],
            'synsPerConn': [3, 2],
            'delay': [[1, 1, 1], [2, 2]],
        }
        sim.create(netParams = netParams, simConfig = simConfig)
        conns = sim.net.cells[sim.net.pops['dst'].cellGids[0]].conns
        
        synMechs = [conn['synMech'] for conn in conns]
        dels = [conn['delay'] for conn in conns]

        assert synMechs == ['AMPA', 'AMPA', 'AMPA',
                            'GABA', 'GABA']
        assert dels == [1, 1, 1,
                        2, 2]

    def test_eight_neg(self, pkg_setup): # weight/delay has wrong size
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synMech': ['AMPA', 'GABA', 'GABA'],
            'weight': [3, 2],
        }
        try:
            sim.create(netParams = netParams, simConfig = simConfig)
        except Exception as e:
            return
        assert False, "This scenario should generate exception"

    def test_eight_neg2(self, pkg_setup): # synsPerConn has wrong size
        netParams, simConfig = self.setUp()

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'synMech': ['AMPA', 'GABA'],
            'synsPerConn': [3],
        }
        try:
            sim.create(netParams = netParams, simConfig = simConfig)
        except Exception as e:
            return
        assert False, "This scenario should generate exception"

    # [9] fromListConn 
    def test_nine_pos(self, pkg_setup):
        netParams, simConfig = self.setUp()
        netParams.popParams['src'] = {'cellType': 'PYR', 'numCells': 2} # add dict with params for this pop

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'connList': [[0,0], [1,0]],
            'delay': 2,
            'weight': [0.1, 0.2],
        }

        sim.create(netParams = netParams, simConfig = simConfig)
        conns = sim.net.cells[sim.net.pops['dst'].cellGids[0]].conns
        
        weights = [conn['weight'] for conn in conns]
        delays = [conn['delay'] for conn in conns]

        assert weights == [0.1, 0.2]
        assert delays == [2, 2]

    def test_nine_pos2(self, pkg_setup): # + multiple synMech + multiple synsPerConn
        netParams, simConfig = self.setUp()
        netParams.popParams['src'] = {'cellType': 'PYR', 'numCells': 2} # add dict with params for this pop

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'connList': [[0,0], [1,0]],
            'synMech': ['AMPA', 'GABA'],
            'synsPerConn': 3,
            'weight': [[[1, 2, 3], [4, 5, 6]], # first conn: AMPA, GABA, 3 synsPerConn each
                    [[7, 8, 9], [10, 11, 12]]],  # second conn: AMPA, GABA (...)

            'delay': [[0.1, 0.2], # first conn: AMPA, GABA, same for all syns in synsPerConn
                    [0.3, 0.4]],  # second conn: AMPA, GABA (...)
        }

        sim.create(netParams = netParams, simConfig = simConfig)
        conns = sim.net.cells[sim.net.pops['dst'].cellGids[0]].conns
        
        synMechs = [conn['synMech'] for conn in conns]
        weights = [conn['weight'] for conn in conns]
        delays = [conn['delay'] for conn in conns]
        preGids = [conn['preGid'] for conn in conns]

        assert len(conns) == 12 # 2 conns X 2 synMech X 3 synsPerConn

        # first conn
        assert preGids[:6] == [0] * 6 # 2 synMech X 3 synsPerConn
        assert synMechs[:6] == ['AMPA', 'AMPA', 'AMPA',
                                'GABA', 'GABA', 'GABA']
        assert weights[:6] == [1, 2, 3, 4, 5, 6]
        assert delays[:6] == [0.1, 0.1, 0.1, 0.2, 0.2, 0.2]

        # second conn
        assert preGids[6:] == [1] * 6 # 2 synMech X 3 synsPerConn
        assert synMechs[6:] == ['AMPA', 'AMPA', 'AMPA',
                                'GABA', 'GABA', 'GABA']
        assert weights[6:] == [7, 8, 9, 10, 11, 12]
        assert delays[6:] == [0.3, 0.3, 0.3, 0.4, 0.4, 0.4]


    def test_nine_neg(self, pkg_setup):
        netParams, simConfig = self.setUp()
        netParams.popParams['src'] = {'cellType': 'PYR', 'numCells': 2} # add dict with params for this pop

        netParams.connParams['PYR->PYR'] = {
            'preConds': {'pop': 'src'}, 'postConds': {'pop': 'dst'},
            'connList': [[0,0], [1,0]],
            'synMech': ['AMPA', 'GABA', 'GABA'],
            'synsPerConn': 2,
            'weight': [[1, 2],  # first conn. 3-elements list expected (because there are 3 syn mechs)
                    [3, 4]],  # second conn (the same as above)
        }
        try:
            sim.create(netParams = netParams, simConfig = simConfig)
        except Exception as e:
            return
        assert False, "This scenario should generate exception"

# if __name__ == '__main__':
#     includeObsolete = True
#     test_one_pos()
#     test_one_pos2()
#     if includeObsolete: test_one_neg() # now generates error

#     test_two_pos()
#     if includeObsolete: test_two_neg() # now generates error
#     if includeObsolete: test_two_neg2() # now generates error

#     test_three_pos()
#     if includeObsolete: test_three_neg() # now generates error

#     test_four_pos()
#     if includeObsolete: test_four_pos2() # no longer an error
#     test_four_pos3()
#     test_four_neg()

#     test_five_pos()
#     test_five_neg()
#     test_five_neg2()

#     if includeObsolete: test_six_pos() # order bug fixed
#     test_six_pos2()
#     test_six_neg()

#     test_seven_pos()
#     test_seven_neg()

#     test_eight_pos()
#     test_eight_pos2()
#     if includeObsolete: test_eight_pos3() # order bug fixed
#     test_eight_pos4()
#     if includeObsolete: test_eight_pos5() # no longer an error

#     test_eight_neg()
#     test_eight_neg2()

#     test_nine_pos()
#     test_nine_pos2()
#     test_nine_neg()


