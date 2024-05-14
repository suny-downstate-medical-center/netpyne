from netpyne.batchtools.search import ray_optuna_search
from netpyne.batchtools import dispatchers, submits
import batchtk

from ray import tune

params = {'nmda.PYR->BC' : tune.uniform(1e-3, 1.8e-3),
          #'nmda.PYR->OLM': tune.uniform(0.4e-3, 1.0e-3),
          #'nmda.PYR->PYR': tune.uniform(0.001e-3, 0.007e-3),
          'ampa.PYR->BC' : tune.uniform(0.2e-3, 0.5e-3),
          #'ampa.PYR->OLM': tune.uniform(0.2e-3, 0.5e-3),
          #'ampa.PYR->PYR': tune.uniform(0.01e-3, 0.03e-3),
          #'gaba.BC->BC'  : tune.uniform(1e-3, 7e-3),
          'gaba.BC->PYR' : tune.uniform(0.4e-3, 1.0e-3),
          #'gaba.OLM->PYR': tune.uniform(40e-3, 100e-3),
          }

# use batch_shell_config if running directly on the machine
shell_config = {'command': 'mpiexec -np 4 nrniv -python -mpi init.py',}

# use batch_sge_config if running on a
sge_config = {
    'queue': 'cpu.q',
    'cores': 5,
    'vmem': '4G',
    'realtime': '00:30:00',
    'command': 'mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py'}

run_config = shell_config

Dispatcher = dispatchers.INETDispatcher
Submit = submits.SGESubmitSOCK
metrics = ['PYR_loss', 'BC_loss', 'OLM_loss', 'loss']

ray_study = ray_optuna_search(
                dispatcher_constructor = Dispatcher,
                submit_constructor=Submit,
                params = params,
                run_config = run_config,
                max_concurrent = 3,
                output_path = '../mo_batch',
                checkpoint_path = '../ray',
                label = 'mo_search',
                num_samples = 15,
                metric = metrics,
                mode = ['min', 'min', 'min', 'loss'],)

results = {
    metric: ray_study.results.get_best_result(metric, 'min') for metric in metrics
}
