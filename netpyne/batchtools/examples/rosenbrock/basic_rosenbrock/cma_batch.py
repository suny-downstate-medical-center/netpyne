from batchtk.runtk.trial import trial, LABEL_POINTER, PATH_POINTER
from netpyne.batchtools import dispatchers, submits
from cmaes import CMA
import numpy
import os
Dispatcher = dispatchers.INETDispatcher
Submit = submits.SHSubmitSOCK

cwd = os.getcwd()

def eval_rosenbrock(x0, x1, tid):
    cfg = {
        'x0': x0,
        'x1': x1,
    }
    submit = Submit()
    submit.update_templates(**{'command': 'python rosenbrock.py',})
    label = 'rosenbrock'
    return float(trial(cfg, label, tid, Dispatcher, cwd, '../cma', submit)['fx'])

#data = eval_rosenbrock(1, 1, "x11")

optimizer = CMA(mean=numpy.zeros(2), sigma=1.0)
for generation in range(3):
    solutions = []
    for cand in range(optimizer.population_size):
        x = optimizer.ask()
        value = eval_rosenbrock(x[0], x[1], "{}_{}".format(cand, generation))
        solutions.append((x, value))
        print(f"#{generation} {value} (x1={x[0]}, x2 = {x[1]})")
    optimizer.tell(solutions)
