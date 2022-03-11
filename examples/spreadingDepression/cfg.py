from netpyne import specs
import numpy as np
#------------------------------------------------------------------------------
#
# SIMULATION CONFIGURATION
#
#------------------------------------------------------------------------------

# Run parameters
cfg = specs.SimConfig()       # object of class cfg to store simulation configuration
cfg.duration = 2e3        # Duration of the simulation, in ms
cfg.hParams['v_init'] = -70.0   # set v_init to -65 mV
cfg.hParams['celsius'] = 37.0
cfg.dt = 0.1 #0.025              # Internal integration timestep to use
cfg.verbose = False            # Show detailed messages 
cfg.recordStep = 1             # Step size in ms to save data (eg. V traces, LFP, etc)
cfg.filename = 'hypox_10s/'   # Set file output name
cfg.Kceil = 15.0
cfg.nRec = 12

 # Network dimensions
cfg.sizeX = 500.0 #250.0 #1000
cfg.sizeY = 200.0 #250.0 #1000
cfg.sizeZ = 500.0 #200.0
cfg.density = 90000.0
cfg.Vtissue = cfg.sizeX * cfg.sizeY * cfg.sizeZ

# slice conditions 
cfg.ox = 'hypoxic'
if cfg.ox == 'perfused':
    cfg.o2_bath = 0.1
    cfg.alpha_ecs = 0.2 
    cfg.tort_ecs = 1.6
elif cfg.ox == 'hypoxic':
    cfg.o2_bath = 0.01
    cfg.alpha_ecs = 0.07 
    cfg.tort_ecs = 1.8

# neuron params 
cfg.betaNrn = 0.24 # total neuronal volume / total tissue volume 
cfg.Ncell = int(cfg.density*(cfg.sizeX*cfg.sizeY*cfg.sizeZ*1e-9)) # default 90k / mm^3
## neuron radius 
if cfg.density == 90000.0:
    cfg.rs = ((cfg.betaNrn * cfg.Vtissue) / (2 * np.pi * cfg.Ncell)) ** (1/3)
else:
    cfg.rs = 7.52
cfg.epas = -70 # False # passive reversal potential
cfg.gpas = 0.0001 # passive conductance
cfg.sa2v = 3.0 # False # neuron surface area to volume ratio
## conversion factor for surface area independent of cell volume
if cfg.sa2v:
    cfg.somaR = (cfg.sa2v * cfg.rs**3 / 2.0) ** (1/2)
else:
    cfg.somaR = cfg.rs
cfg.cyt_fraction = cfg.rs**3 / cfg.somaR**3 

# sd init params 
cfg.k0 = 70.0 # initial K+ bolus concentration
cfg.r0 = 100.0 # initial K+ bolus radius (in microns)