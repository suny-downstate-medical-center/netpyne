import pytest
import os
import sys
from netpyne import sim
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

from .utils import pkg_setup

@pytest.mark.package_data(['examples/HybridTut/', '.'])
class TestHybridTut:
    def test_run(self, pkg_setup):
        import HybridTut_run
        sim.checkOutput('HybridTut')

    def test_export(self, pkg_setup):
        import HybridTut_export
