"""
batch/batch.py 

Class to setup and run batch simulations

Contributors: salvadordura@gmail.com
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
from neuron import h
from copy import copy
from netpyne import specs
from .utils import bashTemplate
from random import Random
from time import sleep, time
from itertools import product
from subprocess import Popen, PIPE
import importlib, types

pc = h.ParallelContext() # use bulletin board master/slave
if pc.id()==0: pc.master_works_on_jobs(0) 

# -------------------------------------------------------------------------------
# function to run single job using ParallelContext bulletin board (master/slave) 
# -------------------------------------------------------------------------------
# func needs to be outside of class
def runEvolJob(script, cfgSavePath, netParamsSavePath, simDataPath):
    import os
    print('\nJob in rank id: ',pc.id())
    command = 'nrniv %s simConfig=%s netParams=%s' % (script, cfgSavePath, netParamsSavePath) 

    with open(simDataPath+'.run', 'w') as outf, open(simDataPath+'.err', 'w') as errf:
        pid = Popen(command.split(' '), stdout=outf, stderr=errf, preexec_fn=os.setsid).pid
    
    with open('./pids.pid', 'a') as file:
        file.write(str(pid) + ' ')
        
# func needs to be outside of class
def runJob(script, cfgSavePath, netParamsSavePath):
    print('\nJob in rank id: ',pc.id())
    command = 'nrniv %s simConfig=%s netParams=%s' % (script, cfgSavePath, netParamsSavePath) 
    print(command+'\n')
    proc = Popen(command.split(' '), stdout=PIPE, stderr=PIPE)
    print(proc.stdout.read().decode())

# -------------------------------------------------------------------------------
# function to create a folder if it does not exist
# -------------------------------------------------------------------------------
def createFolder(folder):
    import os
    if not os.path.exists(folder):
        try:
            os.mkdir(folder)
        except OSError:
            print(' Could not create %s' %(folder))


# -------------------------------------------------------------------------------
# function to convert tuples to strings (avoids erro when saving/loading)
# -------------------------------------------------------------------------------
def tupleToStr (obj):
    #print '\nbefore:', obj
    if type(obj) == list:
        for item in obj:
            if type(item) in [list, dict]:
                tupleToStr(item)
    elif type(obj) == dict:
        for key,val in obj.items():
            if type(val) in [list, dict]:
                tupleToStr(val)
            if type(key) == tuple:
                obj[str(key)] = obj.pop(key) 
    #print 'after:', obj
    return obj


# -------------------------------------------------------------------------------
# Batch class
# -------------------------------------------------------------------------------
class Batch(object):

    def __init__(self, cfgFile='cfg.py', netParamsFile='netParams.py', params=None, groupedParams=None, initCfg={}, seed=None):
        self.batchLabel = 'batch_'+str(datetime.date.today())
        self.cfgFile = cfgFile
        self.initCfg = initCfg
        self.netParamsFile = netParamsFile
        self.saveFolder = '/'+self.batchLabel
        self.method = 'grid'
        self.runCfg = {}
        self.evolCfg = {}
        self.params = []
        self.seed = seed
        if params:
            for k,v in params.items():
                self.params.append({'label': k, 'values': v})
        if groupedParams:
            for p in self.params:
                if p['label'] in groupedParams: p['group'] = True
    

    def save(self, filename):
        import os
        from copy import deepcopy
        basename = os.path.basename(filename)
        folder = filename.split(basename)[0]
        ext = basename.split('.')[1]
        
        # make dir
        createFolder(folder)

        odict = deepcopy(self.__dict__)
        if 'evolCfg' in odict:
            odict['evolCfg']['fitnessFunc'] = 'removed'
        odict['initCfg'] = tupleToStr(odict['initCfg'])
        dataSave = {'batch': tupleToStr(odict)} 
        if ext == 'json':
            from .. import sim
            #from json import encoder
            #encoder.FLOAT_REPR = lambda o: format(o, '.12g')
            print(('Saving batch to %s ... ' % (filename)))

            sim.saveJSON(filename, dataSave)

    def setCfgNestedParam(self, paramLabel, paramVal):
        if isinstance(paramLabel, tuple):
            container = self.cfg
            for ip in range(len(paramLabel)-1):
                if isinstance(container, specs.SimConfig):
                    container = getattr(container, paramLabel[ip])
                else:
                    container = container[paramLabel[ip]]
            container[paramLabel[-1]] = paramVal
        else:
            setattr(self.cfg, paramLabel, paramVal) # set simConfig params


    def saveScripts(self):
        import os

        # create Folder to save simulation
        createFolder(self.saveFolder)
        
        # save Batch dict as json
        targetFile = self.saveFolder+'/'+self.batchLabel+'_batch.json'
        self.save(targetFile)

        # copy this batch script to folder
        targetFile = self.saveFolder+'/'+self.batchLabel+'_batchScript.py'
        os.system('cp ' + os.path.realpath(__file__) + ' ' + targetFile) 

        # copy this batch script to folder, netParams and simConfig
        #os.system('cp ' + self.netParamsFile + ' ' + self.saveFolder + '/netParams.py')

        netParamsSavePath = self.saveFolder+'/'+self.batchLabel+'_netParams.py'
        os.system('cp ' + self.netParamsFile + ' ' + netParamsSavePath) 
        
        os.system('cp ' + os.path.realpath(__file__) + ' ' + self.saveFolder + '/batchScript.py')
        
        # save initial seed
        with open(self.saveFolder + '/_seed.seed', 'w') as seed_file:
            if not self.seed: self.seed = int(time())
            seed_file.write(str(self.seed))
            
        # import cfg
        cfgModuleName = os.path.basename(self.cfgFile).split('.')[0]

        try:  # py3
            loader = importlib.machinery.SourceFileLoader(cfgModuleName, self.cfgFile)
            cfgModule = types.ModuleType(loader.name)
            loader.exec_module(cfgModule)
        except:  # py2
            cfgModule = imp.load_source(cfgModuleName, self.cfgFile)
        
        if hasattr(cfgModule, 'cfg'):
            self.cfg = cfgModule.cfg
        else:
            self.cfg = cfgModule.simConfig
            
        self.cfg.checkErrors = False  # avoid error checking during batch


    def openFiles2SaveStats(self):
        stat_file_name = '%s/%s_stats.cvs' %(self.saveFolder, self.batchLabel)
        ind_file_name = '%s/%s_stats_indiv.cvs' %(self.saveFolder, self.batchLabel)
        individual = open(ind_file_name, 'w')
        stats = open(stat_file_name, 'w')
        stats.write('#gen  pop-size  worst  best  median  average  std-deviation\n')
        individual.write('#gen  #ind  fitness  [candidate]\n')
        return stats, individual


    def run(self):
        # -------------------------------------------------------------------------------
        # Grid Search optimization
        # -------------------------------------------------------------------------------
        if self.method in ['grid','list']:
            # create saveFolder
            import os,glob
            try:
                os.mkdir(self.saveFolder)
            except OSError:
                if not os.path.exists(self.saveFolder):
                    print(' Could not create', self.saveFolder)
            
            # save Batch dict as json
            targetFile = self.saveFolder+'/'+self.batchLabel+'_batch.json'
            self.save(targetFile)

            # copy this batch script to folder
            targetFile = self.saveFolder+'/'+self.batchLabel+'_batchScript.py'
            os.system('cp ' + os.path.realpath(__file__) + ' ' + targetFile) 
 
            # copy netParams source to folder
            netParamsSavePath = self.saveFolder+'/'+self.batchLabel+'_netParams.py'
            os.system('cp ' + self.netParamsFile + ' ' + netParamsSavePath) 
            
            # import cfg
            cfgModuleName = os.path.basename(self.cfgFile).split('.')[0]

            try:
                loader = importlib.machinery.SourceFileLoader(cfgModuleName, self.cfgFile)
                cfgModule = types.ModuleType(loader.name)
                loader.exec_module(cfgModule)
            except:
                cfgModule = imp.load_source(cfgModuleName, self.cfgFile)

            self.cfg = cfgModule.cfg
            self.cfg.checkErrors = False  # avoid error checking during batch

            # set initial cfg initCfg
            if len(self.initCfg) > 0:
                for paramLabel, paramVal in self.initCfg.items():
                    self.setCfgNestedParam(paramLabel, paramVal)

            # iterate over all param combinations
            if self.method == 'grid':
                groupedParams = False
                ungroupedParams = False
                for p in self.params:
                    if 'group' not in p: 
                        p['group'] = False
                        ungroupedParams = True
                    elif p['group'] == True: 
                        groupedParams = True

                if ungroupedParams:
                    labelList, valuesList = zip(*[(p['label'], p['values']) for p in self.params if p['group'] == False])
                    valueCombinations = list(product(*(valuesList)))
                    indexCombinations = list(product(*[range(len(x)) for x in valuesList]))
                else:
                    valueCombinations = [(0,)] # this is a hack -- improve!
                    indexCombinations = [(0,)]
                    labelList = ()
                    valuesList = ()

                if groupedParams:
                    labelListGroup, valuesListGroup = zip(*[(p['label'], p['values']) for p in self.params if p['group'] == True])
                    valueCombGroups = zip(*(valuesListGroup))
                    indexCombGroups = zip(*[range(len(x)) for x in valuesListGroup])
                    labelList = labelListGroup+labelList
                else:
                    valueCombGroups = [(0,)] # this is a hack -- improve!
                    indexCombGroups = [(0,)]

            # if using pc bulletin board, initialize all workers
            if self.runCfg.get('type', None) == 'mpi_bulletin':
                for iworker in range(int(pc.nhost())):
                    pc.runworker()

            for iCombG, pCombG in zip(indexCombGroups, valueCombGroups):
                for iCombNG, pCombNG in zip(indexCombinations, valueCombinations):
                    if groupedParams and ungroupedParams: # temporary hack - improve
                        iComb = iCombG+iCombNG
                        pComb = pCombG+pCombNG
                    elif ungroupedParams:
                        iComb = iCombNG
                        pComb = pCombNG
                    elif groupedParams:
                        iComb = iCombG
                        pComb = pCombG
                    else:
                        iComb = []
                        pComb = []
                        
                    print(iComb, pComb)

                    for i, paramVal in enumerate(pComb):
                        paramLabel = labelList[i]
                        self.setCfgNestedParam(paramLabel, paramVal)

                        print(str(paramLabel)+' = '+str(paramVal))
                        
                    # set simLabel and jobName
                    simLabel = self.batchLabel+''.join([''.join('_'+str(i)) for i in iComb])
                    jobName = self.saveFolder+'/'+simLabel  

                    # skip if output file already exists
                    if self.runCfg.get('skip', False) and glob.glob(jobName+'.json'):
                        print('Skipping job %s since output file already exists...' % (jobName))
                    elif self.runCfg.get('skipCfg', False) and glob.glob(jobName+'_cfg.json'):
                        print('Skipping job %s since cfg file already exists...' % (jobName))
                    elif self.runCfg.get('skipCustom', None) and glob.glob(jobName+self.runCfg['skipCustom']):
                        print('Skipping job %s since %s file already exists...' % (jobName, self.runCfg['skipCustom']))
                    else:
                        # save simConfig json to saveFolder                        
                        self.cfg.simLabel = simLabel
                        self.cfg.saveFolder = self.saveFolder
                        cfgSavePath = self.saveFolder+'/'+simLabel+'_cfg.json'
                        self.cfg.save(cfgSavePath)
                        
                        sleepInterval = 1

                        # hpc torque job submission
                        if self.runCfg.get('type',None) == 'hpc_torque':

                            # read params or set defaults
                            sleepInterval = self.runCfg.get('sleepInterval', 1)
                            nodes = self.runCfg.get('nodes', 1)
                            ppn = self.runCfg.get('ppn', 1)
                            script = self.runCfg.get('script', 'init.py')
                            mpiCommand = self.runCfg.get('mpiCommand', 'mpiexec')
                            walltime = self.runCfg.get('walltime', '00:30:00')
                            queueName = self.runCfg.get('queueName', 'default')
                            nodesppn = 'nodes=%d:ppn=%d'%(nodes,ppn)
                            custom = self.runCfg.get('custom', '')
                            numproc = nodes*ppn
                            
                            command = '%s -np %d nrniv -python -mpi %s simConfig=%s netParams=%s' % (mpiCommand, numproc, script, cfgSavePath, netParamsSavePath)  


                            jobString = """#!/bin/bash 
