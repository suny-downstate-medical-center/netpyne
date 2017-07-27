# simplified corticospinal cell model (6 compartment)

from neuron import h
from math import exp,log

Vrest       = -88.5366550238 
h.v_init = -75.0413649414 
h.celsius     = 34.0 # for in vitro opt

# geom properties
somaL = 48.4123467666 
somaDiam = 28.2149102762 
axonL = 594.292937602 
axonDiam =  1.40966286462 
apicL = 261.904636003 
apicDiam = 1.5831889597 
bdendL = 299.810775175 
bdendDiam = 2.2799248874 

# passive properties 
axonCap =  1.01280903702 
somaCap =  1.78829677463 
apicCap = 1.03418636866 
bdendCap = 1.89771901209 
rall = 114.510490019 
axonRM = 3945.2107187 
somaRM = 18501.7540916 
apicRM = 10751.193413 
bdendRM = 13123.00174 

# Na, K reversal potentials calculated from BenS internal/external solutions via Nernst eq.
p_ek = -104.0 # these reversal potentials for in vitro conditions
p_ena = 42.0 
# h-current
h.erev_h = h.erev_ih = -37.0 # global
gbar_h = 0.000140956438043 
h_gbar_tuft = 0.00565 # mho/cm^2 (based on Harnett 2015 J Neurosci)

# d-current
gbar_kdmc = 0.000447365630734
kdmc_gbar_axonm = 20
# spiking currents
gbar_nax = 0.0345117294903
nax_gbar_axonm = 5.0
nax_gbar_somam = 1.0
nax_gbar_dendm = 1.0
gbar_kdr = 0.0131103978049
kdr_gbar_axonm = 5.0
# A few kinetic params changed vis-a-vis kdr.mod defaults:
kdr_vhalfn = 11.6427471384
gbar_kap = 0.0898600246397
kap_gbar_axonm = 5.0
# A few kinetic params changed vis-a-vis kap.mod defaults:
kap_vhalfn  = 32.7885075379
kap_tq      = -52.0967985869
kap_vhalfl = -59.7867409796 # global!!

# other ion channel parameters 
cal_gcalbar = 4.41583533572e-06
can_gcanbar = 4.60717910591e-06
calginc = 1.0
h_lambda = 325.0
kBK_gpeak = 5.09733585163e-05
kBK_caVhminShift = 43.8900261407
cadad_depth = 0.119408607923
cadad_taur = 99.1146852282 
			
