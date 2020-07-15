import os
from netpyne import specs
from netpyne.batch import Batch 


def run_batch(label, params, cfgFile, netParamsFile, script, grouped=None):
    """Runs a batch of simulations."""

    b = Batch(cfgFile=cfgFile, netParamsFile=netParamsFile)
    for k,v in params.items():
        b.params.append({'label': k, 'values': v})
    if grouped is not None:
        for p in b.params:
            if p['label'] in grouped: 
                p['group'] = True
    b.batchLabel = label
    b.saveFolder = os.path.join(b.batchLabel+'_data')
    b.method = 'grid'
    b.runCfg = {'type': 'mpi_bulletin', 
                'script': script, 
                'skip': True}

    if not os.path.isdir(b.saveFolder):
        try:
            os.makedirs(b.saveFolder)
        except:
            pass

    b.run()


def batchTauWeight():
    # Create an ordered dictionary to hold params (NetPyNE's customized version) 
    params = specs.ODict()   

    # Parameters and values to explore (corresponds to variable in simConfig) 
    params['synMechTau2'] = [3.0, 5.0, 7.0]   
    params['connWeight'] = [0.005, 0.01, 0.15]

    run_batch('tauWeight', params, 'tut8_cfg.py', 'tut8_netParams.py', 'tut8_init.py',  grouped=None)


# Main code
if __name__ == '__main__':
    batchTauWeight() 
