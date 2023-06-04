"""
Module with helper functions to set up and run batch simulations

"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import builtins

from future import standard_library

standard_library.install_aliases()

import numpy as np
import json
import pickle
import subprocess

# -------------------------------------------------------------------------------
# function to create a folder if it does not exist
# -------------------------------------------------------------------------------
def createFolder(folder):
    """
    Function for/to <short description of `netpyne.batch.utils.createFolder`>

    Parameters
    ----------
    folder : <type>
        <Short description of folder>
        **Default:** *required*


    """

    import os

    if not os.path.exists(folder):
        try:
            os.mkdir(folder)
        except OSError:
            print(' Could not create %s' % (folder))


# -------------------------------------------------------------------------------
# function to define template for bash submission
# -------------------------------------------------------------------------------


def jobStringMPIDirect(custom, folder, command):
    return f"""#!/bin/bash
{custom}
cd {folder}
{command}
    """


def jobStringHPCSlurm(
    jobName, allocation, walltime, nodes, coresPerNode, jobPath, email, reservation, custom, folder, command
):
    res = '#SBATCH --res=%s' % (reservation) if reservation else ''
    return f"""#!/bin/bash
#SBATCH --job-name={jobName}
#SBATCH -A {allocation}
#SBATCH -t {walltime}
#SBATCH --nodes={nodes}
#SBATCH --ntasks-per-node={coresPerNode}
#SBATCH -o {jobPath}.run
#SBATCH -e {jobPath}.err
#SBATCH --mail-user={email}
#SBATCH --mail-type=end
{res}
{custom}
source ~/.bashrc
cd {folder}
{command}
wait
    """


def jobStringHPCTorque(jobName, walltime, queueName, nodes, coresPerNode, jobPath, custom, command):
    return f"""#!/bin/bash
#PBS -N {jobName}
#PBS -l walltime={walltime}
#PBS -q {queueName}
#PBS -l nodes={nodes}:ppn={coresPerNode}
#PBS -o {jobPath}.run
#PBS -e {jobPath}.err
{custom}
cd $PBS_O_WORKDIR
echo $PBS_O_WORKDIR
{command}
        """

def jobStringHPCSGE(jobName, walltime, vmem, queueName, cores, custom, command):
    """
    creates string for SUN GRID ENGINE
    https://gridscheduler.sourceforge.net/htmlman/htmlman1/qsub.html
    """
    return f"""#!/bin/bash
