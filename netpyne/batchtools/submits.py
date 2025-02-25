from batchtk.runtk import Submit, Template
from batchtk import runtk

SFS_HANDLES = {runtk.SUBMIT: '{output_path}/{label}.sh',
               runtk.STDOUT: '{output_path}/{label}.run',
               runtk.MSGOUT: '{output_path}/{label}.out',
               runtk.SGLOUT: '{output_path}/{label}.sgl'}
class SHSubmit(Submit):
    script_args = {'label', 'project_path', 'output_path', 'env', 'command'}
    script_template = \
        """\
#!/bin/sh
cd {project_path}
export JOBID=$$
{env}
nohup {command} > {output_path}/{label}.run 2>&1 &
pid=$!
echo $pid >&1
"""
    script_handles = {
        runtk.STDOUT: '{output_path}/{label}.run',
        runtk.SUBMIT: '{output_path}/{label}.sh'}
    def __init__(self, **kwargs):
        super().__init__(
            submit_template = Template(template="sh {output_path}/{label}.sh",
                                       key_args={'project_path', 'output_path', 'label'}),
            script_template = Template(template=self.script_template,
                                       key_args=self.script_args),
            handles = self.script_handles,
        )
    def set_handles(self):
        pass

    def submit_job(self):
        proc = super().submit_job()
        try:
            self.job_id = int(proc.stdout)
        except Exception as e:
            raise(Exception("{}\nJob submission failed:\n{}\n{}\n{}\n{}".format(e, self.submit, self.script, proc.stdout, proc.stderr)))
        if self.job_id < 0:
            raise(Exception("Job submission failed:\n{}\n{}\n{}\n{}".format(self.submit, self.script, proc.stdout, proc.stderr)))
        return self.job_id

class SHSubmitSFS(SHSubmit):
    script_args = {'label', 'project_path', 'output_path', 'env', 'command'}
    script_template = \
        """\
#!/bin/sh
cd {project_path}
export OUTFILE="{output_path}/{label}.out"
export SGLFILE="{output_path}/{label}.sgl"
export JOBID=$$
{env}
nohup {command} > {output_path}/{label}.run 2>&1 &
pid=$!
echo $pid >&1
"""
    script_handles = {runtk.SUBMIT: '{output_path}/{label}.sh',
                      runtk.STDOUT: '{output_path}/{label}.run',
                      runtk.MSGOUT: '{output_path}/{label}.out',
                      runtk.SGLOUT: '{output_path}/{label}.sgl'}

class SHSubmitSOCK(SHSubmit):
    script_args = {'label', 'project_path', 'output_path', 'env', 'command', 'sockname'}
    script_template = \
        """\
#!/bin/sh
cd {project_path}
export SOCNAME="{sockname}"
export JOBID=$$
{env}
nohup {command} > {output_path}/{label}.run 2>&1 &
pid=$!
echo $pid >&1
"""
    script_handles = {runtk.SUBMIT: '{output_path}/{label}.sh',
                      runtk.STDOUT: '{output_path}/{label}.run',
                      runtk.SOCKET: '{sockname}'}

class SGESubmit(Submit):
    script_args = {'label', 'project_path', 'output_path', 'env', 'command', 'cores', 'vmem', }
    script_template = \
        """\
#!/bin/bash
#$ -N job{label}
#$ -q {queue}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -l h_rt={realtime}
#$ -o {output_path}/{label}.run
cd {project_path}
source ~/.bashrc
export JOBID=$JOB_ID
{env}
{command}
"""
    script_handles = {runtk.SUBMIT: '{output_path}/{label}.sh',
                      runtk.STDOUT: '{output_path}/{label}.run'}
    def __init__(self, **kwargs):
        super().__init__(
            submit_template = Template(template="qsub {output_path}/{label}.sh",
                                       key_args={'output_path',  'label'}),
            script_template = Template(template=self.script_template,
                                       key_args=self.script_args),
            handles = self.script_handles,
            )

    def submit_job(self, **kwargs):
        proc = super().submit_job()
        try:
            self.job_id = proc.stdout.split(' ')[2]
        except Exception as e: #not quite sure how this would occur
            raise(Exception("{}\nJob submission failed:\n{}\n{}\n{}\n{}".format(e, self.submit, self.script, proc.stdout, proc.stderr)))
        return self.job_id

    def set_handles(self):
        pass


class SGESubmitSFS(SGESubmit):
    script_args = {'label', 'project_path', 'output_path', 'env', 'command', 'cores', 'vmem', }
    script_template = \
        """\
#!/bin/bash
#$ -N job{label}
#$ -q {queue}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -l h_rt={realtime}
#$ -o {output_path}/{label}.run
cd {project_path}
source ~/.bashrc
export JOBID=$JOB_ID
export OUTFILE="{output_path}/{label}.out"
export SGLFILE="{output_path}/{label}.sgl"
{env}
{command}
"""
    script_handles = {runtk.SUBMIT: '{output_path}/{label}.sh',
                      runtk.STDOUT: '{output_path}/{label}.run',
                      runtk.MSGOUT: '{output_path}/{label}.out',
                      runtk.SGLOUT: '{output_path}/{label}.sgl',
                      }

class SGESubmitSOCK(SGESubmit):
    script_args = {'label', 'project_path', 'output_path', 'env', 'command', 'cores', 'vmem', 'sockname'}
    script_template = \
        """\
#!/bin/bash
#$ -N job{label}
#$ -q {queue}
#$ -pe smp {cores}
#$ -l h_vmem={vmem}
#$ -l h_rt={realtime}
#$ -o {output_path}/{label}.run
cd {project_path}
source ~/.bashrc
export JOBID=$JOB_ID
export SOCNAME="{sockname}"
{env}
{command}
"""
    script_handles = {runtk.SUBMIT: '{output_path}/{label}.sh',
                      runtk.STDOUT: '{output_path}/{label}.run',
                      runtk.SOCKET: '{sockname}'
                      }

