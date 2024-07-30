import pandas
from collections import namedtuple
def get_data(filename, params, metrics):
    data = pandas.read_csv(filename)
    param_space = data[["config/{}".format(param) for param in params]]
    param_space = param_space.rename(columns={'config/{}'.format(param): param for param in params})
    results = data[metrics]
    return namedtuple('data',['param_space', 'results'])(param_space, results)

def fanova_analysis(filename, params, metrics):
    from rfr_eval import Importance
    data = get_data(filename, params, metrics)
    importance = Importance()
    return importance.evaluate(data.param_space, data.results)

filename = 'optuna.csv'

params = ['x.0', 'x.1', 'x.2', 'x.3']
metrics = ['fx']

data = get_data('optuna.csv', params, metrics)
#f = fanova_analysis('optuna.csv', ['x.0', 'x.1', 'x.2', 'x.3'], 'fx')

#f.quantify_importance((0, 1, 2, 3))
