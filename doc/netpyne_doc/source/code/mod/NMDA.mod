NEURON{ POINT_PROCESS NMDA
  RANGE B 
  GLOBAL mg
}

PARAMETER {
  mg        = 1.    (mM)     : external magnesium concentration
  Cdur	= 1.	(ms)	 : transmitter duration (rising phase)
  Alpha	= 4.	(/ms mM) : forward (binding) rate
  Beta	= 0.0067 (/ms)	 : backward (unbinding) rate 1/150
  Erev	= 0.	(mV)	 : reversal potential
}

ASSIGNED { B }

INCLUDE "netcon.inc"
: EXTRA BREAKPOINT MUST BE BELOW THE INCLUDE
BREAKPOINT {
  rates(v)
  g = g * B : g = GMAX * R * B
  i = i * B : i = g*(v - Erev)
}

PROCEDURE rates(v(mV)) {
  TABLE B
  DEPEND mg
  FROM -100 TO 80 WITH 180
  B = 1 / (1 + exp(0.062 (/mV) * -v) * (mg / 3.57 (mM)))
}
 
:** GABAa






