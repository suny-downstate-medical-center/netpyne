from netpyne import specs
from netpyne.batch import Batch

''' Example of evolutionary algorithm optimization of a cell using NetPyNE

To run use: mpiexec -np [num_cores] nrniv -mpi batch.py
'''

def batchEvol():
    # parameters space to explore
    
    params = specs.ODict()
    params['prob'] = [0.01, 0.5]
    params['weight'] = [0.001, 0.1]
    params['delay'] = [1, 20]

    # fitness function
    from cfg import cfg
    fitnessFuncArgs = {}
    fitnessFuncArgs['times'] = cfg.IClamp1['start']
    fitnessFuncArgs['duration'] = cfg.IClamp1['duration']
    fitnessFuncArgs['targetRates'] = [0, 0, 19, 29, 37, 45, 51, 57, 63, 68, 73, 77, 81]
    
    
    def fitnessFunc(simData, **kwargs):
        import numpy as np
        from netpyne import sim

        amps = kwargs['amps']
        times = kwargs['times']
        duration = kwargs['duration']
        targetRates = kwargs['targetRates']
        
        rates = []
        for t in times:
            rates.append(sim.analysis.popAvgRates(trange=[t, t+duration]))  
            
        diffRates = [abs(x-t) for x,t in zip(rates, targetRates)]
        fitness = np.mean(diffRates)
        
        print(' Candidate rates: ' + rates)
        print(' Target rates:    ' + targetRates)
        print(' Difference:      ' + diffRates)
        print(' FITNESS: ' + fitness)

        return fitness
        
    # create Batch object with paramaters to modify, and specifying files to use
    b = Batch(params=params)
    
    # Set output folder, grid method (all param combinations), and run configuration
    b.batchLabel = 'simple'
    b.saveFolder = './'+b.batchLabel
    b.method = 'evol'
    b.runCfg = {
        'type': 'mpi_bulletin',#'hpc_slurm', 
        'script': 'init.py',
        # # options required only for hpc
        # 'mpiCommand': 'mpirun',  
        # 'nodes': 1,
        # 'coresPerNode': 2,
        # 'allocation': 'default',
        # 'email': 'salvadordura@gmail.com',
        # 'reservation': None,
        # 'folder': '/home/salvadord/evol'
        # #'custom': 'export LD_LIBRARY_PATH="$HOME/.openmpi/lib"' # only for conda users
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
    batchEvol()  # 'simple' or 'complex' 


