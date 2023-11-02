import pytest
import sys, os, shutil
from netpyne import sim, specs
import __main__
if '-nogui' not in sys.argv:
    sys.argv.append('-nogui')
from tests.examples.utils import pkg_setup

@pytest.mark.package_data(['.', None])
class TestSaveModel():

    def test_save_from_scratch(self, pkg_setup):
        # create model from netParams and cfg only, i.e. not having anything previously loaded from index
        cfg, netParams = specs.SimConfig(), specs.NetParams()
        netParams.connParams['PYR->PYR'] = {'postConds': {'cellType': 'PYR_HH'}}
        cfg.recordStep = 123

        sim.saveModel(netParams, cfg,
            srcPath=None,
            dstPath='/tmp/HybridTut_tmp'
        )
        del cfg, netParams

        cfg, netParams = sim.loadModel('/tmp/HybridTut_tmp')
        self.checkModelIsModified(netParams, cfg)


    def test_save_in_place(self, pkg_setup):
        # load model, modify netParams and simConfig and save as same model (re-write)

        # First, dublicate original model to avoid affecting code base:
        shutil.copytree('examples/HybridTut', 'examples/HybridTut_tmp')

        cfg, netParams = sim.loadModel('examples/HybridTut_tmp')
        self.modifyModel(netParams, cfg)

        sim.saveModel(netParams, cfg,
            srcPath='examples/HybridTut_tmp',
            dstPath=None, # None meaning re-write model at srcPath
        )
        del cfg, netParams

        # check model
        cfg, netParams = sim.loadModel('examples/HybridTut_tmp')
        self.checkModelIsModified(netParams, cfg)

        shutil.rmtree('examples/HybridTut_tmp')


    def test_save_another_variant(self, pkg_setup):
        # load model, modify netParams and simConfig and save to same folder, but as a new model variant (separate index-file)
        cfg, netParams = sim.loadModel('examples/HybridTut', loadMechs=False)
        self.modifyModel(netParams, cfg)

        sim.saveModel(netParams, cfg,
            srcPath='examples/HybridTut',
            dstPath='examples/HybridTut/index_new.npjson',
        )
        del cfg, netParams

        # check model
        cfg, netParams = sim.loadModel('examples/HybridTut/index_new.npjson', loadMechs=False)
        self.checkModelIsModified(netParams, cfg)

        # check that original one kept intact
        cfg, netParams = sim.loadModel('examples/HybridTut', loadMechs=False)
        self.checkModelNotModified(netParams, cfg)


    def test_save_to_new_folder(self, pkg_setup):
        # load model, modify netParams and simConfig and save to new folder
        cfg, netParams = sim.loadModel('examples/HybridTut', loadMechs=False)
        self.modifyModel(netParams, cfg)

        sim.saveModel(netParams, cfg,
            srcPath='examples/HybridTut',
            dstPath='examples/HybridTut_tmp2/',
            exportNetParamsAsPython=True
        )
        del cfg, netParams

        # check model
        cfg, netParams = sim.loadModel('examples/HybridTut_tmp2/', loadMechs=False)
        self.checkModelIsModified(netParams, cfg)
        # check netParams exported as python (not a default json)
        assert os.path.exists('examples/HybridTut_tmp2/src/netParams.py')
        assert os.path.exists('examples/HybridTut_tmp2/src/netParams.json') == False

        # check that original one kept intact
        cfg, netParams = sim.loadModel('examples/HybridTut', loadMechs=False)
        self.checkModelNotModified(netParams, cfg)

        shutil.rmtree('examples/HybridTut_tmp2')

    # utility

    def modifyModel(self, netParams, cfg):
        netParams.connParams['PYR->PYR']['postConds']['cellType'] = 'PYR_HH'
        cfg.recordStep = 123

    def checkModelIsModified(self, netParams, cfg):
        assert netParams.connParams['PYR->PYR']['postConds']['cellType'] == 'PYR_HH'
        assert cfg.recordStep == 123

    def checkModelNotModified(self, netParams, cfg):
        assert netParams.connParams['PYR->PYR']['postConds']['cellType'] == ['PYR_HH', 'PYR_Izhi']
        assert cfg.recordStep == 0.025
