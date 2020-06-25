COMMENT
kv.mod

Potassium channel, Hodgkin-Huxley style kinetics
Kinetic rates based roughly on Sah et al. and Hamill et al. (1991)

Author: Zach Mainen, Salk Institute, 1995, zach@salk.edu
	
26 Ago 2002 Modification of original channel to allow 
variable time step and to correct an initialization error.
Done by Michael Hines(michael.hines@yale.e) and 
Ruggero Scorcioni(rscorcio@gmu.edu) at EU Advance Course 
in Computational Neuroscience. Obidos, Portugal

20110202 made threadsafe by Ted Carnevale
20120514 fixed singularity in PROCEDURE rates

Special comment:

This mechanism was designed to be run at a single operating 
temperature--37 deg C--which can be specified by the hoc 
assignment statement
celsius = 37
This mechanism is not intended to be used at other temperatures, 
or to investigate the effects of temperature changes.

Zach Mainen created this particular model by adapting conductances 
from lower temperature to run at higher temperature, and found it 
necessary to reduce the temperature sensitivity of spike amplitude 
and time course.  He accomplished this by increasing the net ionic 
conductance through the heuristic of changing the standard HH 
formula
  g = gbar*product_of_gating_variables
to
  g = tadj*gbar*product_of_gating_variables
where
  tadj = q10^((celsius - temp)/10)
  temp is the "reference temperature" (at which the gating variable
    time constants were originally determined)
  celsius is the "operating temperature"

Users should note that this is equivalent to changing the channel 
density from gbar at the "reference temperature" temp (the 
temperature at which the at which the gating variable time 
constants were originally determined) to tadj*gbar at the 
"operating temperature" celsius.
ENDCOMMENT

NEURON {
    THREADSAFE
	SUFFIX kv
	USEION k READ ek WRITE ik
	RANGE n, gk, gbar
	RANGE ninf, ntau
	GLOBAL Ra, Rb
	GLOBAL q10, temp, tadj, vmin, vmax
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(pS) = (picosiemens)
	(um) = (micron)
} 

PARAMETER {
	gbar = 5   	(pS/um2)	: 0.03 mho/cm2
								
	tha  = 25	(mV)		: v 1/2 for inf
	qa   = 9	(mV)		: inf slope		
	
	Ra   = 0.02	(/ms)		: max act rate
	Rb   = 0.002	(/ms)		: max deact rate	

:	dt		(ms)
	temp = 23	(degC)		: original temp 	
	q10  = 2.3			: temperature sensitivity

	vmin = -120	(mV)
	vmax = 100	(mV)
} 


ASSIGNED {
	v 		(mV)
	celsius		(degC)
	a		(/ms)
	b		(/ms)
	ik 		(mA/cm2)
	gk		(pS/um2)
	ek		(mV)
	ninf
	ntau (ms)	
	tadj
}
 

STATE { n }

INITIAL {
    tadj = q10^((celsius - temp)/(10 (degC))) : make all threads calculate tadj at initialization

	trates(v)
	n = ninf
}

BREAKPOINT {
        SOLVE states METHOD cnexp
	gk = tadj*gbar*n
	ik = (1e-4) * gk * (v - ek)
} 

DERIVATIVE  states {   :Computes state variable n 
        trates(v)      :             at the current v and dt.
        n' =  (ninf-n)/ntau
}

PROCEDURE trates(v (mV)) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.
    TABLE ninf, ntau
    DEPEND celsius, temp, Ra, Rb, tha, qa
    FROM vmin TO vmax WITH 199

	rates(v): not consistently executed from here if usetable_hh == 1

:        tinc = -dt * tadj
:        nexp = 1 - exp(tinc/ntau)
}

UNITSOFF
PROCEDURE rates(v (mV)) {  :Computes rate and other constants at current v.
                      :Call once from HOC to initialize inf at resting v.

    : singular when v = tha
:    a = Ra * (v - tha) / (1 - exp(-(v - tha)/qa))
:    a = Ra * qa*((v - tha)/qa) / (1 - exp(-(v - tha)/qa))
:    a = Ra * qa*(-(v - tha)/qa) / (exp(-(v - tha)/qa) - 1)
    a = Ra * qa * efun(-(v - tha)/qa)

    : singular when v = tha
:    b = -Rb * (v - tha) / (1 - exp((v - tha)/qa))
:    b = -Rb * qa*((v - tha)/qa) / (1 - exp((v - tha)/qa))
:    b = Rb * qa*((v - tha)/qa) / (exp((v - tha)/qa) - 1)
    b = Rb * qa * efun((v - tha)/qa)

        tadj = q10^((celsius - temp)/10)
        ntau = 1/tadj/(a+b)
	ninf = a/(a+b)
}
UNITSON

FUNCTION efun(z) {
	if (fabs(z) < 1e-4) {
		efun = 1 - z/2
	}else{
		efun = z/(exp(z) - 1)
	}
}






