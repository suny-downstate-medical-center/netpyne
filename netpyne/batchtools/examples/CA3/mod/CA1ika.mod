: $Id: CA1ika.mod,v 1.2 2010/12/01 05:06:07 samn Exp $ 
TITLE Ika CA1

UNITS {
  (mA) = (milliamp)
  (mV) = (millivolt)
}
 
NEURON {
  SUFFIX kacurrent
  NONSPECIFIC_CURRENT ika, ikad
  RANGE g, gd, e, ninf, ntau, ndinf, ndtau, linf, ltau
}
 
PARAMETER {
  celsius	(degC)
  g= 0.048	(mho/cm2)
  gd= 0		(mho/cm2)
  e= -90	(mV)
}
 
STATE {
  n
  nd : distal
  l
}
 
ASSIGNED {
  v	(mV)
  ika	(mA/cm2) 
  ikad	(mA/cm2)
  ninf
  ntau  (ms)
  ndinf
  ndtau (ms)
  linf
  ltau	(ms)
}

PROCEDURE iassign () {
  ika=g*n*l*(v-e)
  ikad=gd*nd*l*(v-e)
}
 
BREAKPOINT {
  SOLVE states METHOD cnexp
  iassign()
}
 
DERIVATIVE states { 
  rates(v)
  n'= (ninf- n)/ ntau
  l'= (linf- l)/ ltau
  nd'= (ndinf-nd)/ndtau
}

INITIAL { 
  rates(v)
  n = ninf
  l = linf
  iassign()
}

PROCEDURE rates(v (mV)) {
  LOCAL  a, b
  UNITSOFF
  a = exp(-0.038*(1.5+1/(1+exp(v+40)/5))*(v-11))
  b =	exp(-0.038*(0.825+1/(1+exp(v+40)/5))*(v-11))
  ntau=4*b/(1+a)
  if (ntau<0.1) {ntau=0.1}
  ninf=1/(1+a)
	
  a=exp(-0.038*(1.8+1/(1+exp(v+40)/5))*(v+1))
  b=exp(-0.038*(0.7+1/(1+exp(v+40)/5))*(v+1))
  ndtau=2*b/(1+a)
  if (ndtau<0.1) {ndtau=0.1}
  ndinf=1/(1+a)

  a = exp(0.11*(v+56))
  ltau=0.26*(v+50)
  if (ltau<2) {ltau=2}
  linf=1/(1+a)
  UNITSON
}

