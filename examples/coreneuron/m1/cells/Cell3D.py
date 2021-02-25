from neuron import h, gui
h.load_file('import3d.hoc')

class Cell3D:
  def __init__ (self, fmorph): # fmorph is path to file with morphology (e.g., ASC file)
    self.fmorph = fmorph
    # Checks morph to determine type of cell
    cell = h.Import3d_Neurolucida3()
    cell.input(fmorph)
    i3d = h.Import3d_GUI(cell, 0)
    i3d.instantiate(self)
    self.init_once()
  def init_once (self): pass # subclasses should implement this to setup ion channels
