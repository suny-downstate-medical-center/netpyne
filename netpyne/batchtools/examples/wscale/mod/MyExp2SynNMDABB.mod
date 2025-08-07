: $Id: MyExp2SynNMDABB.mod,v 1.4 2010/12/13 21:28:02 samn Exp $ 
NEURON {
:  THREADSAFE
  POINT_PROCESS MyExp2SynNMDABB
  RANGE e, i, iNMDA, s, sNMDA, r, tau1NMDA, tau2NMDA, Vwt, smax, sNMDAmax, g
  NONSPECIFIC_CURRENT iNMDA
  USEION ca READ cai,cao WRITE ica
  GLOBAL fracca
  RANGE ica
}

UNITS {
  (nA) = (nanoamp)
  (mV) = (millivolt)
  (uS) = (microsiemens)
  FARADAY = (faraday) (coulomb)
  R = (k-mole) (joule/degC)
}

PARAMETER {
  tau1NMDA = 15  (ms)
  tau2NMDA = 150 (ms)
  e        = 0	(mV)
  r        = 1
  smax     = 1e9 (1)
  sNMDAmax = 1e9 (1)  
  Vwt   = 0 : weight for inputs coming in from vector
  fracca = 0.13 : fraction of current that is ca ions; Srupuston &al 95
}

ASSIGNED {
  v       (mV)
  iNMDA   (nA)
  sNMDA   (1)
  mgblock (1)
  factor2 (1)	
  ica	  (nA)
  cai     (mM)
  cao     (mM)
  g       (umho)
}

STATE {
  A2 (1)
  B2 (1)
}

INITIAL {
  LOCAL tp
  Vwt = 0 : testing
  if (tau1NMDA/tau2NMDA > .9999) {
    tau1NMDA = .9999*tau2NMDA
  }
  A2 = 0
  B2 = 0	
  tp = (tau1NMDA*tau2NMDA)/(tau2NMDA - tau1NMDA) * log(tau2NMDA/tau1NMDA)
  factor2 = -exp(-tp/tau1NMDA) + exp(-tp/tau2NMDA)
  factor2 = 1/factor2  
}

BREAKPOINT {
  LOCAL iTOT
  SOLVE state METHOD cnexp
  : Jahr Stevens 1990 J. Neurosci
  mgblock = 1.0 / (1.0 + 0.28 * exp(-0.062(/mV) * v) )
  sNMDA = B2 - A2
  if (sNMDA>sNMDAmax) {sNMDA=sNMDAmax}: saturation

  :iTOT = sNMDA * (v - e) * mgblock  
  :iNMDA = iTOT * (1-fracca)
  :ica = iTOT * fracca
  
  iNMDA = sNMDA * (v - e) * mgblock * (1-fracca)
  if(fracca>0.0){ica =   sNMDA * ghkg(v,cai,cao,2) * mgblock * fracca}
  g = sNMDA * mgblock
}

INCLUDE "ghk.inc"

DERIVATIVE state {
  A2' = -A2/tau1NMDA
  B2' = -B2/tau2NMDA
}

NET_RECEIVE(w (uS)) {LOCAL ww
  ww=w
  :printf("NMDA Spike: %g\n", t)
  if(r>=0){ : if r>=0, g = NMDA*r
    A2 = A2 + factor2*ww*r
    B2 = B2 + factor2*ww*r
  }
}
