: $Id: CA1ina.mod,v 1.4 2010/11/30 19:50:00 samn Exp $ 
TITLE INa CA1

UNITS {
  (mA) = (milliamp)
  (mV) = (millivolt)
}

NEURON {
  SUFFIX nacurrent
  NONSPECIFIC_CURRENT ina
  RANGE g, e, vi, ki
  RANGE minf,hinf,iinf,mtau,htau,itau : testing
}
  
PARAMETER {
  : v	    (mV)
  celsius	    (degC)
  g = 0.032   (mho/cm2)
  e = 55	    (mV)
  vi = -60    (mV)
  ki = 0.8
}
 
STATE {
  m
  h
  I : i 
}
 
ASSIGNED {
  i (mA/cm2)
  ina	(mA/cm2) 
  minf
  mtau    (ms)
  hinf
  htau	(ms)
  iinf
  itau	(ms)
  v	(mV) : testing
}

: PROCEDURE iassign () { ina=g*m*m*m*h*i*(v-e) }
PROCEDURE iassign () { i=g*m*m*m*h*I*(v-e) ina=i}
 
BREAKPOINT {
  SOLVE states METHOD cnexp
  iassign()
}
 
DERIVATIVE states { 
  rates(v)
  m' = (minf - m) / mtau
  h' = (hinf - h) / htau
  : i' = (iinf - i) / itau	    
  I' = (iinf - I) / itau	    
}

INITIAL { 
  rates(v)
  h = hinf
  m = minf
  : i = iinf
  I = iinf
  iassign() : testing
}


PROCEDURE rates(v (mV)) {
  LOCAL  a, b
  UNITSOFF
  a = 0.4*(v+30)/(1-exp(-(v+30)/7.2))
  b = 0.124*(v+30)/(exp((v+30)/7.2)-1) 	
  mtau=0.5/(a+b)
  if (mtau<0.02) {mtau=0.02}
  minf=a/(a+b)
  a = 0.03*(v+45)/(1-exp(-(v+45)/1.5))
  b = 0.01*(v+45)/(exp((v+45)/1.5)-1)
  htau=0.5/(a+b)
  if (htau<0.5) {htau=0.5}
  hinf=1/(1+exp((v+50)/4))
  a =	exp(0.45*(v+66))
  b = exp(0.09*(v+66))
  itau=3000*b/(1+a)
  if (itau<10) {itau=10}
  iinf=(1+ki*exp((v-vi)/2))/(1+exp((v-vi)/2))
  UNITSON
}

