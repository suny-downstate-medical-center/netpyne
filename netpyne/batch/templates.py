"""
Templates for job submission (PBS, SLURM, SGE, etc)
"""



def createJob(submit, filename = '', filescript = ''):
    """
    wrapper for job submission.
    1. writes script to job
    2. subprocess will execute:
        submit job
    """
    return {'submit': submit, 'filename': filename, 'filescript': filescript}

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
#SBATCH --job-name={simLabel}
#SBATCH -A {allocation}
#SBATCH -t {walltime}
#SBATCH --nodes={nodes}
#SBATCH --ntasks-per-node={coresPerNode}
#SBATCH -o {jobName}.run
#SBATCH -e {jobName}.err
#SBATCH --mail-user={email}
#SBATCH --mail-type=end
{res}
{custom}
source ~/.bashrc
cd {folder}
{command}
"""
    return createJob(submit = "qsub {jobName}.sh".format(**args), filename = "{jobName}.sh".format(**args), filescript = template.format(**args))
    #return {'submit': 'qsub', 'script': template.format(**args)}

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
#PBS -N {simLabel}
#PBS -l walltime={walltime}
#PBS -q {queueName}
#PBS -l nodes={nodes}:ppn={coresPerNode}
#PBS -o {jobName}.run
#PBS -e {jobName}.err
{custom}
cd $PBS_O_WORKDIR
echo $PBS_O_WORKDIR
{command}
"""
    return createJob(submit = 'qsub {jobName}.sh'.format(**args), filename = "{jobName}.sh".format(**args), filescript = template.format(**args))

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
#$ -N {simLabel}
#$ -q {queueName}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -l h_rt={walltime}
#$ -o {jobName}.run
#$ -e {jobName}.err
{pre}
source ~/.bashrc
{command}
{post}
"""
    return createJob(submit = 'qsub {jobName}.sh'.format(**args), filename = "{jobName}.sh".format(**args), filescript = template.format(**args))

def jobMPIDirect(batchCfg):
    return createJob(submit = 'mpirun something', filename = )
templates = {
    'hpc_torque': jobHPCTorque,
    'hpc_slurm': jobHPCSlurm,
    'hpc_sge': jobHPCSGE,
}


def jobStringMPIDirect(custom, folder, command):
    return f"""#!/bin/bash
{custom}
cd {folder}
{command}
    """




