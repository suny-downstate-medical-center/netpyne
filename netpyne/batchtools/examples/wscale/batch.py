from netpyne.batchtools.search import search
import json
import numpy

with open('Na12HH16HH_TF.json', 'r') as fptr:
    #cell_params = pickle.load(fptr, encoding='latin1')
    cell_params = json.load(fptr)

filtered_secs = ['axon_1'] # will only run the search on this one section.

sec_loc = [
    [sec, loc]
    for sec in cell_params['secs'] if sec in filtered_secs
    for loc in numpy.linspace(0, 1, cell_params['secs'][sec]['geom']['nseg'] + 2)[1:-1]
]

weights = list(numpy.linspace(0.01, 0.2, 2)/100.0) #can increase granularity of weights

params = {
    'sec_loc': sec_loc,
    'weight': weights,
}

# use batch_shell_config if running directly on the machine
shell_config = {"command": "python test.py"}

run_config = shell_config


result_grid = search(job_type='sh',
                     comm_type="socket",
                     params=params,
                     run_config=shell_config,
                     label="wscale_search",
                     output_path="./wscale_batch",
                     checkpoint_path="./ray",
                     num_samples=1,
                     metric='epsp',
                     mode='min',
                     algorithm="grid",
                     max_concurrent=5)
