from netpyne.batchtools.search import search
import numpy

params = {'nmda.PYR->BC' : numpy.linspace(1e-3, 1.8e-3, 3),
          #'nmda.PYR->OLM': numpy.linspace(0.4e-3, 1.0e-3, 3),
          #'nmda.PYR->PYR': numpy.linspace(0.001e-3, 0.007e-3, 3),
          'ampa.PYR->BC' : numpy.linspace(0.2e-3, 0.5e-3, 3),
          #'ampa.PYR->OLM': numpy.linspace(0.2e-3, 0.5e-3, 3),
          #'ampa.PYR->PYR': numpy.linspace(0.01e-3, 0.03e-3, 3),
          #'gaba.BC->BC'  : numpy.linspace(1e-3, 7e-3, 3),
          'gaba.BC->PYR' : numpy.linspace(0.4e-3, 1.0e-3, 3),
          #'gaba.OLM->PYR': numpy.linspace(40e-3, 100e-3, 3),
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


run_config = sge_config

search(job_type = 'sge', # 'sh', and ssh based options
       comm_type = 'socket', # 'socket', 'sfs', None
       label = 'grid',
       params = params,
#       output_path = './batch', # defaults to ./batch
#       checkpoint_path = './checkpoint', # defaults to ./checkpoint
       run_config = run_config,
       metric = 'loss', # if a metric and mode is specified, the search will collect metric data and report on the optimal configuration
       mode = 'min',
       algorithm = 'grid',
       max_concurrent = 9)
