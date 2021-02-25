COMMENT
kca.mod

Calcium-dependent potassium channel
Based on
Pennefather (1990) -- sympathetic ganglion cells
taken from
Reuveni et al (1993) -- neocortical cells

Author: Zach Mainen, Salk Institute, 1995, zach@salk.edu

26 Ago 2002 Modification of original channel to allow 
variable time step and to correct an initialization error.
Done by Michael Hines(michael.hines@yale.e) and 
Ruggero Scorcioni(rscorcio@gmu.edu) at EU Advance Course 
in Computational Neuroscience. Obidos, Portugal

20110202 made threadsafe by Ted Carnevale
20120105 SOLVE switched to derivimplicit from euler - TMM
20120106 SOLVE switched back to cnexp because ode linear in n -TMM
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

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
    THREADSAFE
	SUFFIX kca
	USEION k READ ek WRITE ik
	USEION ca READ cai
	RANGE n, gk, gbar
	RANGE ninf, ntau
	GLOBAL Ra, Rb, caix
	GLOBAL q10, temp, vmin, vmax
	RANGE tadj
}

UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)
	(pS) = (picosiemens)
	(um) = (micron)
} 

PARAMETER {
	gbar = 10   	(pS/um2)	: 0.03 mho/cm2
	v 		(mV)
	cai  		(mM)
	caix = 1	
									
	Ra   = 0.01	(/ms)		: max act rate  
	Rb   = 0.02	(/ms)		: max deact rate 

	dt		(ms)
	celsius		(degC)
	temp = 23	(degC)		: original temp 	
	q10  = 2.3			: temperature sensitivity

	vmin = -120	(mV)
	vmax = 100	(mV)
} 


ASSIGNED {
	a		(/ms)
	b		(/ms)
	ik 		(mA/cm2)
	gk		(pS/um2)
	ek		(mV)
	ninf
	ntau 		(ms)	
	tadj
}
 

STATE { n }

INITIAL { 
	rates(cai)
	n = ninf
}

BREAKPOINT {
        SOLVE states METHOD cnexp
	gk = tadj*gbar*n
	ik = (1e-4) * gk * (v - ek)
} 

LOCAL nexp

DERIVATIVE states {   :Computes state variable n 
        rates(cai)      :             at the current v and dt.
        n' =  (ninf-n)/ntau

}

PROCEDURE rates(cai(mM)) {  

        

        a = Ra * cai^caix
        b = Rb

        tadj = q10^((celsius - temp)/10)

        ntau = 1/tadj/(a+b)
	ninf = a/(a+b)

 
:        tinc = -dt * tadj
:        nexp = 1 - exp(tinc/ntau)
}






