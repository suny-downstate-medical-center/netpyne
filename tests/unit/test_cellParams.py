import numpy as np
import pytest
import sys
from netpyne import sim, specs
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

@pytest.fixture()
def pkg_setup():
    pass

class TestCellParams():

    def test_vars(self, pkg_setup):

        netParams = specs.NetParams()
        simConfig = specs.SimConfig()

        cellRule = {'secs': {'soma': {}}}
        cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}
        cellRule['secs']['soma']['geom'] = {'diam': 'x', 'nseg': 'int(discunif(3,3))'}
        cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 'xnorm', 'gkbar': 'ynorm', 'gl': 'znorm'}
        # cellRule['secs']['soma']['mechs']['pas'] = {'g': 'dist_path', 'e': 'dist_euclidean'}

        cellRule['secs']['dend'] = {'geom': {}, 'topol': {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}, 'pointps': {}}
        cellRule['secs']['dend']['pointps']['intFire'] = {'mod': 'IntFire1', 'tau': 'y'}
        netParams.cellParams['PYR'] = cellRule

        netParams.cellParams['IF'] = {'cellModel': 'IntFire1', 'params': {
            'tau': 'z'
        }}

        netParams.popParams['pyr'] = {'cellType': 'PYR', 'numCells': 1}
        netParams.popParams['intFire'] = {'cellType': 'IF', 'numCells': 1}

        sim.create(netParams, simConfig)

        obj = sim.net.cells[0].secs.soma.hObj
        tags = sim.net.cells[0].tags
        assert obj.diam == tags['x'], 'CompartCell params: variable in geom params string function handled incorrectly (x)'
        assert obj.nseg == 3, 'CompartCell params: nseg in geom params string function handled incorrectly'

        seg = obj(0.5)
        assert seg.gnabar_hh == tags['xnorm'], "CompartCell params: variable in 'mechs' params string function handled incorrectly (xnorm)"
        assert seg.gkbar_hh == tags['ynorm'], "CompartCell params: variable in 'mechs' params string function handled incorrectly (ynorm)"
        assert seg.gl_hh == tags['znorm'], "CompartCell params: variable in 'mechs' params string function handled incorrectly (znorm)"

        obj = sim.net.cells[0].secs.dend.pointps['intFire'].hObj
        assert obj.tau == tags['y'], "CompartCell params: variable in 'pointps' params string function handled incorrectly (x)"

        obj = sim.net.cells[1].hPointp
        tags = sim.net.cells[1].tags
        assert obj.tau == tags['z'], 'PointCells params: variable handled incorrectly in string function (z)'
