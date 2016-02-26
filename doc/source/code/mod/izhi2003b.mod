NEURON {
    POINT_PROCESS Izhi2003b
    RANGE a,b,c,d,f,g,Iin,fflag,thresh,cellid
    NONSPECIFIC_CURRENT i
}

UNITS {
    (mV) = (millivolt)
    (nA) = (nanoamp)
    (nF) = (nanofarad)
}

INITIAL {
  v=-65
  u=0.2*v
  net_send(0,1)  
}

PARAMETER {
    a       = 0.02 (/ms)
    b       = 0.2  (/ms)
    c       = -65  (mV)   : reset potential after a spike
    d       = 2    (mV/ms)
    f = 5
    g = 140
    Iin = 10
    thresh = 30   (mV)   : spike threshold
    fflag = 1
    cellid = -1 : A parameter for storing the cell ID, if required (useful for diagnostic information)
}

ASSIGNED {
    v (mV)
    i (nA)
}

STATE {
    u (mV/ms)
}

BREAKPOINT {
    SOLVE states METHOD derivimplicit  : cnexp # either method works
    i = -0.001*(0.04*v*v + f*v + g - u + Iin)
}

DERIVATIVE states {
    u' = a*(b*v - u)
}

NET_RECEIVE (w) {
    if (flag == 1) {
        WATCH (v > thresh) 2
    } else if (flag == 2) {
        net_event(t)
        v = c
        u = u + d
    }
}
