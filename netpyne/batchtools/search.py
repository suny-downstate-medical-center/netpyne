import ray
import pandas
import os
from ray import tune, train
from ray.air import session, RunConfig
from ray.tune.search.basic_variant import BasicVariantGenerator
from ray.tune.search import create_searcher, ConcurrencyLimiter, SEARCH_ALG_IMPORT
from netpyne.batchtools import runtk
from collections import namedtuple
from pubtk.raytk.search import ray_trial
import numpy
"""
from netpyne.batchtools import search, paramtypes
import numpy

https://docs.ray.io/en/latest/tune/api/doc/ray.tune.search.Searcher.html#ray.tune.search.Searcher



params = {'synMechTau2': [3.0, 5.0, 7.0], # assumes list of values by default if grid search-like algo
		  #'synMechTau2': [3.0, 7.0], # assumes lower/upper bounds by default if evol-like algo
          'connWeight' : paramtypes.sample_from(lambda _: numpy.random.uniform(0.005, 0.15))} # can optionally pass any of the paramtypes (= ray.tune data types)

batch_config = {'sge': 5, 'command': 'python init.py'}

#TODO rename ray_search to search
search(dispatcher = 'inet', # defaults to 'inet' if no arg is passed?
           submit = 'socket', # defaults to 'socket' if no arg is passed?
           params = params,
           batch_config = batch_config, #
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

#should be constant?
constructors = namedtuple('constructors', 'dispatcher, submit')
constructor_tuples = {
    ('sge', 'socket'): constructors(runtk.dispatchers.INETDispatcher, runtk.submits.SGESubmitSOCK),
    #('sge', 'unix'): constructors(runtk.dispatchers.UNIXDispatcher, runtk.submits.SGESubmitSOCK), #can't use AF_UNIX sockets on networked machines
    ('sge', 'sfs' ): constructors(runtk.dispatchers.SFSDispatcher , runtk.submits.SGESubmitSFS ),
    #('zsh', 'inet'): constructors(runtk.dispatchers.INETDispatcher, runtk.submits.ZSHSubmitSOCK), #TODO preferable to use AF_UNIX sockets on local machines
    ('zsh', 'socket'): constructors(runtk.dispatchers.UNIXDispatcher, runtk.submits.ZSHSubmitSOCK),
    ('zsh', 'sfs' ): constructors(runtk.dispatchers.SFSDispatcher , runtk.submits.ZSHSubmitSFS ),
}#TODO, just say "socket"?

"""
some shim functions before ray_search
"""
def generate_constructors(job_type, comm_type = 'socket'):
    """"
    returns the dispatcher, submit constructor pair for ray_search based on the job_type and comm_type inputs
    """
    if (job_type, comm_type) not in constructor_tuples:
        raise ValueError("Invalid job_type or comm_type pairing")
    return constructor_tuples[(job_type, comm_type)]

def generate_parameters(param_dict, algo):
    """
    returns a dictionary of parameters for ray_search based on the input dictionary
    from NOTES Salvador:
    params = {'synMechTau2': [3.0, 5.0, 7.0], # assumes list of values by default if grid search-like algo
		  #'synMechTau2': [3.0, 7.0], # assumes lower/upper bounds by default if evol-like algo
          'connWeight' : paramtypes.sample_from(lambda _: numpy.random.uniform(0.005, 0.15))} # can optionally pass any of the paramtypes (= ray.tune data types)

    #TODO: bloated function, prone to error
    """
    ray_params = {}
    for param, space in param_dict.items():
        lsp = len(space) == 2
        if   isinstance(space, (list, tuple)) and algo in {'variant_generator'}:
            ray_params[param] = tune.grid_search(space)
        elif isinstance(space, (list, tuple)) and algo in SEARCH_ALG_IMPORT.keys():
            if lsp: #if 2 sample from uniform lb, ub
                ray_params[param] = tune.uniform(*space)
            else: #otherwise treat as a list
                ray_params[param] = tune.choice(space)
    return ray_params
def search(job_type, params, batch_config, algorithm, concurrency, output_path, checkpoint_path, label, num_samples = 1, comm_type='socket'): #requires some shimming
    dispatcher_constructor, submit_constructor = generate_constructors(job_type, comm_type)
    params = generate_parameters(params, algorithm)
    ray_search(dispatcher_constructor, submit_constructor, algorithm, label, params, concurrency, output_path, checkpoint_path, batch_config, num_samples)

def ray_search(dispatcher_constructor, submit_constructor, algorithm = "variant_generator", label = 'search',
               params = None, concurrency = 1, output_path = '../batch', checkpoint_path = '../ray',
               batch_config = None, num_samples = 1):
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
        **batch_config
    )
    project_path = os.getcwd()
    def run(config):
        data = ray_trial(config, label, dispatcher_constructor, project_path, output_path, submit)
        tid = ray.train.get_context().get_trial_id()
        tid = int(tid.split('_')[-1]) #integer value for the trial
        run_label = '{}_{}'.format(label, tid)
        dispatcher = dispatcher_constructor(project_path = project_path, output_path = output_path, submit = submit,
                                            gid = run_label)

        dispatcher.update_env(dictionary = config)
        dispatcher.update_env(dictionary = {
            'saveFolder': output_path,
            'simLabel': run_label,
        })
        try:
            dispatcher.run()
            dispatcher.accept()
            data = dispatcher.recv()
            dispatcher.clean()
        except Exception as e:
            dispatcher.clean()
            raise(e)
        data = pandas.read_json(data, typ='series', dtype=float)
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
