
"""
netParams.py 

High-level specifications for M1 network model using NetPyNE

Contributors: salvadordura@gmail.com
"""

from netpyne import specs
import pickle, json

netParams = specs.NetParams()   # object of class NetParams to store the network parameters

netParams.version = 49

try:
	from __main__ import cfg  # import SimConfig object with params from parent module
except:
	from cfg import cfg

#------------------------------------------------------------------------------
#
# NETWORK PARAMETERS
#
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# General connectivity parameters
#------------------------------------------------------------------------------
netParams.defaultThreshold = 0.0 # spike threshold, 10 mV is NetCon default, lower it for all cells
netParams.defaultDelay = 2.0 # default conn delay (ms)
netParams.propVelocity = 500.0 # propagation velocity (um/ms)
netParams.probLambda = 100.0  # length constant (lambda) for connection probability decay (um)
netParams.sizeX = 500
netParams.sizeY = 1350  # cortical depth (will be converted to negative values)
netParams.sizeZ = 20


#------------------------------------------------------------------------------
# Cell parameters
#------------------------------------------------------------------------------
cellModels = ['HH_simple', 'HH_reduced', 'HH_full']
layer = {'2': [0.12,0.31], '4': [0.31,0.42], '5A': [0.42,0.52], '45A':[0.31,0.52], '5B': [0.73,0.77], '6': [0.77,1.0], 'long': [2.0,3.0]}  # normalized layer boundaries

#------------------------------------------------------------------------------
## Load cell rules previously saved using netpyne format
cellParamLabels = [] # ['PT5B_full'] #  # list of cell rules to load from file
loadCellParams = cellParamLabels
saveCellParams = False #True

for ruleLabel in loadCellParams:
	netParams.loadCellParamsRule(label=ruleLabel, fileName='cells/'+ruleLabel+'_cellParams.pkl')

#------------------------------------------------------------------------------
# Specification of cell rules not previously loaded
# Includes importing from hoc template or python class, and setting additional params

#------------------------------------------------------------------------------
## PT5B full cell model params (700+ comps)
if 'PT5B_full' not in loadCellParams:
	ihMod2str = {'harnett': 1, 'kole': 2, 'migliore': 3}
	cellRule = netParams.importCellParams(label='PT5B_full', conds={'cellType': 'PT', 'cellModel': 'HH_full'},
	  fileName='cells/PTcell.hoc', cellName='PTcell', cellArgs=[ihMod2str[cfg.ihModel], cfg.ihSlope], somaAtOrigin=True)
	nonSpiny = ['apic_0', 'apic_1']
	netParams.addCellParamsSecList(label='PT5B_full', secListName='perisom', somaDist=[0, 50])  # sections within 50 um of soma
	netParams.addCellParamsSecList(label='PT5B_full', secListName='below_soma', somaDistY=[-600, 0])  # sections within 0-300 um of soma
	for sec in nonSpiny: cellRule['secLists']['perisom'].remove(sec)
	cellRule['secLists']['alldend'] = [sec for sec in cellRule.secs if ('dend' in sec or 'apic' in sec)] # basal+apical
	cellRule['secLists']['apicdend'] = [sec for sec in cellRule.secs if ('apic' in sec)] # apical
	cellRule['secLists']['spiny'] = [sec for sec in cellRule['secLists']['alldend'] if sec not in nonSpiny]
	# Adapt ih params based on cfg param
	for secName in cellRule['secs']:
		for mechName,mech in cellRule['secs'][secName]['mechs'].iteritems():
			if mechName in ['ih','h','h15', 'hd']: 
				mech['gbar'] = [g*cfg.ihGbar for g in mech['gbar']] if isinstance(mech['gbar'],list) else mech['gbar']*cfg.ihGbar
				if cfg.ihModel == 'migliore':   
					mech['clk'] = cfg.ihlkc  # migliore's shunt current factor
					mech['elk'] = cfg.ihlke  # migliore's shunt current reversal potential
				if secName.startswith('dend'): 
					mech['gbar'] *= cfg.ihGbarBasal  # modify ih conductance in soma+basal dendrites
					mech['clk'] *= cfg.ihlkcBasal  # modify ih conductance in soma+basal dendrites
				if secName in cellRule['secLists']['below_soma']: #secName.startswith('dend'): 
					mech['clk'] *= cfg.ihlkcBelowSoma  # modify ih conductance in soma+basal dendrites
	# Reduce dend Na to avoid dend spikes (compensate properties by modifying axon params)
	for secName in cellRule['secLists']['alldend']:
		cellRule['secs'][secName]['mechs']['nax']['gbar'] = 0.0153130368342 * cfg.dendNa # 0.25 
	cellRule['secs']['soma']['mechs']['nax']['gbar'] = 0.0153130368342  * cfg.somaNa
	cellRule['secs']['axon']['mechs']['nax']['gbar'] = 0.0153130368342  * cfg.axonNa # 11  
	cellRule['secs']['axon']['geom']['Ra'] = 137.494564931 * cfg.axonRa # 0.005
	# Remove Na (TTX)
	if cfg.removeNa:
		for secName in cellRule['secs']: cellRule['secs'][secName]['mechs']['nax']['gbar'] = 0.0
	netParams.addCellParamsWeightNorm('PT5B_full', 'conn/PT5B_full_weightNorm.pkl', threshold=cfg.weightNormThreshold)  # load weight norm
	netParams.saveCellParamsRule(label='PT5B_full', fileName='cells/PT5B_full_cellParams.pkl')


