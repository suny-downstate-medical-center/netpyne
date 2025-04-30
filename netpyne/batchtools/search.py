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
from io import StringIO
import numpy
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from netpyne.batchtools import submits
#import signal #incompatible with signal and threading from ray
#import threading

choice = tune.choice
grid = tune.grid_search
uniform = tune.uniform

class LocalGridDispatcher(runtk.dispatchers.LocalDispatcher):
    def start(self):
        super().start(restart=True)

    def connect(self):
        return

    def recv(self, interval):
        return '{"_none_placeholder": 0}'  # dummy json value to return...

class SSHGridDispatcher(runtk.dispatchers.SSHDispatcher):
    def start(self):
        super().start(restart=True)

    def connect(self):
        return

    def recv(self, interval):
        return '{"_none_placeholder": 0}'  # dummy json value to return...

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
                      ray_config: Optional[dict] = None, # additional configuration for the ray initialization
                      clean_checkpoint = True, # whether to clean the checkpoint directory after the search
                      ) -> namedtuple('Study', ['algo', 'results']):
    """ #TODO -- fold this into the ray_search object later---
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
    ray_config:Optional[dict] = None, # additional configuration for the ray initialization

    Creates
    -------
    <label>.csv: file containing the results of the search

    Returns
    -------
    Study: namedtuple('Study', ['algo', 'results'])(algo, results), # named tuple containing the created algorithm and the results of the search
    """
    from ray.tune.search.optuna import OptunaSearch

    if ray_config is None:
        ray_config = {}
    ray_init_kwargs = ray_config#{"runtime_env": {"working_dir:": "."}} | ray_config # do not actually need to specify a working dir, can
    ray.init(**ray_init_kwargs)# TODO needed for python import statements ?
    if optuna_config == None:
        optuna_config = {}

    storage_path = get_path(checkpoint_path)
    algo = ConcurrencyLimiter(searcher=OptunaSearch(metric=metric, mode=mode, **optuna_config),
                              max_concurrent=max_concurrent,
                              batch=batch) #TODO does max_concurrent and batch work?

    #submit = submit_constructor()
    #submit.update_templates(
    #    **run_config
    #)
    project_path = os.getcwd()

    def run(config):
        config.update({'saveFolder': output_path, 'simLabel': LABEL_POINTER})
        data = ray_trial(config=config, label=label, dispatcher_constructor=dispatcher_constructor,
                         project_path=project_path, output_path=output_path, submit_constructor=submit_constructor,
                         submit_kwargs=run_config, log=None)
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
    if clean_checkpoint:
        os.system("rm -r {}".format(storage_path))
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
def prune_dataframe(results: pandas.DataFrame) -> pandas.DataFrame:
    #def process_column(column):
    #    expanded_column = column.apply(lambda x: pandas.read_csv(StringIO(x), sep='\s\s+', header=None))
    #    return pandas.DataFrame([c.values.T[1] for c in expanded_column], columns=expanded_column[0].values.T[0]).drop(columns=['dtype:'])
    # call process_column instead, with both 'config' and 'data'
    try:
        data   = results['data'].apply(lambda x: pandas.read_csv(StringIO(x), sep='\s\s+', header=None))
        df     = pandas.DataFrame([d.values.T[1] for d in data], columns=data[0].values.T[0]).iloc[ :, :-1]
    except Exception as e:
        df = results
    # use >=2 whitespace delimiter for compatibility with lists, dictionaries, where single whitespace character is placed between
    # objects.
    #config = results['config'].apply(lambda x: pandas.read_csv(StringIO(x), sep='\s+', header=None))
    return df

