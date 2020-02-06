TITLE Ih-current
: modified from http://senselab.med.yale.edu/ModelDB/showmodel.cshtml?model=64195&file=%5cStochastic%5cStochastic_Na%5cih.mod
: /u/samn/papers/jnsci_26_1677.pdf
: 
: @article{kole2006single,
:  title={Single Ih channels in pyramidal neuron dendrites: properties, distribution, and impact on action potential output},
:  author={Kole, M.H.P. and Hallermann, S. and Stuart, G.J.},
:  journal={The Journal of neuroscience},
:  volume={26},
:  number={6},
:  pages={1677--1687},
:  year={2006},
:  publisher={Soc Neuroscience}
: }

COMMENT
Author: Stefan Hallermann; modified by Sam Neymotin (parameterized)
Provides deterministic Ih-currents as described in Kole et al. (2006).
ENDCOMMENT

UNITS {
  (mA) = (milliamp)
  (mV) = (millivolt)
}

PARAMETER {
  v (mV)
  erev=-45  		(mV) 	:ih-reversal potential			       
  gbar=0.00015 	(S/cm2)	:default Ih conductance; exponential distribution is set in Ri18init.hoc 
  q10 = 2.2
  ascale = 0.00643
  bscale = 0.193
  ashift = 154.9
  aslope = 11.9
  bslope = 33.1
}

NEURON {
 THREADSAFE
  SUFFIX ih
  NONSPECIFIC_CURRENT i
  RANGE i,gbar,ascale,bscale,ashift,aslope,bslope
}

STATE {
  m
}

ASSIGNED {
  i (mA/cm2)
}

INITIAL { LOCAL a,b
  a = alpha(v)
  b = beta(v)
  m = a / (a + b)
}

BREAKPOINT {
  SOLVE state METHOD cnexp
  i = gbar*m*(v-erev)
}

: tau = 1 / (alpha + beta)
FUNCTION alpha(v(mV)) {
  alpha = ascale*(v+ashift)/(exp((v+ashift)/aslope)-1)  
  :parameters are estimated by direct fitting of HH model to activation time constants and voltage activation curve recorded at 34C
}

FUNCTION beta(v(mV)) {
  beta = bscale*exp(v/bslope)
}

DERIVATIVE state {
  m' = (1-m)*alpha(v) - m*beta(v)
}
