: $Id: iholmw.mod,v 1.2 2010/11/30 16:34:22 samn Exp $ 
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
  (mS) = (millisiemens)
}

NEURON {
  SUFFIX Iholmw
  NONSPECIFIC_CURRENT i
  RANGE gh,eh
}
	
PARAMETER {
  gh = 0.15 (mS/cm2)
  eh = -40  (mV)
}
    
ASSIGNED { 
  v (mV)
  i (mA/cm2)
}

STATE { q }

PROCEDURE iassign () { i = (1e-3) * gh * q * (v-eh) }

INITIAL { 
  q  = qinf(v) 
  iassign()
}

BREAKPOINT {
  SOLVE states METHOD cnexp
  iassign()
}

DERIVATIVE states { q' = (qinf(v)-q)/qtau(v) }

FUNCTION qinf(v(mV))     { qinf = fun2(v, -80, 1, 10)*1(ms) }
FUNCTION qtau(v(mV))(ms) { qtau = 200(ms)/(exp((v+70(mV))/20(mV))+exp(-(v+70(mV))/20(mV))) + 5(ms) }

INCLUDE "aux_fun.inc"
