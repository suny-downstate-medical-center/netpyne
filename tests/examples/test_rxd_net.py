import pytest
import os
import subprocess
import sys
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

from .utils import pkg_setup


@pytest.mark.package_data(['examples/rxd_net/', 'mod'])
class TestRxdNet:
    def test_init(self, pkg_setup):
        import src.init
