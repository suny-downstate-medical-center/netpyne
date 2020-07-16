# simplified corticostriatal cell model (6 compartment)
from neuron import h

h.load_file('stdrun.hoc')

Vrest = -90.7942106535
h.v_init = -75.8801688855
h.celsius     = 34.0 # for in vitro opt

# these are to be used by h_kole.mod
h_aslope = 7.12195833953
h_ascale  =  0.00276508832116
h_bslope  =  28.5415800392
h_bscale  =  0.154401580683
h_ashift  =  118.919921764

# geom properties
somaL = 25.0612875049
somaDiam = 27.1149930518
axonL = 598.648623864
axonDiam =  0.552948640016
apicL = 294.615634554
apicDiam = 2.86090460606
bdendL = 265.920165144
bdendDiam = 1.02617341611

# passive properties 
axonCap =  1.98999103645
somaCap =  1.98838095104
apicCap = 1.9931856141
bdendCap = 1.98526067401
rall = 88.8088669637
axonRM = 2426.70520092
somaRM = 11399.5571402
apicRM = 12053.0391655
bdendRM = 23023.3272552

# Na, K reversal potentials calculated from BenS internal/external solutions via Nernst eq.
p_ek = -104.0 # these reversal potentials for in vitro conditions
p_ena = 42.0 
# h-current
#h.erev_h = h.erev_ih = -37.0 # global
gbar_h = 9.99986721729e-06

# spiking currents
gbar_nax = 0.0345117294903
nax_gbar_axonm = 5.0
gbar_kdr = 0.0131103978049
kdr_gbar_axonm = 5.0
# A few kinetic params changed vis-a-vis kdr.mod defaults:
kdr_vhalfn = 11.6427471384
gbar_kap = 0.0898600246397
kap_gbar_axonm = 5.0
# A few kinetic params changed vis-a-vis kap.mod defaults:
kap_vhalfn  = 32.7885075379
kap_tq      = -52.0967985869
kap_vhalfl = -59.7867409796 # 

# other ion channel parameters 
cal_gcalbar = 4.41583533572e-06
can_gcanbar = 4.60717910591e-06
cat_gcatbar = 1.00149259311e-06
calginc = 1.0
kBK_gpeak = 5.09733585163e-05
kBK_caVhminShift = 43.8900261407
cadad_depth = 0.119408607923
cadad_taur = 99.1146852282 

gbar_nap = 0.00301840094235
gbar_ican = 0.000106856758751
			
