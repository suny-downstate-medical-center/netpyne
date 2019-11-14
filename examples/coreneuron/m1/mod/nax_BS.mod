TITLE nax
: Na current for axon. No slow inact.
: M.Migliore Jul. 1997
: added sh to account for higher threshold M.Migliore, Apr.2002
: thread-safe 2010-05-31 Ben Suter
: 2010-11-07 Ben Suter reformatting, renaming thegna to g, setting sh = 0 (was 8 mV)
:
: :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
: Copyright 2011, Benjamin Suter (for changes only)
: Used in model of corticospinal neuron BS0284 and published as:
:  "Intrinsic electrophysiology of mouse corticospinal neurons: a characteristic set of features embodied in a realistic computational model"
:  by Benjamin Suter, Michele Migliore, and Gordon Shepherd
:  Submitted September 2011
: :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


NEURON {
    SUFFIX nax
    USEION na READ ena WRITE ina
    RANGE  gbar, ina, sh
:   GLOBAL minf, hinf, mtau, htau,thinf, qinf, Rb, Rg, qg
}

PARAMETER {
    v                   (mV)
    celsius             (degC)
    ena                 (mV)        : must be explicitly def. in hoc

    sh      = 0         (mV)
    gbar    = 0.010     (mho/cm2)

    tha     = -30       (mV)        : v 1/2 for act
    qa      = 7.2       (mV)        : act slope (4.5)
    Ra      = 0.4       (/ms)       : open (v)
    Rb      = 0.124     (/ms)       : close (v)

    thi1    = -45       (mV)        : v 1/2 for inact
    thi2    = -45       (mV)        : v 1/2 for inact
    qd      = 1.5       (mV)        : inact tau slope
    qg      = 1.5       (mV)
    mmin    = 0.02
    hmin    = 0.5
    q10     = 2
    Rg      = 0.01      (/ms)       : inact recov (v)
    Rd      = 0.03      (/ms)       : inact (v)

    thinf   = -50       (mV)        : inact inf slope
    qinf    = 4         (mV)        : inact inf slope
}


UNITS {
    (mA) = (milliamp)
    (mV) = (millivolt)
    (pS) = (picosiemens)
    (um) = (micron)
}

ASSIGNED {
    ina         (mA/cm2)
    g           (mho/cm2)
    minf
    hinf
    mtau        (ms)
    htau        (ms)
}

STATE { m h}

BREAKPOINT {
    SOLVE states METHOD cnexp
    g = gbar*m*m*m*h
    ina = g * (v - ena)
}

INITIAL {
    trates(v,sh)
    m = minf
    h = hinf
}

DERIVATIVE states {
    trates(v,sh)
    m' = (minf-m)/mtau
    h' = (hinf-h)/htau
}

PROCEDURE trates(vm,sh2) {
    LOCAL  a, b, qt
    qt = q10^((celsius-24)/10)

    a = trap0(vm,tha+sh2,Ra,qa)
    b = trap0(-vm,-tha-sh2,Rb,qa)
    mtau = 1/(a+b)/qt
    if (mtau<mmin) {
        mtau = mmin
    }
    minf = a/(a+b)

    a = trap0(vm,thi1+sh2,Rd,qd)
    b = trap0(-vm,-thi2-sh2,Rg,qg)
    htau =  1/(a+b)/qt
    if (htau<hmin) {
        htau = hmin
    }
    hinf = 1/(1+exp((vm-thinf-sh2)/qinf))
}

FUNCTION trap0(v,th,a,q) {
    if (fabs(v-th) > 1e-6) {
        trap0 = a * (v - th) / (1 - exp(-(v - th)/q))
    } else {
        trap0 = a * q
    }
}
