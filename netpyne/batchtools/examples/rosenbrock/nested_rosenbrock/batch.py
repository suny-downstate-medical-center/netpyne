from netpyne.batchtools.search import search
import numpy


params = {'xn.0': numpy.arange(0, 5),
          'xn.1': numpy.arange(0, 5)
          }

# use shell_config if running directly on the machine
shell_config = {'command': 'python rosenbrock.py',}

search(job_type = 'sh', # or sh
       comm_type = 'socket',
       label = 'grid',
       params = params,
       output_path = '../grid_batch',
       checkpoint_path = '../ray',
       run_config = {'command': 'python rosenbrock.py'},
       num_samples = 1,
       metric = 'fx',
       mode = 'min',
       algorithm = 'variant_generator',
       max_concurrent = 3)