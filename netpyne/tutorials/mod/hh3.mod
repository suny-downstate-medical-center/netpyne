TITLE HH channel
: Mel-modified Hodgkin - Huxley conductances (after Ojvind et al.)

VERBATIM
static const char rcsid[]="$Id: hh3.mod,v 1.1 1996/05/19 19:26:28 karchie Exp $";
ENDVERBATIM

NEURON {
	SUFFIX hh3
	USEION na READ ena WRITE ina
	USEION k READ ek WRITE ik
	NONSPECIFIC_CURRENT il
	RANGE gnabar, gkbar, gl, el
	GLOBAL taus,taun,taum,tauh,tausb
	GLOBAL tausv,tausd,mN,nN
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
}

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

PARAMETER {
	v (mV)
	celsius = 37	(degC)
	dt (ms)
	gnabar=.20 (mho/cm2)
	gkbar=.12 (mho/cm2)
	gl=.0001 (mho/cm2)
	ena = 40 (mV)
	ek = -80 (mV)
	el = -70.0 (mV)	: steady state at v = -65 mV
	taum=0.05
	tauh=0.5
	taus=50
	tausv=30
	tausd=1
	taun=1
	mN=3
	nN=3
	tausb=0.5
}
STATE {
	m h n s
}
ASSIGNED {
	ina (mA/cm2)
	ik (mA/cm2)
	il (mA/cm2)

}

BREAKPOINT {
	SOLVE states

	ina = gnabar*h*s*(v - ena)*m^mN
	ik = gkbar*(v - ek)*n^nN

:ina = gnabar*m*m*h*(v - ena)
:ik = gkbar*n*n*(v - ek)
	il = gl*(v - el)
}

PROCEDURE states() {	: exact when v held constant
	LOCAL sigmas
	sigmas=1/(1+exp((v+tausv)/tausd))
	m = m + (1 - exp(-dt/taum))*(1 / (1 + exp((v + 40)/(-3)))  - m)
	h = h + (1 - exp(-dt/tauh))*(1 / (1 + exp((v + 45)/3))  - h)
	s = s + (1 - exp(-dt/(taus*sigmas+tausb)))*(1 / (1 + exp((v + 44)/3))  - s)
	n = n + (1 - exp(-dt/taun))*(1 / (1 + exp((v + 40)/(-3)))  - n)
	VERBATIM
	return 0;
	ENDVERBATIM
}

