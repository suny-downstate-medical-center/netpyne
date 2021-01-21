import optuna
from time import sleep
from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

def objective(trial, min_x, max_x):

    x = trial.suggest_uniform('x', min_x, max_x)
    return (x - 2)** 2

    '''
    # Categorical parameter
    optimizer = trial.suggest_categorical('optimizer', ['MomentumSGD', 'Adam'])

    # Int parameter
    num_layers = trial.suggest_int('num_layers', 1, 3)

    # Uniform parameter
    dropout_rate = trial.suggest_uniform('dropout_rate', 0.0, 1.0)

    # Loguniform parameter
    learning_rate = trial.suggest_loguniform('learning_rate', 1e-5, 1e-2)

    # Discrete-uniform parameter
    drop_path_rate = trial.suggest_discrete_uniform('drop_path_rate', 0.0, 1.0, 0.1)
    '''

min_x = 1
max_x = 10
sleep(rank)
study = optuna.create_study(study_name='test1', storage='sqlite:///example.db', load_if_exists=True)
study.optimize(lambda trial: objective(trial, min_x, max_x), n_trials=10) #timeout

if rank == size-1:
    print(study.best_params)
    print(study.best_value)
    print(study.best_trial)

    df = study.trials_dataframe(attrs=('number', 'value', 'params', 'state'))
    importance = optuna.importance.get_param_importances(study=study)
