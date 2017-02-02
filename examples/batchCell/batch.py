"""
batch.py 

Batch simulation for M1 model using NetPyNE

Contributors: salvadordura@gmail.com
"""

from netpyne.batch import Batch
import numpy as np


def createBatch(params):
	# Create Batch object
	b = Batch()
	for k,v in params.iteritems():
		b.params.append({'label': k, 'values': v})
	return b


def runBatch(b, label):
	b.batchLabel = label
	b.saveFolder = 'data/'+b.batchLabel
	b.method = 'grid'
	b.runCfg = {'type': 'mpi', 
				'script': 'init.py', 
				'skip': True}
	
	b.run() # run batch


def batchNa():
	b = createBatch({'dendNa': [0.025, 0.03, 0.035, 0.4],  
					('IClamp1', 'amp'): list(np.arange(-2.0, 8.0, 0.5)/10.0)})
	runBatch(b, 'batchNa')


def batchNMDA():
	b = createBatch({'tau1NMDA': [10, 15, 20, 25],  
	  		('NetStim1', 'weight'): list(np.arange(1.0, 10.0, 1.0)/1e4)})
	runBatch(b, 'batchNMDA')


# Main code
if __name__ == '__main__':
	batchNa() 
	# batchNMDA()



