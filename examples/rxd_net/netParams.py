from netpyne import specs

from cfg import cfg

#------------------------------------------------------------------------------
#
# NETWORK PARAMETERS
#
#------------------------------------------------------------------------------

netParams = specs.NetParams()  # object of class NetParams to store the network parameters

netParams.sizeX = cfg.sizeX # x-dimension (horizontal length) size in um
netParams.sizeY = cfg.sizeY # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = cfg.sizeZ # z-dimension (horizontal length) size in um
netParams.propVelocity = 100.0 # propagation velocity (um/ms)
netParams.probLengthConst = 150.0 # length constant for conn probability (um)

#------------------------------------------------------------------------------
## Population parameters
netParams.popParams['E2'] = {'cellType': 'E', 'numCells': 10, 'yRange': [50,150], 'cellModel': 'HH'}
netParams.popParams['I2'] = {'cellType': 'I', 'numCells': 10, 'yRange': [50,150], 'cellModel': 'HH'}
netParams.popParams['E4'] = {'cellType': 'E', 'numCells': 10, 'yRange': [150,300], 'cellModel': 'HH'}
netParams.popParams['I4'] = {'cellType': 'I', 'numCells': 10, 'yRange': [150,300], 'cellModel': 'HH'}
netParams.popParams['E5'] = {'cellType': 'E', 'numCells': 10, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}
netParams.popParams['I5'] = {'cellType': 'I', 'numCells': 10, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}

#------------------------------------------------------------------------------
## Cell property rules
netParams.loadCellParamsRule(label='CellRule', fileName='CSTR_cellParams.json')

#------------------------------------------------------------------------------
## Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 5.3, 'e': 0}  # NMDA synaptic mechanism
netParams.synMechParams['inh'] = {'mod': 'Exp2Syn', 'tau1': 0.6, 'tau2': 8.5, 'e': -75}  # GABA synaptic mechanism

#------------------------------------------------------------------------------
# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 25, 'noise': 0.8}
netParams.stimTargetParams['bkg->all'] = {'source': 'bkg', 'conds': {'cellType': ['E','I']}, 'weight': 0.01, 'sec': 'soma', 'delay': 'max(1, normal(5,2))', 'synMech': 'exc'}

#------------------------------------------------------------------------------
## Cell connectivity rules
netParams.connParams['E->all'] = {
  'preConds': {'cellType': 'E'}, 'postConds': {'y': [50,500]},  #  E -> all (100-1000 um)
  'probability': 0.1,                  # probability of connection
  'weight': '0.04*post_ynorm',         # synaptic weight 
  'delay': 'dist_3D/propVelocity',      # transmission delay (ms)
  'sec': ['Adend1', 'Adend2', 'Adend3'], 
  'synMech': 'exc'}                     # synaptic mechanism 

netParams.connParams['I->E'] = {
  'preConds': {'cellType': 'I'}, 'postConds': {'pop': ['E2','E4','E5']},       #  I -> E
  'probability': '0.3*exp(-dist_3D/probLengthConst)',   # probability of connection
  'weight': 0.01,                                      # synaptic weight 
  'delay': 'dist_3D/propVelocity',                      # transmission delay (ms) 
  'sec': ['soma','Bdend'], 
  'synMech': 'inh'}                                     # synaptic mechanism 


#------------------------------------------------------------------------------
## RxD params

### constants
constants = {'ip3_init': cfg.ip3_init,  # initial ip3 concentration 
            'caDiff': 0.08,  # calcium diffusion coefficient
            'ip3Diff': 1.41,  # ip3 diffusion coefficient
            'caci_init': 1e-5,  # intracellular calcium initial concentration
            'caco_init': 2.0,   # extracellular calcium initial concentration
            'gip3r': 12040 * 100,  # ip3 receptors density
            'gserca': 0.3913,  # SERCA conductance
            'gleak': 6.020,   # ER leak channel conductance
            'kserca': 0.1,  # SERCA reaction constant
            'kip3': 0.15,  # ip3 reaction constant
            'kact': 0.4,  #
            'ip3rtau': 2000,  # ip3 receptors time constant
            'fc': 0.8,  # fraction of cytosol
            'fe': 0.2,  # fraction of ER
            'margin': 20}  # extracellular volume additional margin 

netParams.rxdParams['constants'] = constants

### regions
regions = {}
regions['cyt'] = {'cells': 'all', 'secs': 'all', 'nrn_region': 'i', 'geometry': {'class': 'FractionalVolume', 'args': {'volume_fraction': constants['fc'], 'surface_fraction': 1}}}
regions['er'] = {'cells': 'all', 'secs': 'all', 'geometry': {'class': 'FractionalVolume', 'args': {'volume_fraction': constants['fe']}}}
regions['cyt_er_membrane'] = {'cells': 'all', 'secs': 'all', 'geometry': {'class': 'ScalableBorder', 'args': {'scale': 1, 'on_cell_surface': False}}}

margin = 20  # extracellular volume additional margin 
x, y, z = [0-margin, 100+margin], [-500-margin, 0+margin], [0-margin, 100+margin]
regions['ecs'] = {'extracellular': True, 'xlo': x[0], 'ylo': y[0], 'zlo': z[0], 'xhi': x[1], 'yhi': y[1], 'zhi': z[1], 'dx': 5, 'volume_fraction': 0.2, 'tortuosity': 1.6} 

netParams.rxdParams['regions'] = regions

### species 
species = {}
species['ca'] = {'regions': ['cyt', 'er', 'ecs'], 'd': constants['caDiff'], 'charge': 2,
                'initial': 'caco_init if isinstance(node,rxd.node.NodeExtracellular) else (0.0017 - caci_init * fc) / fe if node.region == er else caci_init'}
species['ip3'] = {'regions': ['cyt'], 'd': constants['ip3Diff'], 'initial': constants['ip3_init']}
netParams.rxdParams['species'] = species

### states
netParams.rxdParams['states'] = {'ip3r_gate_state': {'regions': ['cyt_er_membrane'], 'initial': 0.8}}

### reactions
minf = 'ip3[cyt] * 1000. * ca[cyt] / (ip3[cyt] + kip3) / (1000. * ca[cyt] + kact)'
h_gate = 'ip3r_gate_state[cyt_er_membrane]'
kip3 = 'gip3r * (%s * %s) ** 3' % (minf, h_gate)

mcReactions = {}
mcReactions['serca'] = {'reactant': 'ca[cyt]', 'product': 'ca[er]', 'rate_f': 'gserca / ((kserca / (1000. * ca[cyt])) ** 2 + 1)', 'membrane': 'cyt_er_membrane', 'custom_dynamics': True}
mcReactions['leak'] = {'reactant': 'ca[er]', 'product': 'ca[cyt]', 'rate_f': constants['gleak'], 'rate_b': constants['gleak'], 'membrane': 'cyt_er_membrane'}
mcReactions['ip3r'] = {'reactant': 'ca[er]', 'product': 'ca[cyt]', 'rate_f': kip3, 'rate_b': kip3, 'membrane': 'cyt_er_membrane'}
netParams.rxdParams['multicompartmentReactions'] = mcReactions

### rates
netParams.rxdParams['rates'] = {'ip3rg': {'species': h_gate, 'rate': '(1. / (1 + 1000. * ca[cyt] / (0.3)) - %s) / ip3rtau'%(h_gate)}}

