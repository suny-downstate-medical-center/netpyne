: $Id: kca.mod,v 1.5 2004/06/08 21:07:12 billl Exp $

COMMENT
26 Ago 2002 Modification of original channel to allow variable time step and to correct an initialization error.
Done by Michael Hines(michael.hines@yale.e) and Ruggero Scorcioni(rscorcio@gmu.edu) at EU Advance Course in Computational Neuroscience. Obidos, Portugal

kca.mod

Calcium-dependent potassium channel
Based on
Pennefather (1990) -- sympathetic ganglion cells
taken from
Reuveni et al (1993) -- neocortical cells

Author: Zach Mainen, Salk Institute, 1995, zach@salk.edu

ENDCOMMENT

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
  SUFFIX kca
  USEION k READ ek WRITE ik
  USEION ca READ cai
  RANGE i, n, gk, gmax
  RANGE ninf, ntau
  GLOBAL Ra, Rb, caix
  GLOBAL q10, temp, tadj, vmin, vmax
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
  cai  		(mM)
  caix = 1	
  
  Ra   = 0.01	(/ms)		: max act rate  
  Rb   = 0.02	(/ms)		: max deact rate 

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
  ntau 		(ms)	
  tadj
}


STATE { n }

INITIAL { 
  tadj = q10^((celsius - temp)/10)
  rates(cai)
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
  rates(cai)      :             at the current v and dt.
  n' =  (ninf-n)/ntau

}

PROCEDURE rates(cai(mM)) {  
  a = Ra * cai : ^caix 1
  b = Rb
  ntau = 1/tadj/(a+b)
  ninf = a/(a+b)
  :        tinc = -dt * tadj
  :        nexp = 1 - exp(tinc/ntau)
}
