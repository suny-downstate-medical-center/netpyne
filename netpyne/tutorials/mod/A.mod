NEURON { SUFFIX A }
NEURON { USEION k WRITE ik }
ASSIGNED { ik(mA/cm2) }

PARAMETER {
  erev = -70 (mV)
  gmax  = 1.45e-07 (mho/cm2)
  VhlfMaxm = -24
  VhlfMaxh = 8
  slopem = -3.2
  slopeh = 4.9
  taum = 82 (ms)
  tauh = 5 (ms)
}

INCLUDE "ofc.inc"

PROCEDURE iassign () { i = g*(v-erev) ik=i }






