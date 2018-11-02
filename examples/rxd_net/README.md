# RxD network example
## Description
A 3-layer network with intra- and extra-cellular RxD and LFP recording illustrating multiscale effects.

Changing the initial intracellular ip3 (e.g. from 0 to 0.1) concentration leads to a chain of effects that reduces network firing and the LFP signal:
high ip3 -> ER Ca released to Cyt -> kBK channels open -> less firing 

![rxd_net](https://github.com/Neurosim-lab/netpyne/blob/development/examples/rxd_net/rxdfig.png)

Developed using NetPyNE (www.netpyne.org)

## Setup and execution

Requires NEURON with RxD and Python. 

1. Type or ./compile or the equivalent `nrnivmodl mod`. This should create a directory called either i686 or x86_64, depending on your computer's architecture. 

2. To run type: `python -i init.py`

## Overview of file structure:

* /init.py: Main executable; calls functions from other modules. Sets what parameter file to use.

* /netParams.py: Network parameters

* /cfg.py: Simulation configuration


For further information please contact: salvadordura@gmail.com 

