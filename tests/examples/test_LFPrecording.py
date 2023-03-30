import pytest
import os
import subprocess
import sys
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

from .utils import pkg_setup


@pytest.mark.package_data(['examples/LFPrecording/', 'mod'])
class TestLFPrecording:
    def test_cell_lfp(self, pkg_setup):
        import src.cell.init
