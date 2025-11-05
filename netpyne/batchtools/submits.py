from batchtk.runtk import Submit, Template
from batchtk import runtk

SFS_HANDLES = {runtk.SUBMIT: '{output_dir}/{label}.sh',
               runtk.STDOUT: '{output_dir}/{label}.run',
               runtk.MSGOUT: '{output_dir}/{label}.out',
               runtk.SGLOUT: '{output_dir}/{label}.sgl'}
class SHSubmit(Submit):
    script_args = {'label', 'project_dir', 'output_dir', 'env', 'command'}
    script_template = \
        """\
#!/bin/sh
cd {project_dir}
export JOBID=$$
{env}
nohup {command} > {output_dir}/{label}.run 2>&1 &
pid=$!
echo $pid >&1
"""
    script_handles = {
        runtk.STDOUT: '{output_dir}/{label}.run',
        runtk.SUBMIT: '{output_dir}/{label}.sh'}
    def __init__(self, **kwargs):
        super().__init__(
            submit_template = Template(template="sh {output_dir}/{label}.sh",
                                       key_args={'project_dir', 'output_dir', 'label'}),
            script_template = Template(template=self.script_template,
                                       key_args=self.script_args),
            handles = self.script_handles,
        )
    def set_handles(self):
        pass

    def submit_job(self, **kwargs):
        proc = super().submit_job(**kwargs)
        try:
            self.job_id = int(proc.stdout)
        except Exception as e:
            raise(Exception("{}\nJob submission failed:\n{}\n{}\n{}\n{}".format(e, self.submit, self.script, proc.stdout, proc.stderr)))
        if self.job_id < 0:
            raise(Exception("Job submission failed:\n{}\n{}\n{}\n{}".format(self.submit, self.script, proc.stdout, proc.stderr)))
        return self.job_id

class SHSubmitSFS(SHSubmit):
    script_args = {'label', 'project_dir', 'output_dir', 'env', 'command'}
    script_template = \
        """\
#!/bin/sh
cd {project_dir}
export MSGFILE="{output_dir}/{label}.out"
export SGLFILE="{output_dir}/{label}.sgl"
export JOBID=$$
{env}
nohup {command} > {output_dir}/{label}.run 2>&1 &
pid=$!
echo $pid >&1
"""
    script_handles = {runtk.SUBMIT: '{output_dir}/{label}.sh',
                      runtk.STDOUT: '{output_dir}/{label}.run',
                      runtk.MSGOUT: '{output_dir}/{label}.out',
                      runtk.SGLOUT: '{output_dir}/{label}.sgl'}

class SHSubmitSOCK(SHSubmit):
    script_args = {'label', 'project_dir', 'output_dir', 'env', 'command', 'sockname'}
    script_template = \
        """\
#!/bin/sh
cd {project_dir}
export SOCNAME="{sockname}"
export JOBID=$$
{env}
nohup {command} > {output_dir}/{label}.run 2>&1 &
pid=$!
echo $pid >&1
"""
    script_handles = {runtk.SUBMIT: '{output_dir}/{label}.sh',
                      runtk.STDOUT: '{output_dir}/{label}.run',
                      runtk.SOCKET: '{sockname}'}

class SGESubmit(Submit):
    script_args = {'label', 'queue', 'cores', 'vmem' 'realtime', 'output_dir', 'project_dir', 'env', 'command', }
    script_template = \
        """\
#!/bin/bash
#$ -N job{label}
#$ -q {queue}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -l h_rt={realtime}
#$ -o {output_dir}/{label}.run
source ~/.bashrc
cd {project_dir}
export JOBID=$JOB_ID
{env}
{command}
"""
    script_handles = {runtk.SUBMIT: '{output_dir}/{label}.sh',
                      runtk.STDOUT: '{output_dir}/{label}.run'}
    def __init__(self, **kwargs):
        super().__init__(
            submit_template = Template(template="qsub {output_dir}/{label}.sh",
                                       key_args={'output_dir',  'label'}),
            script_template = Template(template=self.script_template,
                                       key_args=self.script_args),
            handles = self.script_handles,
            )

    def submit_job(self, **kwargs):
        proc = super().submit_job(**kwargs)
        #raise(Exception("Job submission failed:\n{}\n{}\n{}".format(self.submit, self.script, proc)))
        return proc


    def set_handles(self):
        pass #TODO get rid of this in both NetPyNE and batchtk


