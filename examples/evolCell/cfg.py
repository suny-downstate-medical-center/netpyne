"""
cfg.py 

Simulation configuration 

Contributors: salvadordura@gmail.com
"""

import numpy as np
from netpyne import specs

cfg = specs.SimConfig()

#------------------------------------------------------------------------------
#
# SIMULATION CONFIGURATION
#
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Run parameters
#------------------------------------------------------------------------------
cfg.duration = 26*1e3			## Duration of the sim, in ms -- value from M1 cfg.py 
cfg.dt = 0.05                   ## Internal Integration Time Step -- value from M1 cfg.py 
cfg.verbose = 0              	## Show detailed messages
cfg.hParams['celsius'] = 37
cfg.printRunTime = 1
cfg.printPopAvgRates = [500, cfg.duration]


#------------------------------------------------------------------------------
# Recording 
#------------------------------------------------------------------------------
cfg.recordTraces = {'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}}
cfg.recordStims = False  
cfg.recordStep = 0.1 


#------------------------------------------------------------------------------
# Saving
#------------------------------------------------------------------------------
cfg.simLabel = 'sim1'
cfg.saveFolder = 'data'
cfg.savePickle = True
cfg.saveJson = False
cfg.saveDataInclude = ['simConfig', 'netParams']#, 'net'] #'simData',


#------------------------------------------------------------------------------
# Analysis and plotting 
#------------------------------------------------------------------------------
cfg.analysis['plotTraces'] = {'include': [0], 'oneFigPer': 'cell', 'saveFig': True, 
							  'showFig': False, 'figSize': (40,8), 'timeRange': [0,cfg.duration]}


#------------------------------------------------------------------------------
# Current inputs 
#------------------------------------------------------------------------------
cfg.addIClamp = 1
amp = list(np.arange(0.0, 0.65, 0.05))
start = list(np.arange(1000, 2000*len(amp), 2000))
cfg.IClamp1 = {'pop': 'ITS4', 'sec': 'soma', 'loc': 0.5, 'start': start, 'dur': 1000, 'amp': amp}


#------------------------------------------------------------------------------
# Parameters
#------------------------------------------------------------------------------
cfg.tune = specs.Dict()
cfg.tune['soma']['vinit'] = -75.0
cfg.tune['dend']['cadad']['kd'] = 0.1
cfg.tune['dend1']['Ra'] = 0.222


'''
**** PARAMS_NEW: cm = 0.75, e_pas = -70, g_pas = 3.79e-03
**** v_init --> -70.4 
*** ACTIVE: 
**** use test_stellate.py with ITS4_ORIG.py to find rheobase: ~0.054nA 
****PARAMS: gmax_naz = 30000, kv_gbar = 1500

53.5 
**** naz_gmax = 72000
**** kv_gbar = 1700 
'''