from netpyne.batchtools.search import search

params = {'nmda.PYR->BC' : [1e-3, 1.8e-3],
          #'nmda.PYR->OLM': [0.4e-3, 1.0e-3],
          #'nmda.PYR->PYR': [0.001e-3, 0.007e-3],
          'ampa.PYR->BC' : [0.2e-3, 0.5e-3],
          #'ampa.PYR->OLM': [0.2e-3, 0.5e-3],
          #'ampa.PYR->PYR': [0.01e-3, 0.03e-3],
          #'gaba.BC->BC'  : [1e-3, 7e-3],
          'gaba.BC->PYR' : [0.4e-3, 1.0e-3],
          #'gaba.OLM->PYR': [40e-3, 100e-3],
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

search(job_type = 'sh',
       comm_type = 'socket',
       label = 'search',
       params = params,
       output_path = '../optuna_batch',
       checkpoint_path = '../ray',
       run_config = run_config,
       num_samples = 1,
       metric = 'loss',
       mode = 'min',
       algorithm = 'optuna',
       max_concurrent = 4)
