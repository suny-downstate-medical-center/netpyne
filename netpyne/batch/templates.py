"""
Templates for job submission (PBS, SLURM, SGE, etc)
"""
from subprocess import PIPE
from builtins import open
import typing

default_args = {
    ### default (constants) ###
    'sleepInterval': 1,  # what is this for?
    'nodes': 1,
    'script': 'init.py',
    'walltime': '00:30:00',
    'folder': '.',
    'custom': '',
    'printOutput': False,
    'run': True,
}


def createJob(submit: str, filename: str = '', filescript: str = '', stdout: typing.TextIO = PIPE, stderr: typing.TextIO = PIPE):
    """
    wrapper for job submission.
    1. writes to <filename>, <filescript> to execute
    2. subprocess will execute:
        <submit>
    """
    return {'submit': submit, 'filename': filename, 'filescript': filescript, 'stdout': stdout, 'stderr': stderr}

def jobHPCSlurm(batchCfg):
    # default values
    args = {
        'allocation': 'csd403',
        'coresPerNode': 1,
        'email': 'a@b.c',
        'mpiCommand': 'ibrun',
        'reservation': None,
    }
    args.update(batchCfg)
    args['numproc'] = args['nodes'] * args['coresPerNode']
    args.update({
        'res': '#$ -R %s' % (args['reservation']) if args['reservation'] else '',
        'command': "{mpiCommand} -n {numproc} nrniv -python -mpi {script} simConfig={cfgSavePath} netParams={netParamsSavePath}".format(**args),
    })
    # template
    template = \
"""#!/bin/bash
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
"""
    return createJob(submit = "qsub {jobPath}.sh".format(**args), filename = "{jobPath}.sh".format(**args), filescript = template.format(**args))
    
def jobHPCTorque(batchCfg):
    # default values
    args = {
        'ppn': 1,
        'mpiCommand': 'mpiexec',
        'queueName': 'default',
    }
    args.update(batchCfg)
    args['numproc'] = args['nodes'] * args['ppn']
    args['command'] = \
        "{mpiCommand} -n {numproc} nrniv -python -mpi {script} simConfig={cfgSavePath} netParams={netParamsSavePath}".format(**args)
    # template
    template = \
"""#!/bin/bash
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
    return createJob(submit = 'qsub {jobPath}.sh'.format(**args), filename = "{jobPath}.sh".format(**args), filescript = template.format(**args))

def jobHPCSGE(batchCfg):
    """
    creates string for SUN GRID ENGINE
    https://gridscheduler.sourceforge.net/htmlman/htmlman1/qsub.html
    recommended optional pre and post commands
    rsync -a $SGE_O_WORKDIR/ $TMPDIR/
    cd $TMPDIR
    <execute command here>
    rsync -a --exclude '*.run' --exclude '*.err' $TMPDIR/ $SGE_O_WORKDIR/
    """
    # default values
    args = {
            'vmem': '32G',
            'queueName': 'cpu.q',
            'cores': 2,
            'pre': '', 'post': '',
            'mpiCommand': 'mpiexec',
        }
    args.update(batchCfg)
    args['command'] = \
        "{mpiCommand} -n $NSLOTS -hosts $(hostname) nrniv -python -mpi {script} simConfig={cfgSavePath} netParams={netParamsSavePath}".format(**args)
    # template
    template = \
"""#!/bin/bash
#$ -cwd
#$ -N {jobName}
#$ -q {queueName}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -l h_rt={walltime}
#$ -o {jobPath}.run
#$ -e {jobPath}.err
{pre}
source ~/.bashrc
{command}
{post}
"""
    return createJob(submit = 'qsub {jobPath}.sh'.format(**args), filename = "{jobPath}.sh".format(**args), filescript = template.format(**args))

def jobMPIDirect(batchCfg):
    args = {
        'cores': 1,
        'mpiCommand': 'mpirun',
        'script': 'init.py'
    }
    args.update(batchCfg)
    command = \
        "{mpiCommand} -n {cores} nrniv -python -mpi {script} simConfig={cfgSavePath} netParams={netParamsSavePath}"
    stdout = open("{jobName}.run".format(**args), 'w')
    stderr = open("{jobName}.err".format(**args), 'w')
    return createJob(submit = command.format(**args),
                     stdout = stdout,
                     stderr = stderr)

jobTypes = {
    'hpc_torque': jobHPCTorque,
    'hpc_slurm': jobHPCSlurm,
    'hpc_sge': jobHPCSGE,
    'mpi': jobMPIDirect,
    'mpi_direct': jobMPIDirect
}