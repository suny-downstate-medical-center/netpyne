: $Id: km.mod,v 1.5 2004/06/08 21:07:12 billl Exp $

COMMENT
26 Ago 2002 Modification of original channel to allow variable time step and to correct an initialization error.
Done by Michael Hines(michael.hines@yale.e) and Ruggero Scorcioni(rscorcio@gmu.edu) at EU Advance Course in Computational Neuroscience. Obidos, Portugal

km.mod

Potassium channel, Hodgkin-Huxley style kinetics
Based on I-M (muscarinic K channel)
Slow, noninactivating

Author: Zach Mainen, Salk Institute, 1995, zach@salk.edu

ENDCOMMENT

NEURON {
  SUFFIX km
  USEION k READ ek WRITE ik
  RANGE n, gk, gmax, i
  RANGE ninf, ntau, tadj
  GLOBAL Ra, Rb
  GLOBAL q10, temp, vmin, vmax
}

UNITS {
  (mA) = (milliamp)
  (mV) = (millivolt)
  (pS) = (picosiemens)
  (um) = (micron)
} 

PARAMETER {
  gmax = 10   	(pS/um2)	: 0.03 mho/cm2
  v 		(mV)
  
  tha  = -30	(mV)		: v 1/2 for inf
  qa   = 9	(mV)		: inf slope		
  
  Ra   = 0.001	(/ms)		: max act rate  (slow)
  Rb   = 0.001	(/ms)		: max deact rate  (slow)

  dt		(ms)
  celsius		(degC)
  temp = 23	(degC)		: original temp 	
  q10  = 2.3			: temperature sensitivity

  vmin = -120	(mV)
  vmax = 100	(mV)
} 


ASSIGNED {
  a		(/ms)
  b		(/ms)
  i 		(mA/cm2)
  ik 		(mA/cm2)
  gk		(pS/um2)
  ek		(mV)
  ninf
  ntau (ms)	
  tadj
}

STATE { n }

INITIAL { 
  tadj = q10^((celsius - temp)/10)
  rates(v)
  n = ninf
}

BREAKPOINT {
  SOLVE states METHOD cnexp
  gk = tadj*gmax*n
  i = (1e-4) * gk * (v - ek)
  ik = i
} 

LOCAL nexp

DERIVATIVE states {   :Computes state variable n 
  rates(v)      :             at the current v and dt.
  n' = (ninf-n)/ntau

}

PROCEDURE rates(v) {  :Computes rate and other constants at current v.
  :Call once from HOC to initialize inf at resting v.

  a = Ra * (v - tha) / (1 - exp(-(v - tha)/qa))
  b = -Rb * (v - tha) / (1 - exp((v - tha)/qa))

  ntau = 1/tadj/(a+b)
  ninf = a/(a+b)
}

