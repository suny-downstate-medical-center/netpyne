"""
batch.py 

Batch simulation for M1 model using NetPyNE

Contributors: salvadordura@gmail.com
"""

from netpyne.batch import Batch
import numpy as np


def runBatch(b, label, setup='mpi_bulletin'):

    b.batchLabel = label
    b.saveFolder = 'data/'+b.batchLabel
    b.method = 'grid'

    if setup == 'mpi_bulletin':
        b.runCfg = {'type': 'mpi_bulletin', 
                    'script': 'init.py', 
                    'skip': True}
	
    elif setup == 'hpc_slurm_comet':
        b.runCfg = {'type': 'hpc_slurm', 
                    'allocation': 'csd403', 
                    'walltime': '6:00:00',
                    'nodes': 1,
                    'coresPerNode': 24,  
                    'email': 'salvadordura@gmail.com',
                    'folder': '/home/salvadord/netpyne/examples/batchCell',  # startup folder
                    'script': 'init.py', 
                    'mpiCommand': 'ibrun'}  # specific command for Comet
                    
    b.run() # run batch

def runBatchComet(b, label):
	b.batchLabel = label
	b.saveFolder = 'data/'+b.batchLabel
	b.method = 'grid'
	b.runCfg = {'type': 'mpi_bulletin', 
				'script': 'init.py', 
				'skip': True}
	
	b.run() # run batch


def batchNa():
	params = {'dendNa': [0.025, 0.03, 0.035, 0.4],  
			('IClamp1', 'amp'): list(np.arange(-2.0, 8.0, 0.5)/10.0)}
	initCfg = {'duration': 1.1, 'tau1NMDA': 15}
	b = Batch(params=params, initCfg=initCfg)
	runBatch(b, 'batchNa', setup='mpi_bulletin')


def batchNMDA():
	params = {'tau1NMDA': [10, 15, 20, 25],  
	  		 ('NetStim1', 'weight'): list(np.arange(1.0, 10.0, 1.0)/1e4)}
	initCfg = {'duration': 1.1}
	b = Batch(params=params, initCfg=initCfg)
	runBatch(b, 'batchNMDA', setup='mpi_bulletin')


# Main code
if __name__ == '__main__':
	batchNa() 
	# batchNMDA()

