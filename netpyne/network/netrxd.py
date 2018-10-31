
"""
network/rxd.py 

Network class methods to add RxD  

Contributors: salvadordura@gmail.com
"""
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from builtins import dict
from builtins import range

from builtins import round
from future import standard_library
standard_library.install_aliases()
import copy
import imp
import numpy as np 



# -----------------------------------------------------------------------------
# Add RxD
# -----------------------------------------------------------------------------
def addRxD (self):
    from .. import sim

    if len(self.params.rxdParams):
        try:
            global rxd
            from neuron import crxd as rxd 
            sim.net.rxd = {'species': {}, 'regions': {}}  # dictionary for rxd  
        except:
            print('cRxD module not available')
            return -1
    else:
        return -1


    # Instantiate network connections based on the connectivity rules defined in params
    sim.timing('start', 'rxdTime')
    if sim.rank==0: 
        print('Adding RxD...')

    # make copy of Python structure
    #if sim.cfg.createPyStruct: -- don't make conditional since need to have Python structure
    sim.net.rxd = copy.deepcopy(sim.net.params.rxdParams)

    # add NEURON objects
    if sim.cfg.createNEURONObj:
        rxdParams = sim.net.params.rxdParams
        if 'regions' in rxdParams:
            self.addRegions(rxdParams['regions'])
        if 'extracellular' in rxdParams:
            self.addExtracellular(rxdParams['extracellular'])
        if 'species' in rxdParams:
            self.addSpecies(rxdParams['species'])
        if 'states' in rxdParams:
            self.addStates(rxdParams['states'])
        if 'reactions' in rxdParams:
            self.addReactions(rxdParams['reaction'])
        if 'multicompartmentReactions' in rxdParams:
            self.addReactions(rxdParams['multicompartmentReactions'], multicompartment=True)
        if 'rates' in rxdParams:
            self.addRates(rxdParams['rate'])

    sim.pc.barrier()
    sim.timing('stop', 'rxdTime')
    if sim.rank == 0 and sim.cfg.timing: print(('  Done; RxD setup time = %0.2f s.' % sim.timingData['rxdTime']))

    return sim.net.rxd



# -----------------------------------------------------------------------------
# Add RxD regions
# -----------------------------------------------------------------------------
def addRegions(self, params):
    from .. import sim

    for label, param in params.items():
        # cells
        if 'cells' not in param:
            param['cells'] = 'all'

        # secs
        if 'secs' not in param:
            param['secs'] = ['all']
        if not isinstance(param['secs'], list):
            param['secs'] = [param['secs']] 
        
        # nrn_region
        if 'nrn_region' not in param:
            param['nrn_region'] = None
        
        # geomery
        if 'geometry' not in param:
            param['geometry'] = None
        if isinstance(param['geometry'], dict):
            try:
                param['geometry']['hObj'] = getattr(rxd, param['geometry']['class'])(**param['geometry']['args'])
            except:
                print('  Error creating %s Region geometry using %s class'%(label, param['geometry']['class'])) 
            
            # List of allowed geometry classes: 
            # class neuron.rxd.geometry.FixedCrossSection(cross_area, surface_area=0) 
            # class neuron.rxd.geometry.FractionalVolume(volume_fraction=1, surface_fraction=0, neighbor_areas_fraction=None) 
            # class neuron.rxd.geometry.FixedPerimeter(perimeter, on_cell_surface=False) 
            # class neuron.rxd.geometry.Shell(lo=None, hi=None) 
        
        # geomery
        if 'dimension' not in param:
            param['dimension'] = None
        
        # geomery
        if 'dx' not in param:
            param['dx'] = None

        # get list of h.Sections() based on cells and secs
        if 'all' in param['cells'] and 'all' in param['secs']:
            nrnSecs = list(sim.h.allsec())
        else:
            cells = sim.getCellsList(param['cells'])
            nrnSecs = []
            for cell in cells:
                for secName,sec in cell.secs.items():
                    if 'all' in param['secs'] or secName in param['secs']: 
                        nrnSecs.append(sec['hObj'])

        # call rxd method to create Region
        self.rxd['regions'][label]['hObj'] = rxd.Region(secs=nrnSecs, 
                                                nrn_region=param['nrn_region'], 
                                                geometry=param['geometry']['hObj'], 
                                                dimension=param['dimension'], 
                                                dx=param['dx'], 
                                                name=label)
        print('  Created Region %s'%(label))


