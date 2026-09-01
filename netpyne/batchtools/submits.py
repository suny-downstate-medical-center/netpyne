from batchtk import runtk
from batchtk.runtk.submits import Submit, Template, SHSubmit
from batchtk.header.header import SOCKET_HANDLES, FILE_HANDLES, ALL_HANDLES

class SGESubmit(SHSubmit):
    SCRIPT_TEMPLATE = Template(
        template = \
"""\
#!/bin/bash
#$ -N job{label}
#$ -q {queue}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -l h_rt={realtime}
#$ -o {stdout}
{handles}
source ~/.bashrc
cd {project_dir}
export JOBID=$JOB_ID
{env}
{command}
""",
        key_args = {'label', 'queue', 'cores', 'vmem', 'realtime', 'output_dir', 'label', 'project_dir', 'output_dir', 'socket_name', 'stdout', 'stderr', 'env', 'command',
                     'handles'}
    )
    COMMAND_TEMPLATE  = Template(
        template = "qsub {output_dir}/{label}.sh",
        key_args = {'output_dir', 'label'}
    )
    SUBMIT_TEMPLATE  = Template(
        template = "qsub {output_dir}/{label}.sh",
        key_args = {'output_dir', 'label'}
    ) # SUBMIT_TEMPLATE deprecated

    def submit_job(self, **kwargs):
        proc = super().submit_job(**kwargs)
        #raise(Exception("Job submission failed:\n{}\n{}\n{}".format(self.submit, self.script, proc)))
        return proc


    def set_handles(self):
        pass #TODO get rid of this in both NetPyNE and batchtk


class SUNYSubmit(SHSubmit):
    SCRIPT_TEMPLATE = Template(
        template = \
"""\
#!/bin/sh
#SBATCH --job-name=search_{label}
#SBATCH --nodes=1
#SBATCH --ntasks={cores}
#SBATCH --mem={mem}
#SBATCH --time={realtime}
#SBATCH --output={stdout}
#SBATCH --error={stderr}
{custom}
{handles}
{env}
cd {project_dir}
source ~/.bashrc
srun --mpi=pmi2 nrniv -python -mpi {script}
""",
        key_args = {'label', 'allocation', 'realtime', 'nodes', 'cores', 'mem',
                    'partition', 'stdout', 'stderr', 'output_dir', 'email', 'handles',
                    'env', 'custom', 'project_dir', 'command', 'script'}
    )

    COMMAND_TEMPLATE = Template(
        template = "sbatch {output_dir}/{label}.sh",
        key_args = {'output_dir', 'label'}
    )
    SUBMIT_TEMPLATE = Template(
        template = "sbatch {output_dir}/{label}.sh",
        key_args = {'output_dir', 'label'}
    )

    def submit_job(self, **kwargs):
        proc = super().submit_job(**kwargs)
        #raise(Exception("Job submission failed:\n{}\n{}\n{}".format(self.submit, self.script, proc)))
        return proc


    def set_handles(self):
        pass #TODO get rid of this in both NetPyNE and batchtk

class SlurmSubmit(SHSubmit):
    SCRIPT_TEMPLATE = Template(
        template = \
"""\
#!/bin/bash
#SBATCH --job-name={label}
#SBATCH -A {allocation}
#SBATCH -t {realtime}
#SBATCH --nodes={nodes}
#SBATCH --ntasks-per-node={coresPerNode}
#SBATCH --cpus-per-task=1
#SBATCH --mem={mem}
#SBATCH --partition={partition}
#SBATCH -o {stdout}
#SBATCH -e {stderr}
#SBATCH --mail-user={email}
#SBATCH --mail-type=end
#SBATCH --export=ALL
export JOBID=$SLURM_JOB_ID
{handles}
{env}
{custom}
cd {project_dir}
{command}
wait
""",
        key_args = {'label', 'allocation', 'realtime', 'nodes', 'coresPerNode', 'mem',
                    'partition', 'stdout', 'stderr', 'output_dir', 'email', 'handles',
                    'env', 'custom', 'project_dir', 'command'}
    )

    COMMAND_TEMPLATE = Template(
        template = "/cm/shared/apps/slurm/current/bin/sbatch {output_dir}/{label}.sh",
        key_args = {'output_dir', 'label'}
    )
    SUBMIT_TEMPLATE = Template(
        template = "/cm/shared/apps/slurm/current/bin/sbatch {output_dir}/{label}.sh",
        key_args = {'output_dir', 'label'}
    ) #submit template deprecated

    def submit_job(self, **kwargs):
        proc = super().submit_job(**kwargs)
        #raise(Exception("Job submission failed:\n{}\n{}\n{}".format(self.submit, self.script, proc)))
        return proc


    def set_handles(self):
        pass #TODO get rid of this in both NetPyNE and batchtk

SHSubmitSOCK = SHSubmit
SHSubmitSFS = SHSubmit
SUNYSubmitSFS = SUNYSubmit

SlurmSubmitSSH = SlurmSubmit
SlurmSubmitSFS = SlurmSubmit # not really any different. No sockets for now...
SGESubmitSSH = SGESubmit
SGESubmitSFS = SGESubmit
SGESubmitSOCK = SGESubmit




