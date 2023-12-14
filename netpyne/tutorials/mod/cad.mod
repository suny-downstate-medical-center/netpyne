TITLE Calcium dynamics for RD Traub, J Neurophysiol 89:909-921, 2003

COMMENT

	Implemented by Maciej Lazarewicz 2003 (mlazarew@seas.upenn.edu)

ENDCOMMENT

NEURON {
	SUFFIX cad
	USEION ca READ ica WRITE cai
	RANGE  phi, beta
	GLOBAL ceiling
}

UNITS {
	(mA)	= (milliamp)
}

PARAMETER {
	phi		(1)
	beta		(/ms)
	ceiling		(1)
}

STATE {	cai (1) }

INITIAL { 
	cai = 0.0 
}

ASSIGNED { 
	ica		(mA/cm2) 
}
	
BREAKPOINT {
	SOLVE state METHOD cnexp
	if( cai < 0 ){ cai = 0 }
	if( cai > ceiling ){ cai = ceiling }
}

DERIVATIVE state { 
	cai' = - phi * ica - beta * cai 
}
