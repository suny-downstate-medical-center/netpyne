TITLE leak conductance (voltage independent)

COMMENT
leak conductance (voltage independent)

Ions: non-specific

Style: quasi-ohmic

From: unknown

Updates:
2014 December (Marianne Bezaire): documented
ENDCOMMENT


VERBATIM
#include <stdlib.h> /* 	Include this library so that the following
						(innocuous) warning does not appear:
						 In function '_thread_cleanup':
						 warning: incompatible implicit declaration of 
						          built-in function 'free'  */
ENDVERBATIM

UNITS {
	(mA) =(milliamp)
	(mV) =(millivolt)
}
 
NEURON { 
	SUFFIX ch_leak 
	NONSPECIFIC_CURRENT i
	RANGE gmax, e, i
	RANGE myi, g
    THREADSAFE
}
 
PARAMETER {
	g (mho/cm2)		: conductance of the leak channels    
	gmax (mho/cm2)		: conductance of the leak channels    
	e (mV)			: reversal potential of the leak channels
}

ASSIGNED {	: assigned variables are by default RANGE, but not available to hoc (unless RANGE in NEURON block)	     		
	v (mV) 			: membrane voltage
					: available to all mechanisms by default, but for
					: cross-simulator fluency, it is included here 
	i (mA/cm2)		: current through the leak channels
	myi (mA/cm2)
} 

BREAKPOINT {
	g = gmax
	i = g*(v-e)	: solve for the current (at each dt)
	myi = i
}






