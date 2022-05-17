import pytest
import subprocess
import sys
from netpyne import sim
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

from .utils import pkg_setup

pkg = 'examples/M1/'

@pytest.mark.package_data(['examples/M1/', '.'])
class TestM1:
    def test_run(self, pkg_setup):
        import M1_run
        sim.checkOutput('M1')

    def test_export(self, pkg_setup):
        import M1_export
