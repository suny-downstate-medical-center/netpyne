: $Id: iholmw.mod,v 1.5 2013/01/02 16:02:37 samn Exp $ 
COMMENT

//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
//
// NOTICE OF COPYRIGHT AND OWNERSHIP OF SOFTWARE
//
// Copyright 2007, The University Of Pennsylvania
// 	School of Engineering & Applied Science.
//   All rights reserved.
//   For research use only; commercial use prohibited.
//   Distribution without permission of Maciej T. Lazarewicz not permitted.
//   mlazarew@seas.upenn.edu
//
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

ENDCOMMENT

UNITS {
  (mA) = (milliamp)
  (mV) = (millivolt)
}

NEURON {
  SUFFIX Iholmw
  NONSPECIFIC_CURRENT i
  RANGE gbar,gh,eh,gfactor
}
	
PARAMETER {
  gbar = 0.00015 (mho/cm2)
  eh = -40  (mV)
  gfactor = 1
}
    
ASSIGNED { 
  v (mV)
  i (mA/cm2)
  gh (mho/cm2)
}

STATE { q }

PROCEDURE giassign () { 
  : i = (1e-3) * gh * q * (v-eh) * gfactor 
  gh = gbar * q * gfactor 
  i =  gh * (v-eh)
}

INITIAL { 
  q  = qinf(v) 
  giassign()
}

BREAKPOINT {
  SOLVE states METHOD cnexp
  giassign()
}

DERIVATIVE states { q' = (qinf(v)-q)/qtau(v) }

FUNCTION qinf(v(mV))     { qinf = fun2(v, -80, 1, 10)*1(ms) }
FUNCTION qtau(v(mV))(ms) { qtau = 200(ms)/(exp((v+70(mV))/20(mV))+exp(-(v+70(mV))/20(mV))) + 5(ms) }

INCLUDE "aux_fun.inc"
