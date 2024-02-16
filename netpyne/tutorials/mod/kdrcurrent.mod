: $Id: CA1ikdr.mod,v 1.2 2010/12/01 05:10:52 samn Exp $ 
TITLE IKDR CA1

UNITS {
  (mA) = (milliamp)
  (mV) = (millivolt)
}
 
NEURON {
  SUFFIX kdrcurrent
  NONSPECIFIC_CURRENT ik
  RANGE g, e, ninf, ntau, vshift
}
 
PARAMETER {
  celsius	(degC)
  g = 0.010	(mho/cm2)
  e = -90	(mV)
  vshift = -13
}
 
STATE {
  n 
}
 
ASSIGNED {
  v	  (mV)
  ik	  (mA/cm2) 
  ninf
  ntau    (ms)
}

PROCEDURE iassign () { ik=g*n*(v-e) }
 
BREAKPOINT {
  SOLVE states METHOD cnexp
  iassign()
}
 
DERIVATIVE states { 
  rates(v)
  n'= (ninf- n)/ ntau
}

INITIAL { 
  rates(v)
  n = ninf
  iassign()
}

PROCEDURE rates(v (mV)) {
  LOCAL  a, b
  UNITSOFF
  a = exp(-0.11*(v-13))
  b = exp(-0.08*(v-13)) 	
  ntau=50*b/(1+a)
  if (ntau<2) {ntau=2}
  ninf=1/(1+a)
  UNITSON
}

