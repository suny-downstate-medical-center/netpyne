import pytest
import os
import subprocess
import sys
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

from .utils import pkg_setup, NETPYNE_DIR

package_dir = NETPYNE_DIR + '/examples/rxd_net/'
@pytest.mark.package_data([package_dir, 'mod'])
class TestRxdNet:
    def test_init(self, pkg_setup):
        import src.init
