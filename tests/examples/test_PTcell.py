import pytest
import os
import subprocess
import sys
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

from .utils import pkg_setup, NETPYNE_DIR

package_dir = NETPYNE_DIR + '/examples/PTcell/'
@pytest.mark.package_data([package_dir, 'mod'])
class TestPTcell:
    def test_init(self, pkg_setup):
        import src.init
        from netpyne import sim
        sim.checkOutput('PTcell')
