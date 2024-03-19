import ray
import pandas
import os
from ray import tune, train
from ray.air import session, RunConfig
from ray.tune.search.basic_variant import BasicVariantGenerator
from ray.tune.search import create_searcher, ConcurrencyLimiter, SEARCH_ALG_IMPORT

"""
SEE:
'variant_generator'
'random'
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




def ray_search(dispatcher_constructor, submit_constructor, algorithm = "variant_generator", label = 'search',
               params = None, concurrency = 1, output_path = '../batch', checkpoint_path = '../ray',
               batch_config = None):
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
    algo = create_searcher(algorithm)
    algo = ConcurrencyLimiter(searcher=algo, max_concurrent=concurrency, batch=True)

    submit = submit_constructor()
    submit.update_templates(
        **batch_config
    )
    project_path = os.getcwd()
    def run(config):
        tid = ray.train.get_context().get_trial_id()
        tid = int(tid.split('_')[-1]) #integer value for the trial
        run_label = '{}_{}'.format(label, tid)
        dispatcher = dispatcher_constructor(project_path = project_path, output_path = output_path, submit = submit,
                                            gid = run_label)

        dispatcher.update_env(dictionary = config)
        try:
            dispatcher.run()
            dispatcher.accept()
            data = dispatcher.recv()
            dispatcher.clean()
        except Exception as e:
            dispatcher.clean()
            raise(e)
        data = pandas.read_json(data, typ='series', dtype=float)
        session.report({'data': data})

    tuner = tune.Tuner(
        run,
        tune_config=tune.TuneConfig(
            search_alg=algo,
            num_samples=1, # grid search samples 1 for each param
            metric="data"
        ),
        run_config=RunConfig(
            storage_path=checkpoint_path,
            name=algorithm,
        ),
        param_space=params,
    )

    results = tuner.fit()
    resultsdf = results.get_dataframe()
    resultsdf.to_csv("{}.csv".format(label))


def ray_grid_search(dispatcher_constructor, submit_constructor, label = 'grid', params = None, concurrency = 1, checkpoint_dir = '../grid', batch_config = None):
    ray.init(
        runtime_env={"working_dir": ".", # needed for python import statements
                     "excludes": ["*.csv", "*.out", "*.run",
                                  "*.sh" , "*.sgl", ]}
    )
    #TODO class this object for self calls? cleaner? vs nested functions
    #TODO clean up working_dir and excludes

    for key, val in params.items():
        if 'grid_search' not in val: #check that parametrized to grid_search
            params[key] = tune.grid_search(val)

    #brief check path
    if checkpoint_dir[0] == '/':
        storage_path = os.path.normpath(checkpoint_dir)
    elif checkpoint_dir[0] == '.':
        storage_path = os.path.normpath(os.path.join(os.getcwd(), checkpoint_dir))
    else:
        raise ValueError("checkpoint_dir must be an absolute path (starts with /) or relative to the current working directory (starts with .)")
    #TODO check that write permissions to path are possible
    """
    if os.path.exists(checkpoint_dir):
        storage_path = os.path.normpath(checkpoint_dir)
    else:
        storage_path = os.path.normpath(os.path.join(os.getcwd(), checkpoint_dir))
    """
    algo = create_searcher('variant_generator')
    algo = ConcurrencyLimiter(searcher=algo, max_concurrent=concurrency, batch=True)
    submit = submit_constructor()
    submit.update_templates(
        **batch_config
    )
    cwd = os.getcwd()
    def run(config):
        tid = ray.train.get_context().get_trial_id()
        tid = int(tid.split('_')[-1]) #integer value for the trial
        dispatcher = dispatcher_constructor(cwd = cwd, submit = submit, gid = '{}_{}'.format(label, tid))
        dispatcher.update_env(dictionary = config)
        try:
            dispatcher.run()
            dispatcher.accept()
            data = dispatcher.recv(1024)
            dispatcher.clean([])
        except Exception as e:
            dispatcher.clean([])
            raise(e)
        data = pandas.read_json(data, typ='series', dtype=float)
        session.report({'data': data})

    tuner = tune.Tuner(
        run,
        tune_config=tune.TuneConfig(
            search_alg=algo,
            num_samples=1, # grid search samples 1 for each param
            metric="data"
        ),
        run_config=RunConfig(
            storage_path=storage_path,
            name="grid",
        ),
        param_space=params,
    )

    results = tuner.fit()
    resultsdf = results.get_dataframe()
    resultsdf.to_csv("{}.csv".format(label))