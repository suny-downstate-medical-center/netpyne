from netpyne import specs, sim

netParams = specs.NetParams()

#Create artificial cell with spike times
netParams.popParams['bkg'] = {'cellModel' : 'VecStim', 'numCells': 5, 'spkTimes': [100, 200, 300, 400, 500]}

#Create cell type
netParams.popParams['S'] = {'cellType': 'PYR', 'numCells': 20, 'cellModel': 'HH'}

#Define cell characteristics
cellRule = {'conds': {'cellType': 'PYR'},  'secs': {}}    # cell rule dict
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}                                   # soma params dict
cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}                             # soma geometry
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}        # soma hh mechanisms
cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}                          # dend params dict
cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}                     # dend geometry
cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}                  # dend topology 
cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70}                               # dend mechanisms
netParams.cellParams['PYRrule'] = cellRule
   
#Import synaptic mechanism
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 5.0, 'e': 0}

#Connect artificial cell to regular cells with 100% probability
netParams.connParams['bkg->S'] = {'preConds': {'popLabel': 'bkg'}, 
   'postConds': {'popLabel': 'S'},
   'probability': 1,          # probability of connection
   'weight': 2,          # synaptic weight 
   'delay': 5,               # transmission delay (ms) 
   'sec': 'adend',            # section to connect to
   'loc': 0.5,               # location of synapse
   'synMech': 'exc'}         # target synaptic mechanism
   
#Simulate
simConfig = specs.SimConfig()      # object of class SimConfig to store simulation configuration

simConfig.duration = 1*1e3          # Duration of the simulation, in ms
simConfig.dt = 0.025             # Internal integration timestep to use
simConfig.recordStep = 0.25          # Step size in ms to save data (eg. V traces, LFP, etc)

simConfig.analysis['plotRaster'] = True         # Plot a raster
simConfig.analysis['plot2Dnet']  = True          # plot 2D visualization of cell positions and connections

# Create network and run simulation
sim.createSimulateAnalyze(netParams = netParams, simConfig = simConfig)    
   
import pylab; pylab.show()  # this line is only necessary in certain systems where figures appear empty

