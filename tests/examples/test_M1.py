import pytest
import subprocess
import sys
from netpyne import sim
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

from .utils import pkg_setup, NETPYNE_DIR

package_dir = NETPYNE_DIR + '/examples/M1/'
@pytest.mark.package_data([package_dir, 'mod'])
class TestM1:
    def test_run(self, pkg_setup):
        import src.init
        sim.checkOutput('M1')

    def test_export(self, pkg_setup):
        import src.export
