"""
batch.py

Batch simulation for M1 model using NetPyNE
"""
import sys 
sys.path.insert(0,'../../../netpyne/')
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

init_list = [0.0, 0.5, 1.0]
gip3r_list = [12040 * 50, 12040 * 100, 12040 * 150]
def batchRxd():
	params = {'ip3_init' : init_list,
			'gip3r' : gip3r_list}
	initCfg = {'duration' : 1.0*1e3}
	b = Batch(params=params, initCfg=initCfg)
	runBatch(b, 'batchRxd', setup='mpi_bulletin')

# Main code
if __name__ == '__main__':
	from neuron import h 
	pc = h.ParallelContext()
	pcid = pc.id()
	batchRxd()

	# ## analyze 
	# if pcid === 0:
	# 	import json
	# 	for init_ind in range(len(init_list)):
	# 		for gip3d_ind in range(len())
