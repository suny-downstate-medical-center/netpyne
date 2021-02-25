: Delayed rectifier K+ channel

NEURON {
	SUFFIX kdrcr
	USEION k READ ki, ko WRITE ik
	RANGE gkdrbar, ik, gk
	
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	
}

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}
PARAMETER {
	v (mV)
	dt (ms)
	gkdrbar= 0.0338 (mho/cm2) <0,1e9>
	
	
}

STATE {
	n
}

ASSIGNED {
	ik (mA/cm2)
	inf
	tau (ms)
	gk (mho/cm2)
	ek (mV)
	ki (mM)
	ko (mM)

}


INITIAL {
	rate(v)
	n = inf
}

BREAKPOINT {
	SOLVE states METHOD cnexp
	gk= gkdrbar*n*n*n*n
	ek = 25 * log(ko/ki)
	ik = gk*(v-ek)
	
}

DERIVATIVE states {
	rate(v)
	n' = (inf-n)/tau
}

UNITSOFF

FUNCTION alf(v){ LOCAL va 
	
	   va=v-13
	if (fabs(va)<1e-04){
	   va=va+0.0001
		alf= (-0.018*va)/(-1+exp(-(va/25)))
	} else {
	  	alf = (-0.018*(v-13))/(-1+exp(-((v-13)/25)))
	}
}


FUNCTION bet(v) { LOCAL vb 
	
	  vb=v-23
	if (fabs(vb)<1e-04){
	  vb=vb+0.0001
		bet= (0.0054*vb)/(-1+exp(vb/12))
	} else {
	  	bet = (0.0054*(v-23))/(-1+exp((v-23)/12))
	}
}	






PROCEDURE rate(v (mV)) {LOCAL q10, sum, aa, ab
	
	aa=alf(v) ab=bet(v) 
	
	sum = aa+ab
	inf = aa/sum
	tau = 1/(sum)
	
	
}

UNITSON	









