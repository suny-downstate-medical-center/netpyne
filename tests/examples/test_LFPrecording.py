import pytest
import os
import subprocess
import sys
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

from .utils import pkg_setup, NETPYNE_DIR

package_dir = NETPYNE_DIR + '/examples/LFPrecording/'
@pytest.mark.package_data([package_dir, 'mod'])
class TestLFPrecording:
    def test_cell_lfp(self, pkg_setup):
        import src.cell.init
