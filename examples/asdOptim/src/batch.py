from netpyne import specs
from netpyne.batch import Batch

''' Example of adaptive stochastic descent algorithm optimization of a network using NetPyNE
'simple' network, 3 parameters are optimized to match target firing rates in 2 populations

To run use: mpiexec -np [num_cores] nrniv -mpi batchRun.py
'''

def batchASD():
    # parameters space to explore

    ## simple net
    params = specs.ODict()
    params['prob'] = [0.01, 0.5, [0.4, 0.3]]  # can add 3rd value for starting value (0)
    params['weight'] = [0.001, 0.1, [0.1, 0.2]]
    params['delay'] = [1, 20, [5, 3]]

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
    b.method = 'asd'
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
        'stepsize':     0.1,     #   Initial step size as a fraction of each parameter
        'sinc':         2,       #   Step size learning rate (increase)
        'sdec':         2,       #   Step size learning rate (decrease)
        'pinc':         2,       #   Parameter selection learning rate (increase)
        'pdec':         2,       #   Parameter selection learning rate (decrease)
        #'pinitial':     None,    #    Set initial parameter selection probabilities
        #'sinitial':     None,    #    Set initial step sizes; if empty, calculated from stepsize instead
        'maxiters':     2,    #    Maximum number of iterations (1 iteration = 1 function evaluation)
        'maxtime':      3600,    #    Maximum time allowed, in seconds
        'abstol':       1e-6,    #    Minimum absolute change in objective function
        'reltol':       1e-3,    #    Minimum relative change in objective function
        #'stalliters':   10*len(params)*len(params),  #    Number of iterations over which to calculate TolFun (n = number of parameters)
        #'stoppingfunc': None,    #    External method that can be used to stop the calculation from the outside.
        #'randseed':     None,    #    The random seed to use
        'verbose':      2,       #    How much information to print during the run
        #'label':        None    #    A label to use to annotate the output
        'maxiter_wait': 10,
        'time_sleep': 5,
        'popsize': 1
    }

    # Run batch simulations
    b.run()

# Main code
if __name__ == '__main__':
    batchASD()  # 'simple' or 'complex'
