TITLE K-DR channel
: from Klee Ficker and Heinemann
: modified to account for Dax et al.
: M.Migliore 1997
: thread-safe 2010-05-31 Ben Suter
: 2010-11-07 Ben Suter, removing "kdr" from parameter names, reformatting, setting sh = 0 (was 24 mV)
:
: :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
: Copyright 2011, Benjamin Suter (for changes only)
: Used in model of corticospinal neuron BS0284 and published as:
:  "Intrinsic electrophysiology of mouse corticospinal neurons: a characteristic set of features embodied in a realistic computational model"
:  by Benjamin Suter, Michele Migliore, and Gordon Shepherd
:  Submitted September 2011
: :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


UNITS {
    (mA) = (milliamp)
    (mV) = (millivolt)
}

PARAMETER {
    v                   (mV)
    celsius             (degC)
    ek                  (mV)     : must be explicitely def. in hoc

    gbar    = 0.003     (mho/cm2)
    vhalfn  = 13        (mV)
    a0n     = 0.0075    (/ms)
    zetan   = -3        (1)
    gmn     = 0.7       (1)
    nmax    = 20        (1)
    q10     = 1
    sh      = 0
}

NEURON {
    THREADSAFE
    SUFFIX kdr
    USEION k READ ek WRITE ik
    RANGE g, gbar, sh, ninf, taun, vhalfn, ik
}

STATE {
    n
}

ASSIGNED {
    ik      (mA/cm2)
    ninf
    g
    taun
}

BREAKPOINT {
    SOLVE states METHOD cnexp
    g = gbar*n
    ik = g*(v-ek)
}

INITIAL {
    rates(v)
    n=ninf
}

FUNCTION alpn(v(mV)) {
    alpn = exp(1.e-3*zetan*(v-vhalfn-sh)*9.648e4/(8.315*(273.16+celsius)))
}

FUNCTION betn(v(mV)) {
    betn = exp(1.e-3*zetan*gmn*(v-vhalfn-sh)*9.648e4/(8.315*(273.16+celsius)))
}

DERIVATIVE states {     : exact when v held constant; integrates over dt step
    rates(v)
    n' = (ninf - n)/taun
}

PROCEDURE rates(v (mV)) { :callable from hoc
    LOCAL a,qt
    qt = q10^((celsius-24)/10)

    a = alpn(v)
    ninf = 1/(1+a)
    taun = betn(v)/(qt*a0n*(1+a))
    if (taun<nmax) {
        taun = nmax/qt
    }
}
