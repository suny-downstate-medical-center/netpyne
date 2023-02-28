from netpyne import specs
from netpyne.batch import Batch

'''
Example of using Optuna - a hyperparameter optimization framework. The example uses NetPyNE 'simple' network, 3 parameters are optimized to match target firing rates in 2 populations

Optuna doesn’t use mpi to run in parallel. Instead you just need to run multiple instances, which will communicate with each other via an SQL database file.
This means each instance works asynchronously from the rest and just checks the database file to know what is the latest set of solutions, and decides the next set of parameters to explore.
To run optuna instances you can use the ./batch_optuna.sh N, where N is the number of instances you want to run. Each instance will run in the background using screen,
and will submit Slurm jobs and coordinate with the rest via the shared database file.

This has advantages as you can start by submitting a single instance:  ./batch_optuna.sh 1 ; then check if it’s working correctly, and if so submit the rest, eg. ./batch_optuna.sh 49.

To check if it’s working correctly you can look at the screenlog.0 file that will be generated in the folder where you submit from, e.g.

cat screenlog.0
grep Best screenlog.0  	# to see all the best solutions so far
grep Best screenlog.0  | tail 	# to see the last best solutions


Requires installation of the following packages:
optuna, psutil, scikit-learn
'''
def batchOptuna():
    # parameters space to explore

    ## simple net
    params = specs.ODict()
    params['prob'] = [0.01, 0.5]  # can add 3rd value for starting value (0)
    params['weight'] = [0.001, 0.1]
    params['delay'] = [1, 20]

    pops = {}
    pops['S'] = {'target': 5, 'width': 2, 'min': 2}
    pops['M'] = {'target': 15, 'width': 2, 'min': 0.2}

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
    b.method = 'optuna'
    b.runCfg = {
        'type': 'mpi_direct',#'hpc_slurm',
        'script': 'src/init.py',
        # options required only for mpi_direct or hpc
        'mpiCommand': 'mpiexec',
        'nodes': 1,
        'coresPerNode': 2,
        # 'allocation': 'default',
        # 'email': 'salvadordura@gmail.com',
        # 'reservation': None,
        # 'folder': '/home/salvadord/evol'
        #'custom': 'export LD_LIBRARY_PATH="$HOME/.openmpi/lib"' # only for conda users
    }
    b.optimCfg = {
        'fitnessFunc': fitnessFunc, # fitness expression (should read simData)
        'fitnessFuncArgs': fitnessFuncArgs,
        'maxFitness': fitnessFuncArgs['maxFitness'],
        'maxiters':     20,    #    Maximum number of iterations (1 iteration = 1 function evaluation)
        'maxtime':      3600,    #    Maximum time allowed, in seconds
        'maxiter_wait': 10,
        'time_sleep': 5,
    }

    # Run batch simulations
    b.run()

# Main code
if __name__ == '__main__':
    batchOptuna()  # 'simple' or 'complex'
