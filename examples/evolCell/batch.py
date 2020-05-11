import numpy as np
from netpyne import specs
from netpyne.batch import Batch

''' Example of evolutionary algorithm optimization of a cell using NetPyNE

To run use: mpiexec -np [num_cores] nrniv -mpi batch.py
'''

# ---------------------------------------------------------------------------------------------- #
def evolCellITS4():
    # parameters space to explore
    params = specs.ODict()

    params[('tune', 'soma', 'Ra')] = [100.*0.5, 100*1.5] 
    params[('tune', 'soma', 'cm')] = [0.75*0.5, 0.75*1.5]
    params[('tune', 'soma', 'kv', 'gbar')] = [1700.0*0.5, 1700.0*1.5]
    params[('tune', 'soma', 'naz', 'gmax')] = [72000.0*0.5, 72000.0*1.5]
    params[('tune', 'soma', 'pas', 'e')] = [-70*1.5, -70.0*0.5]
    params[('tune', 'soma', 'pas', 'g')] = [3.3333333333333335e-05*0.5, 3.3333333333333335e-05*1.5]

    params[('tune', 'dend', 'Ra')] = [0.02974858749381221*0.5, 0.02974858749381221*1.5] 
    params[('tune', 'dend', 'cm')] = [0.75*0.5, 0.75*1.5]
    params[('tune', 'dend', 'Nca', 'gmax')] = [0.3*0.5, 0.3*1.5]
    params[('tune', 'dend', 'kca', 'gbar')] = [3.0 * 0.5, 3.0 * 1.5]
    params[('tune', 'dend', 'km', 'gbar')] = [0.1*0.5, 0.1*1.5]
    params[('tune', 'dend', 'naz', 'gmax')] = [15.0*0.5, 15.0*1.5]
    params[('tune', 'dend', 'pas', 'e')] = [-70*1.5, -70.0*0.5]
    params[('tune', 'dend', 'pas', 'g')] = [3.3333333333333335e-05*0.5, 3.3333333333333335e-05*1.5]

    params[('tune', 'dend1', 'Ra')] = [0.015915494309189534*0.5, 0.015915494309189534*1.5] 
    params[('tune', 'dend1', 'cm')] = [0.75*0.5, 0.75*1.5]
    params[('tune', 'dend1', 'Nca', 'gmax')] = [0.3*0.5, 0.3*1.5]
    params[('tune', 'dend1', 'kca', 'gbar')] = [3.0*0.5, 3.0*1.5]
    params[('tune', 'dend1', 'km', 'gbar')] = [0.1*0.5, 0.1*1.5]
    params[('tune', 'dend1', 'naz', 'gmax')] = [15.0*0.5, 15.0*1.5]
    params[('tune', 'dend1', 'pas', 'e')] = [-70*1.5, -70.0*0.5]
    params[('tune', 'dend1', 'pas', 'g')] = [3.3333333333333335e-05*0.5, 3.3333333333333335e-05*1.5]


    # current injection params
    amps = list(np.arange(0.0, 0.65, 0.05))  # amplitudes
    times = list(np.arange(1000, 2000 * len(amps), 2000))  # start times
    dur = 500  # ms
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
        'pop_size': 40,
        'num_elites': 1, # keep this number of parents for next generation if they are fitter than children
        'mutation_rate': 0.4,
        'crossover': 0.5,
        'maximize': False, # maximize fitness function?
        'max_generations': 20,
        'time_sleep': 5, # wait this time before checking again if sim is completed (for each generation)
        'maxiter_wait': 20, # max number of times to check if sim is completed (for each generation)
        'defaultFitness': 1000 # set fitness value in case simulation time is over
    }
    # Run batch simulations
    b.run()


