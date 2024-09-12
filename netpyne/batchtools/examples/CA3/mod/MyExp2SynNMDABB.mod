: $Id: MyExp2SynNMDABB.mod,v 1.4 2010/12/13 21:28:02 samn Exp $ 
NEURON {
:  THREADSAFE
  POINT_PROCESS MyExp2SynNMDABB
  RANGE tau1, tau2, e, i, iNMDA, s, sNMDA, r, tau1NMDA, tau2NMDA, Vwt, smax, sNMDAmax
  NONSPECIFIC_CURRENT i, iNMDA
}

UNITS {
  (nA) = (nanoamp)
  (mV) = (millivolt)
  (uS) = (microsiemens)
}

PARAMETER {
  tau1     =   0.1 (ms) <1e-9,1e9>
  tau2     =  10 (ms) <1e-9,1e9>	
  tau1NMDA = 15  (ms)
  tau2NMDA = 150 (ms)
  e        = 0	(mV)
  mg       = 1
  r        = 1
  smax     = 1e9 (1)
  sNMDAmax = 1e9 (1)
  
  Vwt   = 0 : weight for inputs coming in from vector
}

ASSIGNED {
  v       (mV)
  i       (nA)
  iNMDA   (nA)
  s       (1)
  sNMDA   (1)
  mgblock (1)
  factor  (1)
  factor2 (1)
	
  etime (ms)
}

STATE {
  A  (1)
  B  (1)
  A2 (1)
  B2 (1)
}

INITIAL {

  LOCAL tp
  
  Vwt = 0 : testing

  if (tau1/tau2 > .9999) {
    tau1 = .9999*tau2
  }
  A = 0
  B = 0	
  tp = (tau1*tau2)/(tau2 - tau1) * log(tau2/tau1)
  factor = -exp(-tp/tau1) + exp(-tp/tau2)
  factor = 1/factor
  
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
  SOLVE state METHOD cnexp
  : Jahr Stevens 1990 J. Neurosci
  mgblock = 1.0 / (1.0 + 0.28 * exp(-0.062(/mV) * v) )
  s     = B  - A
  sNMDA = B2 - A2
  if (s    >smax)     {s    =smax    }: saturation
  if (sNMDA>sNMDAmax) {sNMDA=sNMDAmax}: saturation
  i     = s     * (v - e) 
  iNMDA = sNMDA * (v - e) * mgblock
}

DERIVATIVE state {
  A'  = -A/tau1
  B'  = -B/tau2	
  A2' = -A2/tau1NMDA
  B2' = -B2/tau2NMDA
}

NET_RECEIVE(w (uS)) {LOCAL ww
  ww=w
  :printf("NMDA Spike: %g\n", t)
  if(r>=0){ : if r>=0, g = AMPA + NMDA*r
    A  = A  + factor *ww
    B  = B  + factor *ww
    A2 = A2 + factor2*ww*r
    B2 = B2 + factor2*ww*r
  }else{
    if(r>-1000){ : if r>-1, g = NMDA*r  
      A2 = A2 - factor2*ww*r
      B2 = B2 - factor2*ww*r
    }
    : if r<0 and r<>-1, g = 0
  }
}
