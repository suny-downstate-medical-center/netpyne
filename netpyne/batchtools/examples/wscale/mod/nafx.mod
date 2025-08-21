: Fast Na+ channel
: added the 's' attenuation system from hha2.mod
: Kiki Sidiropoulou
: September 27, 2007

NEURON {
	SUFFIX Nafx
	USEION na READ ena WRITE ina
	RANGE gnafbar, ina, gna, ar2
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	
}

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

PARAMETER {
	v (mV)
	dt (ms)
	gnafbar	= 0 (mho/cm2)
	:gnafbar= 0.086 (mho/cm2) <0,1e9>
	ena = 55 (mV)
	
	:PARAMETERS FOR S ATTENUATION SYSTEM
	taumin = 30 (ms)  :min activation time for "s" attenuation system
        vhalfr =-60 (mV)       :half potential for "s" attenuation system, -60
        vvh=-58		(mV) 
 	vvs = 2 (mV)
	a0r = 0.0003 (/ms)
        b0r = 0.0003 (/ms)
       : a0r = 0.0003 (ms)
        :b0r = 0.0003 (ms)
        zetar = 12    
	zetas = 12   
        gmr = 0.2   
	ar2 = 1.0               :initialized parameter for location-dependent
                                :Na-conductance attenuation, "s", (ar=1 -> zero attenuation)
}
STATE {
	m h s
}
ASSIGNED {
	celsius (degC)
	ina (mA/cm2)
	minf 
	hinf
	sinf 
	mtau (ms)
	htau (ms)
	stau (ms)
	gna (mho/cm2)
	
}



INITIAL {
	rate(v, ar2)
	m = minf
	h = hinf
	s = sinf
}

BREAKPOINT {
	SOLVE states METHOD cnexp
	gna = gnafbar*m*m*m*h*s
	ina = gna*(v-55)
	
}

DERIVATIVE states {
	rate(v, ar2)
	m' = (minf-m)/mtau
	h' = (hinf-h)/htau
	s' = (sinf-s)/stau
}

UNITSOFF

FUNCTION malf( v){ LOCAL va 
	va=v+28
	:va=v+28
	if (fabs(va)<1e-04){
	   malf= -0.2816*(-9.3 + va*0.5)
	   :malf= -0.2816*(-9.3 + va*0.5)
	}else{
	   malf = -0.2816*(v+28)/(-1+exp(-va/9.3))
	}
}


FUNCTION mbet(v(mV))(/ms) { LOCAL vb 
	vb=v+1
	:vb=v+1
	if (fabs(vb)<1e-04){
	    mbet = 0.2464*(6+vb*0.5)
	    :mbet = 0.2464*(6 + vb*0.5)
	}else{
	   mbet = 0.2464*(v+1)/(-1+exp(vb/6))	  :/(-1+exp((v+1)/6))
	}
	}	


FUNCTION half(v(mV))(/ms) { LOCAL vc 
	:vc=v+15.1
	vc=v+40.1	:changed to 40.1 by kiki
	if (fabs(vc)<1e-04){
	   half=0.098*(20 + vc*0.5)
	}else{
	   half=0.098/exp(vc+43.1/20)  :43.1, also spike train attenuation
}
}


FUNCTION hbet(v(mV))(/ms) { LOCAL vd
	:vd=v+13.1
	vd=v+13.1  :decreasing it increases the peak current
	if (fabs(vd)<1e-04){
	   hbet=1.4*(10 + vd*0.5)
	}else{
	   hbet=1.4/(1+exp(-(vd-13.1)/10))  :13.1 increasing it, increases the spike train attenuation and increases spike width
} 
}


:FUNCTIONS FOR S 
FUNCTION alpv(v(mV)) {
         alpv = 1/(1+exp((v-vvh)/vvs))
}


FUNCTION alpr(v(mV)) {       :used in "s" activation system tau

  alpr = exp(1.e-3*zetar*(v-vhalfr)*9.648e4/(8.315*(273.16+celsius))) 
}

FUNCTION betr(v(mV)) {       :used in "s" activation system tau

  betr = exp(1.e-3*zetar*gmr*(v-vhalfr)*9.648e4/(8.315*(273.16+celsius))) 
}



PROCEDURE rate(v (mV),ar2) {LOCAL q10, msum, hsum, ma, mb, ha, hb,c
	

	ma=malf(v) mb=mbet(v) ha=half(v) hb=hbet(v)
	
	msum = ma+mb
	minf = ma/msum
	mtau = 1/(msum)
	
	
	hsum=ha+hb
	hinf=ha/hsum
	htau = 1 / (hsum)

	stau = betr(v)/(a0r*(1+alpr(v))) 
	if (stau<taumin) {stau=taumin} :s activation tau
	c = alpv(v)
	sinf = c+ar2*(1-c) 	
}

	
UNITSON


