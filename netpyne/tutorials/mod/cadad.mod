: $Id: cadad.mod,v 1.4 2002/11/08 15:42:37 billl Exp $
TITLE Fast mechanism for submembranal Ca++ concentration (cai)
:
: Takes into account:
:
:	- increase of cai due to calcium currents
:	- extrusion of calcium with a simple first order equation
:
: This mechanism is compatible with the calcium pump "cad" and has the 
: same name and parameters; however the parameters specific to the pump
: are dummy here.
:
: Parameters:
:
:	- depth: depth of the shell just beneath the membran (in um)
:	- cainf: equilibrium concentration of calcium (2e-4 mM)
:	- taur: time constant of calcium extrusion (must be fast)
:	- kt,kd: dummy parameters
:
: Written by Alain Destexhe, Salk Institute, 1995
:

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
  SUFFIX cadad
  USEION ca READ ica, cai WRITE cai
  RANGE depth,kt,kd,cainf,taur
}

UNITS {
  (molar) = (1/liter)			: moles do not appear in units
  (mM)	= (millimolar)
  (um)	= (micron)
  (mA)	= (milliamp)
  (msM)	= (ms mM)
}

CONSTANT {
  FARADAY = 96489		(coul)		: moles do not appear in units
  :	FARADAY = 96.489	(k-coul)	: moles do not appear in units
}

PARAMETER {
  depth	= 1	(um)		: depth of shell
  taur	= 5	(ms)		: rate of calcium removal
  cainf	= 2.4e-4	(mM)
  kt	= 0	(mM/ms)		: dummy
  kd	= 0	(mM)		: dummy
}

STATE {
  cai		(mM) 
}

INITIAL {
  cai = cainf
}

ASSIGNED {
  ica		(mA/cm2)
  drive_channel	(mM/ms)
}
	
BREAKPOINT {
  SOLVE state METHOD cnexp
}

DERIVATIVE state { 
  drive_channel =  - (10000) * ica / (2 * FARADAY * depth)
  if (drive_channel <= 0.) { drive_channel = 0. }	: cannot pump inward
  cai' = drive_channel + (cainf-cai)/taur
}

