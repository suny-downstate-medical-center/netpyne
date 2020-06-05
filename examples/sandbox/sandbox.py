##Tutorial for NetPyNE
##http://www.netpyne.org/tutorial.html
'''
ALWAYS START WITH
import sys; sys.path.append('/Applications/NEURON-7.7/nrn/lib/python')
ALWAYS END WITH
import pylab; pylab.show()
'''
# import sys; sys.path.append('/Applications/NEURON-7.7/nrn/lib/python')	##ALWAYS KEEP
from netpyne import specs, sim
#nrnivmodl
## Network parameters
netParams = specs.NetParams() # object of class NetParams to store network parameters
## Population parameters
netParams.popParams['S'] = {'cellType': 'PYR', 'numCells':20, 'cellModel': 'HH'}
netParams.popParams['M'] = {'cellType': 'PYR', 'numCells':20, 'cellModel': 'HH'}
#print (netParams.popParams)
## Cell Rules
cellRule = {'conds': {'cellType': 'PYR'},  'secs': {}}	# cell rule dict
cellRule['secs']['soma'] = {'geom': {}, 'mechs': {}}	# soma params dict
cellRule['secs']['soma']['geom'] = {'diam': 18.8, 'L': 18.8, 'Ra': 123.0}	# soma geometry
cellRule['secs']['soma']['mechs']['hh'] = {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}	# soma hh mechanism
cellRule['secs']['dend'] = {'geom': {}, 'topol': {}, 'mechs': {}}	 # dend params dict
cellRule['secs']['dend']['geom'] = {'diam': 5.0, 'L': 150.0, 'Ra': 150.0, 'cm': 1}	# dend geometry
cellRule['secs']['dend']['topol'] = {'parentSec': 'soma', 'parentX': 1.0, 'childX': 0}	# dend topology
cellRule['secs']['dend']['mechs']['pas'] = {'g': 0.0000357, 'e': -70}    # dend mechanism
netParams.cellParams['PYRrule'] = cellRule
##OR
# netParams.cellParams['PYRrule'] = {             # cell rule label
#        'conds': {'cellType': 'PYR'},   # properties will be applied to cells that match these conditions
#        'secs': {'soma':                                        # sections
#                {'geom': {'diam': 18.8, 'L': 18.8, 'Ra': 123.0},                # geometry
#                'mechs': {'hh': {'gnabar': 0.12, 'gkbar': 0.036, 'gl': 0.003, 'el': -70}}}}})   # mechanisms
## Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 1.0, 'tau2': 5.0, 'e': 0}  # excitatory synaptic mechanism
# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 10, 'noise': 0.5}
netParams.stimTargetParams['bkg->PYR'] = {'source': 'bkg', 'conds': {'cellType': 'PYR'}, 'weight': 0.01, 'delay': 5, 'synMech': 'exc'}
## Cell connectivity rules
netParams.connParams['S->M'] = {	#  S -> M label
        'preConds': {'pop': 'S'},	# conditions of presyn cells
        'postConds': {'pop': 'M'},	# conditions of postsyn cells
        'probability': 0.5,		# probability of connection
        'weight': 0.01,			# synaptic weight
        'delay': 5,			# transmission delay (ms)
	    'sec': 'dend',			# section to connect to
	    'loc': 1.0,			# location of synapse
        'synMech': 'exc'}		# synaptic mechanism
## Simulation options
simConfig = specs.SimConfig()		# object of class SimConfig to store simulation configuration
simConfig.duration = 1*1e3		# Duration of the simulation, in ms
simConfig.dt = 0.025			# Internal integration timestep to use
simConfig.verbose = False		# Show detailed messages
simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}	# Dict with traces to record
simConfig.recordStep = 0.1		# Step size in ms to save data (e.g. V traces, LFP, etc)
simConfig.filename = 'model_output'	# Set file output name
simConfig.savePickle = False		# Save params, network and sim output to pickle file
simConfig.analysis['plotRaster'] = True			# Plot a raster
simConfig.analysis['plotTraces'] = {'include': [1]}	# Plot recorded traces for this list of cells
simConfig.analysis['plot2Dnet'] = True			# plot 2D visualization of cell positions and connections
sim.createSimulateAnalyze(netParams, simConfig)