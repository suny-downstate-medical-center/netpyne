import pytest
import sys
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

pkg = 'examples/rxd_buffering/'

@pytest.fixture()
def simple_pkg_setup():
    sys.path.append(pkg)
    yield True
    sys.path.remove(pkg)


class Test_rxd_buffering():
    def test_buffering(self, simple_pkg_setup):
        import buffering
