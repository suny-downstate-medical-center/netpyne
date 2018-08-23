from netpyne import specs, batch

def batchEvol():
	params = specs.ODict()
	params['prob'] = [0.01, 0.5]
	params['weight'] = [0.001, 0.1]
	params['delay'] = [1, 20]
		
	# create Batch object with paramaters to modify, and specifying files to use
	b = batch.Batch(params=params)
	
	# Set output folder, grid method (all param combinations), and run configuration
	b.batchLabel = 'simple_evol'
	b.method = 'evol'
	b.runCfg = {
		'type': 'mpi_bulletin',#'hpc_slurm',#'mpi_bulletin',
		'script': 'init.py',
		'mpiCommand': 'mpirun',
		'nodes': 1,
		'coresPerNode': 2,
		'allocation': 'default',
		'email': 'salvadordura@gmail.com',
		'reservation': None,
		'folder': '/home/salvadord/evol'
		#'custom': 'export LD_LIBRARY_PATH="$HOME/.openmpi/lib"' # only for conda users =)
	}
	b.evolCfg = {
		'pop_size': 10,
		'num_elites': 1, # keep this number of parent for next generation
		'maximize': False, # maximize fitness function?
		'mutation_rate': 0.1,
		'max_generations': 5,
		'mutation_strength': 0.65, # <1 mutation is close to original. >1 mutation is far from original. 
		'fitness': 'abs(17 - float(len(simData["spkt"])) / 40)', # fitness extression. shoud read simData
		'time_sleep': 5, # wait this time before checking again if sim is completed (for each generation)
		'maxiter_wait': 40, # max number of times to check if sim is completed (for each generation)
		'default_fitness': 15000 # set fitness value in case simulation time is over
	}
	# Run batch simulations
	b.run()

# Main code
if __name__ == '__main__':
	batchEvol() 