#------------------------------------------------------------------------------
# Population parameters
#------------------------------------------------------------------------------
cellsList = [{'x': x} for x in [20, 37, 45, 60, 87, 90, 119, 135, 160, 188, 202, 205, 238, 265, 275]]
netParams.popParams['PT5B'] = {'cellModel': 'HH_full', 'cellType': 'PT', 'ynormRange': layer['5B'], 'cellsList': cellsList} # numCells':20}

#------------------------------------------------------------------------------
# Synaptic mechanism parameters
#------------------------------------------------------------------------------
netParams.synMechParams['NMDA'] = {'mod': 'MyExp2SynNMDABB', 'tau1NMDA': 15, 'tau2NMDA': 150, 'e': 0}
netParams.synMechParams['AMPA'] = {'mod':'MyExp2SynBB', 'tau1': 0.05, 'tau2': 5.3*cfg.AMPATau2Factor, 'e': 0}
netParams.synMechParams['GABAB'] = {'mod':'MyExp2SynBB', 'tau1': 3.5, 'tau2': 260.9, 'e': -93} 
netParams.synMechParams['GABAA'] = {'mod':'MyExp2SynBB', 'tau1': 0.07, 'tau2': 18.2, 'e': -80}
netParams.synMechParams['GABAASlow'] = {'mod': 'MyExp2SynBB','tau1': 2, 'tau2': 100, 'e': -80}

ESynMech = ['AMPA', 'NMDA']
SOMESynMech = ['GABAASlow','GABAB']
PVSynMech = ['GABAA']

#------------------------------------------------------------------------------
# Current inputs (IClamp)
#------------------------------------------------------------------------------
if cfg.addIClamp:
 	for key in [k for k in dir(cfg) if k.startswith('IClamp')]:
		params = getattr(cfg, key, None)
		[pop,sec,loc,start,dur,amp] = [params[s] for s in ['pop','sec','loc','start','dur','amp']]

		#cfg.analysis['plotTraces']['include'].append((pop,0))  # record that pop

		# add stim source
		netParams.stimSourceParams[key] = {'type': 'IClamp', 'delay': start, 'dur': dur, 'amp': amp}
		
		# connect stim source to target
		netParams.stimTargetParams[key+'_'+pop] =  {
			'source': key, 
			'conds': {'pop': pop},
			'sec': sec, 
			'loc': loc}

#------------------------------------------------------------------------------
# NetStim inputs
#------------------------------------------------------------------------------
if cfg.addNetStim:
    for key in [k for k in dir(cfg) if k.startswith('NetStim')]:
    	params = getattr(cfg, key, None)
    	[pop, ynorm, sec, loc, synMech, synMechWeightFactor, start, interval, noise, number, weight, delay] = \
    	[params[s] for s in ['pop', 'ynorm', 'sec', 'loc', 'synMech', 'synMechWeightFactor', 'start', 'interval', 'noise', 'number', 'weight', 'delay']] 

        if synMech == ESynMech:
            wfrac = cfg.synWeightFractionEE
        elif synMech == SOMESynMech:
            wfrac = cfg.synWeightFractionSOME
        else:
            wfrac = [1.0]

        # add stim source
        netParams.stimSourceParams[key] = {'type': 'NetStim', 'start': start, 'interval': interval, 'noise': noise, 'number': number}

        # connect stim source to target
        # for i, syn in enumerate(synMech):
        netParams.stimTargetParams[key+'_'+pop] =  {
            'source': key, 
            'conds': {'pop': pop, 'ynorm': ynorm},
            'sec': sec, 
            'loc': loc,
            'synMech': synMech,
            'weight': weight,
            'synMechWeightFactor': synMechWeightFactor,
            'delay': delay}


#------------------------------------------------------------------------------
# Subcellular connectivity (synaptic distributions)
#------------------------------------------------------------------------------   		
if cfg.addSubConn:
	with open('conn/conn_dend_PT.json', 'r') as fileObj: connDendPTData = json.load(fileObj)
	
	#------------------------------------------------------------------------------
	# Use subcellular distribution from L2/3 -> PT (Suter, 2015)
	lenY = 30 
	spacing = 50
	gridY = range(0, -spacing*lenY, -spacing)
	synDens, _, fixedSomaY = connDendPTData['synDens'], connDendPTData['gridY'], connDendPTData['fixedSomaY']

	netParams.subConnParams['L2->PT'] = {
	'preConds': {'cellType': 'NetStim'}, # all presyn inputs 
	'postConds': {'cellType': 'PT5B'},  
	'sec': 'spiny',
	'groupSynMechs': ESynMech, 
	'density': {'type': '1Dmap', 'gridX': None, 'gridY': gridY, 'gridValues': synDens['L2_PT'], 'fixedSomaY': fixedSomaY}} 

