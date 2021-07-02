import pytest
import sys
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

pkg = 'examples/HHTut/'

@pytest.fixture()
def pkg_setup():
    sys.path.append(pkg)
    yield True
    sys.path.remove(pkg)


class TestHHTut():
    def test_run(self, pkg_setup):
        import HHTut_run

    def test_export(self, pkg_setup):
        import HHTut_export
