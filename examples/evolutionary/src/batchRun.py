from netpyne import specs
from netpyne.batch import Batch

''' Example of evolutionary algorithm optimization of a network using NetPyNE
2 examples are provided: 'simple' and 'complex'
In 'simple', 3 parameters are optimized to match target firing rates in 2 populations
In 'complex', 6 parameters are optimized to match target firing rates in 6 populations

To run use: mpiexec -np [num_cores] nrniv -mpi batchRun.py
'''

def batchEvol(networkType):
	# parameters space to explore

	if networkType == 'simple':
		## simple net
		params = specs.ODict()
		params['prob'] = [0.01, 0.5]
		params['weight'] = [0.001, 0.1]
		params['delay'] = [1, 20]

		pops = {}
		pops['S'] = {'target': 5, 'width': 2, 'min': 2}
		pops['M'] = {'target': 15, 'width': 2, 'min': 0.2}

	elif networkType == 'complex':
		# complex net
		params = specs.ODict()
		params['probEall'] = [0.05, 0.2] # 0.1
		params['weightEall'] = [0.0025, 0.0075] #5.0
		params['probIE'] = [0.2, 0.6] #0.4
		params['weightIE'] = [0.0005, 0.002]
		params['probLengthConst'] = [100,200]
		params['stimWeight'] = [0.05, 0.2]

		pops = {}
		pops['E2'] = {'target': 5, 'width': 2, 'min': 1}
		pops['I2'] = {'target': 10, 'width': 5, 'min': 2}
		pops['E4'] = {'target': 30, 'width': 10, 'min': 1}
		pops['I4'] = {'target': 10, 'width': 3, 'min': 2}
		pops['E5'] = {'target': 40, 'width': 4, 'min': 1}
		pops['I5'] = {'target': 25, 'width': 5, 'min': 2}

	# fitness function
	fitnessFuncArgs = {}
	fitnessFuncArgs['pops'] = pops
	fitnessFuncArgs['maxFitness'] = 1000

	def fitnessFunc(simData, **kwargs):
		import numpy as np
		pops = kwargs['pops']
		maxFitness = kwargs['maxFitness']
		popFitness = [None for i in pops.items()]
		popFitness = [min(np.exp(  abs(v['target'] - simData['popRates'][k])  /  v['width']), maxFitness)
				if simData["popRates"][k]>v['min'] else maxFitness for k,v in pops.items()]
		fitness = np.mean(popFitness)
		popInfo = '; '.join(['%s rate=%.1f fit=%1.f'%(p,r,f) for p,r,f in zip(list(simData['popRates'].keys()), list(simData['popRates'].values()), popFitness)])
		print('  '+popInfo)
		return fitness

	# create Batch object with paramaters to modify, and specifying files to use
	b = Batch(cfgFile='src/cfg.py', netParamsFile='src/netParams.py', params=params)

	# Set output folder, grid method (all param combinations), and run configuration
	b.batchLabel = 'simple'
	b.saveFolder = './'+b.batchLabel
	b.method = 'evol'
	b.runCfg = {
		'type': 'mpi_bulletin',#'hpc_slurm',
		'script': 'src/init.py',
		# options required only for hpc
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
		'evolAlgorithm': 'custom',
		'fitnessFunc': fitnessFunc, # fitness expression (should read simData)
		'fitnessFuncArgs': fitnessFuncArgs,
		'pop_size': 6,
		'num_elites': 1, # keep this number of parents for next generation if they are fitter than children
		'mutation_rate': 0.4,
		'crossover': 0.5,
		'maximize': False, # maximize fitness function?
		'max_generations': 4,
		'time_sleep': 5, # wait this time before checking again if sim is completed (for each generation)
		'maxiter_wait': 40, # max number of times to check if sim is completed (for each generation)
		'defaultFitness': 1000 # set fitness value in case simulation time is over
	}
	# Run batch simulations
	b.run()

# Main code
if __name__ == '__main__':
	batchEvol('simple')  # 'simple' or 'complex'
