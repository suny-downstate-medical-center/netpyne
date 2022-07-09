"""
Module for SBI optimization
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from builtins import zip

from builtins import range
from builtins import open
from builtins import str
from lib2to3.pytree import NegatedPattern
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
import signal
import glob
from copy import copy
from random import Random
from time import sleep, time
from itertools import product
from subprocess import Popen, PIPE
import importlib, types
import numpy.random as nr
import numpy as np
from scipy.stats import kurtosis

import dill as pickle

from neuron import h
from netpyne import sim, specs
from sbi import utils as utils
from sbi import analysis as analysis
from sbi.inference.base import infer
from sbi.analysis.plot import pairplot
from sbi import utils
from sbi import analysis
from sbi import inference
from sbi.inference import SNPE, SNLE, SNRE, simulate_for_sbi, prepare_for_sbi
import torch
import torch.nn as nn 
import torch.nn.functional as F
from scipy.stats import kurtosis

import time
import multiprocessing


from .utils import createFolder
from .utils import bashTemplate
from .utils import dcp, sigfig

pc = h.ParallelContext() # use bulletin board master/slave


# -------------------------------------------------------------------------------
# Simulation-Based-Inference (SBI) optimization
# -------------------------------------------------------------------------------

def runJob(nrnCommand, script, cfgSavePath, netParamsSavePath, simDataPath):
    """
    Function for/to <short description of `netpyne.batch.sbi_parallel.runJob`>

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
    command = '%s %s simConfig=%s netParams=%s' % (nrnCommand, script, cfgSavePath, netParamsSavePath)
    print(command)

    with open(simDataPath+'.run', 'w') as outf, open(simDataPath+'.err', 'w') as errf:
        pid = Popen(command.split(' '), stdout=outf, stderr=errf, preexec_fn=os.setsid).pid

    with open('./pids.pid', 'a') as file:
        file.write(str(pid) + ' ')


    
