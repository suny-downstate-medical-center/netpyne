: from https://senselab.med.yale.edu/ModelDB/ShowModel.cshtml?model=168148&file=/stadler2014_layerV/kBK.mod
TITLE large-conductance calcium-activated potassium channel (BK)
	:Mechanism according to Gong et al 2001 and Womack&Khodakakhah 2002,
	:adapted for Layer V cells on the basis of Benhassine&Berger 2005.
	:NB: concentrations in mM
	
NEURON {
	SUFFIX kBK
	USEION k READ ek WRITE ik
	USEION ca READ cai
	RANGE gpeak, gkact, caPh, caPk, caPmax, caPmin
	RANGE caVhh, CaVhk, caVhmax, caVhmin, k, tau
        GLOBAL pinfmin : cutoff - if pinf < pinfmin, set to 0.; by default cutoff not used (pinfmin==0)
}


UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(molar) = (1/liter)
	(mM) 	= (millimolar)
}


PARAMETER {
		:maximum conductance (Benhassine 05)
	gpeak   = 268e-4	(mho/cm2) <0, 1e9>
	
	                                    : Calcium dependence of opening probability (Gong 2001)
	caPh    = 2e-3     (mM)             : conc. with half maximum open probaility
	caPk    = 1                         : Steepness of calcium dependence curve
	caPmax  = 1                         : max and
	caPmin  = 0                         : min open probability
		
	                                    : Calcium dependence of Vh shift (Womack 2002)
	caVhh   = 2e-3    (mM)              : Conc. for half of the Vh shift
	caVhk   = -0.94208                  : Steepness of the Vh-calcium dependence curve
	caVhmax = 155.67 (mV)               : max and
	caVhmin = -46.08 (mV)               : min Vh
	
	                                    : Voltage dependence of open probability (Gong 2001)
	                                    : must not be zero
	k       = 17	(mV)
	
	                                    : Timeconstant of channel kinetics
	                                    : no data for a description of a calcium&voltage dependence
	                                    : some points (room temp) in Behassine 05 & Womack 02
	tau     = 1 (ms) <1e-12, 1e9>
	scale   = 100                       : scaling to incorporate higher ca conc near ca channels
        
        pinfmin = 0.0                       : cutoff for pinf - less than that set pinf to 0.0

} 	


ASSIGNED {
	v 		(mV)
	ek		(mV)
	ik 		(mA/cm2)
    	cai  		(mM)
	caiScaled	(mM)
	pinf		(1)
}


STATE {
        p
}

BREAKPOINT {
	SOLVE states METHOD cnexp
	ik = gpeak*p* (v - ek)
}

DERIVATIVE states {     
        rate(v, cai)
        p' =  (pinf - p)/tau
}

INITIAL {     
        rate(v, cai)
        p = pinf
}

PROCEDURE rate(v(mV), ca(mM))  {
        caiScaled = ca*scale	
        pinf = P0ca(caiScaled) / ( 1 + exp( (Vhca(caiScaled)-v)/k ) )
        if(pinf < pinfmin) { pinf = 0.0 }
}

FUNCTION P0ca(ca(mM)) (1) {
		
	if (ca < 1E-18) { 		:check for division by zero		
	P0ca = caPmin
	} else {
	P0ca = caPmin + ( (caPmax - caPmin) / ( 1 + (caPh/ca)^caPk ))
	}
}

FUNCTION Vhca(ca(mM)) (mV) {
		
	if (ca < 1E-18) {		:check for division by zero
	Vhca = caVhmax
	} else {
	Vhca = caVhmin + ( (caVhmax - caVhmin ) / ( 1 + ((caVhh/ca)^caVhk)) )
	}
}	

