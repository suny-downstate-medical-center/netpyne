: $Id: xtra.mod,v 1.4 2014/08/18 23:15:25 ted Exp $

COMMENT
This mechanism is intended to be used in conjunction 
with the extracellular mechanism.  Pointers specified 
at the hoc level must be used to connect the 
extracellular mechanism's e_extracellular and i_membrane 
to this mechanism's ex and im, respectively.

xtra does three useful things:

1. Serves as a target for Vector.play() to facilitate 
extracellular stimulation.  Assumes that one has initialized 
a Vector to hold the time sequence of the stimulus current.
This Vector is to be played into the GLOBAL variable is 
(GLOBAL so only one Vector.play() needs to be executed), 
which is multiplied by the RANGE variable rx ("transfer 
resistance between the stimulus electrode and the local 
node").  This product, called ex in this mechanism, is the 
extracellular potential at the local node, i.e. is used to 
drive local e_extracellular.

2. Reports the contribution of local i_membrane to the 
total signal that would be picked up by an extracellular 
recording electrode.  This is computed as the product of rx, 
i_membrane (called im in this mechanism), and the surface area 
of the local segment, and is reported as er.  The total 
extracellularly recorded potential is the sum of all er_xtra 
over all segments in all sections, and is to be computed at 
the hoc level, e.g. with code like

func fieldrec() { local sum
  sum = 0
  forall {
    if (ismembrane("xtra")) {
      for (x,0) sum += er_xtra(x)
    }
  }
  return sum
}

Bipolar recording, i.e. recording the difference in potential 
between two extracellular electrodes, can be achieved with no 
change to either this NMODL code or fieldrec(); the values of 
rx will reflect the difference between the potentials at the 
recording electrodes caused by the local membrane current, so 
some rx will be negative and others positive.  The same rx 
can be used for bipolar stimulation.

Multiple monopolar or bipolar extracellular recording and 
stimulation can be accommodated by changing this mod file to 
include additional rx, er, and is, and changing fieldrec() 
to a proc.

3. Allows local storage of xyz coordinates interpolated from 
the pt3d data.  These coordinates are used by hoc code that 
computes the transfer resistance that couples the membrane 
to extracellular stimulating and recording electrodes.


Prior to NEURON 5.5, the SOLVE statement in the BREAKPOINT block 
used METHOD cvode_t so that the adaptive integrators wouldn't miss 
the stimulus.  Otherwise, the BREAKPOINT block would have been called 
_after_ the integration step, rather than from within cvodes/ida, 
causing this mechanism to fail to deliver a stimulus current 
when the adaptive integrator is used.

With NEURON 5.5 and later, this mechanism abandons the BREAKPOINT 
block and uses the two new blocks BEFORE BREAKPOINT and  
AFTER SOLVE, like this--

BEFORE BREAKPOINT { : before each cy' = f(y,t) setup
  ex = is*rx*(1e6)
}
AFTER SOLVE { : after each solution step
  er = (10)*rx*im*area
}

This ensures that the stimulus potential is computed prior to the 
solution step, and that the recorded potential is computed after.
ENDCOMMENT

NEURON {
	SUFFIX xtra
	RANGE rx, er
	RANGE x, y, z
	GLOBAL is
	RANGE im, ex
}

PARAMETER {
	: default transfer resistance between stim electrodes and axon
	rx = 1 (megohm) : mV/nA
	x = 0 (1) : spatial coords
	y = 0 (1)
	z = 0 (1)
}

ASSIGNED {
	v (millivolts)
	is (milliamp)
	ex (millivolts)
	im (milliamp/cm2)
	er (microvolts)
	area (micron2)
}

INITIAL {
	ex = is*rx*(1e6)
	er = (10)*rx*im*area
: this demonstrates that area is known
: UNITSOFF
: printf("area = %f\n", area)
: UNITSON
}

: Use BREAKPOINT for NEURON 5.4 and earlier
: BREAKPOINT {
:	SOLVE f METHOD cvode_t
: }
:
: PROCEDURE f() {
:	: 1 mA * 1 megohm is 1000 volts
:	: but ex is in mV
:	ex = is*rx*(1e6)
:	er = (10)*rx*im*area
: }

: With NEURON 5.5 and later, abandon the BREAKPOINT block and PROCEDURE f(),
: and instead use BEFORE BREAKPOINT and AFTER SOLVE

BEFORE BREAKPOINT { : before each cy' = f(y,t) setup
  ex = is*rx*(1e6)
  :printf("%f\n", ex)
}
AFTER SOLVE { : after each solution step
  er = (10)*rx*im*area
}