# ---------------------------------------------------------------------------------------------- #
def evolCellNGF():
    # parameters space to explore
    params = specs.ODict()

    params[('tune', 'soma', 'Ra')] = [14., 14.]#*0.5, 14.*1.5] 
    # params[('tune', 'soma', 'cm')] = [1.5*0.5, 1.5*1.5] 
    # params[('tune', 'soma', 'ch_CavL', 'gmax')] = [0.056108352*0.5, 0.056108352*1.5] 
    # params[('tune', 'soma', 'ch_CavN', 'gmax')] = [0.00058169587*0.5, 0.00058169587*1.5] 
    # params[('tune', 'soma', 'ch_KCaS', 'gmax')] = [0.006 * 0.5, 0.006 * 1.5]
    # params[('tune', 'soma', 'ch_Kdrfastngf', 'gmax')] = [0.09*0.5, 0.09*1.5] 
    # params[('tune', 'soma', 'ch_KvAngf', 'gmax')] = [0.052*0.5, 0.052*1.5] 
    # params[('tune', 'soma', 'ch_KvAngf', 'gml')] = [1.0*0.5, 1.0*1.5] 
    # params[('tune', 'soma', 'ch_KvAngf', 'gmn')] = [0.6*0.5, 0.6*1.5] 
    # params[('tune', 'soma', 'ch_KvCaB', 'gmax')] = [1.0235317e-06*0.5, 1.0235317e-06*1.5] 
    # params[('tune', 'soma', 'ch_Navngf', 'gmax')] = [0.1*0.5, 0.1*1.5] 
    # params[('tune', 'soma', 'hd', 'ehd')] = [-30*1.5, -30*0.5] 
    # params[('tune', 'soma', 'hd', 'elk')] = [-70*1.5, -70*0.5] 
    # params[('tune', 'soma', 'hd', 'gbar')] = [1e-05*0.5, 1e-05*1.5] 
    # params[('tune', 'soma', 'hd', 'vhalfl')] = [-90*1.5, -90*0.5] 
    # # params[('tune', 'soma', 'iconc_Ca', 'caiinf')] = [5e-06*0.5, 5e-06*1.5]   # convergence issues
    # # params[('tune', 'soma', 'iconc_Ca', 'catau')] = [-10*1.5, -10*0.5] 
    # params[('tune', 'soma', 'pas', 'e')] = [-85*1.5, -85*0.5]
    # params[('tune', 'soma', 'pas', 'g')] = [5e-7*0.5, 5e-7*1.5]  

    # params[('tune', 'dend', 'Ra')] = [14*0.5, 14*1.5] 
    # params[('tune', 'dend', 'cm')] = [1.5*0.5, 1.5*1.5] 
    # params[('tune', 'dend', 'ch_Kdrfastngf', 'gmax')] = [0.03*0.5, 0.03*1.5] 
    # params[('tune', 'dend', 'ch_Navngf', 'gmax')] = [3.7860265*0.5, 3.7860265*1.5] 
    # params[('tune', 'dend', 'pas', 'e')] = [-67*1.5, -67*0.5] 
    # params[('tune', 'dend', 'pas', 'g')] = [0.0003*0.5, 0.0003*1.5] 


    # current injection params
    interval = 10000
    dur = 500  # ms
    durSteady = 200  # ms
    amps = list(np.arange(0.04+0.075, 4.0, 0.05))# 0.121+0.075, 0.01))  # amplitudes
    times = list(np.arange(1000, (dur+interval) * len(amps), dur+interval))  # start times
    targetRatesOnset = [43., 52., 68., 80., 96., 110., 119., 131., 139.]
    targetRatesSteady = [22., 24., 27., 30., 33., 35., 37., 39., 41.]
    #targetRates = [(o + s) / 2 for o, s in zip(targetRatesOnset, targetRatesSteady)]
    
    # initial cfg set up
    initCfg = {} # specs.ODict()
    initCfg['duration'] = (dur+interval) * len(amps)
    initCfg[('hParams', 'celsius')] = 37

    initCfg['savePickle'] = True
    initCfg['saveJson'] = False
    initCfg['saveDataInclude'] = ['simConfig', 'netParams', 'net', 'simData']

    initCfg[('IClamp1', 'pop')] = 'NGF'
    initCfg[('IClamp1', 'amp')] = amps
    initCfg[('IClamp1', 'start')] = times
    initCfg[('IClamp1', 'dur')] = dur

    initCfg[('analysis', 'plotTraces', 'timeRange')] = [0, initCfg['duration']] 
    initCfg[('analysis', 'plotfI', 'amps')] = amps
    initCfg[('analysis', 'plotfI', 'times')] = times
    initCfg[('analysis', 'plotfI', 'calculateOnset')] = True
    initCfg[('analysis', 'plotfI', 'dur')] = dur
    initCfg[('analysis', 'plotfI', 'durSteady')] = durSteady
    initCfg[('analysis', 'plotfI', 'targetRates')] = [] #
    initCfg[('analysis', 'plotfI', 'targetRatesOnset')] = [] #targetRatesOnset
    initCfg[('analysis', 'plotfI', 'targetRatesSteady')] = [] #targetRatesSteady
    
    for k, v in params.items():
        initCfg[k] = v[0]  # initialize params in cfg so they can be modified    

    # fitness function
    fitnessFuncArgs = {}
    fitnessFuncArgs['targetRatesOnset'] = targetRatesOnset
    fitnessFuncArgs['targetRatesSteady'] = targetRatesSteady
    
    def fitnessFunc(simData, **kwargs):
        targetRatesOnset = kwargs['targetRatesOnset']
        targetRatesSteady = kwargs['targetRatesSteady']
            
        diffRatesOnset = [abs(x-t) for x,t in zip(simData['fI_onset'], targetRatesOnset)]
        diffRatesSteady = [abs(x-t) for x,t in zip(simData['fI_steady'], targetRatesSteady)]

        fitness = np.mean(diffRatesOnset+diffRatesSteady)
        
        print(' Candidate rates: ', simData['fI_onset']+simData['fI_steady'])
        print(' Target rates:    ', targetRatesOnset+targetRatesSteady)
        print(' Difference:      ', diffRatesOnset+diffRatesSteady)

        return fitness
        

    # create Batch object with paramaters to modify, and specifying files to use
    b = Batch(params=params, initCfg=initCfg)
    
    # Set output folder, grid method (all param combinations), and run configuration
    b.batchLabel = 'NGF_evol'
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
        'maxiter_wait': 20, # max number of times to check if sim is completed (for each generation)
        'defaultFitness': 1000 # set fitness value in case simulation time is over
    }
    # Run batch simulations
    b.run()


# ---------------------------------------------------------------------------------------------- #
# Main code
if __name__ == '__main__':
    evolCellNGF() 

