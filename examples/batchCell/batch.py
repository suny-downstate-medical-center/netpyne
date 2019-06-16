"""
batch.py 

Batch simulation for M1 model using NetPyNE

Contributors: salvadordura@gmail.com
"""

from netpyne.batch import Batch
import numpy as np


def runBatch(b, label):
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
	runBatch(b, 'batchNa')


def batchNMDA():
	params = {'tau1NMDA': [10, 15, 20, 25],  
	  		 ('NetStim1', 'weight'): list(np.arange(1.0, 10.0, 1.0)/1e4)}
	initCfg = {'duration': 1.1}
	b = Batch(params=params, initCfg=initCfg)
	runBatch(b, 'batchNMDA')


# Main code
if __name__ == '__main__':
	batchNa() 
	# batchNMDA()



