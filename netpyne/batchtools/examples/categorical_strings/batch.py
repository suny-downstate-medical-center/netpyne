from netpyne.batchtools.search import search

params = {
          'param_str': [ 'string0', 'string1', 'string2' ]
          }

search(job_type = 'sh', # grid based search with no communication (only works for grid or random searches)
       label = 'categorical',
       params = params,
       run_config = {'command': 'python categorical.py'},
       num_samples = 1,
       algorithm = 'variant_generator',
       max_concurrent = 3)
