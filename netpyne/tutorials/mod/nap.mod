TITLE Sodium persistent current for RD Traub, J Neurophysiol 89:909-921, 2003

COMMENT

	Implemented by Maciej Lazarewicz 2003 (mlazarew@seas.upenn.edu)

ENDCOMMENT

INDEPENDENT { t FROM 0 TO 1 WITH 1 (ms) }

UNITS { 
	(mV) = (millivolt) 
	(mA) = (milliamp) 
} 
NEURON { 
	SUFFIX nap
	USEION na READ ena WRITE ina
	RANGE gbar, ina
}

PARAMETER { 
	gbar = 0.0 	(mho/cm2)
	v ena 		(mV)  
} 
ASSIGNED { 
	ina 		(mA/cm2) 
	minf 		(1)
	mtau 		(ms) 
} 
STATE {
	m
}

BREAKPOINT { 
	SOLVE states METHOD cnexp
	ina = gbar * m * ( v - ena ) 
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

	minf  = 1 / ( 1 + exp( ( - v - 48 ) / 10 ) )
	if( v < -40.0 ) {
		mtau = 0.025 + 0.14 * exp( ( v + 40 ) / 10 )
	}else{
		mtau = 0.02 + 0.145 * exp( ( - v - 40 ) / 10 )
	}
}
UNITSON