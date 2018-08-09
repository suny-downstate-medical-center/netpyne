TITLE Calcium low threshold T type current for RD Traub, J Neurophysiol 89:909-921, 2003

COMMENT

	Implemented by Maciej Lazarewicz 2003 (mlazarew@seas.upenn.edu)

ENDCOMMENT

INDEPENDENT { t FROM 0 TO 1 WITH 1 (ms) }

UNITS { 
	(mV) = (millivolt) 
	(mA) = (milliamp) 
}
 
NEURON { 
	SUFFIX cat
	NONSPECIFIC_CURRENT i   : not causing [Ca2+] influx
	RANGE gbar, i
}

PARAMETER { 
	gbar = 0.0 	(mho/cm2)
	v eca 		(mV)  
}
 
ASSIGNED { 
	i 		(mA/cm2) 
	minf hinf 	(1)
	mtau htau 	(ms) 
}
 
STATE {
	m h
}

BREAKPOINT { 
	SOLVE states METHOD cnexp 
	i = gbar * m * m * h * ( v - 125 ) 
}
 
INITIAL { 
	settables(v) 
	m  = minf
	h  = hinf
	m  = 0
} 

DERIVATIVE states { 
	settables(v) 
	m' = ( minf - m ) / mtau 
	h' = ( hinf - h ) / htau
}

UNITSOFF 

PROCEDURE settables(v) { 
	TABLE minf, mtau,hinf, htau FROM -120 TO 40 WITH 641
	minf  = 1 / ( 1 + exp( ( -v - 56 ) / 6.2 ) )
	mtau  = 0.204 + 0.333 / ( exp( ( v + 15.8 ) / 18.2 ) + exp( ( - v - 131 ) / 16.7 ) )
	hinf  = 1 / ( 1 + exp( ( v + 80 ) / 4 ) )
	if( v < -81 ) {
		htau  = 0.333 * exp( ( v + 466 ) / 66.6 )
	}else{
		htau  = 9.32 + 0.333 * exp( ( -v - 21 ) / 10.5 )
	}
}

UNITSON