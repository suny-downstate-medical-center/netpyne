: $Id: gabab.mod,v 1.9 2004/06/17 16:04:05 billl Exp $

COMMENT
-----------------------------------------------------------------------------

	Kinetic model of GABA-B receptors
	=================================

  MODEL OF SECOND-ORDER G-PROTEIN TRANSDUCTION AND FAST K+ OPENING
  WITH COOPERATIVITY OF G-PROTEIN BINDING TO K+ CHANNEL

  PULSE OF TRANSMITTER

  SIMPLE KINETICS WITH NO DESENSITIZATION

	Features:

  	  - peak at 100 ms; time course fit to Tom Otis' PSC
	  - SUMMATION (psc is much stronger with bursts)


	Approximations:

	  - single binding site on receptor	
	  - model of alpha G-protein activation (direct) of K+ channel
	  - G-protein dynamics is second-order; simplified as follows:
		- saturating receptor
		- no desensitization
		- Michaelis-Menten of receptor for G-protein production
		- "resting" G-protein is in excess
		- Quasi-stat of intermediate enzymatic forms
	  - binding on K+ channel is fast


	Kinetic Equations:

	  dR/dt = K1 * T * (1-R-D) - K2 * R

	  dG/dt = K3 * R - K4 * G

	  R : activated receptor
	  T : transmitter
	  G : activated G-protein
	  K1,K2,K3,K4 = kinetic rate cst

  n activated G-protein bind to a K+ channel:

	n G + C <-> O		(Alpha,Beta)

  If the binding is fast, the fraction of open channels is given by:

	O = G^n / ( G^n + KD )

  where KD = Beta / Alpha is the dissociation constant

-----------------------------------------------------------------------------

  Parameters estimated from patch clamp recordings of GABAB PSP's in
  rat hippocampal slices (Otis et al, J. Physiol. 463: 391-407, 1993).

-----------------------------------------------------------------------------

  PULSE MECHANISM

  Kinetic synapse with release mechanism as a pulse.  

  Warning: for this mechanism to be equivalent to the model with diffusion 
  of transmitter, small pulses must be used...

  For a detailed model of GABAB:

  Destexhe, A. and Sejnowski, T.J.  G-protein activation kinetics and
  spill-over of GABA may account for differences between inhibitory responses
  in the hippocampus and thalamus.  Proc. Natl. Acad. Sci. USA  92:
  9515-9519, 1995.

  For a review of models of synaptic currents:

  Destexhe, A., Mainen, Z.F. and Sejnowski, T.J.  Kinetic models of 
  synaptic transmission.  In: Methods in Neuronal Modeling (2nd edition; 
  edited by Koch, C. and Segev, I.), MIT press, Cambridge, 1996.

  This simplified model was introduced in:

  Destexhe, A., Bal, T., McCormick, D.A. and Sejnowski, T.J.
  Ionic mechanisms underlying synchronized oscillations and propagating
  waves in a model of ferret thalamic slices. Journal of Neurophysiology
  76: 2049-2070, 1996.  

  See also http://www.cnl.salk.edu/~alain



  Alain Destexhe, Salk Institute and Laval University, 1995

-----------------------------------------------------------------------------
ENDCOMMENT



INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
	POINT_PROCESS GABAB
	RANGE R, G, g
	NONSPECIFIC_CURRENT i
	GLOBAL Cmax, Cdur
	GLOBAL K1, K2, K3, K4, KD, Erev, warn, cutoff
}
UNITS {
	(nA) = (nanoamp)
	(mV) = (millivolt)
	(umho) = (micromho)
	(mM) = (milli/liter)
}

PARAMETER {

	Cmax	= 0.5	(mM)		: max transmitter concentration
	Cdur	= 0.3	(ms)		: transmitter duration (rising phase)
:
:	From Kfit with long pulse (5ms 0.5mM)
:
	K1	= 0.52	(/ms mM)	: forward binding rate to receptor
	K2	= 0.0013 (/ms)		: backward (unbinding) rate of receptor
	K3	= 0.098 (/ms)		: rate of G-protein production
	K4	= 0.033 (/ms)		: rate of G-protein decay
	KD	= 100			: dissociation constant of K+ channel
	n	= 4			: nb of binding sites of G-protein on K+
	Erev	= -95	(mV)		: reversal potential (E_K)
	warn	= 0			: too large G warning has/has not been issued
        cutoff = 1e12
}


ASSIGNED {
	v		(mV)		: postsynaptic voltage
	i 		(nA)		: current = g*(v - Erev)
	g 		(umho)		: conductance
	Gn
	R				: fraction of activated receptor
	edc
	synon
	Rinf
	Rtau (ms)
	Beta (/ms)
}

STATE {
	Ron Roff
	G				: fraction of activated G-protein
}


INITIAL {
	R = 0
	G = 0
	Ron = 0
	Roff = 0
	synon = 0
	Rinf = K1*Cmax/(K1*Cmax + K2)
	Rtau = 1/(K1*Cmax + K2)
	Beta = K2

}

BREAKPOINT {
	SOLVE bindkin METHOD derivimplicit
	if (G < cutoff) {
		Gn = G*G*G*G : ^n = 4
		g = Gn / (Gn+KD)
	} else {
		if(!warn){
			printf("gabab.mod WARN: G = %g too large\n", G)		
			warn = 1
		}
		g = 1
	}
	i = g*(v - Erev)
}


DERIVATIVE bindkin {
	Ron' = synon*K1*Cmax - (K1*Cmax + K2)*Ron
	Roff' = -K2*Roff
	R = Ron + Roff
	G' = K3 * R - K4 * G
}

: following supports both saturation from single input and
: summation from multiple inputs
: Note: automatic initialization of all reference args to 0 except first

NET_RECEIVE(weight,  r0, t0 (ms)) {
	if (flag == 1) { : at end of Cdur pulse so turn off
		r0 = weight*(Rinf + (r0 - Rinf)*exp(-(t - t0)/Rtau))
		t0 = t
		synon = synon - weight
		state_discontinuity(Ron, Ron - r0)
		state_discontinuity(Roff, Roff + r0)
        }else{ : at beginning of Cdur pulse so turn on
		r0 = weight*r0*exp(-Beta*(t - t0))
		t0 = t
		synon = synon + weight
		state_discontinuity(Ron, Ron + r0)
		state_discontinuity(Roff, Roff - r0)
		:come again in Cdur
		net_send(Cdur, 1)
        }
}
