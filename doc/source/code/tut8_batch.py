from netpyne import specs
from netpyne.batch import Batch 

def batchTauWeight():
	# Create variable of type ordered dictionary (NetPyNE's customized version) 
	params = specs.ODict()   

	# Parameters and values to explore (corresponds to variable in simConfig) 
	params['synMechTau2'] = [3.0, 5.0, 7.0]   
	params['connWeight'] = [0.005, 0.01, 0.15]

	# create Batch object with paramaters to modify, and model files to use
	b = Batch(params=params,
              cfgFile='tut8_cfg.py', 
              netParamsFile='tut8_netParams.py')
	
	# Set output folder, optimization method, and run configuration
	b.batchLabel = 'tauWeight'
	b.saveFolder = 'tut8_data'
	b.method = 'grid'
	b.runCfg = {'type': 'mpi_bulletin', 
				'script': 'tut8_init.py', 
				'skip': True}

	# Run batch simulations
	b.run()

# Main code
if __name__ == '__main__':
	batchTauWeight() 