study = namedtuple('Study', ['results', 'data'])
def ray_search(dispatcher_constructor: Callable, # constructor for the dispatcher (e.g. INETDispatcher)
               submit_constructor: Callable, # constructor for the submit (e.g. SHubmitSOCK)
               run_config: Dict, # batch configuration, (keyword: string pairs to customize the submit template)
               params: Dict, # search space (dictionary of parameter keys: tune search spaces)
               algorithm: Optional[str] = "variant_generator", # search algorithm to use, see SEARCH_ALG_IMPORT for available options
               label: Optional[str] = 'search', # label for the search
               output_path: Optional[str] = './batch', # directory for storing generated files
               checkpoint_path: Optional[str] = './checkpoint', # directory for storing checkpoint files
               max_concurrent: Optional[int] = 1, # number of concurrent trials to run at one time
               batch: Optional[bool] = True, # whether concurrent trials should run synchronously or asynchronously
               num_samples: Optional[int] = 1, # number of trials to run
               metric: Optional[str] = None, # metric to optimize, if not supplied, no data will be collated.
               mode: Optional[str] = "min",  # either 'min' or 'max' (whether to minimize or maximize the metric
               sample_interval: Optional[int] = 15,  # interval to check for new results (in seconds)
               algorithm_config: Optional[dict] = None, # additional configuration for the search algorithm
               ray_config: Optional[dict] = None, # additional configuration for the ray initialization
               attempt_restore: Optional[bool] = True, # whether to attempt to restore from a checkpoint
               clean_checkpoint = True, # whether to clean the checkpoint directory after a completed successful search, errored searches will skip cleanup.
               report_config = ('path', 'config', 'data'), # what to report back to the user
               prune_metadata = True, # whether to prune the metadata from the results.csv
               remote_dir: Optional[str] = None, # absolute path for directory to run the search on (for submissions over SSH)
               host: Optional[str] = None,  # host to run the search on
               key: Optional[str] = None  # key for TOTP generator...
               ) -> study:

    expected_total = params.pop('_expected_trials_per_sample') * num_samples
    if (dispatcher_constructor == runtk.dispatchers.SSHDispatcher) or \
       (dispatcher_constructor == SSHGridDispatcher):
        if submit_constructor == submits.SGESubmitSFS:
            from fabric import connection
            dispatcher_kwargs = {'connection': connection.Connection(host)}
        if submit_constructor == submits.SlurmSubmitSSH:
            from batchtk.utils import TOTPConnection
            dispatcher_kwargs = {'connection': TOTPConnection(host, key)}
    else:
        dispatcher_kwargs = {}
    if ray_config is None:
        ray_config = {}

    ray_init_kwargs = ray_config#{"runtime_env": {"working_dir:": "."}} | ray_config

    ray.init(**ray_init_kwargs) # TODO needed for python import statements ?

    if algorithm_config is None:
        algorithm_config = {}

    algorithm_config = {
        'metric': metric,
        'mode': mode,
        'max_concurrent': max_concurrent,
        'batch': batch,
    } | algorithm_config

    if metric is None:
        algorithm_config['metric'] = '_none_placeholder'

    #TODO class this object for self calls? cleaner? vs nested functions
    #TODO clean up working_dir and excludes
    storage_path = get_path(checkpoint_path)
    load_path = "{}/{}".format(storage_path, label)
    algo = create_searcher(algorithm, **algorithm_config) #concurrency may not be accepted by all algo
    #search_alg – The search algorithm to use.
    #  metric – The training result objective value attribute. Stopping procedures will use this attribute.
    #  mode – One of {min, max}. Determines whether objective is minimizing or maximizing the metric attribute.
    #  **kwargs – Additional parameters. These keyword arguments will be passed to the initialization function of the chosen class.
    try:
        algo = ConcurrencyLimiter(searcher=algo, max_concurrent=algorithm_config['max_concurrent'], batch=algorithm_config['batch'])
    except:
        pass

    #submit = submit_constructor()
    #submit.update_templates(
    #    **run_config
    #)
    project_path = remote_dir or os.getcwd() # if remote_dir is None, then use the current working directory
    def run(config):
        config.update({'saveFolder': output_path, 'simLabel': LABEL_POINTER})
        data = ray_trial(config=config, label=label, dispatcher_constructor=dispatcher_constructor,
                         project_path=project_path, output_path=output_path, submit_constructor=submit_constructor,
                         dispatcher_kwargs=dispatcher_kwargs, submit_kwargs=run_config,
                         interval=sample_interval, log=None, report=report_config)
        if metric is None:
            metrics = {'data': data, '_none_placeholder': 0} #TODO, should include 'config' now with purge_metadata?
            session.report(metrics)
        elif isinstance(metric, str):
            metrics = {'data': data, metric: data[metric]}
            session.report(metrics)
        elif isinstance(metric, (list, tuple)):
            metrics = {k: data[k] for k in metric}
            metrics['data'] = data
            #metrics['config'] = config
            session.report(metrics)
        else:
            session.report({'data': data, '_none_placeholder': 0})
    if attempt_restore and tune.Tuner.can_restore(load_path):#TODO check restore
        print("resuming previous run from {}".format(load_path))
        tuner = tune.Tuner.restore(path=load_path,
                                   trainable=run,
                                   resume_unfinished=True,
                                   resume_errored=False,
                                   restart_errored=True,
                                   param_space=params,
                                   )
    else:
        print("starting new run to {}".format(load_path))
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
                name=label,
            ),
            param_space=params,
        )
    results = tuner.fit()
    errors = results.errors
    df = results.get_dataframe() # note that results.num_terminated DOES NOT CURRENTLY reflect collected datapoints.
    num_total = len(df)
    if errors or num_total < expected_total:
        print("errors/SIGINT occurred during execution: {}".format(errors))
        print("only {} of {} expected trials completed successfully".format(num_total, expected_total))
        print("see {} for more information".format(output_path))
        print("keeping {} checkpoint directory".format(load_path))
        print("rerunning the same search again will restore valid checkpointed data in {}".format(load_path))
        if prune_metadata:
            df = prune_dataframe(df)
        print("saving current results to {}.csv".format(label))
        df.to_csv("{}.csv".format(label))
        return study( results, df)
    #df = results.get_dataframe()
    if prune_metadata:
        df = prune_dataframe(df)
    print("saving results to {}.csv".format(label))
    df.to_csv("{}.csv".format(label))
    if clean_checkpoint:
        os.system("rm -r {}".format(load_path))
    return study( results, df)

