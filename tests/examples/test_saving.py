import pytest
import sys
from netpyne import sim
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')


from .utils import pkg_setup, NETPYNE_DIR

package_dir = NETPYNE_DIR + '/examples/saving/'
@pytest.mark.package_data([package_dir, None])
class Test_saving():
    def test_init(self, pkg_setup):
        import src.init
        sim.checkOutput('saving')
