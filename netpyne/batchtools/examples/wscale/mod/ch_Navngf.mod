TITLE sodium channel (voltage dependent, higher threshold)

COMMENT
sodium channel (voltage dependent, higher threshold)

Ions: na

Style: quasi-ohmic

From: modified from ch_Nav to have a higher threshold, 
	  suitable for neurogliaform and ivy cells

Updates:
2014 December (Marianne Bezaire): documented
ENDCOMMENT

COMMENT
VERBATIM
#include <stdlib.h> 
/* 	Include this library so that the following (innocuous) warning does not appear:
		In function '_thread_cleanup':
		warning: incompatible implicit declaration of built-in function 'free'  */
ENDVERBATIM
ENDCOMMENT

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
	SUFFIX ch_Navngf 
	USEION na READ ena WRITE ina VALENCE 1
	RANGE g, gmax, minf, mtau, hinf, htau, ina, m, h
	RANGE myi
	THREADSAFE
}

PARAMETER {
	ena  (mV)
	gmax (mho/cm2)   
	
	mAlphC = -0.34133 (1)
	mAlphV = 24 (mV)
	mBetaC = 0.28483 (1)
	mBetaV = -4 (mV)

	hAlphC = 0.29648 (1)
	hAlphV = 64.4184 (mV)
	hBetaC = 3.0931  (1)
	hBetaV = 12.1463 (mV)
}

STATE {
	m h
}

ASSIGNED {
	v (mV) 
	celsius (degC) : temperature - set in hoc; default is 6.3
	dt (ms) 

	g (mho/cm2)
	ina (mA/cm2)
	minf
	hinf
	mtau (ms)
	htau (ms)
	mexp
	hexp 
	myi (mA/cm2)
}

BREAKPOINT {
	SOLVE states
	g = gmax*m*m*m*h  
	ina = g*(v - ena)
	myi = ina
}
 
UNITSOFF
 
INITIAL {
	trates(v)
	m = minf
	h = hinf
}

PROCEDURE states() {	:Computes state variables m, h, and n 
	trates(v)			:      at the current v and dt.
	m = m + mexp*(minf-m)
	h = h + hexp*(hinf-h)
}
 
LOCAL q10	: declare outside a block so available to whole mechanism
PROCEDURE rates(v) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
	LOCAL  alpha, beta, sum	: only available to block; must be first line in block

	q10 = 3^((celsius - 34)/10)

	:"m" sodium activation system - act and inact cross at -40
	alpha = mAlphC*vtrap((v+mAlphV),-5)
	beta = mBetaC*vtrap((v+mBetaV),5)
	sum = alpha+beta        
	mtau = 1/sum 
	minf = alpha/sum
	
	:"h" sodium inactivation system
	alpha = hAlphC/exp((v+hAlphV)/20)
	beta = hBetaC/(1+exp((v+hBetaV)/-10))
	sum = alpha+beta
	htau = 1/sum 
	hinf = alpha/sum 		
}
 
PROCEDURE trates(v) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
	LOCAL tinc	: only available to block; must be first line in block
	TABLE minf, mexp, hinf, hexp, mtau, htau
	DEPEND dt, celsius, mAlphV, mAlphC, mBetaV, mBetaC, hAlphV, hAlphC, hBetaV, hBetaC
	FROM -100 TO 100 WITH 200

	rates(v)	: not consistently executed from here if usetable_hh == 1
				: so don't expect the tau values to be tracking along with
				: the inf values in hoc

	tinc = -dt * q10

	mexp = 1 - exp(tinc/mtau)
	hexp = 1 - exp(tinc/htau)
}
 
FUNCTION vtrap(x,y) {  :Traps for 0 in denominator of rate eqns.
	if (fabs(x/y) < 1e-6) {
		vtrap = y*(1 - x/y/2)
	}else{  
		vtrap = x/(exp(x/y) - 1)
	}
}
 
UNITSON







