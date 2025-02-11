from netpyne.batchtools.search import search

params = {
          'param_str': [ 'string0', 'string1', 'string2' ]
          }

search(job_type = 'sh', # when not specifying a comm type, metric or mode, the job will simply be dispatched
       label = 'categorical',
       params = params,
       output_path = './grid_batch',
       checkpoint_path = './ray',
       run_config = {'command': 'python categorical.py'},
       algorithm = 'grid',
       max_concurrent = 3)