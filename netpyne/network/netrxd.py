
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
import numpy as np 



# -----------------------------------------------------------------------------
# Add RxD
# -----------------------------------------------------------------------------
def addRxD (self):
    from .. import sim

    if len(self.params.rxdParams):
        try:
            global nrnRxD
            from neuron import crxd as nrnRxD 
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
    sim.net.rxd = sim.net.params.rxdParams

    # add NEURON objects
    if sim.cfg.createNEURONObj:
        for rxdParamLabel,rxdParam in self.params.rxdParams.items():  # for each conn rule or parameter set
            if rxdParamLabel == 'region':
                self.addRegions(rxdParam)
            elif rxdParamLabel == 'species':
                self.addSpecies(rxdParam)
            elif rxdParamLabel == 'reaction':
                self.addReactions(rxdParam)
            elif rxdParamLabel == 'multicompartmentReaction':
                self.addMulticompartmentReactions(rxdParam)
            elif rxdParamLabel == 'rate':
                self.addRates(rxdParam)
            elif rxdParamLabel == 'extracellular':
                self.addExtracellular(rxdParam)

    sim.pc.barrier()
    sim.timing('stop', 'add RxD')
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
            cells = sim.getCellsList(param['cells'])
        # secs
        if 'secs' not in param:
            param['secs'] = ['all']
        if not isinstance(param['secs'], list):
            param['secs'] = [param['secs']] 
        # nrn_region
        if 'nrn_region' not in param:
            param['nrn_region'] == None
        # geomery
        if 'geometry' not in param:
            param['geometry'] == None
            #             class neuron.rxd.geometry.FixedCrossSection(cross_area, surface_area=0) 
            # __call__() 
            # calling returns self to allow for rxd.inside or rxd.inside()

            # class neuron.rxd.geometry.FractionalVolume(volume_fraction=1, surface_fraction=0, neighbor_areas_fraction=None) 
            # __call__() 
            # calling returns self to allow for rxd.inside or rxd.inside()

            # class neuron.rxd.geometry.FixedPerimeter(perimeter, on_cell_surface=False) 
            # __call__() 
            # calling returns self to allow for rxd.inside or rxd.inside()

            # class neuron.rxd.geometry.Shell(lo=None, hi=None) 
            # __call__() 
            # calling returns self to allow for rxd.inside or rxd.inside()
        # geomery
        if 'dimension' not in param:
            param['dimension'] == None
        # geomery
        if 'dx' not in param:
            param['dx'] == None

        # get list of h.Sections() based on cells and secs
        if 'cells' == 'all' and 'secs' == 'all':
            nrnSecs = list(sim.h.allSec())
        else:
            nrnSecs = []
            for cell in cells:
                for secName,sec in cell.secs.items():
                    if 'all' in param['secs'] or secName in param['secs']: 
                        nrnSecs.append(sec['hObj'])

        # call rxd method to create Region
        self.rxd['regions'][label] = nrnRxD.Region(secs=nrnSecs, 
                                                nrn_region=param['nrn_region'], 
                                                geometry=param['geometry'], 
                                                dimension=param['dimension'], 
                                                dx=param['dx'], 
                                                name=label)


# -----------------------------------------------------------------------------
# Add RxD species
# -----------------------------------------------------------------------------
def addSpecies(params):
    from .. import sim

    #regions=None, d=0, name=None, charge=0, initial=None, atolscale=1

    for label, param in params.items():
        # regions
        if 'regions' not in param:
            print('  Species %s not added because "regions" was missing'%(label))
        # d
        if 'd' not in param:
            param['d'] = 0
        # nrn_region
        if 'charge' not in params:
            params['charge'] == 0
        # nrn_region
        if 'initial' not in param:
            params['initial'] == None
        # atolscale
        if 'atolscale' not in param:
            params['atolscale'] == 1


