from neuron import h
from cfg import cfg 
import numpy as np 

class ENeuron:
    """ A neuron with soma and dendrite with; fast and persistent sodium
    currents, potassium currents, passive leak and potassium leak and an
    accumulation mechanism. """
    def __init__(self):
        self.soma = h.Section(name='Esoma', cell=self)
        # add 3D points to locate the neuron in the ECS  
        self.soma.pt3dadd(0.0, 0.0, 0.0, 2.0 * cfg.somaR)
        self.soma.pt3dadd(0.0, 2.0 * cfg.somaR, 0.0, 2.0 * cfg.somaR)
        if cfg.epas:
            self.soma.insert('pas')
            self.soma(0.5).pas.e = cfg.epas
            self.soma(0.5).pas.g = cfg.gpas

class E2Neuron:
    """ A neuron with soma and dendrite with; fast and persistent sodium
    currents, potassium currents, passive leak and potassium leak and an
    accumulation mechanism. """
    def __init__(self):
        self.soma = h.Section(name='E2soma', cell=self)
        # add 3D points to locate the neuron in the ECS  
        self.soma.pt3dadd(0.0, 0.0, 0.0, 2.0 * cfg.somaR)
        self.soma.pt3dadd(0.0, 2.0 * cfg.somaR, 0.0, 2.0 * cfg.somaR)
        if cfg.epas:
            self.soma.insert('pas')
            self.soma(0.5).pas.e = cfg.epas
            self.soma(0.5).pas.g = cfg.gpas

class I2Neuron:
    """ A neuron with soma and dendrite with; fast and persistent sodium
    currents, potassium currents, passive leak and potassium leak and an
    accumulation mechanism. """
    def __init__(self):
        self.soma = h.Section(name='I2soma', cell=self)
        # add 3D points to locate the neuron in the ECS  
        self.soma.pt3dadd(0.0, 0.0, 0.0, 2.0 * cfg.somaR)
        self.soma.pt3dadd(0.0, 2.0 * cfg.somaR, 0.0, 2.0 * cfg.somaR)
        if cfg.epas:
            self.soma.insert('pas')
            self.soma(0.5).pas.e = cfg.epas
            self.soma(0.5).pas.g = cfg.gpas

class E4Neuron:
    """ A neuron with soma and dendrite with; fast and persistent sodium
    currents, potassium currents, passive leak and potassium leak and an
    accumulation mechanism. """
    def __init__(self):
        self.soma = h.Section(name='E4soma', cell=self)
        # add 3D points to locate the neuron in the ECS  
        self.soma.pt3dadd(0.0, 0.0, 0.0, 2.0 * cfg.somaR)
        self.soma.pt3dadd(0.0, 2.0 * cfg.somaR, 0.0, 2.0 * cfg.somaR)
        if cfg.epas:
            self.soma.insert('pas')
            self.soma(0.5).pas.e = cfg.epas
            self.soma(0.5).pas.g = cfg.gpas

class I4Neuron:
    """ A neuron with soma and dendrite with; fast and persistent sodium
    currents, potassium currents, passive leak and potassium leak and an
    accumulation mechanism. """
    def __init__(self):
        self.soma = h.Section(name='I4soma', cell=self)
        # add 3D points to locate the neuron in the ECS  
        self.soma.pt3dadd(0.0, 0.0, 0.0, 2.0 * cfg.somaR)
        self.soma.pt3dadd(0.0, 2.0 * cfg.somaR, 0.0, 2.0 * cfg.somaR)
        if cfg.epas:
            self.soma.insert('pas')
            self.soma(0.5).pas.e = cfg.epas
            self.soma(0.5).pas.g = cfg.gpas

class E5Neuron:
    """ A neuron with soma and dendrite with; fast and persistent sodium
    currents, potassium currents, passive leak and potassium leak and an
    accumulation mechanism. """
    def __init__(self):
        self.soma = h.Section(name='E5soma', cell=self)
        # add 3D points to locate the neuron in the ECS  
        self.soma.pt3dadd(0.0, 0.0, 0.0, 2.0 * cfg.somaR)
        self.soma.pt3dadd(0.0, 2.0 * cfg.somaR, 0.0, 2.0 * cfg.somaR)
        if cfg.epas:
            self.soma.insert('pas')
            self.soma(0.5).pas.e = cfg.epas
            self.soma(0.5).pas.g = cfg.gpas

class I5Neuron:
    """ A neuron with soma and dendrite with; fast and persistent sodium
    currents, potassium currents, passive leak and potassium leak and an
    accumulation mechanism. """
    def __init__(self):
        self.soma = h.Section(name='I5soma', cell=self)
        # add 3D points to locate the neuron in the ECS  
        self.soma.pt3dadd(0.0, 0.0, 0.0, 2.0 * cfg.somaR)
        self.soma.pt3dadd(0.0, 2.0 * cfg.somaR, 0.0, 2.0 * cfg.somaR)
        if cfg.epas:
            self.soma.insert('pas')
            self.soma(0.5).pas.e = cfg.epas
            self.soma(0.5).pas.g = cfg.gpas

# v0.00 - classes for each cell type in network