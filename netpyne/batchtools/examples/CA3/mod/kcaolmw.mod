: $Id: kcaolmw.mod,v 1.2 2010/11/30 16:47:18 samn Exp $ 
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
  (mA)     = (milliamp)
  (mV)     = (millivolt)
  (mS)     = (millisiemens)
  (mollar) = (1/liter)
  (mM)     = (millimollar)
}

NEURON {
  SUFFIX KCaolmw
  USEION k WRITE ik
  USEION ca READ cai
  RANGE gkca,ek,kd
}
	
PARAMETER {
  gkca =  10 (mS/cm2)
  ek   = -90 (mV)
  kd   =  30 (mM)
}
    
ASSIGNED {    
  cai (mM) 
  v   (mV)
  ik  (mA/cm2) 
}

PROCEDURE iassign () { ik  = (1e-3) * gkca * cai/(cai+kd) * (v-ek) }

INITIAL {
  iassign()
}

BREAKPOINT { iassign() }
