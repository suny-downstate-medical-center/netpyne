"""
Module for grid search parameter optimization and exploration

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

import csv
import imp
import json
import logging
import datetime
import os, sys
import glob
from copy import copy
from random import Random
from time import sleep, time
from itertools import product
from subprocess import Popen, PIPE
import subprocess
import importlib, types

from neuron import h
from netpyne import specs
from .utils import createFolder
from .utils import bashTemplate

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

    print('\nJob in rank id: ',pc.id())
    command = 'nrniv %s simConfig=%s netParams=%s' % (script, cfgSavePath, netParamsSavePath)
    print(command+'\n')
    proc = subprocess.run(command.split(' '), stdout=PIPE, stderr=PIPE, check=False)
    processes.append(proc)


# -------------------------------------------------------------------------------
# Grid Search optimization
# -------------------------------------------------------------------------------
def gridSearch(batch, pc):
    """
    Function for/to <short description of `netpyne.batch.grid.gridSearch`>

    Parameters
    ----------
    batch : <type>
        <Short description of batch>
        **Default:** *required*

    pc : <type>
        <Short description of pc>
        **Default:** *required*


    """

    if batch.runCfg.get('type',None) == 'mpi_bulletin':
        pc.runworker() # only 1 runworker needed in rank0

    createFolder(batch.saveFolder)

    # save Batch dict as json
    targetFile = batch.saveFolder+'/'+batch.batchLabel+'_batch.json'
    batch.save(targetFile)

    # copy this batch script to folder
    targetFile = batch.saveFolder+'/'+batch.batchLabel+'_batchScript.py'
    os.system('cp ' + os.path.realpath(__file__) + ' ' + targetFile)

    # copy netParams source to folder
    netParamsSavePath = batch.saveFolder+'/'+batch.batchLabel+'_netParams.py'
    os.system('cp ' + batch.netParamsFile + ' ' + netParamsSavePath)

    # import cfg
    if batch.cfg is None:
        cfgModuleName = os.path.basename(batch.cfgFile).split('.')[0]

        try:
            loader = importlib.machinery.SourceFileLoader(cfgModuleName, batch.cfgFile)
            cfgModule = types.ModuleType(loader.name)
            loader.exec_module(cfgModule)
        except:
            cfgModule = imp.load_source(cfgModuleName, batch.cfgFile)

        batch.cfg = cfgModule.cfg

    batch.cfg.checkErrors = False  # avoid error checking during batch

    # set initial cfg initCfg
    if len(batch.initCfg) > 0:
        for paramLabel, paramVal in batch.initCfg.items():
            batch.setCfgNestedParam(paramLabel, paramVal)

    processes = []
    processFiles = []

    if batch.method == 'list':
        paramListFile = batch.runCfg.get('paramListFile', 'params.csv')
        with open(paramListFile, 'r') as lf:
            paramLines = list(csv.reader(lf))
        paramLabels = paramLines.pop(0) # 1st line of file is header
        print(f'Running {len(paramLines)} simulations from {paramListFile}')
        for ii, line in enumerate(paramLines):
            for paramLabel, paramVal in zip(paramLabels, line):
                batch.setCfgNestedParam(paramLabel, paramVal)
                print(f'{paramLabel} = {paramVal}')
            # set simLabel and jobName
            simLabel = f'{batch.batchLabel}{ii}'
            jobName = f'{batch.saveFolder}/{simLabel}'
            gridSubmit(batch, pc, netParamsSavePath, jobName, simLabel, processes, processFiles)

    elif batch.method == 'grid': # iterate over all param combinations
        groupedParams = False
        ungroupedParams = False
        for p in batch.params:
            if 'group' not in p:
                p['group'] = False
                ungroupedParams = True
            elif p['group'] == True:
                groupedParams = True

        if ungroupedParams:
            labelList, valuesList = zip(*[(p['label'], p['values']) for p in batch.params if p['group'] == False])
            valueCombinations = list(product(*(valuesList)))
            indexCombinations = list(product(*[range(len(x)) for x in valuesList]))
        else:
            valueCombinations = [(0,)] # this is a hack -- improve!
            indexCombinations = [(0,)]
            labelList = ()
            valuesList = ()

        if groupedParams:
            labelListGroup, valuesListGroup = zip(*[(p['label'], p['values']) for p in batch.params if p['group'] == True])
            valueCombGroups = zip(*(valuesListGroup))
            indexCombGroups = zip(*[range(len(x)) for x in valuesListGroup])
            labelList = labelListGroup+labelList
        else:
            valueCombGroups = [(0,)] # this is a hack -- improve!
            indexCombGroups = [(0,)]

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
                    batch.setCfgNestedParam(paramLabel, paramVal)

                    print(str(paramLabel)+' = '+str(paramVal))

                # set simLabel and jobName
                simLabel = batch.batchLabel+''.join([''.join('_'+str(i)) for i in iComb])
                jobName = batch.saveFolder+'/'+simLabel

                sleepInterval = 1
                
                gridSubmit(batch, pc, netParamsSavePath, jobName, simLabel, processes, processFiles)
        print("-"*80)
        print("   Finished creating jobs for parameter exploration   ")
        print("-" * 80)

    if batch.runCfg.get('type',None) == 'mpi_bulletin':
        while pc.working(): pass
    outfiles = []
    for procFile in processFiles:
        outfiles.append(open(procFile, 'r'))

    # note: while the process is running the poll() method will return None
    # depending on the platform or the way the source file is executed (e.g. if run using mpiexec),
    # the stored processes ids might correspond to completed processes
    # and therefore return 1 (even though nrniv processes are still running)
    while any([proc.poll() is None for proc in processes]):
        for i, proc in enumerate(processes):
            newline = outfiles[i].readline()
            if len(newline) > 1:
                print(newline, end='')

        #sleep(sleepInterval)

    # attempt to terminate completed processes
    for proc in processes:
        try:
            proc.terminate()
        except:
            pass
    pc.done()
    h.quit()

def gridSubmit(batch, pc, netParamsSavePath, jobName, simLabel, processes, processFiles):

    # skip if output file already exists
    if batch.runCfg.get('skip', False) and glob.glob(jobName+'.json'):
        print('Skipping job %s since output file already exists...' % (jobName))
    elif batch.runCfg.get('skipCfg', False) and glob.glob(jobName+'_cfg.json'):
        print('Skipping job %s since cfg file already exists...' % (jobName))
    elif batch.runCfg.get('skipCustom', None) and glob.glob(jobName+batch.runCfg['skipCustom']):
        print('Skipping job %s since %s file already exists...' % (jobName, batch.runCfg['skipCustom']))
    else:
        # save simConfig json to saveFolder
        batch.cfg.simLabel = simLabel
        batch.cfg.saveFolder = batch.saveFolder
        cfgSavePath = batch.saveFolder+'/'+simLabel+'_cfg.json'
        batch.cfg.save(cfgSavePath)

    # hpc torque job submission
    if batch.runCfg.get('type',None) == 'hpc_torque':

        # read params or set defaults
        sleepInterval = batch.runCfg.get('sleepInterval', 1)
        nodes = batch.runCfg.get('nodes', 1)
        ppn = batch.runCfg.get('ppn', 1)
        script = batch.runCfg.get('script', 'init.py')
        mpiCommand = batch.runCfg.get('mpiCommand', 'mpiexec')
        walltime = batch.runCfg.get('walltime', '00:30:00')
        queueName = batch.runCfg.get('queueName', 'default')
        nodesppn = 'nodes=%d:ppn=%d'%(nodes,ppn)
        custom = batch.runCfg.get('custom', '')
        printOutput = batch.runCfg.get('printOutput', False)
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
        print('Submitting job ',jobName)
        print(jobString+'\n')

        batchfile = '%s.pbs'%(jobName)
        with open(batchfile, 'w') as text_file:
            text_file.write("%s" % jobString)

        proc = Popen(['qsub', batchfile], stderr=PIPE, stdout=PIPE)  # Open a pipe to the qsub command.
        (output, input) = (proc.stdin, proc.stdout)

    # hpc slurm job submission
    elif batch.runCfg.get('type',None) == 'hpc_slurm':

        # read params or set defaults
        sleepInterval = batch.runCfg.get('sleepInterval', 1)
        allocation = batch.runCfg.get('allocation', 'csd403') # NSG account
        nodes = batch.runCfg.get('nodes', 1)
        coresPerNode = batch.runCfg.get('coresPerNode', 1)
        email = batch.runCfg.get('email', 'a@b.c')
        folder = batch.runCfg.get('folder', '.')
        script = batch.runCfg.get('script', 'init.py')
        mpiCommand = batch.runCfg.get('mpiCommand', 'ibrun')
        walltime = batch.runCfg.get('walltime', '00:30:00')
        reservation = batch.runCfg.get('reservation', None)
        custom = batch.runCfg.get('custom', '')
        printOutput = batch.runCfg.get('printOutput', False)
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
    elif batch.runCfg.get('type',None) == 'mpi_direct':
        jobName = batch.saveFolder+'/'+simLabel
        print('Running job ',jobName)
        cores = batch.runCfg.get('cores', 1)
        folder = batch.runCfg.get('folder', '.')
        script = batch.runCfg.get('script', 'init.py')
        mpiCommand = batch.runCfg.get('mpiCommand', 'mpirun')
        printOutput = batch.runCfg.get('printOutput', False)

        command = '%s -n %d nrniv -python -mpi %s simConfig=%s netParams=%s' % (mpiCommand, cores, script, cfgSavePath, netParamsSavePath)

        print(command+'\n')
        proc = Popen(command.split(' '), stdout=open(jobName+'.run','w'),  stderr=open(jobName+'.err','w'))
        processes.append(proc)
        processFiles.append(jobName+'.run')

    # pc bulletin board job submission (master/slave) via mpi
    # eg. usage: mpiexec -n 4 nrniv -mpi batch.py
    elif batch.runCfg.get('type',None) == 'mpi_bulletin':
        script = batch.runCfg.get('script', 'init.py')

        jobName = batch.saveFolder+'/'+simLabel
        printOutput = batch.runCfg.get('printOutput', False)
        print('Submitting job ',jobName)
        # master/slave bulletin board scheduling of jobs
        pc.submit(runJob, script, cfgSavePath, netParamsSavePath, processes)
    else:
        print(batch.runCfg)
        print("Error: invalid runCfg 'type' selected; valid types are 'mpi_bulletin', 'mpi_direct', 'hpc_slurm', 'hpc_torque'")
        sys.exit(0)
