# RxD Spreading Depression/Depiolarization
## Overview
A tissue-scale model of spreading depolarization (SD) in brain slices
ported to NetPyNE from [Kelley et al. 2022](https://github.com/suny-downstate-medical-center/SDinSlice).

We use NetPyNE to interface with the NEURON simulator's reaction-diffusion framework to embed thousands of neurons 
(based on the the model from Wei et al. 2014)
in the extracellular space of a brain slice, which is itself embedded in an bath solution.
![rxd_sd](https://github.com/Neurosim-lab/netpyne/blob/development/examples/rxd_net/schematic.png)

We initiate SD in the slice by elevating extracellular K+ in a spherical region at the center of the slice.
Effects of hypoxia and propionate on the slice were modeled by appropriate changes to the volume fraction 
and tortuosity of the extracellular space and oxygen/chloride concentrations.

In this example, we use NetPyNE to define the cells, extracellular space,
ion/oxygen dynamics, and channel/cotransporter/pump dynamics, but we use  
calls to NEURON to handle running the simulation and interval saving. 

## Setup and execution
Requires NEURON with RxD and Python. We recommend using [MPI](https://www.open-mpi.org/) to parallelize simulations.  Simulations, especially without 
multiple cores, may take upwards of thiry minutes.

To run the simulation on a sinle core:
```
python3 init.py
```
To run on (for instance) 6 cores with MPI:
```
mpiexec -n 6 nrniv -python -mpi init.py
```

Parameters like slice oxygenation, radius and concentration of the K+ bolus used 
to initiate SD, neuronal density, etc. can be changed by editing **cfg.py**.

## References
Craig Kelley, Adam J. H. Newton, Sabina Hrabetova, Robert A. McDougal, and William W. Lytton. 2022. “Multiscale Computer Modeling of Spreading Depolarization in Brain Slices.” bioRxiv. https://doi.org/10.1101/2022.01.20.477118.

Yina Wei, Ghanim Ullah, and Steven J. Schiff. "Unification of neuronal spikes, seizures, and spreading depression." Journal of Neuroscience 34, no. 35 (2014): 11733-11743.
https://doi.org/10.1523/JNEUROSCI.0516-14.2014