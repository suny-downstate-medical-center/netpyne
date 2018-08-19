from netpyne import specs
from batch import Batch 

def batchEvol():
	# create Batch object with paramaters to modify, and specifying files to use
	b = Batch(cfgFile='simConfig.py', netParamsFile='netParams.py')
	
	# Set output folder, grid method (all param combinations), and run configuration
	b.batchLabel = 'dentateGyrus'
	b.method = 'evol'
	b.runCfg = {
		'type': 'hpc_slurm', # hpc_torque or hpc_slurm 
		'script': 'init.py',
		'mpiCommand': 'ibrun',
		'paramLabels': ['prob', 'weight', 'delay'],
		'nodes': 1,
		'coresPerNode': 1,
		'allocation': 'csd403',
		'email': 'frodriguez4600@gmail.com',
		'reservation': None,
		#'custom': 'export LD_LIBRARY_PATH="$HOME/.openmpi/lib"' # only for conda users =)
	}
	b.evolCfg = {
		'pop_size': 2,
		'num_elites': 1, # keep this number of parent for next generation
		'maximize': False, # maximize fitness function?
		'mutation_rate': 0.1,
		'max_generations': 2,
		'mutation_strength': 0.65, # <1 mutation is close to original. >1 mutation is far from original. 
		'upper_bound' : [0.5,   0.1,   20], # upper value limit for param 1, 2, ...
		'lower_bound' : [0.01,  0.001,  1], # lower value limit for param 1, 2, ...
		'fitness': 'abs(17 - float(len(simData["spkt"])) / 40)', # fitness extression. shoud read simData
		'time_sleep': 4, # wait this time before checking again if sim is completed (for each generation)
		'maxiter_wait': 4, # max number of times to check if sim is completed (for each generation)
		'default_fitness': +10 # set fitness value in case simulation time is over
	}
	# Run batch simulations
	b.run()

# Main code
if __name__ == '__main__':
	batchEvol() 
