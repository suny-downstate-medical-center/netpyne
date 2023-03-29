from netpyne import specs

try:
    from __main__ import cfg  # import SimConfig object with params from parent module
except:
    from cfg import cfg

#------------------------------------------------------------------------------
#
# NETWORK PARAMETERS
#
#------------------------------------------------------------------------------

netParams = specs.NetParams()  # object of class NetParams to store the network parameters

netParams.sizeX = cfg.sizeX# - 2*cfg.somaR # x-dimension (horizontal length) size in um
netParams.sizeY = cfg.sizeY# - 2*cfg.somaR # y-dimension (vertical height or cortical depth) size in um
netParams.sizeZ = cfg.sizeZ# - 2*cfg.somaR # z-dimension (horizontal length) size in um
netParams.propVelocity = 100.0     # propagation velocity (um/ms)
netParams.probLengthConst = 150.0  # length constant for conn probability (um)

#------------------------------------------------------------------------------
## Population parameters
netParams.popParams['E'] = {'cellType': 'E', 'numCells': cfg.Ncell, 
    'xRange': [0.0, cfg.sizeX], 
    'yRange': [2 *cfg.somaR, cfg.sizeY - 2 *cfg.somaR],
    'zRange': [0.0, cfg.sizeZ], 'cellModel': 'rxdE'}

#------------------------------------------------------------------------------
## Cell property rules
Erule = netParams.importCellParams(label='Erule', fileName='cells/Neuron.py', 
                conds={'cellType' : 'E', 'cellModel' : 'rxdE'}, cellName='ENeuron')
netParams.cellParams['Erule'] = Erule      

#------------------------------------------------------------------------------
## RxD params

### constants
from neuron.units import sec, mM
import math 

e_charge =  1.60217662e-19
scale = 1e-14/e_charge
alpha = 5.3
constants = {'e_charge' : e_charge,
            'scale' : scale,
            'gnabar' : (30/1000) * scale,     # molecules/um2 ms mV ,
            'gnabar_l' : (0.0247/1000) * scale,
            'gkbar' : (25/1000) * scale,
            'gkbar_l' : (0.05/1000) * scale,
            'gclbar_l' : (0.1/1000) * scale,
            'ukcc2' : 0.3 * mM/sec ,
            'unkcc1' : 0.1 * mM/sec ,
            'alpha' : alpha,
            'epsilon_k_max' : 0.25/sec,
            'epsilon_o2' : 0.17/sec,
            'vtau' : 1/250.0,
            'g_gliamax' : 5 * mM/sec,
            'beta0' : 7.0,
            'avo' : 6.0221409*(10**23),
            'p_max' : 0.8, # * mM/sec,
            'nao_initial' : 144.0,
            'nai_initial' : 18.0,
            'gnai_initial' : 18.0,
            'gki_initial' : 80.0,
            'ko_initial' : 3.5,
            'ki_initial' : 140.0,
            'clo_initial' : 130.0,
            'cli_initial' : 6.0,
            'o2_bath' : cfg.o2_bath,
            'v_initial' : -70.0,
            'r0' : 100.0, 
            'k0' : 70.0}

#sodium activation 'm'
alpha_m = "(0.32 * (rxd.v + 54.0))/(1.0 - rxd.rxdmath.exp(-(rxd.v + 54.0)/4.0))"
beta_m = "(0.28 * (rxd.v + 27.0))/(rxd.rxdmath.exp((rxd.v + 27.0)/5.0) - 1.0)"
alpha_m0 =(0.32 * (constants['v_initial'] + 54.0))/(1.0 - math.exp(-(constants['v_initial'] + 54)/4.0))
beta_m0 = (0.28 * (constants['v_initial'] + 27.0))/(math.exp((constants['v_initial'] + 27.0)/5.0) - 1.0)
m_initial = alpha_m0/(beta_m0 + 1.0)

#sodium inactivation 'h'
alpha_h = "0.128 * rxd.rxdmath.exp(-(rxd.v + 50.0)/18.0)"
beta_h = "4.0/(1.0 + rxd.rxdmath.exp(-(rxd.v + 27.0)/5.0))"
alpha_h0 = 0.128 * math.exp(-(constants['v_initial'] + 50.0)/18.0)
beta_h0 = 4.0/(1.0 + math.exp(-(constants['v_initial'] + 27.0)/5.0))
h_initial = alpha_h0/(beta_h0 + 1.0)