#PBS -N %s
#PBS -l walltime=%s
#PBS -q %s
#PBS -l %s
#PBS -o %s.run
#PBS -e %s.err
%s
cd $PBS_O_WORKDIR
echo $PBS_O_WORKDIR
%s
                            """ % (jobName, walltime, queueName, nodesppn, jobName, jobName, custom, command)

                           # Send job_string to qsub
                            print('Submitting job ',jobName)
                            print(jobString+'\n')

                            batchfile = '%s.pbs'%(jobName)
                            with open(batchfile, 'w') as text_file:
                                text_file.write("%s" % jobString)

                            proc = Popen(['qsub', batchfile], stderr=PIPE, stdout=PIPE)  # Open a pipe to the qsub command.
                            (output, input) = (proc.stdin, proc.stdout)


                        # hpc torque job submission
                        elif self.runCfg.get('type',None) == 'hpc_slurm':

                            # read params or set defaults
                            sleepInterval = self.runCfg.get('sleepInterval', 1)
                            allocation = self.runCfg.get('allocation', 'csd403') # NSG account
                            nodes = self.runCfg.get('nodes', 1)
                            coresPerNode = self.runCfg.get('coresPerNode', 1)
                            email = self.runCfg.get('email', 'a@b.c')
                            folder = self.runCfg.get('folder', '.')
                            script = self.runCfg.get('script', 'init.py')
                            mpiCommand = self.runCfg.get('mpiCommand', 'ibrun')
                            walltime = self.runCfg.get('walltime', '00:30:00')
                            reservation = self.runCfg.get('reservation', None)
                            custom = self.runCfg.get('custom', '')
                            if reservation:
                                res = '#SBATCH --res=%s'%(reservation)
                            else:  
                                res = ''

                            numproc = nodes*coresPerNode
                            command = '%s -np %d nrniv -python -mpi %s simConfig=%s netParams=%s' % (mpiCommand, numproc, script, cfgSavePath, netParamsSavePath) 

                            jobString = """#!/bin/bash 
