: $Id: Nca.mod,v 1.7 2004/06/08 21:07:12 billl Exp $

COMMENT
26 Ago 2002 Modification of original channel to allow variable time step and to correct an initialization error.
Done by Michael Hines(michael.hines@yale.e) and Ruggero Scorcioni(rscorcio@gmu.edu) at EU Advance Course in Computational Neuroscience. Obidos, Portugal

ca.mod
Uses fixed eca instead of GHK eqn

HVA Ca current
Based on Reuveni, Friedman, Amitai and Gutnick (1993) J. Neurosci. 13:
4609-4621.

Author: Zach Mainen, Salk Institute, 1994, zach@salk.edu

ENDCOMMENT

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
  SUFFIX Nca
  USEION ca READ eca WRITE ica
  RANGE i, m, h, gca, gmax
  RANGE minf, hinf, mtau, htau
  GLOBAL q10, temp, tadj, vmin, vmax, vshift
}

PARAMETER {
  gmax = 0.1   	(pS/um2)	: 0.12 mho/cm2
  vshift = 0	(mV)		: voltage shift (affects all)

  cao  = 2.5	(mM)	        : external ca concentration
  cai		(mM)
  
  temp = 23	(degC)		: original temp 
  q10  = 2.3			: temperature sensitivity

  v 		(mV)
  dt		(ms)
  celsius		(degC)
  vmin = -120	(mV)
  vmax = 100	(mV)
}


UNITS {
  (mA) = (milliamp)
  (mV) = (millivolt)
  (pS) = (picosiemens)
  (um) = (micron)
  FARADAY = (faraday) (coulomb)
  R = (k-mole) (joule/degC)
  PI	= (pi) (1)
} 

ASSIGNED {
  i 		(mA/cm2)
  ica 		(mA/cm2)
  gca		(pS/um2)
  eca		(mV)
  minf 		hinf
  mtau (ms)	htau (ms)
  tadj
}


STATE { m h }

INITIAL { 
  tadj = q10^((celsius - temp)/10)
  rates(v+vshift)
  m = minf
  h = hinf
}

BREAKPOINT {
  SOLVE states METHOD cnexp
  gca = tadj*gmax*m*m*h
  i = (1e-4) * gca * (v - eca)
  ica = i
} 

LOCAL mexp, hexp

:PROCEDURE states() {
  :        rates(v+vshift)      
  :        m = m + mexp*(minf-m)
  :        h = h + hexp*(hinf-h)
  :	VERBATIM
  :	return 0;
  :	ENDVERBATIM
  :}

  DERIVATIVE states {
    rates(v+vshift)      
    m' =  (minf-m)/mtau
    h' =  (hinf-h)/htau
  }

  PROCEDURE rates(vm) {  
    LOCAL  a, b

    a = 0.055*(-27 - vm)/(exp((-27-vm)/3.8) - 1)
    b = 0.94*exp((-75-vm)/17)
    
    mtau = 1/tadj/(a+b)
    minf = a/(a+b)

    :"h" inactivation 

    a = 0.000457*exp((-13-vm)/50)
    b = 0.0065/(exp((-vm-15)/28) + 1)

    htau = 1/tadj/(a+b)
    hinf = a/(a+b)
  }

  FUNCTION efun(z) {
    if (fabs(z) < 1e-4) {
      efun = 1 - z/2
    }else{
      efun = z/(exp(z) - 1)
    }
  }
