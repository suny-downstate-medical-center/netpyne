import pytest
import os
import subprocess
import sys
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

from .utils import pkg_setup


@pytest.mark.package_data(['examples/PTcell/', 'mod'])
class TestPTcell:
    def test_init(self, pkg_setup):
        import init
        from netpyne import sim
        sim.checkOutput('PTcell')
