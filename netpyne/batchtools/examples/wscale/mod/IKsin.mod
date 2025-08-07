: Slowly inactivating K+ channel

NEURON {
	SUFFIX IKsin
	USEION k READ ki, ko WRITE ik
	RANGE gKsbar, ik, gk
	
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
        (mM) = (milli/liter)
	
}
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}
PARAMETER {
	v (mV)
	dt (ms)
	gKsbar= 0.00014 (mho/cm2) <0,1e9>
	
}


STATE {
	a b
}


ASSIGNED {
	ik (mA/cm2)
	ainf binf
	atau (ms)
	btau (ms)
	gk (mho/cm2)
	ek  (mV)
	ki (mM)
	ko  (mM)
}



INITIAL {
	rate(v)
	a = ainf
	b = binf
}

BREAKPOINT {
	SOLVE states METHOD cnexp
		
	gk = gKsbar * a * b
	ek = 25 * log(ko/ki)
	ik = gk*(v-ek)
	
}

DERIVATIVE states {
	rate(v)
	
	a' = (ainf-a)/atau
	b' = (binf-b)/btau
}
UNITSOFF

PROCEDURE rate(v (mV)) {LOCAL va, vb, vc, vd
	
	
	va = v + 34
	vb = v + 65
	vd = v + 63.6
	

if (fabs(va)<1e-04){ va = va+0.00001 }
	   ainf = 1/(1 + exp(-va/6.5))
	   atau = 10
	  :atau=6
	

if (fabs(vb)<1e-04){ vb = vb+0.00001 }
	   binf = 1/(1 + exp(vb/6.6))

 
if (fabs(vd)<1e-04){ vd = vd+0.00001 }
	   btau = 200 + 3200 / (1 + exp(-vd/4))
	:btau = 200 + 3200 / (1 + exp(-vd/4))
}

	
UNITSON







