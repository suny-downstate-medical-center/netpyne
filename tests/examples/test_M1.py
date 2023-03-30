import pytest
import subprocess
import sys
from netpyne import sim
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

from .utils import pkg_setup


@pytest.mark.package_data(['examples/M1/', 'mod'])
class TestM1:
    def test_run(self, pkg_setup):
        import src.init
        sim.checkOutput('M1')

    def test_export(self, pkg_setup):
        import src.export