#should be constant?
constructors = namedtuple('constructors', 'dispatcher, submit')
constructor_tuples = {
    ('sge', 'socket'): constructors(runtk.dispatchers.INETDispatcher, submits.SGESubmitSOCK),
    ('sge', 'sfs' ): constructors(runtk.dispatchers.LocalDispatcher , submits.SGESubmitSFS ),
    ('sge', None): constructors(LocalGridDispatcher, submits.SGESubmit),
    ('ssh_sge', 'sftp'): constructors(runtk.dispatchers.SSHDispatcher, submits.SGESubmitSSH), #TODO, both of these need comm types
    ('ssh_slurm', 'sftp'): constructors(runtk.dispatchers.SSHDispatcher, submits.SlurmSubmitSSH),
    ('ssh_sge', None): constructors(SSHGridDispatcher, submits.SGESubmitSSH), #don't need to worry about changing the handl
    ('ssh_slurm', None): constructors(SSHGridDispatcher, submits.SlurmSubmitSSH),
    #('zsh', 'inet'): constructors(runtk.dispatchers.INETDispatcher, runtk.submits.ZSHSubmitSOCK), #TODO preferable to use AF_UNIX sockets on local machines
    #('slurm', 'socket'): constructors(runtk.dispatchers.INETDispatcher, submits.SlurmSubmitSOCK),
    #('slurm', 'sfs' ): constructors(runtk.dispatchers.SFSDispatcher , submits.SlurmSubmitSFS),
    ('sh', 'socket'): constructors(runtk.dispatchers.INETDispatcher, submits.SHSubmitSOCK), #
    ('sh', 'sfs' ): constructors(runtk.dispatchers.LocalDispatcher , submits.SHSubmitSFS),
    ('sh', None): constructors(LocalGridDispatcher, submits.SHSubmit),
}#TODO, just say "socket"?

def load_search(path: str, prune_metadata=True) -> pandas.DataFrame:
    def run(config):
        pass
    path = get_path(path)
    try:
        tuner = tune.Tuner.restore(path, run)
    except Exception as e:
        raise e
    df = tuner.get_results().get_dataframe()
    if prune_metadata:
        df = prune_dataframe(df)
    return df
"""
some shim functions before ray_search
"""
def generate_constructors(job_type, comm_type, **kwargs):
    """"
    returns the dispatcher, submit constructor pair for ray_search based on the job_type and comm_type inputs
    """
    if (job_type, comm_type) not in constructor_tuples:
        raise ValueError("Invalid job_type or comm_type pairing")
    return constructor_tuples[(job_type, comm_type)]

def generate_parameters(params, algorithm, **kwargs):
    """
    returns a dictionary of parameters for ray_search based on the input dictionary
    from NOTES Salvador:
    params = {'synMechTau2': [3.0, 5.0, 7.0], # assumes list of values by default if grid search-like algo
		  #'synMechTau2': [3.0, 7.0], # assumes lower/upper bounds by default if evol-like algo
          'connWeight' : paramtypes.sample_from(lambda _: numpy.random.uniform(0.005, 0.15))} # can optionally pass any of the paramtypes (= ray.tune data types)

    #TODO: check coverage of conditional statements (looks okay?)
    """
    ray_params = {}
    _expected_trials_per_sample = 1
    for param, space in params.items():
        if   isinstance(space, (list, tuple, range, numpy.ndarray)) and algorithm in {'variant_generator'}:
            ray_params[param] = tune.grid_search(space) #specify random for uniform and choice.
            _expected_trials_per_sample *= len(space)
        elif isinstance(space, (list, tuple)) and algorithm in SEARCH_ALG_IMPORT.keys():
            if len(space) == 2: #if 2 sample from uniform lb, ub
                ray_params[param] = tune.uniform(*space)
            else: #otherwise treat as a list for a categorical search
                ray_params[param] = tune.choice(space)
        else: #assume a tune search space was defined
            ray_params[param] = space
            if isinstance(space, dict):
                _expected_trials_per_sample *= len(space['grid_search'])
    ray_params['_expected_trials_per_sample'] = _expected_trials_per_sample
    return ray_params


