TITLE Sodium transient current for RD Traub, J Neurophysiol 89:909-921, 2003

COMMENT

	Implemented by Maciej Lazarewicz 2003 (mlazarew@seas.upenn.edu)

ENDCOMMENT

INDEPENDENT { t FROM 0 TO 1 WITH 1 (ms) }

UNITS { 
	(mV) = (millivolt) 
	(mA) = (milliamp) 
} 
NEURON { 
	SUFFIX naf
	USEION na READ ena WRITE ina
	RANGE gbar, ina
}
PARAMETER { 
	fastNashift = -3.5 (mV)
	gbar = 0.0 	   (mho/cm2)
	v ena 		   (mV)  
} 
ASSIGNED { 
	ina 		   (mA/cm2) 
	minf hinf 	   (1)
	mtau htau 	   (ms) 
} 
STATE {
	m h
}
BREAKPOINT { 
	SOLVE states METHOD cnexp
	ina = gbar * m * m * m * h * ( v - ena ) 
} 
INITIAL { 
	settables( v - fastNashift ) 
	m = minf
	m = 0
	h  = hinf
} 
DERIVATIVE states { 
	settables( v ) 
	m' = ( minf - m ) / mtau 
	h' = ( hinf - h ) / htau
}

UNITSOFF 

PROCEDURE settables(v1(mV)) {

	TABLE minf, hinf, mtau, htau  FROM -120 TO 40 WITH 641

	minf  = 1 / ( 1 + exp( ( - ( v1 + fastNashift ) - 38 ) / 10 ) )
	if( ( v1 + fastNashift ) < -30.0 ) {
		mtau = 0.025 + 0.14 * exp( ( ( v1 + fastNashift ) + 30 ) / 10 )
	} else{
		mtau = 0.02 + 0.145 * exp( ( - ( v1 + fastNashift ) - 30 ) / 10 ) 
	}

	: hinf, and htau are shifted 3.5 mV comparing to the paper

	hinf  = 1 / ( 1 + exp( ( ( v1 + fastNashift * 0 ) + 62.9 ) / 10.7 ) )
	htau = 0.15 + 1.15 / ( 1 + exp( ( ( v1 + fastNashift * 0 ) + 37 ) / 15 ) )
}

UNITSON