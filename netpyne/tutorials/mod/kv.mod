: $Id: kv.mod,v 1.9 2004/07/28 21:25:39 billl Exp $

COMMENT
26 Ago 2002 Modification of original channel to allow variable time step and to correct an initialization error.
Done by Michael Hines(michael.hines@yale.e) and Ruggero Scorcioni(rscorcio@gmu.edu) at EU Advance Course in Computational Neuroscience. Obidos, Portugal

kv.mod

Potassium channel, Hodgkin-Huxley style kinetics
Kinetic rates based roughly on Sah et al. and Hamill et al. (1991)

Author: Zach Mainen, Salk Institute, 1995, zach@salk.edu

ENDCOMMENT

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
  SUFFIX kv
  USEION k READ ek WRITE ik
  RANGE  n, i, gk, gmax
  GLOBAL ninf, ntau
  GLOBAL Ra, Rb
  GLOBAL q10, temp, tadj
}

UNITS {
  (mA) = (milliamp)
  (mV) = (millivolt)
  (pS) = (picosiemens)
  (um) = (micron)
} 

PARAMETER {
  gmax = 5   	(pS/um2)	: 0.03 mho/cm2
  v 		(mV)
  
  tha  = 25	(mV)		: v 1/2 for inf
  qa   = 9	(mV)		: inf slope		
  
  Ra   = 0.02	(/ms)		: max act rate
  Rb   = 0.002	(/ms)		: max deact rate	

  dt		(ms)
  celsius		(degC)
  temp = 23	(degC)		: original temp 	
  q10  = 2.3			: temperature sensitivity

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



DERIVATIVE  states {   :Computes state variable n 
  rates(v)      :             at the current v and dt.
  n' =  (ninf-n)/ntau
}

PROCEDURE rates(v) {  :Computes rate and other constants at current v.
  :Call once from HOC to initialize inf at resting v.

  a = trap0(v,tha,Ra,qa)
  b = trap0(v,tha,-Rb,-qa)
  ntau = 1/tadj/(a+b)
  ninf = a/(a+b)
}

FUNCTION trap0(v,th,a,q) {
  if (fabs(v-th) > 1e-6) {
    trap0 = a * (v - th) / (1 - exp(-(v - th)/q))
  } else {
    trap0 = a * q
  }
}	
