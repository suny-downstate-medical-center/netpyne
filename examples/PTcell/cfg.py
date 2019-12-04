"""
cfg.py 

Simulation configuration for M1 model (using NetPyNE)

Contributors: salvadordura@gmail.com
"""

from netpyne import specs
import pickle

cfg = specs.SimConfig()  

#------------------------------------------------------------------------------
#
# SIMULATION CONFIGURATION
#
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Run parameters
#------------------------------------------------------------------------------
cfg.duration = 0.25*1e3
cfg.dt = 0.05
cfg.seeds = {'conn': 4321, 'stim': 1234, 'loc': 4321} 
cfg.hParams = {'celsius': 34, 'v_init': -80}  
cfg.verbose = 0
cfg.createNEURONObj = True
cfg.createPyStruct = True  
cfg.cvode_active = False
cfg.cvode_atol = 1e-6
cfg.cache_efficient = True
cfg.printRunTime = 0.1

cfg.includeParamsLabel = False
cfg.printPopAvgRates = True

cfg.checkErrors = False

#------------------------------------------------------------------------------
# Recording 
#------------------------------------------------------------------------------
allpops = ['PT5B']

cfg.recordTraces = {'V_soma': {'sec':'soma', 'loc':0.5, 'var':'v'}}

cfg.recordStim = False
cfg.recordTime = False  
cfg.recordStep = 0.1
#cfg.recordLFP = [[10, y, 90] for y in range(450, 1250, 100)] 
cfg.saveLFPCells = False

#------------------------------------------------------------------------------
# Saving
#------------------------------------------------------------------------------
cfg.simLabel = 'PTcell'
cfg.saveFolder = '.'
cfg.savePickle = False
cfg.saveJson = True
cfg.saveDataInclude = ['simData', 'simConfig', 'netParams']#, 'net']
cfg.backupCfgFile = None #['cfg.py', 'backupcfg/'] 
cfg.gatherOnlySimData = False
cfg.saveCellSecs = True
cfg.saveCellConns = True

#------------------------------------------------------------------------------
# Analysis and plotting 
#------------------------------------------------------------------------------
with open('cells/popColors.pkl', 'rb') as fileObj: popColors = pickle.load(fileObj)['popColors']
cfg.analysis['plotTraces'] = {'include': [('PT5B',00)], 'timeRange': [0,cfg.duration], 'oneFigPer': 'cell', 'figSize': (10,4), 'saveFig': True, 'showFig': True} 
#cfg.analysis['plotLFP'] = {'separation': 1.0, 'plots': ['timeSeries', 'locations']}

#------------------------------------------------------------------------------
# Cells
#------------------------------------------------------------------------------
cfg.ihModel = 'migliore'  # ih model
cfg.ihGbar = 1.0  # multiplicative factor for ih gbar in PT cells
cfg.ihGbarBasal = 1.0 # 0.1 # multiplicative factor for ih gbar in PT cells
cfg.ihlkc = 0.2 # ih leak param (used in Migliore)
cfg.ihlkcBasal = 1.0
cfg.ihlkcBelowSoma = 0.01
cfg.ihlke = -86  # ih leak param (used in Migliore)
cfg.ihSlope = 14*2

cfg.removeNa = False  # simulate TTX; set gnabar=0s
cfg.somaNa = 5
cfg.dendNa = 0.3
cfg.axonNa = 7
cfg.axonRa = 0.005

cfg.gpas = 0.5  # multiplicative factor for pas g in PT cells
cfg.epas = 0.9  # multiplicative factor for pas e in PT cells

#------------------------------------------------------------------------------
# Synapses
#------------------------------------------------------------------------------
cfg.synWeightFractionEE = [0.5, 0.5] # E->E AMPA to NMDA ratio
cfg.synWeightFractionEI = [0.5, 0.5] # E->I AMPA to NMDA ratio
cfg.synWeightFractionSOME = [0.9, 0.1] # SOM -> E GABAASlow to GABAB ratio

cfg.AMPATau2Factor = 1.0

#------------------------------------------------------------------------------
# Network 
#------------------------------------------------------------------------------
cfg.weightNormThreshold = 4.0  # weight normalization factor threshold

#------------------------------------------------------------------------------
# Subcellular distribution
#------------------------------------------------------------------------------
cfg.addSubConn = 1

#------------------------------------------------------------------------------
# Current inputs 
#------------------------------------------------------------------------------
cfg.addIClamp = 0

cfg.IClamp1 = {'pop': 'PT5B', 'sec': 'soma', 'loc': 0.5, 'start': 0, 'dur': 1000, 'amp': 0.40}


#------------------------------------------------------------------------------
# NetStim inputs 
#------------------------------------------------------------------------------
cfg.addNetStim = 1

# cfg.NetStim1 = {'pop': 'PT5B', 'numCells': 1000, 'ynorm':[0,1], 'sec': 'spiny', 'loc': 0.5, 'synMech': ['AMPA', 'NMDA'], 'synMechWeightFactor': [0.5, 0.5], 'start': 0, 'interval': 1000.0/40.0, 'noise': 0.5, 'number': 100.0, 'weight': 1.0*0.01, 'delay': 2.}

cfg.NetStim1 = {'pop': 'PT5B', 'numCells': 10, 'ynorm':[0,1], 'sec': 'spiny', 'loc': 0.5, 'synMech': ['AMPA','NMDA'], 'synMechWeightFactor': [0.7, 0.3], 'start': 0, 'rate': 20., 'noise': 0.5, 'number': 100.0, 'weight': 0.5*1e5*0.001, 'delay': 2.}
