: $Id: caolmw.mod,v 1.2 2010/11/30 16:40:09 samn Exp $ 
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
  (mollar) = (1/liter)
  (M)      = (mollar)
  (mM)     = (millimollar)
  (mA)     = (milliamp)
  (mV)     = (millivolt)
  (mS)     = (millisiemens)
}

NEURON {
  SUFFIX Caolmw
  USEION ca READ ica, cai WRITE cai
  RANGE alpha, tau
}
	
PARAMETER {
  alpha = 0.002 (cm2-M/mA-ms)
  tau   = 80    (ms)
}
    
ASSIGNED { ica (mA/cm2) }

INITIAL { cai = 0 }

STATE { cai (mM) }

BREAKPOINT { SOLVE states METHOD cnexp }

DERIVATIVE states { cai' = -(1000) * alpha * ica - cai/tau }
