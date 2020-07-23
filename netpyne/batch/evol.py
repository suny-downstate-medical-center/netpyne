"""
Module for/to <short description of `netpyne.batch.evol`>

"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from builtins import zip

from builtins import range
from builtins import open
from builtins import str
from future import standard_library
standard_library.install_aliases()

# required to make json saving work in Python 2/3
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

import imp
import json
import logging
import datetime
import os
import glob
from copy import copy
from random import Random
from time import sleep, time
from itertools import product
from subprocess import Popen, PIPE
import importlib, types

from neuron import h
from netpyne import specs
from .utils import createFolder
from .utils import bashTemplate

pc = h.ParallelContext() # use bulletin board master/slave

# -------------------------------------------------------------------------------
# Evolutionary optimization
# -------------------------------------------------------------------------------

# func needs to be outside of class
def runEvolJob(script, cfgSavePath, netParamsSavePath, simDataPath):
    """
    Function for/to <short description of `netpyne.batch.evol.runEvolJob`>

    Parameters
    ----------
    script : <type>
        <Short description of script>
        **Default:** *required*

    cfgSavePath : <type>
        <Short description of cfgSavePath>
        **Default:** *required*

    netParamsSavePath : <type>
        <Short description of netParamsSavePath>
        **Default:** *required*

    simDataPath : <type>
        <Short description of simDataPath>
        **Default:** *required*


    """


    import os
    print('\nJob in rank id: ',pc.id())
    command = 'nrniv %s simConfig=%s netParams=%s' % (script, cfgSavePath, netParamsSavePath)
    print(command)

    with open(simDataPath+'.run', 'w') as outf, open(simDataPath+'.err', 'w') as errf:
        pid = Popen(command.split(' '), stdout=outf, stderr=errf, preexec_fn=os.setsid).pid
    
    with open('./pids.pid', 'a') as file:
        file.write(str(pid) + ' ')


def evolOptim(self, pc):
    """
    Function for/to <short description of `netpyne.batch.evol.evolOptim`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*

    pc : <type>
        <Short description of pc>
        **Default:** *required*


    """


    import sys
    import inspyred.ec as EC


    # -------------------------------------------------------------------------------
    # Evolutionary optimization: Parallel evaluation
    # -------------------------------------------------------------------------------
    def evaluator(candidates, args):
        import os
        import signal
        global ngen
        ngen += 1
        total_jobs = 0

        # options slurm, mpi
        type = args.get('type', 'mpi_direct')
        
        # paths to required scripts
        script = args.get('script', 'init.py')
        netParamsSavePath =  args.get('netParamsSavePath')
        genFolderPath = self.saveFolder + '/gen_' + str(ngen)
        
        # mpi command setup
        nodes = args.get('nodes', 1)
        paramLabels = args.get('paramLabels', [])
        coresPerNode = args.get('coresPerNode', 1)
        mpiCommand = args.get('mpiCommand', 'ibrun')
        numproc = nodes*coresPerNode
        
        # slurm setup
        custom = args.get('custom', '')
        folder = args.get('folder', '.')
        email = args.get('email', 'a@b.c')
        walltime = args.get('walltime', '00:01:00')
        reservation = args.get('reservation', None)
        allocation = args.get('allocation', 'csd403') # NSG account

        # fitness function
        fitnessFunc = args.get('fitnessFunc')
        fitnessFuncArgs = args.get('fitnessFuncArgs')
        defaultFitness = args.get('defaultFitness')
        
        # read params or set defaults
        sleepInterval = args.get('sleepInterval', 0.2)
        
        # create folder if it does not exist
        createFolder(genFolderPath)
        
        # remember pids and jobids in a list
        pids = []
        jobids = {}
        
        # create a job for each candidate
        for candidate_index, candidate in enumerate(candidates):
            # required for slurm
            sleep(sleepInterval)
            
            # name and path
            jobName = "gen_" + str(ngen) + "_cand_" + str(candidate_index)
            jobPath = genFolderPath + '/' + jobName

            # set initial cfg initCfg
            if len(self.initCfg) > 0:
                for paramLabel, paramVal in self.initCfg.items():
                    self.setCfgNestedParam(paramLabel, paramVal)
            
            # modify cfg instance with candidate values
            for label, value in zip(paramLabels, candidate):
                print('set %s=%s' % (label, value))
                self.setCfgNestedParam(label, value)
            
            #self.setCfgNestedParam("filename", jobPath)
            self.cfg.simLabel = jobName
            self.cfg.saveFolder = genFolderPath

            # save cfg instance to file
            cfgSavePath = jobPath + '_cfg.json' 
            self.cfg.save(cfgSavePath)
            
            
            if type=='mpi_bulletin':
                # ----------------------------------------------------------------------
                # MPI master-slaves
                # ----------------------------------------------------------------------
                pc.submit(runEvolJob, script, cfgSavePath, netParamsSavePath, jobPath)
                print('-'*80)

            else:
                # ----------------------------------------------------------------------
                # MPI job commnand
                # ----------------------------------------------------------------------
                command = '%s -np %d nrniv -python -mpi %s simConfig=%s netParams=%s ' % (mpiCommand, numproc, script, cfgSavePath, netParamsSavePath)
                
                # ----------------------------------------------------------------------
                # run on local machine with <nodes*coresPerNode> cores
                # ----------------------------------------------------------------------
                if type=='mpi_direct':
                    executer = '/bin/bash'
                    jobString = bashTemplate('mpi_direct') %(custom, folder, command)
                
                # ----------------------------------------------------------------------
                # run on HPC through slurm
                # ----------------------------------------------------------------------
                elif type=='hpc_slurm':
                    executer = 'sbatch'
                    res = '#SBATCH --res=%s' % (reservation) if reservation else ''
                    jobString = bashTemplate('hpc_slurm') % (jobName, allocation, walltime, nodes, coresPerNode, jobPath, jobPath, email, res, custom, folder, command)
                
                # ----------------------------------------------------------------------
                # run on HPC through PBS
                # ----------------------------------------------------------------------
                elif type=='hpc_torque':
                    executer = 'qsub'
                    queueName = args.get('queueName', 'default')
                    nodesppn = 'nodes=%d:ppn=%d' % (nodes, coresPerNode)
                    jobString = bashTemplate('hpc_torque') % (jobName, walltime, queueName, nodesppn, jobPath, jobPath, custom, command)
                
                # ----------------------------------------------------------------------
                # save job and run
                # ----------------------------------------------------------------------
                print('Submitting job ', jobName)
                print(jobString)
                print('-'*80)
                # save file 
                batchfile = '%s.sbatch' % (jobPath)
                with open(batchfile, 'w') as text_file:
                    text_file.write("%s" % jobString)
                
                #with open(jobPath+'.run', 'a+') as outf, open(jobPath+'.err', 'w') as errf:
                with open(jobPath+'.jobid', 'w') as outf, open(jobPath+'.err', 'w') as errf:
                    pids.append(Popen([executer, batchfile], stdout=outf,  stderr=errf, preexec_fn=os.setsid).pid)
                #proc = Popen(command.split([executer, batchfile]), stdout=PIPE, stderr=PIPE)
                sleep(0.1)
                #read = proc.stdout.read()                            
                with open(jobPath+'.jobid', 'r') as outf:
                    read=outf.readline()
                print(read)
                if len(read) > 0:
                    jobid = int(read.split()[-1])
                    jobids[candidate_index] = jobid
                print('jobids', jobids)
            total_jobs += 1
            sleep(0.1)


        # ----------------------------------------------------------------------
        # gather data and compute fitness
        # ----------------------------------------------------------------------
        if type == 'mpi_bulletin':
            # wait for pc bulletin board jobs to finish
            try:
                while pc.working():
                    sleep(1)
                #pc.done()
            except:
                pass
                
        num_iters = 0
        jobs_completed = 0
        fitness = [None for cand in candidates]
        # print outfilestem
        print("Waiting for jobs from generation %d/%d ..." %(ngen, args.get('max_generations')))
        # print "PID's: %r" %(pids)
        # start fitness calculation
        while jobs_completed < total_jobs:
            unfinished = [i for i, x in enumerate(fitness) if x is None ]
            for candidate_index in unfinished:
                try: # load simData and evaluate fitness
                    jobNamePath = genFolderPath + "/gen_" + str(ngen) + "_cand_" + str(candidate_index)
                    if os.path.isfile(jobNamePath+'.json'):
                        with open('%s.json'% (jobNamePath)) as file:
                            simData = json.load(file)['simData']
                        fitness[candidate_index] = fitnessFunc(simData, **fitnessFuncArgs)
                        jobs_completed += 1
                        print('  Candidate %d fitness = %.1f' % (candidate_index, fitness[candidate_index]))
                except Exception as e:
                    # print 
                    err = "There was an exception evaluating candidate %d:"%(candidate_index)
                    print(("%s \n %s"%(err,e)))
                    #pass
                    #print 'Error evaluating fitness of candidate %d'%(candidate_index)
            num_iters += 1
            print('completed: %d' %(jobs_completed))
            if num_iters >= args.get('maxiter_wait', 5000): 
                print("Max iterations reached, the %d unfinished jobs will be canceled and set to default fitness" % (len(unfinished)))
                for canditade_index in unfinished:
                    fitness[canditade_index] = defaultFitness
                    jobs_completed += 1      
                    if 'scancelUser' in kwargs:
                        os.system('scancel -u %s'%(kwargs['scancelUser']))
                    else:              
                        os.system('scancel %d'%(jobids[candidate_index]))  # terminate unfinished job (resubmitted jobs not terminated!)
            sleep(args.get('time_sleep', 1))
        
        # kill all processes
        if type=='mpi_bulletin':
            try:
                with open("./pids.pid", 'r') as file: # read pids for mpi_bulletin
                    pids = [int(i) for i in file.read().split(' ')[:-1]]
                
                with open("./pids.pid", 'w') as file: # delete content
                    pass
                for pid in pids:
                    try:
                        os.killpg(os.getpgid(pid), signal.SIGTERM)
                    except:
                        pass
            except:
                pass
        # don't want to to this for hpcs since jobs are running on compute nodes not master 
        # else: 
        #     try: 
        #         for pid in pids: os.killpg(os.getpgid(pid), signal.SIGTERM)
        #     except:
        #         pass
        # return
        print("-"*80)
        print("  Completed a generation  ")
        print("-"*80)
        return fitness
        

    # -------------------------------------------------------------------------------
    # Evolutionary optimization: Generation of first population candidates
    # -------------------------------------------------------------------------------
    def generator(random, args):
        # generate initial values for candidates
        return [random.uniform(l, u) for l, u in zip(args.get('lower_bound'), args.get('upper_bound'))]


    # -------------------------------------------------------------------------------
    # Mutator
    # -------------------------------------------------------------------------------
    @EC.variators.mutator
    def nonuniform_bounds_mutation(random, candidate, args):
        """Return the mutants produced by nonuniform mutation on the candidates.
        .. Arguments:
            random -- the random number generator object
            candidate -- the candidate solution
            args -- a dictionary of keyword arguments
        Required keyword arguments in args:
        Optional keyword arguments in args:
        - *mutation_strength* -- the strength of the mutation, where higher
            values correspond to greater variation (default 1)
        """
        lower_bound = args.get('lower_bound')
        upper_bound = args.get('upper_bound')
        strength = args.setdefault('mutation_strength', 1)
        mutant = copy(candidate)
        for i, (c, lo, hi) in enumerate(zip(candidate, lower_bound, upper_bound)):
            if random.random() <= 0.5:
                new_value = c + (hi - c) * (1.0 - random.random() ** strength)
            else:
                new_value = c - (c - lo) * (1.0 - random.random() ** strength)
            mutant[i] = new_value
        
        return mutant
    # -------------------------------------------------------------------------------
    # Evolutionary optimization: Main code
    # -------------------------------------------------------------------------------
    import os
    # create main sim directory and save scripts
    self.saveScripts()

    global ngen
    ngen = -1
    
    # log for simulation      
    logger = logging.getLogger('inspyred.ec')
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(self.saveFolder+'/inspyred.log', mode='a')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)    

    # create randomizer instance
    rand = Random()
    rand.seed(self.seed) 
    
    # create file handlers for observers
    stats_file, ind_stats_file = self.openFiles2SaveStats()

    # gather **kwargs
    kwargs = {'cfg': self.cfg}
    kwargs['num_inputs'] = len(self.params)
    kwargs['paramLabels'] = [x['label'] for x in self.params]
    kwargs['lower_bound'] = [x['values'][0] for x in self.params]
    kwargs['upper_bound'] = [x['values'][1] for x in self.params]
    kwargs['statistics_file'] = stats_file
    kwargs['individuals_file'] = ind_stats_file
    kwargs['netParamsSavePath'] = self.saveFolder+'/'+self.batchLabel+'_netParams.py'

    for key, value in self.evolCfg.items(): 
        kwargs[key] = value
    if not 'maximize' in kwargs: kwargs['maximize'] = False
    
    for key, value in self.runCfg.items(): 
        kwargs[key] = value
    
    # if using pc bulletin board, initialize all workers
    if self.runCfg.get('type', None) == 'mpi_bulletin':
        for iworker in range(int(pc.nhost())):
            pc.runworker()

    #------------------------------------------------------------------
    # Evolutionary algorithm method
    #-------------------------------------------------------------------
    # Custom algorithm based on Krichmar's params
    if self.evolCfg['evolAlgorithm'] == 'custom':
        ea = EC.EvolutionaryComputation(rand)
        ea.selector = EC.selectors.tournament_selection
        ea.variator = [EC.variators.uniform_crossover, nonuniform_bounds_mutation] 
        ea.replacer = EC.replacers.generational_replacement
        if not 'tournament_size' in kwargs: kwargs['tournament_size'] = 2
        if not 'num_selected' in kwargs: kwargs['num_selected'] = kwargs['pop_size']
    
    # Genetic
    elif self.evolCfg['evolAlgorithm'] == 'genetic':
        ea = EC.GA(rand)
    
    # Evolution Strategy
    elif self.evolCfg['evolAlgorithm'] == 'evolutionStrategy':
        ea = EC.ES(rand)
    
    # Simulated Annealing
    elif self.evolCfg['evolAlgorithm'] == 'simulatedAnnealing':
        ea = EC.SA(rand)
    
    # Differential Evolution
    elif self.evolCfg['evolAlgorithm'] == 'diffEvolution':
        ea = EC.DEA(rand)
    
    # Estimation of Distribution
    elif self.evolCfg['evolAlgorithm'] == 'estimationDist':
        ea = EC.EDA(rand)
    
    # Particle Swarm optimization
    elif self.evolCfg['evolAlgorithm'] == 'particleSwarm':
        from inspyred import swarm 
        ea = swarm.PSO(rand)
        ea.topology = swarm.topologies.ring_topology
    
    # Ant colony optimization (requires components)
    elif self.evolCfg['evolAlgorithm'] == 'antColony':
        from inspyred import swarm
        if not 'components' in kwargs: raise ValueError("%s requires components" %(self.evolCfg['evolAlgorithm']))
        ea = swarm.ACS(rand, self.evolCfg['components'])
        ea.topology = swarm.topologies.ring_topology
    
    else:
        raise ValueError("%s is not a valid strategy" % (self.evolCfg['evolAlgorithm']))
        
    ea.terminator = EC.terminators.generation_termination
    ea.observer = [EC.observers.stats_observer, EC.observers.file_observer]


    # -------------------------------------------------------------------------------
    # Run algorithm
    # ------------------------------------------------------------------------------- 
    final_pop = ea.evolve(generator=generator, 
                        evaluator=evaluator,
                        bounder=EC.Bounder(kwargs['lower_bound'],kwargs['upper_bound']),
                        logger=logger,
                        **kwargs)

    # close file
    stats_file.close()
    ind_stats_file.close()
    
    # print best and finish
    print(('Best Solution: \n{0}'.format(str(max(final_pop)))))
    print("-"*80)
    print("   Completed evolutionary algorithm parameter optimization   ")
    print("-"*80)
    sys.exit()