from netpyne import specs
from netpyne.batch import Batch
from scipy.stats import kurtosis

''' Example of SBI optimization of a network using NetPyNE
'simple' network, 3 parameters are optimized to match target firing rates in 2 populations

To run use: mpiexec -np [num_cores] nrniv -mpi src/batch.py
'''

def batchSBI():
    # parameters space to explore

    ## simple net
    params = specs.ODict()
    params['prob'] = [0.01, 0.5]
    params['weight'] = [0.001, 0.1]
    params['delay'] = [1, 20]

    pops = {} 
    pops['S'] = {'target': 5, 'width': 2, 'min': 2} #If 'Observed' parameter is given include those given PopRates in 'target'
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


    # SummaryStat function
    SummaryStatisticArg = {}
    SummaryStatisticArg['pops'] = pops
    SummaryStatisticArg['length'] = len(pops) + 7 #change '7' according to the length of your statistics
    SummaryStatisticArg['observed'] = [None] # If 'Observed' parameter pass in those values else None

    # No metrics that are compared to 'Observed Parameter data' can be used, metrics have to be self-sufficient and non changing in terms of vector size 
    # Change this according to problem but output must be a list
    def SummaryStats(simData, **kwargs):
        import numpy as np
        from scipy.stats import kurtosis

        spiketimes = simData['spkt']
        pops = kwargs['pops']

        # retrieves poprates 
        popRates = [None for i in pops.items()]
        popRates = [simData["popRates"][k] for k in pops.keys()]  
           
        #Need static vector length per analysis or else will crash
        avg_popRates = np.mean(popRates)
        number_spikes = len(spiketimes)
        avg_spiketimes = np.average(spiketimes)
        sd_spiketimes = np.std(spiketimes)
        kurt_spiketimes = kurtosis(spiketimes)

        #Assuming more than one spike
        min_spiketime = min(spiketimes)
        max_spiketime = max(spiketimes)

        sum_stats = popRates + [avg_popRates, number_spikes, avg_spiketimes, sd_spiketimes, kurt_spiketimes, min_spiketime, max_spiketime]
    
        return sum_stats


    # create Batch object with paramaters to modify, and specifying files to use
    b = Batch(cfgFile='src/cfg.py', netParamsFile='src/netParams', params=params)

    # Set output folder, grid method (all param combinations), and run configuration
    b.batchLabel = 'simple'
    b.saveFolder = './'+b.batchLabel
    b.method = 'sbi'
    b.runCfg = {
        'type': 'mpi_direct',#'hpc_slurm',
        'script': 'src/init.py',
        # options required only for mpi_direct or hpc
        'mpiCommand': 'mpiexec',
        'nodes': 2,
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
        'summaryStats': SummaryStats,
        'summaryStatisticArg': SummaryStatisticArg,
        'summaryStatisticLength': SummaryStatisticArg['length'],
        'summaryStatisticObserved': SummaryStatisticArg['observed'],
        'maxFitness': fitnessFuncArgs['maxFitness'],
        'maxiters':     500,    #    Maximum number of iterations (1 iteration = 1 function evaluation)
        'maxtime':      3600,    #    Maximum time allowed, in seconds
        'maxiter_wait': 3,
        'time_sleep': 5,
        'sbi_method': 'SNPE', # SNPE, SNLE, or SNRE
        'inference_type': 'single', # single or multi 
        'rounds': 2, # If multi, choose a round amount else unused
    }

    # Run batch simulations
    b.run()

# Main code
if __name__ == '__main__':
    batchSBI()  # 'simple' or 'complex'