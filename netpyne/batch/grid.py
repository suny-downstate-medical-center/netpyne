"""
Module for grid search parameter optimization and exploration

"""

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
from netpyne.logger import logger

pc = h.ParallelContext() # use bulletin board master/slave


# -------------------------------------------------------------------------------
# function to run single job using ParallelContext bulletin board (master/slave)
# -------------------------------------------------------------------------------

# func needs to be outside of class
def runJob(script, cfgSavePath, netParamsSavePath, processes):
    """
    Function for/to <short description of `netpyne.batch.grid.runJob`>

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


    """


    logger.info('Job in rank id: ' + pc.id())
    command = 'nrniv %s simConfig=%s netParams=%s' % (script, cfgSavePath, netParamsSavePath)
    logger.info(command+'\n')
    proc = Popen(command.split(' '), stdout=PIPE, stderr=PIPE)
    logger.info(proc.stdout.read().decode())
    processes.append(proc)



# -------------------------------------------------------------------------------
# Grid Search optimization
# -------------------------------------------------------------------------------
def gridSearch(self, pc):
    """
    Function for/to <short description of `netpyne.batch.grid.gridSearch`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*

    pc : <type>
        <Short description of pc>
        **Default:** *required*


    """


    createFolder(self.saveFolder)

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
    if self.cfg is None:
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

    processes = []
    processFiles = []

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

            logger.info(iComb, pComb)

            for i, paramVal in enumerate(pComb):
                paramLabel = labelList[i]
                self.setCfgNestedParam(paramLabel, paramVal)

                logger.info(str(paramLabel)+' = '+str(paramVal))

            # set simLabel and jobName
            simLabel = self.batchLabel+''.join([''.join('_'+str(i)) for i in iComb])
            jobName = self.saveFolder+'/'+simLabel

            sleepInterval = 1

            # skip if output file already exists
            if self.runCfg.get('skip', False) and glob.glob(jobName+'.json'):
                logger.warning('Skipping job %s since output file already exists...' % (jobName))
            elif self.runCfg.get('skipCfg', False) and glob.glob(jobName+'_cfg.json'):
                logger.warning('Skipping job %s since cfg file already exists...' % (jobName))
            elif self.runCfg.get('skipCustom', None) and glob.glob(jobName+self.runCfg['skipCustom']):
                logger.warning('Skipping job %s since %s file already exists...' % (jobName, self.runCfg['skipCustom']))
            else:
                # save simConfig json to saveFolder
                self.cfg.simLabel = simLabel
                self.cfg.saveFolder = self.saveFolder
                cfgSavePath = self.saveFolder+'/'+simLabel+'_cfg.json'
                self.cfg.save(cfgSavePath)

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
                    printOutput = self.runCfg.get('printOutput', False)
                    numproc = nodes*ppn

                    command = '%s -n %d nrniv -python -mpi %s simConfig=%s netParams=%s' % (mpiCommand, numproc, script, cfgSavePath, netParamsSavePath)


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
                    logger.info('Submitting job ' + jobName)
                    logger.info(jobString + '\n')

                    batchfile = '%s.pbs'%(jobName)
                    with open(batchfile, 'w') as text_file:
                        text_file.write("%s" % jobString)

                    proc = Popen(['qsub', batchfile], stderr=PIPE, stdout=PIPE)  # Open a pipe to the qsub command.
                    (output, input) = (proc.stdin, proc.stdout)


                # hpc slurm job submission
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
                    printOutput = self.runCfg.get('printOutput', False)
                    if reservation:
                        res = '#SBATCH --res=%s'%(reservation)
                    else:
                        res = ''

                    numproc = nodes*coresPerNode
                    command = '%s -n %d nrniv -python -mpi %s simConfig=%s netParams=%s' % (mpiCommand, numproc, script, cfgSavePath, netParamsSavePath)

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

                    # Send job_string to sbatch

                    logger.info('Submitting job ' + jobName)
                    logger.info(jobString+'\n')

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
                    logger.info('Running job ' + jobName)
                    cores = self.runCfg.get('cores', 1)
                    folder = self.runCfg.get('folder', '.')
                    script = self.runCfg.get('script', 'init.py')
                    mpiCommand = self.runCfg.get('mpiCommand', 'mpirun')
                    printOutput = self.runCfg.get('printOutput', False)

                    command = '%s -n %d nrniv -python -mpi %s simConfig=%s netParams=%s' % (mpiCommand, cores, script, cfgSavePath, netParamsSavePath)

                    logger.info(command+'\n')
                    proc = Popen(command.split(' '), stdout=open(jobName+'.run','w'),  stderr=open(jobName+'.err','w'))
                    processes.append(proc)
                    processFiles.append(jobName+'.run')

                # pc bulletin board job submission (master/slave) via mpi
                # eg. usage: mpiexec -n 4 nrniv -mpi batch.py
                elif self.runCfg.get('type',None) == 'mpi_bulletin':
                    jobName = self.saveFolder+'/'+simLabel
                    printOutput = self.runCfg.get('printOutput', False)
                    logger.info('Submitting job ' + jobName)
                    # master/slave bulletin board schedulling of jobs
                    pc.submit(runJob, self.runCfg.get('script', 'init.py'), cfgSavePath, netParamsSavePath, processes)

                else:
                    logger.warning(self.runCfg)
                    logger.warning("Error: invalid runCfg 'type' selected; valid types are 'mpi_bulletin', 'mpi_direct', 'hpc_slurm', 'hpc_torque'")
                    import sys
                    sys.exit(0)

            sleep(sleepInterval) # avoid saturating scheduler
    logger.info("-"*80)
    logger.info("   Finished submitting jobs for grid parameter exploration   ")
    logger.info("-" * 80)
    while pc.working():
        sleep(sleepInterval)

    outfiles = []
    for procFile in processFiles:
        outfiles.append(open(procFile, 'r'))
        
    while any([proc.poll() is None for proc in processes]):
        for i, proc in enumerate(processes):
            newline = outfiles[i].readline()
            if len(newline) > 1:
                # TODO this needs to be changed to logger - but check how to better do it
                print(newline, end='')

        #sleep(sleepInterval)
    
    # attempt to terminate completed processes
    for proc in processes:
        try:
            proc.terminate()
        except:
            pass