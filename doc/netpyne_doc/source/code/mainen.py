# translated from /u/samn/npredict/geom_mainen.hoc // $Id: geom_mainen.hoc,v 1.3 2007/04/16 14:42:33 samn Exp $
from neuron import h
from math import pi

class PYR2:
  def __init__ (self,ID=0,ty=0,col=0,rho=165.0,kappa=10.0,soma_pas=False):
    self.ID=ID
    self.ty=ty
    self.col=col
    self.soma_pas = soma_pas
    self.soma = soma = h.Section(name='soma',cell=self)
    self.dend = dend = h.Section(name='dend',cell=self)
    self.dend.connect(self.soma,0.5,0) #   connect dend(0), soma(0.5)
    self.rho = rho # dendritic to axo-somatic area ratio 
    self.kappa = kappa # coupling resistance (Mohm) 
    for sec in [self.soma,self.dend]:
      sec.insert('k_ion')
      sec.insert('na_ion')
      sec.insert('ca_ion')
      sec.ek = -90 # K+ current reversal potential (mV)
      sec.ena = 60 # Na+ current reversal potential (mV)
      sec.eca = 140 # Ca2+ current reversal potential (mV)      
      h.ion_style("ca_ion",0,1,0,0,0) # using an ohmic current rather than GHK equation
      sec.Ra=100
    self.initsoma()
    self.initdend()

  def initsoma (self):
    soma = self.soma
    soma.nseg = 1
    soma.diam = 10.0/pi
    soma.L = 10
    soma.cm = 0.75
    soma.insert('naz') # naz.mod
    soma.insert('kv') # kv.mod
    soma.gmax_naz = 30e3
    soma.gmax_kv = 1.5e3    
    if self.soma_pas:
      soma.insert('pas')
      soma.e_pas=-70
      soma.g_pas=1/3e4

  def initdend (self):
    dend = self.dend
    dend.nseg = 1
    dend.diam = 10.0/pi
    self.config()
    dend.cm = 0.75
    dend.insert('naz') # naz.mod
    dend.insert('km') # km.mod
    dend.insert('kca') # kca.mod
    dend.insert('Nca') # Nca.mod
    dend.insert('cadad') # cadad.mod
    dend.insert('pas')
    dend.eca=140
    h.ion_style("ca_ion",0,1,0,0,0) # already called before
    dend.e_pas = -70 # only dendrite has leak conductance - why?
    dend.g_pas = 1/3e4 # only dendrite has leak conductance
    dend.gmax_naz=15
    dend.gmax_Nca = 0.3 # high voltage-activated Ca^2+ 
    dend.gmax_km = 0.1 # slow voltage-dependent non-inactivating K+
    dend.gmax_kca = 3  # slow Ca^2+-activated K+

  def config (self):
    self.dend. L  = self.rho*self.soma.L # dend area is axon area multiplied by rho
    self.dend.Ra = self.dend.Ra*self.kappa/self.dend(0.5).ri() # axial resistivity is adjusted to achieve

  # resets cell to default values
  def todefault(self):
    self.rho = 165
    self.kappa = 10
    self.config()
    self.soma.gmax_naz = 30e3
    self.soma.gmax_kv = 1.5e3
    self.dend.g_pas = 1/3e4
    self.dend.gmax_naz = 15
    self.dend.gmax_Nca = 0.3
    self.dend.gmax_km = 0.1
    self.dend.gmax_kca = 3
    self.soma.ek = dend.ek = -90
    self.soma.ena = dend.ena = 60
    self.soma.eca = dend.eca = 140
