# Running batch simulations using NetPyNE and SGE.

An example of running NetPyNE batch with SGE
This model is a modification of tutorial 8:
http://www.netpyne.org/tutorial.html#tutorial-8-running-batch-simulations

to run on an HPC implementing Sun Grid Engine
https://docs.oracle.com/cd/E19279-01/820-3257-12/n1ge.html
https://gridscheduler.sourceforge.net/htmlman/htmlman1/qsub.html


It implements each 4-core simulation on a compute node.

## Requirements
- NEURON with MPI support
- NetPyNE 

## Quick steps to run batch sims

1) cd src
2) python batch.py

results are generated in tut8_data
simulation logs are generated in ~/qsub/

## Code structure:

* src/netParams.py: Defines the network model. Includes "fixed" parameter values of cells, synapses, connections, stimulation, etc. Changes to this file should only be made for relatively stable improvements of the model. Parameter values that will be varied systematically to explore or tune the model should be included here by referencing the appropiate variable in the simulation configuration (cfg) module. Only a single netParams file is required for each batch of simulations.

* src/cfg.py: Simulation configuration module. Includes parameter values for each simulation run such as duration, dt, recording parameters etc. Also includes the model parameters that are being varied to explore or tune the network. When running a batch, NetPyNE will create one cfg file for each parameter configuration.

* src/init.py: Sequence of commands to run a single simulation. Can be executed via 'ipython init.py'. When running a batch, NetPyNE will call init.py multiple times, pass a different cfg file for each of the parameter configurations explored. 

* src/batch.py: Defines the parameters and parameter values explored in the batch, as well as the run configuration.
```
    b.runCfg = {'type': 'hpc_sge',
                'jobName': 'my_batch',
                'cores': 4,
                'script': 'init.py',
                'skip': True} 
```

* arguments accepted by runCfg are described in netpyne/batch/grid.py
```
    sge_args = {
        'jobName': jobName,
        'walltime': walltime,
        'vmem': '32G',
        'queueName': 'cpu.q',
        'cores': 1,
        'custom': '',
        'mpiCommand': 'mpiexec',
        'log': "~/qsub/{}.run".format(jobName)
        }
```
      
