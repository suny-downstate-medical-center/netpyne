TITLE calcium-activated potassium channel (non-voltage-dependent)

COMMENT
Ca2+ activated K+ channel (not voltage dependent)

From:  original said for granule cells, but used in all the cell types

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
        (mM)    = (millimolar)
	(mA)	= (milliamp)
	(mV)	= (millivolt)
}

NEURON {
	SUFFIX ch_KCaS
	USEION k READ ek WRITE ik VALENCE 1
	USEION ca READ cai VALENCE 2
	RANGE g, gmax, qinf, qtau, ik
	RANGE myi
    THREADSAFE
}

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

PARAMETER {
      celsius (degC) : temperature - set in hoc; default is 6.3
	v		(mV)
	dt		(ms)
	gmax  (mho/cm2)
	ek	(mV)
	cai (mM)
}

STATE { q }

ASSIGNED {
	ik (mA/cm2) 
	g (mho/cm2) 
	qinf 
	qtau (ms) 
	qexp
	myi (mA/cm2)
}


BREAKPOINT {          :Computes i=g*q^2*(v-ek)
	SOLVE state
    g = gmax * q*q
	ik = g * (v-ek)
	myi = ik
}

UNITSOFF
: verbatim blocks are not thread safe (perhaps related, this mechanism cannot be used with cvode)
INITIAL {
	q=qinf
	rate(cai)
}

PROCEDURE state() {  :Computes state variable q at current v and dt.
	:cai = ncai + lcai + tcai
	rate(cai)
	q = q + (qinf-q) * qexp
}

LOCAL q10
PROCEDURE rate(cai) {  :Computes rate and other constants at current v.
	LOCAL alpha, beta, tinc
	q10 = 3^((celsius - 34)/10) : set to 1 for the cutsuridis model?
		:"q" activation system
alpha = 1.25e1 * cai * cai
beta = 0.00025 

	qtau = 1 /(alpha + beta)/q10
	qinf = alpha * qtau
	tinc = -dt
	qexp = 1 - exp(tinc/qtau)
}

UNITSON






