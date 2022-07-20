import sys
import json
import pytest

if "-nogui" not in sys.argv:
    sys.argv.append("-nogui")
sys.path.append("doc/source/code/")
sys.path.append("examples/HHTut/")
from multiprocessing import Process
from netpyne import sim

def test_tutorial_1():
    import tut1
    sim.checkOutput('tut1')


def test_tutorial_2():
    import tut2
    sim.checkOutput('tut2')


def test_tutorial_3():
    import tut3
    sim.checkOutput('tut3')


# TODO: Needs fixing
# def test_tutorial_4():
#     import tut4


def test_tutorial_5():
    import tut5
    sim.checkOutput('tut5')


def test_tutorial_6():
    import tut6
    sim.checkOutput('tut6')


def test_tutorial_7():
    import tut7
    sim.checkOutput('tut7')


def batch_example():
    """batch example from tutorial 8 with fewer parameters"""

    from netpyne import specs
    from netpyne.batch import Batch
    import json

    params = specs.ODict()
    params["synMechTau2"] = [3.0]
    params["connWeight"] = [0.005]
    b = Batch(
        params=params,
        cfgFile="doc/source/code/tut8_cfg.py",
        netParamsFile="doc/source/code/tut8_netParams.py",
    )
    b.batchLabel = "tauWeight"
    b.saveFolder = "/tmp/tut8_data"
    b.method = "grid"
    b.runCfg = {
        "type": "mpi_bulletin",
        "script": "doc/source/code/tut8_init.py",
        "skip": True,
    }
    # Run batch simulations
    b.run()


def test_tutorial_8():
    """test tutorial 8 grid parameter search"""

    p = Process(target=batch_example)
    p.start()
    p.join()
    # check the output
    test = json.load(open("/tmp/tut8_data/tauWeight_0_0_data.json", "r"))
    assert test["simData"]["avgRate"] == 13.675