#$ -N {jobName}
#$ -q {queueName}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -l h_rt={walltime}
#$ -o {jobName}.run
{custom}
rsync -a $SGE_O_WORKDIR/ $TMPDIR/
cd $TMPDIR
source ~/.bashrc
{command}
rsync -a $TMPDIR/ $SGE_O_WORKDIR/
        """

def cp(obj, verbose=True, die=True):
    '''
    Function for/to <short description of `netpyne.batch.utils.cp`>

    Parameters
    ----------
    obj : <type>
        <Short description of obj>
        **Default:** *required*

    verbose : bool
        <Short description of verbose>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    die : bool
        <Short description of die>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>
    '''
    from copy import copy

    try:
        output = copy.copy(obj)
    except Exception as E:
        output = obj
        errormsg = 'Warning: could not perform shallow copy, returning original object: %s' % str(E)
        if die:
            raise Exception(errormsg)
        else:
            print(errormsg)
    return output


def dcp(obj, verbose=True, die=False):
    '''
    Function for/to <short description of `netpyne.batch.utils.dcp`>

    Parameters
    ----------
    obj : <type>
        <Short description of obj>
        **Default:** *required*

    verbose : bool
        <Short description of verbose>
        **Default:** ``True``
        **Options:** ``<option>`` <description of option>

    die : bool
        <Short description of die>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
    '''
    import copy

    try:
        output = copy.deepcopy(obj)
    except Exception as E:
        output = cp(obj)
        errormsg = 'Warning: could not perform deep copy, performing shallow instead: %s' % str(E)
        if die:
            raise Exception(errormsg)
        else:
            print(errormsg)
    return output


def sigfig(X, sigfigs=5, SI=False, sep=False, keepints=False):
    '''
    Function for/to <short description of `netpyne.batch.utils.sigfig`>

    Parameters
    ----------
    X : <type>
        <Short description of X>
        **Default:** *required*

    sigfigs : int
        <Short description of sigfigs>
        **Default:** ``5``
        **Options:** ``<option>`` <description of option>

    SI : bool
        <Short description of SI>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    sep : bool
        <Short description of sep>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>

    keepints : bool
        <Short description of keepints>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>
    '''
    output = []

    try:
        n = len(X)
        islist = True
    except:
        X = [X]
        n = 1
        islist = False
    for i in range(n):
        x = X[i]

        suffix = ''
        formats = [(1e18, 'e18'), (1e15, 'e15'), (1e12, 't'), (1e9, 'b'), (1e6, 'm'), (1e3, 'k')]
        if SI:
            for val, suff in formats:
                if abs(x) >= val:
                    x = x / val
                    suffix = suff
                    break  # Find at most one match

        try:
            if x == 0:
                output.append('0')
            elif sigfigs is None:
                output.append(flexstr(x) + suffix)
            elif x > (10**sigfigs) and not SI and keepints:  # e.g. x = 23432.23, sigfigs=3, output is 23432
                roundnumber = int(round(x))
                if sep:
                    string = format(roundnumber, ',')
                else:
                    string = '%0.0f' % x
                output.append(string)
            else:
                magnitude = np.floor(np.log10(abs(x)))
                factor = 10 ** (sigfigs - magnitude - 1)
                x = round(x * factor) / float(factor)
                digits = int(
                    abs(magnitude) + max(0, sigfigs - max(0, magnitude) - 1) + 1 + (x < 0) + (abs(x) < 1)
                )  # one because, one for decimal, one for minus
                decimals = int(max(0, -magnitude + sigfigs - 1))
                strformat = '%' + '%i.%i' % (digits, decimals) + 'f'
                string = strformat % x
                if sep:  # To insert separators in the right place, have to convert back to a number
                    if decimals > 0:
                        roundnumber = float(string)
                    else:
                        roundnumber = int(string)
                    string = format(roundnumber, ',')  # Allow comma separator
                string += suffix
                output.append(string)
        except:
            output.append(flexstr(x))
    if islist:
        return tuple(output)
    else:
        return output[0]


# func needs to be outside of class
def runJob(nrnCommand, script, cfgSavePath, netParamsSavePath, simDataPath, rankId):
    """
    Function for/to <short description of `netpyne.batch.utils.runJob`>

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

    print('\nJob in rank id: ', rankId)
    command = '%s %s simConfig=%s netParams=%s' % (nrnCommand, script, cfgSavePath, netParamsSavePath)
    print(command)

    with open(simDataPath + '.run', 'w') as outf, open(simDataPath + '.err', 'w') as errf:
        pid = subprocess.Popen(command.split(' '), stdout=outf, stderr=errf, start_new_session=True).pid

    with open('./pids.pid', 'a') as file:
        file.write(str(pid) + ' ')


