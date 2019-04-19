TITLE Potasium dr type current for RD Traub, J Neurophysiol 89:909-921, 2003

COMMENT

	Implemented by Maciej Lazarewicz 2003 (mlazarew@seas.upenn.edu)

ENDCOMMENT

INDEPENDENT { t FROM 0 TO 1 WITH 1 (ms) }

UNITS { 
	(mV) = (millivolt) 
	(mA) = (milliamp) 
} 

NEURON { 
	SUFFIX kdr
	USEION k READ ek WRITE ik
	RANGE gbar, ik
}

PARAMETER { 
	gbar = 0.0 	(mho/cm2)
	v ek 		(mV)  
}
 
ASSIGNED { 
	ik 		(mA/cm2) 
	minf 		(1)
	mtau 		(ms) 
}
 
STATE {
	m
}

BREAKPOINT { 
	SOLVE states METHOD cnexp
	ik = gbar * m * m * m * m * ( v - ek ) 
}
 
INITIAL { 
	settables(v) 
	m = minf
	m = 0
}
 
DERIVATIVE states { 
	settables(v) 
	m' = ( minf - m ) / mtau 
}

UNITSOFF 

PROCEDURE settables(v) { 
	TABLE minf, mtau FROM -120 TO 40 WITH 641

	minf  = 1 / ( 1 + exp( ( -v - 29.5 ) / 10 ) )
	if( v < -10.0 ) {
		mtau = 0.25 + 4.35 * exp( ( v + 10 ) / 10 )
	}else{
		mtau = 0.25 + 4.35 * exp( ( -v - 10 ) / 10 )
	}
}

UNITSON