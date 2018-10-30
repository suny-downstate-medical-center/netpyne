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

## Population parameters
netParams.popParams['E2'] = {'cellType': 'E', 'numCells': 10, 'yRange': [50,150], 'cellModel': 'HH'}
netParams.popParams['I2'] = {'cellType': 'I', 'numCells': 10, 'yRange': [50,150], 'cellModel': 'HH'}
netParams.popParams['E4'] = {'cellType': 'E', 'numCells': 10, 'yRange': [150,300], 'cellModel': 'HH'}
netParams.popParams['I4'] = {'cellType': 'I', 'numCells': 10, 'yRange': [150,300], 'cellModel': 'HH'}
netParams.popParams['E5'] = {'cellType': 'E', 'numCells': 10, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}
netParams.popParams['I5'] = {'cellType': 'I', 'numCells': 10, 'ynormRange': [0.6,1.0], 'cellModel': 'HH'}

## Cell property rules
netParams.loadCellParamsRule(label='CellRule', fileName='CSTR_cellParams.json')

## Synaptic mechanism parameters
netParams.synMechParams['exc'] = {'mod': 'Exp2Syn', 'tau1': 0.8, 'tau2': 5.3, 'e': 0}  # NMDA synaptic mechanism
netParams.synMechParams['inh'] = {'mod': 'Exp2Syn', 'tau1': 0.6, 'tau2': 8.5, 'e': -75}  # GABA synaptic mechanism

# Stimulation parameters
netParams.stimSourceParams['bkg'] = {'type': 'NetStim', 'rate': 20, 'noise': 0.3}
netParams.stimTargetParams['bkg->all'] = {'source': 'bkg', 'conds': {'cellType': ['E','I']}, 'weight': 0.01, 'sec': 'soma', 'delay': 'max(1, normal(5,2))', 'synMech': 'exc'}

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


## RxD params

### constants
constants = {'ip3_init': 0.0,  # Change value between 0 and 1: high ip3 -> ER Ca released to Cyt -> kBK channels open -> less firing
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
netParams.rxdParams['regions'] = {}
netParams.rxdParams['regions']['cyt'] = {'cells': 'all', 
                                        'secs': 'all',
                                        'nrn_region': 'i', 
                                        'geometry': {'class': 'FractionalVolume', 'args': {'volume_fraction': constants['fc'], 'surface_fraction': 1}}}

netParams.rxdParams['regions']['er'] = {'cells': 'all', 
                                        'secs': 'all',
                                        'geometry': {'class': 'FractionalVolume', 'args': {'volume_fraction': constants['fe']}}}

netParams.rxdParams['regions']['cyt_er_membrane'] = {'cells': 'all', 
                                                    'secs': 'all',
                                                    'geometry': {'class': 'ScalableBorder', 'args': {'volume_fraction': 1, 'on_cell_surface': False}}}

### species
netParams.rxdParams['species'] = {}
netParams.rxdParams['species']['ca'] = {'regions': ['cyt'], 
                                        'd': constants['caDiff'], 
                                        'charge': 2,
                                        'initial': 'caco_init if isinstance(node,rxd.node.NodeExtracellular) else (0.0017 - caci_init * fc) / fe if node.region == er else caci_init'}
netParams.rxdParams['species']['ip3'] = {'regions': ['cyt'], 
                                        'd': constants['ip3Diff'], 
                                        'initial': constants['ip3_init']}


### reactions
netParams.rxdParams['multicompartmentReactions']['ca_leak'] = {'reactant': 'ca[er]', 
                                                                'product': 'ca[cyt]',
                                                                'rate_f': constants['gleak'], 
                                                                'rate_b': constants['gleak'],
                                                                'membrante': 'cyt_er_membrane'}

# leak = rxd.MultiCompartmentReaction(ca[er], ca[cyt], gleak, gleak, membrane=cyt_er_membrane)


# # ---------------------
# # rxd intracellular and extracellular
# # ---------------------

# rxd.nthread(4)

# # parameters
# ip3_init = 0.0  # Change value between 0 and 1: high ip3 -> ER Ca released to Cyt -> kBK channels open -> less firing
# caDiff = 0.08  # calcium diffusion coefficient
# ip3Diff = 1.41  # ip3 diffusion coefficient
# caci_init = 1e-5  # intracellular calcium initial concentration
# caco_init = 2.0   # extracellular calcium initial concentration
# gip3r = 12040 * 100  # ip3 receptors density
# gserca = 0.3913  # SERCA conductance
# gleak = 6.020   # ER leak channel conductance
# kserca = 0.1  # SERCA reaction constant
# kip3 = 0.15  # ip3 reaction constant
# kact = 0.4  #
# ip3rtau = 2000  # ip3 receptors time constant
# fc = 0.8  # fraction of cytosol
# fe = 0.2  # fraction of ER
# margin = 20  # extracellular volume additional margin 
# x, y, z = [0-margin, 100+margin], [-500-margin, 0+margin], [0-margin, 100+margin]

# # create intracellular region
# cyt = rxd.Region(h.allsec(), nrn_region='i', geometry=rxd.FractionalVolume(fc, surface_fraction=1))
# er = rxd.Region(h.allsec(), geometry=rxd.FractionalVolume(fe))
# cyt_er_membrane = rxd.Region(h.allsec(), geometry=rxd.ScalableBorder(1, on_cell_surface=False))

# # create extracellular region
# rxd.options.enable.extracellular = True
# extracellular = rxd.Extracellular(xlo=x[0], ylo=y[0], zlo=z[0], xhi=x[1], yhi=y[1], zhi=z[1], dx=5, volume_fraction=0.2, tortuosity=1.6) #vol_fraction and tortuosity associated w region 

# # create Species 
# ca = rxd.Species([cyt, er, extracellular], d=caDiff, name='ca', charge=2, 
#       initial=lambda nd: caco_init if isinstance(nd,rxd.node.NodeExtracellular) else (0.0017 - caci_init * fc) / fe if nd.region == er else caci_init)
# ip3 = rxd.Species(cyt, d=ip3Diff, name='ip3', initial=ip3_init)
# ip3r_gate_state = rxd.State(cyt_er_membrane, initial=0.8)

# # create Reactions 
# serca = rxd.MultiCompartmentReaction(ca[cyt], ca[er], gserca / ((kserca / (1000. * ca[cyt])) ** 2 + 1), membrane=cyt_er_membrane, custom_dynamics=True)
# leak = rxd.MultiCompartmentReaction(ca[er], ca[cyt], gleak, gleak, membrane=cyt_er_membrane)

# minf = ip3[cyt] * 1000. * ca[cyt] / (ip3[cyt] + kip3) / (1000. * ca[cyt] + kact)
# h_gate = ip3r_gate_state[cyt_er_membrane]
# kip3 = gip3r * (minf * h_gate) ** 3
# ip3r = rxd.MultiCompartmentReaction(ca[er], ca[cyt], kip3, kip3, membrane=cyt_er_membrane)
# ip3rg = rxd.Rate(h_gate, (1. / (1 + 1000. * ca[cyt] / (0.3)) - h_gate) / ip3rtau)

