import pytest
import os
import subprocess
import sys
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

from .utils import pkg_setup, NETPYNE_DIR

package_dir = NETPYNE_DIR + '/examples/NeuroMLImport/'
@pytest.mark.package_data([package_dir, '.'])
class TestPTcell:
    def test_init(self, pkg_setup):
        import SimpleNet_import
