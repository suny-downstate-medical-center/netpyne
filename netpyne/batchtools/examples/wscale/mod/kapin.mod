TITLE K-A channel from Klee Ficker and Heinemann
: modified by Brannon and Yiota Poirazi (poirazi@LNC.usc.edu)
: to account for Hoffman et al 1997 proximal region kinetics
: used only in soma and sections located < 100 microns from the soma


NEURON {
	SUFFIX kapin
	USEION k READ ek WRITE ik
        RANGE gkabar, ik
        :GLOBAL ninf,linf,taul,taun,lmin
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)

}


PARAMETER {                       :parameters that can be entered when function is called in cell-setup

       	gkabar = 0      (mho/cm2) :initialized conductance
        vhalfn = 11     (mV)      :activation half-potential
        vhalfl = -56    (mV) 	  :inactivation half-potential
	:vhalfl = -56    (mV) 	  :inactivation half-potential
        a0n = 0.05      (/ms)     :parameters used
        zetan = -1.5    (1)       :in calculation of (-1.5)
        zetal = 3       (1)       :steady state values(3)
        gmn = 0.55      (1)       :and time constants(0.55) change to get an effect on spike repolarization
        gml = 1         (1)
	:gml = 1         (1)
	lmin = 2        (ms)
	nmin = 0.1      (ms)
	pw = -1         (1)
	tq = -40	(mV)
	qq = 5		(mV)
	q10 = 5                   :temperature sensitivity
}



 
ASSIGNED {       :parameters needed to solve DE
	v               (mV)
        ek              (mV)      :K reversal potential  (reset in cell-setup.hoc)
	celsius         (degC)
	ik              (mA/cm2)
        ninf
        linf      
        taul            (ms)
        taun            (ms)
}


STATE {          :the unknown parameters to be solved in the DEs 
	n l
}

LOCAL qt

INITIAL {		:initialize the following parameter using rates()
        qt = q10^((celsius-24)/10(degC))         : temprature adjustment factor
	rates(v)
	n = ninf
	l = linf
}

BREAKPOINT {
	SOLVE states METHOD cnexp
:	ik = gkabar*n*l*(v+70)
	ik = gkabar*n*l*(v-ek)
}

DERIVATIVE states {
	rates(v)
        n' = (ninf - n)/taun
        l' = (linf - l)/taul
}



PROCEDURE rates(v (mV)) {                  :callable from hoc
        LOCAL a
	
        a = alpn(v)
        ninf = 1/(1 + a)                   : activation variable steady state value
        taun = betn(v)/(qt*a0n*(1+a))      : activation variable time constant
	if (taun<nmin) {taun=nmin}         : time constant not allowed to be less than nmin
        
	a = alpl(v)
        linf = 1/(1+ a)                    : inactivation variable steady state value
	taul = 12 (ms)
	:taul = 0.26(ms/mV)*(v+50)               : inactivation variable time constant
	:if (taul<lmin) {taul=lmin}         : time constant not allowed to be less than lmin

}

FUNCTION alpn(v(mV)) { LOCAL zeta 
  zeta = zetan+pw/(1+exp((v-tq)/qq))
UNITSOFF
  alpn = exp(1.e-3*zeta*(v-vhalfn)*9.648e4/(8.315*(273.16+celsius))) 
UNITSON
}

FUNCTION betn(v(mV)) { LOCAL zeta
  zeta = zetan+pw/(1+exp((v-tq)/qq))
UNITSOFF
  betn = exp(1.e-3*zeta*gmn*(v-vhalfn)*9.648e4/(8.315*(273.16+celsius))) 
UNITSON
}

FUNCTION alpl(v(mV)) {
UNITSOFF
  alpl = exp(1.e-3*zetal*(v-vhalfl)*9.648e4/(8.315*(273.16+celsius))) 
UNITSON
}

FUNCTION betl(v(mV)) {
UNITSOFF
  betl = exp(1.e-3*zetal*gml*(v-vhalfl)*9.648e4/(8.315*(273.16+celsius))) 
UNITSON
}

