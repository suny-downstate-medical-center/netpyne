from netpyne.batchtools.search import search
import numpy

params = {'x.0': numpy.linspace(-1, 3, 5),
          'x.1': numpy.linspace(-1, 3, 5),
          'x.2': numpy.linspace(-1, 3, 5),
          'x.3': numpy.linspace(-1, 3, 5),
          }

# use shell_config if running directly on the machine
shell_config = {'command': 'python rosenbrock.py',}

search(job_type = 'sh', # or sh
       comm_type = 'socket',
       label = 'grid',
       params = params,
       run_config = {'command': 'python rosenbrock.py'},
       num_samples = 1,
       metric = 'fx',
       mode = 'min',
       algorithm = 'variant_generator',
       max_concurrent = 3)
