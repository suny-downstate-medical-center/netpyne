import ray
import pandas
import os
from ray import tune, train
from ray.air import session, RunConfig
from ray.tune.search.basic_variant import BasicVariantGenerator
from ray.tune.search import create_searcher, ConcurrencyLimiter, SEARCH_ALG_IMPORT
from netpyne.batchtools import runtk
from collections import namedtuple
from batchtk.raytk.search import ray_trial, LABEL_POINTER
from batchtk.utils import get_path
import numpy
from typing import Any, Callable, Dict, List, Optional, Tuple, Union



choice = tune.choice
grid = tune.grid_search
uniform = tune.uniform

def ray_optuna_search(dispatcher_constructor: Callable, # constructor for the dispatcher (e.g. INETDispatcher)
                      submit_constructor: Callable, # constructor for the submit (e.g. SHubmitSOCK)
                      run_config: Dict, # batch configuration, (keyword: string pairs to customize the submit template)
                      params: Dict, # search space (dictionary of parameter keys: tune search spaces)
                      label: Optional[str] = 'optuna_search', # label for the search
                      output_path: Optional[str] = '../batch', # directory for storing generated files
                      checkpoint_path: Optional[str] = '../ray', # directory for storing checkpoint files
                      max_concurrent: Optional[int] = 1, # number of concurrent trials to run at one time
                      batch: Optional[bool] = True, # whether concurrent trials should run synchronously or asynchronously
                      num_samples: Optional[int] = 1, # number of trials to run
                      metric: Optional[str|list|tuple] = "loss", # metric to optimize (this should match some key: value pair in the returned data
                      mode: Optional[str|list|tuple] = "min", # either 'min' or 'max' (whether to minimize or maximize the metric
                      optuna_config: Optional[dict] = None, # additional configuration for the optuna search algorithm
                      ) -> namedtuple('Study', ['algo', 'results']):
    """
    ray_optuna_search(...)

    Parameters
    ----------
    dispatcher_constructor:Callable, # constructor for the dispatcher (e.g. INETDispatcher)
    submit_constructor:Callable, # constructor for the submit (e.g. SHubmitSOCK)
    run_config:Dict, # batch configuration, (keyword: string pairs to customize the submit template)
    params:Dict, # search space (dictionary of parameter keys: tune search spaces)
    label:Optional[str] = 'optuna_search', # label for the search
    output_path:Optional[str] = '../batch', # directory for storing generated files
    checkpoint_path:Optional[str] = '../ray', # directory for storing checkpoint files
    max_concurrent:Optional[int] = 1, # number of concurrent trials to run at one time
    batch:Optional[bool] = True, # whether concurrent trials should run synchronously or asynchronously
    num_samples:Optional[int] = 1, # number of trials to run
    metric:Optional[str] = "loss", # metric to optimize (this should match some key: value pair in the returned data
    mode:Optional[str] = "min", # either 'min' or 'max' (whether to minimize or maximize the metric
    optuna_config:Optional[dict] = None, # additional configuration for the optuna search algorithm (incl. sampler, seed, etc.)

    Creates
    -------
    <label>.csv: file containing the results of the search

    Returns
    -------
    Study: namedtuple('Study', ['algo', 'results'])(algo, results), # named tuple containing the created algorithm and the results of the search
    """
    from ray.tune.search.optuna import OptunaSearch

    ray.init(runtime_env={"working_dir": "."})# TODO needed for python import statements ?
    if optuna_config == None:
        optuna_config = {}

    storage_path = get_path(checkpoint_path)
    algo = ConcurrencyLimiter(searcher=OptunaSearch(metric=metric, mode=mode, **optuna_config),
                              max_concurrent=max_concurrent,
                              batch=batch) #TODO does max_concurrent and batch work?

    submit = submit_constructor()
    submit.update_templates(
        **run_config
    )
    project_path = os.getcwd()

    def run(config):
        config.update({'saveFolder': output_path, 'simLabel': LABEL_POINTER})
        data = ray_trial(config, label, dispatcher_constructor, project_path, output_path, submit)
        if isinstance(metric, str):#TODO only Optuna supports multiobjective?
            metrics = {'config': config, 'data': data, metric: data[metric]}
            session.report(metrics)
        elif isinstance(metric, (list, tuple)):
            metrics = {k: data[k] for k in metric}
            metrics['config'] = config
            metrics['data'] = data
            session.report(metrics)
        else:
            raise ValueError("metric must be a string or a list/tuple of strings")
    tuner = tune.Tuner(
        run,
        tune_config=tune.TuneConfig(
            search_alg=algo,
            num_samples=num_samples,
        ),
        run_config=RunConfig(
            storage_path=storage_path,
            name=label,
        ),
        param_space=params,
    )

    results = tuner.fit()
    resultsdf = results.get_dataframe()
    resultsdf.to_csv("{}.csv".format(label))
    #return namedtuple('Study', ['algo', 'results'])(algo, results)
    return namedtuple('Study', ['algo', 'results'])(algo.searcher._ot_study, results)

