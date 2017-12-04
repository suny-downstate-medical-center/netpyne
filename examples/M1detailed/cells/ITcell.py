from neuron import h
from math import sqrt, pi 
import os
from Cell3D import *

####################################################################
# Setting up params             
####################################################################
Vrest       = -94.5896010066
h.v_init = -94.5896010066
h.celsius = 34.0 # same as experiment

# passive properties (optimization proxies)
cap         = 0.800045777348
rall        = 149.477586545
rm          = 44140.5795522
spinecapfactor = 1.10734608835 # not used when == 1.0 since have explicit spine neck/head

#Na, K reversal potentials calculated from BenS internal and external solutions via Nernst equation
p_ek          = -104
p_ena         = 42

# h-current - based on Kole 2006, but parameterized for opt
h.erev_ih = h_erev = -37.0 
h_gbar      = 6.18831640879e-06 # mho/cm^2
h_ascale = 0.00643
h_bscale = 0.193
h_ashift = 154.9
h_aslope = 11.9
h_bslope = 33.1

# spiking currents
nax_gbar    = 0.0153130368342 
nax_gbar_axonm = nax_gbar_somam = 5

kdr_gbar    = 0.0084715576279
kdr_gbar_axonm = kdr_gbar_somam = 5

kap_gbar    = 0.06
kap_gbar_axonm = kap_gbar_somam = 5
# These param values match the default values in kap.mod (except where indicated).
kap_vhalfn  = 35.0 # def 11
kap_vhalfl  = -56.0
kap_tq      = -45.0 # def -40

# new ion channel parameters
cal_gcalbar = 5.73945708921e-06
can_gcanbar = 4.74427101753e-06
cat_gcatbar = 1.08074219052e-06
calginc = 1.0
kBK_gpeak = 7.67842640257e-05 # original value of 268e-4 too high for this model
kBK_caVhminShift = 45.0 # shift upwards to get lower effect on subthreshold
cadad_depth = 0.102468419281 # original 1; reduced for tighter coupling of ica and cai
cadad_taur = 16.0181691392 

nap_gbar = 0.0
ican_gbar = 0.0

