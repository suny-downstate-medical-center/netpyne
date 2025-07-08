TITLE N-type calcium channel (voltage dependent)
 
COMMENT
N-Type Ca2+ channel (voltage dependent)

Ions: ca

Style: quasi-ohmic

From: Aradi and Holmes, 1999

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
	(molar) = (1/liter)
	(mM) = (millimolar)
	FARADAY = 96520 (coul)
	R = 8.3134	(joule/degC)
}
 
 
NEURON {
	SUFFIX ch_CavN				: The name of the mechanism
	USEION ca READ eca WRITE ica VALENCE 2 
	RANGE g
	RANGE gmax
	RANGE cinf, ctau, dinf, dtau
	RANGE myi
	THREADSAFE
}
 
INDEPENDENT {t FROM 0 TO 100 WITH 100 (ms)}


PARAMETER {
	v (mV) 					: membrane potential
      celsius (degC) : temperature - set in hoc; default is 6.3
	gmax (mho/cm2)		: conductance flux - defined in CavT but not here
}
 
STATE {
	c d		
}
 
ASSIGNED {			: assigned (where?)
	dt (ms) 				: simulation time step

	ica (mA/cm2)	: current flux
	g (mho/cm2)	: conductance flux
	eca (mV)		: reversal potential

	cinf dinf
	ctau (ms)
	dtau (ms) 
	cexp dexp      
	myi (mA/cm2)
}

BREAKPOINT {
	SOLVE states : what is the method? let's specify one
    g = gmax*c*c*d
	ica = g*(v-eca)
	myi = ica
}
 
UNITSOFF
 
INITIAL {
	trates(v)
	c = cinf
	d = dinf
}

? states : verbatim blocks are not thread safe (perhaps related, this mechanism cannot be used with cvode)
PROCEDURE states() {	:Computes state variables m, h, and n 
        trates(v)	:      at the current v and dt.
	c = c + cexp*(cinf-c)
	d = d + dexp*(dinf-d)
        :VERBATIM				
        :return 0;
        :ENDVERBATIM
}
 
LOCAL q10

PROCEDURE rates(v) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
        LOCAL  alpha, beta, sum
       :q10 = 3^((celsius - 6.3)/10)
       q10 = 3^((celsius - 34)/10)
                :"c" NCa activation system
        alpha = -0.19*vtrap(v-19.88,-10)
	beta = 0.046*exp(-v/20.73)
	sum = alpha+beta        
	ctau = 1/sum      cinf = alpha/sum
                :"d" NCa inactivation system
	alpha = 0.00016*exp(-v/48.4) : this is multiplied, not divided in Aradi & Holmes formula
	beta = 1/(exp((-v+39)/10)+1)
	sum = alpha+beta        
	dtau = 1/sum      dinf = alpha/sum
}

PROCEDURE trates(v) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
	LOCAL tinc
	TABLE  cinf, cexp, dinf, dexp, ctau, dtau
	DEPEND dt, celsius FROM -100 TO 100 WITH 200
                           
	rates(v)	: not consistently executed from here if usetable_hh == 1
				: so don't expect the tau values to be tracking along with
				: the inf values in hoc

	tinc = -dt * q10
	cexp = 1 - exp(tinc/ctau)
	dexp = 1 - exp(tinc/dtau)
}

FUNCTION vtrap(x,y) {  :Traps for 0 in denominator of rate eqns.
	if (fabs(x/y) < 1e-6) {
		vtrap = y*(1 - x/y/2)
	}else{  
		vtrap = x/(exp(x/y) - 1)
	}
}

UNITSON







