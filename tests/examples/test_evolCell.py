import pytest
import os
import sys
import csv
from netpyne.batch import Batch
from netpyne import specs
from multiprocessing import Process

if "-nogui" not in sys.argv:
    sys.argv.append("-nogui")

from .utils import pkg_setup


@pytest.mark.package_data(["examples/evolCell/", "mod"])
class TestEvolCell:
    def evol_run(self, pkg_setup):
        """run a reduced version of the evolCell example"""

        params = specs.ODict()
        params[("tune", "soma", "Ra")] = [100.0 * 0.5, 100 * 1.5]

        amps = [0.0, 0.65]  # amplitudes
        times = [100, 200]  # start times
        dur = 50  # ms
        targetRates = [0.0, 81.0]

        # initial cfg set up
        initCfg = {}  # specs.ODict()
        initCfg["duration"] = 200 * len(amps)
        initCfg[("hParams", "celsius")] = 37

        initCfg["savePickle"] = True
        initCfg["saveJson"] = False
        initCfg["saveDataInclude"] = ["simConfig", "netParams", "net", "simData"]

        initCfg[("IClamp1", "pop")] = "ITS4"
        initCfg[("IClamp1", "amp")] = amps
        initCfg[("IClamp1", "start")] = times
        initCfg[("IClamp1", "dur")] = 100

        initCfg[("analysis", "plotfI", "amps")] = amps
        initCfg[("analysis", "plotfI", "times")] = times
        initCfg[("analysis", "plotfI", "dur")] = dur
        initCfg[("analysis", "plotfI", "targetRates")] = targetRates

        for k, v in params.items():
            initCfg[k] = v[0]  # initialize params in cfg so they can be modified

        # fitness function
        fitnessFuncArgs = {}
        fitnessFuncArgs["targetRates"] = targetRates

        def fitnessFunc(simData, **kwargs):
            targetRates = kwargs["targetRates"]

            diffRates = [abs(x - t) for x, t in zip(simData["fI"], targetRates)]
            fitness = np.mean(diffRates)

            print(" Candidate rates: ", simData["fI"])
            print(" Target rates:    ", targetRates)
            print(" Difference:      ", diffRates)

            return fitness

        # create Batch object with paramaters to modify, and specifying files to use
        b = Batch(params=params, initCfg=initCfg)

        # Set output folder, grid method (all param combinations), and run configuration
        b.batchLabel = "ITS4_evol"
        b.saveFolder = "/tmp/" + b.batchLabel
        b.method = "evol"
        b.seed = 0
        b.runCfg = {"type": "mpi_bulletin", "script": "init.py"}
        b.evolCfg = {
            "evolAlgorithm": "custom",
            "fitnessFunc": fitnessFunc,  # fitness expression (should read simData)
            "fitnessFuncArgs": fitnessFuncArgs,
            "pop_size": 2,
            "num_elites": 1,  # keep this number of parents for next generation if they are fitter than children
            "mutation_rate": 0.4,
            "crossover": 0.5,
            "maximize": False,  # maximize fitness function?
            "max_generations": 1,
            "time_sleep": 0.25,  # wait this time before checking again if sim is completed (for each generation)
            "maxiter_wait": 20,  # max number of times to check if sim is completed (for each generation)
            "defaultFitness": 1000,  # set fitness value in case simulation time is over
        }
        # Run batch simulations
        b.run()

    def test_evolCell(self, pkg_setup):
        """test the evolCell example runs"""

        p = Process(target=self.evol_run, args=(pkg_setup,))
        p.start()
        p.join()

        # check it created output
        assert os.path.exists("/tmp/ITS4_evol/ITS4_evol_stats_indiv.csv")

        # check one value in the output
        with open("/tmp/ITS4_evol/ITS4_evol_stats_indiv.csv") as f:
            rd = csv.reader(f)
            for r in rd:
                continue
        assert abs(float(r[-1][2:-1]) - 118.83081597006257) < 1e-9
