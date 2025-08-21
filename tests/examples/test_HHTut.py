import pytest
import sys, os
from netpyne import sim
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

from .utils import pkg_setup, NETPYNE_DIR

package_dir = NETPYNE_DIR + '/examples/HHTut/'
@pytest.mark.package_data([package_dir, None])
class TestHHTut():
    def test_run(self, pkg_setup):
        import src.init
        sim.checkOutput('HHTut')


    def test_export(self, pkg_setup):
        import src.export
