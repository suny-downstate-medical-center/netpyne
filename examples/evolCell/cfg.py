"""
cfg.py 

Simulation configuration 

Contributors: salvadordura@gmail.com
"""

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
cfg.duration = 1.5*1e3			## Duration of the sim, in ms -- value from M1 cfg.py 
cfg.dt = 0.05                   ## Internal Integration Time Step -- value from M1 cfg.py 
cfg.verbose = 1                	## Show detailed messages
cfg.hParams['celsius'] = 37
cfg.printRunTime = 0.1
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
cfg.savePickle = False
cfg.saveJson = True
cfg.saveDataInclude = ['simData', 'simConfig', 'netParams', 'net']


#------------------------------------------------------------------------------
# Analysis and plotting 
#------------------------------------------------------------------------------
cfg.analysis['plotTraces'] = {'include': [0], 'oneFigPer': 'cell', 'saveFig': True, 
							  'showFig': False, 'figSize': (10,8), 'timeRange': [0,cfg.duration]}


#------------------------------------------------------------------------------
# Current inputs 
#------------------------------------------------------------------------------
cfg.addIClamp = 1
cfg.IClamp1 = {'pop': 'ITS4', 'sec': 'soma', 'loc': 0.5, 'start': 500, 'dur': 1000, 'amp': 0.0}


#------------------------------------------------------------------------------
# Parameters
#------------------------------------------------------------------------------
'''
cfg.vinit = -75.0

**** PARAMS_NEW: cm = 0.75, e_pas = -70, g_pas = 3.79e-03
**** v_init --> -70.4 
*** ACTIVE: 
**** use test_stellate.py with ITS4_ORIG.py to find rheobase: ~0.054nA 
****PARAMS: gmax_naz = 30000, kv_gbar = 1500

53.5 
**** naz_gmax = 72000
**** kv_gbar = 1700 
'''