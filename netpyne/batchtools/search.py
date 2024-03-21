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

def search():
    pass


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
