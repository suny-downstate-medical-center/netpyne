from netpyne.batchtools.search import search
import numpy
x0 = numpy.arange(0, 3)
x1 = x0**2

x0_x1 = [*zip(x0.tolist(), x1.tolist())]
params = {'x0_x1': x0_x1
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