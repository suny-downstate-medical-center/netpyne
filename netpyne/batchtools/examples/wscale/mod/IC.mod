TITLE Ca-dependent potassium current
:
:   Ca++ dependent K+ current IC responsible for 
:   action potentials AHP's
:   Differential equations
:
:   Model of Yamada, Koch & Adams, in: Methods in Neuronal Modeling,
:   Ed. by Koch & Segev, MIT press, 1989.
:
:   This current models the "fast" IK[Ca]:
:      - potassium current
:      - activated by intracellular calcium
:      - VOLTAGE DEPENDENT
:
:   Written by Alain Destexhe, Salk Institute, Sept 18, 1992
:
: should be considered 'BK' - fast, big conductance

NEURON {
	SUFFIX ikc
	USEION k READ ek WRITE ik
	USEION ca READ cai
        RANGE gkbar, ik
	RANGE m_inf, tau_m
        RANGE taumin
        GLOBAL ascale,bscale,vfctr
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(molar) = (1/liter)
	(mM) = (millimolar)
}

PARAMETER {
	v		(mV)
        celsius         (degC)
	ek		(mV)
        cai             (mM)
	gkbar	= .003	(mho/cm2)	: taken from 
        taumin = 0.1
        ascale = 250.0
        bscale = 0.1
        vfctr = 24.0
}

STATE {
	m
}

INITIAL {
	evaluate_fct(v,cai)
	m = m_inf
}

ASSIGNED {
	ik	(mA/cm2)
	m_inf
	tau_m	(ms)
}

BREAKPOINT { 
	SOLVE states METHOD cnexp
	ik = gkbar * m * (v - ek)
}

DERIVATIVE states { 
	evaluate_fct(v,cai)
	m' = (m_inf - m) / tau_m
}

UNITSOFF
PROCEDURE evaluate_fct(v(mV),cai(mM)) {  LOCAL a,b,tadj
:
:  activation kinetics of Yamada et al were at 22 deg. C
:  transformation to 36 deg assuming Q10=3
:
	tadj = 3 ^ ((celsius-22.0)/10)

	a = ascale * cai * exp(v/vfctr)
	b = bscale * exp(-v/vfctr)

	tau_m = 1.0 / (a + b) / tadj
        if(tau_m < taumin){ tau_m = taumin }
	m_inf = a / (a + b)
}
UNITSON