def evaluator(batch, candidates, args, ngen, pc, **kwargs):

    import os
    import signal
    from time import sleep

    total_jobs = 0
    # options slurm, mpi
    type = args.get('type', 'mpi_direct')

    # paths to required scripts
    script = args.get('script', 'init.py')
    netParamsSavePath = args.get('netParamsSavePath')
    genFolderPath = batch.saveFolder + '/gen_' + str(ngen)
    # mpi command setup
    nodes = args.get('nodes', 1)
    paramLabels = args.get('paramLabels', [])
    coresPerNode = args.get('coresPerNode', 1)

    mpiCommand = args.get('mpiCommand', batch.mpiCommandDefault)
    nrnCommand = args.get('nrnCommand', 'nrniv')

    numproc = nodes * coresPerNode
    # slurm setup
    custom = args.get('custom', '')
    folder = args.get('folder', '.')
    email = args.get('email', 'a@b.c')
    walltime = args.get('walltime', '00:01:00')
    reservation = args.get('reservation', None)
    allocation = args.get('allocation', 'csd403')  # NSG account
    # fitness function
    fitnessFunc = args.get('fitnessFunc')
    fitnessFuncArgs = args.get('fitnessFuncArgs')
    if batch.method == 'evol':
        indexToRerun = args.get('defaultFitness')
    else:
        indexToRerun = args.get('maxFitness')
    # summary statistics
    collectSummaryStats = batch.method == 'sbi'
    if collectSummaryStats:
        summaryStatsFunc = args.get('summaryStats')
        summaryStatsArgs = args.get('summaryStatisticArg')
        summaryStatsLength = args.get('summaryStatisticLength')

    # read params or set defaults
    sleepInterval = args.get('sleepInterval', 0.2)
    # create folder if it does not exist
    createFolder(genFolderPath)

    # remember pids and jobids in a list
    pids = []
    jobids = {}

    def jobPathAndNameForCand(index):
        if batch.method in ['optuna', 'sbi']:
            jobName = "trial_" + str(ngen)
        else:
            jobName = "gen_" + str(ngen) + "_cand_" + str(candidate_index)
        return jobName, genFolderPath + '/' + jobName

    # create a job for each candidate
    for candidate_index, candidate in enumerate(candidates):
        # required for slurm
        sleep(sleepInterval)
        # name and path
        jobName, jobPath = jobPathAndNameForCand(candidate_index)
        # set initial cfg initCfg
        if len(batch.initCfg) > 0:
            for paramLabel, paramVal in batch.initCfg.items():
                batch.setCfgNestedParam(paramLabel, paramVal)
        # modify cfg instance with candidate values
        print(paramLabels, candidate)
        for label, value in zip(paramLabels, candidate):
            print('set %s=%s' % (label, value))
            batch.setCfgNestedParam(label, value)
        # self.setCfgNestedParam("filename", jobPath)
        batch.cfg.simLabel = jobName
        batch.cfg.saveFolder = genFolderPath
        # save cfg instance to file
        cfgSavePath = jobPath + '_cfg.json'
        batch.cfg.save(cfgSavePath)

        if type == 'mpi_bulletin':
            # ----------------------------------------------------------------------
            # MPI master-slaves
            # ----------------------------------------------------------------------
            pc.submit(runJob, nrnCommand, script, cfgSavePath, netParamsSavePath, jobPath, pc.id())
            print('-' * 80)
        else:
            # ----------------------------------------------------------------------
            # MPI job command
            # ----------------------------------------------------------------------

            if mpiCommand == '':
                command = '%s %s simConfig=%s netParams=%s ' % (nrnCommand, script, cfgSavePath, netParamsSavePath)
            else:
                command = '%s -n %d %s -python -mpi %s simConfig=%s netParams=%s ' % (
                    mpiCommand,
                    numproc,
                    nrnCommand,
                    script,
                    cfgSavePath,
                    netParamsSavePath,
                )

            # ----------------------------------------------------------------------
            # run on local machine with <nodes*coresPerNode> cores
            # ----------------------------------------------------------------------
            if type == 'mpi_direct':
                #executer = '/bin/bash'
                executer = 'sh' # OS agnostic (Windows)
                jobString = jobStringMPIDirect(custom, folder, command)
            # ----------------------------------------------------------------------
            # Create script to run on HPC through slurm
            # ----------------------------------------------------------------------
            elif type == 'hpc_slurm':
                executer = 'sbatch'
                jobString = jobStringHPCSlurm(
                    jobName,
                    allocation,
                    walltime,
                    nodes,
                    coresPerNode,
                    jobPath,
                    email,
                    reservation,
                    custom,
                    folder,
                    command,
                )
            # ----------------------------------------------------------------------
            # Create script to run on HPC through PBS
            # ----------------------------------------------------------------------
            elif type == 'hpc_torque':
                executer = 'qsub'
                queueName = args.get('queueName', 'default')
                jobString = jobStringHPCTorque(
                    jobName, walltime, queueName, nodes, coresPerNode, jobPath, custom, command
                )
            # ----------------------------------------------------------------------
            # Create script to run on HPC through SGE
            # ----------------------------------------------------------------------
            elif type == 'hpc_sge':
                executer = 'qsub'
                queueName = args.get('queueName', 'default')
                jobString = jobStringHPCSGE(
                    jobName, walltime, queueName, nodes, coresPerNode, jobPath, custom, command
                )
            # ----------------------------------------------------------------------
            # save job and run
            # ----------------------------------------------------------------------
            print('Submitting job ', jobName)
            print(jobString)
            print('-' * 80)
            # save file
            batchfile = '%s.sbatch' % (jobPath)
            with open(batchfile, 'w') as text_file:
                text_file.write("%s" % jobString)

            if type == 'mpi_direct':
                with open(jobPath + '.run', 'a+') as outf, open(jobPath + '.err', 'w') as errf:
                    pids.append(subprocess.Popen([executer, batchfile], stdout=outf, stderr=errf,
                                                 start_new_session=True).pid)
            else:
                with open(jobPath + '.jobid', 'w') as outf, open(jobPath + '.err', 'w') as errf:
                    pids.append(subprocess.Popen([executer, batchfile], stdout=outf, stderr=errf,
                                                 start_new_session=True).pid)
            # proc = subprocess.Popen(command.split([executer, batchfile]), stdout=PIPE, stderr=PIPE)

            sleep(0.1)
            # read = proc.stdout.read()
            if type == 'mpi_direct':
                with open('./pids.pid', 'a') as file:
                    file.write(str(pids))
            else:
                with open(jobPath + '.jobid', 'r') as outf:
                    read = outf.readline()
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
            # pc.done()
        except:
            pass
    num_iters = 0
    jobs_completed = 0
    fitness = [None for cand in candidates]
    # print outfilestem
    if batch.method == 'evol':
        totalGen = args.get('max_generations')
    else:
        totalGen = args.get('maxiters')
    print(f"Waiting for jobs from generation {ngen}/{totalGen} ...")

    # print "PID's: %r" %(pids)
    # start fitness calculation
    while jobs_completed < total_jobs:
        unfinished = [i for i, x in enumerate(fitness) if x is None]
        for candidate_index in unfinished:
            try:  # load simData and evaluate fitness
                _, jobPath = jobPathAndNameForCand(candidate_index)
                dataPath = jobPath + '_data.json'
                simData = None
                if os.path.isfile(dataPath):
                    with open(dataPath) as file:
                        simData = json.load(file)['simData']
                else:
                    dataPath = jobPath + '_data.pkl'
                    if os.path.isfile(dataPath):
                        with open(dataPath, 'rb') as file:
                            simData = pickle.load(file)['simData']
                if simData:
                    fitness[candidate_index] = fitnessFunc(simData, **fitnessFuncArgs)
                    if collectSummaryStats:
                        sum_statistics = summaryStatsFunc(simData, **summaryStatsArgs)
                    jobs_completed += 1
                    print('  Candidate %d fitness = %.1f' % (candidate_index, fitness[candidate_index]))
            except Exception as e:
                err = "There was an exception evaluating candidate %d:" % (candidate_index)
                print(("%s \n %s" % (err, e)))
        num_iters += 1
        print('completed: %d' % (jobs_completed))
        if num_iters >= args.get('maxiter_wait', 5000):
            print(
                "Max iterations reached, the %d unfinished jobs will be canceled and set to default fitness"
                % (len(unfinished))
            )
            for canditade_index in unfinished:
                fitness[canditade_index] = indexToRerun  # rerun those that didn't complete;
                if collectSummaryStats:
                    sum_statistics = [
                        -1 * indexToRerun for _ in range(summaryStatsLength)
                    ]  # -indexToRerun (i.e. -maxFitness) for size of summ stats
                jobs_completed += 1
                try:
                    if 'scancelUser' in kwargs:
                        os.system('scancel -u %s' % (kwargs['scancelUser']))
                    else:
                        os.system(
                            'scancel %d' % (jobids[candidate_index])
                        )  # terminate unfinished job (resubmitted jobs not terminated!)
                except:
                    pass
        sleep(args.get('time_sleep', 1))
    # kill all processes
    if type == 'mpi_bulletin':
        try:
            with open("./pids.pid", 'r') as file:  # read pids for mpi_bulletin
                pids = [int(i) for i in file.read().split(' ')[:-1]]
            with open("./pids.pid", 'w') as file:  # delete content
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

    if collectSummaryStats:
        return fitness, sum_statistics
    else:
        return fitness
