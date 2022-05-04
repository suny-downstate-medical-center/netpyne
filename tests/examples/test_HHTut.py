import pytest
import sys, os
from netpyne import sim
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')

pkg = 'examples/HHTut/'

@pytest.fixture()
def pkg_setup():
    orig = os.getcwd()
    os.chdir(orig + "/" + pkg)
    yield True
    os.chdir(orig)


class TestHHTut():
    def test_run(self, pkg_setup):
        exec(open("src/init.py").read())
        sim.checkOutput('HHTut')


    def test_export(self, pkg_setup):
        exec(open("src/export.py").read())
