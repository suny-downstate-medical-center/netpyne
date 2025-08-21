from matplotlib import pyplot
import random
from datetime import datetime
import pickle
from neuron import h, gui


class Cell(object):
    def __init__(self):
        self.synlist = []
        self.createSections()
        self.buildTopology()
        self.defineGeometry()
        self.defineBiophysics()
        self.createSynapses()
        self.nclist = []

    def createSections(self):
        pass

    def buildTopology(self):
        pass

    def defineGeometry(self):
        pass

    def defineBiophysics(self):
        pass

    def createSynapses(self):
        """Add an exponentially decaying synapse """
        synsoma = h.ExpSyn(self.soma(0.5))
        synsoma.tau = 2
        synsoma.e = 0
        syndend = h.ExpSyn(self.dend(0.5))
        syndend.tau = 2
        syndend.e = 0
        self.synlist.append(synsoma) # synlist is defined in Cell
        self.synlist.append(syndend) # synlist is defined in Cell


    def createNetcon(self, thresh=10):
        """ created netcon to record spikes """
        nc = h.NetCon(self.soma(0.5)._ref_v, None, sec = self.soma)
        nc.threshold = thresh
        return nc


class HHCellClass(Cell):
    """HH cell: A soma with active channels"""
    def createSections(self):
        """Create the sections of the cell."""
        self.soma = h.Section(name='soma', cell=self)
        self.dend = h.Section(name='dend', cell=self)

    def defineGeometry(self):
        """Set the 3D geometry of the cell."""
        self.soma.L = 18.8
        self.soma.diam = 18.8
        self.soma.Ra = 123.0

        self.dend.L = 200.0
        self.dend.diam = 1.0
        self.dend.Ra = 100.0

    def defineBiophysics(self):
        """Assign the membrane properties across the cell."""
        # Insert active Hodgkin-Huxley current in the soma
        self.soma.insert('hh')
        self.soma.gnabar_hh = 0.12  # Sodium conductance in S/cm2
        self.soma.gkbar_hh = 0.036  # Potassium conductance in S/cm2
        self.soma.gl_hh = 0.003    # Leak conductance in S/cm2
        self.soma.el_hh = -70       # Reversal potential in mV

        self.dend.insert('pas')
        self.dend.g_pas = 0.001  # Passive conductance in S/cm2
        self.dend.e_pas = -65    # Leak reversal potential mV
        self.dend.nseg = 1000

    def buildTopology(self):
        self.dend.connect(self.soma(1))
