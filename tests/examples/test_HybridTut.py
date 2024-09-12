import pytest
import os
import sys
from netpyne import sim
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

from .utils import pkg_setup, NETPYNE_DIR

package_dir = NETPYNE_DIR + '/examples/HybridTut/'

@pytest.mark.package_data([package_dir, 'mod'])
class TestHybridTut:
    def test_run(self, pkg_setup):
        import src.init
        sim.checkOutput('HybridTut')

    def test_export(self, pkg_setup):
        import src.export