#potassium activation 'n'
alpha_n = "(0.032 * (rxd.v + 52.0))/(1.0 - rxd.rxdmath.exp(-(rxd.v + 52.0)/5.0))"
beta_n = "0.5 * rxd.rxdmath.exp(-(rxd.v + 57.0)/40.0)"
alpha_n0 = (0.032 * (constants['v_initial'] + 52.0))/(1.0 - math.exp(-(constants['v_initial'] + 52.0)/5.0))
beta_n0 = 0.5 * math.exp(-(constants['v_initial'] + 57.0)/40.0)
n_initial = alpha_n0/(beta_n0 + 1.0)

netParams.rxdParams['constants'] = constants

### regions
regions = {}

#### ecs dimensions 
# margin = cfg.somaR
x = [0, cfg.sizeX]
y = [-cfg.sizeY, 0]
z = [0, cfg.sizeZ]

regions['ecs'] = {'extracellular' : True, 'xlo' : x[0],
                                          'xhi' : x[1],
                                          'ylo' : y[0],
                                          'yhi' : y[1],
                                          'zlo' : z[0],
                                          'zhi' : z[1],
                                          'dx' : 25,
                                          'volume_fraction' : cfg.alpha_ecs,
                                          'tortuosity' : cfg.tort_ecs}

regions['ecs_o2'] = {'extracellular' : True, 'xlo' : x[0],
                                            'xhi' : x[1],
                                            'ylo' : y[0],
                                            'yhi' : y[1],
                                            'zlo' : z[0],
                                            'zhi' : z[1],
                                            'dx' : 25,
                                            'volume_fraction' : 1.0,
                                            'tortuosity' : 1.0}
                                          
regions['cyt'] = {'cells': 'all', 'secs': 'all', 'nrn_region': 'i', 
                'geometry': {'class': 'FractionalVolume', 
                'args': {'volume_fraction': cfg.cyt_fraction, 'surface_fraction': 1}}}

regions['mem'] = {'cells' : 'all', 'secs' : 'all', 'nrn_region' : None, 'geometry' : 'membrane'}

netParams.rxdParams['regions'] = regions

### species 
species = {}

k_init_str = 'ki_initial if isinstance(node, rxd.node.Node1D) else (%f if ((node.x3d - %f/2)**2+(node.y3d + %f/2)**2+(node.z3d - %f/2)**2 <= %f**2) else ko_initial)' % (cfg.k0, cfg.sizeX, cfg.sizeY, cfg.sizeZ, cfg.r0)
species['k'] = {'regions' : ['cyt', 'mem', 'ecs'], 'd' : 2.62, 'charge' : 1,
                'initial' : k_init_str,
                'ecs_boundary_conditions' : constants['ko_initial'], 'name' : 'k'}

species['na'] = {'regions' : ['cyt', 'mem', 'ecs'], 'd' : 1.78, 'charge' : 1,
                'initial' : 'nai_initial if isinstance(node, rxd.node.Node1D) else nao_initial',
                'ecs_boundary_conditions': constants['nao_initial'], 'name' : 'na'}

species['cl'] = {'regions' : ['cyt', 'mem', 'ecs'], 'd' : 2.1, 'charge' : -1,
                'initial' : 'cli_initial if isinstance(node, rxd.node.Node1D) else clo_initial',
                'ecs_boundary_conditions' : constants['clo_initial'], 'name' : 'cl'}

species['o2_extracellular'] = {'regions' : ['ecs_o2'], 'd' : 3.3, 'initial' : constants['o2_bath'],
                'ecs_boundary_conditions' : constants['o2_bath'], 'name' : 'o2'}

netParams.rxdParams['species'] = species

### parameters
params = {}
params['dump'] = {'regions' : ['cyt', 'ecs', 'ecs_o2'], 'name' : 'dump'}

params['ecsbc'] = {'regions' : ['ecs', 'ecs_o2'], 'name' : 'ecsbc', 'value' :
    '1 if (abs(node.x3d - ecs._xlo) < ecs._dx[0] or abs(node.x3d - ecs._xhi) < ecs._dx[0] or abs(node.y3d - ecs._ylo) < ecs._dx[1] or abs(node.y3d - ecs._yhi) < ecs._dx[1] or abs(node.z3d - ecs._zlo) < ecs._dx[2] or abs(node.z3d - ecs._zhi) < ecs._dx[2]) else 0'}

netParams.rxdParams['parameters'] = params

