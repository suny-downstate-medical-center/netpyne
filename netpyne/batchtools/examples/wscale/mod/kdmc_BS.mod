TITLE K-D channel with activation for motor cortex
: K-D current with activation, for motor cortex pyramidal neurons, per Miller et al. (2008)
: Based on K-A current K-A current for Mitral Cells from Wang et al (1996), by M.Migliore Jan. 2002
: 2011-02-25 Ben Suter, first version, using MM's kamt.mod as a starting template
: 2011-09-18 Ben Suter, set default parameter values to those found from MRF optimization for BS0284 model
:
: :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
: Copyright 2011, Benjamin Suter
: Used in model of corticospinal neuron BS0284 and published as:
:  "Intrinsic electrophysiology of mouse corticospinal neurons: a characteristic set of features embodied in a realistic computational model"
:  by Benjamin Suter, Michele Migliore, and Gordon Shepherd
:  Submitted September 2011
: :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


NEURON {
    THREADSAFE
    SUFFIX kdmc
    USEION k READ ek WRITE ik
    RANGE  gbar, minf, mtau, hinf, htau, ik
    GLOBAL taumin
}

PARAMETER {
    gbar    = 0.002     (mho/cm2)

    celsius
    ek                  (mV)   : must be explicitly def. in hoc
    v                   (mV)

    : activation
    vhalfmt = -25       : original -20   : rough estimate from Miller et al (2008) Fig. 3D I-V curve
    km      = 14        : manual fit to match this I-V curve

    : inactivation
    : NOTE: These values are still quite arbitrary (but get about the correct htau at -40 and -30 mV
    vhalfh  = -5        : original -55
    zetah   = 0.02      : original 0.05
    gmh     = 0.2       : original 0.7
    a0h     = 0.00058   : original 0.00055
    taumin	= 0.1	(ms)		: minimal value of time constant

    vhalfht = -100      : original -88   : measured by Storm (1988)
    kh      = 8         : manual fit to match inactivation curve in Storm (1988) and Johnston+Wu textbook

    q10     = 3
}


UNITS {
    (mA) = (milliamp)
    (mV) = (millivolt)
    (pS) = (picosiemens)
    (um) = (micron)
}

ASSIGNED {
    ik      (mA/cm2)
    minf        mtau (ms)
    hinf        htau (ms)
}


STATE { m h }

BREAKPOINT {
    SOLVE states METHOD cnexp
    ik  = gbar*m*h*(v - ek)
}

INITIAL {
    trates(v)
    m   = minf
    h   = hinf
}

DERIVATIVE states {
    trates(v)
    m'  = (minf-m)/mtau
    h'  = (hinf-h)/htau
}

PROCEDURE trates(v) {
    LOCAL qt
    qt   = q10^((celsius-34)/10)

    minf = 1/(1 + exp(-(v-vhalfmt)/km))
    mtau = 1

    hinf = 1/(1 + exp((v-vhalfht)/kh))
    htau = exp(zetah*gmh*(v-vhalfh)) / (qt*a0h*(1 + exp(zetah*(v-vhalfh))))
    if(htau < taumin) { htau = taumin } 	: min value of time constant
}
