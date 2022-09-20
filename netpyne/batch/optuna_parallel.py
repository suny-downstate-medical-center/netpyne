"""
Module for Optuna hyperparameter optimization (optuna.org)

"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from builtins import zip

from builtins import range
from builtins import open
from builtins import str
from future import standard_library
standard_library.install_aliases()

# required to make json saving work in Python 2/3
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

import pickle

from neuron import h
import optuna

pc = h.ParallelContext() # use bulletin board master/slave




# -------------------------------------------------------------------------------
# Optuna optimization
# -------------------------------------------------------------------------------


def optunaOptim(batch, pc):
    """
    Function for/to <short description of `netpyne.batch.optuna_parallel.optunaOptim`>

    Parameters
    ----------
    batch : <type>
        <Short description of batch>
        **Default:** *required*

    pc : <type>
        <Short description of pc>
        **Default:** *required*


    """


    import sys
    from .utils import evaluator

    # -------------------------------------------------------------------------------
    # Optuna optimization: Main code
    # -------------------------------------------------------------------------------
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

    args = {}
    args['popsize'] = batch.optimCfg.get('popsize', 1)
    args['minVals'] = [x['values'][0] for x in batch.params]
    args['maxVals'] = [x['values'][1] for x in batch.params]
    args['cfg'] = batch.cfg  # include here args/params to pass to evaluator function
    args['paramLabels'] = [x['label'] for x in batch.params]
    args['netParamsSavePath'] = batch.saveFolder + '/' + batch.batchLabel + '_netParams.py'
    args['maxiters'] = batch.optimCfg.get('maxiters', 1000)
    args['maxtime'] = batch.optimCfg.get('maxtime')
    args['fitnessFunc'] = batch.optimCfg['fitnessFunc']
    args['fitnessFuncArgs'] = batch.optimCfg['fitnessFuncArgs']
    args['maxiter_wait'] = batch.optimCfg['maxiter_wait']
    args['time_sleep'] = batch.optimCfg['time_sleep']
    args['maxFitness'] = batch.optimCfg.get('maxFitness', 1000)
    args['direction'] = batch.optimCfg.get('direction', 'minimize')

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

    sleep(rank) # each process wiats a different time to avoid saturating sqlite database
    study = optuna.create_study(study_name=batch.batchLabel, storage='sqlite:///%s/%s_storage.db' % (batch.saveFolder, batch.batchLabel),
                                load_if_exists=True, direction=args['direction'])
    # params
    paramLabels = args.get('paramLabels', [])
    minVals = args.get('minVals', [])
    maxVals = args.get('maxVals', [])

    try:
        def func(trial):
            # --------------------------------------
            # generate param values for optuna trial
            candidate = [] # just 1 candidate
            for paramLabel, minVal, maxVal in zip(paramLabels, minVals, maxVals):
                candidate.append(trial.suggest_uniform(str(paramLabel), minVal, maxVal))
            return evaluator(batch, [candidate], args, trial.number, pc)
        study.optimize(func, n_trials=args['maxiters'], timeout=args['maxtime'])
    except Exception as e:
        print(e)


    # print best and finish
    if rank == size-1:
        df = study.trials_dataframe(attrs=('number', 'value', 'params', 'state'))
        importance = optuna.importance.get_param_importances(study=study)

        print('\nBest trial: ', study.best_trial)
        print('\nParameter importance: ', dict(importance))

        print('\nBest Solution with fitness = %.4g: \n' % (study.best_value), study.best_params)

        print('\nSaving to output.pkl...\n')
        output = {'study': study, 'df': df, 'importance': importance}
        with open('%s/%s_output.pkl' % (batch.saveFolder, batch.batchLabel), 'wb') as f:
            pickle.dump(output, f)

        sleep(1)

        print("-" * 80)
        print("   Completed Optuna parameter optimization   ")
        print("-" * 80)


    sys.exit()
