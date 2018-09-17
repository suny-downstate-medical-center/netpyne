
"""
network/shape.py 

Network class methods to deal with the each population's cell shape (morphology) 

Contributors: salvadordura@gmail.com
"""

from neuron import h

# -----------------------------------------------------------------------------
# Calculate segment coordinates from 3d point coordinates 
# -----------------------------------------------------------------------------
def calcSegCoords(self):   
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
    from .. import sim
    if sim.cfg.createNEURONObj:
        sim.net.compartCells = [c for c in sim.net.cells if type(c) is sim.CompartCell]
        h.define_shape()
        for cell in sim.net.compartCells:
            cell.updateShape()
