from netpyne import specs

cfg = specs.SimConfig()

    # General simulation paramaters
cfg.duration = 1000           # Simulation duration in ms
cfg.dt       = 0.025          # Simulation time step in ms
cfg.verbose  = True           # Verbose output

cfg.sec_loc = ('soma', 0.5)
    # config sec/weight

cfg.weight = 0.001

cfg.hParams = {
        'celsius' : 34.0,
        'v_init'  : -80.0         # Initial membrane potential
}

cfg.recordStep   = 0.1       # Step size in ms to save data (e.g., V traces, LFP, etc)

    # Saving options
cfg.filename     = 'wscale'       # Output file name prefix
cfg.savePickle   = True       # Save simulation data to a pickle file
cfg.saveJson     = True       # Save simulation data to a .json file
cfg.saveFolder   = '.'
cfg.simLabel     = 'wscale'

    # Analysis options
    # Other options
cfg.cache_efficient = True




# Initialize configuration

