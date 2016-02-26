"""
IZHI

Python wrappers for the different celltypes of Izhikevich neuron. 
Equations and parameter values taken from
  Izhikevich EM (2007). "Dynamical systems in neuroscience", MIT Press
Equation for synaptic inputs taken from
  Izhikevich EM, Edelman GM (2008). "Large-scale model of mammalian thalamocortical systems." PNAS 105(9) 3593-3598.

Cell types available are based on Izhikevich, 2007 book:
    1. RS - Layer 5 regular spiking pyramidal cell (fig 8.12 from 2007 book)
    2. IB - Layer 5 intrinsically bursting cell (fig 8.19 from 2007 book)
    3. CH - Cat primary visual cortex chattering cell (fig8.23 from 2007 book)
    4. LTS - Rat barrel cortex Low-threshold  spiking interneuron (fig8.25 from 2007 book)
    5. FS - Rat visual cortex layer 5 fast-spiking interneuron (fig8.27 from 2007 book)
    6. TC - Cat dorsal LGN thalamocortical (TC) cell (fig8.31 from 2007 book)
    7. RTN - Rat reticular thalamic nucleus (RTN) cell  (fig8.32 from 2007 book)
"""

import collections
from neuron import h
dummy = h.Section()
type2003 = collections.OrderedDict([
  #                                 a         b     c         d      
 ('tonic spiking'               , (0.02   ,  0.2 , -65.0 ,   6.0)) ,
 ('mixed mode'                  , (0.02   ,  0.2 , -55.0 ,   4.0)) ,
 ('spike latency'               , (0.02   ,  0.2 , -65.0 ,   6.0)) ,
 ('rebound spike'               , (0.03   , 0.25 , -60.0 ,   4.0)) ,
 ('Depolarizing afterpotential' , (1.0    ,  0.2 , -60.0 , -21.0)) ,
 ('phasic spiking'              , (0.02   , 0.25 , -65.0 ,   6.0)) ,
 ('spike frequency adaptation'  , (0.01   ,  0.2 , -65.0 ,   8.0)) ,
 ('subthreshold oscillations'   , (0.05   , 0.26 , -60.0 ,   0.0)) ,
 ('rebound burst'               , (0.03   , 0.25 , -52.0 ,   0.0)) ,
 ('accomodation'                , (0.02   ,  1.0 , -55.0 ,   4.0)) ,
 ('tonic bursting'              , (0.02   ,  0.2 , -50.0 ,   2.0)) ,
 ('Class 1'                     , (0.02   , -0.1 , -55.0 ,   6.0)) ,
 ('resonator'                   , (0.1    , 0.26 , -60.0 ,  -1.0)) ,
 ('threshold variability'       , (0.03   , 0.25 , -60.0 ,   4.0)) ,
 ('inhibition-induced spiking'  , (-0.02  , -1.0 , -60.0 ,   8.0)) ,
 ('phasic bursting'             , (0.02   , 0.25 , -55.0 ,  0.05)) ,
 ('Class 2'                     , (0.2    , 0.26 , -65.0 ,   0.0)) ,
 ('integrator'                  , (0.02   , -0.1 , -55.0 ,   6.0)) ,
 ('bistability'                 , (0.1    , 0.26 , -60.0 ,   0.0)) ,
 ('inhibition-induced bursting' , (-0.026 , -1.0 , -45.0 ,  -2.0))])

# class of basic Izhikevich neuron based on parameters in type2003
class IzhiCell (): 
  '''Create an izhikevich cell based on 2007 parameterization using either izhi2007.mod (no hosting section) or izhi2007b.mod (v in created section)
  If host is omitted or None, this will be a section-based version that uses Izhi2007b with state vars v, u where v is the section voltage
  If host is given then this will be a shared unused section that simply houses an Izhi2007 using state vars V and u
  Note: Capacitance 'C' differs from sec.cm which will be 1; vr is RMP; vt is threshold; vpeak is peak voltage
'''

  def __init__ (self, type='tonic spiking', host=None, cellid=-1):
    self.type=type
    if host is None:  # need to set up a sec for this
      self.sec=h.Section(name='izhi2003'+type+str(cellid))
      self.sec.L, self.sec.diam = 6.3, 5 # empirically tuned
      self.izh = h.Izhi2003b(0.5, sec=self.sec) 
    else: 
      self.sec = dummy
      self.izh = h.Izhi2003a(0.5, sec=self.sec) # Create a new u,V 2007 neuron at location 0.5 (doesn't matter where) 

    self.izh.a,self.izh.b,self.izh.c,self.izh.d = type2003[type]
    self.izh.Iin = 0
   
  def init (self): self.sec(0.5).v = self.vinit

  def reparam (self, type='tonic spiking', cellid=-1):
    self.type=type
    self.izh.a,self.izh.b,self.izh.c,self.izh.d = type2003[type]
   