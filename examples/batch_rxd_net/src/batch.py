"""
batch.py

Batch simulation for M1 model using NetPyNE
"""
import sys 
from netpyne.batch import Batch


def batchRxd():
    init_list = [0.0, 1.0]
    gip3r_list = [12040 * 50, 12040 * 150]
    
    params = {'ip3_init' : init_list,
            'gip3r' : gip3r_list}

    initCfg = {'duration' : 0.5*1e3}

    b = Batch(cfgFile='src/cfg.py', netParamsFile='src/netParams.py', params=params, initCfg=initCfg)
    
    b.batchLabel = 'batchRxd'
    b.saveFolder = 'data/'+b.batchLabel
    b.method = 'grid'

    b.runCfg = {'type': 'mpi_bulletin',
                'script': 'init.py'}
    
    b.run()


# Main code
if __name__ == '__main__':
    batchRxd()
