TITLE n-calcium channel
: n-type calcium channel
: MODELDB 126814 CA3 by Safiulina et al - http://senselab.med.yale.edu/modeldb/ShowModel.asp?model=126814
: by Michele Migliore


UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)

	FARADAY = 96520 (coul)
	R = 8.3134 (joule/degC)
	KTOMV = .0853 (mV/degC)
}

PARAMETER {
	v (mV)
	celsius 		(degC)
	gcanbar=.0003 (mho/cm2)
	ki=.001 (mM)
	cai=50.e-6 (mM)
	cao = 2  (mM)
	q10=5
	mmin = 0.2
	hmin = 3
	a0m =0.03
	zetam = 2
	vhalfm = -14
	gmm=0.1	
        USEGHK=1
        erev = 100
}

NEURON {
	SUFFIX can
	USEION ca READ cai,cao WRITE ica
        RANGE gcanbar, ica, gcan       
        RANGE hinf,minf,taum,tauh
        GLOBAL USEGHK
}

STATE {
	m h 
}

ASSIGNED {
	ica (mA/cm2)
        gcan  (mho/cm2) 
        minf
        hinf
        taum
        tauh
}

INITIAL {
        rates(v)
        m = minf
        h = hinf
}

BREAKPOINT {
	SOLVE states METHOD cnexp
	gcan = gcanbar*m*m*h*h2(cai)
        if (USEGHK == 1) {
          ica = gcan*ghk(v,cai,cao)
        } else {
          ica = gcan*(v-erev)
        }
}

UNITSOFF
FUNCTION h2(cai(mM)) {
	h2 = ki/(ki+cai)
}


FUNCTION ghk(v(mV), ci(mM), co(mM)) (mV) {
        LOCAL nu,f

        f = KTF(celsius)/2
        nu = v/f
        ghk=-f*(1. - (ci/co)*exp(nu))*efun(nu)
}

FUNCTION KTF(celsius (degC)) (mV) {
        KTF = ((25./293.15)*(celsius + 273.15))
}


FUNCTION efun(z) {
	if (fabs(z) < 1e-4) {
		efun = 1 - z/2
	}else{
		efun = z/(exp(z) - 1)
	}
}

FUNCTION alph(v(mV)) {
	alph = 1.6e-4*exp(-v/48.4)
}

FUNCTION beth(v(mV)) {
	beth = 1/(exp((-v+39.0)/10.)+1.)
}

FUNCTION alpm(v(mV)) {
	alpm = 0.1967*(-1.0*v+19.88)/(exp((-1.0*v+19.88)/10.0)-1.0)
}

FUNCTION betm(v(mV)) {
	betm = 0.046*exp(-v/20.73)
}

FUNCTION alpmt(v(mV)) {
  alpmt = exp(0.0378*zetam*(v-vhalfm)) 
}

FUNCTION betmt(v(mV)) {
  betmt = exp(0.0378*zetam*gmm*(v-vhalfm)) 
}

UNITSON

DERIVATIVE states {     : exact when v held constant; integrates over dt step
        rates(v)
        m' = (minf - m)/taum
        h' = (hinf - h)/tauh
}

PROCEDURE rates(v (mV)) { :callable from hoc
        LOCAL a, b, qt
        qt=q10^((celsius-25)/10)
        a = alpm(v)
        b = 1/(a + betm(v))
        minf = a*b
	taum = betmt(v)/(qt*a0m*(1+alpmt(v)))
	if (taum<mmin/qt) {taum=mmin/qt}
        a = alph(v)
        b = 1/(a + beth(v))
        hinf = a*b
:	tauh=b/qt
	tauh= 80
	if (tauh<hmin) {tauh=hmin}
}