class SGESubmitSSH(Submit):
    script_args = {'label', 'queue', 'cores', 'vmem' 'realtime', 'output_dir', 'project_dir', 'env', 'command', }
    script_template = \
        """\
#!/bin/bash
#$ -N job{label}
#$ -q {queue}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -l h_rt={realtime}
#$ -o {output_dir}/{label}.run
source ~/.bashrc
cd {project_dir}
export JOBID=$JOB_ID
export MSGFILE="{output_dir}/{label}.out"
export SGLFILE="{output_dir}/{label}.sgl"
{env}
touch $MSGFILE
{command}
"""
    script_handles = {runtk.SUBMIT: '{output_dir}/{label}.sh',
                      runtk.STDOUT: '{output_dir}/{label}.run',
                      runtk.MSGOUT: '{output_dir}/{label}.out',
                      runtk.SGLOUT: '{output_dir}/{label}.sgl',
                      }
    def __init__(self, **kwargs):
        super().__init__(
            submit_template = Template(template="source ~/.bash_profile; /ddn/age/bin/lx-amd64/qsub {output_dir}/{label}.sh",
                                       key_args={'output_dir',  'label'}),
            script_template = Template(template=self.script_template,
                                       key_args=self.script_args),
            handles = self.script_handles,
            )

    def submit_job(self, **kwargs):
        proc = super().submit_job(**kwargs)
        #raise(Exception("Job submission failed:\n{}\n{}\n{}".format(self.submit, self.script, proc)))
        return proc


    def set_handles(self):
        pass #TODO get rid of this in both NetPyNE and batchtk

class SlurmSubmitSSH(Submit):
    script_args = {'label', 'allocation', 'realtime', 'nodes', 'coresPerNode',
                   'partition', 'output_dir', 'email', 'env', 'custom', 'project_dir', 'command'}
    script_template = \
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
#SBATCH -o {output_dir}/{label}.run
#SBATCH -e {output_dir}/{label}.err
#SBATCH --mail-user={email}
#SBATCH --mail-type=end
#SBATCH --export=ALL
export JOBID=$SLURM_JOB_ID
export MSGFILE="{output_dir}/{label}.out"
export SGLFILE="{output_dir}/{label}.sgl"
{env}
{custom}
cd {project_dir}
{command}
wait
"""
    script_handles = {runtk.SUBMIT: '{output_dir}/{label}.sh',
                      runtk.STDOUT: '{output_dir}/{label}.run',
                      runtk.MSGOUT: '{output_dir}/{label}.out',
                      runtk.SGLOUT: '{output_dir}/{label}.sgl',
                      }
    def __init__(self, **kwargs):
        super().__init__(
            submit_template = Template(template="/cm/shared/apps/slurm/current/bin/sbatch {output_dir}/{label}.sh",
                                       key_args={'output_dir',  'label'}),
            script_template = Template(template=self.script_template,
                                       key_args=self.script_args),
            handles = self.script_handles,
            )

    def submit_job(self, **kwargs):
        proc = super().submit_job(**kwargs)
        #raise(Exception("Job submission failed:\n{}\n{}\n{}".format(self.submit, self.script, proc)))
        return proc


    def set_handles(self):
        pass #TODO get rid of this in both NetPyNE and batchtk

SlurmSubmitSFS = SlurmSubmitSSH # not really any different. No sockets for now...


class SGESubmitSFS(SGESubmit):
    script_args = {'label', 'queue', 'cores', 'vmem' 'realtime', 'output_dir', 'project_dir', 'env', 'command', }
    script_template = \
        """\
