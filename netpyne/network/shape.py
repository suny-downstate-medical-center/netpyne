"""
Module to handle cell morphology in networks

"""

from neuron import h

# -----------------------------------------------------------------------------
# Calculate segment coordinates from 3d point coordinates
# -----------------------------------------------------------------------------
def calcSegCoords(self):
    """
    Function for/to <short description of `netpyne.network.shape.calcSegCoords`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*


    """

    from .. import sim

    if sim.cfg.createNEURONObj:
        # Calculate relative seg coords for 1 cell per pop,
        for pop in list(self.pops.values()):
            if pop.cellModelClass == sim.CompartCell:
                pop.calcRelativeSegCoords()

        # Calculate abs seg coords for all cells
        for cell in sim.net.compartCells:
            cell.calcAbsSegCoords()


# -----------------------------------------------------------------------------
# Add 3D points to sections with simplified geometry
# -----------------------------------------------------------------------------
def defineCellShapes(self):
    """
    Function for/to <short description of `netpyne.network.shape.defineCellShapes`>

    Parameters
    ----------
    self : <type>
        <Short description of self>
        **Default:** *required*


    """

    from .. import sim

    if sim.cfg.createNEURONObj:
        sim.net.compartCells = [c for c in sim.net.cells if type(c) is sim.CompartCell]
        h.define_shape()
        for cell in sim.net.compartCells:
            cell.updateShape()
