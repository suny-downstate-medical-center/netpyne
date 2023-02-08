import pytest
import sys
from netpyne import sim
from netpyne.conversion import createPythonScript, createPythonNetParams, createPythonSimConfig
import __main__
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')
from tests.examples.utils import pkg_setup

@pytest.mark.package_data(['doc/source/code', 'mod'])
class TestCreatePython():

    def test_netParams_and_cfg(self, pkg_setup):
        from tut6 import netParams, simConfig
        createPythonScript('test_script.py', netParams, simConfig)
        del netParams, simConfig # to make sure nothing got cached..

        import test_script
        sim.checkOutput('tut6')


    def test_netParams(self, pkg_setup):
        from tut6 import netParams
        createPythonNetParams(fname='test_net_params.py', netParams=netParams)
        del netParams

        from test_net_params import netParams
        from tut6 import simConfig
        sim.createSimulateAnalyze(netParams, simConfig)
        sim.checkOutput('tut6')


    def test_simConfig(self, pkg_setup):
        from tut6 import simConfig
        createPythonSimConfig(fname='test_sim_config.py', simConfig=simConfig)
        del simConfig

        from test_sim_config import simConfig
        from tut6 import netParams
        sim.createSimulateAnalyze(netParams, simConfig)
        sim.checkOutput('tut6')