###############################################################################
# SPI6 Cell
###############################################################################
class SPI6 ():
  "Simplified Corticospinal Cell Model"
  def __init__(self,x=0,y=0,z=0,ID=0):
    self.x,self.y,self.z=x,y,z
    self.ID=ID
    self.all_sec = []
    self.add_comp('soma')
    self.set_morphology()
    self.insert_conductances()
    self.set_props()

  def add_comp(self, name):
    self.__dict__[name] = h.Section(name=name)#,cell=self)
    self.all_sec.append(self.__dict__[name])

  def set_morphology(self):
    self.add_comp('axon')
    self.add_comp('Bdend')
    self.add_comp('Adend1')
    self.add_comp('Adend2')
    self.add_comp('Adend3')
    self.apic = [self.Adend1, self.Adend2, self.Adend3]
    self.basal = [self.Bdend]
    self.alldend = [self.Adend1, self.Adend2, self.Adend3, self.Bdend]
    self.set_geom()
    self.axon.connect(self.soma, 0.0, 0.0)
    self.Bdend.connect(self.soma,      0.5, 0.0) # soma 0.5 to Bdend 0
    self.Adend1.connect(self.soma,   1.0, 0.0)
    self.Adend2.connect(self.Adend1,   1.0, 0.0)
    self.Adend3.connect(self.Adend2,   1.0, 0.0)

  def set_geom (self):
    self.axon.L = axonL; self.axon.diam = axonDiam;
    self.soma.L = somaL; self.soma.diam = somaDiam
    for sec in self.apic: sec.L,sec.diam = apicL,apicDiam
    self.Bdend.L = bdendL; self.Bdend.diam = bdendDiam

  def activeoff (self):
    for sec in self.all_sec: sec.gbar_nax=sec.gbar_kdr=sec.gbar_kap=0.0

  def set_axong (self):
    axon = self.axon
    axon.gbar_kdmc  = gbar_kdmc * kdmc_gbar_axonm
    axon.gbar_nax = gbar_nax * nax_gbar_axonm
    axon.gbar_kdr = gbar_kdr * kdr_gbar_axonm
    axon.gbar_kap = gbar_kap * kap_gbar_axonm

  def set_calprops (self,sec):
    sec.gcalbar_cal = cal_gcalbar 
    sec.gcanbar_can = can_gcanbar 
    sec.gpeak_kBK = kBK_gpeak
    sec.caVhmin_kBK = -46.08 + kBK_caVhminShift
    sec.depth_cadad = cadad_depth
    sec.taur_cadad = cadad_taur   

  def set_somag (self):
    sec = self.soma
    sec.gbar_ih = gbar_h # Ih
    self.set_calprops(sec)
    sec.gbar_kdmc  = gbar_kdmc 
    sec.gbar_nax = gbar_nax * nax_gbar_somam

  def set_bdendg (self): 
    sec = self.Bdend
    sec.gbar_ih = gbar_h # Ih
    self.set_calprops(sec)
    sec.gbar_nax = gbar_nax * nax_gbar_dendm

  def set_apicg (self):
    h.distance(0,0.5,sec=self.soma) # middle of soma is origin for distance
    self.nexusdist = nexusdist = 300.0
    self.h_gbar_tuftm = h_gbar_tuftm = h_gbar_tuft / gbar_h
    self.h_lambda = h_lambda = nexusdist / log(h_gbar_tuftm)
    for sec in self.apic:
      self.set_calprops(sec)
      for seg in sec:
        d = h.distance(seg.x,sec=sec)
        if d <= nexusdist: seg.gbar_ih = gbar_h * exp(d/h_lambda)
        else: seg.gbar_ih = h_gbar_tuft
      sec.gbar_nax = gbar_nax * nax_gbar_dendm
    self.apic[1].gcalbar_cal = cal_gcalbar * calginc # middle apical dend gets more iL

  # set properties
  def set_props (self):
    self.set_geom()
    # cm - can differ across locations
    self.axon.cm = axonCap
    self.soma.cm = somaCap
    self.Bdend.cm = bdendCap
    for sec in self.apic: sec.cm = apicCap
    # g_pas == 1.0/rm - can differ across locations
    self.axon.g_pas = 1.0/axonRM
    self.soma.g_pas = 1.0/somaRM
    self.Bdend.g_pas = 1.0/bdendRM
    for sec in self.apic: sec.g_pas = 1.0/apicRM
    for sec in self.all_sec:
      sec.ek = p_ek # K+ current reversal potential (mV)
      sec.ena = p_ena # Na+ current reversal potential (mV)
      sec.Ra = rall; sec.e_pas = Vrest # passive      
      sec.gbar_nax    = gbar_nax # Na      
      sec.gbar_kdr    = gbar_kdr # KDR
      sec.vhalfn_kdr = kdr_vhalfn # KDR kinetics 
      sec.gbar_kap    = gbar_kap # K-A
      sec.vhalfn_kap = kap_vhalfn # K-A kinetics
      sec.vhalfl_kap = kap_vhalfl
      sec.tq_kap = kap_tq
    self.set_somag()
    self.set_bdendg()
    self.set_apicg()
    self.set_axong()

  def insert_conductances (self):
    for sec in self.all_sec:
      sec.insert('k_ion')
      sec.insert('na_ion')
      sec.insert('pas') # passive
      sec.insert('nax') # Na current
      sec.insert('kdr') # K delayed rectifier current
      sec.insert('kap') # K-A current
    for sec in [self.Adend3, self.Adend2, self.Adend1, self.Bdend, self.soma]:
      sec.insert('ih') # h-current      
      sec.insert('ca_ion') # calcium channels
      sec.insert('cal') # cal_mig.mod
      sec.insert('can') # can_mig.mod
      sec.insert('cadad') # cadad.mod - calcium decay 
      sec.insert('kBK') # kBK.mod - ca and v dependent k channel
    for sec in [self.soma, self.axon]: sec.insert('kdmc')  # K-D current in soma & axon only

#
def prmstr (p,s,fctr=2.0,shift=5.0):
  if p == 0.0:
    print s,'=',str(p-shift),str(p+shift),str(p),'True'
  elif p < 0.0:
    print s, '=',str(p*fctr),str(p/fctr),str(p),'True'
  else:
    print s, ' = ' , str(p/fctr), str(p*fctr), str(p), 'True'

