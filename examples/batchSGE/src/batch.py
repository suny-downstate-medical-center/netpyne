from netpyne import specs
from netpyne.batch import Batch

def batchTauWeight():
        # Create variable of type ordered dictionary (NetPyNE's customized version)
        params = specs.ODict()

        # fill in with parameters to explore and range of values (key has to coincide with a variable in simConfig)
        params['synMechTau2'] = [3.0, 5.0, 7.0]
        params['connWeight'] = [0.005, 0.01, 0.15]

        # create Batch object with parameters to modify, and specifying files to use
        b = Batch(params=params, cfgFile='src/cfg.py', netParamsFile='src/params.py',)

        # Set output folder, grid method (all param combinations), and run configuration
        b.batchLabel = 'tauWeight'
        b.saveFolder = 'tut8_data'
        b.method = 'grid'
        b.runCfg = {'type': 'hpc_sge',
                    'jobName': 'my_batch',
                    'cores': 4,
                    'script': 'src/init.py',
                    'skip': True}

        # Run batch simulations
        b.run()

# Main code
if __name__ == '__main__':
        batchTauWeight()
