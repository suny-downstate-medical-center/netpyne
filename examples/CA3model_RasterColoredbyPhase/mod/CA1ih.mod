: $Id: CA1ih.mod,v 1.4 2010/12/13 21:35:47 samn Exp $ 
TITLE Ih CA3

UNITS {
  (mA) = (milliamp)
  (mV) = (millivolt)
}
 
NEURON {
  SUFFIX hcurrent
  NONSPECIFIC_CURRENT ih
  RANGE g, e, v50, htau, hinf
  RANGE gfactor
}
 
PARAMETER {
  celsius	(degC)
  g= 0.0001	(mho/cm2)
  e= -30	(mV)
  v50=-82	(mV)
  gfactor = 1
}
 
STATE {
  h
}
 
ASSIGNED {
  ih	  (mA/cm2) 
  hinf
  htau    (ms)
  v	  (mV)
}

PROCEDURE iassign () { ih=g*h*(v-e)*gfactor }
 
BREAKPOINT {
  SOLVE states METHOD cnexp
  iassign()
}
 
DERIVATIVE states { 
  rates(v)
  h'= (hinf- h)/ htau
}

INITIAL { 
  rates(v)
  h = hinf
  iassign()
}

PROCEDURE rates(v (mV)) {
  UNITSOFF
  : HCN1
  :hinf = 1/(1+exp(0.151*(v-v50)))
  :htau = exp((0.033*(v+75)))/(0.011*(1+exp(0.083*(v+75))))

  : HCN2
  hinf = 1/(1+exp((v-v50)/10.5))
  htau = (1/(exp(-14.59-0.086*v)+exp(-1.87+0.0701*v))) 
  UNITSON
}

