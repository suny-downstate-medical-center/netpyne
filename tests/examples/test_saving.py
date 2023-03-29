import pytest
import sys
from netpyne import sim
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')


from .utils import pkg_setup


@pytest.mark.package_data(['examples/saving', None])
class Test_saving():
    def test_init(self, pkg_setup):
        import src.init
        sim.checkOutput('saving')
