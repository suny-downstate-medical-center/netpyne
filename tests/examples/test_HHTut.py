import pytest
import sys, os
from netpyne import sim
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

from .utils import pkg_setup

@pytest.mark.package_data(['examples/HHTut/', '.'])
class TestHHTut():
    def test_run(self, pkg_setup):
        import src.init
        sim.checkOutput('HHTut')


    def test_export(self, pkg_setup):
        import src.export
