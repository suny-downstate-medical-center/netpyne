import numpy as np
import pytest
import sys
from netpyne import sim, specs
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

@pytest.fixture()
def pkg_setup():
    pass

class TestSynMechParams():

    def test_random(self, pkg_setup):

        netParams = specs.NetParams()
        simConfig = specs.SimConfig()

        netParams.cellParams['PYR'] = {'secs': {'soma': {}}}

        expectedMean, expectedVar = (10, 3)
        expectedRange = (0.8, 1.0)

        netParams.synMechParams['syn'] = {
            'mod': 'Exp2Syn',
            'tau1': f'normal({expectedMean}, {expectedVar})',
            'tau2': f'5 + 10 * uniform({expectedRange[0]}, {expectedRange[1]})',
            'e': 'lognormal(0, 0.01)' # just to check 'lognormal' parsed correctly (not messed with 'normal')
        }
        numCells = 60
        netParams.popParams['src'] = {'cellModel': 'NetStim', 'numCells': 1}
        netParams.popParams['trg'] = {'cellType': 'PYR', 'numCells': numCells}

        netParams.connParams['conn'] = {
            'preConds': {'pop': 'src'},
            'postConds': {'pop': 'trg'},
            'synsPerConn': 20,
            'synMech': 'syn',
            'weight': 0.01
        }

        sim.initialize(netParams, simConfig)
        sim.net.createPops()
        sim.net.createCells()
        conns = sim.net.connectCells()

        flatConns = []
        for conn in conns: flatConns.extend(conn)
        tau1 = [conn['hObj'].syn().tau1 for conn in flatConns]
        tau2 = [conn['hObj'].syn().tau2 for conn in flatConns]

        # ensure tau1 comes from normal distribution with given parameters
        assert np.allclose([expectedMean, expectedVar],
            [np.mean(tau1), np.var(tau1)],
            rtol=0.1), "synMechParams: normal distribution in string function failed"

        # ensure tau2 belongs to range [13.0, 15.0] (i.e. '5 + 10 * uniform(0.8, 1.0))
        assert np.min(tau2) >= 13.0 and np.max(tau2) <= 15.0, "synMechParams: uniform distribution in string function failed"

    def test_vars(self, pkg_setup):

        netParams = specs.NetParams()
        simConfig = specs.SimConfig()

        netParams.sizeX = netParams.sizeY = 100

        somaHalfLen = 6.0
        cellRule = {'secs': {'soma': {}}}
        cellRule['secs']['soma'] = {'geom': {}, 'topol': {}}
        cellRule['secs']['soma']['geom'] = {'pt3d':[]}
        cellRule['secs']['soma']['geom']['pt3d'].append((0, 0, 0, 20))
        cellRule['secs']['soma']['geom']['pt3d'].append((0, 0, somaHalfLen*2, 20))

        # dend from 2 ortogonal parts
        dendPart1 = 6.0
        dendPart2 = 5.0

        expectedDistPath = somaHalfLen + dendPart1 + dendPart2
        expectedDictEuclSquared = (somaHalfLen + dendPart1)**2 + dendPart2**2

        prev = somaHalfLen*2
        cellRule['secs']['dend'] = {'geom': {}, 'topol': {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}}
        cellRule['secs']['dend']['geom'] = {'pt3d':[]}
        cellRule['secs']['dend']['geom']['pt3d'].append((0, 0, prev, 5))
        cellRule['secs']['dend']['geom']['pt3d'].append((0, 0, prev + dendPart1, 5))
        cellRule['secs']['dend']['geom']['pt3d'].append((dendPart2, 0, prev + dendPart1, 5))

        netParams.cellParams['PYR'] = cellRule

        netParams.synMechParams['syn0'] = {
            'mod': 'Exp2Syn',
            'tau1': 'post_x',
            'tau2': 'post_ynorm',
            'e': 0
        }
        netParams.synMechParams['syn1'] = {
            'mod': 'Exp2Syn',
            'tau1': 'post_dist_path',
            'tau2': 'post_dist_euclidean',
            'e': 0
        }

        netParams.popParams['src'] = {'cellType': 'NetStim', 'numCells': 1}
        netParams.popParams['trg'] = {'cellType': 'PYR', 'numCells': 1}

        netParams.connParams['conn0'] = {
            'preConds': {'pop': 'src'},
            'postConds': {'pop': 'trg'},
            'synMech': 'syn0',
            'weight': 0.01
        }
        netParams.connParams['conn1'] = {
            'preConds': {'pop': 'src'},
            'postConds': {'pop': 'trg'},
            'synMech': 'syn1',
            'weight': 0.01,
            'loc': 1.0,
            'sec': 'dend'
        }

        sim.create(netParams, simConfig)

        cellTags = sim.net.cells[1].tags
        for conn in sim.net.cells[1].conns:
            syn = conn.hObj.syn()
            if conn.synMech == 'syn0':
                assert syn.tau1 == cellTags['x'], "synMechParams: post_x variable handled incorrectly in string function"
                assert syn.tau2 == cellTags['ynorm'], "synMechParams: post_ynorm variable handled incorrectly in string function"
            elif conn.synMech == 'syn1':
                # path distance from center of soma
                assert syn.tau1 == expectedDistPath, "synMechParams: post_dist_path variable handled incorrectly in string function"
                # euclidian distance
                assert syn.tau2**2 == expectedDictEuclSquared, "synMechParams: post_dist_euclidean variable handled incorrectly in string function"

