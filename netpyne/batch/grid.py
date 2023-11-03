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

import pandas as pd
import imp
import os, sys
import glob
from time import sleep
from itertools import product
from subprocess import Popen, PIPE
import importlib, types

from neuron import h

from .templates import jobHPCSlurm, jobHPCTorque, jobHPCSGE, jobTypes
from .utils import createFolder, jobSubmit

pc = h.ParallelContext()  # use bulletin board master/slave


# -------------------------------------------------------------------------------
# function to run single job using ParallelContext bulletin board (master/slave)
# -------------------------------------------------------------------------------

# func needs to be outside of class
def runJob(script, cfgSavePath, netParamsSavePath, processes, jobName):
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

    print('\nJob in rank id: ', pc.id())
    command = "nrniv %s simConfig=%s netParams=%s" % (script, cfgSavePath, netParamsSavePath)
    print(command + '\n')

    stdout = open(jobName + '.run', 'w')
    stderr = open(jobName + '.err', 'w')
    proc = Popen(command.split(' '), stdout=PIPE, stderr=PIPE)

    stdout.write(proc.stdout.read().decode())
    stderr.write(proc.stderr.read().decode())

    processes.append(proc)


# -------------------------------------------------------------------------------
# Get parameter combinations
# -------------------------------------------------------------------------------
def getParamCombinations(batch):

    indices = []
    values = []
    filenames = []

    combData = {}

    # generate param combinations
    (
        groupedParams,
        ungroupedParams,
        indexCombGroups,
        valueCombGroups,
        indexCombinations,
        valueCombinations,
        labelList,
        valuesList,
    ) = generateParamCombinations(batch)

    for iCombG, pCombG in zip(indexCombGroups, valueCombGroups):
        for iCombNG, pCombNG in zip(indexCombinations, valueCombinations):
            if groupedParams and ungroupedParams:  # temporary hack - improve
                iComb = iCombG + iCombNG
                pComb = pCombG + pCombNG
            elif ungroupedParams:
                iComb = iCombNG
                pComb = pCombNG
            elif groupedParams:
                iComb = iCombG
                pComb = pCombG
            else:
                iComb = []
                pComb = []

            # set simLabel and jobName
            simLabel = batch.batchLabel + ''.join([''.join('_' + str(i)) for i in iComb])
            jobName = batch.saveFolder + '/' + simLabel

            indices.append(iComb)
            values.append(pComb)
            filenames.append(jobName)

    return {'indices': indices, 'values': values, 'labels': labelList, 'filenames': filenames}


# -------------------------------------------------------------------------------
# Generate parameter combinations
# -------------------------------------------------------------------------------
def generateParamCombinations(batch):

    # iterate over all param combinations
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
        valueCombinations = [(0,)]  # this is a hack -- improve!
        indexCombinations = [(0,)]
        labelList = ()
        valuesList = ()

    if groupedParams:
        labelListGroup, valuesListGroup = zip(*[(p['label'], p['values']) for p in batch.params if p['group'] == True])
        valueCombGroups = zip(*(valuesListGroup))
        indexCombGroups = zip(*[range(len(x)) for x in valuesListGroup])
        labelList = labelListGroup + labelList
    else:
        valueCombGroups = [(0,)]  # this is a hack -- improve!
        indexCombGroups = [(0,)]

    return (
        groupedParams,
        ungroupedParams,
        indexCombGroups,
        valueCombGroups,
        indexCombinations,
        valueCombinations,
        labelList,
        valuesList,
    )


# -------------------------------------------------------------------------------
# Get parameter combinations
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

    # create main sim directory and save scripts
    batch.saveScripts()
    netParamsSavePath = batch.netParamsSavePath

    # set initial cfg initCfg
    if len(batch.initCfg) > 0:
        for paramLabel, paramVal in batch.initCfg.items():
            batch.setCfgNestedParam(paramLabel, paramVal)

    if batch.runCfg.get('type', None) == 'mpi_bulletin':
        pc.runworker()  # only 1 runworker needed in rank0

    processes, processFiles = [], []

    if batch.method == 'list':
        paramListFile = batch.runCfg.get('paramListFile', 'params.csv')
        paramLines = pd.read_csv(paramListFile)
        paramLabels = list(paramLines.columns)
        print(f'Running {len(paramLines)} simulations from {paramListFile}')
        for row in paramLines.itertuples():
            for paramLabel, paramVal in zip(paramLabels, row[1:]):  # 0th element is Index
                batch.setCfgNestedParam(paramLabel, paramVal)
                print(f'{paramLabel} = {paramVal}')
            # set simLabel and jobName
            simLabel = f'{batch.batchLabel}{row.Index}'
            jobName = f'{batch.saveFolder}/{simLabel}'

            gridSubmit(batch, pc, netParamsSavePath, jobName, simLabel, processes, processFiles)

    elif batch.method == 'grid':  # iterate over all param combinations
        # generate param combinations
        combinationsData = getParamCombinations(batch)
        for jobName, iComb, comb in zip(
            combinationsData['filenames'], combinationsData['indices'], combinationsData['values']
        ):
            print(iComb, comb)
            for i, paramVal in enumerate(comb):
                paramLabel = combinationsData['labels'][i]
                batch.setCfgNestedParam(paramLabel, paramVal)
                print(str(paramLabel) + ' = ' + str(paramVal))
            simLabel = jobName.split('/')[-1]

            gridSubmit(batch, pc, netParamsSavePath, jobName, simLabel, processes, processFiles)

    else:
        print("Error: invalid batch.method selected; valid types are 'list', 'grid'")

    print("-" * 80)
    print("   Finished creating jobs for parameter exploration   ")
    print("-" * 80)

    if batch.runCfg.get('type', None) == 'mpi_bulletin':
        while pc.working():
            pass
    outfiles = []
    # processFile polling for batch submission ... ?
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

        # sleep(sleepInterval)

    # attempt to terminate completed processes
    for proc in processes:
        try:
            proc.terminate()
        except:
            pass
    
    pc.done()
    # TODO: line below was commented out due to issue on Netpyne-UI (https://dura-bernallab.slack.com/archives/C02UT6WECEL/p1671724489096569?thread_ts=1671646899.368969&cid=C02UT6WECEL)
    # Needs to be re-visited.
    # h.quit()