#SBATCH --job-name=%s
#SBATCH -A %s
#SBATCH -t %s
#SBATCH --nodes=%d
#SBATCH --ntasks-per-node=%d
#SBATCH -o %s.run
#SBATCH -e %s.err
#SBATCH --mail-user=%s
#SBATCH --mail-type=end
%s
%s

source ~/.bashrc
cd %s
%s
wait
                            """  % (simLabel, allocation, walltime, nodes, coresPerNode, jobName, jobName, email, res, custom, folder, command)

                            # Send job_string to qsub
                            print('Submitting job ',jobName)
                            print(jobString+'\n')

                            batchfile = '%s.sbatch'%(jobName)
                            with open(batchfile, 'w') as text_file:
                                text_file.write("%s" % jobString)

                            #subprocess.call
                            proc = Popen(['sbatch',batchfile], stdin=PIPE, stdout=PIPE)  # Open a pipe to the qsub command.
                            (output, input) = (proc.stdin, proc.stdout)


                        # run mpi jobs directly e.g. if have 16 cores, can run 4 jobs * 4 cores in parallel
                        # eg. usage: python batch.py
                        elif self.runCfg.get('type',None) == 'mpi_direct':
                            jobName = self.saveFolder+'/'+simLabel     
                            print('Running job ',jobName)
                            cores = self.runCfg.get('cores', 1)
                            folder = self.runCfg.get('folder', '.')
                            script = self.runCfg.get('script', 'init.py')
                            mpiCommand = self.runCfg.get('mpiCommand', 'ibrun')

                            command = '%s -np %d nrniv -python -mpi %s simConfig=%s netParams=%s' % (mpiCommand, cores, script, cfgSavePath, netParamsSavePath) 
                            
                            print(command+'\n')
                            proc = Popen(command.split(' '), stdout=open(jobName+'.run','w'),  stderr=open(jobName+'.err','w'))
                            #print proc.stdout.read()
                            
                            
                        # pc bulletin board job submission (master/slave) via mpi
                        # eg. usage: mpiexec -n 4 nrniv -mpi batch.py
                        elif self.runCfg.get('type',None) == 'mpi_bulletin':
                            jobName = self.saveFolder+'/'+simLabel     
                            print('Submitting job ',jobName)
                            # master/slave bulletin board schedulling of jobs
                            pc.submit(runJob, self.runCfg.get('script', 'init.py'), cfgSavePath, netParamsSavePath)
                            
                        else:
                            print("Error: invalid runCfg 'type' selected; valid types are 'mpi_bulletin', 'mpi_direct', 'hpc_slurm', 'hpc_torque'")
                            import sys
                            sys.exit(0)
                
                    sleep(sleepInterval) # avoid saturating scheduler
            print("-"*80)
            print("   Finished submitting jobs for grid parameter exploration   ")
            print("-" * 80)
            while pc.working():
                sleep(sleepInterval)



        # -------------------------------------------------------------------------------
        # Evolutionary optimization
        # -------------------------------------------------------------------------------
        elif self.method == 'evol':
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
                    
                    # modify cfg instance with candidate values
                    for label, value in zip(paramLabels, candidate):
                        self.setCfgNestedParam(label, value)
                        print('set %s=%s' % (label, value))
                    
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

            ####################################################################
            #                       Evolution strategy
            ####################################################################
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
                raise ValueError("%s is not a valid strategy" %(self.evolCfg['evolAlgorithm']))
            ####################################################################
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
