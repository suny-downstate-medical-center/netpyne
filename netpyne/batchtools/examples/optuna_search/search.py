from batchtk.algos import optuna_search
from batchtk.utils import expand_path

from netpyne.batchtools.search import generate_constructors

#option for local run
dispatcher, submit = generate_constructors('sh', 'sfs')

#option for slurm run
#dispatcher, submit = generate_constructors('slurm', 'sfs')
slurm_args = {
    'allocation': 'csd403',
    'realtime': '00:30:00',
    'nodes': '1',
    'coresPerNode': '1',
    'mem': '4G',
    'partition': 'shared',
    'email': '<user_email_here>',
    'custom': '',
    'command': 'python single_opt.py',
}

slurm_args = {
    'allocation': 'csd403',
    'realtime': '00:30:00',
    'nodes': '1',
    'coresPerNode': '1',
    'mem': '4G',
    'partition': 'shared',
    'email': 'jchen.6727@gmail.com',
    'custom': '',
    'command': 'python single_opt.py',
}
results = optuna_search(
    study_label='rosenbrock',
    param_space={'x0': (-5, 5), 'x1': (-5, 5)},
    metrics={'fx': 'minimize'},
    num_trials=12, num_workers=3,
    dispatcher_constructor=dispatcher,
    submit_constructor=submit,
    submit_kwargs={'command': 'python single_opt.py'}, # normal run
    #submit_kwargs=slurm_args,
    interval=10,
    project_path='.',
    output_path=expand_path('./optimization', create_dirs=True),
)