def gridSubmit(batch, pc, netParamsSavePath, jobPath, jobName, processes, processFiles):

    # skip if output file already exists
    if batch.runCfg.get('skip', False) and glob.glob(jobPath + '_data.json'):
        print('Skipping job %s since output file already exists...' % (jobPath))
        return
    elif batch.runCfg.get('skipCfg', False) and glob.glob(jobPath + '_cfg.json'):
        print('Skipping job %s since cfg file already exists...' % (jobPath))
        return
    elif batch.runCfg.get('skipCustom', None) and glob.glob(jobPath + batch.runCfg['skipCustom']):
        print('Skipping job %s since %s file already exists...' % (jobPath, batch.runCfg['skipCustom']))
        return

    jobSubmit(batch, pc, netParamsSavePath, jobPath, jobName, processes, processFiles)
"""
    # save simConfig json to saveFolder
    batch.cfg.jobName = jobName
    batch.cfg.saveFolder = batch.saveFolder
    cfgSavePath = jobPath + '_cfg.json'
    batch.cfg.save(cfgSavePath)

    # read params or set defaults
    runCfg_args = {
        'jobPath': jobPath,
        'jobName': jobName,
        'cfgSavePath': cfgSavePath,
        'netParamsSavePath': netParamsSavePath,
    }

    runCfg_args.update(batch.runCfg)
    run = batch.runCfg.get('run', True)
    jobFunc = False
    if batch.runCfg['type'] in jobTypes: # goal to eventually deprecate this for custom functions
        jobFunc = jobTypes[batch.runCfg['type']]
    if 'function' in batch.runCfg:
        jobFunc = batch.runCfg['function']
    if jobFunc:
        job = jobFunc(runCfg_args)
        print('Submitting job ', jobPath)
        filescript = job['filescript']
        if filescript:
            print(job['filescript'] + '\n')
        else:
            print(job['submit'] + '\n')
        batchfile = job['filename']
        if batchfile:
            with open(batchfile, 'w') as text_file:
                text_file.write("{}".format(job['filescript']))
        if run:
            proc = Popen(job['submit'].split(' '), stderr=job['stderr'], stdout=job['stdout'])  # Open a pipe to the pipe command.
            (output, input) = (proc.stdin, proc.stdout)
            processes.append(proc)
            processFiles.append(jobPath + ".run")
    # run mpi jobs directly e.g. if have 16 cores, can run 4 jobs * 4 cores in parallel
    # eg. usage: python batch.py
    # pc bulletin board job submission (master/slave) via mpi
    # eg. usage: mpiexec -n 4 nrniv -mpi batch.py
    elif batch.runCfg.get('type', None) == 'mpi_bulletin':
        script = batch.runCfg.get('script', 'init.py')

        # unnecessary jobPath = batch.saveFolder + '/' + jobName --
        print('Submitting job ', jobPath)
        # master/slave bulletin board scheduling of jobs
        pc.submit(runJob, script, cfgSavePath, netParamsSavePath, processes, jobPath)
        print('Saving output to: ', jobPath + '.run')
        print('Saving errors to: ', jobPath + '.err')
        print('')

    else:
        print(batch.runCfg)
        print("Error: invalid runCfg 'type' selected; valid types are: \n")
        print(jobTypes)
        sys.exit(0)
        
        
    else:
        script = batch.runCfg.get('script', 'init.py')

        jobName = batch.saveFolder + '/' + simLabel
        print('Submitting job ', jobName)
        # master/slave bulletin board scheduling of jobs
        pc.submit(runJob, script, cfgSavePath, netParamsSavePath, processes, jobName)
        print('Saving output to: ', jobName + '.run')
        print('Saving errors to: ', jobName + '.err')
        print('')

"""