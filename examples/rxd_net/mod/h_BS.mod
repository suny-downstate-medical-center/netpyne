TITLE I-h channel from Magee 1998 for distal dendrites
: modified to take into account Sonia's exp. Apr.2008 M.Migliore
: thread-safe 2010-05-18 Ben Suter
: 2010-11-07 Ben Suter, removing "hd" from parameter names, changing suffix from "hd" to "h"
: Parameters fit to pre-ZD current-clamp step responses from experiment BS0284 (traces and reconstruction from single corticospinal neuron)
: 2011-09-18 Ben Suter, set default parameter values to those found from MRF optimization for BS0284 model
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
    v                       (mV)
    celsius  = 34.0    (degC)
    erev     = -37.0               (mV)
    gbar     = 0.0001       (mho/cm2)
    vhalfl   = -78.474      (mV)    : was -81
    kl       = -6                   : was -8
    vhalft   = -66.139      (mV)    : was -62
    a0t      = 0.009        (/ms)   : was 0.0077696
    zetat    = 20           (1)     : was 5
    gmt      = 0.01         (1)     : was 0.057127
    q10      = 4.5
    qtl      = 1
    taumin	= 2.0	(ms)		: minimal value of time constant
}

NEURON {
    SUFFIX h
    NONSPECIFIC_CURRENT i
    RANGE gbar, vhalfl
    RANGE linf, taul, g
    GLOBAL taumin
}

STATE {
    l
}

ASSIGNED {
    i       (mA/cm2)
    linf
    taul
    g
}

INITIAL {
    rate(v)
    l       = linf
}

BREAKPOINT {
    SOLVE states METHOD cnexp
    g       = gbar*l
    i       = g*(v-erev)
}

FUNCTION alpt(v(mV)) {
    alpt    = exp(0.0378*zetat*(v-vhalft))
}

FUNCTION bett(v(mV)) {
    bett    = exp(0.0378*zetat*gmt*(v-vhalft))
}

DERIVATIVE states {     : exact when v held constant; integrates over dt step
    rate(v)
    l'      = (linf - l)/taul
}

PROCEDURE rate(v (mV)) { :callable from hoc
    LOCAL a,qt
    qt      = q10^((celsius-33)/10)
    a       = alpt(v)
    linf    = 1/(1 + exp(-(v-vhalfl)/kl))
    taul    = bett(v)/(qtl*qt*a0t*(1+a)) + 1e-8 
    if(taul < taumin) { taul = taumin } 	: min value of time constant
}
