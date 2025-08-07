: Fast Na+ channel

NEURON {
	SUFFIX Nafcr
	USEION na READ ena WRITE ina
	RANGE gnafbar, ina, gna
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	
}

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

PARAMETER {
	v (mV)
	dt (ms)
	gnafbar= 0.086 (mho/cm2) <0,1e9>
	ena = 55 (mV)

}
STATE {
	m h
}
ASSIGNED {
	ina (mA/cm2)
	minf hinf 
	mtau (ms)
	htau (ms)
	gna (mho/cm2)
	
}



INITIAL {
	rate(v)
	m = minf
	h = hinf
}

BREAKPOINT {
	SOLVE states METHOD cnexp
	gna = gnafbar*m*m*m*h
	ina = gna*(v-55)
	
}

DERIVATIVE states {
	rate(v)
	m' = (minf-m)/mtau
	h' = (hinf-h)/htau
}

UNITSOFF

FUNCTION malf( v){ LOCAL va 
	va=v+28
	if (fabs(va)<1e-04){
	   malf= -0.2816*(-9.3 + va*0.5)
	}else{
	   malf = -0.2816*(v+28)/(-1+exp(-(v+28)/9.3))
	}
}


FUNCTION mbet(v(mV))(/ms) { LOCAL vb 
	vb=v+1
	if (fabs(vb)<1e-04){
	   mbet = 0.2464*(6 + vb*0.5)
	}else{
	   mbet = 0.2464*(v+1)/(-1+exp((v+1)/6))
}
}	


FUNCTION half(v(mV))(/ms) { LOCAL vc 
	vc=v+43.1
	if (fabs(vc)<1e-04){
	   half=0.098*(20 + vc*0.5)
	}else{
	   half=0.098/exp((v+23.1)/20) :was 43.1
}
}


FUNCTION hbet(v(mV))(/ms) { LOCAL vd
	vd=v+13.1
	if (fabs(vd)<1e-04){
	   hbet=1.4*(10 + vd*0.5)
	}else{
	   hbet=1.4/(1+exp(-(v+25.1)/10)) :was 13.1 changed july 30, 2007
} 
}




PROCEDURE rate(v (mV)) {LOCAL q10, msum, hsum, ma, mb, ha, hb
	

	ma=malf(v) mb=mbet(v) ha=half(v) hb=hbet(v)
	
	msum = ma+mb
	minf = ma/msum
	mtau = 1/(msum)
	
	
	hsum=ha+hb
	hinf=ha/hsum
	htau = 1 / (hsum)
	
}

	
UNITSON








