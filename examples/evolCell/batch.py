import numpy as np
from netpyne import specs
from netpyne.batch import Batch

''' Example of evolutionary algorithm optimization of a cell using NetPyNE

To run use: mpiexec -np [num_cores] nrniv -mpi batch.py
'''

def evolCell():
    # parameters space to explore
    params = specs.ODict()
    params[('tune', 'soma', 'vinit')] = [-75, -75] #[-90, -60]
    params[('tune', 'dend', 'cadad', 'kd')] = [0.0, 0.0]
    params[('tune', 'dend1', 'Ra')] = [0.015915494309189534, 0.015915494309189534]

        # "soma": {
        #     "geom": {
        #         "Ra": 100.0,
        #         "cm": 0.75,
        #     "mechs": {
        #         "kv": {
        #             "gbar": 1700.0
        #         },
        #         "naz": {
        #             "gmax": 72000.0
        #         },
        #         "pas": {
        #             "e": -70.0,
        #             "g": 3.3333333333333335e-05
        # "dend": {
        #     "geom": {
        #         "Ra": 0.02974858749381221,
        #         "cm": 0.75,
        #     "mechs": {
        #         "Nca": {
        #             "gmax": 0.3
        #         },
        #         "kca": {
        #             "gbar": 3.0
        #         },
        #         "km": {
        #             "gbar": 0.1
        #         },
        #         "naz": {
        #             "gmax": 15.0
        #         },
        #         "pas": {
        #             "e": -70.0,
        #             "g": 3.3333333333333335e-05
        #         }
        # "dend1": {
        #     "geom": {
        #         "Ra": 0.015915494309189534,
        #         "cm": 0.75,
        #     "mechs": {
        #         "Nca": {
        #             "gmax": 0.3
        #         },
        #         "kca": {
        #             "gbar": 3.0
        #         },
        #         "km": {
        #             "gbar": 0.1
        #         },
        #         "naz": {
        #             "gmax": 15.0
        #         },
        #         "pas": {
        #             "e": -70.0,
        #             "g": 3.3333333333333335e-05
        #         }
        #     },

        #         }


    # current injection params
    amps = list(np.arange(0.0, 0.65, 0.05))  # amplitudes
    times = list(np.arange(1000, 2000 * len(amps), 2000))  # start times
    dur = 1000  # ms
    targetRates = [0., 0., 19., 29., 37., 45., 51., 57., 63., 68., 73., 77., 81.]
 
    # initial cfg set up
    initCfg = {} # specs.ODict()
    initCfg['duration'] = 2000 * len(amps)
    initCfg[('hParams', 'celsius')] = 37

    initCfg['savePickle'] = True
    initCfg['saveJson'] = False
    initCfg['saveDataInclude'] = ['simConfig', 'netParams', 'net', 'simData']

    initCfg[('IClamp1', 'pop')] = 'ITS4'
    initCfg[('IClamp1', 'amp')] = amps
    initCfg[('IClamp1', 'start')] = times
    initCfg[('IClamp1', 'dur')] = 1000

    initCfg[('analysis', 'plotfI', 'amps')] = amps
    initCfg[('analysis', 'plotfI', 'times')] = times
    initCfg[('analysis', 'plotfI', 'dur')] = dur
    initCfg[('analysis', 'plotfI', 'targetRates')] = targetRates
    
    for k, v in params.items():
        initCfg[k] = v[0]  # initialize params in cfg so they can be modified    

    # fitness function
    fitnessFuncArgs = {}
    fitnessFuncArgs['targetRates'] = targetRates
    
    def fitnessFunc(simData, **kwargs):
        targetRates = kwargs['targetRates']
            
        diffRates = [abs(x-t) for x,t in zip(simData['fI'], targetRates)]
        fitness = np.mean(diffRates)
        
        print(' Candidate rates: ', simData['fI'])
        print(' Target rates:    ', targetRates)
        print(' Difference:      ', diffRates)

        return fitness
        

    # create Batch object with paramaters to modify, and specifying files to use
    b = Batch(params=params, initCfg=initCfg)
    
    # Set output folder, grid method (all param combinations), and run configuration
    b.batchLabel = 'ITS4_evol'
    b.saveFolder = 'data/'+b.batchLabel
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
        'pop_size': 1,
        'num_elites': 1, # keep this number of parents for next generation if they are fitter than children
        'mutation_rate': 0.4,
        'crossover': 0.5,
        'maximize': False, # maximize fitness function?
        'max_generations': 1,
        'time_sleep': 5, # wait this time before checking again if sim is completed (for each generation)
        'maxiter_wait': 12, # max number of times to check if sim is completed (for each generation)
        'defaultFitness': 1000 # set fitness value in case simulation time is over
    }
    # Run batch simulations
    b.run()


# Main code
if __name__ == '__main__':
    evolCell() 