def shim(dispatcher_constructor: Optional[Callable] = None, # constructor for the dispatcher (e.g. INETDispatcher)
         submit_constructor: Optional[Callable] = None, # constructor for the submit (e.g. SHubmitSOCK)
         job_type: Optional[str] = None, # the submission engine to run a single simulation (e.g. 'sge', 'sh')
         comm_type: Optional[str] = None, # the method of communication between host dispatcher and the simulation (e.g. 'socket', 'sfs' (shared filesystem), None (no communication) )
         run_config: Optional[Dict] = None,  # batch configuration, (keyword: string pairs to customize the submit template)
         params: Optional[Dict] = None,  # search space (dictionary of parameter keys: tune search spaces)
         algorithm: Optional[str] = "variant_generator", # search algorithm to use, see SEARCH_ALG_IMPORT for available options
         label: Optional[str] = 'search',  # label for the search
         output_path: Optional[str] = './batch',  # directory for storing generated files
         checkpoint_path: Optional[str] = './checkpoint',  # directory for storing checkpoint files
         max_concurrent: Optional[int] = 1,  # number of concurrent trials to run at one time
         batch: Optional[bool] = True,  # whether concurrent trials should run synchronously or asynchronously
         num_samples: Optional[int] = 1,  # number of trials to run
         metric: Optional[str] = None, # metric to optimize (this should match some key: value pair in the returned data
         mode: Optional[str] = "min",  # either 'min' or 'max' (whether to minimize or maximize the metric
         sample_interval: Optional[int] = 15,  # interval to check for new results (in seconds)
         algorithm_config: Optional[dict] = None,  # additional configuration for the search algorithm
         ray_config: Optional[dict] = None,  # additional configuration for the ray initialization
         attempt_restore: Optional[bool] = True, # whether to attempt to restore from a checkpoint
         clean_checkpoint: Optional[bool] = True, # whether to clean the checkpoint directory after the search
         report_config=('path', 'config', 'data'),  # what to report back to the user
         prune_metadata: Optional[bool] = True, # whether to prune the metadata from the results.csv
         remote_dir: Optional[str] = None, # absolute path for directory to run the search on (for submissions over SSH)
         host: Optional[str] = None,  # host to run the search on
         key: Optional[str] = None  # key for TOTP generator...
         ) -> Dict:
    kwargs = locals()
    if metric is None and algorithm not in ['variant_generator', 'random', 'grid']:
        raise ValueError("a metric (string) must be specified for optimization searches")
    if algorithm == 'grid':
        kwargs['algorithm'] = 'variant_generator'
    if job_type is not None and (comm_type is not None or metric is None):
        kwargs['dispatcher_constructor'], kwargs['submit_constructor'] = generate_constructors(job_type, comm_type)
    if dispatcher_constructor is not None and (submit_constructor is not None or metric is None):
        kwargs['dispatcher_constructor'] = dispatcher_constructor
        kwargs['submit_constructor'] = submit_constructor
    if kwargs['dispatcher_constructor'] is None or (kwargs['submit_constructor'] is None and metric is not None):
        raise ValueError("missing job method and communication type for an optimization search, either specify a dispatcher_constructor and submit_constructor or a job_type and comm_type")
    if (kwargs['dispatcher_constructor'] == runtk.dispatchers.SSHDispatcher) and (host is None or remote_dir is None):
        raise ValueError("missing host and remote directory for SSH based dispatcher")
    if (kwargs['submit_constructor'] == submits.SlurmSubmitSSH) and key is None:
        raise ValueError("missing key for Slurm based dispatcher")
    if kwargs['dispatcher_constructor'] is None:
        raise ValueError("missing job type for grid or random based search, specify a job type")
    if params is None:
        raise ValueError("missing parameters, specify params")
    if run_config is None:
        run_config = {}
    [kwargs.pop(args) for args in ['job_type', 'comm_type']]
    kwargs['params'] = generate_parameters(**kwargs)
    return kwargs