# -----------------------------------------------------------------------------
# Add RxD species
# -----------------------------------------------------------------------------
def addSpecies(self, params):
    from .. import sim

    for label, param in params.items():
        # regions
        if 'regions' not in param:
            print('  Error creating Species %s: "regions" parameter was missing'%(label))
            continue
        if not isinstance(param['regions'], list):
            param['regions'] = [param['regions']]
        try:
            nrnRegions = [self.rxd['regions'][region]['hObj'] for region in param['regions']]
        except:
           print('  Error creating Species %s: could not find regions %s'%(label, param['regions']))
        
        # d
        if 'd' not in param:
            param['d'] = 0
        
        # charge
        if 'charge' not in param:
            param['charge'] = 0
        
        # initial
        if 'initial' not in param:
            param['initial'] == None
        if isinstance(param['initial'], str):  # string-based func
            funcStr = self.replaceRxDStr(param['initial'], constants=True, regions=True, species=False)

            # create final function dynamically from string
            importStr = ' from neuron import crxd as rxd \n from netpyne import sim'
            afterDefStr = 'sim.net.rxd["species"]["%s"]["initialFunc"] = initial' % (label)
            funcStr = 'def initial (node): \n%s \n return %s \n%s' % (importStr, funcStr, afterDefStr) # convert to lambda function
            try:
                exec(funcStr, {'rxd': rxd}, {'sim': sim})        
                initial = sim.net.rxd["species"][label]["initialFunc"]
            except:
                print('  Error creating Species %s: cannot evaluate "initial" expression -- "%s"'%(label, param['initial']))
                continue
        else:
            initial = param['initial']
        
        # atolscale
        if 'atolscale' not in param:
            param['atolscale'] = 1

        # call rxd method to create Region
        self.rxd['species'][label]['hObj'] = rxd.Species(regions=nrnRegions, 
                                                d=param['d'], 
                                                charge=param['charge'], 
                                                initial=initial, 
                                                atolscale=param['atolscale'], 
                                                name=label)
        print('  Created Species %s'%(label))


# -----------------------------------------------------------------------------
# Add RxD states
# -----------------------------------------------------------------------------
def addState(self, params):
    from .. import sim

    for label, param in params.items():
        # regions
        if 'regions' not in param:
            print('  Error creating State %s: "regions" parameter was missing'%(label))
            continue
        if not isinstance(param['regions'], list):
            param['regions'] = [param['regions']]
        try:
            nrnRegions = [self.rxd['regions'][region]['hObj'] for region in param['regions']]
        except:
           print('  Error creating State %s: could not find regions %s'%(label, param['regions']))
        
        # initial
        if 'initial' not in param:
            param['initial'] == None
        if isinstance(param['initial'], str):  # string-based func
            funcStr = self.replaceRxDStr(param['initial'], constants=True, regions=True, species=False)

            # create final function dynamically from string
            importStr = ' from neuron import crxd as rxd \n from netpyne import sim'
            afterDefStr = 'sim.net.rxd["states"]["%s"]["initialFunc"] = initial' % (label)
            funcStr = 'def initial (node): \n%s \n return %s \n%s' % (importStr, funcStr, afterDefStr) # convert to lambda function
            try:
                exec(funcStr, {'rxd': rxd}, {'sim': sim})        
                initial = sim.net.rxd["species"][label]["initialFunc"]
            except:
                print('  Error creating State %s: cannot evaluate "initial" expression -- "%s"'%(label, param['initial']))
                continue
        else:
            initial = param['initial']
        
        # call rxd method to create Region
        self.rxd['states'][label]['hObj'] = rxd.State(region=nrnRegions, 
                                                    initial=initial)
        print('  Created State %s'%(label))


