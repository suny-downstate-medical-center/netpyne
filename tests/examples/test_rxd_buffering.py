import pytest
import sys
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

from .utils import pkg_setup

@pytest.mark.package_data(['examples/rxd_buffering/', '.'])
class Test_rxd_buffering():
    def test_buffering(self, pkg_setup):
        import src.init
