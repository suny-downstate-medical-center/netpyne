TITLE K-A channel from Klee Ficker and Heinemann
: modified to account for Dax A Current --- M.Migliore Jun 1997
: modified to be used with cvode  M.Migliore 2001
: thread-safe 2010-05-31 Ben Suter
: 2010-11-07 Ben Suter, removing "ka" from parameter names, reformatting, setting sh = 0 (was 24 mV)
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
    ek

    sh      = 0
    gbar    = 0.008     (mho/cm2)
    vhalfn  = 11        (mV)
    vhalfl  = -56       (mV)
    a0l     = 0.05      (/ms)
    a0n     = 0.05      (/ms)
    zetan   = -1.5      (1)
    zetal   = 3         (1)
    gmn     = 0.55      (1)
    gml     = 1         (1)
    lmin    = 5         (mS)
    nmin    = 0.4       (mS)
    pw      = -1        (1)
    tq      = -40
    qq      = 5
    q10     = 5
    qtl     = 1
}


NEURON {
    SUFFIX kap
    USEION k READ ek WRITE ik
    RANGE gbar, g, sh, tq, vhalfn, vhalfl, ik : 
:        GLOBAL ninf,linf,taul,taun,lmin
}

STATE {
    n
    l
}

ASSIGNED {
    ik      (mA/cm2)
    ninf
    linf
    taul
    taun
    g
}

INITIAL {
    rates(v)
    n=ninf
    l=linf
}


BREAKPOINT {
    SOLVE states METHOD cnexp
    g = gbar*n*l
    ik = g*(v-ek)
}


FUNCTION alpn(v(mV)) {
    LOCAL zeta
    zeta=zetan+pw/(1+exp((v-tq-sh)/qq))
    alpn = exp(1.e-3*zeta*(v-vhalfn-sh)*9.648e4/(8.315*(273.16+celsius)))
}

FUNCTION betn(v(mV)) {
    LOCAL zeta
    zeta=zetan+pw/(1+exp((v-tq-sh)/qq))
    betn = exp(1.e-3*zeta*gmn*(v-vhalfn-sh)*9.648e4/(8.315*(273.16+celsius)))
}

FUNCTION alpl(v(mV)) {
    alpl = exp(1.e-3*zetal*(v-vhalfl-sh)*9.648e4/(8.315*(273.16+celsius)))
}

FUNCTION betl(v(mV)) {
    betl = exp(1.e-3*zetal*gml*(v-vhalfl-sh)*9.648e4/(8.315*(273.16+celsius)))
}

DERIVATIVE states {     : exact when v held constant; integrates over dt step
    rates(v)
    n' = (ninf - n) / taun
    l' = (linf - l) / taul
}

PROCEDURE rates(v (mV)) { :callable from hoc
    LOCAL a,qt
    qt = q10^((celsius-24)/10)

    a = alpn(v)
    ninf = 1/(1 + a)
    taun = betn(v)/(qt*a0n*(1+a))
    if (taun<nmin) {
        taun=nmin
    }

    a = alpl(v)
    linf = 1/(1+ a)
    taul = 0.26*(v+50-sh)/qtl
    if (taul<lmin/qtl) {
        taul=lmin/qtl
    }
}
