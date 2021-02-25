TITLE t-type calcium channel with high threshold for activation
: used in somatic and dendritic regions 
: Updated to use CVode --Carl Gold 08/10/03


NEURON {
	SUFFIX catcb
	USEION ca READ cai, eca    
        RANGE gcatbar, iCa
        RANGE gcatbar, ica
	:GLOBAL hinf, minf
        RANGE hinf, minf
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(molar) = (1/liter)
	(mM) =	(millimolar)
	FARADAY = (faraday) (coulomb)
	R = (k-mole) (joule/degC)
}

PARAMETER {           
	gcatbar = 0   (mho/cm2)  
	zetam = -3
	zetah = 5.2
	vhalfm =-36 (mV)
	vhalfh =-68 (mV)
	tm0=1.5(ms)
	th0=10(ms)
}



ASSIGNED {     : parameters needed to solve DE
	v            (mV)
	celsius      (degC)
	ica          (mA/cm2)
	cai          (mM)       
	eca          (mV)       
        minf
        hinf
}


STATE {	
	m 
	h 
}  

INITIAL {
	rates(v)
        m = minf
        h = hinf
}

BREAKPOINT {
	SOLVE states METHOD cnexp
	ica = gcatbar*m*m*h*(v-eca)	
}

FUNCTION ghk(v(mV), ci(mM), co(mM)) (.001 coul/cm3) {
	LOCAL z, eci, eco
	z = (1e-3)*2*FARADAY*v/(R*(celsius+273.15))
	eco = co*efun(z)
	eci = ci*efun(-z)
	ghk = (.001)*2*FARADAY*(eci - eco)
}

FUNCTION efun(z) {
	if (fabs(z) < 1e-4) {
		efun = 1 - z/2
	}else{
		efun = z/(exp(z) - 1)
	}
}


DERIVATIVE states {
	rates(v)
	m' = (minf -m)/tm0
	h'=  (hinf - h)/th0
}


PROCEDURE rates(v (mV)) { 
        LOCAL a, b
        
	a = alpm(v)
	minf = 1/(1+a)
        
        b = alph(v)
	hinf = 1/(1+b)
}



FUNCTION alpm(v(mV)) {
UNITSOFF
  alpm = exp(1.e-3*zetam*(v-vhalfm)*9.648e4/(8.315*(273.16+celsius))) 
UNITSON
}

FUNCTION alph(v(mV)) {
UNITSOFF
  alph = exp(1.e-3*zetah*(v-vhalfh)*9.648e4/(8.315*(273.16+celsius))) 
UNITSON
}

