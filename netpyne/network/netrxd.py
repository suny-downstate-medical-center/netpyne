
"""
Module for adding reaction-diffusion to network models

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from builtins import dict
from builtins import range

from builtins import round
try:
    basestring
except NameError:
    basestring = str
from future import standard_library
standard_library.install_aliases()
import copy
try:
    from neuron.crxd import rxdmath
except:
    print('Warning: Could not import rxdmath module')

# -----------------------------------------------------------------------------
# Add RxD
# -----------------------------------------------------------------------------
def addRxD(self):
    """
    Function for/to <short description of `netpyne.network.netrxd.addRxD`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*


    """


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
            self._addRegions(rxdParams['regions'])
        if 'extracellular' in rxdParams:
            self._addExtracellular(rxdParams['extracellular'])
        if 'species' in rxdParams:
            self._addSpecies(rxdParams['species'])
        if 'states' in rxdParams:
            self._addStates(rxdParams['states'])
        if 'reactions' in rxdParams:
            self._addReactions(rxdParams['reactions'])
        if 'multicompartmentReactions' in rxdParams:
            self._addReactions(rxdParams['multicompartmentReactions'], multicompartment=True)
        if 'rates' in rxdParams:
            self._addRates(rxdParams['rates'])

    sim.pc.barrier()
    sim.timing('stop', 'rxdTime')
    if sim.rank == 0 and sim.cfg.timing: print(('  Done; RxD setup time = %0.2f s.' % sim.timingData['rxdTime']))

    return sim.net.rxd



# -----------------------------------------------------------------------------
# Add RxD regions
# -----------------------------------------------------------------------------
def _addRegions(self, params):
    from .. import sim

    for label, param in params.items():

        if 'extracellular' in param and param['extracellular'] == True:
            self._addExtracellularRegion(label, param)
            continue

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
            geometry = param['geometry']
        if isinstance(param['geometry'], dict):
            try:
                param['geometry']['hObj'] = getattr(rxd, param['geometry']['class'])(**param['geometry']['args'])
                geometry = param['geometry']['hObj']
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
        if nrnSecs: self.rxd['regions'][label]['hObj'] = rxd.Region(secs=nrnSecs,
                                                                   nrn_region=param['nrn_region'],
                                                                   geometry=geometry,
                                                                   dimension=param['dimension'],
                                                                   dx=param['dx'],
                                                                   name=label)
        else: self.rxd['regions'][label]['hObj'] = None
        print('  Created Region %s'%(label))


# -----------------------------------------------------------------------------
# Add RxD extracellular
# -----------------------------------------------------------------------------
def _addExtracellularRegion(self, label, param):

    try:
        rxd.options.enable.extracellular = True
    except:
        print('Error enabling extracellular rxd')
        return -1

    # (xlo, ylo, zlo, xhi, yhi, zhi, dx, volume_fraction=1, tortuosity=1)

    requiredArgs = ['xlo', 'ylo', 'zlo', 'xhi', 'yhi', 'zhi', 'dx']
    for arg in requiredArgs:
        if arg not in param:
            print('  Error creating Extracellular object %s: %s parameter was missing'%(label, arg))

    if 'volume_fraction' not in param:
        param['volume_fraction'] = 1

    if 'tortuosity' not in param:
        param['tortuosity'] = 1

    # call rxd method to create Region
    self.rxd['regions'][label]['hObj'] = rxd.Extracellular(**{k:v for k,v in param.items() if k != 'extracellular'})

    print('  Created Extracellular Region %s'%(label))


# -----------------------------------------------------------------------------
# Add RxD species
# -----------------------------------------------------------------------------
def _addSpecies(self, params):
    from .. import sim

    for label, param in params.items():
        # regions
        if 'regions' not in param:
            print('  Error creating Species %s: "regions" parameter was missing'%(label))
            continue
        if not isinstance(param['regions'], list):
            param['regions'] = [param['regions']]
        try:
            nrnRegions = [self.rxd['regions'][region]['hObj'] for region in param['regions'] if self.rxd['regions'][region]['hObj'] != None]

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
        if isinstance(param['initial'], basestring):  # string-based func
            funcStr = self._replaceRxDStr(param['initial'], constants=True, regions=True, species=False)

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
        if nrnRegions: self.rxd['species'][label]['hObj'] = rxd.Species(regions=nrnRegions,
                                                                       d=param['d'],
                                                                       charge=param['charge'],
                                                                       initial=initial,
                                                                       atolscale=param['atolscale'],
                                                                       name=label)
        else: self.rxd['species'][label]['hObj'] = None
        print('  Created Species %s'%(label))


# -----------------------------------------------------------------------------
# Add RxD states
# -----------------------------------------------------------------------------
def _addStates(self, params):
    from .. import sim

    for label, param in params.items():
        # regions
        if 'regions' not in param:
            print('  Error creating State %s: "regions" parameter was missing'%(label))
            continue
        if not isinstance(param['regions'], list):
            param['regions'] = [param['regions']]
        try:
            nrnRegions = [self.rxd['regions'][region]['hObj'] for region in param['regions'] if self.rxd['regions'][region]['hObj'] != None]
        except:
           print('  Error creating State %s: could not find regions %s'%(label, param['regions']))

        # initial
        if 'initial' not in param:
            param['initial'] == None
        if isinstance(param['initial'], basestring):  # string-based func
            funcStr = self._replaceRxDStr(param['initial'], constants=True, regions=True, species=False)

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
        if nrnRegions: self.rxd['states'][label]['hObj'] = rxd.State(regions=nrnRegions,
                                                                    initial=initial)
        else: self.rxd['states'][label]['hObj'] = None
        print('  Created State %s'%(label))


# -----------------------------------------------------------------------------
# Add RxD reactions
# -----------------------------------------------------------------------------
def _addReactions(self, params, multicompartment=False):
    from .. import sim

    reactionStr = 'MultiCompartmentReaction' if multicompartment else 'Reaction'
    reactionDictKey = 'multicompartmentReactions' if multicompartment else 'reactions'

    for label, param in params.items():
        dynamicVars = {'sim': sim, 'rxdmath': rxdmath}
        # reactant
        if 'reactant' not in param:
            print('  Error creating %s %s: "reactant" parameter was missing'%(reactionStr,label))
            continue
        reactantStr = self._replaceRxDStr(param['reactant'])
        try:
            exec('reactant = ' + reactantStr, dynamicVars)
        except TypeError:
            continue
        if 'reactant' not in dynamicVars: dynamicVars['reactant']  # fix for python 2

        # product
        if 'product' not in param:
            print('  Error creating %s %s: "product" parameter was missing'%(reactionStr,label))
            continue
        productStr = self._replaceRxDStr(param['product'])
        exec('product = ' + productStr, dynamicVars)
        if 'product' not in dynamicVars: dynamicVars['product']  # fix for python 2

        # rate_f
        if 'rate_f' not in param:
            print('  Error creating %s %s: "scheme" parameter was missing'%(reactionStr,label))
            continue
        if isinstance(param['rate_f'], basestring):
            rate_fStr = self._replaceRxDStr(param['rate_f'])
            exec('rate_f = ' + rate_fStr, dynamicVars)
            if 'rate_f' not in dynamicVars: dynamicVars['rate_f']  # fix for python 2
        else:
            rate_f = param['rate_f']

        # rate_b
        if 'rate_b' not in param:
            param['rate_b'] = None
        if isinstance(param['rate_b'], basestring):
            rate_bStr = self._replaceRxDStr(param['rate_b'])
            exec('rate_b = ' + rate_bStr, dynamicVars)
            if 'rate_b' not in dynamicVars: dynamicVars['rate_b']  # fix for python 2
        else:
            rate_b = param['rate_b']

        # regions
        if 'regions' not in param:
            param['regions'] = None
            nrnRegions = None
        elif not isinstance(param['regions'], list):
            param['regions'] = [param['regions']]
            try:
                nrnRegions = [self.rxd['regions'][region]['hObj'] for region in param['regions'] if self.rxd['regions'][region]['hObj'] != None]
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
        if 'membrane_flux' not in param:
            param['membrane_flux'] = False



        if rate_b is None and dynamicVars.get('rate_b', None) is None:
            # omit positional argument 'rate_b'
            self.rxd[reactionDictKey][label]['hObj'] = getattr(rxd, reactionStr)(dynamicVars['reactant'],
                                                                            dynamicVars['product'],
                                                                            dynamicVars['rate_f'] if 'rate_f' in dynamicVars else rate_f,
                                                                            regions=nrnRegions,
                                                                            custom_dynamics=param['custom_dynamics'],
                                                                            membrane_flux=param['membrane_flux'],
                                                                            membrane=nrnMembraneRegion)

        else:
            # include positional argument 'rate_b'
            self.rxd[reactionDictKey][label]['hObj'] = getattr(rxd, reactionStr)(dynamicVars['reactant'],
                                                                            dynamicVars['product'],
                                                                            dynamicVars['rate_f'] if 'rate_f' in dynamicVars else rate_f,
                                                                            dynamicVars['rate_b'] if 'rate_b' in dynamicVars else rate_b,
                                                                            regions=nrnRegions,
                                                                            custom_dynamics=param['custom_dynamics'],
                                                                            membrane_flux=param['membrane_flux'],
                                                                            membrane=nrnMembraneRegion)

        print('  Created %s %s'%(reactionStr, label))

# -----------------------------------------------------------------------------
# Add RxD reactions
# -----------------------------------------------------------------------------
def _addRates(self, params):
    from .. import sim

    for label, param in params.items():
        dynamicVars = {'sim': sim, 'rxdmath': rxdmath}
        # species
        if 'species' not in param:
            print('  Error creating Rate %s: "species" parameter was missing'%(label))
            continue
        if isinstance(param['species'], basestring):
            speciesStr = self._replaceRxDStr(param['species'])
            exec('species = ' + speciesStr, dynamicVars)
            if 'species' not in dynamicVars: dynamicVars['species']  # fix for python 2
        else:
            print('  Error creating Rate %s: "species" parameter should be a string'%(param['species']))
            continue

        # rate
        if 'rate' not in param:
            print('  Error creating Rate %s: "rate" parameter was missing'%(label))
            continue
        if isinstance(param['rate'], basestring):
            rateStr = self._replaceRxDStr(param['rate'])
            exec('rate = ' + rateStr, dynamicVars)
            if 'rate' not in dynamicVars: dynamicVars['rate']  # fix for python 2

        # regions
        if 'regions' not in param:
            param['regions'] = None
            nrnRegions = None
        elif not isinstance(param['regions'], list):
            param['regions'] = [param['regions']]
            try:
                nrnRegions = [self.rxd['regions'][region]['hObj'] for region in param['regions']]
            except:
               print('  Error creating Rate %s: could not find regions %s'%(label, param['regions']))

        # membrane_flux
        if 'membrane_flux' not in param:
            param['membrane_flux'] = False

        self.rxd['rates'][label]['hObj'] = rxd.Rate(dynamicVars['species'],
                                                    dynamicVars['rate'],
                                                    regions=nrnRegions,
                                                    membrane_flux=param['membrane_flux'])

        print('  Created Rate %s'%(label))

# -----------------------------------------------------------------------------
# Replace RxD param strings with expression
# -----------------------------------------------------------------------------
def _replaceRxDStr(self, origStr, constants=True, regions=True, species=True):
    import re
    replacedStr = str(origStr)

    mapping = {}

    # replace constants
    if constants and 'constants' in self.rxd:
        constantsList = [c for c in self.params.rxdParams['constants'] if c in origStr]  # get list of variables used (eg. post_ynorm or dist_xyz)
        for constantLabel in constantsList:
            mapping[constantLabel] = 'sim.net.rxd["constants"]["%s"]'%(constantLabel)

    # replace regions
    if regions and 'regions' in self.rxd:
        for regionLabel in self.rxd['regions']:
            mapping[regionLabel] = 'sim.net.rxd["regions"]["%s"]["hObj"]'%(regionLabel)

    # replace species
    if species and 'species' in self.rxd:
        for speciesLabel in self.rxd['species']:
            mapping[speciesLabel] = 'sim.net.rxd["species"]["%s"]["hObj"]'%(speciesLabel)
    if species and 'states' in self.rxd:
        for statesLabel in self.rxd['states']:
            mapping[statesLabel] = 'sim.net.rxd["states"]["%s"]["hObj"]'%(statesLabel)

    # Place longer ones first to keep shorter substrings from matching where the longer ones should take place
    substrs = sorted(mapping, key=len, reverse=True)

    # Create a big OR regex that matches any of the substrings to replace
    regexp = re.compile('|'.join(map(re.escape, substrs)))

    # For each match, look up the new string in the mapping
    replacedStr = regexp.sub(lambda match: mapping[match.group(0)], replacedStr)

    return replacedStr
