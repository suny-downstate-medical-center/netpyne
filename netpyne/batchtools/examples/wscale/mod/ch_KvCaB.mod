TITLE Calcium activated potassium channel (voltage dependent)

COMMENT
Ca2+-activated K+ channel (voltage dependent)

Ions: k

Style: quasi-ohmic

From: Modified from Moczydlowski and Latorre (1983) J. Gen. Physiol. 82

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
	(molar) = (1/liter)
}

UNITS {
	(mV) =	(millivolt)
	(mA) =	(milliamp)
	(mM) =	(millimolar)
}

NEURON {
	SUFFIX ch_KvCaB
	USEION k READ ek WRITE ik
	USEION ca READ cai VALENCE 2
	:USEION nca READ ncai VALENCE 2
	:USEION lca READ lcai VALENCE 2
	:USEION tca READ tcai VALENCE 2
	RANGE gmax, g, ik
	RANGE myi
	GLOBAL oinf, otau	: these two are not thread safe
    THREADSAFE
}

UNITS {
	FARADAY = (faraday)  (kilocoulombs)
	R = 8.313424 (joule/degC)
}

PARAMETER {	: clean up the PARAMETER and ASSIGNED blocks
	gmax=.01	(mho/cm2)	: Maximum Permeability

	d1 = .84
	d2 = 1.	
	k1 = .48e-3	(mM)
	k2 = .13e-6	(mM)
	:cai = 5.e-5	(mM)
	cai (mM)
	
	abar = .28	(/ms)
	bbar = .48	(/ms)
	
	st=1		(1)
}

ASSIGNED {	: clean up the PARAMETER and ASSIGNED blocks
      celsius (degC) : temperature - set in hoc; default is 6.3
	v			(mV)

	:lcai		(mV)
	:ncai		(mV)
	:tcai		(mV)

	ek			(mV)
	ik			(mA/cm2)

	oinf
	otau		(ms)
	g		(mho/cm2)
	myi (mA/cm2)
}

INITIAL {
	:cai= ncai + lcai : + tcai
        rate(v,cai)
        o=oinf
}

STATE {	o }		: fraction of open channels

BREAKPOINT {
	SOLVE state METHOD cnexp
	g = gmax*o^st
	ik = g*(v - ek)
	myi = ik
}

DERIVATIVE state {	: exact when v held constant; integrates over dt step
	:cai= ncai + lcai : + tcai
	rate(v, cai)
	o' = (oinf - o)/otau
}

FUNCTION alp(v (mV), c (mM)) (1/ms) { :callable from hoc
	alp = c*abar/(c + exp1(k1,d1,v))
}

FUNCTION bet(v (mV), c (mM)) (1/ms) { :callable from hoc
	bet = bbar/(1 + c/exp1(k2,d2,v))
}

FUNCTION exp1(k (mM), d, v (mV)) (mM) { :callable from hoc
	exp1 = k*exp(-2*d*FARADAY*v/R/(273.15 + celsius))
}

PROCEDURE rate(v (mV), c (mM)) { :callable from hoc
	LOCAL a
	a = alp(v,c)
	otau = 1/(a + bet(v, c))
	oinf = a*otau
}






