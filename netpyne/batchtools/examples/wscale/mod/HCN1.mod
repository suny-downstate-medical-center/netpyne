: $Id: HCN1.mod,v 1.4 2013/01/02 15:01:55 samn Exp $ 

TITLE HCN1 

UNITS {
  (mA) = (milliamp)
  (mV) = (millivolt)
}
 
NEURON {
  SUFFIX HCN1
  NONSPECIFIC_CURRENT ih
  RANGE gbar, g, e, v50, htau, hinf
  RANGE gfactor, htaufactor
}
 
PARAMETER {
  celsius	(degC)
  gbar = 0.0001	(mho/cm2)
  e= -30	(mV)
  v50= -73	(mV)
  gfactor = 1
  htaufactor = 1.0 : 4.78
}
 
STATE {
  h
}
 
ASSIGNED {
  ih	  (mA/cm2) 
  hinf
  htau    (ms)
  v	  (mV)
  g       (mho/cm2)
}

PROCEDURE giassign () { 
  : ih=g*h*(v-e)*gfactor 
  g = gbar*h*gfactor
  ih = g*(v-e)
}
 
BREAKPOINT {
  SOLVE states METHOD cnexp
  giassign()
}
 
DERIVATIVE states { 
  rates(v)
  h'= (hinf- h)/ htau
}

INITIAL { 
  rates(v)
  h = hinf
  giassign()
}

PROCEDURE rates(v (mV)) {
  UNITSOFF
  : HCN1
  hinf = 1/(1+exp(0.151*(v-v50)))
  htau = htaufactor*exp((0.033*(v+75)))/(0.011*(1+exp(0.083*(v+75))))
  UNITSON
}

