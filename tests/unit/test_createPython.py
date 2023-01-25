import pytest
import sys
from netpyne import sim
from netpyne.conversion import createPythonScript, createPythonNetParams, createPythonSimConfig
import __main__
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')
from tests.examples.utils import pkg_setup

@pytest.mark.package_data(['examples/HHTut/', None]) # TODO: use some more light-weight example?
class TestCreatePython():

    def test_netParams_and_cfg(self, pkg_setup):
        from src.cfg import cfg
        __main__.cfg = cfg
        from src.netParams import netParams

        createPythonScript(fname='test_script.py', netParams=netParams, simConfig=cfg)
        del netParams, cfg

        import test_script
        sim.checkOutput('HHTut')


    def test_netParams(self, pkg_setup):
        from src.cfg import cfg
        __main__.cfg = cfg
        from src.netParams import netParams

        createPythonNetParams(fname='test_net_params.py', netParams=netParams)
        del netParams

        from test_net_params import netParams
        sim.createSimulateAnalyze(netParams, cfg)

        sim.checkOutput('HHTut')


    def test_simConfig(self, pkg_setup):
        from src.cfg import cfg

        createPythonSimConfig(fname='test_sim_config.py', simConfig=cfg)
        del cfg

        from test_sim_config import simConfig
        __main__.cfg = simConfig
        from src.netParams import netParams
        sim.createSimulateAnalyze(netParams, simConfig)

        sim.checkOutput('HHTut')
