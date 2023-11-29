TITLE Slow Ca-dependent cation current
: from
:  https://senselab.med.yale.edu/ModelDB/ShowModel.cshtml?model=144089&file=/PFCcell/mechanism/ican.mod
:
:   Ca++ dependent nonspecific cation current ICAN
:   Differential equations
:
:   Model based on a first order kinetic scheme
:
:       + n cai <->     (alpha,beta)
:
:   Following this model, the activation fct will be half-activated at 
:   a concentration of Cai = (beta/alpha)^(1/n) = cac (parameter)
:
:   The mod file is here written for the case n=2 (2 binding sites)
:   ---------------------------------------------
:
:   Kinetics based on: Partridge & Swandulla, TINS 11: 69-72, 1988.
:
:   This current has the following properties:
:      - inward current (non specific for cations Na, K, Ca, ...)
:      - activated by intracellular calcium
:      - NOT voltage dependent
:
:   A minimal value for the time constant has been added
:
:   Ref: Destexhe et al., J. Neurophysiology 72: 803-818, 1994.
:   See also:  http://www.cnl.salk.edu/~alain , http://cns.fmed.ulaval.ca
:

: Updated by Kiki Sidiropoulou (2010) so that dADP has slow inactivation kinetics and it
: is activated after 5 spikes

: Updated by Sam Neymotin (2016) to avoid using n ion and get rid of 'mystart' rule; also
: make sure that INITIAL block assigns currents

NEURON {
  SUFFIX ican
  NONSPECIFIC_CURRENT i
  USEION ca READ cai
  USEION na WRITE ina
  RANGE gbar, m_inf, tau_m
  GLOBAL beta, cac, taumin
}

UNITS {
  (mA) = (milliamp)
  (mV) = (millivolt)
  (molar) = (1/liter)
  (mM) = (millimolar)
}

PARAMETER {
  v               (mV)
  celsius = 36    (degC)
  erev      = -20   (mV)            	: reversal potential
  cai     	     (mM)           	: initial [Ca]i
  gbar    = 0.0001 (mho/cm2)
  beta    = 0.0001 (1/ms) 	 	: backward rate constant
  cac     = 0.0004 (mM)
  : middle point of activation fct, for ip3 as somacar, for current injection
  taumin  = 0.1   (ms)            	: minimal value of time constant
}

STATE {
  m
}

ASSIGNED {
  i      (mA/cm2)
  ina     (mA/cm2)
  m_inf
  tau_m   (ms)
  tadj
  g (mho/cm2)
}

PROCEDURE iassign () {
  g = gbar * m * m
  i = g * (v - erev) 
  ina = 0.7 * i
}

BREAKPOINT { 
  SOLVE states METHOD cnexp  
  iassign()
}

DERIVATIVE states { 
  evaluate_fct(v,cai)  
  m' = (m_inf - m) / tau_m
}

UNITSOFF
INITIAL {
  :  activation kinetics are assumed to be at 22 deg. C
  :  Q10 is assumed to be 3
  tadj = 3.0 ^ ((celsius-22.0)/10)  
  evaluate_fct(v,cai)
  m = m_inf
  iassign()
}

PROCEDURE evaluate_fct(v(mV),cai(mM)) {  LOCAL alpha2  
  alpha2 = beta * (cai/cac)^2  
  tau_m = 1 / (alpha2 + beta) / tadj
  m_inf = alpha2 / (alpha2 + beta)  
  if(tau_m < taumin) { tau_m = taumin } : min value of time constant
}
UNITSON