### states
netParams.rxdParams['states'] = {'vol_ratio' : {'regions' : ['cyt', 'ecs'], 'initial' : 1.0, 'name': 'volume'}, 
                                'mgate' : {'regions' : ['cyt', 'mem'], 'initial' : m_initial, 'name' : 'mgate'},
                                'hgate' : {'regions' : ['cyt', 'mem'], 'initial' : h_initial, 'name' : 'hgate'},
                                'ngate' : {'regions' : ['cyt', 'mem'], 'initial' : n_initial, 'name' : 'ngate'}}

### reactions
gna = "gnabar*mgate**3*hgate"
gk = "gkbar*ngate**4"
fko = "1.0 / (1.0 + rxd.rxdmath.exp(16.0 - k[ecs] / vol_ratio[ecs]))"
nkcc1A = "rxd.rxdmath.log((k[cyt] * cl[cyt] / vol_ratio[cyt]**2) / (k[ecs] * cl[ecs] / vol_ratio[ecs]**2))"
nkcc1B = "rxd.rxdmath.log((na[cyt] * cl[cyt] / vol_ratio[cyt]**2) / (na[ecs] * cl[ecs] / vol_ratio[ecs]**2))"
nkcc1 = "unkcc1 * (%s) * (%s+%s)" % (fko, nkcc1A, nkcc1B)
kcc2 = "ukcc2 * rxd.rxdmath.log((k[cyt] * cl[cyt] * vol_ratio[cyt]**2) / (k[ecs] * cl[ecs] * vol_ratio[ecs]**2))"

#Nerst equation - reversal potentials
ena = "26.64 * rxd.rxdmath.log(na[ecs]*vol_ratio[cyt]/(na[cyt]*vol_ratio[ecs]))"
ek = "26.64 * rxd.rxdmath.log(k[ecs]*vol_ratio[cyt]/(k[cyt]*vol_ratio[ecs]))"
ecl = "26.64 * rxd.rxdmath.log(cl[cyt]*vol_ratio[ecs]/(cl[ecs]*vol_ratio[cyt]))"

o2ecs = "o2_extracellular[ecs_o2]"
o2switch = "(1.0 + rxd.rxdmath.tanh(1e4 * (%s - 5e-4))) / 2.0" % (o2ecs)
p = "%s * p_max / (1.0 + rxd.rxdmath.exp((20.0 - (%s/vol_ratio[ecs]) * alpha)/3.0))" % (o2switch, o2ecs)
pumpA = "(%s / (1.0 + rxd.rxdmath.exp((25.0 - na[cyt] / vol_ratio[cyt])/3.0)))" % (p)
pumpB = "(1.0 / (1.0 + rxd.rxdmath.exp(3.5 - k[ecs] / vol_ratio[ecs])))"
pump = "(%s) * (%s)" % (pumpA, pumpB)
gliapump = "(1.0/3.0) * (%s / (1.0 + rxd.rxdmath.exp((25.0 - gnai_initial) / 3.0))) * (1.0 / (1.0 + rxd.rxdmath.exp(3.5 - k[ecs]/vol_ratio[ecs])))" % (p)
g_glia = "g_gliamax / (1.0 + rxd.rxdmath.exp(-((%s)*alpha/vol_ratio[ecs] - 2.5)/0.2))" % (o2ecs)
glia12 = "(%s) / (1.0 + rxd.rxdmath.exp((18.0 - k[ecs] / vol_ratio[ecs])/2.5))" % (g_glia)

# epsilon_k = "(epsilon_k_max/(1.0 + rxd.rxdmath.exp(-(((%s)/vol_ratio[ecs]) * alpha - 2.5)/0.2))) * (1.0/(1.0 + rxd.rxdmath.exp((-20 + ((1.0+1.0/beta0 -vol_ratio[ecs])/vol_ratio[ecs]) /2.0))))" % (o2ecs)
epsilon_kA = "(epsilon_k_max/(1.0 + rxd.rxdmath.exp(-((%s/vol_ratio[ecs]) * alpha - 2.5)/0.2)))" % (o2ecs)
epsilon_kB = "(1.0/(1.0 + rxd.rxdmath.exp((-20 + ((1.0+1.0/beta0 - vol_ratio[ecs])/vol_ratio[ecs]) /2.0))))"
epsilon_k = '%s * %s' % (epsilon_kA, epsilon_kB)


volume_scale = "1e-18 * avo * %f" % (1.0 / cfg.sa2v)

