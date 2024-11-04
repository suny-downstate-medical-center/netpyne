from netpyne.batchtools.search import search
from netpyne.batchtools import dispatchers, submits
import numpy
from batchtk import runtk

dispatcher = dispatchers.SFSDispatcher

shell_script = """\
#!/bin/sh
cd {project_path}
export MSGFILE="{output_path}/{label}.out"
export SGLFILE="{output_path}/{label}.sgl"
export JOBID=$$
{env}
nohup python rosenbrock.py > {output_path}/{label}.run 2>&1 &
pid=$!
echo $pid >&1
"""

sbatch_script = """\
#SBATCH --job-name={label}
#SBATCH -A csd403
#SBATCH -t 00:30:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH -o {output_path}/{label}.run

export JOBID=$SLURM_JOB_ID
export MSGFILE="{output_path}/{label}.out"
export SGLFILE="{output_path}/{label}.sgl"

{env}
        
cd {project_path}
python rosenbrock.py
"""


class CustomSubmit(submits.SHSubmitSFS):
    script_args = {'label', 'output_path', 'project_path'}
    script_template = shell_script
    script_handles = {runtk.SUBMIT: '{output_path}/{label}.sh',
                      runtk.STDOUT: '{output_path}/{label}.run',
                      runtk.MSGOUT: '{output_path}/{label}.out',
                      runtk.SGLOUT: '{output_path}/{label}.sgl',
                      }

params = {'x0': numpy.linspace(0, 1, 2),
          'x1': numpy.linspace(0, 1, 2)
          }

search(dispatcher_constructor=dispatcher,
       submit_constructor=CustomSubmit,
       label='grid',
       params=params,
       output_path='../custom_batch',
       checkpoint_path='../ray',
       run_config={},
       num_samples=1,
       metric='fx',
       mode='min',
       algorithm='variant_generator',
       max_concurrent=3)