###############################################################################
# CSTR6 Cell
###############################################################################
class CSTR6 ():
  "Simplified Corticostriatal Cell Model"
  def __init__(self,x=0,y=0,z=0,ID=0,params=None):
    self.x,self.y,self.z=x,y,z
    self.ID=ID
    self.all_sec = []
    self.add_comp('soma')
    self.set_morphology()
    self.insert_conductances()
    if params: self.set_params(params)
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
    axon.gbar_nax = gbar_nax * nax_gbar_axonm
    axon.gbar_kdr = gbar_kdr * kdr_gbar_axonm
    axon.gbar_kap = gbar_kap * kap_gbar_axonm

  def set_calprops (self,sec):
    sec.gcalbar_cal = cal_gcalbar 
    sec.gcanbar_can = can_gcanbar 
    sec.gcatbar_cat = cat_gcatbar
    sec.gpeak_kBK = kBK_gpeak
    sec.caVhmin_kBK = -46.08 + kBK_caVhminShift
    sec.depth_cadad = cadad_depth
    sec.taur_cadad = cadad_taur   
    #sec.gbar_ican = gbar_ican

  def set_somag (self):
    sec = self.soma
    sec.gbar_ih = gbar_h # Ih
    self.set_calprops(sec)
    #sec.gbar_nap = gbar_nap

  def set_bdendg (self): 
    sec = self.Bdend
    sec.gbar_ih = gbar_h # Ih
    #sec.gbar_nap = gbar_nap
    self.set_calprops(sec)

  def set_apicg (self):
    for sec in self.apic:
      self.set_calprops(sec)
      sec.gbar_ih = gbar_h
      #sec.gbar_nap = gbar_nap
    self.apic[1].gcalbar_cal = cal_gcalbar * calginc # middle apical dend gets more iL

  def set_ihkinetics (self):
    for sec in [self.soma,self.Bdend,self.Adend1,self.Adend2,self.Adend3]:
      sec.ascale_ih = h_ascale
      sec.bscale_ih = h_bscale
      sec.ashift_ih = h_ashift
      sec.aslope_ih = h_aslope
      sec.bslope_ih = h_bslope

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
    self.set_ihkinetics()

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
      sec.insert('cat') # cat_mig.mod
      sec.insert('cadad') # cadad.mod - calcium decay 
      sec.insert('kBK') # kBK.mod - ca and v dependent k channel
      #sec.insert('nap') # nap_sidi.mod
      #sec.insert('ican') # ican_sidi.mod

  # set parameters tuned to specific cell
  def set_params(self, params):
    global h
    global axonRM
    global somaRM
    global apicRM
    global bdendRM
    global rall
    global Vrest
    global gbar_h
    global axonCap
    global somaCap
    global apicCap
    global bdendCap
    global somaL
    global somaDiam
    global apicL
    global apicDiam
    global bdendL
    global bdendDiam
    global axonL
    global axonDiam
    global h_ascale
    global h_bscale
    global h_ashift
    global h_aslope
    global h_bslope
    global gbar_nap
    global gbar_ican
    global kap_vhalfn
    global kBK_caVhminShift
    global kBK_gpeak
    global kap_vhalfl
    global gbar_kap
    global gbar_kdr
    global cal_gcalbar
    global kap_tq
    global gbar_nax
    global can_gcanbar
    global cat_gcatbar

    if params == 'BS1578':
      # properties from subthreshold fits
      axonRM = 2822.01325416
      somaRM = 10590.6461169
      apicRM = 13889.6757076
      bdendRM = 7068.31281683
      rall = 70.0015514222 
      Vrest = -87.1335623948
      h.v_init = -88.7986728464 
      gbar_h = 3.3176340367e-05
      axonCap = 2.4630760526 
      somaCap = 2.4998269977 
      apicCap = 2.74242941886 
      bdendCap = 2.74086279376 
      somaL = 48.4123467666 
      somaDiam = 28.2149102762
      apicL = 261.904636003 
      apicDiam = 1.5831889597
      bdendL = 299.810775175 
      bdendDiam = 2.2799248874
      axonL = 594.292937602  
      axonDiam = 1.40966286462 
      h_ascale = 0.00320887293027
      h_bscale = 0.285307415701 
      h_ashift = 119.696272155 
      h_aslope = 7.09800576233 
      h_bslope = 23.2995848558 
      gbar_nap = 0.0 
      gbar_ican = 0.0 
      kap_vhalfn = 32.179925527
      kBK_caVhminShift = 89.9991422912

      # properties from evolution
      kBK_gpeak = 4.45651933019e-05
      kap_vhalfl = -36.7754836348
      gbar_kap = 0.0240195239098
      gbar_kdr = 0.00833766634808
      cal_gcalbar = 2.39132864454e-06
      kap_tq = -49.7149526489
      gbar_nax = 0.0768253702194
      can_gcanbar = 8.13137955053e-07
      cat_gcatbar = 9.29455717585e-07

    elif params == 'BS1579':
      # properties from subthreshold fits
      axonRM = 3120.59603524
      somaRM = 25551.9729631
      apicRM = 48333.5799025
      bdendRM = 11763.9607778
      rall = 114.969186163 
      Vrest = -79.8821836579
      h.v_init = -92.8364820902 
      gbar_h = 3.13760461868e-05
      axonCap = 1.87389705992 
      somaCap = 1.89133252551 
      apicCap = 2.49841939531 
      bdendCap = 2.46671987855
      somaL = 48.4123467666 
      somaDiam = 28.2149102762
      apicL = 261.904636003 
      apicDiam = 1.5831889597
      bdendL = 299.810775175 
      bdendDiam = 2.2799248874
      axonL = 594.292937602  
      axonDiam = 1.40966286462
      h_ascale = 0.00365676240119
      h_bscale = 0.26993550346 
      h_ashift = 115.040811905 
      h_aslope = 7.63692206734 
      h_bslope = 37.2740194128 
      gbar_nap = 0.0 
      gbar_ican = 0.0 

      # properties from evolution
      kBK_gpeak = 4.2923494376e-05
      kap_vhalfl = -78.3762490029
      gbar_kap = 0.306752147542
      gbar_kdr = 0.00501206206504
      cal_gcalbar = 7.79902252875e-05
      kap_tq = -55.772342395
      gbar_nax = 0.146326621958
      can_gcanbar = 8.43780573752e-05
      cat_gcatbar = 5.85477866612e-05


#
def prmstr (p,s,fctr=2.0,shift=5.0):
  if p == 0.0:
    print (s,'=',str(p-shift),str(p+shift),str(p),'True')
  elif p < 0.0:
    print (s, '=',str(p*fctr),str(p/fctr),str(p),'True')
  else:
    print (s, ' = ' , str(p/fctr), str(p*fctr), str(p), 'True')

