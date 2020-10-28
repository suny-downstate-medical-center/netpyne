TITLE Fast delayed rectifier potassium channel (voltage dependent, for neurogliaform family)

COMMENT
Fast delayed rectifier potassium channel (voltage dependent, for neurogliaform family)

Ions: k

Style: quasi-ohmic

From: Yuen and Durand, 1991 (squid axon)

Updates:
2014 December (Marianne Bezaire): documented
? ? (Aradi): shifted the voltage dependence by 16 mV
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
	(uF) = (microfarad)
	(molar) = (1/liter)
	(nA) = (nanoamp)
	(mM) = (millimolar)
	(um) = (micron)
	FARADAY = 96520 (coul)
	R = 8.3134	(joule/degC)
}
 
NEURON { 
	SUFFIX ch_Kdrfastngf
	USEION k READ ek WRITE ik VALENCE 1
	RANGE g, gmax, ninf, ntau, ik
	RANGE myi, offset5, offset6, slope5, slope6
	THREADSAFE
}
 
PARAMETER {

	:ek  (mV)
	gmax (mho/cm2)
	offset5=17 (mV)
	offset6=17 (mv)
	slope5=.07 (1)
	slope6=.264 (1)
}
 
STATE {
	n	
}
 
ASSIGNED {		     
	g (mho/cm2)
	ik (mA/cm2)
	ninf
	ntau (ms)
	nexp
	myi (mA/cm2)
	ek (mV)
	v (mV) 
	celsius (degC) : temperature - set in hoc; default is 6.3
	dt (ms) 
} 

BREAKPOINT {
	SOLVE states
	g = gmax*n*n*n*n
	ik = g*(v-ek)
	myi =  ik
}
 
UNITSOFF
 
INITIAL {
	trates(v)

	n = ninf
}

PROCEDURE states() {	:Computes state variables m, h, and n 
	trates(v)	:      at the current v and dt.       
	n = n + nexp*(ninf-n)
}
 
LOCAL q10
PROCEDURE rates(v) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
	LOCAL  alpha, beta, sum, tinc
	:q10 = 3^((celsius - 6.3)/10)
	q10 = 3^((celsius - 34)/10)

	:"nf" fKDR activation system
	alpha = -1*slope5*vtrap((v+65-47-offset5),-6)
	beta = slope6/exp((v+65-22-offset6)/40)
	sum = alpha+beta        
	ntau = 1/sum
	ninf = alpha/sum	
	
	tinc = -dt * q10
	nexp = 1 - exp(tinc/ntau)
}
 
PROCEDURE trates(v) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
	LOCAL tinc
	TABLE ninf, nexp, ntau
	DEPEND dt, celsius, slope5, slope6, offset5, offset6
	FROM -100 TO 100 WITH 200
						   
	rates(v)	: not consistently executed from here if usetable_hh == 1
	: so don't expect the tau values to be tracking along with
	: the inf values in hoc

	:tinc = -dt * q10
	:nexp = 1 - exp(tinc/ntau)
}
 
FUNCTION vtrap(x,y) {  :Traps for 0 in denominator of rate eqns.
        if (fabs(x/y) < 1e-6) {
                vtrap = y*(1 - x/y/2)
        }else{  
                vtrap = x/(exp(x/y) - 1)
        }
}
 
UNITSON