avo = 6.0221409*(10**23)
osm = "(1.1029 - 0.1029*rxd.rxdmath.exp( ( (na[ecs] + k[ecs] + cl[ecs] + 18.0)/vol_ratio[ecs] - (na[cyt] + k[cyt] + cl[cyt] + 132.0)/vol_ratio[cyt])/20.0))"
scalei = str(avo * 1e-18)
scaleo = str(avo * 1e-18)

### reactions
mcReactions = {}

## volume dynamics
mcReactions['vol_dyn'] = {'reactant' : 'vol_ratio[cyt]', 'product' : 'dump[ecs]', 
                        'rate_f' : "-1 * (%s) * vtau * ((%s) - vol_ratio[cyt])" % (scalei, osm), 
                        'membrane' : 'mem', 'custom_dynamics' : True,
                        'scale_by_area' : False}
                        
mcReactions['vol_dyn_ecs'] = {'reactant' : 'dump[cyt]', 'product' : 'vol_ratio[ecs]', 
                            'rate_f' : "-1 * (%s) * vtau * ((%s) - vol_ratio[cyt])" % (scaleo, osm), 
                            'membrane' : 'mem', 'custom_dynamics' : True, 
                            'scale_by_area' : False}

# # CURRENTS/LEAKS ----------------------------------------------------------------
# sodium (Na) current
mcReactions['na_current'] = {'reactant' : 'na[cyt]', 'product' : 'na[ecs]', 
                            'rate_f' : "%s * (rxd.v - %s )" % (gna, ena),
                            'membrane' : 'mem', 'custom_dynamics' : True, 'membrane_flux' : True}

# potassium (K) current
mcReactions['k_current'] = {'reactant' : 'k[cyt]', 'product' : 'k[ecs]', 
                            'rate_f' : "%s * (rxd.v - %s)" % (gk, ek), 
                            'membrane' : 'mem', 'custom_dynamics' : True, 'membrane_flux' : True}

# nkcc1 (Na+/K+/2Cl- cotransporter)
mcReactions['nkcc1_current1'] = {'reactant': 'cl[cyt]', 'product': 'cl[ecs]', 
                                'rate_f': "2.0 * (%s) * (%s)" % (nkcc1, volume_scale), 
                                'membrane': 'mem', 'custom_dynamics' : True, 'membrane_flux' : True}

mcReactions['nkcc1_current2'] = {'reactant': 'k[cyt]', 'product': 'k[ecs]',
                                'rate_f': "%s * %s" % (nkcc1, volume_scale), 
                                'membrane': 'mem', 'custom_dynamics' : True, 'membrane_flux' : True}

mcReactions['nkcc1_current3'] = {'reactant': 'na[cyt]', 'product': 'na[ecs]', 
                                'rate_f': "%s * %s" % (nkcc1, volume_scale), 
                                'membrane': 'mem', 'custom_dynamics' : True, 'membrane_flux' : True}

# ## kcc2 (K+/Cl- cotransporter)
mcReactions['kcc2_current1'] = {'reactant' : 'cl[cyt]', 'product': 'cl[ecs]', 
                                'rate_f': "%s * %s" % (kcc2, volume_scale), 
                                'membrane' : 'mem', 'custom_dynamics' : True, 'membrane_flux' : True}

mcReactions['kcc2_current2'] = {'reactant' : 'k[cyt]', 'product' : 'k[ecs]', 
                                'rate_f': "%s * %s" % (kcc2, volume_scale), 
                                'membrane' : 'mem', 'custom_dynamics' : True, 'membrane_flux' : True}

## sodium leak
mcReactions['na_leak'] = {'reactant' : 'na[cyt]', 'product' : 'na[ecs]', 
                        'rate_f' : "gnabar_l * (rxd.v - %s)" % (ena), 
                        'membrane' : 'mem', 'custom_dynamics' : True, 'membrane_flux' : True}

# ## potassium leak
mcReactions['k_leak'] = {'reactant' : 'k[cyt]', 'product' : 'k[ecs]', 
                        'rate_f' : "gkbar_l * (rxd.v - %s)" % (ek), 
                        'membrane' : 'mem', 'custom_dynamics' : True, 'membrane_flux' : True}

# ## chlorine (Cl) leak 
mcReactions['cl_current'] = {'reactant' : 'cl[cyt]', 'product' : 'cl[ecs]', 
                            'rate_f' : "gclbar_l * (%s - rxd.v)" % (ecl), 
                            'membrane' : 'mem', 'custom_dynamics' : True, 'membrane_flux' : True} 