#!/bin/bash
#$ -N job{label}
#$ -q {queue}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -l h_rt={realtime}
#$ -o {output_dir}/{label}.run
source ~/.bashrc
cd {project_dir}
export JOBID=$JOB_ID
export MSGFILE="{output_dir}/{label}.out"
export SGLFILE="{output_dir}/{label}.sgl"
{env}
touch $MSGFILE
{command}
"""
    script_handles = {runtk.SUBMIT: '{output_dir}/{label}.sh',
                      runtk.STDOUT: '{output_dir}/{label}.run',
                      runtk.MSGOUT: '{output_dir}/{label}.out',
                      runtk.SGLOUT: '{output_dir}/{label}.sgl',
                      }

class SGESubmitSOCK(SGESubmit):
    script_args = {'label', 'queue', 'cores', 'vmem' 'realtime', 'output_dir', 'project_dir', 'sockname', 'env', 'command', }
    script_template = \
        """\
#!/bin/bash
#$ -N job{label}
#$ -q {queue}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -l h_rt={realtime}
#$ -o {output_dir}/{label}.run
source ~/.bashrc
cd {project_dir}
export JOBID=$JOB_ID
export SOCNAME="{sockname}"
{env}
{command}
"""
    script_handles = {runtk.SUBMIT: '{output_dir}/{label}.sh',
                      runtk.STDOUT: '{output_dir}/{label}.run',
                      runtk.SOCKET: '{sockname}'
                      }


class SlurmSubmit(Submit):
    script_args = {'label', 'allocation', 'walltime', 'nodes', 'coresPerNode', 'output_dir', 'email', 'reservation', 'custom', 'project_dir', 'command'}
    script_template = \
        """\
#SBATCH --job-name={label}
#SBATCH -A {allocation}
#SBATCH -t {walltime}
#SBATCH --nodes={nodes}
#SBATCH --ntasks-per-node={coresPerNode}
#SBATCH -o {output_dir}/{label}.run
#SBATCH -e {output_dir}/{label}.err
#SBATCH --mail-user={email}
#SBATCH --mail-type=end
export JOBID=$SLURM_JOB_ID
{custom}
{env}
cd {project_dir}
{command}
"""
    script_handles = {runtk.SUBMIT: '{output_dir}/{label}.sh',
                      runtk.STDOUT: '{output_dir}/{label}.run'}
    def __init__(self, **kwargs):
        super().__init__(
            submit_template = Template(template="/cm/shared/apps/slurm/current/bin/sbatch {output_dir}/{label}.sh",
                                       key_args={'output_dir',  'label'}),
            script_template = Template(template=self.script_template,
                                       key_args=self.script_args),
            handles = self.script_handles,
            )

    def submit_job(self, **kwargs):
        proc = super().submit_job(**kwargs)
        return proc


    def set_handles(self):
        pass


class SlurmSubmitSOCK(SlurmSubmit):
    script_args = {'label', 'allocation', 'walltime', 'nodes', 'coresPerNode', 'output_dir', 'email', 'reservation', 'custom', 'project_dir', 'command'}
    script_template = \
        """\
#SBATCH --job-name={label}
#SBATCH -A {allocation}
#SBATCH -t {walltime}
#SBATCH --nodes={nodes}
#SBATCH --ntasks-per-node={coresPerNode}
#SBATCH -o {output_dir}/{label}.run
#SBATCH -e {output_dir}/{label}.err
#SBATCH --mail-user={email}
#SBATCH --mail-type=end
export JOBID=$SLURM_JOB_ID
export SOCNAME="{sockname}"
{custom}
{env}
cd {project_dir}
{command}
"""
    script_handles = {runtk.SUBMIT: '{output_dir}/{label}.sh',
                      runtk.STDOUT: '{output_dir}/{label}.run',
                      runtk.SOCKET: '{sockname}'
                      }

