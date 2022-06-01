import pytest
import sys
from netpyne import sim
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

pkg = 'examples/saving/'

@pytest.fixture()
def pkg_setup():
    sys.path.append(pkg)
    yield True
    sys.path.remove(pkg)


class Test_saving():
    def test_init(self, pkg_setup):
        import init
        sim.checkOutput('saving')
