import pandas
from collections import namedtuple
import numpy

from optuna.importance._fanova._fanova import _Fanova


class Fanova(object):
    def __init__(self, n_trees: int = 64, max_depth: int = 64, seed: int | None = None) -> None:
        self._evaluator = _Fanova(
            n_trees=n_trees,
            max_depth=max_depth,
            min_samples_split=2,
            min_samples_leaf=1,
            seed=seed,
        )

    def evaluate(self, X: pandas.DataFrame, y: pandas.DataFrame) -> dict:
        assert X.shape[0] == y.shape[0] # all rows must be present
        assert y.shape[1] == 1 # only evaluation for single metric supported

        evaluator = self._evaluator
        #mins, maxs = X.min().values, X.max().values #in case bound matching is necessary.
        search_spaces = numpy.array([X.min().values, X.max().values]).T # bounds
        column_to_encoded_columns = [numpy.atleast_1d(i) for i in range(X.shape[1])] # encoding (no 1 hot/categorical)
        evaluator.fit(X.values, y.values.ravel(), search_spaces, column_to_encoded_columns)
        importances = numpy.array(
            [evaluator.get_importance(i)[0] for i in range(X.shape[1])]
        )
        return {col: imp for col, imp in zip(X.columns, importances)}


class Analyzer(object):
    def __init__(self,
                 params: list, # list of parameters
                 metrics: list, # list of metrics
                 evaluator = Fanova()) -> None:
        self.params = params
        self.metrics = metrics
        self.data = None
        self.evaluator = evaluator

    def load_file(self,
                  filename: str # filename (.csv) containing the completed batchtools trials
                  ) -> None:
        data = pandas.read_csv(filename)
        param_space = data[["config/{}".format(param) for param in self.params]]
        param_space = param_space.rename(columns={'config/{}'.format(param): param for param in self.params})
        results = data[self.metrics]
        self.data = namedtuple('data', ['param_space', 'results'])(param_space, results)

    def run_analysis(self) -> dict:
        return self.evaluator.evaluate(self.data.param_space, self.data.results)


