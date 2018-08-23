from netpyne import specs, batch

def batchEvol():
	# parameters space to explore
	
	## simple net
	params = specs.ODict()
	params['prob'] = [0.01, 0.5]
	params['weight'] = [0.001, 0.1]
	params['delay'] = [1, 20]

	## complex net
	params = specs.ODict()
	params['probEall'] = [0.05, 0.2] # 0.1
	params['weightEall'] = [0.0025, 0.0075] #5.0
	params['probIE'] = [0.2, 0.6] #0.4
	params['weightIE'] = [0.0005, 0.002]
	params['probLengthConst'] = [100,200]
	params['stimWeight'] = [0.05, 0.2]

	# fitness function
	fitnessFuncArgs = {}
	
	## simple net
	pops = {} 
	pops['S'] = {'target': 5, 'width': 2, 'min': 2}
	pops['M'] = {'target': 15, 'width': 2, 'min': 0.2}
	
	## complex net
	pops = {} 
	pops['E2'] = {'target': 5, 'width': 2, 'min': 1}
	pops['I2'] = {'target': 10, 'width': 5, 'min': 2}
	pops['E4'] = {'target': 30, 'width': 10, 'min': 1}
	pops['I4'] = {'target': 10, 'width': 3, 'min': 2}
	pops['E5'] = {'target': 40, 'width': 4, 'min': 1}
	pops['I5'] = {'target': 25, 'width': 5, 'min': 2}

	
	fitnessFuncArgs['pops'] = pops
	fitnessFuncArgs['maxFitness'] = 1000

	def fitnessFunc(simData, **kwargs):
		import numpy as np
		pops = kwargs['pops']
		maxFitness = kwargs['maxFitness']
		fitness = np.mean([min(np.exp(abs(v['target'] - simData['popRates'][k])/v['width']), maxFitness) 
				if simData["popRates"][k]>v['min'] else maxFitness for k,v in pops.iteritems()])
		print 'fitness = %f'%(fitness)
		return fitness
		
	# create Batch object with paramaters to modify, and specifying files to use
	b = batch.Batch(params=params)
	
	# Set output folder, grid method (all param combinations), and run configuration
	b.batchLabel = 'complex_evol'
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
		#'custom': 'export LD_LIBRARY_PATH="$HOME/.openmpi/lib"' # only for conda users
	}
	b.evolCfg = {
		'fitnessFunc': fitnessFunc, # fitness expression (should read simData)
		'fitnessFuncArgs': fitnessFuncArgs,
		'pop_size': 10,
		'num_elites': 1, # keep this number of parents for next generation if they are fitter than children
		'maximize': False, # maximize fitness function?
		'mutation_rate': 0.1, 
		'max_generations': 20,
		'mutation_strength': 0.65, # <1 mutation moves closer to candidate. >1 mutation moves away from candidate 
		'time_sleep': 5, # wait this time before checking again if sim is completed (for each generation)
		'maxiter_wait': 40, # max number of times to check if sim is completed (for each generation)
		'default_fitness': 1000 # set fitness value in case simulation time is over
	}
	# Run batch simulations
	b.run()

# Main code
if __name__ == '__main__':
	batchEvol() 
