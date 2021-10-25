
"""
Module for modifying the network model instance

"""

from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from netpyne.logger import logger

# -----------------------------------------------------------------------------
# Modify cell params
# -----------------------------------------------------------------------------
from future import standard_library
standard_library.install_aliases()
def modifyCells(self, params, updateMasterAllCells=False):
    """
    Function for/to <short description of `netpyne.network.modify.modifyCells`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*

    params : <type>
        <Short description of params>
        **Default:** *required*

    updateMasterAllCells : bool
        <Short description of updateMasterAllCells>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>


    """


    from .. import sim

    # Instantiate network connections based on the connectivity rules defined in params
    sim.timing('start', 'modifyCellsTime')
    if sim.rank==0:
        logger.info('Modifying cell parameters...')

    for cell in self.cells:
        cell.modify(params)

    if updateMasterAllCells:
        sim._gatherCells()  # update allCells

    sim.timing('stop', 'modifyCellsTime')
    if sim.rank == 0 and sim.cfg.timing: logger.info('  Done; cells modification time = %0.2f s.' % sim.timingData['modifyCellsTime'])


# -----------------------------------------------------------------------------
# Modify synMech params
# -----------------------------------------------------------------------------
def modifySynMechs(self, params, updateMasterAllCells=False):
    """
    Function for/to <short description of `netpyne.network.modify.modifySynMechs`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*

    params : <type>
        <Short description of params>
        **Default:** *required*

    updateMasterAllCells : bool
        <Short description of updateMasterAllCells>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>


    """


    from .. import sim

    # Instantiate network connections based on the connectivity rules defined in params
    sim.timing('start', 'modifySynMechsTime')
    if sim.rank==0:
        logger.info('Modifying synaptic mech parameters...')

    for cell in self.cells:
        cell.modifySynMechs(params)

    if updateMasterAllCells:
         sim._gatherCells()  # update allCells

    sim.timing('stop', 'modifySynMechsTime')
    if sim.rank == 0 and sim.cfg.timing: logger.info('  Done; syn mechs modification time = %0.2f s.' % sim.timingData['modifySynMechsTime'])


# -----------------------------------------------------------------------------
# Modify conn params
# -----------------------------------------------------------------------------
def modifyConns(self, params, updateMasterAllCells=False):
    """
    Function for/to <short description of `netpyne.network.modify.modifyConns`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*

    params : <type>
        <Short description of params>
        **Default:** *required*

    updateMasterAllCells : bool
        <Short description of updateMasterAllCells>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>


    """


    from .. import sim

    # Instantiate network connections based on the connectivity rules defined in params
    sim.timing('start', 'modifyConnsTime')
    if sim.rank==0:
        logger.info('Modifying connection parameters...')

    for cell in self.cells:
        cell.modifyConns(params)

    if updateMasterAllCells:
        sim._gatherCells()  # update allCells

    sim.timing('stop', 'modifyConnsTime')
    if sim.rank == 0 and sim.cfg.timing: logger.info('  Done; connections modification time = %0.2f s.' % sim.timingData['modifyConnsTime'])


# -----------------------------------------------------------------------------
# Modify stim source params
# -----------------------------------------------------------------------------
def modifyStims(self, params, updateMasterAllCells=False):
    """
    Function for/to <short description of `netpyne.network.modify.modifyStims`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*

    params : <type>
        <Short description of params>
        **Default:** *required*

    updateMasterAllCells : bool
        <Short description of updateMasterAllCells>
        **Default:** ``False``
        **Options:** ``<option>`` <description of option>


    """


    from .. import sim

    # Instantiate network connections based on the connectivity rules defined in params
    sim.timing('start', 'modifyStimsTime')
    if sim.rank==0:
        logger.info('Modifying stimulation parameters...')

    for cell in self.cells:
        cell.modifyStims(params)

    if updateMasterAllCells:
        sim._gatherCells()  # update allCells

    sim.timing('stop', 'modifyStimsTime')
    if sim.rank == 0 and sim.cfg.timing: logger.info('  Done; stims modification time = %0.2f s.' % sim.timingData['modifyStimsTime'])
