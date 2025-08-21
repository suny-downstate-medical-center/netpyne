from netpyne.batchtools.search import search

params = {
          'param_str': [ 'string0', 'string1', 'string2' ]
          }

search(job_type = 'sh',
       label = 'categorical',
       params = params,
       output_path = './grid_batch',
       checkpoint_path = './ray',
       run_config = {'command': 'python categorical.py'},
       num_samples = 1,
       algorithm = 'variant_generator',
       max_concurrent = 3)