###############################################################################
# Morph Cell
###############################################################################
class ITcell (Cell3D):
  def __init__ (self,fmorph=None,params=None):
    self.fmorph = fmorph
    if params: self.fmorph = self.set_params(params)
    Cell3D.__init__(self,self.fmorph)

  def addapicchan(self):
    for sec in self.apic:
      sec.insert('ca_ion')
      sec.insert('cadad') # cadad.mod
      sec.insert('cal')   # cal.mod
      sec.insert('can')   # can.mod
      sec.insert('kBK')   #kBK.mod

  def apicchanprop(self):
    for sec in self.apic:
      sec.gcalbar_cal = cal_gcalbar
      sec.gcanbar_can = can_gcanbar
      sec.gpeak_kBK = kBK_gpeak
      sec.caVhmin_kBK = -46.08 + kBK_caVhminShift
      sec.depth_cadad = cadad_depth
      sec.taur_cadad = cadad_taur

  def addbasalchan(self):
    # basal == dend
    for sec in self.dend:
      sec.insert('ca_ion')
      sec.insert('cadad') # cadad.mod
      sec.insert('cal')   # cal.mod
      sec.insert('can')   # can.mod
      sec.insert('kBK')   #kBK.mod

  def basalchanprop(self):
    # basal == dend
    for sec in self.dend:
      sec.gcalbar_cal = cal_gcalbar
      sec.gcanbar_can = can_gcanbar
      sec.gpeak_kBK = kBK_gpeak
      sec.caVhmin_kBK = -46.08 + kBK_caVhminShift
      sec.depth_cadad = cadad_depth
      sec.taur_cadad = cadad_taur

  def geom_nseg(self):
    # local freq, d_lambda, before, after, tmp
    # these are reasonable values for most models
    freq = 100 # Hz, frequency at which AC length constant will be computed
    d_lambda = 0.1
    before = 0
    after = 0
    for sec in self.all: before += sec.nseg
    #soma area(0.5) # make sure diam reflects 3d points
    for sec in self.all:
      # creates the number of segments per section
      # lambda_f takes in the current section
      sec.nseg = int((sec.L/(d_lambda*self.lambda_f(sec))+0.9)/2)*2 + 1
    for sec in self.all:
      after += sec.nseg 
    print "geom_nseg: changed from ", before, " to ", after, " total segments"

  def lambda_f(self, section): 
    # these are reasonable values for most models
    freq = 100      # Hz, frequency at which AC length constant will be computed
    d_lambda = 0.1
    # The lowest number of n3d() is 2
    if (section.n3d() < 2):
      return 1e5*sqrt(section.diam/(4*pi*freq*section.Ra*section.cm)) 
      # above was too inaccurate with large variation in 3d diameter
      # so now we use all 3-d points to get a better approximate lambda
    x1 = section.arc3d(0)
    d1 = section.diam3d(0)
    self.lam = 0
    #print section, " n3d:", section.n3d(), " diam3d:", section.diam3d(0)
    for i in range(section.n3d()): #h.n3d()-1
      x2 = section.arc3d(i)
      d2 = section.diam3d(i)
      self.lam += (x2 - x1)/sqrt(d1 + d2)
      x1 = x2   
      d1 = d2
    #  length of the section in units of lambda
    self.lam *= sqrt(2) * 1e-5*sqrt(4*pi*freq*section.Ra*section.cm)
    return section.L/self.lam

  def optimize_nseg (self):
    # Ra, cm, spinecapfactor
    # use worst case Ra, cm values
    for sec in self.all:
      sec.Ra = rall
      sec.cm = cap
    for i in xrange(2,len(self.apic),1): 
      self.apic[i].cm = spinecapfactor * self.apic[i].cm  	 # spinecapfactor * cm
      self.apic[i].g_pas = spinecapfactor / rm  # spinecapfactor * (1.0/rm)
    for sec in self.dend:  
      sec.cm = spinecapfactor * sec.cm
      sec.g_pas = spinecapfactor / rm
    # optimize # of segments per section (do this afer setting Ra, cm)
    self.geom_nseg()
		
  def init_once (self): 
    if self.fmorph.endswith('BS0409.ASC') or self.fmorph.endswith('BS0284.ASC'):
      # NB: paste-on axon if using SPI morphology (eg for comparing morph effect on dynamics)
      self.axon = [] 
      self.add_axon()
    for sec in self.all: #forall within an object just accesses the sections belonging to the object
      sec.insert('pas')   # passive
      sec.insert('ih')    # h-current in Ih_kole.mod
      sec.insert('nax')   # Na current
      sec.insert('kdr')	# K delayed rectifier current
      sec.insert('kap')	# K-A current
      sec.insert('k_ion')
      sec.insert('na_ion')
    self.setallprop()
    self.addapicchan()
    self.apicchanprop()
    self.addbasalchan()
    self.basalchanprop()
    for i in xrange(2,len(self.apic),1): 
      self.apic[i].cm = spinecapfactor * self.apic[i].cm  	 # spinecapfactor * cm
      self.apic[i].g_pas = spinecapfactor / rm  # spinecapfactor * (1.0/rm)
    for sec in self.dend:  
      sec.cm = spinecapfactor * sec.cm
      sec.g_pas = spinecapfactor / rm
    self.optimize_nseg()
    self.setgbarnaxd()
    self.setgbarkapd() # kap in apic,basal dends
    self.setgbarkdrd() # kdr in apic,basal dends
    self.sethgbar()    # distributes HCN conductance
    for sec in self.soma:
      sec.insert('ca_ion')
      sec.insert('cadad')
      sec.insert('cal')
      sec.insert('cat')
      sec.insert('can')
      sec.insert('kBK')	
      sec.insert('ican') # can_sidi.mod
      sec.insert('nap') # nap_sidi.mod
    self.setsomag()
    self.setaxong()

  def add_axon (self):
    # NB: paste-on axon if using SPI morphology (eg for comparing morph effect on dynamics)
    from PTAxonMorph import axonPts
    self.axon.append(h.Section(name="axon[0]"))
    self.all.append(self.axon[0])
    self.axon[0].connect(self.soma[0], 0.0, 0.0)
    # clears 3d points
    h.pt3dclear()
    # define a logical connection point relative to the first 3-d point
    h.pt3dstyle(axonPts[0][0], axonPts[0][1], axonPts[0][2], axonPts[0][3], sec=self.axon[0])
    # add axon points after first logical connection point
    for x, y, z, d in axonPts[1:]: h.pt3dadd(x, y, z, d, sec=self.axon[0])

  def reconfig (self):
    self.setallprop() # set initial properties, including g_pas,e_pas,cm,Ra,etc.
    self.optimize_nseg() # set nseg based on passive properties
    self.apicchanprop() #  initial apic dend properties
    self.basalchanprop() # initial basal dend properties
    self.setgbarnaxd() # nax in apic,basal dends
    self.setgbarkapd() # kap in apic,basal dends
    self.setgbarkdrd() # kdr in apic,basal dends
    self.sethgbar() # h in all locations
    self.setsomag() # soma-specific conductance values
    self.setaxong() # axon-specific conductance values

  def setallprop (self):
    for sec in self.all:
      # passive
      sec.g_pas       = 1 / rm
      sec.Ra          = rall
      sec.cm          = cap
      sec.e_pas       = Vrest
      # h-current
      h.erev_ih      = h_erev
      # Na current
      sec.gbar_nax    = nax_gbar
      # K delayed rectifier current
      sec.gbar_kdr    = kdr_gbar
      # K-A current
      sec.gbar_kap    = kap_gbar
      sec.vhalfn_kap  = kap_vhalfn 
      sec.vhalfl_kap  = kap_vhalfl   
      sec.tq_kap      = kap_tq     
      # reversal potentials
      sec.ena         = p_ena
      sec.ek          = p_ek

  def setsomag (self):
    for sec in self.soma:
      sec.gcalbar_cal = cal_gcalbar
      sec.gcanbar_can = can_gcanbar
      sec.gcatbar_cat = cat_gcatbar
      sec.gpeak_kBK = kBK_gpeak
      sec.caVhmin_kBK = -46.08 + kBK_caVhminShift
      sec.depth_cadad = cadad_depth
      sec.taur_cadad = cadad_taur
      sec.gbar_nap = nap_gbar
      sec.gbar_ican = ican_gbar

  def setaxong(self):
    # axon has more I_Na, I_KA, I_KDR, and no I_h
    for sec in self.axon:
      # axon has no Ih
      sec.gbar_ih = 0
      # increase the I_Na, I_Ka, and I_KDR
      sec.gbar_nax    = nax_gbar_axonm * nax_gbar
      sec.gbar_kap    = kap_gbar_axonm * kap_gbar
      sec.gbar_kdr    = kdr_gbar_axonm * kdr_gbar

  def setgbarnaxd(self):
    for sec in self.dend: sec.gbar_nax = nax_gbar
    for sec in self.apic: sec.gbar_nax = nax_gbar

  def setgbarkapd(self):
    for sec in self.dend: sec.gbar_kap = kap_gbar
    for sec in self.apic: sec.gbar_kap = kap_gbar

  def setgbarkdrd(self):
    for sec in self.dend: sec.gbar_kdr = kdr_gbar
    for sec in self.apic: sec.gbar_kdr = kdr_gbar

  def sethgbar(self):
    lsec = self.soma + self.apic + self.dend
    for sec in lsec:
      sec.gbar_ih = h_gbar
      sec.ascale_ih = h_ascale
      sec.bscale_ih = h_bscale
      sec.ashift_ih = h_ashift
      sec.aslope_ih = h_aslope
      sec.bslope_ih = h_bslope

  def set_params(self, params):
    global cap
    global kBK_gpeak
    global h_gbar
    global h_bslope
    global rall
    global rm
    global h_bscale
    global h_ashift
    global h_ascale
    global kBK_caVhminShift
    global spinecapfactor
    global h_aslope
    global Vrest
    global v_init
    global nap_gbar
    global ican_gbar
    global kap_gbar
    global cat_gcatbar
    global nax_gbar
    global can_gcanbar
    global kBK_gpeak
    global kap_tq
    global kap_vhalfl
    global cal_gcalbar
    global kdr_gbar

    if params == 'BS1578':
      # properties from subthreshold fits
      cap = 1.08061102459
      kBK_gpeak = 1.01857671029e-08
      h_gbar = 1.52895460186e-05 
      h_bslope = 28.4924968486 
      rall = 169.820315809 
      rm = 34458.8500812 
      h_bscale = 0.158315912545
      h_ashift = 119.088497469 
      h_ascale = 0.00755591656239
      kBK_caVhminShift = 74.643306075
      spinecapfactor = 1.00000193943 
      h_aslope = 7.82783295634 
      Vrest = -93.4020509612 
      h.v_init = -93.4020509612
      nap_gbar = 0.0 
      ican_gbar = 0.0 

      # properties from evolution
      kap_gbar = 0.0648939943904
      cat_gcatbar = 5.09183542632e-05
      nax_gbar = 0.0371377568371
      can_gcanbar = 4.32324870809e-05
      kBK_gpeak = 5.56694789593e-05
      kap_tq = -39.3494405593
      kap_vhalfl = -55.4686026168
      cal_gcalbar = 2.82453671147e-05
      kdr_gbar = 0.00378281934564

      return os.environ['SITE']+'/nrniv/local/morph/BS1578.ASC'

    elif params == 'BS1579':
      # properties from subthreshold fits
      cap = 0.950146286173
      kBK_gpeak = 1.00322132792e-08
      h_gbar = 1.472090636e-05 
      h_bslope = 39.0877074693 
      rall = 138.886815548
      rm = 58383.8130966 
      h_bscale = 0.239679949446
      h_ashift = 106.353947441 
      h_ascale = 0.00600855548467
      kBK_caVhminShift = 61.4360979639
      spinecapfactor = 1.00093462207 
      h_aslope = 5.84695325827 
      Vrest = -79.2637828106 
      h.v_init = -79.2637828106
      nap_gbar = 0.0 
      ican_gbar = 0.0

      # properties from evolution
      kap_gbar = 0.0478807757046
      cat_gcatbar = 4.4250857809e-05
      nax_gbar = 0.0237052062208
      can_gcanbar = 2.8760466502e-05
      kBK_gpeak = 0.000583328963048
      kap_tq = -36.6802561086
      kap_vhalfl = -37.3347304488
      cal_gcalbar = 3.9810325062e-05
      kdr_gbar = 0.00382910493766

      return os.environ['SITE']+'/nrniv/local/morph/BS1579.ASC'


