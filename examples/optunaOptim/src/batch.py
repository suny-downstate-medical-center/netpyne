from netpyne import specs
from netpyne.batch import Batch

''' Example of adaptive stochastic descent algorithm optimization of a network using NetPyNE
'simple' network, 3 parameters are optimized to match target firing rates in 2 populations

To run use: mpiexec -np [num_cores] nrniv -mpi batchRun.py
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
        'popsize': 1  # unused - run with mpi
    }

    # Run batch simulations
    b.run()

# Main code
if __name__ == '__main__':
    batchOptuna()  # 'simple' or 'complex'
