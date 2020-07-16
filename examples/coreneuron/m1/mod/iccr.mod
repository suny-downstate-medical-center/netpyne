:  iC   fast Ca2+/V-dependent K+ channel

NEURON {
	SUFFIX iCcr
	USEION k READ ki, ko WRITE ik
	USEION ca READ cai
    RANGE ik, gk, gkcbar
}

UNITS {
    (mM) = (milli/liter)
	(mA) = (milliamp)
	(mV) = (millivolt)
	
}

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}
PARAMETER {
	v		(mV)
	dt      (ms)
	cai		(mM)
	gkcbar= 0.0022	(mho/cm2)
  
}


STATE {
	c
}

ASSIGNED {
	ik (mA/cm2)
	cinf 
	ctau (ms)
	gk (mho/cm2)
	ek (mV)
	ki (mM)
	ko (mM)

}


INITIAL {
	rate()
	c = cinf
}


BREAKPOINT {
	SOLVE states METHOD cnexp
	gk = gkcbar*c*c
	ek = 25 * log(ko/ki)        
	ik = gk*(v-ek)
}



DERIVATIVE states {
    rate()
	c' = (cinf-c)/ctau
}

UNITSOFF


FUNCTION calf(v (mV), cai (mM)) (/ms) { LOCAL vs, va

       vs=v+40*log10(1000*cai)  :1000*cai
	   va=vs+18
	   if (fabs(va)<1e-04){  va=va+0.0001 }
	   calf = (-0.00642*vs-0.1152)/(-1+exp(-va/12))
}



FUNCTION cbet(v (mV), cai (mM))(/ms) { LOCAL vs, vb 

  vs=v+40*log10(cai*1000)
  vb=vs+152
  if (fabs(vb)<1e-04){ vb=vb+0.0001 }
  cbet = 1.7*exp(-vb/30)

}	



UNITSON

PROCEDURE rate() {LOCAL  csum, ca, cb

	ca=calf(v, cai) cb=cbet(v, cai)
		
	csum = ca+cb
	cinf = ca/csum
	if ((1/csum)>1.1) { ctau = 1 / csum}
	else { ctau = 1.1 }
		
}
	











