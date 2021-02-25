TITLE I-h channel from Magee 1998 for distal dendrites
: default values are for dendrites and low Na
: plus leakage, M.Migliore Mar 2010

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)

}

PARAMETER {
	v 		(mV)
    ehd = -30 		(mV)        
	celsius 	(degC)
	gbar=.0001 	(mho/cm2)
    vhalfl=-90   	(mV)
    vhalft=-75   	(mV)
    a0t=0.0046      	(/ms)
    zetal=4    	(1)
    zetat=2.2    	(1)
    gmt=.4   	(1)
	q10=4.5
	qtl=1
	clk=0
	elk = -70 (mV)
}


NEURON {
	THREADSAFE SUFFIX hd
	NONSPECIFIC_CURRENT i
	NONSPECIFIC_CURRENT lk
        RANGE gbar, vhalfl, elk, clk, glk, ehd
        GLOBAL linf,taul
}


STATE {
        l
}

ASSIGNED {
	i (mA/cm2)
	lk (mA/cm2)
        linf      
        taul
        ghd
	glk
}

INITIAL {
	rate(v)
	l=linf
}


BREAKPOINT {
	SOLVE states METHOD cnexp
	ghd = gbar*l
	i = ghd*(v-ehd)
	lk = clk*gbar*(v-elk)
}


FUNCTION alpl(v(mV)) {
  alpl = exp(0.0378*zetal*(v-vhalfl)) 
}

FUNCTION alpt(v(mV)) {
  alpt = exp(0.0378*zetat*(v-vhalft)) 
}

FUNCTION bett(v(mV)) {
  bett = exp(0.0378*zetat*gmt*(v-vhalft)) 
}

DERIVATIVE states {     : exact when v held constant; integrates over dt step
        rate(v)
        l' =  (linf - l)/taul
}

PROCEDURE rate(v (mV)) { :callable from hoc
        LOCAL a,qt
        qt=q10^((celsius-33)/10)
        a = alpt(v)
        linf = 1/(1+ alpl(v))
        taul = bett(v)/(qtl*qt*a0t*(1+a))
}