"""
Parameters
:
space –
Hyperparameter search space definition for Optuna’s sampler. This can be either a dict with parameter names as keys and optuna.distributions as values, or a Callable - in which case, it should be a define-by-run function using optuna.trial to obtain the hyperparameter values. The function should return either a dict of constant values with names as keys, or None. For more information, see https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/002_configurations.html.
Warning
No actual computation should take place in the define-by-run function. Instead, put the training logic inside the function or class trainable passed to tune.Tuner().
metric – The training result objective value attribute. If None but a mode was passed, the anonymous metric _metric will be used per default. Can be a list of metrics for multi-objective optimization.
mode – One of {min, max}. Determines whether objective is minimizing or maximizing the metric attribute. Can be a list of modes for multi-objective optimization (corresponding to metric).
points_to_evaluate – Initial parameter suggestions to be run first. This is for when you already have some good parameters you want to run first to help the algorithm make better suggestions for future parameters. Needs to be a list of dicts containing the configurations.
sampler –
Optuna sampler used to draw hyperparameter configurations. Defaults to MOTPESampler for multi-objective optimization with Optuna<2.9.0, and TPESampler in every other case. See https://optuna.readthedocs.io/en/stable/reference/samplers/index.html for available Optuna samplers.
Warning
Please note that with Optuna 2.10.0 and earlier default MOTPESampler/TPESampler suffer from performance issues when dealing with a large number of completed trials (approx. >100). This will manifest as a delay when suggesting new configurations. This is an Optuna issue and may be fixed in a future Optuna release.
seed – Seed to initialize sampler with. This parameter is only used when sampler=None. In all other cases, the sampler you pass should be initialized with the seed already.
evaluated_rewards –
If you have previously evaluated the parameters passed in as points_to_evaluate you can avoid re-running those trials by passing in the reward attributes as a list so the optimiser can be told the results without needing to re-compute the trial. Must be the same length as points_to_evaluate.
"""


