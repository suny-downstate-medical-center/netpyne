TITLE Anomalous rectifier current for RD Traub, J Neurophysiol 89:909-921, 2003

COMMENT

	Implemented by Maciej Lazarewicz 2003 (mlazarew@seas.upenn.edu)

ENDCOMMENT

INDEPENDENT { t FROM 0 TO 1 WITH 1 (ms) }

UNITS { 
	(mV) = (millivolt) 
	(mA) = (milliamp) 
} 
NEURON { 
	SUFFIX ar
	NONSPECIFIC_CURRENT i
	RANGE gbar, i
}
PARAMETER { 
	gbar = 0.0 	(mho/cm2)
	v		(mV) 
	erev = -35	(mV)  
} 
ASSIGNED { 
	i 		(mA/cm2) 
	minf 		(1)
	mtau 		(ms) 
} 
STATE {
	m
}
BREAKPOINT { 
	SOLVE states METHOD cnexp
	i = gbar * m * ( v - erev ) 
} 
INITIAL { 
	minf  = 1 / ( 1 + exp( ( v + 75 ) / 5.5 ) )
	mtau = 1 / ( exp( -14.6 - 0.086 * v ) + exp( -1.87 + 0.07 * v ) )
	m = minf
	: m = 0.25 : ??
} 
DERIVATIVE states { 
	minf  = 1 / ( 1 + exp( ( v + 75 ) / 5.5 ) )
	mtau = 1 / ( exp( -14.6 - 0.086 * v ) + exp( -1.87 + 0.07 * v ) )
	m' = ( minf - m ) / mtau 
}