# ## Na+/K+ pump current in neuron (2K+ in, 3Na+ out)
mcReactions['pump_current'] = {'reactant' : 'k[cyt]', 'product' : 'k[ecs]', 
                            'rate_f' : "-2.0 * %s * %s" % (pump, volume_scale), 
                            'membrane' : 'mem', 'custom_dynamics' : True, 'membrane_flux' : True}

mcReactions['pump_current_na'] = {'reactant' : 'na[cyt]', 'product' : 'na[ecs]', 
                                'rate_f' : "3.0 * %s * %s" % (pump, volume_scale), 
                                'membrane' : 'mem', 'custom_dynamics' : True, 'membrane_flux' : True}

# O2 depletrion from Na/K pump in neuron
mcReactions['oxygen'] = {'reactant' : o2ecs, 'product' : 'dump[cyt]', 
                        'rate_f' : "(%s) * (%s)" % (pump, volume_scale), 
                        'membrane' : 'mem', 'custom_dynamics' : True}

netParams.rxdParams['multicompartmentReactions'] = mcReactions

#RATES--------------------------------------------------------------------------
rates = {}
## dm/dt
rates['m_gate'] = {'species' : 'mgate', 'regions' : ['cyt', 'mem'],
    'rate' : "((%s) * (1.0 - mgate)) - ((%s) * mgate)" % (alpha_m, beta_m)}

## dh/dt
rates['h_gate'] = {'species' : 'hgate', 'regions' : ['cyt', 'mem'],
    'rate' : "((%s) * (1.0 - hgate)) - ((%s) * hgate)" % (alpha_h, beta_h)}

## dn/dt
rates['n_gate'] = {'species' : 'ngate', 'regions' : ['cyt', 'mem'],
    'rate' : '((%s) * (1.0 - ngate)) - ((%s) * ngate)' % (alpha_n, beta_n)}

## diffusion
rates['o2diff'] = {'species' : o2ecs, 'regions' : ['ecs_o2'],
    'rate' : 'ecsbc * (epsilon_o2 * (o2_bath - %s/vol_ratio[ecs]))' % (o2ecs)}

rates['kdiff'] = {'species' : 'k[ecs]', 'regions' : ['ecs'],
    'rate' : 'ecsbc * ((%s) * (ko_initial - k[ecs]/vol_ratio[ecs]))' % (epsilon_k)}

rates['nadiff'] = {'species' : 'na[ecs]', 'regions' : ['ecs'],
    'rate' : 'ecsbc * ((%s) * (nao_initial - na[ecs]/vol_ratio[ecs]))' % (epsilon_k)}

rates['cldiff'] = {'species' : 'cl[ecs]', 'regions' : ['ecs'],
    'rate' : 'ecsbc * ((%s) * (clo_initial - cl[ecs]/vol_ratio[ecs]))' % (epsilon_k)}

## Glia K+/Na+ pump current 
rates['glia_k_current'] = {'species' : 'k[ecs]', 'regions' : ['ecs'],
    'rate' : '-(%s) - (2.0 * (%s))' % (glia12, gliapump)}

rates['glia_na_current'] = {'species' : 'na[ecs]', 'regions' : ['ecs'],
    'rate' : '3.0 * (%s)' % (gliapump)}

## Glial O2 depletion 
rates['o2_pump'] = {'species' : o2ecs, 'regions' : ['ecs'],
    'rate' : '-(%s)' % (gliapump)}

netParams.rxdParams['rates'] = rates

# netpyne v0.00 - first working version of model in netpyne.  still need to implement invivo bc. turn off stim to compare to original
# v0.01 - rearrange setting initial high K+ based on new netpyney dimensions
# v0.02 - fixed issue with initial distribution of K+
# v0.03 - added ecs_boundary_conditions and removed hh mechanisms
# v0.04 - fixed issues with naming and cell volume
# v0.05 - setup for 5s anoxic test run
# v0.06 - second iter of test run version, 10s, record 200 cells, anoxic
# v0.07 - udpdated nkcc1 to reflect SpatialModelRealistic.py
# v0.08 - included second ecs for o2 and some other features from SDinSlice/SpatialModel.py previously missing
# v0.09 - replicates results from SpatialModel.py
# v0.10 - six populations, probabilistic connectivity, 60k neurons per mm3 
# v0.11a - separate cell models for separate populations 
# v0.11b - add missing na+ current for glial na/k pump current