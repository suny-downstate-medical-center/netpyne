import pytest
import sys
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

from .utils import pkg_setup, NETPYNE_DIR

package_dir = NETPYNE_DIR + '/examples/rxd_buffering/'
@pytest.mark.package_data([package_dir, None])
class Test_rxd_buffering():
    def test_buffering(self, pkg_setup):
        import src.init
