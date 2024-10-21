from netpyne.batchtools.search import search
from netpyne.batchtools import dispatchers, submits
import numpy
from batchtk import runtk

dispatcher = dispatchers.SFSDispatcher

class CustomSubmit(submits.SlurmSubmitSFS):
    script_args = {'label', 'output_path', 'project_path'}
    script_template = \
        """\
        #SBATCH --job-name={label}
        #SBATCH -A csd403
        #SBATCH -t 00:30:00
        #SBATCH --nodes=1
        #SBATCH --ntasks-per-node=1
        #SBATCH -o {output_path}/{label}.run
        export JOBID=$SLURM_JOB_ID
        export OUTFILE="{output_path}/{label}.out"
        export SGLFILE="{output_path}/{label}.sgl"
        
        {env}
        
        cd {project_path}
        python rosenbrock.py
        """
    script_handles = {runtk.SUBMIT: '{output_path}/{label}.sh',
                      runtk.STDOUT: '{output_path}/{label}.run',
                      runtk.MSGOUT: '{output_path}/{label}.out',
                      runtk.SGLOUT: '{output_path}/{label}.sgl',
                      }

params = {'x0': numpy.arange(0, 5),
          'x1': numpy.arange(0, 5)
          }

search(dispatcher_constructor=dispatcher,
       submit_constructor=CustomSubmit,
       label='grid',
       params=params,
       output_path='../grid_batch',
       checkpoint_path='../ray',
       run_config={},
       num_samples=1,
       metric='fx',
       mode='min',
       algorithm='variant_generator',
       max_concurrent=3)