def ray_search(dispatcher_constructor: Callable, # constructor for the dispatcher (e.g. INETDispatcher)
               submit_constructor: Callable, # constructor for the submit (e.g. SHubmitSOCK)
               run_config: Dict, # batch configuration, (keyword: string pairs to customize the submit template)
               params: Dict, # search space (dictionary of parameter keys: tune search spaces)
               algorithm: Optional[str] = "variant_generator", # search algorithm to use, see SEARCH_ALG_IMPORT for available options
               label: Optional[str] = 'search', # label for the search
               output_path: Optional[str] = '../batch', # directory for storing generated files
               checkpoint_path: Optional[str] = '../ray', # directory for storing checkpoint files
               max_concurrent: Optional[int] = 1, # number of concurrent trials to run at one time
               batch: Optional[bool] = True, # whether concurrent trials should run synchronously or asynchronously
               num_samples: Optional[int] = 1, # number of trials to run
               metric: Optional[str] = "loss", # metric to optimize (this should match some key: value pair in the returned data
               mode: Optional[str] = "min",  # either 'min' or 'max' (whether to minimize or maximize the metric
               algorithm_config: Optional[dict] = None, # additional configuration for the search algorithm
               ) -> tune.ResultGrid:
    ray.init(runtime_env={"working_dir": "."}) # TODO needed for python import statements ?

    if algorithm_config == None:
        algorithm_config = {}

    if 'metric' not in algorithm_config:
        algorithm_config['metric'] = metric

    if 'mode' not in algorithm_config:
        algorithm_config['mode'] = mode

    if 'max_concurrent' not in algorithm_config:
        algorithm_config['max_concurrent'] = max_concurrent

    if 'batch' not in algorithm_config:
        algorithm_config['batch'] = batch

    #TODO class this object for self calls? cleaner? vs nested functions
    #TODO clean up working_dir and excludes
    storage_path = get_path(checkpoint_path)
    algo = create_searcher(algorithm, **algorithm_config) #concurrency may not be accepted by all algo
    #search_alg – The search algorithm to use.
    #  metric – The training result objective value attribute. Stopping procedures will use this attribute.
    #  mode – One of {min, max}. Determines whether objective is minimizing or maximizing the metric attribute.
    #  **kwargs – Additional parameters. These keyword arguments will be passed to the initialization function of the chosen class.
    try:
        algo = ConcurrencyLimiter(searcher=algo, max_concurrent=algorithm_config['max_concurrent'], batch=algorithm_config['batch'])
    except:
        pass

    submit = submit_constructor()
    submit.update_templates(
        **run_config
    )
    project_path = os.getcwd()
    def run(config):
        config.update({'saveFolder': output_path, 'simLabel': LABEL_POINTER})
        data = ray_trial(config, label, dispatcher_constructor, project_path, output_path, submit)
        if isinstance(metric, str):
            metrics = {'config': config, 'data': data, metric: data[metric]}
            session.report(metrics)
        elif isinstance(metric, (list, tuple)):
            metrics = {k: data[k] for k in metric}
            metrics['data'] = data
            metrics['config'] = config
            session.report(metrics)
        else:
            session.report({'data': data, 'config': config})

    tuner = tune.Tuner(
        run,
        tune_config=tune.TuneConfig(
            search_alg=algo,
            num_samples=num_samples, # grid search samples 1 for each param
            metric=algorithm_config['metric'],
            mode=algorithm_config['mode'],
        ),
        run_config=RunConfig(
            storage_path=storage_path,
            name=algorithm,
        ),
        param_space=params,
    )

    results = tuner.fit()
    resultsdf = results.get_dataframe()
    resultsdf.to_csv("{}.csv".format(label))
    return results


#should be constant?
constructors = namedtuple('constructors', 'dispatcher, submit')
constructor_tuples = {
    ('sge', 'socket'): constructors(runtk.dispatchers.INETDispatcher, runtk.submits.SGESubmitSOCK),
    #('sge', 'unix'): constructors(runtk.dispatchers.UNIXDispatcher, runtk.submits.SGESubmitSOCK), #can't use AF_UNIX sockets on networked machines
    ('sge', 'sfs' ): constructors(runtk.dispatchers.SFSDispatcher , runtk.submits.SGESubmitSFS ),
    #('zsh', 'inet'): constructors(runtk.dispatchers.INETDispatcher, runtk.submits.ZSHSubmitSOCK), #TODO preferable to use AF_UNIX sockets on local machines
    ('sh', 'socket'): constructors(runtk.dispatchers.UNIXDispatcher, runtk.submits.SHSubmitSOCK),
    ('sh', 'sfs' ): constructors(runtk.dispatchers.SFSDispatcher , runtk.submits.SHSubmitSFS ),
}#TODO, just say "socket"?

"""
some shim functions before ray_search
"""
def generate_constructors(job_type, comm_type = 'socket', **kwargs):
    """"
    returns the dispatcher, submit constructor pair for ray_search based on the job_type and comm_type inputs
    """
    if (job_type, comm_type) not in constructor_tuples:
        raise ValueError("Invalid job_type or comm_type pairing")
    return constructor_tuples[(job_type, comm_type)]

