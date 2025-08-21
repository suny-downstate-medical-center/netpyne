NEURON {  POINT_PROCESS GABAa }

PARAMETER {
  Cdur	= 1.08	(ms)		: transmitter duration (rising phase)
  Alpha	= 1.	(/ms mM)	: forward (binding) rate
  Beta	= 0.5	(/ms)		: backward (unbinding) rate
  Erev	= -70	(mV)		: reversal potential
}

INCLUDE "netcon.inc"
 
:** GABAb






