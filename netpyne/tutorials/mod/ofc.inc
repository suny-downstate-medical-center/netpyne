: $Id: ofc.inc,v 1.9 2009/03/27 22:50:24 billl Exp $ 
TITLE otto's channel includes

UNITS {
    (mV) = (millivolt)
    (mA) = (milliamp)
}

NEURON {
    RANGE i,g,erev,gmax,VhlfMaxm,VhlfMaxh,slopem,slopeh,taum,tauh
  :   GLOBAL minf,hinf
   RANGE minf,hinf
}

ASSIGNED { 
    i (mA/cm2)
    v (mV)
    g (mho/cm2)
    minf
    hinf
}

STATE {
  m h
}

BREAKPOINT {
    SOLVE states METHOD cnexp
    g = m * h * gmax
    iassign()
}

INITIAL {
    mh(v)
    m = minf
    h = hinf
    g = m * h * gmax 
    iassign()
}

DERIVATIVE states {  
    mh(v)      
    m' = ( minf - m ) / taum
    h' = ( hinf - h ) / tauh
}

UNITSOFF

PROCEDURE mh(v (mV)) {
    minf = 1 / (1 + exp((VhlfMaxm - v)/ slopem ) )
    hinf = 1 / (1 + exp((VhlfMaxh - v)/ slopeh ) )
}

UNITSON