def generate_parameters(params, algorithm, **kwargs):
    """

    Parameters
    ----------
    params = {'synMechTau2': [3.0, 5.0, 7.0], # assumes list of values by default if grid search-like algo
		  #'synMechTau2': [3.0, 7.0], # assumes lower/upper bounds by default if evol-like algo
          'connWeight' : paramtypes.sample_from(lambda _: numpy.random.uniform(0.005, 0.15))} # can optionally pass any of the paramtypes (= ray.tune data types)

    Returns
    -------
    a dictionary of parameters for ray_search based on the input dictionary

    """
     #TODO: bloated function, prone to error
    ray_params = {}
    for param, space in params.items():
        if   isinstance(space, (list, tuple, range, numpy.ndarray)) and algorithm in {'variant_generator'}:
            ray_params[param] = tune.grid_search(space)
        elif isinstance(space, (list, tuple)) and algorithm in SEARCH_ALG_IMPORT.keys():
            if len(space) == 2: #if 2 sample from uniform lb, ub
                ray_params[param] = tune.uniform(*space)
            else: #otherwise treat as a list for a categorical search
                ray_params[param] = tune.choice(space)
        else: #assume a tune search space was defined
            ray_params[param] = space
    return ray_params

def shim(job_type: str, # the submission engine to run a single simulation (e.g. 'sge', 'sh')
         comm_type: str, # the method of communication between host dispatcher and the simulation (e.g. 'socket', 'filesystem')
         run_config: Dict,  # batch configuration, (keyword: string pairs to customize the submit template)
         params: Dict,  # search space (dictionary of parameter keys: tune search spaces)
         algorithm: Optional[str] = "variant_generator", # search algorithm to use, see SEARCH_ALG_IMPORT for available options
         label: Optional[str] = 'search',  # label for the search
         output_path: Optional[str] = '../batch',  # directory for storing generated files
         checkpoint_path: Optional[str] = '../ray',  # directory for storing checkpoint files
         max_concurrent: Optional[int] = 1,  # number of concurrent trials to run at one time
         batch: Optional[bool] = True,  # whether concurrent trials should run synchronously or asynchronously
         num_samples: Optional[int] = 1,  # number of trials to run
         metric: Optional[str] = "loss", # metric to optimize (this should match some key: value pair in the returned data
         mode: Optional[str] = "min",  # either 'min' or 'max' (whether to minimize or maximize the metric
         algorithm_config: Optional[dict] = None,  # additional configuration for the search algorithm
         ):
    kwargs = locals()
    kwargs['dispatcher_constructor'], kwargs['submit_constructor'] = generate_constructors(**kwargs)
    [kwargs.pop(args) for args in ['job_type', 'comm_type']]
    kwargs['params'] = generate_parameters(**kwargs)
    return kwargs


def search(job_type: str, # the submission engine to run a single simulation (e.g. 'sge', 'sh')
           comm_type: str, # the method of communication between host dispatcher and the simulation (e.g. 'socket', 'filesystem')
           run_config: Dict,  # batch configuration, (keyword: string pairs to customize the submit template)
           params: Dict,  # search space (dictionary of parameter keys: tune search spaces)
           algorithm: Optional[str] = "variant_generator", # search algorithm to use, see SEARCH_ALG_IMPORT for available options
           label: Optional[str] = 'search',  # label for the search
           output_path: Optional[str] = '../batch',  # directory for storing generated files
           checkpoint_path: Optional[str] = '../ray',  # directory for storing checkpoint files
           max_concurrent: Optional[int] = 1,  # number of concurrent trials to run at one time
           batch: Optional[bool] = True,  # whether concurrent trials should run synchronously or asynchronously
           num_samples: Optional[int] = 1,  # number of trials to run
           metric: Optional[str] = "loss", # metric to optimize (this should match some key: value pair in the returned data
           mode: Optional[str] = "min",  # either 'min' or 'max' (whether to minimize or maximize the metric
           algorithm_config: Optional[dict] = None,  # additional configuration for the search algorithm
           ) -> tune.ResultGrid: # results of the search
    """
    search(...)

    Parameters
    ----------
    job_type: str, # the submission engine to run a single simulation (e.g. 'sge', 'sh')
    comm_type: str, # the method of communication between host dispatcher and the simulation (e.g. 'socket', 'filesystem')
    run_config: Dict,  # batch configuration, (keyword: string pairs to customize the submit template)
    params: Dict,  # search space (dictionary of parameter keys: tune search spaces)
    algorithm: Optional[str] = "variant_generator", # search algorithm to use, see SEARCH_ALG_IMPORT for available options
    label: Optional[str] = 'search',  # label for the search
    output_path: Optional[str] = '../batch',  # directory for storing generated files
    checkpoint_path: Optional[str] = '../ray',  # directory for storing checkpoint files
    max_concurrent: Optional[int] = 1,  # number of concurrent trials to run at one time
    batch: Optional[bool] = True,  # whether concurrent trials should run synchronously or asynchronously
    num_samples: Optional[int] = 1,  # number of trials to run
    metric: Optional[str] = "loss", # metric to optimize (this should match some key: value pair in the returned data
    mode: Optional[str] = "min",  # either 'min' or 'max' (whether to minimize or maximize the metric
    algorithm_config: Optional[dict] = None,  # additional configuration for the search algorithm

    Creates
    -------
    <label>.csv: file containing the results of the search

    Returns
    -------
    ResultGrid: tune.ResultGrid # results of the search
    """
    kwargs = locals()
    kwargs = shim(**kwargs)
    return ray_search(**kwargs)


