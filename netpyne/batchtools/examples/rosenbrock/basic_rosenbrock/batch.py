from netpyne.batchtools.search import search

params = {'x0': [0, 3],
          'x1': [0, 3]
          }

# use shell_config if running directly on the machine
shell_config = {'command': 'python rosenbrock.py',}

search(job_type = 'sh', # or sh
       comm_type = 'socket',
       label = 'optuna',
       params = params,
       output_path = '../optuna_batch',
       checkpoint_path = '../ray',
       run_config = {'command': 'python rosenbrock.py'},
       num_samples = 9,
       metric = 'fx',
       mode = 'min',
       algorithm = 'optuna',
       max_concurrent = 3)
