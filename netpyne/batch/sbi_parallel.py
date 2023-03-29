"""
Module for SBI optimization
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from builtins import zip

from builtins import range
from builtins import open
from builtins import str
from lib2to3.pytree import NegatedPattern
from future import standard_library

standard_library.install_aliases()

# required to make json saving work in Python 2/3
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from subprocess import Popen
import numpy as np
from scipy.stats import kurtosis

import dill as pickle

from neuron import h
from sbi import utils as utils
from sbi import analysis as analysis
from sbi.inference.base import infer
from sbi.analysis.plot import pairplot
from sbi import utils
from sbi import analysis
from sbi import inference
from sbi.inference import SNPE, SNLE, SNRE, simulate_for_sbi, prepare_for_sbi
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.stats import kurtosis

pc = h.ParallelContext()  # use bulletin board master/slave


# -------------------------------------------------------------------------------
# Simulation-Based-Inference (SBI) optimization
# -------------------------------------------------------------------------------


def runJob(nrnCommand, script, cfgSavePath, netParamsSavePath, simDataPath):
    """
    Function for/to <short description of `netpyne.batch.sbi_parallel.runJob`>

    Parameters
    ----------
    script : <type>
        <Short description of script>
        **Default:** *required*

    cfgSavePath : <type>
        <Short description of cfgSavePath>
        **Default:** *required*

    netParamsSavePath : <type>
        <Short description of netParamsSavePath>
        **Default:** *required*

    simDataPath : <type>
        <Short description of simDataPath>
        **Default:** *required*

    """

    import os

    print('\nJob in rank id: ', pc.id())
    command = '%s %s simConfig=%s netParams=%s' % (nrnCommand, script, cfgSavePath, netParamsSavePath)
    print(command)

    with open(simDataPath + '.run', 'w') as outf, open(simDataPath + '.err', 'w') as errf:
        pid = Popen(command.split(' '), stdout=outf, stderr=errf, preexec_fn=os.setsid).pid

    with open('./pids.pid', 'a') as file:
        file.write(str(pid) + ' ')


def sbiOptim(batch, pc):
    """
    Function for/to <short description of `netpyne.batch.sbi_parallel.sbiOptim`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*

    pc : <type>
        <Short description of pc>
        **Default:** *required*


    """
    import sys
    from .utils import evaluator

    best_fit = []

    def updateBestFit(candidate, fitness):
        # Rewrite in different manner?
        observed = batch.optimCfg.get('summaryStatisticObserved')  # Will be a list or None
        if None in observed:
            if not best_fit:
                best_fit.append(candidate)
                best_fit.append(fitness[0])
            else:
                if fitness[0] < best_fit[1]:
                    best_fit[0] = candidate
                    best_fit[1] = fitness[0]
        else:
            if not best_fit:
                best_fit.append(observed)

    from time import sleep

    try:
        from mpi4py import MPI

        comm = MPI.COMM_WORLD
        size = comm.Get_size()
        rank = comm.Get_rank()
    except:
        size = 1
        rank = 0

    # create main sim directory and save scripts
    batch.saveScripts()

    # gather **kwargs
    args = {}
    args['minVals'] = np.array([x['values'][0] for x in batch.params])
    args['maxVals'] = np.array([x['values'][1] for x in batch.params])
    args['cfg'] = batch.cfg  # include here args/params to pass to evaluator function
    args['paramLabels'] = [x['label'] for x in batch.params]
    args['netParamsSavePath'] = batch.saveFolder + '/' + batch.batchLabel + '_netParams.py'
    args['maxiters'] = batch.optimCfg['maxiters'] if 'maxiters' in batch.optimCfg else 1000
    args['maxtime'] = batch.optimCfg['maxtime'] if 'maxtime' in batch.optimCfg else None
    args['fitnessFunc'] = batch.optimCfg['fitnessFunc']
    args['fitnessFuncArgs'] = batch.optimCfg['fitnessFuncArgs']
    args['summaryStats'] = batch.optimCfg['summaryStats']
    args['summaryStatisticArg'] = batch.optimCfg['summaryStatisticArg']
    args['summaryStatisticLength'] = batch.optimCfg.get('summaryStatisticLength')
    args['maxiter_wait'] = batch.optimCfg['maxiter_wait']
    args['time_sleep'] = batch.optimCfg['time_sleep']
    args['maxFitness'] = batch.optimCfg.get('maxFitness', 1000)
    args['sbi_method'] = batch.optimCfg['sbi_method']
    args['inference_type'] = batch.optimCfg['inference_type']
    args['rounds'] = batch.optimCfg['rounds']

    for key, value in batch.optimCfg.items():
        args[key] = value

    for key, value in batch.runCfg.items():
        args[key] = value

    # if using pc bulletin board, initialize all workers
    if batch.runCfg.get('type', None) == 'mpi_bulletin':
        for iworker in range(int(pc.nhost())):
            pc.runworker()

    # -------------------------------------------------------------------------------
    # Run algorithm
    # -------------------------------------------------------------------------------
    sleep(rank)  # each process waits a different time to avoid saturating sqlite database

    try:

        sbi_method = args.get('sbi_method')  # SNPE, SNLE, or SNRE
        sbi_md = {'SNPE': SNPE, 'SNLE': SNLE, 'SNRE': SNRE}  # sbi_MethodDictionary
        inference_type = args.get('inference_type')  # Single or Multi

        prior = utils.torchutils.BoxUniform(
            low=torch.as_tensor(np.array(args['minVals'])), high=torch.as_tensor(np.array(args['maxVals']))
        )
        global ngen
        ngen = -1

        def objectiveFunc(param):
            candidate = np.asarray(param)
            # first iteration may return multiple param sets instead of one
            # use this first one in this case
            if len(candidate.shape) > 1:
                candidate = candidate[0]
            global ngen
            ngen += 1
            fitness, sum_statistics = evaluator(batch, [candidate], args, ngen, pc)
            updateBestFit(candidate, fitness)
            return torch.as_tensor(fitness + sum_statistics)

        simulator, prior = prepare_for_sbi(lambda param: objectiveFunc(param), prior)
        inference = sbi_md[sbi_method](prior=prior)

        if inference_type == 'single':
            theta, x = simulate_for_sbi(simulator, proposal=prior, num_simulations=args['maxiters'])
            density_estimator = inference.append_simulations(theta, x).train()
            posterior = inference.build_posterior(density_estimator)

            observable_stats = objectiveFunc(best_fit[0])

            samples = posterior.sample((10000,), x=observable_stats)
            posterior_sample = posterior.sample((1,), x=observable_stats).numpy()

        elif inference_type == 'multi':
            rounds = args.get('rounds')
            posteriors = []
            proposal = prior
            for round_iter in range(rounds):
                theta, x = simulate_for_sbi(simulator, proposal=prior, num_simulations=args['maxiters'])
                if sbi_method == 'SNPE':
                    density_estimator = inference.append_simulations(theta, x, proposal=proposal).train()
                else:
                    density_estimator = inference.append_simulations(theta, x).train()
                posterior = inference.build_posterior(density_estimator)
                posteriors.append(posterior)

                if round_iter < 2:
                    observable_stats = objectiveFunc(best_fit[0])
                proposal = posterior.set_default_x(observable_stats)

            samples = posterior.sample((10000,), x=observable_stats)
            posterior_sample = posterior.sample((1,), x=observable_stats).numpy()
        else:
            print('Error on sbi simulation')

        print('~' * 80)
        print('~' * 80)
        print('~' * 80)

    except Exception as e:
        print(e)

    # print best and finish
    if rank == size - 1:
        import matplotlib.pyplot as plt

        plt.figure()
        _ = analysis.pairplot(samples, figsize=(16, 14))
        plt.savefig('PairPlot.png')

        # SAMPLE WILL BE PULLED FROM POSTERIOR SAMPLE OF SBI
        print('\n"Observed" Parameter Where SBI Takes Place Around:', best_fit[0])
        print("-" * 80)
        print('\nPosterior Distribution Sample: ', posterior_sample[0])
        print("-" * 80)

        print('\nSaving to output.pkl...\n')
        output = {samples}  # All 10000 parameter samples will be saved
        with open('%s/%s_output.pkl' % (batch.saveFolder, batch.batchLabel), 'wb') as f:
            pickle.dump(output, f)

        sleep(1)

        print("-" * 80)
        print("   Completed SBI parameter optimization   ")
        print("-" * 80)

    sys.exit()
