"""
batch/utils.py 

Helper functions to set up and run batch simulations

Contributors: salvadordura@gmail.com
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import


from future import standard_library
standard_library.install_aliases()
def bashTemplate(template):
    ''' return the bash commands required by template for batch simulation'''
    
    if template=='mpi_direct':
        return """#!/bin/bash 
%s
cd %s
%s
        """
    elif template=='hpc_slurm':
        return """#!/bin/bash 
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
        """
    elif template=='hpc_torque':
        return """#!/bin/bash 
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
        """