def search(dispatcher_constructor: Optional[Callable] = None, # constructor for the dispatcher (e.g. INETDispatcher)
           submit_constructor: Optional[Callable] = None, # constructor for the submit (e.g. SHubmitSOCK)
           job_type: Optional[str] = None, # the submission engine to run a single simulation (e.g. 'sge', 'sh')
           comm_type: Optional[str] = None, # the method of communication between host dispatcher and the simulation (e.g. 'socket', 'filesystem')
           run_config: Optional[dict] = None,  # batch configuration, (keyword: string pairs to customize the submit template)
           params: Optional[dict] = None,  # search space (dictionary of parameter keys: tune search spaces)
           algorithm: Optional[str] = "variant_generator", # search algorithm to use, see SEARCH_ALG_IMPORT for available options
           label: Optional[str] = 'search',  # label for the search
           output_path: Optional[str] = './batch',  # directory for storing generated files
           checkpoint_path: Optional[str] = './checkpoint',  # directory for storing checkpoint files
           max_concurrent: Optional[int] = 1,  # number of concurrent trials to run at one time
           batch: Optional[bool] = True,  # whether concurrent trials should run synchronously or asynchronously
           num_samples: Optional[int] = 1,  # number of trials to run
           metric: Optional[str] = None, # metric to optimize (this should match some key: value pair in the returned data
           mode: Optional[str] = "min",  # either 'min' or 'max' (whether to minimize or maximize the metric
           sample_interval: Optional[int] = 15,  # interval to check for new results (in seconds)
           algorithm_config: Optional[dict] = None,  # additional configuration for the search algorithm
           ray_config: Optional[dict] = None,  # additional configuration for the ray initialization
           attempt_restore: Optional[bool] = True, # whether to attempt to restore from a checkpoint
           clean_checkpoint: Optional[bool] = True, # whether to clean the checkpoint directory after the search
           report_config=('path', 'config', 'data'),  # what to report back to the user
           prune_metadata: Optional[bool] = True, # whether to prune the metadata from the results.csv
           remote_dir: Optional[str] = None, # absolute path for directory to run the search on (for submissions over SSH)
           host: Optional[str] = None, # host to run the search on
           key: Optional[str] = None # key for TOTP generator...
           ) -> study: # results of the search
    """
    search(...)

    Parameters
    ----------
    dispatcher_constructor: Callable, # constructor for the dispatcher (e.g. INETDispatcher)
    submit_constructor: Callable, # constructor for the submit (e.g. SHubmitSOCK)
    job_type: str, # the submission engine to run a single simulation (e.g. 'sge', 'sh')
    comm_type: Optional[str], # the method of communication between host dispatcher and the simulation (e.g. 'socket', 'filesystem', None), if None, expects a non-optimization based search (grid/random/etc.)
    run_config: Dict,  # batch configuration, (keyword: string pairs to customize the submit template)
    params: Dict,  # search space (dictionary of parameter keys: tune search spaces)
    algorithm: Optional[str] = "variant_generator", # search algorithm to use, see SEARCH_ALG_IMPORT for available options
    label: Optional[str] = 'search',  # label for the search
    output_path: Optional[str] = './batch',  # directory for storing generated files
    checkpoint_path: Optional[str] = './ray',  # directory for storing checkpoint files
    max_concurrent: Optional[int] = 1,  # number of concurrent trials to run at one time
    batch: Optional[bool] = True,  # whether concurrent trials should run synchronously or asynchronously
    num_samples: Optional[int] = 1,  # number of trials to run
    metric: Optional[str] = None, # metric to optimize (this should match some key: value pair in the returned data, or None if no optimization is desired
    mode: Optional[str] = "min",  # either 'min' or 'max' (whether to minimize or maximize the metric
    sample_interval: Optional[int] = 15,  # interval to check for new results (in seconds)
    algorithm_config: Optional[dict] = None,  # additional configuration for the search algorithm
    ray_config: Optional[dict] = None,  # additional configuration for the ray initialization
    attempt_restore: Optional[bool] = True, # whether to attempt to restore from a checkpoint
    clean_checkpoint: Optional[bool] = True, # whether to clean the checkpoint directory after the search
    prune_metadata: Optional[bool] = True, # whether to prune the metadata from the results.csv
    remote_dir: Optional[str] = None, # absolute path for directory to run the search on (for submissions over SSH)
    host: Optional[str] = None, # host to run the search on (for submissions over SSH)
    key: Optional[str] = None # key for TOTP generator (for submissions over SSH)
    Creates (upon completed fitting run...)
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