"""
def ray_search(dispatcher_constructor, submit_constructor, algorithm = "variant_generator", label = 'search',
               params = None, concurrency = 1, output_path = '../batch', checkpoint_path = '../ray',
               run_config = None, num_samples = 1):
    ray.init(
        runtime_env={"working_dir": "."}) # needed for python import statements

    #TODO class this object for self calls? cleaner? vs nested functions
    #TODO clean up working_dir and excludes
    if checkpoint_path[0] == '/':
        storage_path = os.path.normpath(checkpoint_path)
    elif checkpoint_path[0] == '.':
        storage_path = os.path.normpath(os.path.join(os.getcwd(), checkpoint_path))
    else:
        raise ValueError("checkpoint_dir must be an absolute path (starts with /) or relative to the current working directory (starts with .)")
    algo = create_searcher(algorithm, max_concurrent=concurrency, batch=True)
    #algo = ConcurrencyLimiter(searcher=algo, max_concurrent=concurrency, batch=True)
    submit = submit_constructor()
    submit.update_templates(
        **run_config
    )
    project_path = os.getcwd()
    def run(config):
        config.update({'saveFolder': output_path, 'simLabel': LABEL_POINTER})
        data = ray_trial(config, label, dispatcher_constructor, project_path, output_path, submit)
        session.report({'data': data, 'config': config})

    tuner = tune.Tuner(
        run,
        tune_config=tune.TuneConfig(
            search_alg=algo,
            num_samples=num_samples, # grid search samples 1 for each param
            metric="data"
        ),
        run_config=RunConfig(
            storage_path=storage_path,
            name=algorithm,
        ),
        param_space=params,
    )

    results = tuner.fit()
    resultsdf = results.get_dataframe()
    resultsdf.to_csv("{}.csv".format(label))
"""




"""
from netpyne.batchtools import search, paramtypes
import numpy

https://docs.ray.io/en/latest/tune/api/doc/ray.tune.search.Searcher.html#ray.tune.search.Searcher



params = {'synMechTau2': [3.0, 5.0, 7.0], # assumes list of values by default if grid search-like algo
		  #'synMechTau2': [3.0, 7.0], # assumes lower/upper bounds by default if evol-like algo
          'connWeight' : paramtypes.sample_from(lambda _: numpy.random.uniform(0.005, 0.15))} # can optionally pass any of the paramtypes (= ray.tune data types)

run_config = {'sge': 5, 'command': 'python init.py'}

#TODO rename ray_search to search
search(dispatcher = 'inet', # defaults to 'inet' if no arg is passed?
           submit = 'socket', # defaults to 'socket' if no arg is passed?
           params = params,
           run_config = run_config, #
           algorithm = "variant_generator",
           concurrency = 9,
           output_path = '../batch_func',
           checkpoint_path = '../grid_func',
           label = 'func_search',
           num_samples = 3)
SEE:
'variant_generator'
'random' -> points to variant_generator
'ax'
'dragonfly'
'skopt'
'hyperopt'
'bayesopt'
'bohb'
'nevergrad'
'optuna'
'zoopt'
'sigopt'
'hebo'
'blendsearch'
'cfo'
"""