def sbiOptim(self, pc):
    """
    Function for/to <short description of `netpyne.batch.sbi_parallel.sbiOptim`>

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

    best_fit = []

    # -------------------------------------------------------------------------------
    # SBI optimization: Parallel evaluation
    # -------------------------------------------------------------------------------

    global ngen
    def objective(param, args):


        import os

        global ngen
        ngen += 1
        total_jobs = 0

        # options slurm, mpi
        type = args.get('type', 'mpi_direct')

        # parameters
        paramLabels = args.get('paramLabels', [])

        # paths to required scripts
        script = args.get('script', 'init.py')
        netParamsSavePath =  args.get('netParamsSavePath')
        genFolderPath = self.saveFolder + '/trial_' + str(ngen)

        # mpi command setup
        nodes = args.get('nodes', 1)
        coresPerNode = args.get('coresPerNode', 1)
        mpiCommand = args.get('mpiCommand', 'mpiexec')
        nrnCommand = args.get('nrnCommand', 'nrniv -python -mpi')
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
        maxFitness = args.get('maxFitness')

        # summary statistics
        SummaryStats = args.get('SummaryStats')
        SummaryStatisticArg = args.get('SummaryStatisticArg')
        SummaryStatisticLength =  args.get('SummaryStatisticLength')
        SummaryStatisticObserved = args.get('SummaryStatisticObserved')


        # read params or set defaults
        sleepInterval = args.get('sleepInterval', 0.2)

        # create folder if it does not exist
        createFolder(genFolderPath)

        # Candidate
        candidate = []
        candidate = np.asarray(param)

        # remember pids and jobids in a list
        pids = []
        jobids = {}

        # create a job for the candidate
        candidate_index = 0

        sleep(sleepInterval)  # required for slurm

        # name and path
        jobName = "trial_" + str(ngen)
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
            pc.submit(runJob, nrnCommand, script, cfgSavePath, netParamsSavePath, jobPath)
            print('-'*80)

        else:
            # ----------------------------------------------------------------------
            # MPI job commnand
            # ----------------------------------------------------------------------
            if mpiCommand == '':
                command = '%s %s simConfig=%s netParams=%s ' % (nrnCommand, script, cfgSavePath, netParamsSavePath)
            else:
                command = '%s -n %d %s %s simConfig=%s netParams=%s ' % (mpiCommand, numproc,  nrnCommand, script, cfgSavePath, netParamsSavePath)

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

            if type == 'mpi_direct':
                with open(jobPath+'.run', 'a+') as outf, open(jobPath+'.err', 'w') as errf:
                    pids.append(Popen([executer, batchfile], stdout=outf, stderr=errf, preexec_fn=os.setsid).pid)
            else:
                with open(jobPath+'.jobid', 'w') as outf, open(jobPath+'.err', 'w') as errf:
                    pids.append(Popen([executer, batchfile], stdout=outf, stderr=errf, preexec_fn=os.setsid).pid)

            #proc = Popen(command.split([executer, batchfile]), stdout=PIPE, stderr=PIPE)
            sleep(0.1)
            #read = proc.stdout.read()

            if type == 'mpi_direct':
                with open('./pids.pid', 'a') as file:
                    file.write(str(pids))
            else:
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
        fitness = [None]  # just 1 candidate
        
        # print outfilestem
        print("Waiting for jobs from generation %d/%d ..." %(ngen, args.get('maxiters')))
        # print "PID's: %r" %(pids)
        # start fitness calculation

        while jobs_completed < total_jobs:
            unfinished = [i for i, x in enumerate(fitness) if x is None ]
            for candidate_index in unfinished:
                try: # load simData and evaluate fitness
                    jobNamePath = genFolderPath + "/trial_" + str(ngen)
                    if os.path.isfile(jobNamePath+'_data.json'):
                        with open('%s_data.json'% (jobNamePath)) as file:
                            simData = json.load(file)['simData']                  
                        fitness[candidate_index] = fitnessFunc(simData, **fitnessFuncArgs)
                        sum_statistics = SummaryStats(simData, **SummaryStatisticArg) 
                        jobs_completed += 1
                        print('  Candidate %d fitness = %.1f' % (candidate_index, fitness[candidate_index]))
                    #for files .json vs _data.json
                    elif os.path.isfile(jobNamePath+'.json'):
                        with open('%s.json'% (jobNamePath)) as file:
                            simData = json.load(file)['simData']                  
                        fitness[candidate_index] = fitnessFunc(simData, **fitnessFuncArgs)
                        sum_statistics = SummaryStats(simData, **SummaryStatisticArg) #Make sure that this works
                        jobs_completed += 1
                        print('  Candidate %d fitness = %.1f' % (candidate_index, fitness[candidate_index]))
                    elif os.path.isfile(jobNamePath+'_data.pkl'):
                        with open('%s_data.pkl'% (jobNamePath), 'rb') as file:
                            simData = pickle.load(file)['simData']
                        fitness[candidate_index] = fitnessFunc(simData, **SummaryStatisticArg)
                        sum_statistics = SummaryStats(simData, **fitnessFuncArgs)
                        jobs_completed += 1
                        print('  Candidate %d fitness = %.1f' % (candidate_index, fitness[candidate_index]))
                    # for files .json vs _data.json
                    elif os.path.isfile(jobNamePath+'.pkl'):
                        with open('%s.pkl'% (jobNamePath), 'rb') as file:
                            simData = pickle.load(file)['simData']
                        fitness[candidate_index] = fitnessFunc(simData, **SummaryStatisticArg)
                        sum_statistics = SummaryStats(simData, **fitnessFuncArgs)
                        jobs_completed += 1
                        print('  Candidate %d fitness = %.1f' % (candidate_index, fitness[candidate_index]))

                except Exception as e:
                    err = "There was an exception evaluating candidate %d:"%(candidate_index)
                    print(("%s \n %s"%(err,e)))
                    

            num_iters += 1


            #Jobs Completed is 0

            print('completed: %d' %(jobs_completed))
            if num_iters >= args.get('maxiter_wait', 5000):
                print("Max iterations reached, the %d unfinished jobs will be canceled and set to default fitness" % (len(unfinished)))
                for canditade_index in unfinished:
                    fitness[canditade_index] = maxFitness # rerun those that didn't complete;
                    sum_statistics= [-1*maxFitness for _ in range(SummaryStatisticLength)] #-MaxFitness for size of summ stats
                    jobs_completed += 1
                    try:
                        if 'scancelUser' in kwargs:
                            os.system('scancel -u %s'%(kwargs['scancelUser']))
                        else:
                            os.system('scancel %d' % (jobids[candidate_index]))  # terminate unfinished job (resubmitted jobs not terminated!)
                    except:
                        pass
            sleep(args.get('time_sleep', 1))

        # kill all processes
        if type == 'mpi_bulletin':
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

        elif type == 'mpi_direct':

            import psutil

            PROCNAME = "nrniv"

            for proc in psutil.process_iter():
                # check whether the process name matches
                try:
                    if proc.name() == PROCNAME:
                        proc.kill()
                except:
                    pass

        print("-" * 80)
        print("  Completed a generation  ")
        print("-" * 80)

        # Rewrite in different manner? 
        if None in SummaryStatisticObserved:
            if not best_fit:
                best_fit.append(candidate)
                best_fit.append(fitness[0])
            else:
                if fitness[0] < best_fit[1]:
                    best_fit[0] = candidate
                    best_fit[1] = fitness[0]
        else:
            if not best_fit:
                best_fit.append(SummaryStatisticObserved)
                
        return torch.as_tensor(fitness + sum_statistics)

    # -------------------------------------------------------------------------------
    # SBI optimization: Main code
    # -------------------------------------------------------------------------------
    import os
    from time import sleep

    try:
        from mpi4py import MPI

        comm = MPI.COMM_WORLD
        size = comm.Get_size()
        rank = comm.Get_rank()
    except:
        size = 1
        rank = 0

    # create main sim directory and save scripts
    self.saveScripts()

    global ngen 
    ngen = -1
    sim_number = -1

    # gather **kwargs
    args = {}
    args['popsize'] = self.optimCfg.get('popsize', 1)
    args['minVals'] = np.array([x['values'][0] for x in self.params]) 
    args['maxVals'] = np.array([x['values'][1] for x in self.params]) 
    args['cfg'] = self.cfg  # include here args/params to pass to evaluator function
    args['paramLabels'] = [x['label'] for x in self.params]
    args['netParamsSavePath'] = self.saveFolder + '/' + self.batchLabel + '_netParams.py'
    args['maxiters'] = self.optimCfg['maxiters'] if 'maxiters' in self.optimCfg else 1000
    args['maxtime'] = self.optimCfg['maxtime'] if 'maxtime' in self.optimCfg else None
    args['fitnessFunc'] = self.optimCfg['fitnessFunc']
    args['fitnessFuncArgs'] = self.optimCfg['fitnessFuncArgs']
    args['SummaryStats'] = self.optimCfg['SummaryStats']
    args['SummaryStatisticArg'] = self.optimCfg['SummaryStatisticArg']
    args['SummaryStatisticLength'] = self.optimCfg.get('SummaryStatisticLength')
    args['SummaryStatisticObserved'] = self.optimCfg.get('SummaryStatisticObserved') # Will be a list or None 
    args['maxiter_wait'] = self.optimCfg['maxiter_wait']
    args['time_sleep'] = self.optimCfg['time_sleep']
    args['maxFitness'] = self.optimCfg.get('maxFitness', 1000)
    args['sbi_method'] = self.optimCfg['sbi_method']
    args['inference_type'] = self.optimCfg['inference_type']
    args['rounds'] = self.optimCfg['rounds']



    for key, value in self.optimCfg.items():
        args[key] = value

    for key, value in self.runCfg.items():
        args[key] = value


    # if using pc bulletin board, initialize all workers
    if self.runCfg.get('type', None) == 'mpi_bulletin':
        for iworker in range(int(pc.nhost())):
            pc.runworker()

    # -------------------------------------------------------------------------------
    # Run algorithm
    # -------------------------------------------------------------------------------
    sleep(rank) # each process waits a different time to avoid saturating sqlite database

    try:

        sbi_method = args.get('sbi_method') # SNPE, SNLE, or SNRE
        sbi_md = {'SNPE': SNPE, 'SNLE': SNLE, 'SNRE': SNRE} # sbi_MethodDictionary
        inference_type = args.get('inference_type') # Single or Multi

        prior = utils.torchutils.BoxUniform(low=torch.as_tensor(np.array(args['minVals'])), 
                                    high=torch.as_tensor(np.array(args['maxVals'])))

        simulator, prior = prepare_for_sbi(lambda param: objective(param, args), prior)
        inference = sbi_md[sbi_method](prior = prior)   


        if inference_type == 'single':
            theta, x = simulate_for_sbi(simulator, proposal = prior, num_simulations= args['maxiters'])
            density_estimator = inference.append_simulations(theta, x).train()
            posterior = inference.build_posterior(density_estimator)

            observable_stats = objective(best_fit[0], args)
            samples = posterior.sample((10000,),   
                                        x = observable_stats)
            posterior_sample = posterior.sample((1,),
                                                    x = observable_stats).numpy()

        elif inference_type == 'multi':
            rounds = args.get('rounds')
            posteriors = []
            proposal = prior
            for round_iter in range(rounds):
                theta, x = simulate_for_sbi(simulator, proposal = prior, num_simulations= args['maxiters'])
                if sbi_method == 'SNPE':
                    density_estimator = inference.append_simulations(theta, x, proposal=proposal).train()
                else:
                    density_estimator = inference.append_simulations(theta, x).train()
                posterior = inference.build_posterior(density_estimator)
                posteriors.append(posterior)
                
                if round_iter < 2: 
                    observable_stats = objective(best_fit[0], args)
                proposal = posterior.set_default_x(observable_stats)

            samples = posterior.sample((10000,),   
                                        x = observable_stats)
            posterior_sample = posterior.sample((1,),
                                                    x = observable_stats).numpy()
        else:
            print('Error on sbi simulation')
        
        print('~' * 80)
        print('~' * 80)
        print('~' * 80)


    except Exception as e:
        print(e)

    # print best and finish
    if rank == size-1:
        import matplotlib.pyplot as plt
        plt.figure()
        _ = analysis.pairplot(samples, 
                           figsize=(16,14)) 
        plt.savefig('PairPlot.png')

        #SAMPLE WILL BE PULLED FROM POSTERIOR SAMPLE OF SBI
        print('\n"Observed" Parameter Where SBI Takes Place Around:', best_fit[0])
        print("-" * 80)
        print('\nPosterior Distribution Sample: ', posterior_sample[0])
        print("-" * 80)

   
        print('\nSaving to output.pkl...\n')
        output = {samples} #All 10000 parameter samples will be saved
        with open('%s/%s_output.pkl' % (self.saveFolder, self.batchLabel), 'wb') as f:
            pickle.dump(output, f)

        sleep(1)

        print("-" * 80)
        print("   Completed SBI parameter optimization   ")
        print("-" * 80)




    sys.exit()
