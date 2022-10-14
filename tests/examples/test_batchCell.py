import pytest
import os
import sys
import json
from netpyne.batch import Batch
from multiprocessing import Process

if "-nogui" not in sys.argv:
    sys.argv.append("-nogui")

from .utils import pkg_setup


@pytest.mark.package_data(["examples/batchCell/", "mod"])
class TestBatchCell:
    def batch_run(self, pkg_setup):
        """run a reduced version of the batchCell example"""

        params = {"dendNa": [0.025], ("IClamp1", "amp"): [1]}
        initCfg = {"duration": 10}
        b = Batch(params=params, initCfg=initCfg)
        b.batchLabel = "batchNa"
        b.saveFolder = "/tmp/" + b.batchLabel
        b.method = "grid"
        b.runCfg = {"type": "mpi_bulletin", "script": "init.py", "skip": True}
        b.run()

    def test_batchCell(self, pkg_setup):
        """test the batchCell example runs"""

        p = Process(target=self.batch_run, args=(pkg_setup,))
        p.start()
        p.join()

        # check it created output
        assert os.path.exists("/tmp/batchNa/batchNa_0_0_data.json")

        # check one value in the output
        data = json.load(open("/tmp/batchNa/batchNa_0_0_data.json", "r"))
        assert data["simData"]["avgRate"] == 100.0
