from optuna.importance._fanova._fanova import _Fanova
import numpy
class Importance(object):
    def __init__(self, n_trees: int = 64, max_depth: int = 64, seed: int | None = None) -> None:
        self._evaluator = _Fanova(
            n_trees=n_trees,
            max_depth=max_depth,
            min_samples_split=2,
            min_samples_leaf=1,
            seed=seed,
        )

    def evaluate(self, X, y):
        evaluator = self._evaluator
        mins, maxs = X.min().values, X.max().values
        search_spaces = numpy.array([X.min().values, X.max().values]).T # bounds
        column_to_encoded_columns = [numpy.atleast_1d(i) for i in range(X.shape[1])] # encoding (no 1 hot/categorical)
        evaluator.fit(X.values, y.values.ravel(), search_spaces, column_to_encoded_columns)
        importances = numpy.array(
            [evaluator.get_importance(i)[0] for i in range(X.shape[1])]
        )
        return {col: imp for col, imp in zip(X.columns, importances)}