# -----------------------------------------------------------------------------
# Add RxD reactions
# -----------------------------------------------------------------------------
def addReactions(self, params, multicompartment=False):
    from .. import sim

    reactionStr = 'MulticompartmentReaction' if multicompartment else 'Reaction'
    reactionDictKey = 'multicompartmentReactions' if multicompartment else 'reactions'

    for label, param in params.items():
        # reactant
        if 'reactant' not in param:
            print('  Error creating %s %s: "reactant" parameter was missing'%(reactionStr,label))
            continue
        reactant = self.replaceRxDStr(param['reactant'])

        # product
        if 'product' not in param:
            print('  Error creating %s %s: "product" parameter was missing'%(reactionStr,label))
            continue
        product = self.replaceRxDStr(param['product'])

        # rate_f
        if 'rate_f' not in param:
            print('  Error creating %s %s: "scheme" parameter was missing'%(reactionStr,label))
            continue
        if isinstance(param['rate_f'], str):
            rate_f = self.replaceRxDStr(param['rate_f'])
        else:
            rate_f = param['rate_f']

        # rate_b
        if 'rate_b' not in param:
            param['rate_b'] = None 
        if isinstance(param['rate_f'], str):
            rate_b = self.replaceRxDStr(param['rate_b'])
        else:
            rate_b = param['rate_b']

        # regions
        if 'regions' not in param:
            param['regions'] = None
            nrnRegions = None
        elif not isinstance(param['regions'], list):
            param['regions'] = [param['regions']]
            try:
                nrnRegions = [self.rxd['regions'][region]['hObj'] for region in param['regions']]
            except:
               print('  Error creating %s %s: could not find regions %s'%(reactionStr, label, param['regions']))

        # membrane
        if 'membrane' not in param:
            param['membrane'] = None
        if param['membrane'] in self.rxd['regions']:   
            nrnMembraneRegion = self.rxd['regions'][param['membrane']]['hObj']
        else:
            nrnMembraneRegion = None

        # custom_dynamics
        if 'custom_dynamics' not in param:
            param['custom_dynamics'] = False

        self.rxd[reactionDictKey][label]['hObj'] = rxd.Reaction(eval(reactant),
                                                        eval(product), 
                                                        eval(rate_f) if isinstance(rate_f, str) else rate_f, 
                                                        rate_b=eval(rate_b) if isinstance(rate_b, str) else rate_b, 
                                                        regions=nrnRegions, 
                                                        custom_dynamics=param['custom_dynamics'],
                                                        membrane=nrnMembraneRegion)


# -----------------------------------------------------------------------------
# Add RxD reactions
# -----------------------------------------------------------------------------
def addRates(self, params):
    from .. import sim

    for label, param in params.items():
        # species
        if 'species' not in param:
            print('  Error creating Rate %s: "species" parameter was missing'%(label))
            continue
        if isinstance(param['species']) and param['species'] in self.rxd['species']:
            species = self.rxd['species']['hObj']
        else:
            print('  Error creating Rate %s: "species" parameter is invalid (%s)'%(param['species'], label))
            continue

        # rate
        if 'rate' not in param:
            print('  Error creating Rate %s: "rate" parameter was missing'%(label))
            continue
        if isinstance(param['rate'], str):
            rate = self.replaceRxDStr(param['rate'])

        # regions
        if not isinstance(param['regions'], list):
            param['regions'] = [param['regions']]
        try:
            nrnRegions = [self.rxd['regions'][region]['hObj'] for region in param['regions']]
        except:
           print('  Error creating Rate %s: could not find regions %s'%(label, param['regions']))

        # membrane_flux
        if 'membrane_flux' not in param:
            param['membrane_flux'] = False

        self.rxd['rates'][label]['hObj'] = rxd.Rate(species,
                                            eval(rate), 
                                            regions=nrnRegions, 
                                            membrane_flux=param['membrane_flux'])


# -----------------------------------------------------------------------------
# Replace RxD param strings with expression
# -----------------------------------------------------------------------------
def replaceRxDStr(self, origStr, constants=True, regions=True, species=True):
    replacedStr = str(origStr)
    
    # replace constants
    if constants:
        constantsList = [c for c in self.params.rxdParams['constants'] if c in origStr]  # get list of variables used (eg. post_ynorm or dist_xyz)  
        for constantLabel in constantsList:
            replacedStr = replacedStr.replace(constantLabel, 'sim.net.rxd["constants"]["%s"]'%(constantLabel))
        
    # replace regions
    if regions:
        for regionLabel in self.rxd['regions']:
            replacedStr = replacedStr.replace(regionLabel, 'sim.net.rxd["regions"]["%s"]["hObj"]'%(regionLabel))

    # replace species
    if species:
        for speciesLabel in self.rxd['species']:
            replacedStr = replacedStr.replace(speciesLabel, 'sim.net.rxd["species"]["%s"]["hObj"]'%(speciesLabel))

    return replacedStr

